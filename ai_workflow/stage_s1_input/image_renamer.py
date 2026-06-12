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

        for tag, keywords in SEMANTIC_TAGS.items():
            score = 0.0
            hits: list[str] = []
            for kw in keywords:
                if kw.lower() in text_lower:
                    score += 1.0
                    hits.append(kw)

            if score > 0:
                confidence = min(score / max(len(keywords) * 0.3, 1), 1.0)
                matched.append((tag, confidence, hits))

        if matched:
            matched.sort(key=lambda x: x[1], reverse=True)
            return matched[0]

        w, h = img.size
        if w > h * 1.5:
            return "flow_chart", 0.4, []
        elif h > w * 1.5:
            return "ui_prototype", 0.4, []

        return "diagram", 0.3, []

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
