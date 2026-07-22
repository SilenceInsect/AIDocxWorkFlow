# K. CONFIG 游戏项目额外专属（仅游戏项目）

> **非测试类型**——本文件是**仅游戏项目**的 CONFIG 测试点补充。
> 非游戏项目（PC 后台、移动端 App、Web 工具）**忽略**本文件。
>
> **来源**：用户细化定义 §5「游戏项目额外补充测试点」

---

## 1. 本地化配置

### 场景
- 业务背景：游戏出海
- 涉及字段：多区服、多语言、多渠道
- 验证点：配置隔离、互不覆盖

### 种子 TP

#### TP-001（K-本地化）：多区服配置隔离
- **module**：`FIELD_LEGALITY`（CONFIG 子类）
- **precondition**：中国服配置 + 美服配置
- **test_data**：中国服 `cn_drop_rate` vs 美服 `us_drop_rate`
- **expected**：两服配置独立、互不影响
- **notes**：注意"区服"vs"大区"

#### TP-002（K-本地化）：多语言翻译表
- **module**：`FIELD_LEGALITY`
- **precondition**：i18n 翻译表
- **test_data**：中文 vs 英文 vs 日文
- **expected**：3 语言正确显示
- **notes**：注意"必有语言"vs"选有语言"

#### TP-003（K-本地化）：多渠道差异化
- **module**：`FIELD_LEGALITY`
- **precondition**：iOS 渠道 vs Android 渠道 vs Web 渠道
- **test_data**：3 渠道专属配置
- **expected**：3 渠道配置独立
- **notes**：注意"商店"vs"渠道"

#### TP-004（K-本地化）：多区服配置不互相覆盖
- **module**：`FIELD_INTRA_DEP`
- **precondition**：中国服 + 美服
- **test_data**：中国服修改 `cn_pay_rate`，美服同步
- **expected**：美服不受影响
- **notes**：注意"全服"vs"分服"配置

---

## 2. 活动配置边界

### 场景
- 业务背景：限时活动
- 涉及字段：起止时间、奖励
- 验证点：过期失效、重复开启重置

### 种子 TP

#### TP-005（K-活动）：活动过期配置自动失效
- **module**：`FIELD_LEGALITY`
- **precondition**：活动 A 已结束
- **test_data**：玩家尝试访问活动 A
- **expected**：活动不可见、提示"活动已结束"
- **notes**：注意"硬过期"vs"软过期"

#### TP-006（K-活动）：活动重复开启配置重置
- **module**：`FIELD_LEGALITY`
- **precondition**：活动 A 重复开启（如节日活动）
- **test_data**：第二次开启
- **expected**：玩家进度重置、奖励可重新获得
- **notes**：注意"个人重置"vs"全服重置"

#### TP-007（K-活动）：活动配置清理
- **module**：`FIELD_LEGALITY`
- **precondition**：活动结束 7 天后
- **test_data**：配置清理
- **expected**：活动配置从表删除、不影响其他活动
- **notes**：注意"软清理"vs"硬清理"

#### TP-008（K-活动）：活动配置备份
- **module**：`EXPORT_PUBLISH`
- **precondition**：活动配置每次发布
- **test_data**：发布活动配置
- **expected**：可回滚、版本号递增
- **notes**：注意"备份"vs"覆盖"

---

## 3. 礼包 / 商城配置

### 场景
- 业务背景：商城礼包
- 涉及字段：限购次数、折扣倍率、礼包内容
- 验证点：限购生效、无超发漏洞

### 种子 TP

#### TP-009（K-礼包）：限购次数生效
- **module**：`FIELD_LEGALITY`
- **precondition**：礼包限购 1 次
- **test_data**：玩家购买 1 次后再买
- **expected**：第二次购买被拒绝
- **notes**：注意"永久限购"vs"每日限购"

#### TP-010（K-礼包）：每日限购重置
- **module**：`FIELD_LEGALITY`
- **precondition**：每日限购 1 次
- **test_data**：今日买 1 次，次日再买
- **expected**：次日可重新购买
- **notes**：注意"自然日"vs"24 小时"

#### TP-011（K-礼包）：折扣倍率生效
- **module**：`FIELD_LEGALITY`
- **precondition**：礼包原价 100，折扣 0.5
- **test_data**：玩家购买
- **expected**：支付 50
- **notes**：注意"百分比"vs"固定折扣"

#### TP-012（K-礼包）：礼包内容无超发
- **module**：`VALUE_LOGIC`
- **precondition**：礼包内容配置
- **test_data**：玩家多次购买限购礼包
- **expected**：实际发放 = 配置 × 购买次数
- **notes**：注意"循环漏洞"

#### TP-013（K-礼包）：礼包奖励总和校验
- **module**：`VALUE_LOGIC`
- **precondition**：礼包奖励 = 道具 A × 10 + 道具 B × 5
- **test_data**：礼包被购买
- **expected**：玩家实际获得 10 A + 5 B
- **notes**：注意"配置"vs"实际"

---

## 4. 资源配置

