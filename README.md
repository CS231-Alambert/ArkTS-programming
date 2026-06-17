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

```
scaffold.sh → Step 0(扫描) → Step 1(生成) → Step 2(自检) → Step 3(报告)
     │              │               │              │              │
  🆕 一键建项目  磁盘检查点     磁盘检查点    25项自动扫描   自检报告输出
                 00-scan.json   01-gen.json   02-checked.json  对话输出
```

**门禁机制**：每一步写入磁盘检查点文件，下一步读取。`test -f .arkts-check/XX.json` 不存在 → 阻断。不是 prompt 建议——是物理文件存在性检查。

## self-check.sh — 25 项自动验证

| 类别 | Pass | 来源 |
|------|------|------|
| 基础语法 (1-13) | @ohos 旧导入、new Function、@State 冲突、router RouterMode、ForEach key、any/var 禁用、localhost 检测、INTERNET 权限、displayPriority 小数 | 实战踩坑 |
| 编程规范 (14-17) | 多变量同行、NaN 比较、条件赋值、finally 控制流 | [华为编程规范](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V13/arkts-coding-style-guide-V13) 要求级 |
| 性能规则 (18、23) | @Prop→@ObjectLink 建议、循环内状态读取 | [状态管理最佳实践](https://developer.huawei.com/consumer/cn/doc/best-practices-V5/bpta-status-management-V5) |
| 组件规范 (19-22、24-25) | fontSize 误用、Alignment.Left/Right、Shape 缺 stroke、@State 位置、Color 枚举、export default | 实战踩坑 |

每项 FAIL/WARNING 携带：错误描述 + 官方文档链接 + 修复指导 + PITFALLS 锚点。

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
