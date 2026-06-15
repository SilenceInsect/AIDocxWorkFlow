# H. 配置导出 / 导入 / 发布流程

> **子类代码**：`EXPORT_PUBLISH`
> **归属模块**：`CONFIG`
> **来源**：用户细化定义 §5(4)「导出/导入/发布流程校验」
>
> **测什么**：Excel/CSV → JSON/BIN 导出、发布流程、配置日志。
> **不测什么**：单字段合法性（归 A）、解析（归 E）、热更（归 D）。
> **与其他子类的差异**：H 关注"导出/发布层"——A 关注"配置层"，E 关注"运行时解析"。

---

## 1. 典型场景

### 场景 1：Excel 导出 JSON
- 业务背景：策划 Excel → 程序 JSON
- 涉及文件：ItemConfig.xlsx → item_config.json
- 触发动作：导出工具运行
- 验证点：JSON 正确、字段无丢失

### 场景 2：CSV 导出 BIN
- 业务背景：性能要求高的配置（如道具表）
- 涉及文件：item.csv → item.bin（二进制）
- 触发动作：导出工具运行
- **expected**：BIN 解析结果与源数据一致

### 场景 3：导出工具报错高亮
- 业务背景：策划录入错误
- 涉及字段：某行某列错误
- 触发动作：导出工具运行
- 验证点：错误行高亮、错误信息明确

### 场景 4：批量修复
- 业务背景：策划修复错误
- 触发动作：批量修复工具
- 验证点：自动修复 + 确认

### 场景 5：发布流程
- 业务背景：策划 → 审核 → 打包 → 上传
- 涉及角色：策划/QA/发布
- 触发动作：完整发布流程
- 验证点：无遗漏配置表

### 场景 6：配置变更日志
- 业务背景：配置变更追溯
- 涉及字段：变更人/变更内容/变更时间
- 触发动作：每版配置发布
- 验证点：日志可追溯

### 场景 7：导出乱码
- 业务背景：含中文/特殊字符
- 触发动作：导出工具运行
- 验证点：无乱码、字符编码正确

---

## 2. 种子测试点（TP 模板）

### TP-001（EXPORT_PUBLISH）：Excel 导出 JSON
- **scenario**：场景 1
- **module**：`EXPORT_PUBLISH`
- **precondition**：ItemConfig.xlsx 含 100 行道具
- **test_data**：导出工具运行
- **expected**：item_config.json 含 100 行、所有字段正确
- **notes**：注意"空行"vs"数据行"

### TP-002（EXPORT_PUBLISH）：CSV 导出 BIN
- **scenario**：场景 2
- **module**：`EXPORT_PUBLISH`
- **precondition**：item.csv 100 行
- **test_data**：导出工具运行
- **expected**：item.bin 解析结果与 CSV 一致
- **notes**：注意"BIN 格式"vs"JSON 格式"性能

### TP-003（EXPORT_PUBLISH）：导出无数据丢失
- **scenario**：场景 1
- **module**：`EXPORT_PUBLISH`
- **precondition**：源数据 N 行 N 列
- **test_data**：导出后
- **expected**：导出数据 N 行 N 列、所有字段一致
- **notes**：注意"空值"vs"null"

### TP-004（EXPORT_PUBLISH）：导出工具报错高亮
- **scenario**：场景 3
- **module**：`EXPORT_PUBLISH`
- **precondition**：Excel 中某行某列错误
- **test_data**：导出工具运行
- **expected**：错误行高亮、错误信息明确（如"item_id 列第 5 行类型错误"）
- **notes**：注意"高亮颜色"vs"日志"

### TP-005（EXPORT_PUBLISH）：批量修复工具
- **scenario**：场景 4
- **module**：`EXPORT_PUBLISH`
- **precondition**：10 行错误
- **test_data**：批量修复工具运行
- **expected**：自动修复、需确认、不修改非错误行
- **notes**：注意"自动修复"vs"提示修复"

### TP-006（EXPORT_PUBLISH）：发布流程完整
- **scenario**：场景 5
- **module**：`EXPORT_PUBLISH`
- **precondition**：策划提交 5 张表
- **test_data**：完整发布流程
- **expected**：5 张表都通过审核、打包、上传
- **notes**：注意"漏表"vs"全表"

### TP-007（EXPORT_PUBLISH）：发布审核
- **scenario**：场景 5
- **module**：`EXPORT_PUBLISH`
- **precondition**：QA 审核
- **test_data**：QA 检查配置
- **expected**：审核未通过的不允许发布
- **notes**：注意"强制审核"vs"跳过审核"

### TP-008（EXPORT_PUBLISH）：配置变更日志
- **scenario**：场景 6
- **module**：`EXPORT_PUBLISH`
- **precondition**：每版配置变更
- **test_data**：发布 v1.2.0
- **expected**：日志含变更人/内容/时间，可追溯
- **notes**：注意"审计"vs"匿名"

### TP-009（EXPORT_PUBLISH）：导出乱码
- **scenario**：场景 7
- **module**：`EXPORT_PUBLISH`
- **precondition**：含中文/emoji/特殊字符
- **test_data**：导出工具运行
- **expected**：无乱码、字符编码正确（UTF-8）
- **notes**：注意"GBK"vs"UTF-8"

### TP-010（EXPORT_PUBLISH）：导出导出速度
- **scenario**：场景 1
- **module**：`EXPORT_PUBLISH`
- **precondition**：10000 行配置
- **test_data**：导出工具运行
- **expected**：耗时 < 10s
- **notes**：注意"全量导出"vs"增量导出"

---

## 3. 边界陷阱

### 边界 1：vs A. 字段合法性
- **混淆点**：「字段"错误"」——A 测字段、H 测导出
- **判定规则**：测"导出工具拒绝非法字段" → A；测"导出流程报错高亮" → H
- **实例**：字段类型错误 → A-001；导出工具高亮错误行 → H-004

### 边界 2：vs E. 解析与加载
- **混淆点**：「导出"解析"」——E 测运行时解析、H 测导出
- **判定规则**：测"运行时解析性能" → E；测"导出文件格式" → H
- **实例**：万行配置加载耗时 → E-003；Excel 转 JSON 导出 → H-001

### 边界 3：vs D. 热更新
- **混淆点**：「热更"包"」——D 测运行时热更、H 测发布流程
- **判定规则**：测"运行时热更生效" → D；测"热更包发布流程" → H
- **实例**：热更生效 → D-001；热更包审核发布 → H-007

### 边界 4：vs LOG
- **混淆点**：「配置"日志"」——H 测配置变更日志、LOG 测埋点
- **判定规则**：测"配置变更审计日志" → H；测"运行时配置加载日志" → LOG
- **实例**：配置变更追溯 → H-008；运行时配置加载埋点 → LOG

---

## 4. 验证证据

### 视觉证据
- 导出工具报错高亮截图
- 发布流程截图

### 日志证据
- 导出工具运行日志
- 审核流程日志
- 配置变更审计日志

### 数据证据
- 源文件 vs 导出文件 diff
- 配置版本号
- 变更人/时间记录

### 性能证据
- 导出耗时 < 10s
- 审核耗时 < 1h
