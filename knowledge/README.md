# Knowledge SSOT

> 本文件是 `knowledge/` 目录的唯一治理总说明。
> 目标：明确 **公共知识库** 与 **项目级知识库** 的边界、Git 策略、格式策略、审核流、引用规则。
> 若本文件与其他知识库 README 冲突，以本文件为准。

---

## 1. 目录定位

`knowledge/` 是 AIDocxWorkFlow 的知识资产根目录，不承载运行过程产物。

目录分层如下：

```text
knowledge/
├── README.md                   # 本文件（知识库治理 SSOT）
├── public/                     # 公共知识库，纳入 Git
│   ├── module_templates/
│   ├── test_point_library/
│   ├── test_case_library/
│   └── example_test_cases/
└── project_local/              # 项目级知识库，默认不纳入 Git
    ├── <project_name>/         # 单个项目的本地知识目录（不入 Git）
    │   └── s6/
    │       ├── export_profiles/
    │       │   └── test_cases.export.json
    │       └── xlsx_templates/
    │           └── test_cases.template.xlsx
    └── .review_queue/          # Agent 产出的待人工审核候选 / 可提交样例
```

---

## 2. 知识库分类

### 2.1 公共知识库

定义：
- 面向整个 AIDocxWorkFlow 项目复用
- 不绑定某个具体产品、项目、客户或单次需求
- 可作为运行时默认输入，被多个阶段直接读取

特点：
- 纳入 Git
- 要求可审查、可追溯、可复用
- 结构相对稳定，优先追求统一格式

当前公共知识库包括：
- `knowledge/public/module_templates/`
- `knowledge/public/test_point_library/`
- `knowledge/public/test_case_library/`
- `knowledge/public/example_test_cases/`

### 2.2 项目级知识库

定义：
- 只服务某个项目、产品线、业务域或客户
- 允许带有明显项目特征、术语、格式、判定标准
- 不应默认污染整个项目的公共运行时

特点：
- 默认 `.gitignore`
- 允许与公共知识库格式不同
- 可更贴近项目本地语境，不强求公共格式一致

当前项目级知识库根目录：
- `knowledge/project_local/`

项目级知识可进一步细分为：
- 项目级规则知识
- 项目级测试点/用例知识
- 项目级导出模板知识（如 Excel 表头、Sheet 结构、列顺序、显示名）

### 2.3 S6 项目级导出目录规范

S6 项目级导出知识必须拆成两类，不允许再混成一个文件：

```text
knowledge/project_local/<project_name>/s6/
├── export_profiles/
│   └── test_cases.export.json      # JSON 导出配置：字段映射、表头、Sheet 名、列顺序
└── xlsx_templates/
    └── test_cases.template.xlsx    # XLSX 模板文件：样式、额外 Sheet、人工维护布局
```

职责边界：
- `export_profiles/test_cases.export.json` 只负责“怎么把 `test_cases.json` 映射成导出结构”
- `xlsx_templates/test_cases.template.xlsx` 只负责“Excel 长什么样”
- 不允许把字段映射和 Excel 模板职责混写在同一个文件中
- 若项目没有自定义 Excel 模板，可只保留 `export_profiles/test_cases.export.json`

---

## 3. 格式原则

### 3.1 公共库格式原则

- 公共库优先遵循统一结构和统一命名
- 能抽象成跨项目共用规则的，必须先抽象再入库
- 不允许把单个项目的特殊字段、特殊章节、特殊命名直接塞进公共库

### 3.2 项目级库格式原则

- 项目级知识库**允许与公共库格式不同**
- 可以引入项目专属字段、专属章节、专属命名
- 但必须做到“人能快速读懂”和“知道它为什么不同”

### 3.3 公共与项目级格式冲突时

默认处理顺序：
1. 优先判断是否真的是项目特例
2. 若是项目特例，留在 `knowledge/project_local/`
3. 若可抽象出跨项目稳定部分，只把稳定部分提升到 `knowledge/public/`
4. 不允许为了追求统一，硬把项目特例塞进公共库

示例：
- “倒计时模块”在公共库中可定义通用倒计时规则
- 某项目若存在专属倒计时展示格式、状态词、特殊边界，则进入项目级知识库
- 公共规则与项目规则可以并存，但不能混写在同一正式公共文件中
- S6 `test_cases.xlsx` 的表头、Sheet 命名、列顺序、附加列若为项目专属，也应进入项目级知识库，而不是写入公共默认格式

