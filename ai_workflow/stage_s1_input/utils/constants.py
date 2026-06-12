"""Shared constants for Stage S1 input processing."""

import os
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[4]
WORKFLOW_ASSETS: Final[Path] = PROJECT_ROOT / "workflow_assets"

IMAGE_PREFIX: Final[str] = "img_"
IMAGE_SUBDIR: Final[str] = "extracted_images"
OCR_SUBDIR: Final[str] = "ocr_results"
RAW_SUBDIR: Final[str] = "raw"

IMAGE_REF_WIDTH: Final[int] = 3

SEMANTIC_TAGS: Final[dict[str, list[str]]] = {
    "ui_prototype": ["界面", "原型", "UI", "页面", "截图", "wireframe", "mockup", "界面原型"],
    "flow_chart": ["流程", "流程图", "flow", "流向", "步骤", "process"],
    "data_schema": ["结构", "schema", "ER图", "数据模型", "字段", "database"],
    "sequence_diagram": ["时序", "sequence", "交互", "调用", "时序图"],
    "architecture": ["架构", "architecture", "系统设计", "部署", "拓扑"],
    "table": ["表格", "table", "表单", "列表", "grid"],
    "screenshot": ["截图", "截图", "screen", "截图"],
    "diagram": ["图", "diagram", "示意", "示意图"],
}

IMAGE_TAG_KEYWORDS: list[str] = []
for tag, keywords in SEMANTIC_TAGS.items():
    IMAGE_TAG_KEYWORDS.extend(keywords)


def get_s1_output_dir(req_name: str, version: str = "v1.0") -> Path:
    """Get S1 output directory for a given requirement.

    Structure: workflow_assets/<req_name>/「S1 需求评审」/<version>/
    """
    safe_name = req_name.replace("/", "_").replace("\\", "_").strip()
    return WORKFLOW_ASSETS / safe_name / "「S1 需求评审」" / version


def image_ref_name(index: int, semantic_tag: str, extension: str = "png") -> str:
    """Generate a standardized image reference name.

    Format: img_<index>_<semantic_tag>.<ext>
    Example: img_001_ui_prototype.png
    """
    return f"{IMAGE_PREFIX}{index:03d}_{semantic_tag}.{extension.lstrip('.')}"


def ocr_result_filename(image_ref: str) -> str:
    """Generate corresponding OCR result filename for an image reference.

    Example: img_001_ui_prototype.png -> img_001_ui_prototype.json
    """
    base = Path(image_ref).stem
    return f"{base}.json"
