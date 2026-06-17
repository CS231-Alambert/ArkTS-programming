---
name: harmonyos-arkts
description: Generate correct, compilable ArkTS code for HarmonyOS NEXT (API 12+) phone apps in DevEco Studio. Covers all scenarios: UI components, layouts, state management, hardware APIs, routing, permissions, module structure. Uses verified import paths and enforces ArkTS syntax restrictions to prevent compilation errors. Use when building HarmonyOS apps with ArkTS, generating pages/components, calling device APIs, implementing navigation, or fixing ArkTS compilation errors.
---

# HarmonyOS ArkTS 开发 (API 12+)

为 DevEco Studio 生成可直接编译运行的 ArkTS 代码。目标：手机应用、API 12+、HarmonyOS NEXT。

## ⛔ 强制门禁系统（HARD GATES）

本 Skill 的工作流通过**磁盘检查点文件**强制执行。每步产出文件，下一步读取文件——跳过即阻断。

| 步骤 | 产出检查点 | 前置条件 |
|------|----------|---------|
| Step 0 | `.arkts-check/00-scan.json` | — |
| Step 1 | 代码文件 + `.arkts-check/01-generated.json` | `00-scan.json` 必须存在 |
| Step 2 | `.arkts-check/02-checked.json` | `01-generated.json` 必须存在 |
| Step 3 | 自检报告（对话输出） | `02-checked.json` 必须存在 |

**🔴 铁律**: 写任何 `.ets` 文件前，先确认 `00-scan.json` 存在。不存在 → 立即停止，先执行 Step 0。

**门禁检查方法**: 写任何 `.ets` 文件前执行 `test -f .arkts-check/00-scan.json || echo "🔴 BLOCKED: Run Step 0 first"`。Step 2 前执行 `bash scripts/self-check.sh <项目根目录>`。

---

### Step 0 — 前置扫描（强制 · 生成前）

**门禁**: 无前置条件。此步骤是入口，始终允许执行。

> 🚀 **新项目？** `bash scripts/scaffold.sh <项目名> <com.example.app>` 一键生成 Stage 模型 + Navigation 骨架 + 自动执行本步骤。

扫描项目当前状态，并将结果写入检查点文件：

```bash
mkdir -p .arkts-check
python3 -c "
import json, os; root='$(pwd)'
data={
  'media': os.listdir(f'{root}/entry/src/main/resources/base/media/') if os.path.exists(f'{root}/entry/src/main/resources/base/media/') else [],
  'pages': json.load(open(f'{root}/entry/src/main/resources/base/profile/main_pages.json'))['src'],
  'components': os.listdir(f'{root}/entry/src/main/ets/components/') if os.path.exists(f'{root}/entry/src/main/ets/components/') else [],
  'hasInternetPermission': 'ohos.permission.INTERNET' in open(f'{root}/entry/src/main/module.json5').read() if os.path.exists(f'{root}/entry/src/main/module.json5') else False,
  'isThreeLayer': os.path.exists(f'{root}/common') and os.path.exists(f'{root}/features') and os.path.exists(f'{root}/products'),
  'timestamp': '$(date -Iseconds)'
}
json.dump(data, open(f'{root}/.arkts-check/00-scan.json','w'), ensure_ascii=False, indent=2)
print('✓ 00-scan.json written')
"
```

**必须记录到上下文**（生成代码时使用）:
- 可用媒体资源: `.arkts-check/00-scan.json` → `media` 字段
- 已注册页面: `.arkts-check/00-scan.json` → `pages` 字段
- 已有组件: `.arkts-check/00-scan.json` → `components` 字段
- 网络权限声明: `.arkts-check/00-scan.json` → `hasInternetPermission` 字段
- 是否三层架构: `.arkts-check/00-scan.json` → `isThreeLayer` 字段
- 需要时再读 `module.json5` 查看已声明权限

---

### Step 1 — 生成代码（强制 · 有门禁）

**门禁**: `test -f .arkts-check/00-scan.json` → 不存在则 STOP，回 Step 0。

1. **先读取参考文档**: 遇到不确定的组件/API 时，用 `grep` 查 REFERENCE.md 确认存在且签名正确
   ```bash
   grep -n "<组件名>" REFERENCE.md
   # 如果无结果 → 该 API 未文档化 → 使用已知安全的替代方案
   # 如果未读过 PITFALLS.md → 先读开头索引表，定位相关条目
   ```
