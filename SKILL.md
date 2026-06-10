---
name: harmonyos-arkts
description: Generate correct, compilable ArkTS code for HarmonyOS NEXT (API 12+) phone apps in DevEco Studio. Covers all scenarios: UI components, layouts, state management, hardware APIs, routing, permissions, module structure. Uses verified import paths and enforces ArkTS syntax restrictions to prevent compilation errors. Use when building HarmonyOS apps with ArkTS, generating pages/components, calling device APIs, implementing navigation, or fixing ArkTS compilation errors.
---

# HarmonyOS ArkTS 开发 (API 12+)

为 DevEco Studio 生成可直接编译运行的 ArkTS 代码。目标：手机应用、API 12+、HarmonyOS NEXT。

## 核心规则（必须遵守）

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

- `@State` 变量修改时必须整体替换对象引用，不能只改子属性。
- 深层嵌套用 `@Observed` + `@ObjectLink`。
- 父传子单向用 `@Prop`，双向用 `@Link`（父传 `$var`）。

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

**组件导出规范**：可复用组件（`components/` 目录下）必须用 `export default` 导出，引用时用默认导入：

```typescript
// components/MyComponent.ets
@Component
struct MyComponent { /* ... */ }
export default MyComponent

// pages/Index.ets
import MyComponent from '../components/MyComponent'
```

### 页面注册与路由

`resources/base/profile/main_pages.json`:
```json
{ "src": [ "pages/Index", "pages/Detail" ] }
```

跳转（路径不要以 `/` 开头，必须与注册完全一致。**API 12+ 返回 Promise，旧回调签名已废弃**）:
```typescript
import { router } from '@kit.ArkUI'
// ✅ Promise 链（新 API）
try {
  router.pushUrl({ url: 'pages/Detail', params: { id: 123 } },
    router.RouterMode.Standard)
    .then((): void => { /* 跳转成功 */ })
    .catch((err: Error): void => { console.error(err.message) })
} catch (err) {
  console.error(`路由异常: ${JSON.stringify(err)}`)
}
// ⚠ 旧三参数回调式 `(options, mode, callback)` 已废弃，勿用
```

**返回指定页面**（目标页必须在页面栈中存在）:
```typescript
router.back({ url: 'pages/Index', params: { from: 'Detail' } })
```

**返回前拦截询问框**:
```typescript
router.showAlertBeforeBackPage({ message: '确定要返回吗？' })
router.back()  // 会先弹框，用户确认后才返回
```

**清空页面栈**（栈满32页时释放内存）:
```typescript
router.clear()  // 清空后需重新 pushUrl 或 replaceUrl
```

> ⚠️ **架构提示**：`@ohos.router` 耦合度较高，**不适合大型项目的解耦开发**。对于中大型项目，推荐使用 **Navigation + NavPathStack** 组件进行路由管理（支持更灵活的路由栈操作和组件级复用）。小型项目/学习阶段使用 router 完全没问题。

**接收参数**:
```typescript
const params = router.getParams() as Record<string, Object>
// 注意：无参数时返回 undefined，必须先判空
```

### 权限声明

`module.json5`:
```json
{ "module": { "requestPermissions": [
  { "name": "ohos.permission.CAMERA" },
  { "name": "ohos.permission.INTERNET" }
]}}
```

运行时申请：
```typescript
import { abilityAccessCtrl, Permissions } from '@kit.AbilityKit'
const mgr = abilityAccessCtrl.createAtManager()
mgr.requestPermissionsFromUser(context, ['ohos.permission.CAMERA'])
```

### 图形绘制组件 (Shape)

用于绘制2D图形，所有图形组件共享一套描边/填充属性。

| 组件 | 用法 | 独有属性 |
|------|------|----------|
| `Circle` | `Circle({ width, height })` | - |
| `Ellipse` | `Ellipse({ width, height })` | - |
| `Line` | `Line()` | `.startPoint([x,y])`, `.endPoint([x,y])` |
| `Polyline` | `Polyline({ width, height })` | `.points([[x,y],...])`, `.strokeLineJoin()` |
| `Polygon` | `Polygon({ width, height })` | `.points([[x,y],...])` |
| `Rect` | `Rect({ width, height, radius })` | `.radiusWidth()`, `.radiusHeight()`, `.radius()` |
| `Path` | `Path({ width, height, commands })` | `.commands('M...')` 支持 M/L/H/V/C/S/Q/T/A/Z 命令 |

**共用属性（描边/填充）**：
```typescript
Circle({ width: 150, height: 150 })
  .fill(Color.Red)              // 填充颜色
  .fillOpacity(0.3)             // 填充透明度 [0,1]
  .stroke(Color.Blue)           // 边框颜色（不设则无边框）
  .strokeWidth(3)               // 边框宽度
  .strokeDashArray([10, 20])    // 虚线: [线段长, 间距长]
  .strokeDashOffset(0)          // 虚线起点偏移
  .strokeOpacity(0.8)           // 边框透明度 [0,1]
  .strokeLineCap(LineCapStyle.Round)     // 端点样式: Butt/Round/Square
  .strokeLineJoin(LineJoinStyle.Round)   // 拐角样式: Bevel/Miter/Round
```

