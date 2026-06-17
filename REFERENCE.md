# HarmonyOS ArkTS 参考手册 (API 12+)

> **快速定位**：用 Read offset=行号 精准读取。SKILL.md 已涵盖高频规则，此处为完整参考。

| 模块 | 行号 |
|------|------|
| @kit 导入路径表 | 3 |
| 装饰器速查 V1 (@Component/@State/@Prop/@Link等) | 30 |
| **状态管理 V2 (@ComponentV2/@Local/@Param/@Event等)** | **88** |
| 生命周期钩子 | 126 |
| 像素单位 (vp/fp/px/lpx) | 138 |
| 颜色格式 | 151 |
| Span / ImageSpan / ContainerSpan | 161 |
| Text 属性 | 194 |
| TextInput / TextArea 属性 | 214 |
| Button 属性 + 悬浮按钮 | 235 |
| Flex 弹性布局 | 260 |
| Stack 层叠布局 | 281 |
| GridRow / GridCol 栅格 | 297 |
| 资源引用 ($r/$rawfile/国际化) | 322 |
| 图形绘制 (Circle/Line/Path等) | 339 |
| 标题栏 (ComposeTitleBar等) | 414 |
| 通用属性速查 (尺寸/位置/边框/背景/变换等) | 469 |
| 模块声明文件 | 558 |
| 路由完整 API | 598 |
| Tabs/TabContent 页签 | 647 |
| Grid 网格 (非栅格) | 677 |
| EntryAbility 生命周期与 hilog | 710 |
| **HTTP 请求模组** | **887** |
| **第三方 SDK 速查** | **927** |
| **自适应布局属性** | **982** |
| **手势 API** | **1030** |
| **Navigation 路由（替代 Router）** | **1134** |
| **官方编程规范速查** | **1210** |
| **状态管理性能规则** | **1280** |

---

## 完整导入路径表

### @kit 模块（API 12+ 推荐）

| 类别 | 导入路径 | 常用导出 |
|------|----------|----------|
| **UI 框架** | `@kit.ArkUI` | `router`, `window`, `display` |
| **网络** | `@kit.NetworkKit` | `http`, `webSocket`, `netConnection` |
| **数据存储** | `@kit.ArkData` | `preferences`, `relationalStore`, `dataShare` |
| **Ability** | `@kit.AbilityKit` | `UIAbility`, `AbilityConstant`, `Want`, `abilityAccessCtrl`, `Permissions` |
| **文件** | `@kit.CoreFileKit` | `fileIo`, `fileUri`, `fileShare` |
| **相机** | `@kit.CameraKit` | `camera` |
| **传感器** | `@kit.SensorServiceKit` | `sensor` |
| **多媒体** | `@kit.MediaKit` | `media`, `audio`, `AVPlayer` |
| **图片处理** | `@kit.ImageKit` | `image`, `pixelMap` |
| **通知** | `@kit.NotificationKit` | `notificationManager`, `wantAgent` |
| **连接** | `@kit.ConnectivityKit` | `ble`, `wifiManager`, `nfc` |
| **电话** | `@kit.TelephonyKit` | `call`, `sms`, `sim` |
| **位置** | `@kit.GeoLocationManagerKit` | `geoLocationManager` |
| **账号** | `@kit.AccountKit` | `osAccount` |
| **安全** | `@kit.DeviceSecurityKit` | `deviceCertificate`, `cryptoFramework` |
| **DFX (日志)** | `@kit.PerformanceAnalysisKit` | `hiTraceMeter`, `hiAppEvent` |

> 旧版 `@ohos.*` 格式仍可用但已弃用。新项目统一用 `@kit.*`。

---

## 装饰器速查

### 组件定义
| 装饰器 | 用途 |
|--------|------|
| `@Entry` | 标记为页面入口（可独立路由） |
| `@Component` | 声明为可复用组件 |
| `@Preview` | DevEco Studio 预览 |
| `@Builder` | 定义可复用构建函数 |

### 状态管理（V1）
| 装饰器 | 用途 |
|--------|------|
| `@State` | 组件内部状态，变化触发 UI 更新 |
| `@Prop` | 父传子，单向，深拷贝 |
| `@Link` | 父传子，双向绑定，父用 `$var` |
| `@Provide` | 跨层级提供数据 |
| `@Consume` | 跨层级接收数据 |
| `@Observed` | 标记类为可观察 |
| `@ObjectLink` | 配合 `@Observed` 用，追踪对象属性变化 |
| `@StorageLink` | 绑定 AppStorage 键值 |
| `@StorageProp` | 单向绑定 AppStorage |

### 状态管理（V2 - API 12+ 推荐）

V2 是 NEXT 主推的状态管理方案，组件用 `@ComponentV2` 声明。

#### 装饰器速查

| 装饰器 | 对应 V1 | 数据流向 | 说明 |
|--------|---------|----------|------|
| `@Local` | `@State` | 组件内部 | 组件内部状态，变化触发 UI 更新。支持简单类型+对象+数组 |
| `@Param` | `@Prop` | 父→子（单向） | 接收父组件传入。**父传时无需 `$` 前缀**（不同于 V1 Link） |
| `@Param @Once` | — | 父→子（仅一次） | 仅初始化时同步一次，后续父变化不再更新子 |
| `@Event` | — | 子→父（回调） | 声明子组件可触发的事件回调，父通过 `(eventName)=>{...}` 接收 |
| `@Provider('key')` | `@Provide` | 祖先→后代 | 跨层级提供数据，后代用 `@Consumer('key')` 接收 |
| `@Consumer('key')` | `@Consume` | 后代←祖先 | 跨层级接收数据，必须与 `@Provider` 的 key 匹配 |
| `@Computed` | — | 派生计算 | 基于其他状态属性计算派生值，依赖变化时自动重算。**仅 V2 支持** |

#### V2 双向绑定 `!!` 操作符

V2 中双向绑定用 `!!`（不同于 V1 的 `$$`），用于 `@Param` 变量传递给子组件的 `@Param`：

```typescript
@ComponentV2
struct Parent {
  @Local text: string = ''
  build() { Column() { Child({ paramText: this!!.text }) } }
  //                      父传子双向绑定:  this!!.property
}

@ComponentV2
struct Child {
  @Param paramText: string = ''   // 子用 @Param 接收，父变化自动同步
  build() { Text(this.paramText) }
}
```