2. 使用 Step 0 扫描到的可用资源（media/pages/components）作为上下文
3. 生成代码（一次性完成，不自修）
4. **写入检查点**: `python3 -c "import json; json.dump({'timestamp':'$(date -Iseconds)','files':[]},open('.arkts-check/01-generated.json','w'))"`

---

### Step 2 — 生成后自检（强制 · 自动化）

**门禁**: `test -f .arkts-check/01-generated.json` → 不存在则 STOP，回 Step 1。

**运行自动检查脚本**:
```bash
bash scripts/self-check.sh <项目根目录>
```

脚本自动扫描以下 25 项并输出 PASS/FAIL/⚠️WARNING：
- Pass 1-13: 基础语法检查（@ohos 旧导入、new Function、@State 冲突、router RouterMode、ForEach key、any/var 禁用、localhost 检测、INTERNET 权限、displayPriority 小数）
- Pass 14-17: 编程规范（要求级）— 多变量同行、NaN 比较、条件赋值、finally 控制流
- Pass 18、23: 状态管理性能 — @Prop→@ObjectLink 建议、循环内状态读取
- Pass 19-22、24-25: 组件规范 — fontSize 误用、Alignment.Left/Right、Shape 缺 stroke、@State 位置、Color 枚举、export default

**脚本失败时（exit code ≠ 0）**: 根据输出修复 → 重新运行直到 PASS → 才进入 Step 3。

---

### Step 2 手动补充检查

