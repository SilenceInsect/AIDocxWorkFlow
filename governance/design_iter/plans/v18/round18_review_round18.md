# Round 18 Review

## 1. 验收总结

- PASS：编译、两组 self-test、重导、88 × 11、排序、五色、E/F 数据保护、H 列独立性、JSON/backup hash 保护。
- FAIL：预期 48 merges。物理结果为 46，缺少两个 B merge。
- FAIL 根因：两个 purchase OBJ 的 `module` 是真实混合值，而不是 worksheet 合并后的 None 副作用。
- 结论：当前 workbook 的 46 merges 是 uniform guard 按 per-TC module 契约执行后的安全结果。把 46 改成 48 需要新增业务语义，不属于“只重导验证”。

## 2. 触发的反模式

### AP-R18-001：先锁定预期数，再验证数据语义

预期先写成 `16 OBJ × B/C/D = 48`，但没有先检查 B 是否真是 OBJ 级字段。实际 B 是 per-TC module，在两个 OBJ 中含 `LOG`/`SPECIAL`。

修复原则：merge 数量必须由字段层级和 uniformity 推导，不能由“OBJ 数 × 候选列数”直接推导。

### AP-R18-002：将 worksheet 副作用误判为唯一根因

前序诊断把两个 B 漏合并归因于 merged-cell None。切换到内存判断后仍是 False，证明内存数据本身非均匀。

修复原则：导出问题必须依次验证输入数据、内存标准化数据、worksheet 物理结果，不能跳过中间层。

### AP-R18-003：对 `MergedCell` 做逐格样式比较

第一次颜色审计把 merged range 内的 `MergedCell` 当作普通 Cell 比较 fill，产生颜色连续性 false negative。修正后按可见 top-left merged cell 与所有独立列审计，五色契约 PASS。

### AP-R18-004：换行统计转义错误

第一次诊断用字面量 `\\n` 统计换行，错误显示每个 H 为 1 行。修正为 `splitlines()` 后，87/87 H cell 都是多行单 TC string。

### AP-R18-005：诊断命令引号错误

两个只读 one-liner 因 f-string 转义发生 SyntaxError；没有重复重导，也没有改文件。后续改用 heredoc 完成一次正确读审计，避免限流式连续重试。

## 3. V/P Review

- V-001：PASS。
- V-002：PASS。
- V-003：FAIL，BLOCKER。
- V-004：PASS。
- V-005：PASS。
- P-001：PASS。
- P-002：PASS。
- P-003：PASS。

## 4. Follow-up

1. 人工确认 B 列语义：展示每个 TC 的真实 module，还是展示 OBJ 归属模块。
2. 若展示真实 module，接受 46 作为正确结果，并把 48 验收标准修正为“按 uniform guard 动态计算”。
3. 若展示 OBJ 归属模块，新增独立字段和来源契约；禁止用强制 merge 静默覆盖 `LOG`/`SPECIAL`。
4. 选择完成后再更新 snapshot 为 achieved；当前不得伪写 achieved。
