# harmonyos-arkts Skill 设计说明

## 一句话定位

**令行禁止、效率高、质量好**的 ArkTS 代码生成引擎。不是参考手册——是强制执行 4 步硬门禁流水线 + 25 项自动自检 + Hook 硬件级拦截 + 一键脚手架 + MCP Server 知识库搜索的生产级 skill。

---

## 快速开始

```bash
# 1. 安装 Python 依赖
python3 -m venv .venv && source .venv/bin/activate && pip install -e .

# 2. 新建 HarmonyOS 项目
bash scripts/scaffold.sh MyApp com.example.myapp

# 3. 一键部署 Hook（让 Claude Code 自动巡检）
bash scripts/install-hooks.sh

# 4. 运行测试确认一切正常
python3 -m pytest tests/ -v
```

---

## 双形态运行

本项目同时以 **两种形态** 运行，共享同一套代码和知识库：

| 形态 | 入口 | 触发方式 |
|------|------|---------|
| MCP Server | `arkagent` (11 工具) | Claude Code 启动自动拉起，对话中直接调用 |
| Claude Code Skill | `SKILL.md` | `/harmonyos-arkts` 命令触发，注入系统提示词 |

```
用户输入 prompt
      │
      ├─→ arkagent MCP Server（后台常驻）
      │   ├─ arkagent_search_docs     ← "帮我查 javaScriptProxy 怎么用"
      │   ├─ arkagent_check_syntax     ← 自动扫描 .ets 语法错误
      │   ├─ arkagent_gate_scan        ← Step 0 项目扫描
      │   └─ ... 共 11 个工具
      │
      └─→ harmonyos-arkts Skill（按需注入）
          ├─ SKILL.md     → 核心规则 + 门禁流程
          ├─ REFERENCE.md → API 速查（Read offset=）
          ├─ PITFALLS.md  → 编译错误库（Read offset=）
          └─ EXAMPLES.md  → 44 个可编译示例（Read offset=）
```

---

## 文件结构

```
ArkTS-programming/
├── SKILL.md            (~19KB)  — 始终注入 system prompt：门禁流程 + 核心规则 + MCP 工具路由
├── REFERENCE.md        (~42KB)  — 按需 Read，顶部 30 条索引：导入路径、装饰器、性能规则
├── PITFALLS.md         (~46KB)  — 双索引：13 类主题树 + 60+ 条编译错误
├── EXAMPLES.md         (~87KB)  — 按需 Read，顶部 44 条完整可编译示例
├── README.md                     — 本文件
│
├── arkagent/                     — MCP Server (FastMCP, 11 tools)
│   ├── __init__.py               — 公开 API 导出（ServerConfig, build_index, load_index, ...）
│   ├── server.py                 — MCP 入口：lifespan 索引管理 + 工具注册
│   ├── config.py                 — 配置：路径（支持 ARKAGENT_* 环境变量覆盖）、搜索参数
│   ├── indexer/
│   │   ├── builder.py            — TF-IDF 索引构建器（80 文档 → 6400 词条，141 API）
│   │   ├── query.py              — 搜索/查询引擎（search_docs, api_lookup, find_example, list_topics）
│   │   ├── schemas.py            — 数据模型（Section, CodeBlock, SearchIndex, APIReference）
│   │   └── index.json            — 预构建索引（.gitignore 排除，首次启动自动生成）
│   ├── tools/
│   │   ├── knowledge/
│   │   │   └── search_docs.py    — 4 个知识检索工具
│   │   ├── validation/
│   │   │   ├── check_syntax.py       — 25 类 ArkTS 语法错误扫描
│   │   │   ├── check_state_mgmt.py   — V1/V2 状态管理审计
│   │   │   ├── validate_imports.py   — 导入路径合规检查
│   │   │   └── scan_project.py       — 全项目一键检查
│   │   └── gate.py               — 3 个门禁管道工具（scan/check/status）
│   └── rules/
│       └── checkers/             — 规则引擎骨架（imports/syntax/state/security/arch）
│
├── docs/                         — 知识库（4 分类 80 文档 ~763KB）
│   ├── arkweb/       42 文档     — ArkWeb 方舟 Web（JSBridge、离线、渲染、同层）
│   ├── arkts/        15 文档     — ArkTS 方舟编程语言（TaskPool、Worker、迁移）
│   ├── arkui/         6 文档     — ArkUI 方舟 UI 框架（概述、调试、窗口）
│   └── ui-design-kit/ 15 文档    — UI Design Kit（组件、导航、布局）
│
├── scripts/                      — Shell 工具集
│   ├── scaffold.sh               — 一键生成 Stage + Navigation 项目骨架 + 自动 Step 0
│   ├── self-check.sh             — 25 项自动检查 + 三层架构扫描 + 规则分层 + 历史累积
│   ├── quick-check.sh            — Hook 用静默巡检（默认 9 项关键 pass，PASS 不输出）
│   ├── health-report.sh          — 跨会话趋势分析（Bucket-Seal 模式）
│   ├── install-hooks.sh          — 一键部署 PreToolUse + PostToolUse Hook
│   ├── rules-template.json       — L2 项目规则配置模板
│   ├── fetch_huawei_doc.py       — Playwright HTML→MD 转换器
│   ├── fetch_all.sh              — 批量抓取华为 HarmonyOS 文档
│   ├── url_catalog.json          — 140 个华为文档 URL 目录
│   ├── fetch_batch.json          — 80 文档抓取配置
│   └── batch_arkts.json          — 17 项 ArkTS 文档批量配置
│
├── tests/                        — 测试（31 项，pytest + pytest-asyncio）
│   ├── test_builder.py           — TF-IDF 索引构建器（15 项）
│   ├── test_check_syntax.py      — 语法检查工具（6 项）
│   ├── test_gate.py              — 门禁管道（10 项）
│   └── fixtures/minimal_project/ — 测试用 HarmonyOS 最小项目骨架
│
├── pyproject.toml                — Python 包配置（hatchling, fastmcp>=3.0, jieba>=0.42）
├── .gitignore                    — 排除 index.json, .arkts-check/, __pycache__/, .venv/
└── CLAUDE.md                     — （由 Claude Code 自动生成）
```

