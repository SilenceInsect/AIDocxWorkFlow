# K. 画质 / 性能辅助组件

> **子类代码**：`PERF_TOOL`
> **归属模块**：`UTIL`
> **来源**：用户细化定义 §12「画质/性能辅助组件」
>
> **测什么**：帧率控制、画质切换、内存监控、卡顿检测、降帧省电、分辨率适配。
> **不测什么**：业务性能（归 BIZ）、资源管理（归 D）、网络（归 B）。
> **与其他子类的差异**：K 关注"运行时性能工具"——D 关注"资源"，A 关注"通用"。

---

## 1. 典型场景

### 场景 1：帧率控制
- 业务背景：FPS 限制
- 涉及工具：帧率控制器
- 触发动作：玩家设置 60 FPS
- 验证点：游戏帧率 ≤ 60

### 场景 2：画质档位
- 业务背景：高/中/低画质
- 涉及工具：画质切换
- 触发动作：玩家切换画质
- 验证点：画质生效

### 场景 3：内存监控
- 业务背景：内存占用监控
- 涉及工具：内存监控
- 触发动作：游戏运行 1 小时
- 验证点：内存 < 阈值

### 场景 4：性能采样
- 业务背景：性能分析
- 涉及工具：采样工具
- 触发动作：战斗中采样
- 验证点：FPS/CPU/内存数据

### 场景 5：卡顿检测
- 业务背景：卡顿问题定位
- 涉及工具：卡顿检测
- 触发动作：游戏卡顿
- 验证点：卡顿点标记

### 场景 6：后台降帧
- 业务背景：省电
- 涉及工具：降帧工具
- 触发动作：切到后台
- 验证点：帧率降低

### 场景 7：多分辨率适配
- 业务背景：不同分辨率
- 涉及工具：分辨率适配
- 触发动作：不同屏幕
- 验证点：UI 正常

---

## 2. 种子测试点（TP 模板）

### TP-001（PERF_TOOL）：帧率限制生效
- **scenario**：场景 1
- **module**：`PERF_TOOL`
- **precondition**：玩家设置 60 FPS
- **test_data**：观察 FPS
- **expected**：FPS ≤ 60、不掉帧
- **notes**：注意"限制"vs"目标"

### TP-002（PERF_TOOL）：帧率 30 vs 60
- **scenario**：场景 1
- **module**：`PERF_TOOL`
- **precondition**：玩家设置 30 FPS
- **test_data**：观察 FPS
- **expected**：FPS ≈ 30、省电
- **notes**：注意"低端机"vs"高端机"

### TP-003（PERF_TOOL）：画质档位 - 高
- **scenario**：场景 2
- **module**：`PERF_TOOL`
- **precondition**：玩家设置高画质
- **test_data**：观察效果
- **expected**：特效全开、粒子数 = 100%
- **notes**：注意"特效"vs"分辨率"

### TP-004（PERF_TOOL）：画质档位 - 低
- **scenario**：场景 2
- **module**：`PERF_TOOL`
- **precondition**：玩家设置低画质
- **test_data**：观察效果
- **expected**：特效关闭、粒子数 = 30%
- **notes**：注意"低画质"vs"流畅"

### TP-005（PERF_TOOL）：内存监控
- **scenario**：场景 3
- **module**：`PERF_TOOL`
- **precondition**：游戏运行 1 小时
- **test_data**：观察内存
- **expected**：内存 < 1.5GB、按设计
- **notes**：注意"持续监控"vs"阈值告警"

### TP-006（PERF_TOOL）：内存超阈值告警
- **scenario**：场景 3
- **module**：`PERF_TOOL`
- **precondition**：内存阈值 1.5GB
- **test_data**：内存达到 1.5GB
- **expected**：告警、可能自动释放
- **notes**：注意"告警"vs"自动恢复"

### TP-007（PERF_TOOL）：性能采样
- **scenario**：场景 4
- **module**：`PERF_TOOL`
- **precondition**：战斗中
- **test_data**：采样 5 分钟
- **expected**：FPS/CPU/内存/网络数据
- **notes**：注意"采样频率"（如 1Hz）

