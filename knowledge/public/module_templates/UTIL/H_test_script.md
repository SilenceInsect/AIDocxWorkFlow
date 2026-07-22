# H. 测试脚本

> **子类代码**：`TEST_SCRIPT`
> **归属模块**：`AUX`
> **来源**：用户细化定义 §8「测试脚本」
>
> **测什么**：自动化测试、压测、批量造数、回归脚本、日志解析、性能采样。
> **不测什么**：业务测试用例（归 S5/S6）、生产代码（归其他模块）。
> **与其他子类的差异**：H 关注"测试工具/脚本"——I 关注"验收清单"，H 是工具，I 是清单。

---

## 1. 典型场景

### 场景 1：接口压测
- 业务背景：性能测试
- 涉及工具：压测脚本
- 触发动作：1000 并发请求
- 验证点：TPS / 响应时间

### 场景 2：UI 自动化
- 业务背景：回归测试
- 涉及工具：UI 自动化脚本
- 触发动作：模拟点击
- 验证点：操作成功

### 场景 3：配置批量校验
- 业务背景：配置验证
- 涉及工具：配置校验脚本
- 触发动作：扫描所有配置
- 验证点：错误配置高亮

### 场景 4：一键复现脚本
- 业务背景：bug 复现
- 触发动作：执行复现脚本
- 验证点：bug 重现

### 场景 5：批量造号
- 业务背景：测试环境
- 涉及工具：批量造号脚本
- 触发动作：生成 1000 测试账号
- 验证点：账号可用

### 场景 6：批量刷数据
- 业务背景：压测准备
- 触发动作：批量刷 100 万道具
- 验证点：数据写入

### 场景 7：回归用例脚本
- 业务背景：版本回归
- 触发动作：跑 500 回归用例
- 验证点：全通过/失败列表

### 场景 8：日志解析
- 业务背景：日志分析
- 涉及工具：日志解析脚本
- 触发动作：解析 10GB 日志
- 验证点：错误日志提取

### 场景 9：异常抓取
- 业务背景：bug 追踪
- 涉及工具：异常抓取
- 触发动作：游戏崩溃
- 验证点：堆栈捕获

### 场景 10：性能采样
- 业务背景：性能分析
- 涉及工具：性能采样脚本
- 触发动作：战斗中 5 分钟采样
- 验证点：FPS/CPU/内存

### 场景 11：批量导出校验
- 业务背景：数据导出
- 涉及工具：导出脚本
- 触发动作：导出 100 万订单
- 验证点：导出文件正确

---

## 2. 种子测试点（TP 模板）

### TP-001（TEST_SCRIPT）：接口压测 - TPS
- **scenario**：场景 1
- **module**：`TEST_SCRIPT`
- **precondition**：测试服就绪
- **test_data**：1000 并发请求
- **expected**：TPS ≥ 500、平均响应 < 200ms
- **notes**：注意"P95"vs"P99"延迟

### TP-002（TEST_SCRIPT）：接口压测 - 错误率
- **scenario**：场景 1
- **module**：`TEST_SCRIPT`
- **precondition**：1000 并发
- **test_data**：观察错误率
- **expected**：错误率 < 0.1%
- **notes**：注意"超时"vs"业务错误"

### TP-003（TEST_SCRIPT）：UI 自动化 - 点击
- **scenario**：场景 2
- **module**：`TEST_SCRIPT`
- **precondition**：UI 元素就位
- **test_data**：模拟点击购买按钮
- **expected**：点击成功、购买流程触发
- **notes**：注意"坐标"vs"元素 ID"

### TP-004（TEST_SCRIPT）：配置批量校验
- **scenario**：场景 3
- **module**：`TEST_SCRIPT`
- **precondition**：配置目录有 100 张表
- **test_data**：扫描所有配置
- **expected**：错误配置高亮 + 错误报告
- **notes**：注意"高亮"vs"仅日志"

### TP-005（TEST_SCRIPT）：一键复现
- **scenario**：场景 4
- **module**：`TEST_SCRIPT`
- **precondition**：bug 已记录
- **test_data**：执行复现脚本
- **expected**：bug 重现
- **notes**：注意"确定性"复现

### TP-006（TEST_SCRIPT）：批量造号
- **scenario**：场景 5
- **module**：`TEST_SCRIPT`
- **precondition**：测试服
- **test_data**：生成 1000 账号
- **expected**：1000 账号可用
- **notes**：注意"账号隔离"

