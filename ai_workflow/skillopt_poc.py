#!/usr/bin/env python3
"""SkillOpt PoC — 验证 `pip install skillopt` 能跑通、最小 SKILL.md 能产出 best_skill.md。

设计原则（单文件 ≤ 500 行；只做事，不判决）：
  - **不改任何 SKILL.md**：本脚本只生成 candidate `best_skill.md`，人工 review 后再 apply
  - **不动 S8 业务流**：`self_iteration.py` 保持不变
  - **可重复**：clear() 会清掉 PoC 产出；run() 重新生成
  - **不接 SkillOpt-Sleep / WebUI / Codex exec**：只用 minimax_chat backend（OpenAI-compatible）

使用：
    .venv/bin/python -m ai_workflow.skillopt_poc prepare  # 构造 initial.md + split_dir
    .venv/bin/python -m ai_workflow.skillopt_poc run      # 调 skillopt-train
    .venv/bin/python -m ai_workflow.skillopt_poc status   # 看 PoC 状态
    .venv/bin/python -m ai_workflow.skillopt_poc clear    # 清空 PoC 产出
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── 路径常量 ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.resolve()
SKILL_TO_OPTIMIZE = ROOT / ".cursor" / "skills" / "aidocx-feedback-logger" / "SKILL.md"
POC_DIR = ROOT / "workflow_assets" / "skillopt_poc" / "v1.0"
INITIAL_MD = POC_DIR / "initial.md"
SPLIT_DIR = POC_DIR / "data"
OUT_ROOT = POC_DIR / "outputs"
CONFIG_YAML = POC_DIR / "config.yaml"
RUN_LOG = POC_DIR / "run.log"


# ── prepare ──────────────────────────────────────────────────────────────
def prepare() -> None:
    """构造 PoC 输入：
    - 拷贝 SKILL.md → initial.md（SkillOpt 的"权重"起点）
    - 生成 split_dir（train/val/test 各 5 条 trajectory，源自游戏道具商城系统 v2.08-v3.01 真实 pipeline）
    """
    POC_DIR.mkdir(parents=True, exist_ok=True)
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    # 1. initial.md
    shutil.copyfile(SKILL_TO_OPTIMIZE, INITIAL_MD)
    print(f"[PoC] initial.md ← {SKILL_TO_OPTIMIZE.name} ({INITIAL_MD.stat().st_size} bytes)")

    # 2. split_dir：构造 5 条 trajectory 样本（SkillOpt searchqa 格式：{id, question, context, answers}）
    #    本 PoC 用内置 searchqa env（feedback_importer 自定义 env 留到 Phase 2）
    #    - question  = 反馈导入请求
    #    - context   = 当前 SKILL.md 的前 800 字符（让 target LLM 知道 skill 内容）
    #    - answers   = 期望的标准答案
    skill_context = SKILL_TO_OPTIMIZE.read_text(encoding="utf-8")[:800]
    items = [
        {
            "id": "fb-001-excel-pass",
            "question": "用户场景：把测试用例执行结果 Excel（『反馈结果』sheet）导入到 feedback_logs/。请输出标准化 import 命令。",
            "context": skill_context,
            "answers": ["import_from_test_cases_xlsx(xlsx_path='...', version='v1.0')"],
        },
        {
            "id": "fb-002-excel-review",
            "question": "同时有反馈 Excel + 审查结果 Excel 怎么合并导入？",
            "context": skill_context,
            "answers": ["import_feedback(feedback_file=..., review_file=..., output_dir='workflow_assets/feedback_logs/')"],
        },
        {
            "id": "fb-003-csv-gbk",
            "question": "CSV 是 GBK 编码的，怎么导入？",
            "context": skill_context,
            "answers": ["自动识别 GBK/UTF-8 编码（feedback_logger 内部逻辑）"],
        },
        {
            "id": "fb-004-json-array",
            "question": "JSON 顶层是数组格式，能直接导入吗？",
            "context": skill_context,
            "answers": ["支持 3 种 JSON 格式：顶层数组 / entries 字段 / 单条记录"],
        },
        {
            "id": "fb-005-result-norm",
            "question": "执行结果列里写了『通过』『失败』『阻塞』，能识别吗？",
            "context": skill_context,
            "answers": ["自动标准化：✅ 通过 → PASS；❌ 失败 → FAIL；阻塞 → BLOCKED；待执行 → DRAFT"],
        },
        {
            "id": "fb-006-severity-norm",
            "question": "严重程度列写了 P0/P1/P2/P3 怎么映射？",
            "context": skill_context,
            "answers": ["P0 → CRITICAL；P1 → MAJOR；P2 → MINOR；P3 → LOW"],
        },
        {
            "id": "fb-007-column-mapping",
            "question": "列名是中文（『用例ID』『实际结果』『缺陷描述』）能识别吗？",
            "context": skill_context,
            "answers": ["内置自动列名映射（中文 → 标准字段）"],
        },
        {
            "id": "fb-008-output-format",
            "question": "导入后保存的文件叫什么格式？",
            "context": skill_context,
            "answers": ["feedback_<req_name>_<version>_<timestamp>.json（entries 数组）"],
        },
    ]

    # 切分：5 train / 2 val / 1 test
    splits = {"train": items[:5], "val": items[5:7], "test": items[7:]}
    for split_name, split_items in splits.items():
        split_path = SPLIT_DIR / split_name
        split_path.mkdir(parents=True, exist_ok=True)
        (split_path / "items.json").write_text(
            json.dumps(split_items, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[PoC] split '{split_name}': {len(split_items)} items → {split_path / 'items.json'}")

    # 3. config.yaml（SkillOpt v0.1.0 schema）
    #    env.name = searchqa（内置）→ Phase 2 再换成自定义 feedback_importer
    config = {
        "model": {
            "backend": "minimax_chat",
            "target_backend": "minimax_chat",
            "target": "MiniMax-Text-01",
            "optimizer_backend": "minimax_chat",
            "optimizer": "MiniMax-Text-01",
        },
        "train": {
            "num_epochs": 2,
            "train_size": 5,
            "batch_size": 5,
            "accumulation": 1,
            "seed": 42,
        },
        "gradient": {
            "minibatch_size": 4,
            "merge_batch_size": 4,
            "analyst_workers": 1,
            "failure_only": False,
        },
        "optimizer": {
            "learning_rate": 2,
            "min_learning_rate": 1,
            "lr_scheduler": "constant",
            "skill_update_mode": "patch",
        },
        "evaluation": {
            "use_gate": True,
            "sel_env_num": 2,
        },
        "env": {
            "name": "searchqa",
            "split_mode": "split_dir",
            "split_dir": str(SPLIT_DIR),
            "skill_init": str(INITIAL_MD),
            "out_root": str(OUT_ROOT),
            "limit": 0,
        },
    }
    CONFIG_YAML.write_text(
        "# Auto-generated by ai_workflow.skillopt_poc prepare\n"
        + _yaml_dump(config),
        encoding="utf-8",
    )
    print(f"[PoC] config.yaml → {CONFIG_YAML}")


def _yaml_dump(d: dict, indent: int = 0) -> str:
    """极简 YAML 序列化（避免引入 yaml 依赖）。"""
    lines = []
    pad = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            lines.append(f"{pad}{k}:")
            lines.append(_yaml_dump(v, indent + 1))
        elif isinstance(v, str):
            lines.append(f'{pad}{k}: "{v}"')
        elif isinstance(v, bool):
            lines.append(f"{pad}{k}: {str(v).lower()}")
        elif v is None:
            lines.append(f"{pad}{k}: null")
        else:
            lines.append(f"{pad}{k}: {v}")
    return "\n".join(lines) + "\n"


# ── run ──────────────────────────────────────────────────────────────────
def run() -> int:
    """调 `skillopt-train` 跑 PoC 训练。返回 exit code。"""
    if not CONFIG_YAML.exists():
        print("[PoC][ERROR] config.yaml 缺失；先跑 `prepare`", file=sys.stderr)
        return 2

    venv_skillopt = ROOT / ".venv" / "bin" / "skillopt-train"
    if not venv_skillopt.exists():
        print(f"[PoC][ERROR] {venv_skillopt} 不存在；先 `pip install skillopt` 进 venv",
              file=sys.stderr)
        return 2

    cmd = [str(venv_skillopt), "--config", str(CONFIG_YAML)]
    print(f"[PoC] exec: {' '.join(cmd)}")
    print(f"[PoC] log → {RUN_LOG}")

    # 把 stdin 设成 /dev/null，避免 skillopt-train 读取阻塞
    with open(RUN_LOG, "w", encoding="utf-8") as logf:
        logf.write(f"# SkillOpt PoC run @ {datetime.now().isoformat()}\n")
        logf.write(f"# cmd: {' '.join(cmd)}\n\n")
        logf.flush()
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=logf,
            stderr=subprocess.STDOUT,
            cwd=str(ROOT),
            env={**os.environ},  # 继承 MINIMAX_API_KEY 等
        )
    print(f"[PoC] exit code = {proc.returncode}")
    print(f"[PoC] 完整日志见：{RUN_LOG}")
    print(f"[PoC] 末尾 30 行：")
    print(_tail(RUN_LOG, 30))
    return proc.returncode


def _tail(path: Path, n: int = 30) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except Exception as e:
        return f"(log read failed: {e})"


# ── status ───────────────────────────────────────────────────────────────
def status() -> int:
    """打印 PoC 当前状态。"""
    print("=" * 60)
    print("  SkillOpt PoC Status (v1.0)")
    print("=" * 60)
    print(f"  initial.md    : {'✓' if INITIAL_MD.exists() else '✗'} {INITIAL_MD}")
    print(f"  config.yaml   : {'✓' if CONFIG_YAML.exists() else '✗'} {CONFIG_YAML}")
    print(f"  split_dir/    : {'✓' if SPLIT_DIR.exists() else '✗'} {SPLIT_DIR}")
    for split in ("train", "val", "test"):
        p = SPLIT_DIR / split / "items.json"
        cnt = len(json.loads(p.read_text(encoding="utf-8"))) if p.exists() else 0
        print(f"    {split:>5} items.json : {'✓' if cnt else '✗'} ({cnt} 条)")
    print(f"  outputs/      : {'✓' if OUT_ROOT.exists() else '✗'} {OUT_ROOT}")
    if OUT_ROOT.exists():
        best = list(OUT_ROOT.rglob("best_skill.md"))
        print(f"  best_skill.md : {'✓' if best else '✗'} ({len(best)} 个候选)")
        for b in best:
            print(f"    - {b.relative_to(ROOT)} ({b.stat().st_size} bytes)")
    print(f"  run.log       : {'✓' if RUN_LOG.exists() else '✗'} {RUN_LOG}")
    print("=" * 60)
    return 0


# ── clear ────────────────────────────────────────────────────────────────
def clear() -> int:
    """清掉 PoC 产出（保留 POC_DIR 目录本身）。"""
    for sub in ("outputs",):
        p = POC_DIR / sub
        if p.exists():
            shutil.rmtree(p)
            print(f"[PoC] removed {p}")
    for f in (INITIAL_MD, CONFIG_YAML, RUN_LOG):
        if f.exists():
            f.unlink()
            print(f"[PoC] removed {f}")
    if SPLIT_DIR.exists():
        shutil.rmtree(SPLIT_DIR)
        print(f"[PoC] removed {SPLIT_DIR}")
    return 0


# ── main ─────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(
        description="SkillOpt PoC — 验证 install + 跑一次小训练",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare", help="构造 initial.md + split_dir + config.yaml")
    sub.add_parser("run", help="调 skillopt-train 跑训练")
    sub.add_parser("status", help="看 PoC 当前状态")
    sub.add_parser("clear", help="清空 PoC 产出")
    args = ap.parse_args()

    if args.cmd == "prepare":
        prepare()
    elif args.cmd == "run":
        return run()
    elif args.cmd == "status":
        return status()
    elif args.cmd == "clear":
        return clear()
    return 0


if __name__ == "__main__":
    sys.exit(main())