### TP-008（PERF_TOOL）：卡顿检测
- **scenario**：场景 5
- **module**：`PERF_TOOL`
- **precondition**：游戏卡顿
- **test_data**：观察卡顿点
- **expected**：卡顿帧标记、堆栈
- **notes**：注意"卡顿"阈值（如 > 100ms）

### TP-009（PERF_TOOL）：后台降帧
- **scenario**：场景 6
- **module**：`PERF_TOOL`
- **precondition**：玩家切后台
- **test_data**：观察帧率
- **expected**：帧率从 60 降到 10 或暂停
- **notes**：注意"降帧"vs"暂停"

### TP-010（PERF_TOOL）：回前台恢复帧率
- **scenario**：场景 6
- **module**：`PERF_TOOL`
- **precondition**：后台 → 前台
- **test_data**：观察帧率
- **expected**：帧率恢复到 60
- **notes**：注意"恢复"vs"重启"

### TP-011（PERF_TOOL）：多分辨率适配
- **scenario**：场景 7
- **module**：`PERF_TOOL`
- **precondition**：不同屏幕
- **test_data**：1080p / 2K / 4K
- **expected**：UI 正常、缩放正确
- **notes**：与 UI-C 配合

### TP-012（PERF_TOOL）：画质切换实时
- **scenario**：场景 2
- **module**：`PERF_TOOL`
- **precondition**：战斗中
- **test_data**：实时切换画质
- **expected**：生效、不卡顿
- **notes**：注意"实时"vs"重启"

### TP-013（PERF_TOOL）：低端机自适应
- **scenario**：场景 3
- **module**：`PERF_TOOL`
- **precondition**：低端机
- **test_data**：游戏启动
- **expected**：自动降画质、保流畅
- **notes**：注意"自适应"vs"手动"

### TP-014（PERF_TOOL）：GPU 占用监控
- **scenario**：场景 4
- **module**：`PERF_TOOL`
- **precondition**：游戏运行
- **test_data**：观察 GPU
- **expected**：GPU 占用 < 80%
- **notes**：注意"GPU"vs"CPU"

### TP-015（PERF_TOOL）：发热监控
- **scenario**：场景 3
- **module**：`PERF_TOOL`
- **precondition**：长时间游戏
- **test_data**：观察设备温度
- **expected**：温度过高告警、自动降帧
- **notes**：注意"发热"阈值

---

## 3. 边界陷阱

### 边界 1：vs D. 资源管理
- **混淆点**：「资源"性能"」——D 测资源加载、K 测性能
- **判定规则**：测"资源加载/释放" → D；测"运行时 FPS/CPU" → K
- **实例**：场景资源加载 → D；战斗帧率 → K

### 边界 2：vs H. 测试脚本
- **混淆点**：「性能"采样"」——H 测脚本工具、K 测运行时
- **判定规则**：测"性能采样脚本" → H；测"运行时性能监控组件" → K
- **实例**：战斗采样脚本 → H；FPS 监控组件 → K

### 边界 3：vs UI-C 布局
- **混淆点**：「分辨率"适配"」——K 测性能、UI-C 测布局
- **判定规则**：测"分辨率下 UI 布局" → UI-C；测"分辨率下帧率" → K
- **实例**：4K 下 UI 正常 → UI-C；4K 下帧率 ≥ 30 → K

### 边界 4：vs BIZ
- **混淆点**：「业务"性能"」——K 测通用工具、BIZ 测业务
- **判定规则**：测"通用性能工具" → K；测"业务性能需求" → BIZ
- **实例**：FPS 监控 → K；战斗帧率 < 30 不可玩 → BIZ

---

## 4. 验证证据

### 视觉证据
- FPS 显示截图
- 画质对比截图

### 日志证据
- 帧率日志
- 内存日志
- 卡顿点日志
- 发热告警

### 数据证据
- 性能采样数据
- 设备温度数据
- 资源占用统计

### 性能证据
- FPS ≥ 30
- CPU < 50%
- 内存 < 阈值