> **注意**: V2 的 `!!` 仅用于 `@Local` 的双向绑定场景。父→子单向传值直接用 `this.prop`（无需 `!!`）。

#### V2 vs V1 关键差异

| 特性 | V1 | V2 |
|------|----|----|
| 组件声明 | `@Component` | `@ComponentV2` |
| 内部状态 | `@State` | `@Local` |
| 父→子传参 | `@Prop` / `@Link($var)` | `@Param`（单向）/ `this!!.var`（双向） |
| 子→父回调 | 无原生支持 | `@Event` |
| 双向绑定符 | `$`（父传 Link） | `!!`（父传 Param 双向） |
| 派生计算 | 需手写 getter/refresh | `@Computed` 自动追踪 |
| 跨层级 | `@Provide/@Consume` | `@Provider('key')/@Consumer('key')` |
| 观察类 | `@Observed` + `@ObjectLink` | 无需 `@Observed`，`@Local` 自动深度追踪 |
| 重复组件 | `@Builder` / `@BuilderParam` | `@Repeat` 替代 ForEach（更高效） |

#### V2 完整页面模板

```typescript
@ComponentV2
struct MyPage {
  @Local count: number = 0
  @Local items: string[] = ['A', 'B', 'C']
  @Event onItemClick: (item: string) => void

  @Computed
  get totalChars(): number {
    return this.items.join('').length
  }

  build() {
    Column({ space: 12 }) {
      Text(`Count: ${this.count}`).fontSize(20)
      Text(`Total chars: ${this.totalChars}`)  // @Computed 自动更新
      Button('+1').onClick(() => { this.count++ })

      List() {
        ForEach(this.items, (item: string) => {
          ListItem() { Text(item) }
            .onClick(() => { this.onItemClick(item) })  // 触发 @Event
        }, (item: string) => item)
      }
    }
    .width('100%').height('100%')
  }
}
```

#### V2 迁移指南

从 V1 迁移到 V2 的步骤：
1. `@Component` → `@ComponentV2`
2. `@State` → `@Local`
3. `@Prop` → `@Param`
4. `@Link` (父传 `$var`) → `@Param` (父传 `this!!.var`)
5. `@Provide/@Consume` → `@Provider('key')/@Consumer('key')`
6. 子→父通信从 callback prop → `@Event`
7. 手动计算的派生值 → `@Computed`
8. `@Observed class` → 普通 class（`@Local` 自动深度追踪）

> V1 和 V2 **不能在同一组件中混用**，但可以在同一项目的不同组件中分别使用。

---

## 常用组件属性速查

### Text
```
Text('内容')
  .fontSize(16)           // number | Resource
  .fontColor('#333333')   // ResourceColor
  .fontWeight(FontWeight.Bold)  // 或 number (100-900)
  .maxLines(2)
  .textOverflow({ overflow: TextOverflow.Ellipsis })
  .textAlign(TextAlign.Center)
```

### Button
```
Button('确定')
  .type(ButtonType.Capsule)  // Normal | Capsule | Circle
  .fontColor(Color.White)
  .backgroundColor('#007DFF')
  .borderRadius(20)
  .onClick(() => { ... })
```

### TextInput（用 `$$` 双向绑定）
```
TextInput({ text: $$this.inputValue, placeholder: '请输入' })
  .width('100%')
  .type(InputType.Normal)
  .onChange((value: string) => { ... })
```

### Image
```
Image($r('app.media.logo'))      // 本地资源（推荐）
  .width(80).height(80)
Image('https://...')              // 网络图片（需 INTERNET 权限）
  .objectFit(ImageFit.Cover)
```

### List
```
List({ space: 8 }) {
  ForEach(this.dataArr, (item: DataItem) => {
    ListItem() { /* 内容 */ }
  }, (item: DataItem) => item.id.toString())  // 必须唯一 key
}
.divider({ strokeWidth: 1, color: '#E8E8E8' })
.onReachEnd(() => { /* 加载更多 */ })
```

### Column / Row
```
Column({ space: 12 }) { }
  .justifyContent(FlexAlign.Center)   // 主轴
  .alignItems(HorizontalAlign.Center) // Column 交叉轴

Row({ space: 10 }) { }
  .alignItems(VerticalAlign.Center)   // Row 交叉轴
```

---

## 生命周期钩子

| 钩子 | 触发时机 |
|------|----------|
| `aboutToAppear()` | 组件即将创建 |
| `aboutToDisappear()` | 组件即将销毁 |
| `onPageShow()` | 页面显示（仅 @Entry） |
| `onPageHide()` | 页面隐藏（仅 @Entry） |
| `onBackPress(): boolean` | 返回键按下，返回 true 拦截 |

---

## 像素单位

ArkUI 中数值默认单位为 **vp**，共4种单位：

| 单位 | 说明 | 适用场景 |
|------|------|----------|
| **vp** | 视口单位，屏幕密度无关。默认单位，推荐首选 | 所有布局/尺寸 |
| **fp** | 字体像素单位，随系统字体大小缩放 | 仅用于 `fontSize()` |
| **px** | 屏幕物理像素，不同设备差异大 | 精确控制（不推荐） |
| **lpx** | 逻辑像素，基于 designWidth(默认720) | 多端适配 |

> **关键**: 数值不带单位时默认为vp。`fontSize(16)` = 16fp。Path commands 内坐标单位是px（非vp）。

## 颜色格式

| 格式 | 示例 |
|------|------|
| 枚举 | `Color.Red`, `Color.Blue` (**仅约11种，见表下**) |
| 十六进制 | `'#FF0000'`, `'#FF0000FF'` (带alpha), `'#f00'` (简写) |
| rgb | `'rgb(255, 0, 0)'` |
| rgba | `'rgba(255, 0, 0, 0.5)'` (0=全透明, 1=不透明) |
| 数字 | `0xFF0000` (不常用) |

**Color 枚举可用值**（仅以下，没有 Purple/Brown/Cyan 等）：
`Red`, `Blue`, `Green`, `Yellow`, `Black`, `White`, `Gray`, `Grey`, `Orange`, `Pink`, `Transparent`

> **最佳实践**：除 Red/Blue/Black/White 外，统一用十六进制 `'#XXXXXX'`，避免枚举缺失。