---

## ArkAgent MCP Server

独立运行的 MCP Server，提供 80 文档知识库的索引化搜索 + 25 项代码验证 + 4 步门禁管道。

```bash
# 安装（项目根目录）
python3 -m venv .venv && source .venv/bin/activate && pip install -e .

# 启动 MCP Server（注册到 ~/.claude.json mcpServers 后 Claude Code 自动拉起）
python3 -m arkagent.cli mcp

# 重建搜索索引
python3 -m arkagent.cli rebuild-index

# 运行测试
python3 -m pytest tests/ -v
```

### 配置（环境变量）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ARKAGENT_KB_PATH` | `../docs`（相对 config.py） | 知识库根目录 |
| `ARKAGENT_INDEX_PATH` | `indexer/index.json`（相对 config.py） | TF-IDF 索引文件 |
| `ARKAGENT_RULES_PATH` | `~/.claude/rules/ecc/arkts` | ArkTS 规则目录 |

所有路径支持环境变量覆盖，无需修改 config.py。

### 11 个 MCP 工具（实际工具名带 `arkagent_` 前缀）

| 类别 | 工具 | 用途 |
|------|------|------|
| 知识 | `arkagent_search_docs` `arkagent_api_lookup` `arkagent_find_example` `arkagent_list_topics` | 80 文档 TF-IDF 搜索（6400 词条，141 API） |
| 验证 | `arkagent_validate_imports` `arkagent_check_syntax` `arkagent_check_state_mgmt` `arkagent_scan_project` | 代码质量检查（25 类语法 + 状态管理 + 导入合规） |
| 门禁 | `arkagent_gate_scan` `arkagent_gate_check` `arkagent_gate_status` | 4-step 硬门禁流水线（scan→gen→check→report） |

---

## 闭合链条

```
install-hooks.sh ──► Hook 部署
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
   PreToolUse                    PostToolUse
   阻断未扫描写入                 每次 .ets 写入后
         │                     静默 quick-check (9 项)
         ▼                           │
   scaffold.sh ──► Step 0 ──► Step 1 ──► Step 2 ──► Step 3
                      │           │          │          │
                  00-scan    01-gen     02-checked   自检报告
                                           │
                                     history.jsonl
                                           │
                                   health-report.sh
```

**链条闭合条件**：`bash scripts/install-hooks.sh` 之后，整个系统从 prompt 级提升到硬件级。LLM 无法跳过 Step 0、每次写入自动检查、错误跨会话累积。

