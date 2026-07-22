# 程序自测点 GM 命令清单

**需求名称**：游戏道具商城系统
**版本**：v3.01
**日期**：2026-06-20

---

## GM 命令汇总

| 命令 | 用途 | 适用功能 |
|------|------|----------|
| `gm_item_list <page>` | 分页查询道具列表 | F1 商城首页 |
| `gm_item_publish <item_id>` | 模拟道具上架 | F1 商城首页 |
| `gm_item_unpublish <item_id>` | 模拟道具下架 | F1 商城首页 |
| `gm_item_search <keyword>` | 道具名称模糊搜索 | F1 商城首页 |
| `gm_item_detail <item_id>` | 查询道具详情 | F2 道具详情页 |
| `gm_item_price <item_id> <price>` | 修改道具价格 | F2 道具详情页 / F7 后台管理 |
| `gm_player_currency <player_id>` | 查询玩家余额 | F2 道具详情页 |
| `gm_player_vip <player_id>` | 查询玩家 VIP 等级 | F2/F5 |
| `gm_purchase <player_id> <item_id> <quantity>` | 模拟购买道具 | F3 购买流程 |
| `gm_purchase_refund <order_id>` | 模拟退款 | F4 订单管理 |
| `gm_order_list <player_id>` | 查询玩家订单列表 | F4 订单管理 |
| `gm_vip_discount <player_id>` | 验证 VIP 折扣计算 | F5 VIP 专属商城 |
| `gm_promotion_create <promo_id>` | 创建促销活动 | F6 促销系统 |
| `gm_promotion_end <promo_id>` | 结束促销活动 | F6 促销系统 |
| `gm_backstage_log <operator_id>` | 查询后台操作日志 | F7 后台管理 |

---

## 按功能模块分组

### F1 商城首页

| 命令 | 用途 | 测试场景 |
|------|------|----------|
| `gm_item_list 1` | 分页查询首页道具 | 道具上架后玩家端可见 |
| `gm_item_publish <item_id>` | 模拟上架 | 道具上架后玩家端可见 |
| `gm_item_unpublish <item_id>` | 模拟下架 | 道具下架后玩家端不可见 |
| `gm_item_search <keyword>` | 模糊搜索 | 精确匹配 / 模糊匹配 / 无结果场景 |

### F2 道具详情页

| 命令 | 用途 | 测试场景 |
|------|------|----------|
| `gm_item_detail <item_id>` | 查询详情 | 道具详情信息完整展示 |
| `gm_player_currency <player_id>` | 查询余额 | 余额不足时按钮置灰 |

### F3 购买流程

| 命令 | 用途 | 测试场景 |
|------|------|----------|
| `gm_purchase <player_id> <item_id> 1` | 单件购买 | 购买成功，道具到账 ≤ 1000ms |
| `gm_purchase <player_id> <item_id> 99` | 边界数量 | 购买数量最大 99 |
| `gm_purchase <player_id> <item_id> 0` | 边界数量 | 购买数量最小 1 |
| `gm_purchase <player_id> <item_id> 1` (余额不足) | 余额校验 | 余额不足时按钮置灰且提示 |
| `gm_player_vip <player_id>` | VIP 权限 | VIP 专属道具对非 VIP 玩家隐藏 |

### F4 订单管理

| 命令 | 用途 | 测试场景 |
|------|------|----------|
| `gm_order_list <player_id>` | 查询订单 | 30 天内订单完整展示 |
| `gm_purchase_refund <order_id>` | 退款 | 退款订单状态正确标记 |

### F5 VIP 专属商城

| 命令 | 用途 | 测试场景 |
|------|------|----------|
| `gm_player_vip <player_id>` | 查询 VIP 等级 | VIP 等级对应折扣正确 |
| `gm_vip_discount <player_id>` | 验证折扣 | VIP1 95 折 / VIP2 9 折 / VIP3 85 折 |

### F6 促销系统

| 命令 | 用途 | 测试场景 |
|------|------|----------|
| `gm_promotion_create <promo_id>` | 创建促销 | 限时打折 / 满减活动生效 |
| `gm_promotion_end <promo_id>` | 结束促销 | 促销结束后恢复原价 |

### F7 后台管理

| 命令 | 用途 | 测试场景 |
|------|------|----------|
| `gm_item_publish <item_id>` | 道具上下架 | 上架后立即生效（≤ 5 分钟） |
| `gm_item_price <item_id> <price>` | 价格配置 | 修改后立即生效 |
| `gm_backstage_log <operator_id>` | 操作日志 | 后台操作日志完整记录 |
