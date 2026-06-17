# harmonyos-arkts Skill 设计说明

## 一句话定位

**令行禁止、效率高、质量好**的 ArkTS 代码生成引擎。不是参考手册——是强制执行 4 步硬门禁流水线 + 25 项自动自检 + 一键脚手架的生产级 skill。

---

## 文件结构

```
harmonyos-arkts/
├── SKILL.md        (~285行) — 始终注入 system prompt：门禁流程 + 核心规则 + 检查清单 + 指针
├── REFERENCE.md    (1308行) — 按需 Read，顶部索引 30 条：API速查 + 编程规范 + 性能规则
├── PITFALLS.md     (1492行) — 按需 Read，顶部索引 60+ 条：编译错误 + 最佳实践违反
├── EXAMPLES.md     (3077行) — 按需 Read，顶部索引 44 条：完整可编译运行示例
├── README.md        — 本文件
└── scripts/
    ├── self-check.sh   (379行) — 25 项自动检查，硬门禁 Step 2
    └── scaffold.sh     (297行) — 一键生成 Stage + Navigation 项目骨架
```

## 四层文件架构

**核心原则**：SKILL.md 是 session 启动时完整注入的，其他文件仅在需要时通过 `Read offset=` 精准加载。

| 文件 | 加载方式 | 体积策略 | 内容 |
|------|----------|----------|------|
| SKILL.md | **始终全量注入** | < 300 行 | 门禁流程、核心规则、检查清单、子文件定位指南 |
| REFERENCE.md | 按需 `Read offset=` | 可大，有索引 | API 速查、导入路径、编程规范、性能规则 |
| PITFALLS.md | 按需 `Read offset=` | 可大，有索引 | 编译错误、最佳实践违反、修复方案 |
| EXAMPLES.md | 按需 `Read offset=` | 最大 | 44 个完整可编译示例 |

## 硬门禁流水线

代码生成不是"建议"，是**强制 4 步流水线**。每一步产出磁盘检查点，下一步**物理验证**检查点存在——跳过即阻断。

```
  🆕 新项目?                     生成代码                    自动扫描                  交付报告
  scaffold.sh   ────────────▶   Step 1    ────────────▶    Step 2    ────────────▶    Step 3
       │                            │                          │                          │
       ▼                            ▼                          ▼                          ▼
  Step 0 扫描               .arkts-check/               .arkts-check/              对话输出
  .arkts-check/             01-generated.json           02-checked.json             逐项状态
  00-scan.json              门禁: 00 必须存在            门禁: 01 必须存在           门禁: 02 必须存在
```

| 步骤 | 动作 | 产出 | 进入下一轮的前提 |
|:----:|------|------|------------------|
| 🆕 | `bash scripts/scaffold.sh` 一键建项目 → 自动执行 Step 0 | — | — |
| 0 | Python 扫描项目结构（pages/media/components/权限/架构） | `.arkts-check/00-scan.json` | 无前置 |
| 1 | `grep` 校验 API → 生成 .ets 代码 → 写入检查点 | `.arkts-check/01-generated.json` | `test -f 00-scan.json` |
| 2 | `bash scripts/self-check.sh` 全项目 25 项扫描 | `.arkts-check/02-checked.json` | `test -f 01-generated.json` |
| 3 | 读取 02-checked.json `status` 字段 → PASS 输出报告 / FAIL 回 Step 2 | 自检报告 | `test -f 02-checked.json` |

> **🔴 铁律**：写任何 .ets 文件前，`test -f .arkts-check/00-scan.json`。不存在 → 立即停止，先执行 Step 0。

## self-check.sh — 25 项自动验证

脚本 `bash scripts/self-check.sh <项目根目录>` 逐项扫描所有 .ets 源文件。exit code ≠ 0 阻断 Step 3。每项输出携带错误描述 + 官方文档链接 + PITFALLS 锚点。

### 语法层：ArkTS 编译器必报错的模式

| # | 检查项 | 正则模式 | 级别 |
|:--:|--------|----------|:----:|
| 1 | `@ohos.*` 旧式导入 | `@ohos\.` | 🔴 FAIL |
| 2 | `new Function()` 动态执行 | `new Function` | 🔴 FAIL |
| 3 | `Select.options()` 未文档化 API | `\.options(` | 🔴 FAIL |
| 4 | `@State height/weight` 与组件属性冲突 | `@State (height\|weight):` | 🔴 FAIL |
| 5 | `router.pushUrl` 缺 `RouterMode.Standard` | 多文件交叉检查 | 🔴 FAIL |
| 6 | `ForEach` 缺 key 生成函数 | `ForEach(` 计数 | 🟡 WARN |
| 7 | 文件首行非 import/@Entry/@Component/struct | 逐文件 `head -1` | 🟡 WARN |
| 8 | `any` / `unknown` / `var` 禁用关键字 | `\b(any\|unknown\|var)\b` | 🔴 FAIL |
| 9 | ForEach 回调未使用 index/idx 参数 | `ForEach.*index: number` | 🟡 WARN |
| 10 | `localhost` / `127.0.0.1` 模拟器不可达 | `(localhost\|127\.0\.0\.1)` | 🟡 WARN |
| 11 | `@ohos.net.http` 旧式导入 | `@ohos\.net\.http` | 🔴 FAIL |
| 12 | `http.createHttp` 使用但 module.json5 缺 INTERNET 权限 | 交叉检查 module.json5 | 🔴 FAIL |
| 13 | `displayPriority()` 使用小数值 | `displayPriority(\d+\.\d+)` | 🟡 WARN |