### 场景
- 业务背景：特效、音效、贴图
- 涉及字段：资源路径
- 验证点：引用校验、热更后资源不丢失

### 种子 TP

#### TP-014（K-资源）：资源路径存在性
- **module**：`FIELD_LEGALITY`
- **precondition**：特效/音效/贴图路径
- **test_data**：路径存在性检查
- **expected**：所有资源存在、无裂资源
- **notes**：注意"相对路径"vs"绝对路径"

#### TP-015（K-资源）：热更后资源不丢失
- **module**：`RELOAD_4_MODE`
- **precondition**：热更前资源已加载
- **test_data**：热更后引用新资源
- **expected**：新资源加载、无 404
- **notes**：注意"资源包"vs"配置包"

#### TP-016（K-资源）：资源大小写
- **module**：`FIELD_LEGALITY`
- **precondition**：资源路径字段
- **test_data**：`icon.png` vs `ICON.PNG`（Linux 大小写敏感）
- **expected**：按设计决定（统一小写）
- **notes**：注意"Windows"vs"Linux"

#### TP-017（K-资源）：资源后缀规范
- **module**：`FIELD_LEGALITY`
- **precondition**：资源路径字段
- **test_data**：音效 `.mp3` vs `.wav` vs `.ogg`
- **expected**：按设计统一
- **notes**：注意"格式"vs"压缩率"

---

## 5. 防沉迷 / 风控配置

### 场景
- 业务背景：未成年保护、风控
- 涉及字段：时长限制、充值档位、限购
- 验证点：配置生效、不绕过

### 种子 TP

#### TP-018（K-风控）：防沉迷时长限制
- **module**：`SERVER_CONFIG`
- **precondition**：`anti_addiction_minutes_per_day` = 90
- **test_data**：玩家玩 90 分钟
- **expected**：踢出游戏、提示
- **notes**：注意"未成年人"vs"成年人"

#### TP-019（K-风控）：未成年充值档位限制
- **module**：`FIELD_LEGALITY`
- **precondition**：未成年充值限制（如单笔 ≤ 50 元）
- **test_data**：未成年玩家充值 100 元
- **expected**：充值被拒绝、提示
- **notes**：注意"实名认证"vs"未实名"

#### TP-020（K-风控）：礼包限购风控
- **module**：`FIELD_LEGALITY`
- **precondition**：礼包限购 1 次
- **test_data**：玩家尝试绕过（如换号）
- **expected**：被风控识别、拒绝
- **notes**：注意"换号"vs"同人"

#### TP-021（K-风控）：充值档位生效
- **module**：`FIELD_LEGALITY`
- **precondition**：充值档位 6/30/98/198/328/648
- **test_data**：玩家充值 648
- **expected**：到账 6480 钻石（按汇率）
- **notes**：注意"首充"vs"续充"

#### TP-022（K-风控）：风控阈值生效
- **module**：`SERVER_CONFIG`
- **precondition**：`risk_threshold` 字段
- **test_data**：玩家异常行为（如 1 小时充值 10000 元）
- **expected**：触发风控、冻结账户
- **notes**：注意"自动风控"vs"人工审核"

---

## 6. 边界陷阱

### 边界 1：vs K. UI 游戏专项
- **混淆点**：「游戏"配置"」——CONFIG-K 测配置、UI-K 测 UI
- **判定规则**：测"配置字段本身" → CONFIG-K；测"配置加载后 UI 展示" → UI-K
- **实例**：礼包限购 1 次字段 → K-009；礼包按钮置灰 → UI-K

### 边界 2：vs G. 数值逻辑
- **混淆点**：「礼包"配置"」——G 测通用数值逻辑、K 测游戏专项
- **判定规则**：测"通用概率/公式/上限" → G；测"游戏礼包/活动/防沉迷" → K
- **实例**：抽卡保底 90 次 → G-003；礼包限购 1 次 → K-009

### 边界 3：vs BIZ
- **混淆点**：「礼包"购买"」——K 测配置、BIZ 测购买逻辑
- **判定规则**：测"礼包内容/限购配置" → K；测"购买流程/扣款/发货" → BIZ
- **实例**：礼包限购 1 次字段 → K-009；购买时扣款 → BIZ

### 边界 4：vs SPECIAL
- **混淆点**：「防沉迷"配置"」——K 测配置、SPECIAL 测异常处理
- **判定规则**：测"防沉迷阈值字段" → K；测"防沉迷触发/踢出" → SPECIAL
- **实例**：防沉迷 90 分钟字段 → K-018；防沉迷踢出逻辑 → SPECIAL

---

## 7. 验证证据

### 视觉证据
- 多区服 UI 对比截图
- 多语言对比截图
- 礼包限购提示截图
- 防沉迷提示截图

### 日志证据
- 本地化配置加载日志
- 活动开启/关闭日志
- 礼包购买日志
- 风控触发日志

### 数据证据
- DB 中区服/语言/渠道配置表
- 活动配置版本表
- 风控事件记录表

### 性能证据
- 本地化配置加载 < 100ms
- 风控检测 < 50ms
