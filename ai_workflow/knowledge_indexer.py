"""
knowledge_indexer.py
===================
离线构建知识库语义索引：扫描 module_templates → 语义切分 → 向量化 → 存入 Chroma。

用法
----
```bash
# 构建全量索引（所有 8 个模块）
python -m ai_workflow.knowledge_indexer

# 构建指定模块
python -m ai_workflow.knowledge_indexer --module UI

# 增量更新（只重新索引变更文件，基于 content_hash）
python -m ai_workflow.knowledge_indexer --incremental

# 清除并重建
python -m ai_workflow.knowledge_indexer --rebuild

# 指定根目录
python -m ai_workflow.knowledge_indexer --kb-root /path/to/module_templates
```
"""

from __future__ import annotations

import chromadb
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ai_workflow.knowledge_retriever import (
    COLLECTION_NAME,
    KB_ROOT,
    PERSIST_DIR,
    DEFAULT_MODEL,
    _get_client,
    _get_model,
)

LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 模块目录映射
# ---------------------------------------------------------------------------

MODULE_TO_DIR = {
    "UI": "UI",
    "CONFIG": "CONFIG",
    "BIZ": "BIZ",
    "AUX": "AUX",
    "LINK": "LINK",
    "SPECIAL": "SPECIAL",
    "LOG": "LOG",
    "HINT": "HINT",
}

# 文件名 → 文件代码（用于 segment ID）
# 例：A_control_basic.md → "A"
FILENAME_CODE_RE = re.compile(r"^([A-Z])_")

# 种子 TP 标题格式：### TP-001（CONTROL_RENDER）：标题
TP_TITLE_RE = re.compile(
    r"^### TP-(\d+)"   # TP-001
    r"（([A-Z_]+)\)："  # （CONTROL_RENDER）
    r"(.+)$"            # 标题
)

# 边界陷阱标题格式：### 边界 1：xxx
BOUNDARY_TITLE_RE = re.compile(r"^### 边界 (\d+)：(.*)$")

# 场景标题格式：### 场景 1：xxx
SCENE_TITLE_RE = re.compile(r"^### 场景 (\d+)：(.*)$")

# Markdown 标题格式：## 或 ### 开头
SECTION_HDR_RE = re.compile(r"^(#{2,3}) (.+)$")

# frontmatter 格式
FRONTMATTER_RE = re.compile(r"^> \*\*子类代码\*\*：`([^`]+)`", re.MULTILINE)


# ---------------------------------------------------------------------------
# Segment 数据结构
# ---------------------------------------------------------------------------

@dataclass
class RawSegment:
    id: str
    module: str           # "UI"
    source_file: str      # 相对路径
    segment_type: str     # "tp_template" | "boundary" | "scene" | "rule" | "header"
    heading: str
    content: str           # 纯文本（不含标题行）
    keywords: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "module": self.module,
            "source_file": self.source_file,
            "segment_type": self.segment_type,
            "heading": self.heading,
            "content": self.content,
            "keywords": self.keywords,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# 解析器：单文件 → 多个 RawSegment
# ---------------------------------------------------------------------------

