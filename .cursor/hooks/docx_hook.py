#!/usr/bin/env python3
"""Cursor prompt hook: auto-execute AIDocxWorkFlow pipeline.

Trigger patterns (自然语言):
  - 开始全流程 / 开始完整流程
  - 开始快速流程 / 快速流水线

Behavior:
  1. Parse the prompt to find workflow triggers + file references
  2. Read requirement text from referenced files
  3. Auto-execute the simplified flow (S1→S2→S4→S5) using Python rules
  4. Inject execution results into the prompt so the agent can present them
"""

from __future__ import annotations

import json, re, sys, time
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
_WORKFLOW_PATTERNS = [
    r'开始全流程', r'开始完整流程', r'开始快速流程', r'快速流水线',
    r'全流程', r'跑一下', r'跑全流程',
]


def extract_refs(prompt: str) -> list[str]:
    """提取 prompt 中的 .md 文件引用。

    修法（v6.2 方案 B）：保留 3 个 regex 意图清晰，加 normalize + dedup：
      - 模式 1: @"foo.md"  → 提取 "foo.md"（双引号）
      - 模式 2: @'foo.md'  → 提取 "foo.md"（单引号）
      - 模式 3: @foo.md    → 提取 "foo.md"（无引号）
      - dedup：用 normalize 后的路径做 key（去前导引号字符），避免
        同路径被模式 1+3 双重匹配。
    """
    refs: list[str] = []
    seen: set[str] = set()
    patterns = [r'@"([^"]+\.md)"', r"@'([^']+\.md)'", r'@([^\s]+\.md)']
    for pat in patterns:
        for m in re.finditer(pat, prompt):
            p = m.group(1).strip()
            if not p or p.startswith("-"):
                continue
            # normalize: 去前导引号（双/单）作为 dedup key
            key = p.lstrip("\"'")
            if key in seen:
                continue
            seen.add(key)
            refs.append(p)
    return refs


def read_req(refs: list[str]) -> str | None:
    for ref in refs:
        p = Path(ref)
        if p.is_absolute() and p.exists():
            return p.read_text(encoding="utf-8")
        p2 = _PROJECT_ROOT / p
        if p2.exists():
            return p2.read_text(encoding="utf-8")
    return None


def auto_flow(req_text: str, version: str) -> dict:
    try:
        sys.path.insert(0, str(_PROJECT_ROOT))
        from ai_workflow.requirement_reviewer_auto import check_material_gate
        from ai_workflow.test_case_formatter import (
            _auto_breakdown_requirement,
            compose_test_points_from_structure,
            _auto_generate_test_cases,
        )
        from ai_workflow.excel.test_case_writer import write_test_cases
        from ai_workflow.config import get_version_dir

        gate = check_material_gate(req_text)
        if not gate["gate_passed"]:
            return {"ok": False, "error": gate["reason"]}
        bd = _auto_breakdown_requirement(req_text, version)
        tp = compose_test_points_from_structure(bd)
        cases, meta = _auto_generate_test_cases(tp, bd, version)

        vdir, tdir = get_version_dir(version)
        vdir.mkdir(parents=True, exist_ok=True)
        tdir.mkdir(parents=True, exist_ok=True)

        (vdir / "test_points.json").write_text(json.dumps(tp, ensure_ascii=False, indent=2), encoding="utf-8")
        (vdir / "backlog.md").write_text(_build_backlog(bd), encoding="utf-8")
        (tdir / "test_cases.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
        excel = write_test_cases(cases, version)

        return {
            "ok": True,
            "epics": len(bd.get("epics", [])),
            "stories": sum(len(e.get("stories", [])) for e in bd.get("epics", [])),
            "test_points": len(tp),
            "test_cases": len(cases),
            "modules": meta.get("modules", {}),
            "outputs": {
                "backlog": str(vdir / "backlog.md"),
                "test_points": str(vdir / "test_points.json"),
                "test_cases_json": str(tdir / "test_cases.json"),
                "test_cases_xlsx": excel,
            },
        }
    except Exception as exc:
        import traceback
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "tb": traceback.format_exc()}


