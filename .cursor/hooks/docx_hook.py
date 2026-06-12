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
    refs, seen = [], set()
    for pat in [r'@"([^"]+\.md)"', r"@'([^']+\.md)'", r'@([^\s]+\.md)']:
        for m in re.finditer(pat, prompt):
            p = m.group(1).strip()
            if p and p not in seen and not p.startswith("-"):
                seen.add(p); refs.append(p)
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
        from ai_workflow.requirement_reviewer_auto import auto_review_requirement
        from ai_workflow.test_case_formatter import (
            _auto_breakdown_requirement,
            compose_test_points_from_structure,
            _auto_generate_test_cases,
        )
        from ai_workflow.excel.test_case_writer import write_test_cases
        from ai_workflow.config import get_version_dir

        ar = auto_review_requirement(req_text)
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
            "verdict": ar.get("verdict", "PASS"),
            "score": ar.get("score_total"),
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

    v = result["verdict"]
    lines += [
        f"**S1 需求审查**: {'✅' if v=='PASS' else '⚠️'} score={result.get('score','N/A')}/10 → {v}",
        f"**S2 需求分解**: ✅ {result['epics']} Epic / {result['stories']} Story",
        f"**S4 测试点**: ✅ {result['test_points']} 个",
        f"**S5 测试用例**: ✅ {result['test_cases']} 条",
    ]
    mods = result.get("modules", {})
    if mods:
        lines.append(f"**用例分布**: UI={mods.get('UI',0)} 条  |  BIZ={mods.get('BIZ',0)} 条")

    lines += ["", "**产出文件**:", "  - `requirements/<version>/backlog.md` — Epic/Story 分解"]
    lines += ["  - `requirements/<version>/test_points.json` — 测试点"]
    lines += ["  - `test_cases/<version>/test_cases.json` — 测试用例 JSON"]
    lines += ["  - `test_cases/<version>/test_cases.xlsx` — 测试用例 Excel（可直接执行）", ""]
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


if __name__ == "__main__":
    main()
