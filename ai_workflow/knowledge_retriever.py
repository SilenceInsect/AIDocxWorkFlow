"""
knowledge_retriever.py
=====================
语义检索工具：基于 Chroma + sentence-transformers，按需从知识库检索相关片段注入上下文。

用法示例
--------
```python
from knowledge_retriever import retrieve_knowledge, format_for_context

# Agent 查询时
segments = retrieve_knowledge(
    query="倒计时按钮跨天刷新怎么设计TP",
    module="UI",
    top_k=5
)

# 格式化注入上下文
ctx = format_for_context(segments)
# ctx 可直接注入到 Agent 的 system prompt 或 user message
```
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# ChromaDB + sentence-transformers
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# 全局常量
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.parent.resolve()  # AIDocxWorkFlow/
KB_ROOT = ROOT / "knowledge" / "public" / "module_templates"
PERSIST_DIR = ROOT / ".chroma_db"

DEFAULT_MODEL = "BAAI/bge-m3"
DEFAULT_TOP_K = 5

LOG = logging.getLogger(__name__)

# 8 个模块专家 → 对应的模板子目录
MODULE_TO_DIR = {
    "UI": "UI",
    "CONFIG": "CONFIG",
    "BIZ": "BIZ",
    "UTIL": "UTIL",
    "LINK": "LINK",
    "SPECIAL": "SPECIAL",
    "LOG": "LOG",
    "HINT": "HINT",
}

# Chroma collection 名称
COLLECTION_NAME = "module_knowledge"


# ---------------------------------------------------------------------------
# Chroma 客户端（单例）
# ---------------------------------------------------------------------------

_client: Optional[chromadb.PersistentClient] = None
_model: Optional[SentenceTransformer] = None


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(PERSIST_DIR))
        LOG.info("Chroma client initialized at %s", PERSIST_DIR)
    return _client


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(DEFAULT_MODEL)
        LOG.info("Embedding model loaded: %s", DEFAULT_MODEL)
    return _model


def _parse_json_list(val: str | list) -> list:
    """解析 JSON 列表字段（Chroma metadata 中存为 JSON 字符串）。"""
    if isinstance(val, list):
        return val
    try:
        return json.loads(val)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Segment 结构（与 knowledge_indexer.py 保持一致）
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeSegment:
    """知识库检索片段（对应 Chroma 中一条记录）"""

    id: str               # 唯一标识，如 "ui-A-ctrl-8states"
    module: str            # "UI"
    source_file: str       # 相对路径，如 "knowledge/.../UI/A_control_basic.md"
    segment_type: str     # "tp_template" | "boundary" | "scene" | "rule"
    heading: str           # 标题，如 "TP-004（CONTROL_STATE）：按钮 8 种状态完整切换"
    content: str          # 完整文本内容
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

    @classmethod
    def from_dict(cls, d: dict) -> "KnowledgeSegment":
        return cls(
            id=d["id"],
            module=d["module"],
            source_file=d["source_file"],
            segment_type=d["segment_type"],
            heading=d["heading"],
            content=d["content"],
            keywords=d.get("keywords", []),
            metadata=d.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# 核心检索函数
# ---------------------------------------------------------------------------

def retrieve_knowledge(
    query: str,
    module: Optional[str] = None,
    segment_types: Optional[list[str]] = None,
    top_k: int = DEFAULT_TOP_K,
    include_content: bool = True,
    extra_keywords: Optional[list[str]] = None,
) -> list[KnowledgeSegment]:
    """
    语义检索知识库片段。

    参数
    ----
    query : str
        Agent 自然语言查询，如 "倒计时按钮跨天刷新"
    module : str, optional
        限定模块，如 "UI"。None 则搜索所有模块。
    segment_types : list[str], optional
        限定片段类型，如 ["tp_template", "boundary"]。None 则不限制。
    top_k : int
        返回片段数量，默认 5。
    include_content : bool
        是否返回 content 字段（关闭可节省 token）。
    extra_keywords : list[str], optional
        额外关键词，用于补充 query 无法覆盖的检索词。

    返回
    ----
    list[KnowledgeSegment]
        按语义相似度排序的片段列表。
    """
    client = _get_client()

    # 构造组合查询（query + 关键词增强）
    combined_query = query
    if extra_keywords:
        combined_query = f"{query} {' '.join(extra_keywords)}"

    # 获取 collection
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        LOG.warning(
            "Chroma collection '%s' not found. "
            "Run `python -m ai_workflow.knowledge_indexer` to build the index first.",
            COLLECTION_NAME,
        )
        return []

    # 构建 where 过滤条件
    where_filter: Optional[dict] = {}
    if module:
        where_filter["module"] = module
    if segment_types:
        if len(segment_types) == 1:
            where_filter["segment_type"] = segment_types[0]
        # 多类型用 $in（Chroma 支持但 API 略有不同，这里简化为单类型）

    # 查询
    kwargs: dict[str, Any] = {
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where_filter:
        kwargs["where"] = where_filter

    results = collection.query(
        query_texts=[combined_query],
        **kwargs,
    )

    segments = []
    if not results["ids"] or not results["ids"][0]:
        return segments

    for i, doc_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        doc = results["documents"][0][i] if results["documents"] else ""
        distance = results["distances"][0][i] if results["distances"] else None

        # 按 segment_type 二次过滤（支持多类型）
        if segment_types and len(segment_types) > 1:
            if meta.get("segment_type") not in segment_types:
                continue

        # 不返回 content 时截断
        if not include_content:
            doc = ""

        seg = KnowledgeSegment(
            id=doc_id,
            module=meta.get("module", ""),
            source_file=meta.get("source_file", ""),
            segment_type=meta.get("segment_type", ""),
            heading=meta.get("heading", ""),
            content=doc,
            keywords=_parse_json_list(meta.get("keywords", "[]")),
            metadata={
                "distance": distance,
                "sub_codes": _parse_json_list(meta.get("sub_codes", "[]")),
                **{k: v for k, v in meta.items() if k not in (
                    "module", "source_file", "segment_type", "heading", "keywords", "sub_codes"
                )},
            },
        )
        segments.append(seg)

    LOG.info(
        "retrieve_knowledge(module=%s, top_k=%d) → %d segments",
        module, top_k, len(segments),
    )
    return segments


def retrieve_tp_templates(
    query: str,
    module: str,
    top_k: int = 5,
) -> list[KnowledgeSegment]:
    """
    快捷方法：只检索 TP 模板片段（segment_type == "tp_template"）。
    适合 Agent 生成测试点时调用。
    """
    return retrieve_knowledge(
        query=query,
        module=module,
        segment_types=["tp_template"],
        top_k=top_k,
    )


def retrieve_boundaries(
    query: str,
    module: str,
    top_k: int = 3,
) -> list[KnowledgeSegment]:
    """
    快捷方法：只检索边界陷阱片段（segment_type == "boundary"）。
    适合 Agent 区分子类边界时调用。
    """
    return retrieve_knowledge(
        query=query,
        module=module,
        segment_types=["boundary"],
        top_k=top_k,
    )


# ---------------------------------------------------------------------------
# 上下文格式化
# ---------------------------------------------------------------------------

def format_for_context(
    segments: list[KnowledgeSegment],
    show_metadata: bool = True,
    max_content_chars: int = 1500,
) -> str:
    """
    将检索片段格式化为可注入上下文的文本。

    参数
    ----
    segments : list[KnowledgeSegment]
        retrieve_knowledge() 返回的片段。
    show_metadata : bool
        是否显示元数据（来源文件、片段类型）。
    max_content_chars : int
        content 最大字符数，超出截断并加提示。

    返回
    ----
    str
        格式化文本，可直接注入到上下文中。
    """
    if not segments:
        return ""

    lines = ["[知识库检索片段]", ""]

    for i, seg in enumerate(segments, 1):
        # 元数据行
        if show_metadata:
            meta_parts = [
                f"[{i}/{len(segments)}]",
                f"模块:{seg.module}",
                f"类型:{seg.segment_type}",
            ]
            if seg.heading:
                meta_parts.append(f"标题:{seg.heading}")
            lines.append(" - ".join(meta_parts))

            source_rel = seg.source_file
            lines.append(f"  来源: {source_rel}")

            if seg.keywords:
                lines.append(f"  关键词: {', '.join(seg.keywords)}")
        else:
            if seg.heading:
                lines.append(f"[{i}/{len(segments)}] {seg.heading}")

        # 内容
        content = seg.content
        if len(content) > max_content_chars:
            content = content[:max_content_chars] + f"\n... [内容已截断，原文共 {len(seg.content)} 字符]"

        lines.append(content)

        # 相似度（如果有）
        if seg.metadata.get("distance") is not None:
            similarity = 1 - seg.metadata["distance"]
            lines.append(f"  相似度: {similarity:.2%}")

        lines.append("")  # 空行分隔

    lines.append("[/知识库检索片段]")
    return "\n".join(lines)


def format_for_system_prompt(
    segments: list[KnowledgeSegment],
    task_hint: str = "当前任务相关知识库片段：",
) -> str:
    """
    格式化用于注入 system prompt 的精简文本（更紧凑的格式）。
    """
    if not segments:
        return ""

    lines = [task_hint, ""]

    for i, seg in enumerate(segments, 1):
        heading = seg.heading or seg.id
        content_preview = seg.content[:500] + ("..." if len(seg.content) > 500 else "")
        lines.append(f"## [{i}] {seg.module}/{seg.segment_type}: {heading}")
        lines.append(content_preview)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 诊断工具
# ---------------------------------------------------------------------------

def collection_stats() -> dict[str, Any]:
    """
    返回 Chroma collection 的统计信息。
    """
    client = _get_client()
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        count = collection.count()
        sample = collection.peek(limit=3)
        return {
            "collection": COLLECTION_NAME,
            "total_segments": count,
            "persist_dir": str(PERSIST_DIR),
            "model": DEFAULT_MODEL,
            "sample_ids": sample.get("ids", [])[:3],
        }
    except Exception as e:
        return {
            "error": str(e),
            "hint": "Run `python -m ai_workflow.knowledge_indexer` to build the index.",
        }


def list_modules() -> list[str]:
    """返回已索引的模块列表。"""
    client = _get_client()
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        all_meta = collection.get(include=["metadatas"])
        modules = set(m.get("module") for m in all_meta["metadatas"] if m.get("module"))
        return sorted(modules)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# CLI 入口（调试用）
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="知识库检索工具")
    sub = parser.add_subparsers(dest="cmd")

    # 查询
    q = sub.add_parser("query", help="语义检索")
    q.add_argument("query", help="查询文本")
    q.add_argument("--module", "-m", default=None, help="限定模块，如 UI")
    q.add_argument("--top-k", "-k", type=int, default=5, help="返回数量")
    q.add_argument("--type", "-t", action="append", help="片段类型过滤，如 tp_template")
    q.add_argument("--format", "-f", choices=["full", "system"], default="full", help="输出格式")

    # 统计
    sub.add_parser("stats", help="查看索引统计")

    # 模块列表
    sub.add_parser("modules", help="列出已索引的模块")

    args = parser.parse_args()

    if args.cmd == "query":
        segs = retrieve_knowledge(
            query=args.query,
            module=args.module,
            segment_types=args.type,
            top_k=args.top_k,
        )
        if args.format == "system":
            print(format_for_system_prompt(segs))
        else:
            print(format_for_context(segs))

    elif args.cmd == "stats":
        print(json.dumps(collection_stats(), indent=2, ensure_ascii=False))

    elif args.cmd == "modules":
        print("已索引模块:", list_modules())

    else:
        parser.print_help()
