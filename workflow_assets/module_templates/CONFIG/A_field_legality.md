# A. 字段合法性校验

> **子类代码**：`FIELD_LEGALITY`
> **归属模块**：`CONFIG`
> **来源**：用户细化定义 §1「配置表基础结构校验」（原"配置字段校验"拓展）
>
> **测什么**：单个配置表中每个字段的类型、取值、格式、约束、行列规范。
> **不测什么**：表与表之间的一致性（归 B）、跨表 ID 引用（归 C）、热更（归 D）。
> **与其他子类的差异**：A 关注"字段本身"，B 关注"同表/全局一致"，C 关注"跨表关联"。

---

## 1. 典型场景

### 场景 1：字段类型校验
- 业务背景：道具表 `ItemConfig.xlsx`
- 涉及字段：`item_id`（int）、`name`（string）、`drop_rate`（float）
- 触发动作：策划录入 `item_id = "abc"`（应为 int）
- 验证点：导出工具报错、解析失败、上线不生效

### 场景 2：字段取值范围
- 业务背景：概率表 `ProbabilityConfig.xlsx`
- 涉及字段：`drop_rate`（0-1）、`level`（1-100）
- 触发动作：录入 `drop_rate = 1.5`
- 验证点：导出工具拒绝、提示超范围

### 场景 3：枚举值约束
- 业务背景：道具表
- 涉及字段：`item_type`（枚举：1=消耗品/2=装备/3=材料）
- 触发动作：录入 `item_type = 4`
- 验证点：枚举值不存在、导出拒绝

### 场景 4：多语言字段
- 业务背景：道具表
- 涉及字段：`name_cn` / `name_en` / `name_jp`
- 触发动作：录入 `name_en = ""`（空字符串）
- 验证点：必填字段空值检查

### 场景 5：资源路径字段
- 业务背景：道具表
- 涉及字段：`icon_path` / `sfx_path` / `model_path`
- 触发动作：录入 `icon_path = "icons/ITEM_001.png"`（小写）
- 验证点：资源存在性、大小写、后缀规范

### 场景 6：ID 关联字段
- 业务背景：任务表
- 涉及字段：`reward_item_id`（道具 ID）
- 触发动作：录入 `reward_item_id = -1`
- 验证点：非法负数检查

### 场景 7：时间配置
- 业务背景：活动表
- 涉及字段：`start_time` / `end_time`
- 触发动作：录入 `end_time < start_time`
- 验证点：时间倒置检查

### 场景 8：行/列规范
- 业务背景：任何表
- 触发动作：删掉某列
- 验证点：导出工具报错、程序解析失败

### 场景 9：重复行
- 业务背景：道具表
- 触发动作：录入两个相同 `item_id` 的行
- 验证点：主键唯一检查

---

## 2. 种子测试点（TP 模板）

### TP-001（FIELD_LEGALITY）：int 字段非数字拒绝
- **scenario**：场景 1
- **module**：`FIELD_LEGALITY`
- **precondition**：道具表 `item_id` 字段定义为 int
- **test_data**：录入 `item_id = "abc"`
- **expected**：导出工具报错（高亮错误行），程序解析失败，未生效
- **notes**：注意空字符串、null、特殊字符

### TP-002（FIELD_LEGALITY）：float 字段精度
- **scenario**：场景 1
- **module**：`FIELD_LEGALITY`
- **precondition**：`drop_rate` 字段定义为 float
- **test_data**：录入 `0.1 + 0.2 = 0.30000000000000004`
- **expected**：浮点精度处理（按设计），不出现极端小数
- **notes**：注意金融、游戏内货币精度

### TP-003（FIELD_LEGALITY）：array 字段结构
- **scenario**：场景 1
- **module**：`FIELD_LEGALITY`
- **precondition**：`reward_items` 字段定义为数组
- **test_data**：录入 `[{item_id: 1, count: 10}, {item_id: 2, count: 20}]`
- **expected**：数组正确解析，元素类型匹配
- **notes**：嵌套结构

### TP-004（FIELD_LEGALITY）：数值范围上限
- **scenario**：场景 2
- **module**：`FIELD_LEGALITY`
- **precondition**：`level` 字段定义为 1-100
- **test_data**：录入 `level = 101`
- **expected**：导出工具拒绝，提示"超出上限 100"
- **notes**：注意闭区间 [1, 100] vs 半开区间 [1, 100)

