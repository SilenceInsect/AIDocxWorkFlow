#!/usr/bin/env python3
"""Update v303 snapshot to achieved."""
import json, os, sys
sys.path.insert(0, 'ai_workflow')
from goal_snapshot import update_snapshot

gid = open('.goal-log-db/active/_v303_gid.txt').read().strip()
update_snapshot(gid,
    status='achieved',
    loop_round=1,
    latest_artifact='governance/design_iter/plans/v303/CONVERGED.md',
    last_audit={
        'round': 1,
        'verdicts': {
            'V-001': 'PASS',
            'V-002': 'PASS',
            'V-003': 'PASS',
            'P-001': 'PASS',
            'P-002': 'PASS',
            'P-003': 'PASS',
            'P-004': 'PASS',
            'P-005': 'PASS',
            'P-006': 'PASS',
            'P-007': 'PASS',
        },
        'reverse_challenge': 'enforce_obj_p0_coverage._write_pri 双向 mirror 缺失：当前路径下 L1S6Validator 用 canonical 读，不触发；但若下游改回只读 priority 字段则 P0 失效。建议 v3.04 修复',
        'evidence_files': [
            'governance/design_iter/plans/v303/audit_1.md',
            'governance/design_iter/plans/v303/review_1.md',
            'governance/design_iter/plans/v303/CONVERGED.md',
            'ai_workflow/run_normalize_and_export.py',
            'workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx',
            'workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round19.bak.xlsx',
        ],
        'antipattern': [],
    },
    last_review={
        'round': 1,
        'sys_ids': [],
        'recommendations': [
            'driver 调用规范（必须用 normalize_payload 或 3 步骤全显式）',
            'SYS-008 防御条款固化到 SKILL v1.2.1',
            '_write_pri 双向 mirror 修复（v3.04）',
            'driver summary 暴露 obj_risk_stats 到 stdout（MINOR）',
        ],
        'follow_up_items': [
            {
                'description': '_write_pri 双向 mirror 缺失（优先级/P0 写一个 alias 另一个留 stale）',
                'severity': 'MAJOR',
                'suggested_fix': '把 _write_pri 改为同时写两个 alias 字段（保证 P0 promotion 在任意单字段视角都生效）',
                'source_round': 1,
                'source_criterion': '§5 audit_1 侧记',
            },
            {
                'description': 'driver 调用规范缺失（normalize_payload 自动调用 enforce，driver 必须用 normalize_payload 或显式调 3 步）',
                'severity': 'MAJOR',
                'suggested_fix': 'SKILL v1.2.1 加 driver 调用规范条目',
                'source_round': 1,
                'source_criterion': 'review_1 §2 规范问题',
            },
            {
                'description': 'V-303 expected 重复 33.5% 压缩（原 v3.02 carry）',
                'severity': 'MAJOR',
                'suggested_fix': 'scenario_group_merger 加 list(dict.fromkeys()) 保序去重，目标 ≥ 60% 减少',
                'source_round': 1,
                'source_criterion': '原 v3.02 V-003',
            },
        ],
    },
    follow_up_items=[
        {
            'description': '_write_pri 双向 mirror 缺失（优先级/P0 写一个 alias 另一个留 stale）',
            'severity': 'MAJOR',
            'suggested_fix': '把 _write_pri 改为同时写两个 alias 字段',
            'source_round': 1,
            'source_criterion': '§5 audit_1 侧记',
        },
        {
            'description': 'V-303 expected 重复 33.5% 压缩（原 v3.02 carry）',
            'severity': 'MAJOR',
            'suggested_fix': 'scenario_group_merger 加 list(dict.fromkeys()) 保序去重',
            'source_round': 1,
            'source_criterion': '原 v3.02 V-003',
        },
    ],
    efficiency_stats={
        'rounds_used': 1,
        'value_criteria_passed': '3/3',
        'process_criteria_passed': '7/7',
        'task_completed': '4/4',
        'closure_mode': 'achieved',
    },
)

# 验证
s = json.load(open(f'.goal-log-db/active/{gid}/snapshot.json'))
print(f'status={s["status"]}, round={s["loop_round"]}')
print(f'verdicts={list(s["last_audit"]["verdicts"].keys())}')
print(f'follow_up_items={len(s["follow_up_items"])}')