## Span / ImageSpan / ContainerSpan

**Span**: Text子组件，行内文本片段。必须写在 `Text(){}` 内。
```
Text() {
  Span('红色').fontColor(Color.Red).fontSize(16)
  Span('蓝色').fontColor(Color.Blue).fontStyle(FontStyle.Italic)
    .decoration({ type: TextDecorationType.Underline, color: Color.Black })
}
```

**Span特有属性**: `.decoration()`, `.textCase(TextCase.UpperCase)` 大小写, `.fontStyle()`

**ImageSpan**: Text子组件，行内图片。
```
Text() {
  ImageSpan('https://example.com/icon.png')
    .width(40).height(40)
    .verticalAlign(ImageSpanAlignment.CENTER)
  Span('文本')
}
```

**ContainerSpan**: 包裹多个Span/ImageSpan统一设置背景色和圆角。
```
Text() {
  ContainerSpan() {
    ImageSpan('icon.png').width(40).height(40)
    Span('Hello World').fontColor(Color.White)
  }.textBackgroundStyle({ color: '#7F007DFF', radius: '12vp' })
}
```

## Text 属性速查

```
Text('内容')
  .fontSize(16)              // number|string, 默认16fp
  .fontColor(Color.Red)      // ResourceColor
  .fontWeight(FontWeight.Bold)  // 或 number 100-900
  .fontStyle(FontStyle.Italic)  // Normal|Italic
  .lineHeight(30)            // 行高
  .textAlign(TextAlign.Center)  // Start(默认)|Center|End
  .align(Alignment.Top)      // 垂直对齐: Top|Center(默认)|Bottom
  .textIndent(32)            // 首行缩进(vp)
  .maxLines(2)               // 最大行数
  .textOverflow({ overflow: TextOverflow.Ellipsis })  // None|Clip|Ellipsis|MARQUEE
  .decoration({              // 文本修饰线
    type: TextDecorationType.Underline,  // None|Underline|LineThrough|Overline
    color: Color.Red
  })
```

## TextInput 属性速查

```
TextInput({ placeholder: '请输入', text: $$this.inputValue })
  .type(InputType.Normal)    // 输入类型
  .width('100%')
  .height(50)
  .maxLength(11)             // 最大字符数
  .backgroundColor(Color.White)
  .borderRadius(8)
  .onChange((value: string) => {})
```

**InputType 枚举**: `Normal`, `Password`, `Email`, `Number`, `PhoneNumber`

**TextArea (多行)**:
```
TextArea({ text: '默认内容', placeholder: '请输入' })
  .width('100%').height(120)
```

## Button 属性速查

```
Button('标签', { type: ButtonType.Capsule, stateEffect: true })
  .fontSize(16).fontColor(Color.White)
  .backgroundColor('#007DFF')
  .borderRadius(20)
  .onClick(() => {})

// 自定义按钮（内嵌其他组件）
Button() {
  Image($r('app.media.icon')).width(20).height(20)
  Text('文字')
}
.backgroundColor(Color.White)

// 悬浮按钮（配合position固定在可滚动区域）
Button('+').width(50).height(50)
  .position({ x: 250, y: '90%' })
```

**ButtonType**: `Normal`, `Capsule`(胶囊), `Circle`(圆形)

**stateEffect**: `true`(默认，有点击效果) / `false`

## Flex 弹性布局

```
Flex({ direction: FlexDirection.Row, wrap: FlexWrap.Wrap, justifyContent: FlexAlign.Start, alignItems: ItemAlign.Center, alignContent: FlexAlign.Start }) { }
```

| 参数 | 枚举值 | 说明 |
|------|--------|------|
| `direction` | `FlexDirection.Row`(默认)/`Column`/`RowReverse`/`ColumnReverse` | 主轴方向 |
| `wrap` | `FlexWrap.NoWrap`(默认)/`Wrap`/`WrapReverse` | 是否换行 |
| `justifyContent` | `FlexAlign.Start`(默认)/`Center`/`End`/`SpaceBetween`/`SpaceAround`/`SpaceEvenly` | 主轴对齐 |
| `alignItems` | `ItemAlign.Start`/`Center`/`End`/`Stretch`(默认)/`Baseline` | 交叉轴对齐 |
| `alignContent` | 同 FlexAlign | 多行时交叉轴对齐（需wrap=Wrap才生效） |

**子元素 alignSelf**：覆盖父容器 alignItems。
```
Text('内容').alignSelf(ItemAlign.Start)
```

> **Previewer 陷阱**: Flex Column 内嵌套 Flex Column 会导致后续UI不渲染，内层改用 `Column()`。

## Stack 层叠布局

```
Stack({ alignContent: Alignment.TopStart }) {
  Column().width('90%').height('100%').backgroundColor('#ff58b87c')  // 底层
  Text('中间层').width('60%').height('60%').backgroundColor('#ffc3f6aa').zIndex(2)
  Button('顶层').width('30%').height('30%').backgroundColor('#ff8ff3eb').zIndex(3)
}
.width('100%').height(150)
```

| 参数 | 值 | 说明 |
|------|------|------|
| `alignContent` | `Alignment.TopStart`/`Top`/`TopEnd`/`Start`/`Center`/`End`/`BottomStart`/`Bottom`/`BottomEnd` | 九宫格对齐，默认Center |
| `zIndex` | number | 子元素层级，值大在上 |

## GridRow / GridCol 栅格布局

```
GridRow({ columns: { xs: 1, sm: 2, md: 4, lg: 6 }, gutter: { x: 12, y: 12 }, breakpoints: { value: ['320vp', '520vp', '840vp'] } }) {
  GridCol({ span: { xs: 1, sm: 1, md: 2, lg: 4 }, offset: { xs: 0, sm: 0, md: 1, lg: 2 } }) {
    Text('单元格内容')
  }
}
```

| GridRow 参数 | 说明 |
|------|------|
| `columns` | 总列数(默认12)，可响应式 `{xs:1, sm:2, md:4, lg:6}` 最多6断点 |
| `gutter` | 间距: number(统一) 或 `{x, y}`(分水平和垂直) |
| `breakpoints` | 自定义断点 `{value: ['320vp', '520vp', ...]}` 最多5个值(6断点) |
| `direction` | `GridRowDirection.Row`(默认)/`RowReverse` |

