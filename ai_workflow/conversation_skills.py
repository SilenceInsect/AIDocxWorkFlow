#!/usr/bin/env python3
"""AIDocxWorkFlow — AI 协作技能工厂

每个函数生成对应阶段的 system_prompt、user_template 和 save 函数。
AI 读取 prompt，生成内容后调用 save_* 函数写入文件。
"""

from __future__ import annotations

import json, os
from pathlib import Path
from typing import Any

# ── 路径常量 ───────────────────────────────────────────────────────────────

_ROOT = Path(__file__).parent.parent.resolve()   # AIDocxWorkFlow/
WF    = _ROOT / "workflow_assets"


def _req_dir(req_name: str) -> Path:
    return WF / req_name


def _stage_dir(req_name: str, stage: str) -> Path:
    mapping = {
        "S1":   "「S1 需求评审」",
        "S2":   "「S2 需求拆解」",
        "S2.5": "「S2.5 迭代规划」",
        "S3":   "「S3 原型导出」",
        "S4":   "「S4 流程图导出」",
        "S5":   "「S5 测试点生成」",
        "S6":   "「S6 测试用例生成」",
        "S7":   "「S7 用例审查」",
        "S8":   "「S8 自迭代」",
    }
    return _req_dir(req_name) / mapping.get(stage, stage) / "v1.0"


# ─────────────────────────────────────────────────────────────────────────────
# S2.5 — 迭代规划
# ─────────────────────────────────────────────────────────────────────────────

