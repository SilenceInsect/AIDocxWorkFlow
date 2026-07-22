"""Stage S1 — Input Processing: DOCX Extraction + OCR + Markdown Conversion.

Public API:
    run_s1_pipeline(docx_path, req_name, version, skip_ocr, ocr_lang) -> PipelineResult
    S1Pipeline
    DocxExtractor
    OCREngine
    ImageRenamer
    MarkdownConverter
"""

from .pipeline import S1Pipeline, run_s1_pipeline, PipelineResult
from .docx_extractor import DocxExtractor, ExtractedDocument, ExtractedParagraph, ExtractedImage
from .ocr_engine import OCREngine, OCRResult
from .image_renamer import ImageRenamer, ImageNamingResult, generate_image_ref
from .md_converter import MarkdownConverter, ConvertedMarkdown

__all__ = [
    "run_s1_pipeline",
    "S1Pipeline",
    "PipelineResult",
    "DocxExtractor",
    "ExtractedDocument",
    "ExtractedParagraph",
    "ExtractedImage",
    "OCREngine",
    "OCRResult",
    "ImageRenamer",
    "ImageNamingResult",
    "generate_image_ref",
    "MarkdownConverter",
    "ConvertedMarkdown",
]