| GridCol 参数 | 说明 |
|------|------|
| `span` | 占用列数，可响应式 |
| `offset` | 相对前一个子组件的偏移列数 |
| `order` | 排列序号，小排前。不设order的在前，设order的按值排 |

> **⚠️ Previewer 不支持 GridRow/GridCol**，静默空白。开发时用 Flex wrap 替代验证布局。

## 资源引用规范

```
$r('app.string.xxx')     → resources/base/element/string.json
$r('app.color.xxx')      → resources/base/element/color.json
$r('app.float.xxx')      → resources/base/element/float.json
$r('app.media.xxx')      → resources/base/media/xxx.png (不加后缀名)
$r('app.media.xxx_animation')  → resources/base/media/
$rawfile('xxx.html')     → resources/rawfile/ (需加后缀名，可建子目录)
```

**国际化**: resources下创建语言限定词目录如 `en_US/`、`zh_CN/`，`base/`为默认兜底。

---

---

## 图形绘制组件 (Shape)

### Circle / Ellipse
```
Circle({ width: 150, height: 150 })           // 圆
Ellipse({ width: 200, height: 100 })          // 椭圆
```

### Line
```
Line()
  .width(200).height(150)
  .startPoint([0, 0])              // 起点（相对坐标）
  .endPoint([50, 100])             // 终点（相对坐标）
```

### Polyline（折线，不自动闭合）/ Polygon（多边形，自动闭合）
```
Polyline({ width: 100, height: 100 })
  .points([[0, 0], [20, 60], [100, 100]])
  .strokeLineJoin(LineJoinStyle.Round)  // 拐角样式
  .strokeLineCap(LineCapStyle.Round)    // 端点样式

Polygon({ width: 100, height: 100 })
  .points([[0, 0], [50, 100], [100, 0]])
```

### Rect（矩形）
```
Rect({ width: '90%', height: 80 })
  .radius([[40, 40], [20, 20], [40, 40], [20, 20]])  // 四角分别设置
  // 或 .radiusWidth(40).radiusHeight(20)             // 宽高分别设圆角
  // 或 .radius(20)                                   // 四角统一
```

### Path（路径）
```
Path()
  .width('210px').height('310px')
  .commands('M100 0 L200 240 L0 240 Z')   // 三角形
  .fillOpacity(0)
  .stroke(Color.Black).strokeWidth(3)
```

**Path 命令全集**:

| 命令 | 参数 | 说明 |
|------|------|------|
| `M x y` | (x y) | 移动到起始点 |
| `L x y` | (x y) | 画直线到 |
| `H x` | x | 水平线（y不变） |
| `V y` | y | 垂直线（x不变） |
| `C x1 y1 x2 y2 x y` | 控制点1, 控制点2, 终点 | 三次贝塞尔曲线 |
| `S x2 y2 x y` | 控制点2, 终点 | 平滑三次贝塞尔 |
| `Q x1 y1 x y` | 控制点, 终点 | 二次贝塞尔曲线 |
| `T x y` | (x y) | 平滑二次贝塞尔 |
| `A rx ry rot large sweep x y` | 椭圆弧参数 | 椭圆弧 |
| `Z` | 无 | 闭合当前子路径 |

### 图形共用属性速查（fill/stroke系列）

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `fill` | ResourceColor | Color.Black | 填充颜色 |
| `fillOpacity` | number | 1 | 填充透明度[0,1] |
| `stroke` | ResourceColor | - | 边框颜色（不设则无边框） |
| `strokeWidth` | number\|string | 1 | 边框宽度(vp)，不支持% |
| `strokeDashArray` | [number,number] | - | 虚线 [线段长, 间距] |
| `strokeDashOffset` | number | 0 | 虚线起点偏移 |
| `strokeOpacity` | number | 1 | 边框透明度[0,1] |
| `strokeLineCap` | LineCapStyle | Butt | 端点: Butt/Round/Square |
| `strokeLineJoin` | LineJoinStyle | Miter | 拐角: Bevel/Miter/Round |

---

## 标题栏组件 (TitleBar)

三者均从 `@kit.ArkUI` 导入：
```
import { ComposeTitleBar, SelectTitleBar, TabTitleBar } from '@kit.ArkUI'
```

**重要限制**: 标题栏组件**不支持通用属性**（width/height等）。

### ComposeTitleBar
普通标题栏，适用于一/二级页面。
```
ComposeTitleBar({
  title: "标题",                        // 必填
  subtitle: "副标题",                   // 可选
  item: { value: $r('app.media.avatar'), isEnabled: true, action: () => {} },  // 左侧头像(可选)
  menuItems: [
    { value: $r('app.media.icon'), isEnabled: true, action: () => { console.log("click") } }
  ]   // 右侧菜单(可选，最多显示数量由系统决定)
})
```

### SelectTitleBar
下拉菜单标题栏，支持页面间切换。一级/二级页面均可用。
```
SelectTitleBar({
  selected: 0,                          // 必填，当前选中索引
  options: [                            // 必填，下拉项
    { value: '全部' },
    { value: '本地' },
  ],
  onSelected: (index: number) => {},    // 选中回调
  hidesBackButton: false,               // 是否隐藏返回键
  subtitle: 'sub@example.com',          // 副标题
  menuItems: [...],                     // 右侧菜单（同ComposeTitleBar）
  badgeValue: 0                         // 新事件标记（≤0不显示，>99显示99+）
})
```

### TabTitleBar
页签型标题栏，**仅一级页面适用**。不支持通用属性。
```
TabTitleBar({
  tabItems: [                           // 必填，左侧页签列表
    { title: '页签1' },
    { title: '页签2', icon: $r('app.media.icon') },  // 可带图标
  ],
  menuItems: [...],                     // 右侧菜单
  swiperContent: this.componentBuilder  // 必填，@BuilderParam 页面内容
})
```
`TabTitleBarTabItem`: `title`(必填,ResourceStr) + `icon`(可选)

---

## 通用属性速查

### 尺寸设置
| 属性 | 说明 |
|------|------|
| `width(n)` / `height(n)` | 宽/高(vp)，缺省按内容 |
| `size({width, height})` | 同时设宽高 |
| `padding({left,right,top,bottom})` | 内边距 |
| `margin({left,right,top,bottom})` | 外边距 |
| `layoutWeight(n)` | 主轴权重分配（Row/Column/Flex），设置后忽略自身尺寸 |
| `constraintSize({minW,maxW,minH,maxH})` | 约束尺寸范围 |

