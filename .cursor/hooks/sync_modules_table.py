#!/usr/bin/env python3
"""Cursor afterFileEdit hook: sync MODULES.md 副本 (支持多区块协议).

Trigger:
  - 任何 .md / .mdc 文件被编辑后,扫描是否含 [MODULES_SYNC id=...] 区块
  - 同时,MODULES.md 自身变化时,触发所有副本重同步

Mechanism (Marker Protocol v2):
  - 副本文件嵌入多个 [MODULES_SYNC id=<id> src=... sha256=...] ... [END: id] 区块
  - id 可选值: §1(= sections_table 总表) | §3.5(= cross_scene 交叉场景判定)
                | §4.11.2(= hint_ui_boundary HINT vs UI 边界)
  - 区块头部带 src + sha256 + last_sync 元数据
  - 任何被改过(离开同步状态)的副本,强制覆盖并写 diff 日志
  - 向后兼容 v1 单区块 (无 id 参数) → 视为 id=§1

Guard (防级联触发):
  - 钩子写出的副本文件,带 [MODULES_SYNC_GUARD] 标记
  - 二次进入钩子时检测该标记,直接 no-op 退出

Output:
  - 副本文件:被覆盖,顶部加红色 banner
  - 日志:.cursor/sync_logs/modules_sync_YYYYMMDD.jsonl
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ===== 配置 =====
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
MODULES_MD = (PROJECT_ROOT / ".cursor" / "MODULES.md").resolve()
# SYNC_LOG_DIR 在运行时再算, 避免 monkey-patch 失效
SYNC_LOG_DIR = None  # type: ignore[assignment]

# 起止标识 (HTML 标签配对 + 视觉 Banner) — 支持多区块
# 设计: 用 <aside> 真实 HTML 标签,attribute 携带 metadata,Markdown 渲染透明
# block_id 允许中文 § (例如 §1, §3.5, §4.11.2)
# sha256 字段允许占位符 (如 INIT_seed) 或真实 hex
#
# 支持 3 个历史协议版本(自动从旧到新迁移):
#   v1:  <!-- BEGIN: MODULES_TABLE_SYNC ... --> ... <!-- END: MODULES_TABLE_SYNC -->
#   v2:  <!-- BEGIN: MODULES_SYNC id=§X ... --> ... <!-- END: MODULES_SYNC id=§X -->
#   v3:  <aside data-modules-sync-block="§X" ...> ... </aside>   (当前协议)
#
MARKER_BEGIN_RE = re.compile(
    r'<aside\s+data-modules-sync-block="([^"]+)"'
    r'(?:\s+data-src="[^"]*")?'
    r'(?:\s+data-sha256="[A-Za-z0-9]+")?'
    r'(?:\s+data-synced-at="[^"]*")?'
    r'\s*>'
)
MARKER_END_RE = re.compile(r'</aside\s*>')

# v1 协议别名 (单区块, 无 id, 视为 §1)
MARKER_BEGIN_V1 = "<!-- BEGIN: MODULES_TABLE_SYNC"
MARKER_END_V1 = "<!-- END: MODULES_TABLE_SYNC -->"
MARKER_BEGIN_V1_RE = re.compile(r"<!-- BEGIN: MODULES_TABLE_SYNC\b[^>]*?-->")
MARKER_END_V1_RE = re.compile(r"<!-- END: MODULES_TABLE_SYNC\b[^>]*?-->")

# v2 协议别名 (注释 + id=) - 我们之前迭代过的版本
MARKER_BEGIN_V2_RE = re.compile(
    r"<!-- BEGIN: MODULES_SYNC\s+id=([^\s]+)(?:\s+src=[^\s]+)?(?:\s+sha256=[A-Za-z0-9_]+)?\s*-->"
)
MARKER_END_V2_RE = re.compile(
    r"<!-- END: MODULES_SYNC\s+id=([^\s]+)\s*-->"
)

GUARD_MARKER = "<!-- MODULES_SYNC_GUARD: auto-written, do not edit manually -->"
RED_BANNER = "> **🔴 [自动同步区块 `{block_id}`]** 本区块由 `{src}` 自动生成,人工修改将被覆盖。源 SHA: `{sha}` · 同步时间: `{ts}`"

# 扫描范围:哪些文件可能含副本区块
SCAN_GLOBS = [
    ".cursor/skills/**/*.md",
    ".cursor/rules/**/*.mdc",
    "workflow_assets/module_templates/**/*.md",
    "README.md",
    "CHANGELOG.md",
]


# ===== 区块定义 =====
# 每个 block_id 对应一个 MODULES.md 章节抽取函数
BLOCK_DEFINITIONS = {
    # §1 8 模块总表(含 ID 前缀说明段)
    "§1": {
        "src": ".cursor/MODULES.md#§1",
        "label": "8 模块总表",
        "extractor": "_extract_section_1_table",
    },
    # §3.5 交叉场景归属判定规则
    "§3.5": {
        "src": ".cursor/MODULES.md#§3.5",
        "label": "交叉场景归属判定规则",
        "extractor": "_extract_section_3_5_cross_scene",
    },
    # §4.11.2 HINT vs UI 关键边界隔离规则
    "§4.11.2": {
        "src": ".cursor/MODULES.md#§4.11.2",
        "label": "HINT vs UI 关键边界隔离规则",
        "extractor": "_extract_section_4_11_2_hint_ui",
    },
}


# ===== 抽取器 =====
def _read_modules_md() -> str:
    return MODULES_MD.read_text(encoding="utf-8")


def _extract_section(md_text: str, section_header_regex: str, next_section_regex: str = r"\n(?:##|###) ") -> str:
    """通用抽取: 从 ## 或 ### 标题到下一个 ##/### 之间的内容。"""
    m = re.search(section_header_regex, md_text)
    if not m:
        raise RuntimeError(f"Section not found: {section_header_regex}")
    start = m.start()
    end_m = re.search(next_section_regex, md_text[m.end():])
    end = m.end() + end_m.start() if end_m else len(md_text)
    return md_text[start:end].rstrip()


