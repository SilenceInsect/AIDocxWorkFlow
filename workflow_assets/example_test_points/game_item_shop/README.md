# game_item_shop — 游戏道具商城系统 v1.0

> **完整 TP 样例**（S5 端到端跑通的最完整产出）
> **本目录**：S5 LLM 学习"完整 TP 该长什么样"的标准答案

---

## 1. 需求背景

| 维度 | 值 |
|------|---|
| **需求名** | 游戏道具商城系统 |
| **版本** | v1.0 |
| **业务类型** | 玩家购买道具（游戏币/人民币支付）|
| **端到端跑通** | S1 → S1.5 → S2 → S2.5 → S3 → S4 → S5 → S6 → S7 → S8 |
| **原始材料** | `workflow_assets/_archive_pre_rerun/游戏道具商城系统/「S1 需求评审」/v1.0/raw/游戏道具商城系统_v1.0.docx` |

---

## 2. Epic / Story 分布

| # | Epic ID | Epic 名称 | Story 数 | 命中文档 |
|---|---------|----------|---------|---------|
| 1 | **BIZ-PURCHASE** | 购买核心流程 | 5 | 购买确认 / 游戏币支付 / 人民币支付与汇率 / 道具即时到账 / 购买邮件 |
| 2 | **CONFIG-VIP** | VIP 等级体系 | 3 | VIP 等级配置管理 / VIP 折扣计算 / VIP 专属道具可见性 |
| 3 | **CONFIG-DISCOUNT** | 折扣与活动 | 5 | 促销配置 / 限时折扣 / 满减 / 新手礼包 / **折扣叠加规则（[fallback]）** |
| 4 | **UI-SHOP** | 商城 UI | 3 | 热门道具 / 分类导航 / 搜索功能 |
| 5 | **UI-DETAIL** | 道具详情 UI | 2 | 道具详情 / 数量选择与购买 |
| 6 | **BIZ-ORDER** | 订单管理 | 2 | 订单列表 / 订单详情 |
| 7 | **AUX-CACHE** | 道具缓存 | 1 | Redis 缓存 |
| 8 | **AUX-EXRATE** | 汇率管理 | 1 | 汇率表 |
| 9 | **LINK-PAYMENT** | 支付集成 | 1 | 支付接口集成 |
| 10 | **LOG-PAYMENT** | 支付日志 | 1 | 支付操作日志 |
| 11 | **SPECIAL-VIP-CHANGE** | VIP 变更（[fallback]）| 2 | 等级变更生效 / 等级时效处理 |
| **合计** | | | **26 Story** | |

> **注意**：原归档数据中 `BIZ-PURCHASE-005`（购买邮件通知）等包含 v1.0 旧 7 枚举（`SYS_MSG` / `RED_DOT` / `ENTITY_CACHE` / `ASSET_CHANGE` / `ANOMALY` / `DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` / `SWITCH_TO_BACKGROUND` 等），按 v1.6.1+ 已迁移：
> - `SYS_MSG` → `MODAL_DIALOG` 或 `TOAST`
> - `RED_DOT` → `RED_DOT_BADGE`
> - `ENTITY_CACHE` → 移交 `AUX C` (`CACHE_HIT_RATE`)
> - `ASSET_CHANGE` → 按场景分（业务侧=`BIZ_AUDIT_LOG` / 流水=`LOG_ASSET_AUDIT`）
> - `DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` → 按场景分（业务层=`BOUNDARY_EXTREME` / 流量层=`WEAK_NET_RATE_LIMIT`）
> - `SWITCH_TO_BACKGROUND` → `BG_FG_SWITCH`

---

## 3. TP 分布（8 模块 × 4 类型）

### 3.1 按模块分布

| 模块 | TP 数 | 占比 | 主要 Story |
|------|-------|------|-----------|
| **BIZ** | 19 | 25.3% | 购买流程 + 订单管理 |
| **CONFIG** | 19 | 25.3% | VIP 配置 + 折扣配置 |
| **UI** | 14 | 18.7% | 商城 UI + 详情 UI |
| **SPECIAL** | 9 | 12.0% | VIP 变更 [fallback] |
| **HINT** | 5 | 6.7% | 弹窗 / Toast / 飘字 / 红点 |
| **LOG** | 5 | 6.7% | 支付日志 + 资产审计 |
| **LINK** | 3 | 4.0% | 支付渠道 |
| **AUX** | 1 | 1.3% | 缓存 |
| **合计** | **75** | **100%** | |

### 3.2 按类型分布

| 类型 | TP 数 | 占比 |
|------|-------|------|
| **POSITIVE** | 35 | 46.7% |
| **BOUNDARY** | 19 | 25.3% |
| **NEGATIVE** | 12 | 16.0% |
| **EXCEPTION** | 9 | 12.0% |
| **合计** | **75** | **100%** |

---

## 4. 完整 TP 数据