### 位置设置
| 属性 | 说明 |
|------|------|
| `direction(Direction.Rtl)` | 主轴布局方向(Ltr/Rtl/Auto)，Row有效，Column不生效 |
| `position({x,y})` | 绝对定位（相对父容器左上角），在Row/Column/Flex中不占位 |
| `offset({x,y})` | 相对偏移（仅绘制偏移，不影响布局），相对自身左上角 |

### 布局约束
| 属性 | 说明 |
|------|------|
| `aspectRatio(n)` | 宽高比 = width/height。设宽+aspectRatio→自动算高；设高+aspectRatio→自动算宽 |
| `displayPriority(n)` | 显示优先级（>1有值），空间不足时先隐藏低优先级子组件 |

### 边框设置
| 属性 | 说明 |
|------|------|
| `border({width,color,radius,style})` | 统一边框(四边可分别设置) |
| `borderStyle(BorderStyle.Dashed)` | 线型: Dotted/Dashed/Solid |
| `borderWidth(5)` | 边框宽度 |
| `borderColor(0xAFEEEE)` | 边框颜色 |
| `borderRadius(10)` | 圆角半径 |

### 背景设置
| 属性 | 说明 |
|------|------|
| `backgroundColor(0xAFEEEE)` | 背景色 |
| `backgroundImage(url, ImageRepeat.XY)` | 背景图+重复(X/Y/XY/NoRepeat) |
| `backgroundImageSize({width,height})` | 背景图尺寸 |
| `backgroundImagePosition({x,y})` | 背景图位置 |
| `backgroundBlurStyle(BlurStyle.Thin)` | 材质模糊(Thin→Regular→Thick)+景深模糊(BACKGROUND_*)+组件模糊(COMPONENT_*) |

### 透明度
| 属性 | 说明 |
|------|------|
| `opacity(n)` | [0,1]，1=不透明。子组件继承+叠加（父0.1×子0.8=0.08） |

### 显隐控制
| 值 | 说明 |
|------|------|
| `Visibility.Visible` | 显示（默认） |
| `Visibility.Hidden` | 隐藏但占位 |
| `Visibility.None` | 隐藏且不占位 |

### 禁用控制
| 属性 | 说明 |
|------|------|
| `enabled(false)` | 禁止交互（点击/触摸/拖拽/按键/焦点/鼠标均不响应） |

### 图形变换
| 属性 | 核心参数 | 说明 |
|------|----------|------|
| `rotate({x,y,z,angle,centerX,centerY})` | x/y/z旋转轴, angle角度, centerX/Y旋转中心 | 3D旋转 |
| `translate({x,y,z})` | x/y/z平移距离 | 3D平移(z越近→放大) |
| `scale({x,y,z,centerX,centerY})` | x/y/z缩放倍数, centerX/Y缩放中心 | 3D缩放 |

### 形状裁剪
| 属性 | 说明 |
|------|------|
| `clip(true)` | 沿父容器边缘裁剪子组件溢出部分 |
| `clipShape(new Circle({...}))` | 按指定Shape裁剪 |
| `maskShape(new Rect({...}).fill(Color.Gray))` | 按Shape遮罩 |

### 多态样式 (stateStyles)
| 状态 | 说明 |
|------|------|
| `normal` | 无状态（默认） |
| `pressed` | 按下 |
| `disabled` | 禁用 |
| `focused` | 获焦 |
| `clicked` | 点击 |
| `selected` | 选中 |

用法：`.stateStyles({ normal: this.normalStyles, pressed: this.pressedStyles, disabled: this.disabledStyles })`
其中样式定义用 `@Styles` 函数。

---

## 模块声明文件速查

| 文件 | 作用 |
|------|------|
| `AppScope/app.json5` | 应用全局配置：bundleName、版本、图标 |
| `module.json5` | 模块配置：Ability、权限、设备类型 |
| `main_pages.json` | **页面路由清单，新增页面必须手动注册** |
| `build-profile.json5` | 模块构建配置 |
| `oh-package.json5` | 项目依赖管理 |

---

## 路由完整 API (@kit.ArkUI)

> 旧版 `@ohos.router` 已弃用，统一用 `import { router } from '@kit.ArkUI'`。

### pushUrl — 跳转并压栈

