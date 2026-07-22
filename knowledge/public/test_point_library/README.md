# TP 知识库 — 根目录

> **性质**：公共知识库（入 Git）
> **用途**：AIDocxWorkFlow S5 阶段可复用的测试点模板库
> **维护规则**：入库须经人工审核；数据库是主存储，.md 候选文件是审核过渡态

---

## 目录结构

```
test_point_library/
├── tp_library.db         ← 主数据库（SQLite，v33 Round 6 创建）
├── _candidates/          ← 候选过渡区（入库审核用，完成后保留备查）
└── README.md             ← 本文件
```

---

## 数据库

### 路径

```
knowledge/public/test_point_library/tp_library.db
```

### Schema

**tp_candidates 表**（最小集）：

| 字段 | 类型 | 说明 |
|------|------|------|
| tp_id | TEXT PK | 测试点 ID |
| module | TEXT | 模块（BIZ/UI/LOG/LINK/DATA/...) |
| epic_id | TEXT | Epic ID |
| story_id | TEXT | Story ID |
| obj_id | TEXT | 需求对象 ID（可选）|
| feature_point_ref | TEXT | 功能点引用（可选）|
| test_point_type | TEXT | POSITIVE/EXCEPTION/BOUNDARY/ERROR/OA_NORMAL/OA_ABNORMAL/NEGATIVE |
| priority | TEXT | P0/P1/P2（可选）|
| is_assumed | INTEGER | 是否有假设（0/1）|
| description | TEXT | 可执行描述（场景+步骤+预期结果）|
| ac_summary | TEXT | 验收标准摘要 |
| source_req | TEXT | 来源需求名 |
| source_version | TEXT | 来源版本 |
| round_extracted | TEXT | 抽取轮次 |
| status | TEXT | 见状态机 |
| audit_notes | TEXT | 审核意见 |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

**audit_log 表**：

| 字段 | 说明 |
|------|------|
| tp_id | 关联 TP |
| action | 操作类型（import_to_db/approved/rejected/modified）|
| old_status | 操作前状态 |
| new_status | 操作后状态 |
| auditor | 审核人 |
| note | 备注 |
| ts | 时间戳 |

### 状态机

```
in_repo_pending_review
        ↓ [人工审核: 通过]
approved ← 入库正式候选，S5 可引用
        ↓ [人工审核: 拒绝]
rejected ← 保留记录，禁止 S5 引用
        ↓ [审核后修改]
modified ← 重新 pending_review
```

### 常用查询

```sql
-- 列出所有待审 TP
SELECT tp_id, module, test_point_type, description FROM tp_candidates
WHERE status = 'in_repo_pending_review';

-- 按模块统计
SELECT module, COUNT(*) FROM tp_candidates GROUP BY module;

-- 搜索含关键词的 TP
SELECT * FROM tp_candidates
WHERE description LIKE '%折扣%' OR ac_summary LIKE '%折扣%';
```

---

## 审核流程

1. Agent 从 `workflow_assets/` 抽取候选 → 写入 `_candidates/` → **导入 DB**（`import_to_db`）
2. 人工审核 DB 中 `status='in_repo_pending_review'` 的记录
3. 审核人更新 `status`（approved/rejected）+ `audit_notes`
4. 通过 → S5 阶段可引用

---

## 激活进度（v33）

| 指标 | 值 |
|---|---|
| 入库总数 | 10 条 |
| 待审数 | 10 条（`in_repo_pending_review`）|
| 已批准 | 0 条 |
| 已拒绝 | 0 条 |
| 覆盖模块 | BIZ(5) / UI(3) / LOG(1) / LINK(1) |
| 覆盖类型 | POSITIVE(7) / EXCEPTION(2) / BOUNDARY(1) |
| 覆盖 Epic | BIZ-001/002/003/004, UI-001/002 |

---

## Git 管理

- `tp_library.db` 入 Git（SQLite 文件可版本化）
- `_candidates/` 目录入 Git（审核记录备查）
- `README.md` 入 Git

> 本库由 v33 goal-loop 创建，DT-V33-005-FINAL。