自动脚本未覆盖的手工检查项（完整清单见底部「生成代码检查清单」），核心关注：
- `$r('app.media.xxx')` 资源名对照 00-scan.json 存在
- `router.getParams()` 后判空
- TabContent 直接作为 Tabs 子节点
- `components/` 下用 `export default`
- 颜色优先 `'#XXXXXX'`；fontSize 仅用于文本组件
- 网络请求 URL 中使用 `localhost` → 提醒替换为本机 IP（模拟器不可达）
- 引入第三方 SDK（@pura/*）→ 确认 `EntryAbility.onCreate` 中有初始化调用
- 三层架构项目 → 检查 `oh-package.json5` 依赖方向为 products → features → common（不可反向）

---

### Step 3 — 报告自检结果

**门禁**: `test -f .arkts-check/02-checked.json` → 不存在则 STOP，回 Step 2 运行自动检查。

读取 `.arkts-check/02-checked.json` 的 `status` 字段：
- `PASS` → 输出报告
- `FAIL` → 根据错误输出修复 → 重新运行 `self-check.sh` 直到 PASS

输出自检报告：自动脚本结果 + 底部检查清单逐项状态（✅/⏭/❌）。

---

## 核心规则

### 限制

- 禁止 `any` / `unknown`。必须显式声明类型。
- 禁止 `var`。只用 `let` / `const`。
- 禁止动态属性：`obj[key]`、`delete obj.x`、运行时添加属性。
- 禁止 `eval`、`Symbol()`、`Function.bind`、`#private`（用 `private`）。
- 禁止结构化类型：无继承关系的类即使结构相同也不能互换。
- 可选参数必须在必选参数之后。
- 组件属性链（`.width()` 等）必须在子组件之前。
- `ForEach` 必须传第三个参数作为唯一 key 生成函数。
- `Object literal` 不能当类型用 —— 用 `interface` 或 `type`。

### 状态管理

**V1 规则**：`@State` 修改必须整体替换对象引用。深层嵌套用 `@Observed` + `@ObjectLink`。父→子单向 `@Prop`，双向 `@Link`（父传 `$var`）。

**V2 规则（API 12+ 推荐）**：组件用 `@ComponentV2`，内部状态 `@Local`，父传子 `@Param`，子传父 `@Event`，双向绑定 `this!!.var`，派生计算 `@Computed`。V1 和 V2 不可在同一组件混用。

**性能规则（官方最佳实践）**：
- 对象/class 类型用 `@ObjectLink` 替代 `@Prop`——`@Prop` 做深拷贝，`@ObjectLink` 引用共享
- 每个状态变量关联组件 ≤ 20 个，超出则提升到父组件
- 循环内避免直接读取 `@State`/`@Link`，先提取到局部变量
- 装饰器优先级：`@State` 系列 > `@Provide`+`@Consume` > `LocalStorage` > `AppStorage`
- 父子场景用 `@State`+`@Prop/@Link`，跨层级才用 `@Provide`+`@Consume`

> 完整 V2 装饰器表、迁移指南、常见错误 → [REFERENCE.md](REFERENCE.md)「状态管理（V2）」+ [PITFALLS.md](PITFALLS.md)「V2 状态管理常见错误」。
> 装饰器选择决策树 + 初始化约束矩阵 → [REFERENCE.md](REFERENCE.md)「状态管理性能规则」

### 导入路径（最高频错误来源）

API 12+ 优先用 `@kit.*` 格式：

| 模块 | 导入 |
|------|------|
| 路由/UI | `import { router } from '@kit.ArkUI'` |
| 网络/HTTP | `import { http } from '@kit.NetworkKit'` |
| 数据/首选项 | `import { preferences } from '@kit.ArkData'` |
| Ability/上下文 | `import { UIAbility, Want } from '@kit.AbilityKit'` |
| 文件 | `import { fileIo } from '@kit.CoreFileKit'` |
| 相机 | `import { camera } from '@kit.CameraKit'` |
| 传感器 | `import { sensor } from '@kit.SensorServiceKit'` |
| 多媒体 | `import { media } from '@kit.MediaKit'` |
| 通知 | `import { notificationManager } from '@kit.NotificationKit'` |
| 蓝牙 | `import { ble } from '@kit.ConnectivityKit'` |
| 权限控制 | `import { abilityAccessCtrl, Permissions } from '@kit.AbilityKit'` |
| 窗口 | `import { window } from '@kit.ArkUI'` |
| 日志 | `import { hilog } from '@kit.PerformanceAnalysisKit'` |

> 不确定时参考 [REFERENCE.md](REFERENCE.md) 完整导入路径表。

### 项目结构

```
entry/src/main/
├── ets/
│   ├── pages/           # 页面（必须在此目录或子目录）
│   ├── components/      # 可复用组件
│   ├── viewmodel/       # 业务逻辑+状态
│   ├── model/           # 数据实体定义
│   ├── services/        # API调用、网络请求
│   └── common/utils/    # 工具函数
├── resources/
│   └── base/
│       ├── element/     # string.json, color.json
│       ├── media/       # 图片资源
│       └── profile/
│           └── main_pages.json   # 页面路由注册（新增页必须手动加）
└── module.json5         # 权限声明
```

**组件导出规范**：可复用组件（`components/` 目录下）必须用 `export default` 导出，引用时用默认导入。代码示例 → [REFERENCE.md](REFERENCE.md)

### 页面注册与路由

> ⚠️ **Router 已停止功能更新**（页面栈 32 上限、不支持跨设备、深拷贝传参）。华为官方推荐 **Navigation + NavPathStack** 作为长期演进方案。[官方对比](https://developer.huawei.com/consumer/cn/doc/harmonyos-faqs-V5/faqs-arkui-299-V5)

**推荐方案：Navigation（API 12+）**

`resources/base/profile/route_map.json`:
```json
{ "routerMap": [{ "name": "DetailPage", "pageSourceFile": "src/main/ets/pages/Detail.ets", "buildFunction": "DetailBuilder" }] }
```
`module.json5` 声明: `"routerMap": "$profile:route_map"`。页面用 `@Builder` 导出，`NavPathStack.pushPathByName('DetailPage', params)` 跳转。

**旧方案：Router（仅维护旧项目）**

`main_pages.json`: `{ "src": ["pages/Index", "pages/Detail"] }`。跳转：`router.pushUrl({ url: 'pages/Detail' }, router.RouterMode.Standard).then(...)`。接收：`router.getParams()` 先判空。

> 完整 Navigation API（NavPathStack/NavDestination/路由表/跨模块路由解耦）→ [REFERENCE.md](REFERENCE.md)「Navigation 路由」

### 权限声明

`module.json5` 中声明：`"requestPermissions": [{ "name": "ohos.permission.INTERNET" }, ...]`。运行时申请：`abilityAccessCtrl.createAtManager().requestPermissionsFromUser(context, ['ohos.permission.CAMERA'])`。

> 完整 module.json5 模板 + 权限列表 → [REFERENCE.md](REFERENCE.md)「模块声明文件」

### 图形绘制组件 (Shape)

用于绘制2D图形（Circle/Ellipse/Line/Polyline/Polygon/Rect/Path），所有图形组件共享一套描边/填充属性（fill/stroke/strokeWidth等）。
**Shape 必须在代码中显式调用 `.stroke()` 才会在白色背景上可见**。

> 组件列表、共用属性、Path 命令速查 → [REFERENCE.md](REFERENCE.md)「图形绘制组件」。完整示例 → [EXAMPLES.md](EXAMPLES.md) §24。

### 标题栏组件 (TitleBar)

`ComposeTitleBar`（普通页）、`SelectTitleBar`（下拉切换）、`TabTitleBar`（仅一级页面）。
三者均从 `@kit.ArkUI` 导入，**不支持通用属性**（width/height 等不生效）。

> 完整参数、用法示例 → [REFERENCE.md](REFERENCE.md)「标题栏组件」+ [EXAMPLES.md](EXAMPLES.md) §25。

### 页签导航 (Tabs)

`TabContent` 必须直接作为 `Tabs` 子节点，不包裹在 Column/Row 中。`barPosition(BarPosition.End)` = 底部导航（仅一级页面）。

> 完整属性、Tabs+Grid 导航枢纽模式 → [REFERENCE.md](REFERENCE.md)「Tabs/TabContent 页签」+ [EXAMPLES.md](EXAMPLES.md) §12, §34, §36。

### 通用属性速查

尺寸（width/height/layoutWeight/constraintSize）、位置（position/offset）、边框、背景、透明度（opacity）、显隐（visibility）、变换（rotate/translate/scale）、裁剪（clip/clipShape）。

> 完整属性表 → [REFERENCE.md](REFERENCE.md)「通用属性速查」。常见误用 → [PITFALLS.md](PITFALLS.md)「通用属性常见错误」。

## 生成代码检查清单

按清单逐项核对，在 Step 3 报告中逐条输出。

- [ ] 无 `any` / `unknown` / `var`。必须显式声明类型。
- [ ] 导入路径用 `@kit.*` 格式（非 `@ohos.*`）。
- [ ] `ForEach` 有唯一 key 生成函数，且 key gen 中所有参数在函数体中使用（无 unused variable）。
- [ ] 对象属性修改用整体替换（不用 `.prop = `）。
- [ ] 新页面已在 `main_pages.json` 注册说明。
- [ ] 权限已在 `module.json5` 声明及运行时申请。
- [ ] 可选参数在必选参数之后。
- [ ] 组件属性链（`.width()` 等）在子组件之前。
- [ ] 文件路径大小写与实际一致。
- [ ] 标题栏组件（ComposeTitleBar/SelectTitleBar/TabTitleBar）不使用通用属性。
- [ ] Path commands 字符串用单引号，命令字母大写。
- [ ] `visibility(Visibility.None)` vs `Visibility.Hidden` 区分清楚。
- [ ] List/Grid/Scroll 显式声明 `width` 和 `height`（可用 `height(0) + layoutWeight(1)` 占满剩余空间）。
- [ ] `fontSize`/`fontColor`/`fontWeight` 只用于 Text/Span/Button/TextInput 等文本组件，不用于 Column/Row。
- [ ] 颜色除 Red/Blue/Black/White 外，优先用十六进制字符串 `'#XXXXXX'` 而非 `Color.Xxx`。
- [ ] `Alignment` / `Stack.alignContent` / `Column.align` 只使用 Start/End 语义，不用 Left/Right。
- [ ] `router.pushUrl` 有 `router.RouterMode.Standard` 第二参数。
- [ ] `router.pushUrl` 返回 Promise，用 `.then().catch()` 链式调用。
- [ ] `animateTo` 用 `this.getUIContext().animateTo()`，不用全局函数。
- [ ] `getUIContext()` 在同步代码中捕获，不在 setInterval/setTimeout/Promise 异步回调中直接调用。
- [ ] 同步方法（router.getParams/back、JSON.parse）用 try-catch；异步 Promise 方法（router.pushUrl、http.request）用 `.catch()`。
- [ ] `$r('app.media.xxx')` 资源名在 `resources/base/media/` 目录中存在。
- [ ] `components/` 下组件用 `export default` 导出。
- [ ] `router.getParams()` 后先判空再使用。
- [ ] TabContent 直接作为 Tabs 子节点，不包裹在 Column/Row 中。

### 子文件定位指南

三个子文件顶部已加入**完整索引表**，明确指出各章节的**行号**。需要时用 `Read offset=行号 limit=行数` 精准跳转，**切勿全量读取**：

| 文件 | 涵盖内容 | 用法 |
|------|----------|------|
| [REFERENCE.md](REFERENCE.md) | API速查、导入路径、属性全表 | 查具体组件/属性的正确语法 |
| [PITFALLS.md](PITFALLS.md) | 40+常见错误 | 按报错关键词或现象定位，取对应错误块 |
| [EXAMPLES.md](EXAMPLES.md) | 32个可编译运行的完整示例 | 按场景关键词定位示例号，读对应几段 |