## 硬门禁流水线

代码生成是**强制 4 步流水线**。每一步产出磁盘检查点，下一步物理验证检查点存在。

| 步骤 | 动作 | 产出 | 进入前提 |
|:----:|------|------|----------|
| 🆕 | `bash scripts/scaffold.sh` 一键建项目 → 自动执行 Step 0 | — | — |
| 0 | `arkagent_gate_scan` 扫描项目结构 | `.arkts-check/00-scan.json` | 无 |
| 1 | 校验 API → 生成代码 → 写入检查点 | `.arkts-check/01-generated.json` | `test -f 00-scan.json` |
| 2 | `bash scripts/self-check.sh` 全项目 25 项扫描 | `.arkts-check/02-checked.json` | `test -f 01-generated.json` |
| 3 | 读取 `status` 字段 → PASS 输出报告 / FAIL 回 Step 2 | 自检报告 | `test -f 02-checked.json` |

> **🔴 铁律**：写任何 .ets 前 `test -f .arkts-check/00-scan.json`。装了 Hook 后这一步是物理级的——PreToolUse 直接拒绝写入。

## self-check.sh — 25 项自动验证 + 3 种模式

| 模式 | 命令 | 用途 |
|------|------|------|
| 完整 | `bash scripts/self-check.sh .` | Step 2 正式检查，25 项全跑 + PITFALLS 锚点 |
| 快速 | `bash scripts/quick-check.sh .` | PostToolUse Hook 用，9 项关键 pass，PASS 静默 |
| 分层 | `bash scripts/self-check.sh . --project-rules .arkts-check/rules.json` | 带项目/用户自定义规则 |

### 规则分层

| 层级 | 来源 | 优先级 | 配置方式 |
|------|------|:--:|------|
| L1 内置 | `self-check.sh` 自带 25 项 | 最低 | 无需配置 |
| L2 项目 | `.arkts-check/rules.json` | 覆盖 L1 | `--project-rules` |
| L3 用户 | `~/.arkts-check/user-rules.json` | 最高 | `--user-rules` |

规则格式（`rules.json`）：`{"skip": [14, 19], "severity": {"18": "ignore"}, "custom": [...]}` — 参考 `scripts/rules-template.json`。

### 跨会话累积

每次 self-check 运行后追加 `.arkts-check/history.jsonl`（保留最近 50 次）。每 10 次提示执行 `bash scripts/health-report.sh` 查看趋势。Bucket-Seal 模式：积累 10 条 → 建议 LLM 生成健康摘要。

## 四层文件架构

**核心原则**：SKILL.md 在 session 启动时完整注入，其他文件通过 `Read offset=` 精准加载。

| 文件 | 加载方式 | 策略 |
|------|----------|------|
| SKILL.md | 始终全量注入 | ~300 行，只放规则/检查清单/指针 |
| REFERENCE.md | 按需 `Read offset=` | API 速查、编程规范、性能规则 |
| PITFALLS.md | 按需 `Read offset=` | 双索引（主题树 + 源索引），编译错误 + 最佳实践违反 |
| EXAMPLES.md | 按需 `Read offset=` | 44 个完整可编译示例 |

## 内容来源

- **[华为开发者官方文档](https://developer.huawei.com/consumer/cn/doc/)**——每项自动检测对应一条官方规则
- **个人开发实战踩坑**——DevEco Studio 逐行编译报错总结
- **实习课程笔记**——第三方 SDK、三层架构、自适应布局、组合手势
- **OpenHuman 借鉴**——潜意识循环 (quick-check)、Bucket-Seal (history.jsonl)、TokenJuice 三层规则 (L1/L2/L3)

## 迭代原则

1. 新增内容先判断"每次必查"还是"偶尔需要"，前者进 SKILL.md，后者进子文件
2. 每次给子文件加内容，**同时更新顶部索引**
3. SKILL.md 超过 300 行时，低频速查信息下沉到 REFERENCE.md
4. **每条自动检测对应一条官方规则或一个真实编译错误**——不做"可能有用的检查"
5. 新增 Pass → 同步更新 SKILL.md + PITFALLS.md + README
6. 代码改动后运行 `python3 -m pytest tests/ -v`，31 项全绿再提交