```
router.pushUrl(options: RouterOptions, mode?: RouterMode): Promise<void>
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `options.url` | `string` | 目标页面路径（与 main_pages.json 一致，不以 `/` 开头） |
| `options.params` | `Object` | 可选，传递到目标页的参数 |
| `mode` | `RouterMode` | `Standard`(默认,多实例) / `Single`(单实例,复用已存在) |

```
router.pushUrl({ url: 'pages/Detail', params: { id: 1 } }, router.RouterMode.Standard)
```

### replaceUrl — 替换当前页

```
router.replaceUrl(options: RouterOptions, mode?: RouterMode): Promise<void>
```

与 pushUrl 参数一致，但**销毁当前页**，无法返回。

### back — 返回

```
router.back(options?: RouterOptions): Promise<void>
```

| 场景 | 用法 |
|------|------|
| 返回上一页 | `router.back()` |
| 返回到指定页（须在栈中） | `router.back({ url: 'pages/Index' })` |
| 返回指定页 + 传参 | `router.back({ url: 'pages/Index', params: { result: 1 } })` |

### getParams — 获取路由参数

```
router.getParams(): Object | undefined
```

> **必须判空**：没有传递参数时返回 `undefined`。

### getLength — 获取页面栈深度

```
router.getLength(): string
```

返回值为 `'0'` ~ `'32'` 的字符串（不是 number）。

### showAlertBeforeBackPage — 返回前拦截

```
router.showAlertBeforeBackPage(options: { message: string }): void
```

调用后，下次 `router.back()` 会先弹确认框。只对紧接着的一次 back 生效。

```
router.showAlertBeforeBackPage({ message: '确定要离开吗？' })
router.back()  // ← 弹框，用户确认后才执行返回
```

### clear — 清空页面栈

```
router.clear(): void
```

清空整个页面栈（最大容量 32 页），之后需重新 pushUrl/replaceUrl。

---

## Tabs / TabContent 页签

```
Tabs({ index?: number, controller?: TabsController }) {
  TabContent() { /* 内容1 */ }.tabBar('标签1')
  TabContent() { /* 内容2 */ }.tabBar(this.TabBarBuilder2)
}
```

| Tabs 属性 | 说明 |
|-----------|------|
| `barPosition(BarPosition.End)` | **底部导航**（Start=顶部, 默认; End=底部） |
| `barPosition(BarPosition.Start)` | 顶部页签 |
| `scrollable(false)` | 禁止左右滑动切换 |
| `barMode(BarMode.Fixed)` | 页签栏模式：`Fixed`(固定,默认) / `Scrollable`(可滚动) |
| `barWidth(n)` / `barHeight(n)` | 页签栏宽/高 |
| `animationDuration(n)` | 切换动画时长(ms)，默认200 |
| `onChange((index: number) => {})` | 页签切换回调 |

| TabContent 属性 | 说明 |
|-----------------|------|
| `.tabBar(string)` | 页签标题（纯文字简写） |
| `.tabBar(Component)` | 页签标题（自定义组件/Builder） |
| `.tabBar(this.myBuilder)` | 传入 @Builder 函数 |

> **约束**：TabContent 必须直接作为 Tabs 的子节点，不能嵌套在其他容器中。

---

## Grid 网格组件（非栅格）

与 GridRow/GridCol（响应式栅格）不同，`Grid` 是固定列/行布局的容器组件：

```
Grid() {
  GridItem() { Text('A') }
  GridItem() { Text('B') }
}
```

| Grid 属性 | 说明 |
|-----------|------|
| `columnsTemplate('1fr 1fr 1fr')` | 列模板：fr=等分，可混用 `'100vp 1fr 1fr'` |
| `rowsTemplate('1fr 1fr')` | 行模板：同上 |
| `columnsGap(n)` / `rowsGap(n)` | 列/行间距 |
| `scrollBar(BarState.Off)` | 滚动条状态 |

| GridItem 属性 | 说明 |
|---------------|------|
| 支持所有通用属性 | 尤其常用 `.onClick()` + `router.pushUrl()` 实现导航网格 |

> **约束**：Grid 必须显式声明 `width` 和 `height`（或 `height(0) + layoutWeight(1)`）。

---

## EntryAbility 生命周期与 hilog

### EntryAbility 完整模板

```typescript
import { AbilityConstant, ConfigurationConstant, UIAbility, Want } from '@kit.AbilityKit'
import { hilog } from '@kit.PerformanceAnalysisKit'
import { window } from '@kit.ArkUI'

const DOMAIN: number = 0x0000

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    try {
      this.context.getApplicationContext().setColorMode(
        ConfigurationConstant.ColorMode.COLOR_MODE_NOT_SET
      )
    } catch (err) {
      hilog.error(DOMAIN, 'testTag', 'Failed to setColorMode. Cause: %{public}s',
        JSON.stringify(err))
    }
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onCreate')
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index', (err) => {
      if (err.code) {
        hilog.error(DOMAIN, 'testTag', 'Failed to load content. Cause: %{public}s',
          JSON.stringify(err))
        return
      }
      hilog.info(DOMAIN, 'testTag', 'Succeeded in loading the content.')
    })
  }

  onDestroy(): void { /* 释放资源 */ }
  onForeground(): void { /* 应用回到前台 */ }
  onBackground(): void { /* 应用进入后台 */ }
  onWindowStageDestroy(): void { /* 窗口销毁 */ }
}
```

### hilog 日志

| 级别 | 方法 | 格式化占位符 |
|------|------|-------------|
| info | `hilog.info(domain, tag, format, ...args)` | `%{public}s` (string), `%{public}d` (number) |
| warn | `hilog.warn(domain, tag, format, ...args)` | 同上 |
| error | `hilog.error(domain, tag, format, ...args)` | 同上 |
| debug | `hilog.debug(domain, tag, format, ...args)` | 同上 |

> **domain**：十六进制常量 `0x0000`~`0xFFFF`，用于日志分类过滤。
> **私有数据占位符**：`%{private}s`，正式版不输出内容。

### ConfigurationConstant.ColorMode

| 值 | 说明 |
|----|------|
| `COLOR_MODE_NOT_SET` | 跟随系统（推荐） |
| `COLOR_MODE_DARK` | 强制深色模式 |
| `COLOR_MODE_LIGHT` | 强制浅色模式 |

---

## HTTP 请求模组

### 导入

```typescript
import { http } from '@kit.NetworkKit';
```

### 创建请求 + GET

```typescript
const httpReq = http.createHttp();  // 建议在组件中复用实例

httpReq.request(
  'http://192.168.1.100:9988/products',  // URL（模拟器不能用 localhost）
  { method: http.RequestMethod.GET }
).then((res: http.HttpResponse) => {
  const data: string = res.result as string;
  const parsed = JSON.parse(data);
}).catch((err: Error) => {
  console.error('HTTP GET failed:', err.message);
});
```

### POST (JSON body)

```typescript
httpReq.request(
  'http://192.168.1.100:9988/products',
  {
    method: http.RequestMethod.POST,
    header: { 'Content-Type': 'application/json' },
    extraData: JSON.stringify({ name: 'Product A', price: 99 })
  }
).then((res) => { /* ... */ }).catch((err: Error) => { /* ... */ });
```

### json-server 模拟后端

```bash
# 安装（全局一次）
npm install -g json-server@0.17.4

# 准备数据文件 db.json
echo '{"products": [{"id":1,"name":"P1","price":99}]}' > db.json