def _extract_section_1_table() -> str:
    """§1 8 模块总表 + ID 前缀说明。"""
    md = _read_modules_md()
    section = _extract_section(md, r"## 1\. 8 模块总表\s*\n")

    # 追加 ID 前缀说明段
    id_prefix = re.search(
        r"> \*\*ID 前缀说明\*\*：\s*\n(.*?)(?=\n\n|\n---|\Z)", md, re.DOTALL
    )
    if id_prefix:
        section += "\n\n" + id_prefix.group(0).rstrip()
    return section


def _extract_section_3_5_cross_scene() -> str:
    """§3.5 交叉场景归属判定规则。"""
    md = _read_modules_md()
    return _extract_section(md, r"## 3\.5 交叉场景归属判定规则.*?\n")


def _extract_section_4_11_2_hint_ui() -> str:
    """§4.11.2 HINT vs UI 关键边界隔离规则。"""
    md = _read_modules_md()
    return _extract_section(md, r"### 4\.11\.2 关键边界隔离规则.*?\n")


EXTRACTORS = {
    "_extract_section_1_table": _extract_section_1_table,
    "_extract_section_3_5_cross_scene": _extract_section_3_5_cross_scene,
    "_extract_section_4_11_2_hint_ui": _extract_section_4_11_2_hint_ui,
}


def extract_block(block_id: str) -> str:
    """根据 block_id 抽取对应章节。"""
    defn = BLOCK_DEFINITIONS.get(block_id)
    if not defn:
        raise RuntimeError(f"Unknown block_id: {block_id}")
    extractor_name = defn["extractor"]
    extractor = EXTRACTORS[extractor_name]
    return extractor()