def parse_template_file(filepath: Path, module: str) -> list[RawSegment]:
    """
    解析一个模板 .md 文件，返回语义片段列表。
    """
    text = filepath.read_text(encoding="utf-8")
    rel_path = str(filepath.relative_to(KB_ROOT.parent.parent))

    # 提取文件名代码（如 "A" from "A_control_basic.md"）
    fname = filepath.name
    file_code_match = FILENAME_CODE_RE.match(fname)
    file_code = file_code_match.group(1) if file_code_match else fname[:1].upper()

    # 从 frontmatter 提取子类代码（如 "CONTROL_RENDER"）
    sub_codes: list[str] = []
    fm_match = FRONTMATTER_RE.search(text)
    if fm_match:
        sub_codes = [c.strip() for c in fm_match.group(1).split("/")]

    # 提取 keywords（从标题和子类代码）
    keywords = _extract_keywords(text, sub_codes)

    # 按行解析，识别标题块
    lines = text.splitlines()
    segments: list[RawSegment] = []
    current_heading = ""
    current_body_lines: list[str] = []
    current_type = "rule"
    current_seq = 0

    def flush_segment():
        nonlocal current_heading, current_body_lines, current_type, current_seq
        if current_heading and current_body_lines:
            content = "\n".join(current_body_lines).strip()
            if content:
                current_seq += 1
                seg_id = f"{module.lower()}-{file_code}-{current_type}-{current_seq:03d}"
                segments.append(RawSegment(
                    id=seg_id,
                    module=module,
                    source_file=rel_path,
                    segment_type=current_type,
                    heading=current_heading,
                    content=content,
                    keywords=keywords[:],   # 复制
                    metadata={
                        "file_code": file_code,
                        "sub_codes": sub_codes,
                        "seq": current_seq,
                    },
                ))
        current_heading = ""
        current_body_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        hdr_match = SECTION_HDR_RE.match(line.strip())

        if hdr_match:
            # 遇到新标题，先 flush 当前段
            flush_segment()

            raw_title = hdr_match.group(2).strip()

            # 判断标题类型
            tp_match = TP_TITLE_RE.match(raw_title)
            if tp_match:
                current_type = "tp_template"
                tp_num = tp_match.group(1)
                sub_code = tp_match.group(2)
                current_heading = f"TP-{tp_num}（{sub_code}）：{tp_match.group(3).strip()}"
                current_body_lines = []
                i += 1
                continue

            boundary_match = BOUNDARY_TITLE_RE.match(raw_title)
            if boundary_match:
                current_type = "boundary"
                current_heading = f"边界 {boundary_match.group(1)}：{boundary_match.group(2).strip()}"
                current_body_lines = []
                i += 1
                continue

            scene_match = SCENE_TITLE_RE.match(raw_title)
            if scene_match:
                current_type = "scene"
                current_heading = f"场景 {scene_match.group(1)}：{scene_match.group(2).strip()}"
                current_body_lines = []
                i += 1
                continue

            # 其他 ## 标题 → rule 段落
            current_type = "rule"
            current_heading = raw_title
            current_body_lines = []
            i += 1
            continue

        # 非标题行 → 累积 body
        if current_heading:
            current_body_lines.append(line)

        i += 1

    flush_segment()
    return segments


def _extract_keywords(text: str, sub_codes: list[str]) -> list[str]:
    """从内容中提取关键词（辅助语义检索）。"""
    keywords: list[str] = []

    # 子类代码
    keywords.extend(sub_codes)

    # 从 frontmatter 提取归属模块
    module_match = re.search(r"^\> \*\*归属模块\*\*：`([A-Z]+)`", text, re.MULTILINE)
    if module_match:
        keywords.append(module_match.group(1))

    # 从一级标题提取
    h1_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    if h1_match:
        # 取中文字符作为关键词
        cn_chars = re.findall(r"[\u4e00-\u9fff]+", h1_match.group(1))
        keywords.extend(cn_chars)

    # 去重
    seen = set()
    deduped = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            deduped.append(k)

    return deduped


# ---------------------------------------------------------------------------
# 索引构建核心
# ---------------------------------------------------------------------------

def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _manifest_path() -> Path:
    return PERSIST_DIR / f"{COLLECTION_NAME}_manifest.json"


def _read_manifest() -> dict[str, dict[str, str]]:
    """
    读取 manifest，返回 {filepath_rel: {segment_id: content_hash, ...}}。
    文件不存在或格式错误时返回空 dict。
    """
    path = _manifest_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        # 结构: {"files": {"path/to/file.md": {"seg_id": "hash", ...}}, ...}
        return data.get("files", {})
    except Exception:
        return {}


