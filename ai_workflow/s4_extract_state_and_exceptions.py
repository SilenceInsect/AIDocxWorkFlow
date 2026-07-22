"""v12 §S4→BIZ TC 工作流 L3 拍点脚本（v12+ 强制）。

从 business_flow.md §4 层结构化清单节拍出 s4_state_and_exceptions.json，供 S6 引用。

输入：workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md
输出：workflow_assets/<req_name>/<version>/「S4 流程图导出」/s4_state_and_exceptions.json

CLI:
  python3 ai_workflow/s4_extract_state_and_exceptions.py <req_name> <version>
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent


def _parse_markdown_table(block: str) -> list[dict[str, str]]:
    """解析单段 Markdown 表格为 list[dict]。

    输入示例：
        | state | from→to | trigger | guard |
        |-------|---------|---------|-------|
        | 待支付 | [*]→待支付 | 创建订单 | - |
    """
    rows: list[dict[str, str]] = []
    lines = [l.strip() for l in block.strip().split("\n") if l.strip().startswith("|")]
    if len(lines) < 2:
        return rows
    header = [c.strip() for c in lines[0].strip("|").split("|")]
    for line in lines[2:]:  # 跳过表头 + 分隔行
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        row = {header[i]: cells[i] for i in range(len(header))}
        # 过滤占位行
        if all(c in ("-", "", "N/A") for c in cells):
            continue
        rows.append(row)
    return rows


def _extract_section(text: str, section_title: str) -> str | None:
    """抽取指定 §节 的 Markdown 内容。

    支持两种格式：
    1. 显式 §N 标题：`#### §1 状态机表（state_machines）` 或 `### §1 状态机表`
    2. 隐式 H4 标题：`#### 状态机表`（无 §N 前缀）
    """
    # 注：f-string 中 {2,4} 是 format spec，需用 {{2,4}} 转义
    hash_range = "{2,4}"
    # 格式 1: §N 标题（H2/H3/H4 都允许）
    pattern_with_section = (
        rf"^#{hash_range}\s+§\d+\s+{re.escape(section_title)}[^\n]*\n"
        r"(.*?)"
        rf"(?=^#{hash_range}\s+§\d+|^## |\Z)"
    )
    m = re.search(pattern_with_section, text, re.DOTALL | re.MULTILINE)
    if m:
        return m.group(1).strip()
    # 格式 2: 隐式标题（无 §N）
    pattern_plain = (
        rf"^#{hash_range}\s+{re.escape(section_title)}[^\n]*\n"
        r"(.*?)"
        rf"(?=^#{hash_range}\s+|^## |\Z)"
    )
    m = re.search(pattern_plain, text, re.DOTALL | re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def extract_state_and_exceptions(business_flow_md_path: Path) -> dict[str, Any]:
    """从 business_flow.md 拍出 4 层结构化数据。

    返回：
    {
      "scenarios": [...],
      "state_machines": [...],
      "exception_trees": [...],
      "risk_points": [...],
      "meta": {...}
    }
    """
    if not business_flow_md_path.exists():
        raise FileNotFoundError(f"business_flow.md not found at {business_flow_md_path}")

    text = business_flow_md_path.read_text(encoding="utf-8")

    # 1) 状态机表
    state_block = _extract_section(text, "状态机表")
    state_machines = _parse_markdown_table(state_block) if state_block else []

    # 2) 异常决策树叶子列表
    exc_block = _extract_section(text, "异常决策树叶子列表")
    exception_trees = _parse_markdown_table(exc_block) if exc_block else []

    # 3) 风险点 ID
    risk_block = _extract_section(text, "风险点 ID")
    risk_points = _parse_markdown_table(risk_block) if risk_block else []

    # 4) 场景清单
    scen_block = _extract_section(text, "场景清单")
    scenarios = _parse_markdown_table(scen_block) if scen_block else []

    # 兼容：若没 §4 层结构化清单 节，尝试从 risk_points 解析（兼容旧版 business_flow.json）
    if not risk_points and not scenarios:
        # 尝试从 business_flow.json 拍
        json_path = business_flow_md_path.parent / "business_flow.json"
        if json_path.exists():
            data = json.loads(json_path.read_text(encoding="utf-8"))
            risk_points = data.get("risk_points", [])

    return {
        "meta": {
            "extracted_at": datetime.now().isoformat(timespec="seconds"),
            "source_file": str(business_flow_md_path.relative_to(_ROOT)) if _ROOT in business_flow_md_path.parents else str(business_flow_md_path),
            "scenario_count": len(scenarios),
            "state_machine_count": len(state_machines),
            "exception_tree_leaf_count": len(exception_trees),
            "risk_point_count": len(risk_points),
            "has_4_layer_section": bool(scen_block or state_block or exc_block or risk_block),
        },
        "scenarios": scenarios,
        "state_machines": state_machines,
        "exception_trees": exception_trees,
        "risk_points": risk_points,
    }


def main(req_name: str, version: str) -> int:
    assets_root = _ROOT / "workflow_assets" / req_name / version / "「S4 流程图导出」"
    bf_path = assets_root / "business_flow.md"
    output_path = assets_root / "s4_state_and_exceptions.json"

    if not bf_path.exists():
        print(f"❌ {bf_path} 不存在")
        return 1

    print(f"📖 读取 {bf_path}")
    result = extract_state_and_exceptions(bf_path)
    print(f"   scenarios: {result['meta']['scenario_count']}")
    print(f"   state_machines: {result['meta']['state_machine_count']}")
    print(f"   exception_trees: {result['meta']['exception_tree_leaf_count']}")
    print(f"   risk_points: {result['meta']['risk_point_count']}")
    print(f"   含 §4 层结构化清单: {result['meta']['has_4_layer_section']}")

    if not result["meta"]["has_4_layer_section"]:
        print(f"⚠️  business_flow.md 缺 §4 层结构化清单 节（v12 强制输出）")
        print(f"   → 请按 S4 SKILL §v12 补该节后重跑")

    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✅ 已写入 {output_path} ({output_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        mock_path = Path("/tmp/s4_mock_business_flow.md")
        mock_path.write_text("""# S4 业务流程图 — 测试
