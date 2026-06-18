"""Shared constants for Stage S1 input processing."""

import os
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
WORKFLOW_ASSETS: Final[Path] = PROJECT_ROOT / "workflow_assets"

IMAGE_PREFIX: Final[str] = "img_"
IMAGE_SUBDIR: Final[str] = "extracted_images"
OCR_SUBDIR: Final[str] = "ocr_results"
RAW_SUBDIR: Final[str] = "raw"

IMAGE_REF_WIDTH: Final[int] = 3

SEMANTIC_TAGS: Final[dict[str, list[str]]] = {
    # ── UI 原型 — 游戏 PRD 最常见，需覆盖 UI 交互稿、截图、Mockup ──
    "ui_prototype": [
        # 通用 UI 词
        "界面", "原型", "UI", "页面", "截图", "wireframe", "mockup", "界面原型",
        "界面设计", "交互稿", "高保真", "低保真", "UI稿",
        # 游戏 PRD 典型 UI 元素词
        "按钮", "弹窗", "商城", "列表", "道具", "购买", "支付", "道具栏",
        "背包", "装备", "技能", "任务", "活动", "签到", "邮件", "商城首页",
        "详情页", "分类", "标签页", "Tab", "导航", "侧边栏", "菜单",
        "输入框", "下拉框", "单选", "复选", "滑块", "进度条", "loading",
        "头像", "昵称", "等级", "金币", "钻石", "元宝", "VIP", "首充",
        "确认", "取消", "关闭", "返回", "下一步", "完成", "提交", "重置",
        # 常见截图描述
        "示意图", "效果如图", "如图所示", "见下图", "参考图",
        "screen", "screenshot", "截图",
    ],
    # ── 流程图 ──
    "flow_chart": [
        "流程", "流程图", "flow", "流向", "步骤", "process",
        "流程设计", "业务流程", "处理流程", "操作流程", "执行流程",
        "决策", "判断", "分支", "循环", "开始", "结束", "入口", "出口",
        "并行", "串行", "时序", "顺序", "条件",
        "泳道", "跨泳道", "activity", "workflow",
    ],
    # ── 数据结构 / ER 图 ──
    "data_schema": [
        "结构", "schema", "ER图", "数据模型", "字段", "database",
        "表结构", "数据库设计", "实体", "属性", "关联", "关系",
        "字段定义", "数据类型", "主键", "外键", "索引", "约束",
        "表设计", "对象模型", "类图", "UML",
    ],
    # ── 时序图 ──
    "sequence_diagram": [
        "时序", "sequence", "交互", "调用", "时序图",
        "请求", "响应", "回调", "消息", "参与者", "participant",
        "时序设计", "交互流程", "调用链", "API时序",
        "client", "server", "service", "module",
    ],
    # ── 系统架构 ──
    "architecture": [
        "架构", "architecture", "系统设计", "部署", "拓扑",
        "架构图", "系统架构", "部署架构", "网络拓扑", "服务架构",
        "微服务", "模块划分", "分层架构", "三层架构", "B/S", "C/S",
    ],
    # ── 表格 / 表单 / 列表 ──
    "table": [
        "表格", "table", "表单", "列表", "grid",
        "配置表", "数据表", "对照表", "属性表", "规格表",
        "字段列表", "数据列表", "枚举值", "选项列表",
    ],
    # ── 其他图片（截图/照片）──
    "screenshot": [
        "截图", "screen", "截图",
        "实拍", "真实截图", "线上截图", "游戏截图",
    ],
    # ── 其他图（通用兜底）──
    "diagram": [
        "图", "diagram", "示意", "示意图",
        "图示", "图例", "说明图", "参考图",
    ],
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