def _write_manifest(file_map: dict[str, dict[str, str]]) -> None:
    """写入 manifest。"""
    manifest = {
        "version": "1.0",
        "updated_at": str(Path(__file__).stat().st_mtime),
        "files": file_map,
    }
    _manifest_path().write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_file_segments(
    filepaths: list[tuple[Path, str]],
    module: Optional[str],
    kb_root: Path,
) -> tuple[dict[str, RawSegment], dict[str, list[str]]]:
    """
    扫描文件列表，返回：
    - segments_by_id: {segment_id: RawSegment}
    - segments_by_file: {filepath_rel: [segment_id, ...]}
    """
    segments_by_id: dict[str, RawSegment] = {}
    segments_by_file: dict[str, list[str]] = {}

    for filepath, mod_id in filepaths:
        rel_path = str(filepath.relative_to(kb_root.parent.parent))
        try:
            segs = parse_template_file(filepath, mod_id)
        except Exception as e:
            LOG.error("Error parsing %s: %s", filepath, e)
            continue

        segments_by_file[rel_path] = []
        for seg in segs:
            if seg.id in segments_by_id:
                LOG.warning("Duplicate segment ID '%s' across %s and %s — skipping duplicate",
                            seg.id, segments_by_id[seg.id].source_file, seg.source_file)
                continue
            segments_by_id[seg.id] = seg
            segments_by_file[rel_path].append(seg.id)

    return segments_by_id, segments_by_file


def _collect_files(
    modules: dict[str, str],
    kb_root: Path,
) -> list[tuple[Path, str]]:
    """收集所有待扫描的文件，返回 [(filepath, module_id), ...]。"""
    files: list[tuple[Path, str]] = []
    for mod_id, mod_dir in modules.items():
        mod_path = kb_root / mod_dir
        if not mod_path.is_dir():
            continue
        for md in sorted(mod_path.glob("*.md")):
            files.append((md, mod_id))
        # 模块概览文件（如 knowledge/.../UI.md）
        overview = kb_root.parent / f"{mod_id}.md"
        if overview.exists():
            files.append((overview, mod_id))
    return files


def _sanitize_metadata(meta: dict) -> dict:
    """将 list 字段 JSON 序列化（Chroma 要求非空列表）。"""
    sanitized = dict(meta)
    for key in ("keywords", "sub_codes"):
        val = sanitized.get(key, [])
        if not isinstance(val, list):
            val = []
        sanitized[key] = json.dumps(val, ensure_ascii=False)
    return sanitized