## 1. 核心业务流程图
... (省略)
### 4 层结构化清单

#### §1 状态机表（state_machines）
| machine_id | state | from→to | trigger | guard |
|------------|-------|---------|---------|-------|
| SM-001 | 待支付 | [*]→待支付 | 创建订单 | - |
| SM-001 | 已支付 | 支付中→已支付 | 回调成功 | - |

#### §2 异常决策树叶子列表（exception_trees）
| tree_id | leaf_id | condition | action |
|---------|---------|-----------|--------|
| ET-001 | ET-001-Insuff | 余额不足 | UI 提示 |

#### §3 风险点 ID（risk_points）
| risk_id | name | leaf | mitigation |
|---------|------|------|------------|
| RP-001 | 支付超时补单 | S4-FC-001-Timeout | 后台轮询 |

#### §4 场景清单（scenarios）
| scenario_id | name | steps | module |
|-------------|------|-------|--------|
| SC-001 | 正常购买游戏币 | 浏览→详情→确认→支付→到账 | BIZ |
""", encoding="utf-8")
        result = extract_state_and_exceptions(mock_path)
        assert result["meta"]["scenario_count"] == 1, f"scenarios 应为 1, 实际 {result['meta']['scenario_count']}"
        assert result["meta"]["state_machine_count"] == 2, f"state_machines 应为 2, 实际 {result['meta']['state_machine_count']}"
        assert result["meta"]["exception_tree_leaf_count"] == 1, f"exception_trees 应为 1, 实际 {result['meta']['exception_tree_leaf_count']}"
        assert result["meta"]["risk_point_count"] == 1, f"risk_points 应为 1, 实际 {result['meta']['risk_point_count']}"
        print("✅ s4_extract_state_and_exceptions self-test: 通过")
        sys.exit(0)
    if len(sys.argv) >= 3:
        sys.exit(main(sys.argv[1], sys.argv[2]))
    print("Usage: python3 s4_extract_state_and_exceptions.py <req_name> <version>")
    print("       python3 s4_extract_state_and_exceptions.py --self-test")
    sys.exit(1)