# 启动（必须用本机 IP，模拟器才可达）
json-server --watch db.json --port 9988 --host 192.168.x.x
```

| HTTP 方法 | 对应 json-server 路由 |
|-----------|----------------------|
| GET | `/products` 列表, `/products/1` 单条 |
| POST | `/products` 新增 |
| PUT | `/products/1` 全量更新 |
| PATCH | `/products/1` 部分更新 |
| DELETE | `/products/1` 删除 |

---

## 第三方 SDK 速查

### @pura/harmony-utils

常用工具类（50+ 工具类，覆盖设备/存储/多媒体/网络/加密/UI/日志）：

| 模块 | 功能 | 导入 |
|------|------|------|
| DeviceUtil | 设备信息（品牌/型号/系统版本） | `import { DeviceUtil } from '@pura/harmony-utils'` |
| PreferencesUtil | 首选项存储 | `import { PreferencesUtil } from '@pura/harmony-utils'` |
| NetworkUtil | 网络状态检测 | `import { NetworkUtil } from '@pura/harmony-utils'` |
| LogUtil | 日志分级输出 | `import { LogUtil } from '@pura/harmony-utils'` |
| DateUtil | 日期格式化/时间戳 | `import { DateUtil } from '@pura/harmony-utils'` |
| ToastUtil | 轻量提示 | `import { ToastUtil } from '@pura/harmony-utils'` |

### @pura/picker_utils

```typescript
import { PickerUtil, PhotoHelper, ScanUtil } from '@pura/picker_utils';

// 相机（简易版，默认后置拍照）
PickerUtil.cameraEasy().then((uri: string) => console.log(uri));

// 相机（完整配置：前置/后置 + 照片/视频）
PickerUtil.camera({ mediaTypes: [...], cameraPosition: camera.CameraPosition.CAMERA_POSITION_BACK });

// 单选图片
PickerUtil.selectPhoto().then((uris: string[]) => console.log(uris));

// 多选图片+视频
PhotoHelper.selectEasy({ maxSelectNumber: 12, MIMEType: photoAccessHelper.PhotoViewMIMETypes.IMAGE_VIDEO_TYPE });

// 扫码
ScanUtil.startScanForResult().then((result: object) => console.log(JSON.stringify(result)));
```

### @pura/harmony-dialog

常用弹窗 API（均从 `@pura/harmony-dialog` 导入 `DialogHelper`）：

| 方法 | 弹窗类型 |
|------|---------|
| `showAlertDialog({...})` | 确认对话框（双按钮） |
| `showConfirmDialog({...})` | 信息确认（带 checkbox） |
| `showTipsDialog({...})` | 提示框（可带图标） |
| `showSelectDialog({...})` | 单选列表 |
| `showTextInputDialog({...})` | 单行文本输入 |
| `showCustomContentDialog({...})` | 自定义内容区 |
| `showBottomSheetDialog({...})` | 底部动作面板 |
| `showTextPickerDialog({...})` | 选择器弹框 |
| `showDatePickerDialog({...})` | 日期选择器 |
| `showLoadingProgress({...})` | 进度条加载 |
| `showToast(...)` / `showToastTip({...})` | 吐司/带图标吐司 |

### 初始化模板

```typescript
// EntryAbility.ts
import { AppUtil } from '@pura/harmony-utils';
import { DialogHelper } from '@pura/harmony-dialog';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam) {
    AppUtil.init(this.context);
    DialogHelper.setDefaultConfig((config) => {
      config.uiAbilityContext = this.context;
    });
  }
}
```

---

## 自适应布局属性

### 7 种能力速查

| 能力 | 属性/方式 | 适用容器 |
|------|----------|---------|
| 拉伸 | `flexGrow(n)` / `flexShrink(n)` | Row, Column, Flex |
| 均分 | `justifyContent(FlexAlign.SpaceEvenly)` | Row, Column, Flex |
| 占比 | `layoutWeight(n)` | Row, Column |
| 缩放 | `aspectRatio(n)` 保持宽高比 | 任意 |
| 延伸 | `List` 或 `Scroll` + 水平方向 | — |
| 隐藏 | `displayPriority(n)` 整数越大越优先 | Row, Column |
| 折行 | `Flex({ wrap: FlexWrap.Wrap })` | **仅 Flex** |

### displayPriority 详解

```
displayPriority(1)   → 最低优先级（空间不足时先隐藏）
displayPriority(2)   → 中等优先级
displayPriority(3)   → 高优先级（最后被隐藏）

[x, x+1) 区间内值视为同优先级：
displayPriority(1.0) 与 displayPriority(1.9) 效果相同！
```

### Blank 组件

自动填充容器剩余空间，仅在 Row/Column/Flex 中生效：

```typescript
Row() {
  Text("左侧固定")
  Blank()  // 自动占据剩余空间
  Toggle({ type: ToggleType.Switch })
}
```

### FlexWrap 换行

```typescript
Flex({ wrap: FlexWrap.Wrap }) {  // 空间不足时自动换行
  ForEach(items, (item: string) => {
    Text(item).width(100).height(100).margin(12)
  })
}
.width('100%')
```

---

## 手势 API

### PinchGesture（双指缩放）

```typescript
@State scaleValue: number = 1;

.gesture(
  PinchGesture()
    .onActionUpdate((event: PinchGestureEvent) => {
      this.scaleValue = event.scale;
    })
)
```

### PanGesture（单指拖拽）

```typescript
@State offsetX: number = 0;
@State offsetY: number = 0;

.gesture(
  PanGesture()
    .onActionUpdate((event: PanGestureEvent) => {
      this.offsetX += event.offsetX;
      this.offsetY += event.offsetY;
    })
)
```

### GestureGroup（组合手势）

```typescript
.gesture(
  GestureGroup(GestureMode.Exclusive,  // Exclusive=互斥, Parallel=并行, Sequence=顺序
    PinchGesture()
      .onActionUpdate((event: PinchGestureEvent) => {
        this.scaleValue = event.scale;
      }),
    PanGesture()
      .onActionUpdate((event: PanGestureEvent) => {
        this.offsetX += event.offsetX / this.scaleValue;   // 除以缩放因子
        this.offsetY += event.offsetY / this.scaleValue;
      })
  )
)
```

### 手势模式枚举

| GestureMode | 行为 |
|-------------|------|
| `GestureMode.Exclusive` | 互斥，同一时间只识别一个手势 |
| `GestureMode.Parallel` | 并行，多个手势同时识别 |
| `GestureMode.Sequence` | 顺序，按注册顺序依次识别 |

---

## Navigation 路由（替代 Router）

> ⚠️ Router 已停止功能更新。Navigation 是华为官方唯一长期演进推荐方案。
> 对比：Navigation 无路由数限制、支持跨设备、引用传参、路由栈操作、路由拦截、共享元素动画。

### NavPathStack 核心 API

| API | 用途 |
|-----|------|
| `pushPath(info)` / `pushPathByName(name, param)` | 跳转 |
| `pop()` / `popToName(name)` / `popToIndex(index)` | 返回 |
| `replacePath(info)` / `replacePathByName(name, param)` | 替换当前页 |
| `clear()` | 清空全部栈 |
| `moveToTop(name)` / `moveIndexToTop(index)` | 栈操作 |
| `getParamByIndex(index)` / `getParamByName(name)` | 获取参数 |
| `setInterception(predicate)` | 路由拦截（如登录检查） |

### 路由表配置

`resources/base/profile/route_map.json`:
```json
{
  "routerMap": [
    {
      "name": "MainPage",
      "pageSourceFile": "src/main/ets/pages/MainPage.ets",
      "buildFunction": "MainPageBuilder"
    }
  ]
}
```

`module.json5` 中声明: `"routerMap": "$profile:route_map"`

### 基本用法

```typescript
// 入口页面 (Index.ets)
@Entry
@Component
struct Index {
  @Provide('pageStack') pageStack: NavPathStack = new NavPathStack()

