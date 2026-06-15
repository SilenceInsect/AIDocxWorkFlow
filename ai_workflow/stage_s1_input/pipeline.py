"""Pipeline orchestrator for Stage S1 — Docx Extraction + OCR.

Ties together docx_extractor, image_renamer, ocr_engine, and md_converter
into a single end-to-end pipeline that:
1. Extracts text and images from a DOCX file.
2. Generates semantic names for images via OCR analysis.
3. Runs full OCR on each image and saves structured JSON results.
4. Converts content to Markdown with semantic image references.
5. Organizes all output under a requirement-specific directory structure.

Directory layout:
  workflow_assets/<req_name>/「S1 需求评审」/v1.0/
    raw/
      extracted_text.md
      extracted_images/
        img_001_ui_prototype.png
        img_002_flow_chart.png
      ocr_results/
        img_001_ui_prototype.json
        img_002_flow_chart.json
    review_report.md
    review_report.json
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .docx_extractor import DocxExtractor, ExtractedDocument
from .image_renamer import ImageRenamer, ImageNamingResult, generate_image_ref
from .ocr_engine import OCREngine, OCRResult
from .md_converter import MarkdownConverter, ConvertedMarkdown, convert_to_markdown
from .utils.constants import (
    get_s1_output_dir,
    IMAGE_SUBDIR,
    OCR_SUBDIR,
    RAW_SUBDIR,
)


@dataclass
class PipelineResult:
    """Result of the full S1 pipeline execution."""

    req_name: str
    success: bool
    output_dir: Path
    docx_path: Optional[Path] = None
    markdown_path: Optional[Path] = None
    extracted_document: Optional[ExtractedDocument] = None
    image_refs: dict[int, str] = field(default_factory=dict)
    naming_results: list[ImageNamingResult] = field(default_factory=list)
    ocr_results: list[OCRResult] = field(default_factory=list)
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "req_name": self.req_name,
            "success": self.success,
            "output_dir": str(self.output_dir),
            "docx_path": str(self.docx_path) if self.docx_path else None,
            "markdown_path": str(self.markdown_path) if self.markdown_path else None,
            "image_count": len(self.image_refs),
            "naming_results": [
                {"original": r.original_name, "semantic_tag": r.semantic_tag, "confidence": r.confidence}
                for r in self.naming_results
            ],
            "ocr_results": [
                {"image_ref": r.image_ref, "confidence": r.confidence, "text_preview": r.ocr_text[:100]}
                for r in self.ocr_results
            ],
            "error": self.error_message,
        }


class S1Pipeline:
    """End-to-end pipeline for DOCX extraction, image naming, OCR, and MD conversion."""

    def __init__(
        self,
        req_name: str,
        version: str = "v1.0",
        output_root: Optional[Path] = None,
    ):
        """Initialize the S1 pipeline.

        Args:
            req_name: Name of the requirement (used for directory structure).
            version: Version string (default: v1.0).
            output_root: Override the default output root (workflow_assets/).
        """
        self.req_name = req_name
        self.version = version
        self.output_root = output_root or get_s1_output_dir(req_name, version)
        self.docx_path: Optional[Path] = None
        self.extractor: Optional[DocxExtractor] = None
        self.ocr_engine: Optional[OCREngine] = None
        self.image_renamer: Optional[ImageRenamer] = None

    def run(
        self,
        docx_path: str | Path,
        skip_ocr: bool = False,
        ocr_lang: str = "chi_sim+eng",
    ) -> PipelineResult:
        """Run the full S1 pipeline on a DOCX file.

        Args:
            docx_path: Path to the input .docx or .doc file.
            skip_ocr: Skip OCR step (for text-only extraction).
            ocr_lang: Tesseract language pack (default: chi_sim+eng).

        Returns:
            PipelineResult with all outputs and metadata.
        """
        self.docx_path = Path(docx_path)
        raw_dir = self.output_root / RAW_SUBDIR
        images_dir = raw_dir / IMAGE_SUBDIR
        ocr_dir = raw_dir / OCR_SUBDIR

        raw_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        if not skip_ocr:
            ocr_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.extractor = DocxExtractor()
            extracted = self.extractor.extract(self.docx_path)

            saved_paths = self.extractor.save_images(
                extracted, images_dir, prefix="image"
            )

            self.image_renamer = ImageRenamer()
            naming_results = self._rename_images(images_dir, saved_paths)

            image_refs = self._build_ref_map(naming_results)

            self._rename_saved_images(images_dir, naming_results)

            if not skip_ocr:
                self.ocr_engine = OCREngine(lang=ocr_lang)
                ocr_results = self._run_ocr(images_dir, ocr_dir, image_refs)
            else:
                ocr_results = []

            md_path = self.output_root / RAW_SUBDIR / "extracted_text.md"
            converter = MarkdownConverter(image_refs=image_refs)
            md_result = converter.convert(
                extracted,
                doc_title=self.req_name,
            )
            converter.save(md_result, md_path)

            index_map = {
                "req_name": self.req_name,
                "version": self.version,
                "source_docx": str(self.docx_path),
                "output_dir": str(self.output_root),
                "image_refs": {
                    str(idx): refs for idx, refs in image_refs.items()
                },
                "images": [
                    {
                        "index": idx,
                        "ref": refs,
                        "ocr_confidence": next(
                            (r.confidence for r in ocr_results if r.image_ref == refs),
                            None,
                        ),
                    }
                    for idx, refs in image_refs.items()
                ],
            }
            index_path = raw_dir / "image_index.json"
            index_path.write_text(
                json.dumps(index_map, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            return PipelineResult(
                req_name=self.req_name,
                success=True,
                output_dir=self.output_root,
                docx_path=self.docx_path,
                markdown_path=md_path,
                extracted_document=extracted,
                image_refs=image_refs,
                naming_results=naming_results,
                ocr_results=ocr_results,
            )

        except Exception as e:
            return PipelineResult(
                req_name=self.req_name,
                success=False,
                output_dir=self.output_root,
                docx_path=self.docx_path,
                error_message=str(e),
            )

        finally:
            if self.extractor:
                self.extractor.close()

    def _rename_images(
        self,
        images_dir: Path,
        saved_paths: dict[int, str],
    ) -> list[ImageNamingResult]:
        results: list[ImageNamingResult] = []
        index = 1
        for idx in sorted(saved_paths.keys()):
            img_path = Path(saved_paths[idx])
            if img_path.exists():
                result = self.image_renamer.analyze_and_rename(img_path, index)
                results.append(result)
                index += 1
        return results

    def _build_ref_map(
        self,
        naming_results: list[ImageNamingResult],
    ) -> dict[int, str]:
        ref_map: dict[int, str] = {}
        for i, result in enumerate(naming_results, start=1):
            ext = self._detect_extension(
                result.original_name
            )
            ref_name = generate_image_ref(i, result.semantic_tag)
            if "." in ext and ext != ".png":
                ref_name = ref_name.replace(".png", ext)
            ref_map[i] = ref_name
        return ref_map

    def _detect_extension(self, filename: str) -> str:
        for ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"]:
            if ext in filename.lower():
                return ext
        return ".png"

    def _rename_saved_images(
        self,
        images_dir: Path,
        naming_results: list[ImageNamingResult],
    ):
        for i, result in enumerate(naming_results, start=1):
            ext = self._detect_extension(result.original_name)
            new_name = generate_image_ref(i, result.semantic_tag)
            if "." in ext and ext != ".png":
                new_name = new_name.replace(".png", ext)

            old_path = images_dir / result.original_name
            new_path = images_dir / new_name
            if old_path.exists() and old_path != new_path:
                old_path.rename(new_path)

            for img in (
                self.extractor.extracted_document.images
                if self.extractor and self.extractor.extracted_document
                else []
            ):
                if img.original_filename == result.original_name:
                    img.original_filename = new_name

    def _run_ocr(
        self,
        images_dir: Path,
        ocr_dir: Path,
        image_refs: dict[int, str],
    ) -> list[OCRResult]:
        results: list[OCRResult] = []
        for idx, ref_name in sorted(image_refs.items()):
            img_path = images_dir / ref_name
            if not img_path.exists():
                continue
            try:
                result = self.ocr_engine.recognize(img_path, ref_name, page=1)
                results.append(result)
                json_path = ocr_dir / f"{Path(ref_name).stem}.json"
                json_path.write_text(result.to_json(), encoding="utf-8")
            except Exception as e:
                print(f"Warning: OCR failed for {ref_name}: {e}")

        return results


def run_s1_pipeline(
    docx_path: str | Path,
    req_name: str,
    version: str = "v1.0",
    skip_ocr: bool = False,
    ocr_lang: str = "chi_sim+eng",
) -> PipelineResult:
    """Convenience function to run the full S1 pipeline.

    Args:
        docx_path: Path to the input .docx or .doc file.
        req_name: Name of the requirement (for directory structure).
        version: Version string (default: v1.0).
        skip_ocr: Skip OCR step (default: False).
        ocr_lang: Tesseract language pack (default: chi_sim+eng).

    Returns:
        PipelineResult with all outputs and metadata.

    Example:
        result = run_s1_pipeline(
            "/path/to/requirements.docx",
            req_name="游戏道具商城系统",
        )
        if result.success:
            print(f"Output: {result.output_dir}")
            print(f"Images: {result.image_count}")
    """
    pipeline = S1Pipeline(req_name=req_name, version=version)
    return pipeline.run(docx_path, skip_ocr=skip_ocr, ocr_lang=ocr_lang)