def make_stage2_5_skill(req_name: str = "游戏道具商城系统", version: str = "v1.0",
                          project_config: dict | None = None) -> dict:
    """生成 S2.5 迭代规划的 AI 协作技能。

    Args:
        req_name: 需求名称
        version: 版本标识
        project_config: 项目配置字典，字段见下方 schema
    """
    # 读取 backlog
    bd_path = _stage_dir(req_name, "S2") / "backlog.json"
    backlog_data = {}
    if bd_path.exists():
        with bd_path.open(encoding="utf-8") as f:
            backlog_data = json.load(f)

    epics   = backlog_data.get("epics", [])
    summary = backlog_data.get("summary", {})

    epic_list = "\n".join(
        f"  [{e['id']}] {e['title']} (预计{e.get('estimated_weeks', '?')}周, {len(e['stories'])}个Story)"
        for e in epics
    )

    # 项目配置 schema（若未传入则用空模板）
    cfg = project_config or {}
    config_summary = (
        f"项目名：{cfg.get('req_name', req_name)}，"
        f"版本：{cfg.get('version', version)}，"
        f"排期：{cfg.get('schedule', {}).get('start_date', '?')} ~ {cfg.get('schedule', {}).get('end_date', '?')}，"
        f"策划 {cfg.get('estimates', {}).get('planning_hours', '?')}h / "
        f"前端 {cfg.get('estimates', {}).get('frontend_hours', '?')}h / "
        f"后端 {cfg.get('estimates', {}).get('backend_hours', '?')}h / "
        f"测试 {cfg.get('estimates', {}).get('qa_hours', '?')}h，"
        f"团队：前端{cfg.get('team_size', {}).get('frontend', '?')}人·"
        f"后端{cfg.get('team_size', {}).get('backend', '?')}人·"
        f"测试{cfg.get('team_size', {}).get('qa', '?')}人"
    )

    system_prompt = """你是一个专业的游戏项目迭代规划工程师，擅长将需求 Epic 拆解为可执行的迭代计划（Sprint）。

## 工作规范

### 前置输入
- Epic 列表（含估算工时、Story 数量、优先级）
- 项目配置（项目名/版本/排期/各角色预估工时/团队规模）
- 已知风险点

### 项目配置参数（必须体现在报告中）

| 参数 | 来源 |
|------|------|
| 项目名 | project_config.req_name |
| 版本名 | project_config.version |
| 排期开始/截止 | project_config.schedule |
| 策划/前端/后端/测试预估工时 | project_config.estimates |
| 团队规模 | project_config.team_size |
| 迭代总工时（周） | project_config.iterations.total_weeks |

### 输出要求（Markdown + JSON 双格式）

#### 1. Markdown 文档（iteration_plan.md）

```markdown
# 迭代规划 — <项目名> <版本>

## 迭代概览
- 总 Epic 数：X
- 总 Story 数：X
- 总工时估算：X 周
- 迭代轮数：X 轮

## 1. 项目配置

| 参数 | 数值 |
|------|------|
| 项目名 | ... |
| 版本名 | v1.0 |
| 排期开始 | YYYY-MM-DD |
| 排期截止 | YYYY-MM-DD |
| 策划预估工时 | N h |
| 前端预估工时 | N h |
| 后端预估工时 | N h |
| 测试预估工时 | N h |
| 团队规模 | 前端N人 · 后端N人 · 测试N人 |
| 迭代总工时 | N 周 |

## 2. 迭代目标

- 目标1
- 目标2

## 3. 负载平衡

| 成员 | 角色 | 任务数 | 总工时(h) | 迭代可用(h) | 状态 |
|------|------|--------|-----------|-------------|------|
| ... | 前端 | ... | ... | ... | 正常/过载/富余 |

## 4. 里程碑

| 里程碑 | 时间点 | 交付内容 | 通过标准 |
|--------|--------|----------|----------|
| M1 | Sprint 1 末 | ... | ... |

## 5. 资源规划

| 角色 | 人数 | 估算工时(h) |
|------|------|-------------|
| 前端 | N | ... |
| 后端 | N | ... |
| 测试 | N | ... |

## 6. 风险与依赖

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| ... | 高 | ... |
```

#### 2. JSON 数据（iteration_plan.json）

```json
{
  "version": "v1.0",
  "date": "<今天日期>",
  "stage": "S2.5",
  "req_name": "<项目名>",
  "project_config": {
    "req_name": "<项目名>",
    "version": "v1.0",
    "schedule": { "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" },
    "estimates": {
      "planning_hours": N,
      "frontend_hours": N,
      "backend_hours": N,
      "qa_hours": N
    },
    "team_size": { "frontend": N, "backend": N, "qa": N },
    "iterations": { "total_weeks": N, "total_hours_per_person": N }
  },
  "sprints": [
    {
      "sprint_id": "S1",
      "title": "基础能力",
      "goal": "...",
      "epics": ["EPIC-ID-1"],
      "story_ids": ["STORY-ID-1"],
      "estimated_weeks": 2,
      "milestone": "M1",
      "risk_level": "low",
      "risk_items": ["..."],
      "deliverables": ["..."]
    }
  ],
  "milestones": [
    {
      "id": "M1",
      "title": "Alpha 发布",
      "timing": "Sprint 1 末",
      "deliverables": ["..."],
      "pass_criteria": ["..."]
    }
  ],
  "load_balance": [
    {
      "member": "...",
      "role": "前端",
      "task_count": N,
      "total_hours": N,
      "available_hours": N,
      "status": "正常"
    }
  ],
  "resource_plan": {
    "frontend": N,
    "backend": N,
    "qa": N,
    "total_hours": { "frontend": N, "backend": N, "qa": N }
  },
  "total_weeks": N,
  "risks": [
    {
      "description": "...",
      "severity": "high",
      "mitigation": "..."
    }
  ]
}
```

## 质量要求
- 每个 Sprint 必须有明确的目标（goal）和交付物（deliverables）
- Epic 的优先顺序参考 backlog.json 中的 priority_epics
- 总工时不超过团队可用工时（参考 project_config 中的 estimates 和 team_size）
- 里程碑需与业务价值对齐
- 项目配置参数必须完整填入 project_config 字段
"""
    return {
        "system_prompt": system_prompt,
        "user_template": f"""## <项目名> — 迭代规划（S2.5）

请基于以下信息制定迭代计划。

### 项目配置
{config_summary}

### Epic 清单（共 {summary.get('epic_count', len(epics))} 个，{summary.get('story_count', 0)} 个 Story）
{epic_list or "(Epic 数据加载失败，请从 backlog.json 读取)"}

### 关键风险点（来自 S1.5）
- 汇率换算精度：角分四舍五入，订单锁定汇率时机
- 配置变更生效时机：VIP等级/促销/hot标签变更后实时生效
- 折扣叠加边界：限时折扣+VIP折扣的最优价判定逻辑

### 优先级 Epic（优先安排）
{backlog_data.get('priority_epics', [])}

请按以下步骤工作：
1. 分析 Epic 间的依赖关系
2. 基于 project_config 中的排期和工时约束，划分 Sprint（每轮 1-3 周，当前项目迭代节奏较快，{cfg.get('iterations', {}).get('total_weeks', '?')} 周内完成）
3. 确定里程碑（M1: 核心购买流程可用, M2: 全功能可用, M3: 上线稳定）
4. 计算各角色负载（前端{cfg.get('team_size', {}).get('frontend', '?')}人·后端{cfg.get('team_size', {}).get('backend', '?')}人·测试{cfg.get('team_size', {}).get('qa', '?')}人）
5. 识别风险并提出缓解措施
6. 输出 Markdown 文档和 JSON 数据到文件

输出格式：先给 Markdown 计划，再给 JSON（纯 JSON，不含 markdown 代码块）。
请将结果保存到 _STAGE_DIR_。
""".replace("_STAGE_DIR_", str(_stage_dir(req_name, "S2.5"))),
    }