### TP-005（FIELD_LEGALITY）：数值范围下限
- **scenario**：场景 2
- **module**：`FIELD_LEGALITY`
- **precondition**：`level` 字段定义为 1-100
- **test_data**：录入 `level = 0`
- **expected**：导出工具拒绝，提示"低于下限 1"
- **notes**：注意 0 是否合法（某些场景 0 表示"未激活"）

### TP-006（FIELD_LEGALITY）：百分比范围
- **scenario**：场景 2
- **module**：`FIELD_LEGALITY`
- **precondition**：`drop_rate` 字段定义为 0-100
- **test_data**：录入 `150`
- **expected**：导出工具拒绝
- **notes**：注意 0-1 vs 0-100 的设计选择

### TP-007（FIELD_LEGALITY）：ID 字段非负
- **scenario**：场景 6
- **module**：`FIELD_LEGALITY`
- **precondition**：`item_id` 字段定义为 int，非负
- **test_data**：录入 `-1`
- **expected**：导出工具拒绝
- **notes**：注意 0 是否合法

### TP-008（FIELD_LEGALITY）：枚举值合法
- **scenario**：场景 3
- **module**：`FIELD_LEGALITY`
- **precondition**：`item_type` 枚举定义 1/2/3
- **test_data**：录入 `4`
- **expected**：导出工具拒绝，提示"枚举值 4 不存在"
- **notes**：注意中英文枚举（1=消耗品 vs 1=CONSUMABLE）

### TP-009（FIELD_LEGALITY）：枚举空值
- **scenario**：场景 3
- **module**：`FIELD_LEGALITY`
- **precondition**：`item_type` 字段必填
- **test_data**：留空
- **expected**：导出工具拒绝
- **notes**：注意选填字段的空值兜底

### TP-010（FIELD_LEGALITY）：必填字段空值
- **scenario**：场景 4
- **module**：`FIELD_LEGALITY`
- **precondition**：`item_name` 字段必填
- **test_data**：录入 `""` 或 `null`
- **expected**：导出工具拒绝
- **notes**：注意"空字符串"vs"空格"vs"null"的区分

### TP-011（FIELD_LEGALITY）：选填字段空值
- **scenario**：场景 4
- **module**：`FIELD_LEGALITY`
- **precondition**：`description` 字段选填
- **test_data**：留空
- **expected**：导出工具接受，运行时按空值兜底逻辑
- **notes**：注意空值时程序表现（如显示为空字符串）

### TP-012（FIELD_LEGALITY）：多语言 key 缺失
- **scenario**：场景 4
- **module**：`FIELD_LEGALITY`
- **precondition**：多语言字段
- **test_data**：缺 `name_jp`
- **expected**：导出工具拒绝，提示"缺失翻译"
- **notes**：注意必有语言 vs 选有语言

### TP-013（FIELD_LEGALITY）：多语言非法字符
- **scenario**：场景 4
- **module**：`FIELD_LEGALITY`
- **precondition**：多语言字段
- **test_data**：录入含 `\\x00`（NULL 字符）的字符串
- **expected**：导出工具拒绝或自动过滤
- **notes**：注意控制字符、emoji

### TP-014（FIELD_LEGALITY）：资源路径不存在
- **scenario**：场景 5
- **module**：`FIELD_LEGALITY`
- **precondition**：`icon_path` 字段
- **test_data**：录入 `icons/NONEXIST.png`
- **expected**：导出工具检查资源存在性，不存在则拒绝
- **notes**：注意"提示错误"vs"自动跳过"

### TP-015（FIELD_LEGALITY）：资源路径后缀
- **scenario**：场景 5
- **module**：`FIELD_LEGALITY`
- **precondition**：`icon_path` 字段定义为 .png
- **test_data**：录入 `icons/ITEM_001.jpg`
- **expected**：导出工具拒绝，提示"后缀不符"
- **notes**：注意大小写（.PNG vs .png）

### TP-016（FIELD_LEGALITY）：时间格式合法
- **scenario**：场景 7
- **module**：`FIELD_LEGALITY`
- **precondition**：`start_time` 字段定义为时间戳
- **test_data**：录入 `2026-13-01 25:00:00`（非法）
- **expected**：导出工具拒绝
- **notes**：注意时间格式（时间戳 vs 字符串）