完整 75 个 TP 详见：

- **JSON 格式**：[`test_points.json`](./test_points.json)（从 `_archive_pre_rerun/游戏道具商城系统/「S5 测试点生成」/v1.0/test_points.json` 引用）
- **Markdown 格式**：从 JSON 渲染（参考 `test_case_formatter.py` 的 `_save_xlsx` 或 `aidocx-s6-test-cases` 的 markdown 渲染）

> **重要**：本目录**不复制**完整 75 个 TP（避免双写漂移），通过引用 `_archive_pre_rerun/` 中的真实数据。

---

## 5. 拆解思路分析

### 5.1 关键学习点（**S5 LLM 必读**）

| # | 学习点 | 说明 |
|---|--------|------|
| 1 | **每 Story 平均 5-8 个 TP** | 不是每个 Story 都 1:1:1:1 凑数，而是按"业务自然划分" |
| 2 | **同 Story 跨多模块 → 每个模块单独生成 TP** | 如 `BIZ-PURCHASE-002` 跨 BIZ / HINT / LOG / UI 4 个模块，生成 8 个 TP |
| 3 | **EXCEPTION TP 必引用 S4 风险点** | 如 `R-01` / `R-02` / `R-03` 等（v1.0 旧命名） |
| 4 | **POSITIVE 必含正常流程** | 如"购买成功链路"、"扣款+到账"、"配置保存"等 |
| 5 | **BOUNDARY 必含临界值** | 0 / 1 / 99 / 100 / 正好 / 多 1 / 少 1 / 倒计时最后一秒 |
| 6 | **NEGATIVE 必含异常输入** | 非法字符 / SQL 注入 / XSS / 越权访问 / 绕过前端 |
| 7 | **EXCEPTION 必含系统异常** | 网络异常 / 服务宕机 / DB 连接失败 / 缓存击穿 |

### 5.2 误标案例（**S5 LLM 必看**）

| 误标 | 正确 | 原因 |
|------|------|------|
| "购买成功 Toast" 标 UI | 标 HINT（E.TOAST）| 临时弹出 = HINT |
| "背包红点" 标 UI | 标 HINT（A.RED_DOT_BADGE）| 触发弹性 = HINT |
| "购买成功道具飘字" 标 UI | 标 HINT（B.ITEM_FLOAT）| 一次性浮现 = HINT |
| "升级弹窗" 标 BIZ | HINT（K.STATE_CHANGE_DIALOG）+ BIZ（D.STATE_MACHINE）| 弹窗样式归 HINT，升级逻辑归 BIZ |
| "日志中支付异常" 标 BIZ | 标 LOG（A.LOG_CRASH_REPORT 或 J.LOG_SECURITY）| 日志业务规范归 LOG |

### 5.3 反例（**v1.0 旧产物，仅作"误判案例"参考**）

| ID | 误标 | 实际情况 | 处理 |
|----|------|----------|------|
| `BIZ-PURCHASE-001-TP-001` | module=UI, type=POSITIVE | UI 测样式（弹窗展示道具信息）| ✅ 正确 |
| `BIZ-PURCHASE-001-TP-002` | module=UI, type=POSITIVE | 应是 BIZ（余额对比是业务）| ⚠️ 误标（已合并到 TP-001）|
| `BIZ-PURCHASE-002-TP-002` | module=HINT, type=POSITIVE | "系统消息通知" 用了 `SYS_MSG`（v1.6.1 凭空出现）| ⚠️ 应迁移到 `MODAL_DIALOG` 或 `TOAST` |
| `BIZ-PURCHASE-004-TP-002` | module=HINT, type=POSITIVE | "背包红点" 应是 `RED_DOT_BADGE`（v1.7 升级）| ⚠️ 已升级 |

---

## 6. 与 S6 的衔接

| 指标 | v1.0 | v2.0（S6 1:N 拓宽后）|
|------|------|---------------------|
| **TP 数** | 75 | 75（不变）|
| **TC 数** | 75（错误 1:1）| **529**（1:6.87）|
| **方法覆盖** | 1（无）| **16 种 ISTQB 方法** |
| **xlsx Sheets** | 3 | 4 |

详见 `ai_workflow/TP_TO_TC_EXPANSION.md`（SSoT）+ `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §"TP→TC 拓宽"。

---

## 7. 使用方法

S5 LLM 在生成新需求 TP 时：

1. **第 1 步**：读本目录 README + analysis.md（**先理解拆解思路**）
2. **第 2 步**：读 `test_points.json` 完整 75 个 TP（**学习格式**）
3. **第 3 步**：对照 `MODULES.md` §3.5 交叉场景判定规则（**避免误标**）
4. **第 4 步**：按相同格式 + 思路，生成新需求 TP（**严禁照搬**）

---

## 8. 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引（引用 `_archive_pre_rerun/游戏道具商城系统/「S5 测试点生成」/v1.0/test_points.json`）|
