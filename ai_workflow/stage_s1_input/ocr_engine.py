"""OCR engine using Tesseract for image text extraction.

Provides structured OCR results with confidence scores and extracted elements
for semantic image classification.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
import io

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    pytesseract = None
    Image = None


@dataclass
class OCRResult:
    """Structured OCR result for a single image."""

    image_ref: str
    image_path: str
    ocr_text: str
    extracted_elements: list[str] = field(default_factory=list)
    confidence: float = 0.0
    page: int = 1
    language: str = "chi_sim+eng"
    raw_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class OCREngine:
    """Tesseract-based OCR engine for extracting text from images.

    Performs OCR on extracted document images and produces structured JSON results
    suitable for downstream AI processing.
    """

    DEFAULT_LANG: str = "chi_sim+eng"
    DEFAULT_CONFIG: str = "--psm 3 --oem 3"

    def __init__(self, lang: str | None = None):
        """Initialize OCR engine.

        Args:
            lang: Tesseract language pack (default: chi_sim+eng for Chinese+English).
        """
        if pytesseract is None or Image is None:
            raise ImportError(
                "tesseract-ocr dependencies are required.\n"
                "Install with: pip install pytesseract Pillow\n"
                "Also install Tesseract OCR engine:\n"
                "  macOS: brew install tesseract tesseract-lang\n"
                "  Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-ocr-eng tesseract-ocr-ocr-chi-sim\n"
                "  Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki"
            )
        self.lang = lang or self.DEFAULT_LANG
        self._tesseract_cmd = shutil.which("tesseract")
        if not self._tesseract_cmd:
            raise RuntimeError(
                "Tesseract binary not found. Install tesseract-ocr first:\n"
                "  macOS: brew install tesseract tesseract-lang\n"
                "  Ubuntu: sudo apt install tesseract-ocr"
            )

    def recognize(
        self,
        image_path: str | Path | bytes,
        image_ref: str,
        page: int = 1,
    ) -> OCRResult:
        """Recognize text from an image.

        Args:
            image_path: Path to image file or raw image bytes.
            image_ref: The reference name for this image (e.g. 'img_001_ui_prototype.png').
            page: Page number in the source document (default: 1).

        Returns:
            OCRResult with extracted text, elements, and confidence.
        """
        if isinstance(image_path, bytes):
            return self._recognize_bytes(image_path, image_ref, page)
        return self._recognize_file(Path(image_path), image_ref, page)

    def _recognize_file(self, path: Path, image_ref: str, page: int) -> OCRResult:
        img = Image.open(path)
        return self._process_image(img, str(path), image_ref, page)

    def _recognize_bytes(self, data: bytes, image_ref: str, page: int) -> OCRResult:
        img = Image.open(io.BytesIO(data))
        return self._process_image(img, "", image_ref, page)

    def _process_image(self, img: Image.Image, image_path: str, image_ref: str, page: int) -> OCRResult:
        enhanced = self._preprocess(img)

        raw_data = pytesseract.image_to_data(
            enhanced,
            lang=self.lang,
            config=self.DEFAULT_CONFIG,
            output_type=pytesseract.Output.DICT,
        )

        words = []
        confidences = []
        for i, conf in enumerate(raw_data.get("conf", [])):
            if conf > 0:
                text = raw_data["text"][i].strip()
                if text:
                    words.append(text)
                    confidences.append(float(conf))

        ocr_text = " ".join(words)
        avg_conf = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

        lines_data = pytesseract.image_to_data(
            enhanced,
            lang=self.lang,
            config=self.DEFAULT_CONFIG,
            output_type=pytesseract.Output.STRING,
        )
        line_based_data = pytesseract.image_to_string(
            enhanced,
            lang=self.lang,
            config="--psm 4 --oem 3",
        )

        result = OCRResult(
            image_ref=image_ref,
            image_path=image_path,
            ocr_text=ocr_text or line_based_data.strip(),
            confidence=round(avg_conf, 4),
            page=page,
            language=self.lang,
            raw_data={"lines": lines_data},
            extracted_elements=words[:20],
        )
        return result

    def _preprocess(self, img: Image.Image) -> Image.Image:
        if img.mode != "RGB":
            img = img.convert("RGB")
        gray = img.convert("L")
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(1.5)
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        return sharpened

    def recognize_batch(
        self,
        image_dir: str | Path,
        prefix: str = "img_",
        page_start: int = 1,
    ) -> list[OCRResult]:
        """Recognize all images in a directory.

        Images are matched by the given prefix and processed in sorted order.

        Args:
            image_dir: Directory containing image files.
            prefix: Filename prefix to match (default: 'img_').
            page_start: Starting page number for numbering.

        Returns:
            List of OCRResult for each matched image.
        """
        dir_path = Path(image_dir)
        image_files = sorted(
            [f for f in dir_path.iterdir() if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}]
        )

        results: list[OCRResult] = []
        page = page_start
        for img_file in image_files:
            if prefix not in img_file.name:
                continue
            try:
                result = self.recognize(img_file, img_file.name, page=page)
                results.append(result)
            except Exception as e:
                print(f"Warning: failed to OCR {img_file.name}: {e}")
            page += 1

        return results

    def save_results(
        self,
        results: list[OCRResult],
        output_dir: str | Path,
    ) -> dict[str, str]:
        """Save OCR results as JSON files to a directory.

        Each result is saved as <image_ref_without_ext>.json.

        Args:
            results: List of OCRResult objects.
            output_dir: Directory to save JSON files to.

        Returns:
            Mapping of image_ref to saved JSON file path.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        index_map: dict[str, str] = {}
        for result in results:
            json_name = Path(result.image_ref).stem + ".json"
            json_path = out / json_name
            json_path.write_text(result.to_json(), encoding="utf-8")
            index_map[result.image_ref] = str(json_path)

        return index_map

    def quick_preview(self, image_path: str | Path) -> str:
        """Get a quick text preview from an image without full processing.

        Useful for generating semantic labels before full OCR.

        Args:
            image_path: Path to the image.

        Returns:
            Short text extracted from the image.
        """
        img = Image.open(image_path)
        return pytesseract.image_to_string(img, lang=self.lang).strip()[:200]


def run_ocr_on_images(
    image_dir: str | Path,
    output_dir: str | Path,
    image_refs: list[str] | None = None,
) -> list[OCRResult]:
    """Convenience function to run OCR on all images in a directory.

    Args:
        image_dir: Directory containing extracted images.
        output_dir: Directory to save OCR JSON results.
        image_refs: Optional list of specific image refs to process.

    Returns:
        List of OCRResult objects.
    """
    engine = OCREngine()
    if image_refs:
        results = []
        for ref in image_refs:
            img_path = Path(image_dir) / ref
            if img_path.exists():
                results.append(engine.recognize(img_path, ref))
    else:
        results = engine.recognize_batch(image_dir)
    engine.save_results(results, output_dir)
    return results
