"""v12 §S3→TC 工作流 L3 拍点脚本（v12+ 强制）。

从 prototype.md §UI 节点清单节拍出结构化 ui_nodes.json，供 S6 引用。

输入：workflow_assets/<req_name>/<version>/「S3 原型导出」/prototype.md
输出：workflow_assets/<req_name>/<version>/「S3 原型导出」/ui_nodes.json

CLI:
  python3 ai_workflow/s3_extract_ui_nodes.py <req_name> <version>
  python3 ai_workflow/s3_extract_ui_nodes.py 游戏道具商城系统 v3.01
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent


def _parse_ui_node_block(page_id: str, page_name: str, block: str) -> list[dict[str, Any]]:
    """解析单页面的 UI 节点清单块（Markdown 列表格式）。

    输入格式示例：
        #### P-001 商城首页
        - 顶部: [搜索框] [分类导航(武器/时装/坐骑/消耗品/礼包)]
        - 中部: [热门推荐列表(前10个,按销量)]
        - 下部: [分页列表(每页20个,道具卡片N)]
        - 弹窗: 无
        - 状态: 默认 / 加载中 / 错误
    """
    nodes: list[dict[str, Any]] = []
    section_seq = 0
    for line in block.strip().split("\n"):
        line = line.strip()
        if not line.startswith("-"):
            continue
        # 解析 - <区域>: [节点1] [节点2(描述)]
        m = re.match(r"^- ([^:]+):\s*(.*)$", line)
        if not m:
            continue
        section = m.group(1).strip()
        content = m.group(2).strip()
        section_seq += 1
        if content == "无":
            continue
        # 解析 [节点名(描述)] 或 [节点名]
        for node_match in re.finditer(r"\[([^\]]+)\]", content):
            node_str = node_match.group(1)
            # 推断 node_type
            if any(k in node_str for k in ["按钮", "购买", "确认", "取消", "搜索", "支付", "放行", "拒绝"]):
                node_type = "button"
            elif any(k in node_str for k in ["输入", "选择器", "数量", "关键字"]):
                node_type = "input"
            elif any(k in node_str for k in ["列表", "分类", "队列", "推荐", "分页"]):
                node_type = "list"
            elif any(k in node_str for k in ["导航", "切换", "Tab", "面包屑"]):
                node_type = "navigator"
            elif any(k in node_str for k in ["弹窗", "提示", "Loading", "Toast"]):
                node_type = "dialog"
            elif any(k in node_str for k in ["徽章", "指示器", "红点", "库存", "VIP"]):
                node_type = "indicator"
            else:
                node_type = "display"
            # 抽 (描述)
            desc_m = re.search(r"\(([^)]+)\)", node_str)
            label = re.sub(r"\([^)]*\)", "", node_str).strip()
            desc = desc_m.group(1).strip() if desc_m else ""
            nodes.append({
                "node_id": f"{page_id}-{node_type}-{len([n for n in nodes if n.get('node_type') == node_type]) + 1:02d}",
                "page_id": page_id,
                "node_type": node_type,
                "label": label,
                "desc": desc,
                "section": section,
            })
    return nodes


def extract_ui_nodes(prototype_md_path: Path) -> dict[str, Any]:
    """从 prototype.md 拍出 UI 节点清单 + 页面状态机。

    返回结构：
    {
      "pages": [
        {"page_id": "P-001", "page_name": "商城首页", "module": "UI", "nodes": [...]}
      ],
      "page_states": {...},
      "meta": {...}
    }
    """
    if not prototype_md_path.exists():
        raise FileNotFoundError(f"prototype.md not found at {prototype_md_path}")

    text = prototype_md_path.read_text(encoding="utf-8")

    # 解析 §页面清单（必须存在）
    pages: list[dict[str, Any]] = []
    in_page_list = False
    for line in text.split("\n"):
        if line.strip().startswith("## 1. 页面清单"):
            in_page_list = True
            continue
        if in_page_list and line.strip().startswith("## 2."):
            in_page_list = False
            break
        if in_page_list and line.startswith("|") and not line.startswith("|---"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 5 and parts[0].startswith("P-"):
                pages.append({
                    "page_id": parts[0],
                    "page_name": parts[1],
                    "module": parts[2],
                    "entry": parts[3],
                    "story_id": parts[4],
                })

    # 解析 §UI 节点清单（v12 强制输出，可选）
    # 兼容 H2: ## §UI 节点清单 和 H3: ### UI 节点清单 两种格式
    in_ui_node_list = False
    page_blocks: dict[str, list[str]] = {}
    current_page_id = None
    current_block_lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        # 进入节：H2 ## §UI 节点清单 或 H3 ### UI 节点清单
        # 【关键】先清 in_ui，再检查 enter——防止同一行既触发 enter 又触发 exit
        if stripped.startswith("## §UI 节点清单") or stripped.startswith("### UI 节点清单"):
            in_ui_node_list = True
            continue  # 跳过本次迭代，不检查 exit
        if in_ui_node_list:
            # 退出节：下一节标题（H2 ## 开头的非节点行）
            if stripped.startswith("## ") and not stripped.startswith("### "):
                in_ui_node_list = False
                if current_page_id and current_block_lines:
                    page_blocks[current_page_id] = current_block_lines
                break
            # 新的页面标题 ### P-XXX 或 #### P-XXX（H3 / H4 都允许）
            page_h = re.match(r"^#{3,4}\s+(P-\d+)\s+(.*)$", line)
            if page_h:
                if current_page_id and current_block_lines:
                    page_blocks[current_page_id] = current_block_lines
                current_page_id = page_h.group(1)
                current_page_name = page_h.group(2).strip()
                current_block_lines = []
            elif current_page_id and stripped.startswith("-"):
                current_block_lines.append(line)
    # 兜底：for 循环结束后如果还在 in_ui_node_list 也要保存最后一块
    if in_ui_node_list and current_page_id and current_block_lines:
        page_blocks[current_page_id] = current_block_lines

    # 合并：把 UI 节点合并到 pages
    for p in pages:
        pid = p["page_id"]
        if pid in page_blocks:
            p["nodes"] = _parse_ui_node_block(pid, p["page_name"], "\n".join(page_blocks[pid]))
        else:
            p["nodes"] = []

    # 拍出 状态机（保留 Mermaid stateDiagram-v2 块）
    page_states: dict[str, Any] = {}
    state_blocks = re.findall(r"```mermaid\s*\nstateDiagram-v2\s*\n(.*?)\n```", text, re.DOTALL)
    for block in state_blocks:
        transitions: list[dict[str, str]] = []
        for line in block.strip().split("\n"):
            line = line.strip()
            m = re.match(r"^(\S+)\s*-->\s*(\S+)(?:\s*:\s*(.*))?$", line)
            if m:
                transitions.append({
                    "from": m.group(1).replace("[*]", "INIT"),
                    "to": m.group(2).replace("[*]", "END"),
                    "trigger": (m.group(3) or "").strip(),
                })
        if transitions:
            page_states["state_machine"] = transitions

    return {
        "meta": {
            "extracted_at": datetime.now().isoformat(timespec="seconds"),
            "source_file": str(prototype_md_path.relative_to(_ROOT)) if _ROOT in prototype_md_path.parents else str(prototype_md_path),
            "page_count": len(pages),
            "ui_node_count": sum(len(p.get("nodes", [])) for p in pages),
            "has_ui_node_list": bool(page_blocks),
        },
        "pages": pages,
        "page_states": page_states,
    }


def main(req_name: str, version: str) -> int:
    assets_root = _ROOT / "workflow_assets" / req_name / version / "「S3 原型导出」"
    prototype_path = assets_root / "prototype.md"
    output_path = assets_root / "ui_nodes.json"

    if not prototype_path.exists():
        print(f"❌ {prototype_path} 不存在")
        return 1

    print(f"📖 读取 {prototype_path}")
    result = extract_ui_nodes(prototype_path)
    print(f"   页面数: {result['meta']['page_count']}")
    print(f"   UI 节点数: {result['meta']['ui_node_count']}")
    print(f"   包含 §UI 节点清单: {result['meta']['has_ui_node_list']}")

    if not result["meta"]["has_ui_node_list"]:
        print(f"⚠️  prototype.md 缺 §UI 节点清单 节（v12 强制输出）")
        print(f"   → 请按 S3 SKILL §v12 补该节后重跑")

    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✅ 已写入 {output_path} ({output_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        # self-test：用一份 mock prototype.md 验证
        mock_path = Path("/tmp/s3_mock_prototype.md")
        mock_path.write_text("""# S3 原型导出 — 测试