# ===== 区块构建 =====
def build_synced_block(block_id: str, content_md: str, src_sha: str) -> str:
    """构造注入到副本的完整区块（v2 协议: HTML 标签配对 + attribute metadata）。"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    defn = BLOCK_DEFINITIONS[block_id]
    src_ref = defn["src"]
    banner = RED_BANNER.format(block_id=block_id, src=src_ref, sha=src_sha[:12], ts=ts)
    return (
        f'<aside data-modules-sync-block="{block_id}" '
        f'data-src="{src_ref}" '
        f'data-sha256="{src_sha}" '
        f'data-synced-at="{ts}">\n'
        f"{banner}\n\n"
        f"{content_md}\n"
        f"</aside>"
    )


# ===== 区块定位 =====
def find_all_marker_blocks(content: str) -> list[tuple[str, int, int]]:
    """查找文件中所有 MARKER 区块, 返回 [(block_id, start, end), ...]。

    支持 3 个协议版本, 同一文件可能混合多个协议 (升级中状态):
      v3: <aside data-modules-sync-block="§X"> ... </aside>   (当前)
      v2: <!-- BEGIN: MODULES_SYNC id=§X --> ... <!-- END: MODULES_SYNC id=§X -->
      v1: <!-- BEGIN: MODULES_TABLE_SYNC --> ... <!-- END: MODULES_TABLE_SYNC -->  (视为 §1)

    返回所有协议的区块, 不互斥 fallback。
    """
    results: list[tuple[str, int, int]] = []

    # v3 协议
    for m_begin in MARKER_BEGIN_RE.finditer(content):
        block_id = m_begin.group(1)
        m_end = MARKER_END_RE.search(content, m_begin.end())
        if m_end:
            results.append((block_id, m_begin.start(), m_end.end()))

    # v2 协议 (HTML 注释 + id=)
    for m_begin in MARKER_BEGIN_V2_RE.finditer(content):
        block_id = m_begin.group(1)
        m_end = MARKER_END_V2_RE.search(content, m_begin.end())
        if m_end:
            # 避免与 v3 位置重叠
            if not any(s <= m_begin.start() < e for _, s, e in results):
                results.append((block_id, m_begin.start(), m_end.end()))

    # v1 协议 (HTML 注释对, 无 id, 视为 §1)
    for m_begin in MARKER_BEGIN_V1_RE.finditer(content):
        m_end = MARKER_END_V1_RE.search(content, m_begin.end())
        if m_end:
            if not any(s <= m_begin.start() < e for _, s, e in results):
                results.append(("§1", m_begin.start(), m_end.end()))

    # 按 start 排序
    results.sort(key=lambda x: x[1])
    return results


def find_marker_block(content: str, block_id: str = "§1") -> tuple[int, int] | None:
    """查找指定 id 的 MARKER 区块位置。返回 (start, end_exclusive)。"""
    all_blocks = find_all_marker_blocks(content)
    for bid, s, e in all_blocks:
        if bid == block_id:
            return (s, e)
    return None


# ===== 注入 =====
def inject_block_into_content(
    content: str, block_id: str, new_block: str
) -> str:
    """将新区块注入到内容中。返回新内容。"""
    block_range = find_marker_block(content, block_id)
    if block_range:
        start, end = block_range
        return content[:start] + new_block + content[end:]
    else:
        # 追加到文件末尾
        sep = "\n\n" if not content.endswith("\n") else "\n"
        return content + sep + new_block + "\n"


def inject_into_file(target: Path, block_id: str, content_md: str, src_sha: str) -> tuple[bool, str]:
    """将同步区块注入到目标文件。返回 (是否修改, 旧区块 SHA12)。"""
    content = target.read_text(encoding="utf-8")
    new_block = build_synced_block(block_id, content_md, src_sha)

    old_summary = ""
    block_range = find_marker_block(content, block_id)
    if block_range:
        start, end = block_range
        old = content[start:end]
        old_summary = hashlib.sha256(old.encode("utf-8")).hexdigest()[:12]
        new_content = content[:start] + new_block + content[end:]
    else:
        old_summary = "(none)"
        sep = "\n\n" if not content.endswith("\n") else "\n"
        new_content = content + sep + new_block + "\n"

    # 加 GUARD 标记防级联
    if GUARD_MARKER not in new_content:
        new_content = GUARD_MARKER + "\n" + new_content

    target.write_text(new_content, encoding="utf-8")
    return (True, old_summary)


# ===== 副本扫描 =====
def discover_sync_targets() -> list[Path]:
    """扫描项目中所有可能含副本区块的 .md / .mdc 文件。"""
    targets: set[Path] = set()
    for pattern in SCAN_GLOBS:
        for p in PROJECT_ROOT.glob(pattern):
            if p.is_file() and p != MODULES_MD:
                targets.add(p)
    return sorted(targets)


def discover_existing_copies() -> list[Path]:
    """只扫描已含 MARKER 的副本文件（即已经被同步过的）。"""
    def _has_any_marker(text: str) -> bool:
        return (
            MARKER_BEGIN_RE.search(text) is not None
            or MARKER_BEGIN_V2_RE.search(text) is not None
            or MARKER_BEGIN_V1 in text
        )
    return [
        p for p in discover_sync_targets()
        if _has_any_marker(p.read_text(encoding="utf-8", errors="ignore"))
    ]


# ===== 日志 =====
def write_log(entries: list[dict]) -> None:
    log_dir = PROJECT_ROOT / ".cursor" / "sync_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"modules_sync_{datetime.now():%Y%m%d}.jsonl"
    with log_file.open("a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


# ===== 主流程 =====
def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return 0

    file_path_str = payload.get("file_path", "")
    edited_file = Path(file_path_str).resolve() if file_path_str else None

    if not edited_file or not edited_file.exists():
        return 0

    # 统一用 resolve() 解析, 避免 macOS /tmp 符号链接导致的路径不一致
    edited_file = edited_file.resolve()
    modules_md_resolved = MODULES_MD.resolve()
    project_root_resolved = PROJECT_ROOT.resolve()

    content = edited_file.read_text(encoding="utf-8", errors="ignore")

    # === Guard 1: 跳过自己刚写出的副本（防级联触发）===
    if GUARD_MARKER in content:
        return 0

    # === Guard 2: 编辑的不是 MODULES.md,且目标不含任何 MARKER →
    #                说明不是相关文件, no-op ===
    has_any_marker = (
        MARKER_BEGIN_RE.search(content) is not None   # v3 aside
        or MARKER_BEGIN_V2_RE.search(content) is not None  # v2 注释 + id=
        or MARKER_BEGIN_V1 in content                  # v1 注释 (无 id)
    )
    if edited_file != modules_md_resolved and not has_any_marker:
        return 0

    # === 决定要同步哪些 block_id ===
    if edited_file == modules_md_resolved:
        # MODULES.md 改了: 同步所有已知 block_id(遍历所有副本, 看它们用哪些)
        target_block_ids = list(BLOCK_DEFINITIONS.keys())
    else:
        # 副本被改: 同步该副本内已有的所有 block_id
        target_block_ids = list(set(bid for bid, _, _ in find_all_marker_blocks(content)))
        if not target_block_ids:
            return 0

    # === 执行同步 ===
    def _safe_rel(p: Path) -> str:
        try:
            return str(p.relative_to(project_root_resolved))
        except ValueError:
            return str(p)

    entries: list[dict] = []
    for block_id in target_block_ids:
        try:
            content_md = extract_block(block_id)
            src_sha = hashlib.sha256(
                MODULES_MD.read_bytes()
            ).hexdigest()

            # 决定目标
            if edited_file == modules_md_resolved:
                targets = [
                    p for p in discover_existing_copies()
                    if find_marker_block(p.read_text(encoding="utf-8", errors="ignore"), block_id) is not None
                ]
            else:
                targets = [edited_file]

            for target in targets:
                try:
                    ok, old_sum = inject_into_file(target, block_id, content_md, src_sha)
                    entries.append({
                        "ts": datetime.now().isoformat(),
                        "trigger": _safe_rel(edited_file),
                        "block_id": block_id,
                        "target": _safe_rel(target),
                        "src_sha": src_sha[:12],
                        "status": "synced",
                    })
                except Exception as exc:
                    entries.append({
                        "ts": datetime.now().isoformat(),
                        "trigger": _safe_rel(edited_file),
                        "block_id": block_id,
                        "target": _safe_rel(target),
                        "src_sha": src_sha[:12],
                        "status": "error",
                        "error": f"{type(exc).__name__}: {exc}",
                    })
        except Exception as exc:
            sys.stderr.write(f"[sync_modules_table] extract {block_id} failed: {exc}\n")

    if entries:
        write_log(entries)
        synced = sum(1 for e in entries if e["status"] == "synced")
        block_ids_str = ", ".join(target_block_ids)
        sys.stderr.write(
            f"[sync_modules_table] {synced}/{len(entries)} blocks synced "
            f"({block_ids_str}), src_sha={src_sha[:12]}\n"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
