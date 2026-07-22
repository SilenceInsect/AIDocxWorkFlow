"""Semantic image renaming based on OCR text analysis.

Automatically generates descriptive labels for images extracted from DOCX files
by analyzing their OCR text content and matching against known diagram types.
"""

from __future__ import annotations

import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PIL import Image

from .utils.constants import SEMANTIC_TAGS, IMAGE_TAG_KEYWORDS
from .ocr_engine import OCREngine


@dataclass
class ImageNamingResult:
    """Result of semantic naming analysis for a single image."""

    original_name: str
    semantic_tag: str
    confidence: float
    matched_keywords: list[str]
    preview_text: str

    @property
    def ref_name(self) -> str:
        return self.semantic_tag


class ImageRenamer:
    """Generate semantic, descriptive names for extracted images.

    Uses OCR preview text to classify images into semantic categories
    (UI prototype, flow chart, schema, etc.) and produces standardized names.
    """

    def __init__(self, ocr_engine: Optional[OCREngine] = None):
        self.ocr_engine = ocr_engine or OCREngine()

    def analyze_and_rename(
        self,
        image_path: str | Path | bytes,
        index: int,
        override_tag: Optional[str] = None,
    ) -> ImageNamingResult:
        """Analyze an image and determine its semantic tag.

        Args:
            image_path: Path to image file or raw bytes.
            index: Numeric index for the image (used in ref name).
            override_tag: Force a specific semantic tag, skipping OCR analysis.

        Returns:
            ImageNamingResult with semantic tag and metadata.
        """
        if override_tag:
            return ImageNamingResult(
                original_name=getattr(image_path, "name", str(image_path)),
                semantic_tag=override_tag,
                confidence=1.0,
                matched_keywords=["manual_override"],
                preview_text="",
            )

        if isinstance(image_path, bytes):
            img = Image.open(io.BytesIO(image_path))
            preview = self.ocr_engine.quick_preview(image_path)
            original_name = f"image_{index:03d}"
        else:
            img = Image.open(image_path)
            preview = self.ocr_engine.quick_preview(image_path)
            original_name = Path(image_path).name

        tag, confidence, keywords = self._classify_by_ocr(preview, img)

        return ImageNamingResult(
            original_name=original_name,
            semantic_tag=tag,
            confidence=confidence,
            matched_keywords=keywords,
            preview_text=preview[:200],
        )

    def _classify_by_ocr(
        self, text: str, img: Image.Image
    ) -> tuple[str, float, list[str]]:
        """Classify image type from OCR text and image dimensions.

        Args:
            text: OCR-extracted text from the image.
            img: PIL Image object for additional analysis.

        Returns:
            Tuple of (semantic_tag, confidence, matched_keywords).
        """
        text_lower = text.lower()
        matched: list[tuple[str, float, list[str]]] = []

        # ── 1. Keyword 匹配（优先使用）───────────────────────────────────
        # 改进：计算 weighted score，每个 tag 的命中权重不同
        tag_weights = {
            "ui_prototype": 1.0,
            "flow_chart":   1.2,   # 流程图关键词更精准，适当加权
            "data_schema":  1.3,   # 字段/表结构等词高度特异
            "sequence_diagram": 1.1,
            "architecture": 1.2,
            "table":        1.3,   # 表格关键词高度特异
            "screenshot":   0.7,   # 截图关键词较泛用，降低权重
            "diagram":      0.5,   # 图/示意图最泛用，最低权重
        }
        for tag, keywords in SEMANTIC_TAGS.items():
            score = 0.0
            hits: list[str] = []
            for kw in keywords:
                if kw.lower() in text_lower:
                    score += 1.0 * tag_weights.get(tag, 1.0)
                    hits.append(kw)
            if score > 0:
                # 归一化：按关键词总数比例 + 最低置信 0.5
                confidence = min(score / max(len(keywords) * 0.3, 1), 1.0)
                confidence = max(confidence, 0.5)
                matched.append((tag, confidence, hits))

        if matched:
            matched.sort(key=lambda x: x[1], reverse=True)
            top_tag, top_conf, top_hits = matched[0]
            # 关键词命中高置信 → 直接返回
            if top_conf >= 0.65:
                return top_tag, top_conf, top_hits
            # 中等置信 + 宽高比验证 → 双重确认
            w, h = img.size
            aspect = w / h if h > 0 else 1.0
            # 宽高比与 tag 不符 → 降权
            if top_tag == "flow_chart" and aspect < 1.3:
                return (matched[0][0], matched[0][1] * 0.8, matched[0][2]) if len(matched) > 1 else ("ui_prototype", 0.4, [])
            if top_tag == "ui_prototype" and aspect > 2.5:
                return (matched[0][0], matched[0][1] * 0.8, matched[0][2]) if len(matched) > 1 else ("flow_chart", 0.4, [])
            return matched[0]

        # ── 2. 无关键词命中 → 宽高比 heuristics ─────────────────────────
        w, h = img.size
        aspect = w / h if h > 0 else 1.0

        # 宽高比更极端 → 更确信是 UI 原型（手机截图竖长；平板横长）
        if aspect < 0.5:      # 极端竖图（h > 2w）→ 手机 UI 截图
            return "ui_prototype", 0.55, []
        if aspect > 3.0:      # 极端横图 → 可能是长流程图或网页 UI
            return "flow_chart", 0.5, []

        # 中等宽高比（0.5~3.0）→ 尝试颜色分析
        color_confidence, is_ui_like = self._color_analysis(img)
        if is_ui_like:
            # 颜色分布均匀 → UI 原型可能性更高
            return "ui_prototype", 0.5 + color_confidence * 0.1, []

        # ── 3. 极端横图 → 流程图 ────────────────────────────────────────
        if aspect > 1.5:
            return "flow_chart", 0.45, []
        # 极端竖图 → UI 原型
        if aspect < 0.67:
            return "ui_prototype", 0.45, []

        # ── 4. 完全模糊兜底 ──────────────────────────────────────────────
        # 游戏 PRD 中 UI 原型占比最高，默认给 ui_prototype
        return "ui_prototype", 0.3, []

    def _color_analysis(self, img: Image.Image) -> tuple[float, bool]:
        """分析图片颜色分布，判断是否像 UI 原型。

        UI 原型特点：
        - 颜色数量适中（10~100种），不像照片那样复杂
        - 有明显色块边界（矩形区域多）
        - 不像自然照片那样有细腻渐变

        Returns:
            (confidence, is_ui_like) — confidence ∈ [0, 1]
        """
        try:
            img_small = img.convert("RGB").resize((64, 64))
            pixels = list(img_small.getdata())
            unique_colors = len(set(pixels))

            # UI 原型通常颜色种类在 50~5000 之间（过于单调或过于复杂都不是 UI 原型）
            if 30 <= unique_colors <= 5000:
                # 适中颜色数 → UI 原型特征更强
                normalized = unique_colors / 5000
                confidence = min(normalized * 1.5, 1.0) if unique_colors < 5000 else 0.4
                return confidence, True

            return 0.0, False
        except Exception:
            return 0.0, False

    def rename_in_batch(
        self,
        image_dir: str | Path,
        index_start: int = 1,
    ) -> list[ImageNamingResult]:
        """Analyze and rename all images in a directory.

        Args:
            image_dir: Directory containing images.
            index_start: Starting index for numbering.

        Returns:
            List of ImageNamingResult for each image.
        """
        dir_path = Path(image_dir)
        extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}
        image_files = sorted(
            [f for f in dir_path.iterdir() if f.suffix.lower() in extensions]
        )

        results: list[ImageNamingResult] = []
        for i, img_file in enumerate(image_files, start=index_start):
            result = self.analyze_and_rename(img_file, i)
            results.append(result)

        return results

    def save_naming_map(
        self,
        results: list[ImageNamingResult],
        output_path: str | Path,
    ):
        """Save naming results as a mapping JSON file.

        Args:
            results: List of ImageNamingResult objects.
            output_path: Path to save the JSON mapping.
        """
        mapping = {}
        for i, r in enumerate(results, start=1):
            mapping[f"img_{i:03d}"] = {
                "original_name": r.original_name,
                "semantic_tag": r.semantic_tag,
                "ref_name": r.ref_name,
                "confidence": r.confidence,
                "matched_keywords": r.matched_keywords,
            }

        Path(output_path).write_text(
            json.dumps(mapping, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def generate_image_ref(index: int, semantic_tag: str) -> str:
    """Generate a standardized image reference name.

    Args:
        index: Image index number.
        semantic_tag: Semantic classification tag.

    Returns:
        Formatted reference name (e.g., 'img_001_ui_prototype.png').
    """
    return f"img_{index:03d}_{semantic_tag}.png"