### 规范层：华为官方编程规范（要求级）

> 来源：[ArkTS 编程规范](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V13/arkts-coding-style-guide-V13)

| # | 规则 | 正例 | 反例 | 级别 |
|:--:|------|------|------|:----:|
| 14 | 每行只声明一个变量 | `let a = 1; let b = 2;` | `let a = 1, b = 2;` | 🔴 FAIL |
| 15 | NaN 必须用 `Number.isNaN()` | `Number.isNaN(x)` | `x == NaN` | 🔴 FAIL |
| 16 | 条件表达式内禁止赋值 | `if (isFoo)` | `if (isFoo = false)` | 🔴 FAIL |
| 17 | finally 块禁止 return/break/continue/throw | `finally { cleanup() }` | `finally { return 3 }` | 🔴 FAIL |

### 性能层：状态管理最佳实践

> 来源：[状态管理最佳实践](https://developer.huawei.com/consumer/cn/doc/best-practices-V5/bpta-status-management-V5) + [CodeLinter @performance](https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V5/ide_hp-arkui-use-object-link-to-replace-prop-V5)

| # | 规则 | 检测模式 | 级别 |
|:--:|------|----------|:----:|
| 18 | 对象/class 类型用 `@ObjectLink` 替代 `@Prop`（避免深拷贝） | `@Prop \w+ : [A-Z]` | 🟡 WARN |
| 23 | 循环内避免直接读取 `@State`/`@Link`（先提取到局部变量） | `for/while/ForEach{...this.` | 🟡 WARN |

### 组件层：DevEco Studio 高频编译错误

| # | 检查项 | 级别 |
|:--:|--------|:----:|
| 19 | `fontSize`/`fontColor`/`fontWeight` 用于 Column/Row 等非文本容器 | 🟡 WARN |
| 20 | `Alignment.Left`/`Right`（应使用 `Start`/`End` 语义） | 🔴 FAIL |
| 21 | Shape 组件（Circle/Ellipse/Path 等）缺 `.stroke()` | 🟡 WARN |
| 22 | `@State` 声明在 struct 外部 | 🟡 WARN |
| 24 | `Color.Xxx` 枚举可能不存在于 ArkUI（优先用十六进制 `'#XXXXXX'`） | 🟡 WARN |
| 25 | `components/` 目录下组件未用 `export default` | 🔴 FAIL |

## 内容来源

本 skill 的内容来自三个方向：

- **[华为开发者官方文档](https://developer.huawei.com/consumer/cn/doc/)**：ArkTS 编程规范、状态管理最佳实践、高性能编程实践、Navigation vs Router 对比、MVVM 架构指南、装饰器初始化约束——每一项自动检查都对应一条官方规则
- **个人开发实战踩坑**：PITFALLS.md 中大量条目来自 DevEco Studio 逐行编译报错的总结——"为什么改了属性 UI 不更新"、"为什么 router.pushUrl 回调不触发"——这些在文档里往往没有明确答案
- **实习课程笔记**：第三方 SDK 集成、json-server 模拟后端、三层架构多端部署、自适应布局 7 种能力、组合手势——来自专业实习的完整课程体系

## SKILL.md 内容选取原则

只放"每次生成代码都必须检查"的东西：

- **门禁流程**（Step 0→1→2→3 检查点链路）
- **禁止项**（any/var/dynamic property——错一次 = 编译失败）
- **状态管理**（V1/V2 装饰器 + 5 条性能规则）
- **导入路径**（@kit 格式——最高频错误）
- **Navigation 路由**（官方首推方案，Router 标记 ⚠️ 废弃）
- **项目结构 + 权限**
- **生成检查清单**（25 项，在 Step 3 报告逐条输出）
- **子文件定位指南**

不放：完整 API 参数表、完整错误示例、完整代码示例——这些分别归属 REFERENCE/PITFALLS/EXAMPLES。

## 为什么每个子文件顶部要有索引

1. **Agent 倾向"读完再说"**。没有索引时，面对 3000 行的 EXAMPLES.md 可能直接 Read 全量，挤压对用户实际需求的判断空间。
2. **索引让 Agent 知道自己该读多少**。看到索引表后能先定位行号，用 `Read offset=` 精准获取。
3. SKILL.md 底部有"定位指南"，明确告诉 Agent：用 `Read offset=行号 limit=行数` 精准跳转，**切勿全量读取**。

## 迭代原则

1. 新增内容先判断属于"每次必查"还是"偶尔需要"，前者进 SKILL.md，后者进子文件。
2. 每次给子文件加内容后，**同时更新顶部索引**。
3. SKILL.md 超过 300 行时，把低频速查信息下沉到 REFERENCE.md。
4. **每条自动检测必须对应一条官方规则或一个真实编译错误**——不做"可能有用的检查"。
5. 新增 Pass → 同步更新 SKILL.md 的 Pass 列表 + PITFALLS.md 对应条目。