def _build_backlog(bd: dict) -> str:
    lines = [f"# {bd.get('requirement_title', '需求分解')}", ""]
    for epic in bd.get("epics", []):
        lines += [f"## {epic['id']}: {epic['title']}",
                  f"**模块**: {epic.get('module','General')}  |  **故事数**: {len(epic.get('stories',[]))}", ""]
        for story in epic.get("stories", []):
            lines += [f"### {story['id']}: {story['title']}",
                      f"**优先级**: {story.get('priority','P1')}"]
            for ac in story.get("acceptance_criteria", []):
                lines.append(f"- {ac}")
            lines.append("")
    return "\n".join(lines)


def build_result_prompt(result: dict, version: str) -> str:
    lines = ["", "## 工作流自动执行结果", "",
             f"**版本**: `{version}`  ·  **流程**: 简化流水线 (S1→S2→S4→S5)", ""]
    if not result.get("ok"):
        return "\n".join(lines + [f"**状态**: ❌ 执行失败\n**错误**: `{result.get('error','')}`"])

    lines += [
        "**S1 需求审查**: 材料门禁通过（评分由 LLM 按 STAGE_S1_REVIEW.mdc 执行）",
        f"**S2 需求分解**: ✅ {result['epics']} Epic / {result['stories']} Story",
        f"**S4 测试点**: ✅ {result['test_points']} 个",
        f"**S5 测试用例**: ✅ {result['test_cases']} 条",
    ]
    mods = result.get("modules", {})
    if mods:
        lines.append(f"**用例分布**: UI={mods.get('UI',0)} 条  |  BIZ={mods.get('BIZ',0)} 条")

    lines += ["", "**产出文件**:", "  - `workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.md` — Epic/Story 分解"]
    lines += ["  - `workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json` — 测试点"]
    lines += ["  - `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/test_cases.json` — 测试用例 JSON"]
    lines += ["  - `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/test_cases.md` / `test_cases.xlsx` — 仅在已确认项目且存在项目级导出配置/模板时生成", ""]
    lines.append("---")
    lines.append("请以 Markdown 格式展示以上产出文件列表，并提示用户执行完测试后可提交反馈进行迭代优化。")
    return "\n".join(lines)


def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({"prompt": "", "agentMessage": ""})); return
        inp = json.loads(raw)
        prompt = inp.get("prompt", "")

        if not any(re.search(p, prompt) for p in _WORKFLOW_PATTERNS):
            print(json.dumps({"prompt": prompt})); return

        sys.stderr.write("[Hook] Workflow trigger detected\n"); sys.stderr.flush()

        refs = extract_refs(prompt)
        req_text = read_req(refs) if refs else prompt.strip()
        if not req_text or len(req_text) < 50:
            print(json.dumps({"prompt": prompt, "agentMessage": "No valid requirement text found."})); return

        version = f"v_auto_{time.strftime('%Y%m%d%H%M%S')}"
        sys.stderr.write(f"[Hook] Running auto flow version={version}\n"); sys.stderr.flush()
        result = auto_flow(req_text, version)
        sys.stderr.write(f"[Hook] Done: ok={result.get('ok')} cases={result.get('test_cases',0)}\n"); sys.stderr.flush()

        updated = prompt + "\n" + build_result_prompt(result, version)
        msg = (f"Auto-executed: {result.get('test_cases',0)} cases ({version})"
               if result.get("ok") else f"Hook failed: {result.get('error','')}")
        print(json.dumps({"prompt": updated, "agentMessage": msg}), flush=True)

    except json.JSONDecodeError:
        print(json.dumps({"prompt": ""}))
    except Exception as exc:
        import traceback
        sys.stderr.write(f"[Hook Error] {type(exc).__name__}: {exc}\n"); sys.stderr.flush()
        print(json.dumps({"prompt": ""}))