def build_module_index(
    module: Optional[str] = None,
    kb_root: Optional[Path] = None,
    persist_dir: Optional[Path] = None,
    model_name: Optional[str] = None,
    incremental: bool = False,
    rebuild: bool = False,
    verbose: bool = True,
) -> dict[str, Any]:
    """
    构建或更新 Chroma 索引。

    支持两种模式：
    - rebuild=True : 删除整个 collection，从零重建（适合初次构建或 schema 变更）
    - incremental=True : 基于 manifest 对比 content_hash，只增删变化的 segments
    - 两者均为 False : 追加新 segments（幂等，重复 ID 会被 Chroma 忽略或覆盖）

    参数
    ----
    module : str, optional
        指定模块（如 "UI"）。None 则处理所有模块。
    kb_root : Path, optional
        知识库根目录。None 则用 KB_ROOT。
    persist_dir : Path, optional
        Chroma 持久化目录。None 则用 PERSIST_DIR。
    model_name : str, optional
        embedding 模型名。None 则用 DEFAULT_MODEL。
    incremental : bool
        增量模式（基于 manifest + content_hash 对比）。
    rebuild : bool
        重建模式（先删除旧 collection 再重建）。
    verbose : bool
        是否打印详细日志。

    返回
    ----
    dict：统计信息
    """
    kb_root = kb_root or KB_ROOT
    persist_dir = persist_dir or PERSIST_DIR
    model_name = model_name or DEFAULT_MODEL

    client = _get_client()
    model = _get_model()

    # 确定扫描范围
    if module:
        modules_to_scan = {module: MODULE_TO_DIR[module]}
    else:
        modules_to_scan = MODULE_TO_DIR

    # ---- 扫描文件，构建 segments ----
    all_files = _collect_files(modules_to_scan, kb_root)
    segments_by_id, segments_by_file = _build_file_segments(all_files, module, kb_root)

    if not segments_by_id:
        if verbose:
            LOG.warning("No segments found.")
        return {"files_scanned": 0, "segments_created": 0, "skipped": 0, "errors": []}

    # 处理 collection
    if rebuild:
        # rebuild 策略：目标模块替换，其他模块保留
        try:
            collection = client.get_collection(name=COLLECTION_NAME)
        except chromadb.errors.NotFoundError:
            collection = client.create_collection(name=COLLECTION_NAME)
        # 注：Chroma 0.6.x 在 collection 状态异常时可能抛 InternalError，此处不 catch，
        # 让上层感知并人工处置（避免静默重建 collection 丢失其他模块）

        existing = _read_manifest()
        current_file_rels = set(segments_by_file.keys())
        ids_to_delete = [
            sid
            for fp, seg_map in existing.items()
            if fp in current_file_rels
            for sid in seg_map
        ]
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            if verbose:
                LOG.info("Deleted %d stale segments for module rebuild", len(ids_to_delete))

        # merge manifest（保留其他模块的 hash 记录）
        merged = {fp: seg_map for fp, seg_map in existing.items() if fp not in current_file_rels}
        merged.update({
            fp: {sid: _content_hash(segments_by_id[sid].content) for sid in seg_ids}
            for fp, seg_ids in segments_by_file.items()
        })
        _write_manifest(merged)

        # add 当前模块的 segments（IDs 相同会替换旧的）
        _batch_add(collection, model, list(segments_by_id.values()), verbose)

        return {
            "mode": "rebuild",
            "files_scanned": len(all_files),
            "segments_created": len(segments_by_id),
            "skipped": 0,
            "errors": [],
            "persist_dir": str(persist_dir),
            "collection": COLLECTION_NAME,
            "model": model_name,
        }

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        collection = client.create_collection(name=COLLECTION_NAME)

    # ---- 增量 diff（核心）----
    if incremental and not rebuild:
        manifest = _read_manifest()
        new_file_map: dict[str, dict[str, str]] = {}

        to_delete_ids: list[str] = []
        to_add_ids: list[str] = []
        to_update_ids: list[str] = []

        # 遍历 manifest 中的已存文件
        for file_rel, old_seg_map in manifest.items():
            if file_rel in segments_by_file:
                # 文件仍在 → 比对每个 segment 的 hash
                current_ids = set(segments_by_file[file_rel])
                for seg_id, old_hash in old_seg_map.items():
                    if seg_id not in segments_by_id:
                        # segment 被删除
                        to_delete_ids.append(seg_id)
                    elif segments_by_id[seg_id].id == seg_id:
                        new_hash = _content_hash(segments_by_id[seg_id].content)
                        if new_hash != old_hash:
                            # segment 内容变化
                            to_delete_ids.append(seg_id)
                            to_update_ids.append(seg_id)
                # 收集新增 segment（manifest 有文件但文件新增了 segment）
                current_hashes = {
                    sid: _content_hash(segments_by_id[sid].content)
                    for sid in current_ids
                }
                new_file_map[file_rel] = current_hashes
            else:
                # 文件被删除 → 删除其所有 segment
                to_delete_ids.extend(old_seg_map.keys())

        # 遍历扫描结果中不在 manifest 的新文件
        for file_rel, seg_ids in segments_by_file.items():
            if file_rel not in manifest:
                for seg_id in seg_ids:
                    to_add_ids.append(seg_id)
                new_file_map[file_rel] = {
                    sid: _content_hash(segments_by_id[sid].content)
                    for sid in seg_ids
                }

        # 合并 update → 本质是 delete + add
        to_add_ids = list(set(to_add_ids) | set(to_update_ids))

        if verbose:
            LOG.info(
                "Incremental diff: %d to delete, %d to add (total scanned %d)",
                len(to_delete_ids), len(to_add_ids), len(segments_by_id),
            )

        # ---- Chroma 写入 ----
        if to_delete_ids:
            collection.delete(ids=to_delete_ids)
            if verbose:
                LOG.info("Deleted %d stale segments", len(to_delete_ids))

        if to_add_ids:
            _batch_add(collection, model, [segments_by_id[sid] for sid in to_add_ids], verbose)

        # 写入 manifest（所有文件的完整 hash 快照）
        _write_manifest(new_file_map)

        stats = {
            "mode": "incremental",
            "files_scanned": len(all_files),
            "segments_scanned": len(segments_by_id),
            "deleted": len(to_delete_ids),
            "added": len(to_add_ids),
            "skipped": len(segments_by_id) - len(to_add_ids),
            "errors": [],
            "persist_dir": str(persist_dir),
        }

    else:
        # ---- 全量模式（rebuild 或追加）----
        all_ids = list(segments_by_id.keys())

        if verbose:
            LOG.info("Embedding %d segments with %s...", len(all_ids), model_name)

        _batch_add(collection, model, list(segments_by_id.values()), verbose)

        # 构建当前模块的 file_map
        current_file_map: dict[str, dict[str, str]] = {}
        for file_rel, seg_ids in segments_by_file.items():
            current_file_map[file_rel] = {
                sid: _content_hash(segments_by_id[sid].content)
                for sid in seg_ids
            }

        # rebuild 需 merge manifest（避免覆盖其他模块）；追加直接全量覆盖
        if rebuild:
            existing = _read_manifest()
            # 剔除被 rebuild 的模块对应的文件
            # 判定方式：当前扫描范围内的文件视为"被 rebuild"，其余保留
            current_file_rel_paths = set(current_file_map.keys())
            merged = {
                fp: seg_map for fp, seg_map in existing.items()
                if fp not in current_file_rel_paths
            }
            merged.update(current_file_map)
            _write_manifest(merged)
        else:
            _write_manifest(current_file_map)

        stats = {
            "mode": "rebuild" if rebuild else "append",
            "files_scanned": len(all_files),
            "segments_created": len(all_ids),
            "skipped": 0,
            "errors": [],
            "persist_dir": str(persist_dir),
            "collection": COLLECTION_NAME,
            "model": model_name,
        }

    if verbose:
        LOG.info("Index updated: %d segments in collection", collection.count())

    return stats