  build() {
    Navigation(this.pageStack) {
      Column() {
        Button('去详情').onClick(() => {
          this.pageStack.pushPathByName('DetailPage', { id: 123 })
        })
      }
    }
    .navBarWidth('100%')
    .mode(NavigationMode.Stack)
  }
}

// 子页面 (Detail.ets)
@Builder
export function DetailBuilder() {
  DetailPage()
}

@Component
struct DetailPage {
  @Consume('pageStack') pageStack: NavPathStack;

  build() {
    NavDestination() {
      Column() { Text('详情页') }
    }
    .title('详情')
  }
}
```

### 多模块路由解耦（官方最佳实践）

跨 HAR/HSP 模块跳转时，抽取独立 `RouterModule` 避免循环依赖：

```typescript
// common/router/RouterModule.ets
export class RouterModule {
  static builderMap: Map<string, WrappedBuilder<[object]>> = new Map()
  static routerMap: Map<string, NavPathStack> = new Map()

  static registerBuilder(name: string, builder: WrappedBuilder<[object]>): void { ... }
  static createRouter(name: string, router: NavPathStack): void { ... }
}
```

依赖关系：Entry.hap → (A.har, B.har) → RouterModule.har（模块间完全解耦）

---

## 官方编程规范速查

来源：[ArkTS 编程规范](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V13/arkts-coding-style-guide-V13)

### 要求级（原则上必须遵从）

| # | 规则 | 正例 | 反例 |
|----|------|------|------|
| 1 | 每行只声明一个变量 | `let a = 1;\nlet b = 2;` | `let a = 1, b = 2;` |
| 2 | NaN 必须用 `Number.isNaN()` | `Number.isNaN(x)` | `x == NaN` |
| 3 | 条件表达式禁止赋值 | `if (isFoo)` | `if (isFoo = false)` |
| 4 | finally 禁止 return/break/continue/throw | `finally { cleanup() }` | `finally { return 3 }` |
| 5 | 数组遍历优先 Array 方法 | `arr.map(fn)` | `for (let i=0;...)` |

### 建议级（最佳实践）

| # | 规则 |
|---|------|
| 6 | 类名/枚举名/命名空间 `UpperCamelCase` |
| 7 | 变量名/方法名 `lowerCamelCase`，常量全大写+下划线 |
| 8 | 布尔变量用 `is`/`has`/`can` 前缀 |
| 9 | 自定义组件 `UpperCamelCase`，@Builder 函数 `lowerCamelCase` |
| 10 | 条件/循环语句必须使用大括号 `{}` |
| 11 | 字符串使用单引号 |
| 12 | 使用空格缩进（2 空格），禁止 Tab |
| 13 | 每行不超过 120 字符 |
| 14 | 对象属性超 4 个时每行一个 |

### 高性能编程实践

| # | 实践 |
|---|------|
| 15 | 使用 `const` 声明不变变量（基础+引用类型） |
| 16 | 循环中提取不变量到外部 |
| 17 | 避免使用 `ESObject`（仅跨语言调用场景用） |
| 18 | 纯数值计算优先用 TypedArray (`Int8Array` 等) |
| 19 | 减少全局属性查找，循环中缓存为局部变量 |
| 20 | 使用函数参数传递代替闭包 |

---

## 状态管理性能规则

来源：[状态管理最佳实践](https://developer.huawei.com/consumer/cn/doc/best-practices-V5/bpta-status-management-V5) + [CodeLinter @performance](https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V5/ide_hp-arkui-use-object-link-to-replace-prop-V5)

### 装饰器选择决策树

```
需要观察嵌套对象深层属性？
  ├── 是 → @ObservedV2 + @Trace + @ComponentV2 + @Local/@Param
  └── 否 → 复杂对象/class/数组？
            ├── 是 → @State + @ObjectLink（子组件不修改时）或 @Link（需双向同步时）
            └── 否 → @State + @Prop

父子场景 or 跨层级场景？
  ├── 父子 → @State + @Prop/@Link/@ObjectLink（开销 < @Provide+@Consume）
  └── 跨层级（多级传递）→ @Provider + @Consumer
```

### 初始化约束矩阵

| 装饰器 | 本地初始化 | 构造函数初始化 | 说明 |
|--------|:--------:|:--------:|------|
| `@State` | ✅ 必须 | 可选 | 本地值可被构造函数覆盖 |
| `@Prop` | ❌ 禁止 | ✅ 必须 | 仅能通过构造函数 |
| `@Link` | ❌ 禁止 | ✅ 必须 | 仅能通过构造函数 |
| `@ObjectLink` | ❌ 禁止 | ✅ 必须 | 仅能通过构造函数 |
| `@Provide` | ✅ 必须 | 可选 | — |
| `@Consume` | ❌ 禁止 | ❌ 禁止 | 不能直接初始化 |
| `@StorageLink` | ✅ 必须 | ❌ 禁止 | 不可由父组件传入 |
| `@StorageProp` | ✅ 必须 | ❌ 禁止 | 不可由父组件传入 |

### 性能关键数字

- 每个状态变量关联组件 **≤ 20 个**，超出则提升到父组件
- `@Prop` 嵌套超过 **5 层** 时深拷贝开销显著，改用 `@ObjectLink`
- 装饰器开销优先级：`@State` 系列 < `@Provide+@Consume` < `LocalStorage` < `AppStorage`
