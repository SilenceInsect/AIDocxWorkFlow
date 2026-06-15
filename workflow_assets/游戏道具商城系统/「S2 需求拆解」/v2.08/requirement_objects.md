# 需求对象拆解 — 游戏道具商城系统（S2 深度版）

> 复用 S1 阶段 `requirement_objects.md` 的 18 个 OBJ，本文件标注其在 S2 Epic/Story 层级映射关系。

| OBJ | OBJ 名称 | 主模块 | 归属 Epic | 归属 Story |
|---|---|---|---|---|
| OBJ-01 | 商城首页 | UI | E1 | S1.1 |
| OBJ-02 | 道具详情页 | UI | E1 | S1.2 |
| OBJ-03 | 购买流程 | BIZ | E2 | S2.1 |
| OBJ-04 | 订单管理 | BIZ | E2 | S2.2 |
| OBJ-05 | VIP 专属商城 | BIZ | E3 | S3.1 |
| OBJ-06 | 促销系统 | BIZ | E3 | S3.2 |
| OBJ-07 | 支付方式 | LINK | E4 | S4.1 |
| OBJ-08 | 道具数据缓存 | AUX | E4 | S4.2 |
| OBJ-09 | 商城页加载性能监控 | LOG | E5 | S5.1 |
| OBJ-10 | 购买按钮置灰提示 | HINT | E7 | S7.1 |
| OBJ-11 | 购买成功弹窗 | HINT | E7 | S7.1 |
| OBJ-12 | 道具数据配置表 | CONFIG | E6 | S6.1 |
| OBJ-13 | VIP 等级配置表 | CONFIG | E6 | S6.2 |
| OBJ-14 | 促销配置表 | CONFIG | E6 | S6.2 |
| OBJ-15 | 弱网/高并发降级 | SPECIAL | E5 | S5.2 |
| OBJ-16 | 风控拦截 | SPECIAL | E5 | S5.3 |
| OBJ-17 | 资产审计日志 | LOG | E5 | S5.4 |
| OBJ-18 | 支付链路日志 | LOG | E5 | S5.4 |

## 8 模块分布

| 模块 | OBJ 数 | Epic 数 |
|---|---|---|
| UI | 2 | 1 (E1) |
| BIZ | 4 | 2 (E2, E3) |
| AUX | 1 | 1 (E4-S4.2) |
| LINK | 1 | 1 (E4-S4.1) |
| LOG | 3 | 1 (E5) |
| SPECIAL | 2 | 1 (E5) |
| CONFIG | 3 | 1 (E6) |
| HINT | 2 | 1 (E7) |
| **合计** | **18** | **7** |