**Path 命令速查**：
| 命令 | 含义 | 示例 |
|------|------|------|
| `M x y` | 移动到 | `M0 0` |
| `L x y` | 画线到 | `L50 50` |
| `H x` | 水平线 | `H100` |
| `V y` | 垂直线 | `V100` |
| `C x1 y1 x2 y2 x y` | 三次贝塞尔 | - |
| `Q x1 y1 x y` | 二次贝塞尔 | - |
| `A rx ry rot large sweep x y` | 椭圆弧 | - |
| `Z` | 闭合路径 | - |

> 完整代码示例见 [REFERENCE.md](REFERENCE.md)「图形绘制」章节和 [EXAMPLES.md](EXAMPLES.md) §24。

### 标题栏组件 (TitleBar)

导入：`import { ComposeTitleBar, SelectTitleBar, TabTitleBar } from '@kit.ArkUI'`

| 组件 | 适用场景 | 关键参数 |
|------|----------|----------|
| `ComposeTitleBar` | 普通页（一/二级） | `title`, `subtitle`, `item`(左侧头像), `menuItems`(右侧菜单) |
| `SelectTitleBar` | 下拉菜单切换页 | `selected`, `options`, `onSelected`, `hidesBackButton` |
| `TabTitleBar` | **仅一级页面**，页签切换 | `tabItems`, `swiperContent`(@BuilderParam) |

> **注意**：标题栏组件**不支持通用属性**（width/height 等不生效）。
> `TabTitleBar` 仅一级页面适用。完整示例见 [EXAMPLES.md](EXAMPLES.md) §25。

### 页签导航 (Tabs)

```typescript
Tabs() {
  TabContent() { PageA() }.tabBar('首页')       // 简写：纯文本
  TabContent() { PageB() }.tabBar('发现')       // TabContent 必须直接作为 Tabs 子级
  TabContent() { PageC() }.tabBar('我的')
}
.barPosition(BarPosition.End)   // End=底部导航，Start=顶部导航（默认）
```

| 属性 | 说明 |
|------|------|
| `barPosition(BarPosition.End)` | 底部导航（重要：仅一级页面能设 End） |
| `barPosition(BarPosition.Start)` | 顶部（默认值） |
| `scrollable(false)` | 禁止滑动切换 |
| `.onChange((index: number) => {})` | 页签切换回调 |
| `.tabBar(component)` | 自定义 TabBar（传入 @Builder 函数） |

> **组件复用模式**：每个 TabContent 放一个独立 `@Component`，从 `../components/` 导入，用 `export default` 导出。

**Tabs + Grid 导航枢纽模式**（常见于视频/电商 App 首页）：
```typescript
// 主页面：Tabs 框架
Tabs() {
  TabContent() { HomeTab() }.tabBar('首页')
  TabContent() { DiscoverTab() }.tabBar('发现')
  // ...
}
.barPosition(BarPosition.End)

// components/HomeTab.ets：Grid 图标导航 + Grid 内容列表
Grid() {
  ForEach(this.categories, (item: string, index: number) => {
    GridItem() {
      Column() { Image(...).width(50).height(50); Text(item) }
    }
    .onClick(() => {
      router.pushUrl({ url: 'pages/DetailPage', params: { title: item } })
    })
  }, (item: string) => item)
}
.columnsTemplate('1fr 1fr 1fr 1fr 1fr')  // 5列图标区
.width('100%').height(100)

Grid() {
  ForEach(this.dataList, (item: string) => {
    GridItem() {
      Column() { Image(...).width('100%').height(100); Text(item) }
    }
    .onClick(() => {
      router.pushUrl({ url: 'pages/Movie', params: { title: item } })
    })
  }, (item: string) => item)
}
.columnsTemplate('1fr 1fr')  // 2列内容列表
.width('100%').height(0).layoutWeight(1)  // 占满剩余空间
```
> 关键：Grid 必须显式设置宽高；ForEach 第三个参数必须是唯一 key 函数；路由 params 传参实现页面间的数据传递。

### 通用属性速查 (Universal Attributes)