### TP-017（FIELD_LEGALITY）：时间倒置
- **scenario**：场景 7
- **module**：`FIELD_LEGALITY`
- **precondition**：`start_time` < `end_time` 约束
- **test_data**：`end_time = 2026-01-01` < `start_time = 2026-12-31`
- **expected**：导出工具拒绝，提示"结束时间早于开始时间"
- **notes**：注意零时长（start == end）是否合法

### TP-018（FIELD_LEGALITY）：CD 时长合法
- **scenario**：场景 7
- **module**：`FIELD_LEGALITY`
- **precondition**：`cd_duration` 字段定义为秒，0-3600
- **test_data**：录入 `-1` 或 `99999`
- **expected**：导出工具拒绝
- **notes**：注意 0 CD（无 CD）是否合法

### TP-019（FIELD_LEGALITY）：缺列校验
- **scenario**：场景 8
- **module**：`FIELD_LEGALITY`
- **precondition**：道具表必含 `item_id` 列
- **test_data**：删掉 `item_id` 列
- **expected**：导出工具拒绝，提示"缺失列 item_id"
- **notes**：注意"必含列"vs"选含列"

### TP-020（FIELD_LEGALITY）：多余列校验
- **scenario**：场景 8
- **module**：`FIELD_LEGALITY`
- **precondition**：道具表只定义 N 列
- **test_data**：多加一列 `temp_col`
- **expected**：导出工具按设计决定（警告/拒绝/忽略）
- **notes**：注意策划临时列的影响

### TP-021（FIELD_LEGALITY）：主键重复
- **scenario**：场景 9
- **module**：`FIELD_LEGALITY`
- **precondition**：`item_id` 是主键
- **test_data**：两行 `item_id = 1`
- **expected**：导出工具拒绝，提示"主键重复"
- **notes**：注意复合主键

### TP-022（FIELD_LEGALITY）：注释列不影响解析
- **scenario**：场景 8
- **module**：`FIELD_LEGALITY`
- **precondition**：表格含 `# comment` 注释列
- **test_data**：注释列含中英文说明
- **expected**：程序正确忽略注释列，不影响解析
- **notes**：注意注释列命名规范

---

## 3. 边界陷阱

### 边界 1：vs B. 同表一致性
- **混淆点**：「同表内多个道具的属性一致性」——A 测单字段、B 测多字段
- **判定规则**：测"单个字段的合法性" → A；测"同表内多个字段间数值一致" → B
- **实例**：道具 A 攻击力字段为负 → A-007；道具 A 攻击力 vs 道具 B 攻击力梯度 → B-001

### 边界 2：vs C. 跨表依赖
- **混淆点**：「道具 ID 字段合法性」——A 测格式、C 测关联
- **判定规则**：测"道具 ID 字段本身合法（非负、不重复）" → A；测"任务表 reward_item_id 引用的道具 ID 存在" → C
- **实例**：道具 ID -1 → A-007；任务表引用了不存在的道具 ID → C-001

### 边界 3：vs E. 解析与加载
- **混淆点**：「字段类型不匹配"」——A 测配置层、E 测解析层
- **判定规则**：测"导出工具拒绝非法字段" → A；测"运行时解析性能/嵌套结构" → E
- **实例**：字段类型 int 录入 string → A-001；万行配置加载耗时 → E-005

### 边界 4：vs G. 数值逻辑
- **混淆点**：「概率字段 0-100」——A 测范围、G 测总和
- **判定规则**：测"单个概率字段范围 0-100" → A；测"所有概率字段总和 ≤ 100%" → G
- **实例**：单个 drop_rate = 150 → A-006；所有 drop_rate 总和 = 120% → G-001

---

## 4. 验证证据

### 视觉证据
- 导出工具报错截图（红框标注错误行/列）
- 错误日志截图

### 日志证据
- 导出工具错误码（如 `ERROR_FIELD_TYPE_MISMATCH`）
- 解析失败堆栈

### 数据证据
- 配置文件 diff（错误 vs 正确）
- 策划 Excel 错误行高亮

### 性能证据
- 导出工具处理时间 < 10s（10万行）