## 1. 页面清单
| 页面 ID | 页面名 | 所属模块 | 入口 | 关联 Story |
|---------|--------|----------|------|-----------|
| P-001 | 商城首页 | UI | 主菜单 | UI-001 |
| P-002 | 道具详情页 | UI | 首页 | UI-001 |

### UI 节点清单

#### P-001 商城首页
- 顶部: [搜索框] [分类导航(武器/时装)]
- 中部: [热门推荐列表(前10个)]
- 弹窗: 无

#### P-002 道具详情页
- 顶部: [道具图] [名称]
- 中部: [价格] [购买按钮]
- 数量: [选择器(1-99)]
- 弹窗: 无

## 4. 状态机
（省略）
""", encoding="utf-8")
        result = extract_ui_nodes(mock_path)
        assert result["meta"]["page_count"] == 2, f"page_count 应为 2, 实际 {result['meta']['page_count']}"
        assert result["meta"]["ui_node_count"] > 0, "应有 UI 节点"
        # 验证节点类型推断
        p002_nodes = result["pages"][1]["nodes"]
        node_types = {n["node_type"] for n in p002_nodes}
        assert "button" in node_types, f"应有 button 类型, 实际 {node_types} (P-002 nodes: {p002_nodes})"
        assert "input" in node_types, f"应有 input 类型（数量选择器）, 实际 {node_types}"
        print("✅ s3_extract_ui_nodes self-test: 通过")
        sys.exit(0)
    if len(sys.argv) >= 3:
        sys.exit(main(sys.argv[1], sys.argv[2]))
    print("Usage: python3 s3_extract_ui_nodes.py <req_name> <version>")
    print("       python3 s3_extract_ui_nodes.py --self-test")
    sys.exit(1)