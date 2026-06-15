# C. 跨表依赖检查

> **子类代码**：`FIELD_CROSS_DEP`
> **归属模块**：`CONFIG`
> **来源**：用户细化定义 §3「跨表依赖检查」（核心补充，游戏配置高频坑点）
>
> **测什么**：表 A 引用表 B 的 ID 存在性、多表联动闭环、循环依赖拦截。
> **不测什么**：同表/全表一致性（归 B）、单字段合法性（归 A）、热更（归 D）。
> **与其他子类的差异**：C 关注"跨表 ID 关联"——B 关注"同表数值统一"，A 关注"字段本身"。

---

## 1. 典型场景

### 场景 1：外键引用
- 业务背景：任务表 `TaskConfig` 引用道具表 `ItemConfig` 的 `item_id`
- 涉及字段：任务表 `reward_item_id` = 道具表 `item_id`
- 触发动作：任务表录入 `reward_item_id = 9999`，道具表无 item_id=9999
- 验证点：导出工具检测到无效引用、提示错误

### 场景 2：反向依赖（删除基础配置后）
- 业务背景：删除道具表 item_id=100
- 涉及表：任务表、成就表、商城表
- 触发动作：删除道具 100
- 验证点：所有引用 item_id=100 的表都被检查，提示遗留引用

### 场景 3：多表联动闭环
- 业务背景：活动 → 礼包 → 道具 → 合成配方
- 涉及表：4 张表全链路
- 触发动作：活动奖励引用不存在的礼包
- 验证点：全链路闭环校验

### 场景 4：养成系统多表联动
- 业务背景：角色养成（等级/突破/升星）
- 涉及表：3 张成长表
- 触发动作：等级表升到 10 级、突破表突破到 5 阶、升星表升到 3 星
- 验证点：3 张成长表数值联动无冲突

### 场景 5：循环依赖
- 业务背景：表 A 引用表 B，表 B 引用表 A
- 触发动作：导入配置时双向引用
- 验证点：循环依赖检测、不进入死循环

### 场景 6：深层引用链
- 业务背景：5 层引用链
- 涉及表：A → B → C → D → E
- 触发动作：解析时按引用链加载
- 验证点：性能可接受、不死循环

---

## 2. 种子测试点（TP 模板）

### TP-001（FIELD_CROSS_DEP）：外键引用不存在
- **scenario**：场景 1
- **module**：`FIELD_CROSS_DEP`
- **precondition**：任务表 `reward_item_id` 引用道具表 `item_id`
- **test_data**：任务表录入 `reward_item_id = 9999`，道具表无该 ID
- **expected**：导出工具拒绝，提示"任务表 T_001 引用了不存在的道具 9999"
- **notes**：注意"软引用"vs"硬引用"

### TP-002（FIELD_CROSS_DEP）：外键引用存在
- **scenario**：场景 1
- **module**：`FIELD_CROSS_DEP`
- **precondition**：道具表有 item_id=100
- **test_data**：任务表 `reward_item_id = 100`
- **expected**：导出工具接受
- **notes**：注意"存在性"vs"可见性"（灰度配置可能不可见）

### TP-003（FIELD_CROSS_DEP）：反向依赖检查
- **scenario**：场景 2
- **module**：`FIELD_CROSS_DEP`
- **precondition**：删除道具 100
- **test_data**：任务表 `reward_item_id=100`、成就表 `reward_id=100`、商城表 `item_id=100`
- **expected**：导出工具检测到 3 处遗留引用，提示"删除前需清理"
- **notes**：注意"软删除"vs"硬删除"

### TP-004（FIELD_CROSS_DEP）：任务奖励道具链路
- **scenario**：场景 3
- **module**：`FIELD_CROSS_DEP`
- **precondition**：活动表 → 礼包表 → 道具表
- **test_data**：活动 A → 礼包 B → 道具 C
- **expected**：3 张表 ID 全部存在，链路闭环
- **notes**：注意"活动期间"vs"活动结束"

### TP-005（FIELD_CROSS_DEP）：合成配方链路
- **scenario**：场景 3
- **module**：`FIELD_CROSS_DEP`
- **precondition**：合成表 → 材料表
- **test_data**：合成 D 需要材料 E、F、G
- **expected**：E/F/G 都存在于材料表
- **notes**：注意"可合成"vs"材料不足"

### TP-006（FIELD_CROSS_DEP）：养成系统多表联动
- **scenario**：场景 4
- **module**：`FIELD_CROSS_DEP`
- **precondition**：等级表/突破表/升星表
- **test_data**：等级 10 + 突破 5 阶 + 升星 3 星 → 战斗力 X
- **expected**：3 表数值计算无冲突，战斗力按公式计算
- **notes**：注意"分段函数"vs"线性叠加"