def _batch_add(
    collection,
    model,
    segments: list[RawSegment],
    verbose: bool,
    batch_size: int = 100,
) -> None:
    """
    批量向量化 + 写入 Chroma（自动分批，避免内存爆炸）。
    """
    total = len(segments)
    for start in range(0, total, batch_size):
        batch = segments[start:start + batch_size]
        texts = [s.content for s in batch]
        ids = [s.id for s in batch]

        # 复用已计算的 hash（避免重复计算）
        hashes = [_content_hash(s.content) for s in batch]

        metadatas = [
            _sanitize_metadata({
                "module": s.module,
                "source_file": s.source_file,
                "segment_type": s.segment_type,
                "heading": s.heading,
                "keywords": s.keywords,
                "file_code": s.metadata.get("file_code", ""),
                "sub_codes": s.metadata.get("sub_codes", []),
                "content_hash": h,
            })
            for s, h in zip(batch, hashes)
        ]

        if verbose:
            LOG.info("  Batch %d-%d / %d...", start + 1, min(start + batch_size, total), total)

        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="构建知识库语义索引（Chroma + sentence-transformers）"
    )
    parser.add_argument(
        "--module", "-m",
        choices=list(MODULE_TO_DIR.keys()),
        help="指定模块（如 UI）。不指定则构建所有模块。",
    )
    parser.add_argument(
        "--kb-root",
        type=Path,
        default=None,
        help="知识库根目录（默认: knowledge/public/module_templates/ 的父目录）",
    )
    parser.add_argument(
        "--rebuild", "-r",
        action="store_true",
        help="先删除旧 collection 再重建",
    )
    parser.add_argument(
        "--incremental", "-i",
        action="store_true",
        help="增量模式（基于 content_hash，只索引变更文件）",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式（减少输出）",
    )

    args = parser.parse_args()

    result = build_module_index(
        module=args.module,
        kb_root=args.kb_root,
        rebuild=args.rebuild,
        incremental=args.incremental,
        verbose=not args.quiet,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
