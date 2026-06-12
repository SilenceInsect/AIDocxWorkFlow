"""Convert extracted DOCX content to Markdown with image references.

Produces a clean Markdown document where images are referenced by semantic
identifier names (e.g., `img_001_ui_prototype.png`) rather than being embedded.
OCR results are linked by the same reference names for easy cross-referencing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .docx_extractor import ExtractedDocument, ExtractedParagraph
from .image_renamer import ImageNamingResult


@dataclass
class MarkdownImageRef:
    """Represents an image reference placed in the markdown document."""

    image_ref: str
    original_index: int
    paragraph_anchor: Optional[str] = None


@dataclass
class MarkdownSection:
    """Represents a section in the converted markdown."""

    heading: str
    level: int
    content_lines: list[str] = field(default_factory=list)
    image_refs: list[MarkdownImageRef] = field(default_factory=list)


@dataclass
class ConvertedMarkdown:
    """Container for the converted markdown document."""

    content: str
    image_refs: list[MarkdownImageRef]
    sections: list[MarkdownSection]
    metadata: dict = field(default_factory=dict)


class MarkdownConverter:
    """Convert extracted DOCX content to structured Markdown.

    Transforms paragraphs, headings, and image references into clean Markdown
    with semantic image identifiers.
    """

    def __init__(self, image_refs: dict[int, str] | None = None):
        """Initialize the converter.

        Args:
            image_refs: Mapping from image index to semantic reference name.
        """
        self.image_refs: dict[int, str] = image_refs or {}

    def convert(
        self,
        doc: ExtractedDocument,
        doc_title: Optional[str] = None,
    ) -> ConvertedMarkdown:
        """Convert an extracted document to Markdown.

        Args:
            doc: The extracted document from DocxExtractor.
            doc_title: Optional document title (defaults to source filename).

        Returns:
            ConvertedMarkdown with content, sections, and image references.
        """
        lines: list[str] = []
        sections: list[MarkdownSection] = []
        current_section = MarkdownSection(heading="", level=0)
        all_image_refs: list[MarkdownImageRef] = []

        if doc_title:
            lines.append(f"# {doc_title}\n")
        elif doc.source_path:
            lines.append(f"# {Path(doc.source_path).stem}\n")

        lines.append(f"> 自动提取自 DOCX | 图片数量: {doc.get_image_count()} | 段落数: {len(doc.paragraphs)}\n")
        lines.append("---\n")

        image_placed: set[int] = set()

        for para in doc.paragraphs:
            para_text = para.text.strip()
            if not para_text:
                continue

            heading_info = self._detect_heading(para)
            if heading_info:
                if current_section.content_lines or current_section.heading:
                    sections.append(current_section)
                current_section = MarkdownSection(
                    heading=para_text,
                    level=heading_info,
                )
                lines.append(f"{'#' * heading_info} {para_text}\n")
                continue

            for img in para.images:
                if img.index not in image_placed:
                    ref_name = self.image_refs.get(
                        img.index, f"image_{img.index:03d}.png"
                    )
                    img_ref = MarkdownImageRef(
                        image_ref=ref_name,
                        original_index=img.index,
                    )
                    all_image_refs.append(img_ref)
                    image_placed.add(img.index)
                    current_section.image_refs.append(img_ref)

                    img_md = f"![{Path(ref_name).stem}](extracted_images/{ref_name})"
                    lines.append(img_md + "\n")

            md_text = self._to_markdown_line(para_text)
            lines.append(md_md_line(md_text) + "\n")
            current_section.content_lines.append(md_text)

        if current_section.content_lines or current_section.heading:
            sections.append(current_section)

        standalone_images = [
            img for img in doc.images if img.index not in image_placed
        ]
        if standalone_images:
            lines.append("\n## 其他图片\n")
            for img in standalone_images:
                ref_name = self.image_refs.get(
                    img.index, f"image_{img.index:03d}.png"
                )
                img_ref = MarkdownImageRef(image_ref=ref_name, original_index=img.index)
                all_image_refs.append(img_ref)
                img_md = f"![{Path(ref_name).stem}](extracted_images/{ref_name})"
                lines.append(img_md + "\n")

        return ConvertedMarkdown(
            content="".join(lines),
            image_refs=all_image_refs,
            sections=sections,
            metadata={
                "source_path": doc.source_path,
                "paragraph_count": len(doc.paragraphs),
                "image_count": doc.get_image_count(),
                "image_refs_used": len(all_image_refs),
            },
        )

    def _detect_heading(self, para: ExtractedParagraph) -> int | None:
        style = para.style_name or ""
        if not style:
            text = para.text
            if text and text[0] in "#*_~`":
                return None
            if re.match(r"^#{1,6}\s", text):
                return len(text) - len(text.lstrip("#"))
            return None

        style_lower = style.lower()
        if "title" in style_lower or "heading 1" in style_lower:
            return 1
        if "heading" in style_lower or "caption" in style_lower:
            m = re.search(r"heading\s*(\d)", style_lower)
            if m:
                return int(m.group(1))
        if "toc" in style_lower:
            return 1
        return None

    def _to_markdown_line(self, text: str) -> str:
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\*\*(.+?)\*\*", r"**\1**", text)
        text = re.sub(r"__(.+?)__", r"__\1__", text)
        text = re.sub(r"\*(.+?)\*", r"*\1*", text)
        text = re.sub(r"_(.+?)_", r"_\1_", text)
        return text

    def save(
        self,
        converted: ConvertedMarkdown,
        output_path: str | Path,
        insert_image_refs: bool = True,
    ):
        """Save the converted markdown to a file.

        Args:
            converted: The ConvertedMarkdown object.
            output_path: Path to write the .md file.
            insert_image_refs: Whether to include an image reference table.
        """
        path = Path(output_path)
        content = converted.content

        if insert_image_refs and converted.image_refs:
            content += "\n---\n\n## 图片索引\n\n"
            content += "| 编号 | 引用名 | 说明 |\n"
            content += "|-------|--------|------|\n"
            for ref in converted.image_refs:
                stem = Path(ref.image_ref).stem
                desc = _describe_ref(stem)
                content += f"| `{ref.original_index}` | `{ref.image_ref}` | {desc} |\n"

        path.write_text(content, encoding="utf-8")

    def save_image_map(self, output_path: str | Path):
        """Save the image reference mapping as a separate JSON file.

        Args:
            output_path: Path to save the JSON mapping.
        """
        import json
        mapping = {str(idx): ref for idx, ref in self.image_refs.items()}
        Path(output_path).write_text(
            json.dumps(mapping, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def md_md_line(text: str) -> str:
    """Wrap text in a markdown paragraph if not already a special element."""
    if not text:
        return ""
    if text.startswith("#") or text.startswith("!") or text.startswith(">"):
        return text
    return text


def _describe_ref(ref: str) -> str:
    """Generate a human-readable description from a reference name."""
    parts = ref.split("_")
    if len(parts) >= 3:
        tag = "_".join(parts[2:]).replace("-", " ")
        tag_map = {
            "ui prototype": "UI原型图",
            "flow chart": "流程图",
            "data schema": "数据结构图",
            "sequence diagram": "时序图",
            "architecture": "架构图",
            "table": "表格截图",
            "diagram": "示意图",
            "screenshot": "截图",
        }
        return tag_map.get(tag, tag.replace("_", " "))
    return ref


def convert_to_markdown(
    doc: ExtractedDocument,
    output_path: str | Path,
    image_refs: dict[int, str],
    doc_title: str | None = None,
) -> ConvertedMarkdown:
    """Convenience function to convert extracted document to Markdown.

    Args:
        doc: Extracted document.
        output_path: Path for the output .md file.
        image_refs: Mapping from image index to reference name.
        doc_title: Optional document title.

    Returns:
        ConvertedMarkdown object.
    """
    converter = MarkdownConverter(image_refs=image_refs)
    result = converter.convert(doc, doc_title=doc_title)
    converter.save(result, output_path)
    return result