### TP-007（FIELD_CROSS_DEP）：循环依赖拦截
- **scenario**：场景 5
- **module**：`FIELD_CROSS_DEP`
- **precondition**：表 A 引用表 B，表 B 引用表 A
- **test_data**：A.config_id = 1 引用 B.config_id，B.config_id = 2 引用 A.config_id
- **expected**：导出工具检测到循环依赖，提示"A 与 B 形成循环"
- **notes**：注意"自引用"vs"互引用"

### TP-008（FIELD_CROSS_DEP）：自引用检测
- **scenario**：场景 5
- **module**：`FIELD_CROSS_DEP`
- **precondition**：表 A 有 `parent_id` 字段
- **test_data**：A.config_id=1 的 parent_id = 1（指向自己）
- **expected**：导出工具检测到自引用，提示"parent_id 指向自身"
- **notes**：注意"父节点"vs"循环"

### TP-009（FIELD_CROSS_DEP）：深层引用链加载
- **scenario**：场景 6
- **module**：`FIELD_CROSS_DEP`
- **precondition**：A → B → C → D → E 5 层引用
- **test_data**：A.config_id=1 引用链深度 5
- **expected**：导出工具正确加载 5 层引用、无死循环、耗时 < 5s
- **notes**：注意"递归深度"vs"性能"

### TP-010（FIELD_CROSS_DEP）：多张表引用同一基础配置
- **scenario**：场景 2
- **module**：`FIELD_CROSS_DEP`
- **precondition**：5 张表都引用道具 100
- **test_data**：任务/成就/商城/邮件/签到 5 张表都引用 item_id=100
- **expected**：删除道具 100 时，5 张表都被检测到
- **notes**：注意"高被引"配置的检查

### TP-011（FIELD_CROSS_DEP）：条件引用
- **scenario**：场景 4
- **module**：`FIELD_CROSS_DEP`
- **precondition**：任务表有 `if_level>10` 引用
- **test_data**：条件 `if_level>10` 引用的道具 ID=100 存在
- **expected**：导出工具检查条件引用也存在
- **notes**：注意"静态引用"vs"动态引用"

### TP-012（FIELD_CROSS_DEP）：跨模块配置引用
- **scenario**：场景 3
- **module**：`FIELD_CROSS_DEP`
- **precondition**：UI 配置表引用 BIZ 协议 ID
- **test_data**：UI 表引用了 BIZ 协议 protocol_id=999
- **expected**：导出工具检查跨模块引用（按设计决定是否检查）
- **notes**：注意"模块内"vs"跨模块"

---

## 3. 边界陷阱

### 边界 1：vs A. 字段合法性
- **混淆点**：「道具 ID 字段"」——A 测格式、C 测关联
- **判定规则**：测"道具 ID 字段本身合法" → A；测"任务表引用的道具 ID 存在" → C
- **实例**：道具 ID -1 → A-007；任务表引用不存在的道具 ID → C-001

### 边界 2：vs B. 同表一致性
- **混淆点**：「表与表数值"一致"」——B 测同表/全表、C 测跨表
- **判定规则**：测"单表内多字段值统一" → B；测"表 A 引用表 B ID" → C
- **实例**：道具表 5 处基础倍率一致 → B-005；任务表引用道具表 ID → C-001

### 边界 3：vs E. 解析与加载
- **混淆点**：「解析"加载"」——E 测性能、C 测关联
- **判定规则**：测"解析性能/嵌套结构" → E；测"跨表 ID 引用" → C
- **实例**：万行配置加载耗时 → E-005；任务表引用道具表 → C-001

### 边界 4：vs BIZ
- **混淆点**：「任务奖励"逻辑"」——C 测配置关联、BIZ 测业务逻辑
- **判定规则**：测"任务表 reward_item_id 引用存在" → C；测"完成任务发放奖励逻辑" → BIZ
- **实例**：任务表引用道具 → C-001；完成任务后扣道具 + 发奖励 → BIZ

---

## 4. 验证证据

### 视觉证据
- 导出工具跨表错误高亮截图
- 引用关系图（Graphviz）

### 日志证据
- 跨表引用检查报告
- 循环依赖检测日志

### 数据证据
- 跨表 ID 引用统计
- 引用链深度统计

### 性能证据
- 跨表校验耗时 < 10s
- 引用链解析耗时 < 5s
