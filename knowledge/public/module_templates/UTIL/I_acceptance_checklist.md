# I. 策划验收清单

> **子类代码**：`ACCEPTANCE_CHECKLIST`
> **归属模块**：`UTIL`
> **来源**：用户细化定义 §9「策划验收清单」
>
> **测什么**：标准化验收模板、功能/数值/UI 验收 Checklist、上线自检、回归核对。
> **不测什么**：自动测试脚本（归 H）、业务用例（归 S5/S6）、GM（归 G）。
> **与其他子类的差异**：I 关注"人工验收清单"——H 关注"自动执行脚本"。

---

## 1. 典型场景

### 场景 1：标准化验收模板
- 业务背景：功能上线
- 涉及工具：验收模板
- 触发动作：策划填验收表
- 验证点：模板覆盖所有检查项

### 场景 2：功能验收 Checklist
- 业务背景：新功能
- 涉及工具：功能验收 Checklist
- 触发动作：按 Checklist 逐项验证
- 验证点：所有项通过

### 场景 3：数值验收核对表
- 业务背景：数值配置
- 涉及工具：数值验收表
- 触发动作：核对数值
- 验证点：与策划案一致

### 场景 4：UI 走查表
- 业务背景：UI 上线
- 涉及工具：UI 走查表
- 触发动作：设计师走查
- 验证点：UI 与设计稿一致

### 场景 5：上线准入检查
- 业务背景：版本上线
- 涉及工具：上线自检表
- 触发动作：QA/PM 走查
- 验证点：通过

### 场景 6：活动上线验收
- 业务背景：限时活动
- 涉及工具：活动验收项
- 触发动作：按活动 Checklist 验收
- 验证点：活动可正常开启

### 场景 7：热更发布自检
- 业务背景：热更发布
- 涉及工具：热更自检表
- 触发动作：发布前自检
- 验证点：配置/MD5/灰度等通过

### 场景 8：线上问题复现
- 业务背景：bug 复现
- 涉及工具：复现核对清单
- 触发动作：QA 复现
- 验证点：复现成功/失败

### 场景 9：版本回归验收
- 业务背景：新版本
- 涉及工具：回归验收表
- 触发动作：核心功能回归
- 验证点：核心功能正常

---

## 2. 种子测试点（TP 模板）

### TP-001（ACCEPTANCE_CHECKLIST）：验收模板完整性
- **scenario**：场景 1
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：新功能
- **test_data**：填写验收模板
- **expected**：模板覆盖功能/数值/UI/性能/兼容 5 大类
- **notes**：注意"模板"vs"清单"

### TP-002（ACCEPTANCE_CHECKLIST）：功能 Checklist 通过
- **scenario**：场景 2
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：新功能
- **test_data**：按 Checklist 逐项验证
- **expected**：所有项通过
- **notes**：注意"通过"vs"跳过"

### TP-003（ACCEPTANCE_CHECKLIST）：数值核对
- **scenario**：场景 3
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：数值配置
- **test_data**：核对道具 100 攻击力
- **expected**：与策划案一致
- **notes**：注意"精确"vs"误差容忍"

### TP-004（ACCEPTANCE_CHECKLIST）：UI 走查
- **scenario**：场景 4
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：UI 完成
- **test_data**：对比设计稿
- **expected**：颜色/间距/字号一致
- **notes**：注意"像素级"vs"视觉一致"

### TP-005（ACCEPTANCE_CHECKLIST）：上线准入检查
- **scenario**：场景 5
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：版本待上线
- **test_data**：QA/PM 走查
- **expected**：所有项通过、签字
- **notes**：注意"准入门槛"vs"建议"

### TP-006（ACCEPTANCE_CHECKLIST）：活动上线验收
- **scenario**：场景 6
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：活动待上线
- **test_data**：活动 Checklist 走查
- **expected**：活动配置/规则/奖励/时间全部 OK
- **notes**：注意"全量"vs"核心"

### TP-007（ACCEPTANCE_CHECKLIST）：热更发布自检
- **scenario**：场景 7
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：热更待发布
- **test_data**：发布前自检
- **expected**：配置/MD5/灰度/回滚预案齐全
- **notes**：注意"配置"vs"代码"

### TP-008（ACCEPTANCE_CHECKLIST）：线上问题复现
- **scenario**：场景 8
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：线上 bug
- **test_data**：按复现清单操作
- **expected**：QA 复现成功/失败
- **notes**：注意"复现步骤"vs"现象"

### TP-009（ACCEPTANCE_CHECKLIST）：版本回归验收
- **scenario**：场景 9
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：新版本
- **test_data**：核心功能回归
- **expected**：核心 100 个用例通过
- **notes**：注意"核心"vs"全部"

### TP-010（ACCEPTANCE_CHECKLIST）：验收报告归档
- **scenario**：场景 5
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：验收完成
- **test_data**：归档验收报告
- **expected**：报告入库、可追溯
- **notes**：注意"归档"vs"丢"

### TP-011（ACCEPTANCE_CHECKLIST）：跨部门验收
- **scenario**：场景 5
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：跨部门协作
- **test_data**：策划/QA/PM 共同验收
- **expected**：三方签字
- **notes**：注意"单方"vs"多方"

### TP-012（ACCEPTANCE_CHECKLIST）：验收 Checklist 更新
- **scenario**：场景 2
- **module**：`ACCEPTANCE_CHECKLIST`
- **precondition**：新类型 bug
- **test_data**：更新 Checklist
- **expected**：Checklist 持续完善
- **notes**：注意"持续"vs"一次性"

---

## 3. 边界陷阱

### 边界 1：vs H. 测试脚本
- **混淆点**：「测试"清单"」——H 测自动、I 测人工
- **判定规则**：测"自动执行脚本" → H；测"人工验收 Checklist" → I
- **实例**：UI 自动化脚本 → H；UI 走查表 → I

### 边界 2：vs S5/S6 测试用例
- **混淆点**：「测试"用例"」——I 测策划验收、S5/S6 测业务
- **判定规则**：测"策划/PM 验收清单" → I；测"QA 测试用例" → S5/S6
- **实例**：上线自检表 → I；具体接口测试用例 → S5/S6

### 边界 3：vs CONFIG-H
- **混淆点**：「配置"发布"」——I 测发布清单、CONFIG 测发布
- **判定规则**：测"发布 Checklist 流程" → I；测"配置发布工具" → CONFIG-H
- **实例**：热更自检表 → I；Excel 导出 JSON → CONFIG-H

### 边界 4：vs G. GM 工具
- **混淆点**：「GM"验收"」——I 测策划验收、G 测 GM
- **判定规则**：测"GM 指令" → G；测"GM 操作验收" → I
- **实例**：GM 发道具 → G；GM 指令验收清单 → I

---

## 4. 验证证据

### 视觉证据
- 验收 Checklist 截图
- 验收签字截图

### 日志证据
- 验收执行日志
- 归档日志

### 数据证据
- 验收报告库
- 验收通过率

### 性能证据
- 验收执行耗时
- 报告生成耗时