| 类别 | 属性 | 说明 |
|------|------|------|
| **尺寸** | `width`, `height`, `size({width,height})` | 组件尺寸 |
| | `padding`, `margin` | 内外边距 |
| | `layoutWeight(n)` | 主轴权重分配（仅Row/Column/Flex），忽略自身尺寸 |
| | `constraintSize({minW,maxW,minH,maxH})` | 尺寸约束范围 |
| **位置** | `.direction(Direction.Rtl)` | 主轴布局方向（Ltr/Rtl/Auto），Column不生效 |
| | `.position({x,y})` | 绝对定位（相对父容器左上角），不占位 |
| | `.offset({x,y})` | 相对偏移（仅绘制偏移，不影响布局） |
| **布局** | `.aspectRatio(n)` | 宽高比约束（=width/height） |
| | `.displayPriority(n)` | 显示优先级（>1有值），空间不足时低优先级隐藏 |
| **边框** | `.border({width,color,radius,style})` | 统一边框，四边可不同 |
| | `.borderStyle()`, `.borderWidth()`, `.borderColor()`, `.borderRadius()` | 各边框属性单独设置 |
| **背景** | `.backgroundColor()` | 背景色 |
| | `.backgroundImage(url, ImageRepeat.XY)` | 背景图片+重复方式 |
| | `.backgroundImageSize({width,height})` | 背景图尺寸 |
| | `.backgroundImagePosition({x,y})` | 背景图位置 |
| | `.backgroundBlurStyle(BlurStyle.Thin)` | 背景模糊效果 |
| **透明度** | `.opacity(n)` | 不透明度[0,1]，子组件继承并叠加 |
| **显隐** | `.visibility(Visibility.None)` | Hidden=隐藏但占位；None=隐藏不占位 |
| **禁用** | `.enabled(false)` | 禁用交互（点击/触摸/焦点等不响应） |
| **变换** | `.rotate({x,y,z,angle,centerX,centerY})` | 3D旋转 |
| | `.translate({x,y,z})` | 3D平移 |
| | `.scale({x,y,z,centerX,centerY})` | 3D缩放 |
| **裁剪** | `.clip(true)` | 按父容器边缘裁剪子组件 |
| | `.clipShape(new Circle(...))` | 按指定形状裁剪 |
| | `.maskShape(new Rect(...).fill(Color.Gray))` | 按形状遮罩 |
| **多态** | `.stateStyles({normal,pressed,disabled,focused,clicked,selected})` | 不同交互状态下切换样式 |

> 更详细说明及常见误用见 [PITFALLS.md](PITFALLS.md)「通用属性常见错误」。

## 生成代码检查清单

- [ ] 无 `any` / `unknown` / `var`
- [ ] 导入路径用 `@kit.*` 格式
- [ ] `ForEach` 有唯一 key 生成函数
- [ ] 对象属性修改用整体替换（不用 `.prop = `）
- [ ] 新页面已在 `main_pages.json` 注册说明
- [ ] 权限已在 `module.json5` 声明及运行时申请
- [ ] 可选参数在必选参数之后
- [ ] 组件属性链在子组件之前
- [ ] 文件路径大小写与实际一致
- [ ] 标题栏组件（ComposeTitleBar/SelectTitleBar/TabTitleBar）不使用通用属性
- [ ] Path commands 字符串用单引号，命令字母大写
- [ ] `visibility(Visibility.None)` vs `Visibility.Hidden` 区分清楚
- [ ] List/Grid/Scroll 必须显式声明 `width` 和 `height`（可用 `height(0) + layoutWeight(1)` 占满剩余空间）
- [ ] `fontSize`/`fontColor`/`fontWeight` 只用于 Text/Span/Button/TextInput 等文本组件，不用于 Column/Row
- [ ] 颜色除 Red/Blue/Black/White 外，优先用十六进制字符串 `'#XXXXXX'` 而非 `Color.Xxx`（枚举不全）
- [ ] `Alignment` / `Stack.alignContent` / `Column.align` 只使用 Start/End 语义（TopStart/Center/BottomEnd 等），不用 Left/Right
- [ ] `router.pushUrl` 使用 Promise 链 `.then().catch()`，不用回调式签名
- [ ] `animateTo` 使用 `this.getUIContext().animateTo()`，不用全局函数（API 12+ 废弃）
- [ ] `getUIContext()` 在同步代码中捕获，不在 setInterval/setTimeout/Promise 等异步回调中直接调用
- [ ] 涉及 `router`、`http`、`JSON.parse` 的方法体用 `try-catch` 包裹
- [ ] `components/` 下组件用 `export default` 导出，引用用默认导入
- [ ] `router.getParams()` 后先判空再使用（无参数时返回 undefined）
- [ ] TabContent 组件放在 `../components/` 目录，用默认导入引入

### 子文件定位指南

三个子文件顶部已加入**完整索引表**，明确指出各章节的**行号**。需要时用 `Read offset=行号 limit=行数` 精准跳转，**切勿全量读取**：

| 文件 | 涵盖内容 | 用法 |
|------|----------|------|
| [REFERENCE.md](REFERENCE.md) | API速查、导入路径、属性全表 | 查具体组件/属性的正确语法 |
| [PITFALLS.md](PITFALLS.md) | 40+常见错误 | 按报错关键词或现象定位，取对应错误块 |
| [EXAMPLES.md](EXAMPLES.md) | 32个可编译运行的完整示例 | 按场景关键词定位示例号，读对应几段 |