### TP-007（TEST_SCRIPT）：批量刷数据
- **scenario**：场景 6
- **module**：`TEST_SCRIPT`
- **precondition**：测试服
- **test_data**：批量发 100 万道具
- **expected**：DB 写入成功、查询正确
- **notes**：注意"性能"vs"正确"

### TP-008（TEST_SCRIPT）：回归用例
- **scenario**：场景 7
- **module**：`TEST_SCRIPT`
- **precondition**：500 回归用例
- **test_data**：运行全部
- **expected**：通过率 ≥ 95%、失败列表
- **notes**：注意"通过率"vs"全部通过"

### TP-009（TEST_SCRIPT）：日志解析
- **scenario**：场景 8
- **module**：`TEST_SCRIPT`
- **precondition**：10GB 日志
- **test_data**：解析错误日志
- **expected**：提取错误日志条目
- **notes**：注意"正则"vs"解析器"

### TP-010（TEST_SCRIPT）：异常抓取
- **scenario**：场景 9
- **module**：`TEST_SCRIPT`
- **precondition**：游戏崩溃
- **test_data**：观察崩溃报告
- **expected**：堆栈捕获、设备信息
- **notes**：注意"崩溃"vs"ANR"

### TP-011（TEST_SCRIPT）：性能采样
- **scenario**：场景 10
- **module**：`TEST_SCRIPT`
- **precondition**：战斗中
- **test_data**：采样 5 分钟
- **expected**：FPS ≥ 30、CPU < 50%
- **notes**：注意"P50"vs"P95"vs"P99"

### TP-012（TEST_SCRIPT）：批量导出
- **scenario**：场景 11
- **module**：`TEST_SCRIPT`
- **precondition**：100 万订单
- **test_data**：导出到 CSV
- **expected**：导出文件 100 万行
- **notes**：注意"分批导出"

### TP-013（TEST_SCRIPT）：CI 集成
- **scenario**：场景 2
- **module**：`TEST_SCRIPT`
- **precondition**：CI 服务
- **test_data**：PR 提交触发
- **expected**：跑测试、报告
- **notes**：注意"PR"vs"主干"

### TP-014（TEST_SCRIPT）：并发压测稳定性
- **scenario**：场景 1
- **module**：`TEST_SCRIPT`
- **precondition**：1000 并发持续 1h
- **test_data**：观察内存
- **expected**：内存不持续增长
- **notes**：注意"内存泄漏"检测

### TP-015（TEST_SCRIPT）：数据生成可复现
- **scenario**：场景 5
- **module**：`TEST_SCRIPT`
- **precondition**：种子 = 12345
- **test_data**：生成数据两次
- **expected**：两次数据完全一致
- **notes**：注意"可复现"用于回归

---

## 3. 边界陷阱

### 边界 1：vs S5/S6 测试用例
- **混淆点**：「测试"脚本"」——H 测工具、S5/S6 测用例
- **判定规则**：测"测试工具/脚本本身" → H；测"具体测试用例" → S5/S6
- **实例**：压测脚本 → H；具体接口压测用例 → S5/S6

### 边界 2：vs I. 策划验收
- **混淆点**：「测试"清单"」——H 测脚本、I 测清单
- **判定规则**：测"自动执行脚本" → H；测"人工验收 Checklist" → I
- **实例**：UI 自动化 → H；功能验收 Checklist → I

### 边界 3：vs N. 异常兜底
- **混淆点**：「异常"抓取"」——H 测脚本工具、N 测运行时
- **判定规则**：测"异常抓取脚本" → H；测"生产环境异常处理" → N
- **实例**：崩溃堆栈抓取脚本 → H；崩溃自动恢复 → N

### 边界 4：vs K. 性能
- **混淆点**：「性能"采样"」——H 测脚本工具、K 测性能
- **判定规则**：测"性能采样脚本" → H；测"性能监控组件" → K
- **实例**：战斗性能采样脚本 → H；FPS 监控组件 → K

---

## 4. 验证证据

### 视觉证据
- 压测结果曲线图
- 性能采样报告

### 日志证据
- 脚本执行日志
- 错误日志
- 性能日志

### 数据证据
- 压测 TPS / 响应时间报告
- 回归通过率
- 性能数据采样

### 性能证据
- 脚本执行耗时
- 报告生成耗时