---

## 4. Git 策略

### 4.1 必须入 Git

- `knowledge/public/**`
- 与知识库治理相关的说明文档

### 4.2 默认不入 Git

- `knowledge/project_local/**`

例外：
- `knowledge/project_local/.review_queue/` 目录结构可存在
- 若未来需要提交特定候选样例，必须先明确说明原因并单独决策

---

## 5. 入库流程

### 5.1 公共知识库入库

公共知识库不是 Agent 可直接落正式内容的区域。

规则：
- Agent 可以读取公共知识库
- Agent 不得直接改写 `knowledge/public/module_templates/` 正式内容
- Agent 不得因为 S8 自迭代结果，自动把项目经验直接写入公共正式库

标准流程：
1. Agent 产出候选
2. 候选落到 `knowledge/project_local/.review_queue/`
3. 人工审核
4. 人工决定：
   - 回写公共库
   - 保留为项目级知识
   - 丢弃

### 5.2 `module_templates/` 特别规则

`knowledge/public/module_templates/` 属于核心公共知识库。

硬约束：
- 必须人工审核后入库
- 任何新增、改写、补充都不能跳过审核
- S8 只能生成候选，不能直接补正式模板

### 5.3 项目级知识库沉淀

项目级知识沉淀允许更快，但仍需满足：
- 说明适用项目/业务域
- 说明与公共格式的差异点
- 说明为什么不适合直接提升为公共库

---

## 6. 引用原则

### 6.1 运行时默认读取

运行时默认读取：
- `knowledge/public/`

运行时默认不读取：
- `knowledge/project_local/`

原因：
- 项目级知识不应在无判定前污染全局运行时

### 6.2 何时可读取项目级知识库

只有在以下条件满足时才可读取：
- 当前任务明确绑定某个项目/产品线
- 已明确知道要读取哪个项目级知识目录
- 使用者知道该知识可能与公共格式不同

补充：
- 若任务目标是产出项目级 `md/xlsx` 模板或项目级 Excel 表头，**任务开始必须先确认当前是给哪个项目产出**
- 若未确认项目，默认只能产出公共格式产物
- 当前决策中，**公共格式只产出 JSON**；`md/xlsx` 视为项目级导出资产，需项目上下文才允许生成
- 对 S6 而言，项目级导出资产默认从 `knowledge/project_local/<project_name>/s6/` 读取，而不是从需求目录名自动推断

### 6.3 新增知识目录前的判定

新增目录或文件前，必须先判断其归属：
- 公共知识库
- 项目级知识库
- 过程资产
- 规则/治理资产

边界不清时，先询问，不允许先创建再补说明。

---

## 7. 与其他 SSOT 的关系

| 内容 | 真相源 |
|---|---|
| 知识库治理边界 | `knowledge/README.md` |
| 8 模块定义/边界 | `.cursor/MODULES.md` |
| 全局执行与 Git 分类规则 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` |
| 项目决策原则 | `AGENTS.md` |

说明：
- 本文件管“知识库怎么分层、怎么入库、怎么引用”
- `.cursor/MODULES.md` 管“模块本身定义是什么”
- 二者职责不同，禁止互相替代

---

## 8. 维护要求

- 若修改 `knowledge/` 分层、Git 策略、审核流，必须先改本文件
- 若公共库与项目级库新增新的子类型目录，必须先在本文件补分类规则
- 若某个子库 README 与本文件冲突，优先修正子库 README

---

## 9. 当前决策

- 公共知识库放 `knowledge/public/`
- 项目级知识库放 `knowledge/project_local/`
- 项目级知识库默认不纳入 Git
- 公共库和项目级库格式允许不同
- `module_templates/` 必须人工审核后入公共库
- Agent 新增文件/目录前必须先做 Git 分类判定，边界不清先询问
- 公共测试用例格式默认只保证 `json`
- `test_cases.md` / `test_cases.xlsx` 的表头与模板可为项目级知识，生成前必须先确认项目
- S6 项目级导出必须拆分为：
  - `s6/export_profiles/test_cases.export.json`
  - `s6/xlsx_templates/test_cases.template.xlsx`