# ── self-test ───────────────────────────────────────────────────────
def self_test() -> int:
    """python3 .cursor/hooks/docx_hook.py --self-test

    验证 4 项（不测 auto_flow，因为它依赖 ai_workflow + 写文件）：
      1. extract_refs 3 子 case（@ "/path/file.md" / @'path' / @path）
      2. build_result_prompt ok 路径 + fail 路径
      3. main() 无 workflow trigger → stdout 仅回显 prompt
      4. main() 空 stdin / 无效 JSON → 不崩
    """
    # Case 1: extract_refs（v6.2 修复：双/单引号 + 无引号去重）
    r1 = extract_refs('看一下 @"docs/req.md" 和 @\'notes.md\' 还有 @something.md')
    assert len(r1) == 3, f"Case 1: expected 3 refs (dedup 后), got {len(r1)}: {r1}"
    assert r1[0] == "docs/req.md", f"Case 1a: expected 'docs/req.md', got '{r1[0]}'"
    assert r1[1] == "notes.md", f"Case 1b: expected 'notes.md', got '{r1[1]}'"
    assert r1[2] == "something.md", f"Case 1c: expected 'something.md', got '{r1[2]}'"

    r1b = extract_refs("no refs here")
    assert r1b == [], f"Case 1d: expected empty, got {r1b}"
    # 单一 @无引号应该只出现一次
    r1c = extract_refs("看 @only.md 一个")
    assert len(r1c) == 1, f"Case 1e: expected 1 ref, got {len(r1c)}: {r1c}"
    assert r1c[0] == "only.md", f"Case 1e: expected 'only.md', got '{r1c[0]}'"
    # 同一路径同时有双引号 + 无引号 → 去重
    r1d = extract_refs('@"foo.md" 和 @foo.md')
    assert len(r1d) == 1, f"Case 1f: dedup 期望 1, got {len(r1d)}: {r1d}"
    assert r1d[0] == "foo.md", f"Case 1f: expected 'foo.md', got '{r1d[0]}'"
    print(f"  [OK] Case 1: extract_refs 6 sub-cases pass（v6.2 dedup 修复）")

    # Case 2: build_result_prompt
    r2_ok = build_result_prompt({
        "ok": True,
        "epics": 3, "stories": 8,
        "test_points": 24, "test_cases": 24,
        "modules": {"UI": 10, "BIZ": 14},
    }, "v1.0")
    assert "工作流自动执行结果" in r2_ok, "Case 2a: 应含'工作流自动执行结果'"
    assert "3 Epic / 8 Story" in r2_ok, "Case 2a: 应含 '3 Epic / 8 Story'"
    assert "24 个" in r2_ok, "Case 2a: 应含 '24 个'"
    assert "24 条" in r2_ok, "Case 2a: 应含 '24 条'"
    assert "UI=10" in r2_ok, "Case 2a: 应含 'UI=10' 模块分布"

    r2_fail = build_result_prompt({"ok": False, "error": "X 失败原因"}, "v1.0")
    assert "❌ 执行失败" in r2_fail, "Case 2b: 应含 ❌"
    assert "X 失败原因" in r2_fail, "Case 2b: 应含 error"
    print(f"  [OK] Case 2: build_result_prompt ok + fail 两条路径")

    # Case 3: main() 无 workflow trigger → stdout 仅回显 prompt
    proc3 = __import__("subprocess").run(
        [sys.executable, __file__],
        input=json.dumps({"prompt": "hello 普通对话"}),
        capture_output=True, text=True, timeout=10,
    )
    assert proc3.returncode == 0, f"Case 3: expected exit 0, got {proc3.returncode}"
    out3 = json.loads(proc3.stdout.strip())
    assert out3["prompt"] == "hello 普通对话", f"Case 3: expected prompt 回显, got '{out3['prompt']}'"
    print(f"  [OK] Case 3: 无 trigger → 回显原 prompt")

    # Case 4: main() 空 stdin + 无效 JSON
    proc4a = __import__("subprocess").run(
        [sys.executable, __file__], input="",
        capture_output=True, text=True, timeout=10,
    )
    assert proc4a.returncode == 0, f"Case 4a (空 stdin): expected exit 0, got {proc4a.returncode}"
    proc4b = __import__("subprocess").run(
        [sys.executable, __file__], input="not-json",
        capture_output=True, text=True, timeout=10,
    )
    assert proc4b.returncode == 0, f"Case 4b (无效 JSON): expected exit 0, got {proc4b.returncode}"
    print(f"  [OK] Case 4: 空 stdin + 无效 JSON 均 exit 0")

    print("  [OK] self-test passed (4 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    main()
