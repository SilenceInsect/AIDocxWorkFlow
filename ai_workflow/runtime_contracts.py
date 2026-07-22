#!/usr/bin/env python3
"""AIDocxWorkFlow 运行时阶段契约表。

引入：
- 阶段目录/规则/skill 的统一映射
- S5/S6 的上下游输入契约
- 阶段必备输出与运行时 gate 定义
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent.resolve()
WORKFLOW_ROOT = ROOT / "workflow_assets"
KNOWLEDGE_ROOT = ROOT / "knowledge"
PUBLIC_KNOWLEDGE_ROOT = KNOWLEDGE_ROOT / "public"
PROJECT_KNOWLEDGE_ROOT = KNOWLEDGE_ROOT / "project_local"

STAGE_DIRECTORY_NAMES = {
    "S1": "「S1 需求评审」",
    "S2": "「S2 需求拆解」",
    "S2.5": "「S2.5 迭代规划」",
    "S3": "「S3 原型导出」",
    "S4": "「S4 流程图导出」",
    "S5": "「S5 测试点生成」",
    "S6": "「S6 测试用例生成」",
    "S7": "「S7 用例审查」",
    "S8": "「S8 自迭代」",
}

STAGE_RULE_FILES = {
    "S1": ".cursor/rules/STAGE_S1_REVIEW.mdc",
    "S1.5": ".cursor/rules/STAGE_S1.5 Clarification.mdc",
    "S2": ".cursor/rules/STAGE_S2_BREAKDOWN.mdc",
    "S2.5": ".cursor/rules/STAGE_S2_5_ITERATION.mdc",
    "S3": ".cursor/rules/STAGE_S3_PROTOTYPE.mdc",
    "S4": ".cursor/rules/STAGE_S4_FLOWCHART.mdc",
    "S5": ".cursor/rules/STAGE_S5_TEST_POINTS.mdc",
    "S6": ".cursor/rules/STAGE_S6_TEST_CASES.mdc",
    "S7": ".cursor/rules/STAGE_S7_REVIEW.mdc",
    "S8": ".cursor/rules/STAGE_S8_SELF_ITERATION.mdc",
}

STAGE_SKILL_DIRS = {
    "S1": ".cursor/skills/aidocx-s1-review/SKILL.md",
    "S1.5": ".cursor/skills/aidocx-s1-5-clarification/SKILL.md",
    "S2": ".cursor/skills/aidocx-s2-breakdown/SKILL.md",
    "S2.5": ".cursor/skills/aidocx-s2-5-iteration/SKILL.md",
    "S3": ".cursor/skills/aidocx-s3-prototype/SKILL.md",
    "S4": ".cursor/skills/aidocx-s4-flowchart/SKILL.md",
    "S5": ".cursor/skills/aidocx-s5-test-points/SKILL.md",
    "S6": ".cursor/skills/aidocx-s6-test-cases/SKILL.md",
    "S7": ".cursor/skills/aidocx-s7-review/SKILL.md",
    "S8": ".cursor/skills/aidocx-s8-self-iteration/SKILL.md",
}

GLOBAL_RULES = [
    "AGENTS.md",
    ".cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc",
]  

STAGE_CONTRACTS: dict[str, dict[str, Any]] = {
    "S5": {
        "primary_goal": "需求覆盖最大化，先出覆盖矩阵，再出测试点；任何未覆盖点必须显式备案。",
        "anti_patterns": [
            "coding_mindset_shrink",
            "silent_omission",
            "story_only_without_scenario_scan",
        ],
        "must_read": [
            "AGENTS.md",
            ".cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc",
            ".cursor/rules/STAGE_S5_TEST_POINTS.mdc",
            ".cursor/skills/aidocx-s5-test-points/SKILL.md",
        ],
        "upstream_inputs": [
            {
                "key": "s2_backlog",
                "label": "S2 backlog.md",
                "path": "workflow_assets/<REQ>/<VER>/「S2 需求拆解」/backlog.md",
                "required": True,
                "kind": "file",
            },
            {
                "key": "s2_backlog_json",
                "label": "S2 backlog.json",
                "path": "workflow_assets/<REQ>/<VER>/「S2 需求拆解」/backlog.json",
                "required": True,
                "kind": "file",
            },
            {
                "key": "s4_business_flow",
                "label": "S4 business_flow.md",
                "path": "workflow_assets/<REQ>/<VER>/「S4 流程图导出」/business_flow.md",
                "required": True,
                "kind": "file",
            },
            {
                "key": "module_templates_dir",
                "label": "模块模板目录",
                "path": "knowledge/public/module_templates",
                "required": True,
                "kind": "dir",
            },
        ],
        "downstream_contract": {
            "consumer_stage": "S6",
            "expects": [
                "test_points.json",
                "coverage_ledger.json",
                "omission_ledger.json",
            ],
            "critical_fields": [
                "story_id",
                "tp_id",
                "module",
                "test_point_type",
                "description",
                "s4_reference",
            ],
        },
        "required_outputs": [
            "stage_context.md",
            "stage_context.json",
            "read_ack.json",
            "test_points.json",
            "test_points_summary.json",
            "test_points_summary.md",
            "coverage_ledger.json",
            "omission_ledger.json",
        ],
        "gates": [
            "preflight_inputs_exist",
            "read_ack_written",
            "coverage_ledger_generated",
            "omission_ledger_generated",
        ],
    },
    "S6": {
        "primary_goal": "测试用例必须由 coverage ledger 驱动生成，默认目标不是最少用例，而是显式闭合覆盖缺口。",
        "anti_patterns": [
            "coding_mindset_shrink",
            "stage_local_optimization",
            "silent_omission",
        ],
        "must_read": [
            "AGENTS.md",
            ".cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc",
            ".cursor/rules/STAGE_S6_TEST_CASES.mdc",
            ".cursor/skills/aidocx-s6-test-cases/SKILL.md",
        ],
        "upstream_inputs": [
            {
                "key": "s5_test_points",
                "label": "S5 test_points.json",
                "path": "workflow_assets/<REQ>/<VER>/「S5 测试点生成」/test_points.json",
                "required": True,
                "kind": "file",
            },
            {
                "key": "s2_backlog_json",
                "label": "S2 backlog.json",
                "path": "workflow_assets/<REQ>/<VER>/「S2 需求拆解」/backlog.json",
                "required": True,
                "kind": "file",
            },
            {
                "key": "s4_business_flow",
                "label": "S4 business_flow.md",
                "path": "workflow_assets/<REQ>/<VER>/「S4 流程图导出」/business_flow.md",
                "required": True,
                "kind": "file",
            },
            {
                "key": "module_templates_dir",
                "label": "模块模板目录",
                "path": "knowledge/public/module_templates",
                "required": True,
                "kind": "dir",
            },
            {
                "key": "project_export_profile",
                "label": "项目级 S6 导出配置",
                "path": "knowledge/project_local/<PROJECT>/s6/export_profiles/test_cases.export.json",
                "required": False,
                "kind": "file",
            },
        ],
        "downstream_contract": {
            "consumer_stage": "S7",
            "expects": [
                "test_cases.json",
                "coverage_ledger.json",
                "omission_ledger.json",
            ],
            "critical_fields": [
                "case_id",
                "module",
                "story_id",
                "scenario",
                "test_steps",
                "expected_result",
            ],
        },
        "required_outputs": [
            "stage_context.md",
            "stage_context.json",
            "read_ack.json",
            "test_cases.json",
            "coverage_ledger.json",
            "omission_ledger.json",
        ],
        "gates": [
            "preflight_inputs_exist",
            "read_ack_written",
            "public_json_generated",
            "coverage_ledger_generated",
            "omission_ledger_generated",
        ],
    },
    "S7": {
        "primary_goal": "基于 coverage_ledger / omission_ledger 审查覆盖缺口，输出可追溯的事实快照与语义审查输入。",
        "anti_patterns": [
            "overall_pass_dependency",
            "silent_omission",
            "stage_local_optimization",
        ],
        "must_read": [
            "AGENTS.md",
            ".cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc",
            ".cursor/rules/STAGE_S7_REVIEW.mdc",
            ".cursor/skills/aidocx-s7-review/SKILL.md",
        ],
        "upstream_inputs": [
            {
                "key": "s6_test_cases_json",
                "label": "S6 test_cases.json",
                "path": "workflow_assets/<REQ>/<VER>/「S6 测试用例生成」/test_cases.json",
                "required": True,
                "kind": "file",
            },
            {
                "key": "s5_test_points_json",
                "label": "S5 test_points.json",
                "path": "workflow_assets/<REQ>/<VER>/「S5 测试点生成」/test_points.json",
                "required": False,
                "kind": "file",
            },
            {
                "key": "s4_business_flow_md",
                "label": "S4 business_flow.md",
                "path": "workflow_assets/<REQ>/<VER>/「S4 流程图导出」/business_flow.md",
                "required": False,
                "kind": "file",
            },
            {
                "key": "coverage_ledger_json",
                "label": "coverage_ledger.json",
                "path": "workflow_assets/<REQ>/<VER>/「S6 测试用例生成」/coverage_ledger.json",
                "required": False,
                "kind": "file",
            },
            {
                "key": "omission_ledger_json",
                "label": "omission_ledger.json",
                "path": "workflow_assets/<REQ>/<VER>/「S6 测试用例生成」/omission_ledger.json",
                "required": False,
                "kind": "file",
            },
        ],
        "downstream_contract": {
            "consumer_stage": "S8",
            "expects": [
                "review_snapshot.json",
                "review_snapshot.md",
                "review_report.json",
                "review_report.md",
            ],
            "critical_fields": [
                "reviewer_a",
                "reviewer_b",
                "recommendations",
            ],
        },
        "required_outputs": [
            "stage_context.md",
            "stage_context.json",
            "read_ack.json",
            "review_snapshot.json",
            "review_snapshot.md",
            "review_report.json",
            "review_report.md",
        ],
        "gates": [
            "preflight_inputs_exist",
            "read_ack_written",
            "review_snapshot_generated",
        ],
    },
    "S8": {
        "primary_goal": "从 S7 事实快照与反馈日志中归纳根因，形成可执行的迭代改进与归档。",
        "anti_patterns": [
            "overall_pass_dependency",
            "skip_root_cause",
            "stage_local_optimization",
        ],
        "must_read": [
            "AGENTS.md",
            ".cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc",
            ".cursor/rules/STAGE_S8_SELF_ITERATION.mdc",
            ".cursor/skills/aidocx-s8-self-iteration/SKILL.md",
        ],
        "upstream_inputs": [
            {
                "key": "s7_review_report_json",
                "label": "S7 review_report.json / review_snapshot.json",
                "path": "workflow_assets/<REQ>/<VER>/「S6 测试用例生成」/review_report.json",
                "required": True,
                "kind": "file",
            },
            {
                "key": "s5_test_points_json",
                "label": "S5 test_points.json",
                "path": "workflow_assets/<REQ>/<VER>/「S5 测试点生成」/test_points.json",
                "required": True,
                "kind": "file",
            },
            {
                "key": "s6_test_cases_json",
                "label": "S6 test_cases.json",
                "path": "workflow_assets/<REQ>/<VER>/「S6 测试用例生成」/test_cases.json",
                "required": True,
                "kind": "file",
            },
            {
                "key": "s4_business_flow_md",
                "label": "S4 business_flow.md",
                "path": "workflow_assets/<REQ>/<VER>/「S4 流程图导出」/business_flow.md",
                "required": True,
                "kind": "file",
            },
            {
                "key": "feedback_logs_dir",
                "label": "feedback_logs",
                "path": "workflow_assets/feedback_logs",
                "required": False,
                "kind": "dir",
            },
        ],
        "downstream_contract": {
            "consumer_stage": "knowledge/project_local/.review_queue",
            "expects": [
                "iteration.json",
                "iteration.md",
                "knowledge_review_candidates",
            ],
            "critical_fields": [
                "root_causes",
                "defect_patterns",
                "recommendations",
            ],
        },
        "required_outputs": [
            "stage_context.md",
            "stage_context.json",
            "read_ack.json",
            "iteration.json",
            "iteration.md",
        ],
        "gates": [
            "preflight_inputs_exist",
            "read_ack_written",
            "iteration_generated",
        ],
    },
}


def get_stage_dir(req_name: str, stage: str, version: str = "v1.0") -> Path:
    """根据 stage/req/version 算出阶段目录。

    返回值 (v8 主轴): WORKFLOW_ROOT / req_name / version / <阶段名>
    与 conversation_skills._resolve_stage_path() 保持一致。

    防御(v23):阶段名末尾空格 / 任意空白会被 strip,防止 Agent 在 bash 手敲
    `mkdir "「S2 需求拆解」  "` 之类的笔误污染工程目录树（参见 v23/PLAN.md 根因）。
    """
    raw_name = STAGE_DIRECTORY_NAMES.get(stage, stage)
    # v23 防御:目录名两端 strip 任意空白字符,确保不再产生带空格目录
    safe_name = raw_name.strip()
    return WORKFLOW_ROOT / req_name / version / safe_name


def resolve_contract_path(
    path_template: str,
    req_name: str,
    version: str,
    project_name: str | None = None,
) -> Path:
    path = (
        path_template
        .replace("<REQ>", req_name)
        .replace("<VER>", version)
        .replace("<PROJECT>", project_name or req_name)
    )
    return ROOT / path if not path.startswith("/") else Path(path)


def get_stage_contract(stage: str) -> dict[str, Any]:
    contract = deepcopy(STAGE_CONTRACTS.get(stage, {}))
    if contract and "stage" not in contract:
        contract["stage"] = stage
    return contract