def save_iteration_plan(req_name: str, plan_md: str, plan_json: dict | str,
                         version: str = "v1.0",
                         project_config: dict | None = None) -> dict:
    """保存 S2.5 迭代规划结果。"""
    d = _stage_dir(req_name, "S2.5")
    d.mkdir(parents=True, exist_ok=True)

    md_path = d / "iteration_plan.md"
    json_path = d / "iteration_plan.json"
    cfg_path = d / "project_config.json"

    # 保存 Markdown
    with md_path.open("w", encoding="utf-8") as f:
        f.write(plan_md.strip())
    print(f"[S2.5] Markdown → {md_path}")

    # 保存 JSON
    if isinstance(plan_json, str):
        plan_json = json.loads(plan_json)
    plan_json["version"] = version
    plan_json["stage"] = "S2.5"
    plan_json["req_name"] = req_name

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(plan_json, f, ensure_ascii=False, indent=2)
    print(f"[S2.5] JSON → {json_path}")

    # 保存项目配置
    if project_config:
        cfg = project_config if isinstance(project_config, dict) else json.loads(project_config)
        cfg["version"] = version
        cfg["stage"] = "S2.5"
        cfg["req_name"] = req_name
        with cfg_path.open("w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        print(f"[S2.5] project_config.json → {cfg_path}")

    return {"md": str(md_path), "json": str(json_path), "config": str(cfg_path)}


# ─────────────────────────────────────────────────────────────────────────────
# S3 — 原型导出
# ─────────────────────────────────────────────────────────────────────────────

def make_stage3_skill(req_name: str = "游戏道具商城系统", version: str = "v1.0") -> dict:
    """生成 S3 页面原型导出的 AI 协作技能。"""
    system_prompt = """你是一个专业的 UI/UX 原型设计师，擅长将需求转化为高保真页面原型描述和 Mermaid 页面流图。

## 工作规范

### 输入
- Epic/Story 列表（来自 backlog.json）
- 已有的业务流程图（来自 S4 business_flow.md，可选参考）

### 输出要求

#### 1. 页面原型描述（prototype.md）

每个页面包含：
- **页面名称** 和 **页面 ID**（格式：`PAGE-XXX`）
- **入口来源**：用户从哪个页面跳转而来
- **核心功能**：页面提供的主要功能
- **布局结构**：文字描述页面布局（标题区、内容区、操作区）
- **交互元素**：按钮、表单、数据列表等
- **状态说明**：正常态、空数据态、加载态、错误态

示例：
```markdown
## PAGE-001：商城首页

- **入口来源**：玩家登录后自动进入
- **核心功能**：展示道具分类、热门道具、搜索入口
- **布局结构**：
  - 顶部：Logo + 搜索栏 + 用户信息
  - 左侧：分类导航栏（武器/时装/坐骑/消耗品/礼包）
  - 主区域：热门道具推荐区（10个）+ 分类道具列表
  - 底部：分页控件
- **交互元素**：
  - 搜索框（点击触发搜索，支持模糊匹配）
  - 分类标签（点击切换分类，URL 参数变化）
  - 道具卡片（点击跳转详情页）
  - 分页器（切换页面）
- **状态说明**：
  - 空数据：无道具时显示"暂无道具"
  - 加载中：骨架屏占位
```

#### 2. Mermaid 页面流图

```mermaid
flowchart TD
    Start([玩家进入商城]) --> Home[商城首页]
    Home --> Search[搜索页]
    Home --> Category[分类列表页]
    Home --> Hot[热门道具区]
    Hot --> Detail[道具详情页]
    Category --> Detail
    Search --> Detail
    Detail --> Confirm[购买确认弹窗]
    Confirm --> Pay[支付页]
    Pay --> Success[成功页]
    Pay --> Fail[失败页]
    Success --> Mail[邮件通知]
```

## 质量要求
- 覆盖所有 UI 相关的 Epic（UI-SHOP, UI-DETAIL, BIZ-PURCHASE 中的购买流程页面）
- 每个页面必须有唯一的 PAGE-ID
- 页面流图必须与 S4 流程图对齐
- 包含必要的状态说明
"""
    return {
        "system_prompt": system_prompt,
        "user_template": f"""## 游戏道具商城系统 — 原型导出（S3）

基于以下 Story 清单设计页面原型。

### 涉及页面的 Epic/Story（来自 backlog.json）
请重点关注以下模块的页面：
1. **UI-SHOP**（商城首页）：热门道具展示、分类导航、搜索
2. **UI-DETAIL**（道具详情页）：道具信息展示、数量选择
3. **BIZ-PURCHASE**（购买流程）：购买确认弹窗、支付页、成功/失败页

### 已有的业务流程（来自 S4）可参考：
- 请先检查 _STAGE_DIR_REF_/business_flow.md 是否存在

### 输出要求：
1. 编写 `prototype.md`，包含所有页面的详细描述
2. 在 `prototype.md` 末尾包含 Mermaid 页面流图
3. 输出 JSON 格式的页面清单：

```json
{{
  "version": "{version}",
  "stage": "S3",
  "req_name": "{req_name}",
  "pages": [
    {{
      "page_id": "PAGE-001",
      "page_name": "商城首页",
      "module": "UI-SHOP",
      "entry_source": "玩家登录后自动进入",
      "core_functions": ["热门道具展示", "分类导航", "搜索"],
      "interactions": ["搜索框", "分类标签", "道具卡片点击", "分页"],
      "states": ["正常", "空数据", "加载中"]
    }}
  ]
}}
```

请将 `prototype.md` 和 `prototype.json` 保存到 _STAGE_DIR_。
""".replace("_STAGE_DIR_", str(_stage_dir(req_name, "S3"))) \
         .replace("_STAGE_DIR_REF_", str(_stage_dir(req_name, "S4"))),
    }


def save_stage3_output(req_name: str, prototype_md: str, prototype_json: dict | str,
                        version: str = "v1.0") -> dict:
    """保存 S3 原型导出结果。"""
    d = _stage_dir(req_name, "S3")
    d.mkdir(parents=True, exist_ok=True)

    md_path = d / "prototype.md"
    json_path = d / "prototype.json"

    with md_path.open("w", encoding="utf-8") as f:
        f.write(prototype_md.strip())
    print(f"[S3] Markdown → {md_path}")

    if isinstance(prototype_json, str):
        prototype_json = json.loads(prototype_json)
    prototype_json["version"] = version
    prototype_json["stage"] = "S3"
    prototype_json["req_name"] = req_name

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(prototype_json, f, ensure_ascii=False, indent=2)
    print(f"[S3] JSON → {json_path}")

    return {"md": str(md_path), "json": str(json_path)}


# ─────────────────────────────────────────────────────────────────────────────
# S2 — 需求拆解（make only，save 由 AI 调用）
# ─────────────────────────────────────────────────────────────────────────────

def make_stage2_skill(req_name: str = "游戏道具商城系统", version: str = "v1.0") -> dict:
    """生成 S2 需求拆解的 AI 协作技能。"""
    ep_path = _stage_dir(req_name, "S1") / "exit_permission.json"
    req_path = _stage_dir(req_name, "S1") / "终版需求.md"

    ep_data = {}
    if ep_path.exists():
        with ep_path.open(encoding="utf-8") as f:
            ep_data = json.load(f)

    req_text = ""
    if req_path.exists():
        with req_path.open(encoding="utf-8") as f:
            req_text = f.read()[:3000]

    system_prompt = """你是一个专业的游戏需求分析师，负责将需求文档拆解为 Epic/Story/需求对象/功能点层级。

## 输出规范

### 层级结构
1. **Epic**（顶级需求模块）：按业务域划分，如"购买流程"、"VIP体系"、"商城首页"
2. **Story**（具体功能）：每个 Epic 下的具体功能点
3. **需求对象**（数据实体）：如玩家、订单、道具、促销规则
4. **功能点**（原子操作）：不可再分的最小功能单元

### 质量要求
- Epic 估算工时（周），Story 数量
- 每个 Story 包含：ID、标题、验收标准、前置条件、输入数据、预期输出
- 优先级标注（priority: true/false）
- 对应 backlog.json 的格式
"""
    user_template = f"""## 游戏道具商城系统 — 需求拆解（S2）

需求材料：
- 终版需求（{req_path}）：{req_text[:500]}...
- 准出许可：{ep_data.get('exit_permission', {})}

请执行 S2 需求拆解，输出：
1. `backlog.md`（Epic/Story 列表，Markdown 格式）
2. `backlog.json`（机器可读格式）

JSON 格式参考：
```json
{{
  "version": "{version}",
  "date": "<今天>",
  "stage": "S2",
  "req_name": "{req_name}",
  "quality_level": "{ep_data.get('exit_permission', {}).get('quality_level', 'MEDIUM')}",
  "summary": {{"epic_count": N, "story_count": N, "requirement_object_count": N, "feature_point_count": N}},
  "priority_epics": ["EPIC-ID-1", "EPIC-ID-2"],
  "epics": [
    {{
      "id": "EPIC-ID-1",
      "module": "MODULE",
      "title": "Epic标题",
      "estimated_weeks": N,
      "priority": true,
      "stories": [
        {{
          "id": "EPIC-ID-001",
          "title": "Story标题",
          "acceptance_criteria": ["AC1", "AC2"],
          "precondition": "前提条件",
          "input_data": "输入数据",
          "expected_output": "预期输出",
          "source": "original|clarification|fallback"
        }}
      ]
    }}
  ]
}}
```

请将结果保存到 _STAGE_DIR_。
""".replace("_STAGE_DIR_", str(_stage_dir(req_name, "S2")))
    return {"system_prompt": system_prompt, "user_template": user_template}


def save_stage2_output(req_name: str, backlog_md: str, backlog_json: dict | str,
                        version: str = "v1.0") -> dict:
    d = _stage_dir(req_name, "S2")
    d.mkdir(parents=True, exist_ok=True)

    md_path = d / "backlog.md"
    json_path = d / "backlog.json"

    with md_path.open("w", encoding="utf-8") as f:
        f.write(backlog_md.strip())
    print(f"[S2] backlog.md → {md_path}")

    if isinstance(backlog_json, str):
        backlog_json = json.loads(backlog_json)
    backlog_json["version"] = version
    backlog_json["stage"] = "S2"
    backlog_json["req_name"] = req_name

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(backlog_json, f, ensure_ascii=False, indent=2)
    print(f"[S2] backlog.json → {json_path}")

    return {"md": str(md_path), "json": str(json_path)}


# ─────────────────────────────────────────────────────────────────────────────
# S4 — 流程图导出
# ─────────────────────────────────────────────────────────────────────────────

def make_stage4_skill(req_name: str = "游戏道具商城系统", version: str = "v1.0") -> dict:
    """生成 S4 流程图导出的 AI 协作技能。

    v1.1+ 关键约束：4 类可机检 ID（风险点 + 异常树叶子） + 7 类风险点典型清单。
    S5/S6/S7 强依赖这些 ID——S7 100% 覆盖率审计的 SSoT。
    """
    system_prompt = """你是一个专业的业务流程设计师，负责将 S2 backlog 拆解为**可机检的 4 类产出**：
1. Mermaid 业务流程图（Flowchart）— 节点带 `S4-{EpicID}-FNN` ID
2. Mermaid 时序图（Sequence Diagram）
3. 异常/错误决策树 — 叶子节点带 `S4-{EpicID}-X.Y.Z` ID
4. 风险点清单 — 风险带 `R-NNN`（机器友好）+ `R-{EpicID}-NN`（人类可读）双重 ID

## 关键约束（v1.1+）

### 风险点 7 类典型清单（必覆盖最小集，禁止造词）
| 序号 | 风险类型 | 关键判据 |
|------|---------|----------|
| 1 | 竞态条件 | 涉及并发请求 / 锁 / 冻结 |
| 2 | 时间依赖 | 涉及时间戳 / TTL / 倒计时 |
| 3 | 状态损坏 | 涉及状态机 / 配置变更 |
| 4 | 支付幂等性 | 涉及第三方回调 / 订单号 |
| 5 | 数据一致性 | 涉及事务 / 回滚 |
| 6 | 资源/容量 | 涉及上限 / 满载 |
| 7 | 安全/合规 | 涉及鉴权 / 合规风控 |

### ID 命名规范
- 风险点：`R-001`（全局顺序）+ `R-{EpicID}-01`（按 Epic 局部）= 同一风险点
- 异常树叶子：`S4-{EpicID}-1.3.2`（X.Y.Z 三级）
- 流程图节点：`S4-{EpicID}-F03`（推荐，可选）

### 上游消费
- S2 backlog.json 的 `epics[].module`（必填，从 8 模块取值：CONFIG/UI/BIZ/AUX/LINK/LOG/SPECIAL/HINT）
- S2 backlog.json 的 `acceptance_criteria` 推导异常路径
- S3 prototype.md（推荐）消费 `PAGE-XXX` 节点

### 下游契约（S5/S6/S7 强依赖）
- S5 TP `s4_reference` 字段 = `R-{EpicID}-NN` 格式
- S6 禁止照抄 S4 节点名到用例字段
- S7 审查员 B P0 100% 覆盖率（风险点 + 异常树叶子）

## 输出规范

### 1. 业务流程图（Mermaid flowchart）
覆盖核心购买流程：用户操作 → 系统判断 → 结果输出

### 2. 时序图（Mermaid sequence）
展示关键场景中各系统组件的交互顺序

### 3. 异常决策树
覆盖异常路径：余额不足、支付失败、汇率异常、道具售罄等
**每个叶子节点必须有 ID**（S4-{EpicID}-X.Y.Z）

### 4. 风险点清单
每条风险带双重 ID + 7 类归类 + 异常树叶子交叉引用

## 模块定义 SSoT
⚠️ 模块定义见 `.cursor/MODULES.md` §1（项目级唯一真相源）。本文件不重写 8 模块表。

## 质量要求
- 每个 Epic 必须 4 类产出齐全
- 风险点 ID 全局唯一
- 异常树叶子节点 ID 唯一
- 风险点 ↔ 异常树叶子交叉引用 ≥ 50%
- Mermaid 语法合法
"""
    return {
        "system_prompt": system_prompt,
        "user_template": f"""## 游戏道具商城系统 — 流程图导出（S4）

基于 backlog.json 中的 Story 设计业务流程图（**v1.1+ 必须按可机检 ID 规范产出**）。

### 输入材料
1. **S2 backlog.json**（必填）— `epics[].module` + `acceptance_criteria`
2. **S3 prototype.md**（推荐）— `PAGE-XXX` 节点命名参考

请输出 `business_flow.md`，**4 类产出按顺序**：
1. **0. 元信息** — Epic × 模块 × 风险点数 × 异常树叶子数
2. **1. Epic 级产出**（每个 Epic 4 节）：
   - 1.1 主业务流程（Flowchart，节点带 `S4-{EpicID}-FNN` ID）
   - 1.2 时序图（Sequence）
   - 1.3 异常决策树（叶子带 `S4-{EpicID}-X.Y.Z` ID）
   - 1.4 风险点（双重 ID：`R-NNN` + `R-{EpicID}-NN`，7 类归类，↔ 异常树叶子）
3. **N. 风险点汇总（全局）** — 风险点表 `R-001` ~ `R-NNN` 全量列出（这是 S7 100% 覆盖率审计的 SSoT）

### 重点覆盖
- BIZ-PURCHASE 系列 Story（购买确认→游戏币支付→人民币支付→道具到账→邮件通知）
- CONFIG-DISCOUNT 系列 Story（折扣计算叠加规则）
- CONFIG-VIP 系列 Story（VIP折扣计算）
- AUX-CACHE / LINK-PAYMENT / LOG-PAYMENT / SPECIAL-VIP-CHANGE 等支撑模块

### 风险点 7 类必覆盖最小集
竞态条件 / 时间依赖 / 状态损坏 / 支付幂等性 / 数据一致性 / 资源容量 / 安全合规

### 严禁
- ❌ 不要写"风险1, 风险2"——必须带 `R-NNN` ID
- ❌ 不要省略异常树叶子 ↔ 风险点交叉引用
- ❌ 不要用模块中文别名

请将结果保存到 _STAGE_DIR_。
""".replace("_STAGE_DIR_", str(_stage_dir(req_name, "S4"))),
    }


def save_stage4_output(req_name: str, flow_md: str, version: str = "v1.0") -> dict:
    """保存 S4 流程图导出结果（v1.1+ 同时保存 JSON 索引供 S5 消费）。

    必传参数：
      - flow_md: business_flow.md 全文
    """
    import re
    d = _stage_dir(req_name, "S4")
    d.mkdir(parents=True, exist_ok=True)

    md_path = d / "business_flow.md"
    md_path.write_text(flow_md.strip(), encoding="utf-8")
    print(f"[S4] business_flow.md → {md_path}")

    # v1.1+ 提取可机检结构（风险点 + 异常树叶子）→ business_flow.json
    risk_pattern = re.compile(
        r"\|\s*(R-\d{3})\s*\|\s*(R-[A-Z\-]+-\d+)\s*\|"  # R-NNN + R-{EpicID}-NN
    )
    risks = []
    for m in risk_pattern.finditer(flow_md):
        risks.append({
            "risk_id_machine": m.group(1),
            "risk_id_human": m.group(2),
        })

    leaf_pattern = re.compile(r"S4-([A-Z\-]+)-(\d+\.\d+\.\d+)")
    leaves = list(set(leaf_pattern.findall(flow_md)))

    json_path = d / "business_flow.json"
    if risks or leaves:
        json_path.write_text(
            json.dumps(
                {
                    "version": version,
                    "stage": "S4",
                    "req_name": req_name,
                    "risks": risks,
                    "exception_tree_leaves": [
                        {"epic_id": epic_id, "leaf_id": f"S4-{epic_id}-{leaf}"}
                        for epic_id, leaf in leaves
                    ],
                    "summary": {
                        "risk_count": len(risks),
                        "exception_leaf_count": len(leaves),
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"[S4] business_flow.json → {json_path} (R={len(risks)} / leaves={len(leaves)})")

    return {"md": str(md_path), "json": str(json_path) if json_path.exists() else None}


# ─────────────────────────────────────────────────────────────────────────────
# 简化流水线执行器
# ─────────────────────────────────────────────────────────────────────────────

def execute_simple_flow(req_text: str, req_name: str = "游戏道具商城系统",
                        version: str = "v1.0", filename: str = "test_cases") -> dict:
    """简化流水线：S1 → S2 → S5 → S6（Python 自动化 + AI 协作）"""
    results = {"stages": {}, "overall_status": "running"}

    # S1：自动评分
    from ai_workflow.requirement_reviewer_auto import auto_review_requirement
    s1_result = auto_review_requirement(req_text)
    results["stages"]["S1"] = s1_result

    if s1_result.get("verdict") == "REJECT":
        results["overall_status"] = "REJECTED"
        return results

    # S2 / S5 / S6：由 AI 通过 conversation_skills 协作完成
    # 这三个阶段需要 AI 参与，不能纯自动化
    results["overall_status"] = "need_ai_collaboration"
    results["next_stage"] = "S2"
    results["skill"] = make_stage2_skill(req_name, version)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# 全流程执行器
# ─────────────────────────────────────────────────────────────────────────────

def execute_full_flow(req_name: str = "游戏道具商城系统",
                       version: str = "v1.0") -> dict:
    """完整流水线状态查询（不执行，由 AI 协作分阶段执行）"""
    stages = ["S1", "S2", "S2.5", "S3", "S4", "S5", "S6", "S7", "S8"]
    results = {}

    for s in stages:
        d = _stage_dir(req_name, s)
        stage_files = list(d.glob("*")) if d.exists() else []
        results[s] = {
            "done": d.exists() and len(stage_files) > 0,
            "dir": str(d),
            "files": [f.name for f in stage_files],
        }

    return results


if __name__ == "__main__":
    import pprint
    pprint.pprint(execute_full_flow())
