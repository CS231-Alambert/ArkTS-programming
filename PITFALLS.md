# ArkTS 常见错误与修复

> **快速定位**：用关键词搜索或 Read offset=行号 精准读取错误类别。按"报错关键词+现象"定位。
> ⚠️ 行号为近似值，文件内容增删后会偏移——优先用关键词搜索定位。

| 错误类别 | 行号 |
|----------|------|
| any/unknown 类型禁止 | 57 |
| 动态属性访问 obj[key] | 72 |
| var 声明禁止 | 89 |
| 结构化类型混用 | 101 |
| 可选参数位置 | 119 |
| @State 直接改子属性 | 135 |
| 深层嵌套不更新 (@Observed) | 149 |
| ForEach 缺 key | 178 |
| ForEach key gen 参数未使用 | 188 |
| 组件属性链顺序 | 192 |
| @State 写在 struct 外 | 208 |
| **List/Grid/Scroll 缺显式宽高** | 223 |
| **非文本组件使用 fontSize 等** | 240 |
| **函数抛异常未 try-catch** | 260 |
| 导入路径(@kit vs @ohos) | 291 |
| **router.pushUrl 回调签名废弃** | 319 |
| **animateTo 全局函数废弃** | 341 |
| **getUIContext() 异步回调失效** | 360 |
| 文件路径大小写 | 326 |
| 页面未注册 main_pages | 340 |
| 网络权限未声明 | 357 |
| 运行时权限申请 | 368 |
| JSON.parse 大整数 | 385 |
| Shape 无 stroke 不显示 | 403 |
| Path 坐标单位 | 422 |
| **Color.xxx 枚举不存在** | 436 |
| **Alignment 用 Left/Right 而非 Start/End** | **508** |
| Polyline vs Polygon 混淆 | 455 |
| 标题栏用通用属性 | 470 |
| TabTitleBar 用于二级页 | 485 |
| layoutWeight 容器限制 | 499 |
| position vs offset | 516 |
| Visibility.Hidden vs None | 529 |
| opacity 父子叠加 | 544 |
| rotate 变换中心 | 556 |
| enabled 与 stateStyles 联动 | 573 |
| blur vs backgroundBlurStyle | 588 |
| Span 在 Text 外 | 598 |
| Text 内容被 Span 覆盖 | 611 |
| ContainerSpan 属性限制 | 621 |
| TextInput $$ 双向绑定 | 626 |
| 像素单位混用 | 639 |
| Image 资源引用($r vs $rawfile) | 653 |
| 废弃 @system 导入 | 659 |
| Button 自定义语法 | 665 |
| Previewer: GridRow/GridCol | 681 |
| Previewer: Flex 嵌套 Flex | 706 |
| Previewer: @Builder 嵌套 | 746 |
| **router.getParams() undefined** | **860** |
| **router.back 目标页不在栈** | **881** |
| **页面栈超 32 页** | **899** |
| **TabContent 非 Tabs 直接子节点** | **917** |
| **Grid 缺显式宽高** | **933** |
| **V2 状态管理常见错误** | **1044** |
| **export default 缺失** | **950** |
| 快速排查流程 | 971 |
| **三层架构依赖错误** | **1276** |
| **网络请求错误** | **1320** |
| **第三方 SDK 错误** | **1375** |
| **自适应布局+手势错误** | **1435** |

---

## 类型系统错误

### ❌ `any` 类型
```
报错: "arkts-no-any-unknown"
原因: ArkTS 禁止 any/unknown，AOT 编译器必须在编译期确定类型
```
```typescript
// ❌ 错误
let data: any = getData()
let val: unknown = someValue

// ✅ 正确
interface ApiResponse { code: number; data: string[] }
let data: ApiResponse = getData() as ApiResponse
```

### ❌ 动态属性访问
```
报错: 编译失败或运行时 undefined
原因: 禁止 obj[key] 动态索引，对象布局编译期固定
```
```typescript
// ❌ 错误
user['name'] = '张三'
let key = 'age'; console.log(user[key])
delete user.age

// ✅ 正确
user.name = '张三'  // 但在 @State 中必须整体替换
// @State 场景:
this.user = { ...this.user, name: '张三' }
```

### ❌ var 声明
```
报错: "arkts-no-var"
```
```typescript
// ❌ 错误
var count = 10

// ✅ 正确
let count = 10
```

### ❌ 结构化类型混用
```
报错: Type 'T' is not assignable to type 'U'
原因: 无继承关系的类即使结构相同也不能互换
```
```typescript
// ❌ 错误
class T { name: string = '' }
class U { name: string = '' }
let u: U = new T()  // 报错

// ✅ 正确: 用 interface 或继承
interface Named { name: string }
class T implements Named { name: string = '' }
class U implements Named { name: string = '' }
let u: Named = new T()  // OK
```

### ❌ 可选参数位置错误
```
报错: 编译失败
```
```typescript
// ❌ 错误
fn(a?: string, b: string) {}

// ✅ 正确
fn(b: string, a?: string) {}
```

---

## 状态管理错误

### ❌ 直接修改 @State 对象子属性
```
现象: 代码执行但 UI 不更新
原因: @State 只追踪引用变化，不追踪深层属性
```
```typescript
// ❌ 错误 —— UI 不刷新
this.user.name = '新名字'

// ✅ 正确 —— 创建新引用
this.user = { ...this.user, name: '新名字' }
this.user = Object.assign({}, this.user, { name: '新名字' })
```

### ❌ 深层嵌套对象不更新
```
解决: 展平数据结构，或用 @Observed + @ObjectLink
```
```typescript
// ✅ 方案1: 展平
@State userName: string = ''
@State userAge: number = 0

// ✅ 方案2: @Observed + @ObjectLink
@Observed
class User { name: string = ''; age: number = 0 }

// 父组件
@Component struct Parent {
  @State user: User = new User()
  build() { Child({ user: this.user }) }
}

// 子组件
@Component struct Child {
  @ObjectLink user: User  // 追踪属性变化
}
```

---

## 组件语法错误

### ❌ ForEach 缺少 key
```
报错: "ForEach must have a key generator"
```
```typescript
// ❌ 错误
ForEach(this.list, (item) => { ListItem() { Text(item) } })

// ✅ 正确
ForEach(this.list, (item: Item) => {
  ListItem() { Text(item.name) }
}, (item: Item) => item.id.toString())  // key 必须唯一
```

### ❌ ForEach key generator 参数未使用
```
报错: "'item' is declared but its value is never read."
原因: key generator 函数参数如果声明了但未在函数体使用，ArkTSCheck 会报未读警告。
      通常是因为 key gen 只用 index.toString() 而没用到 item 参数。
```
```typescript
// ❌ 警告 —— item 声明了但未使用
ForEach(this.list, (item: Item) => {
  ListItem() { Text(item.name) }
}, (_item: Item, index: number) => index.toString())

// ✅ 正确 —— 使用 item 的某个属性做 key
ForEach(this.list, (item: Item) => {
  ListItem() { Text(item.name) }
}, (item: Item) => item.id.toString())

// ✅ 或用 index + 属性组合确保唯一
ForEach(this.list, (item: Item) => {
  ListItem() { Text(item.name) }
}, (item: Item, index: number) => index.toString() + item.id)

// ✅ 如果 item 本身就是 string/number 等原始值，直接用 item 做 key
ForEach(['A', 'B', 'C'], (item: string) => {
  Text(item)
}, (item: string) => item)
```
> **通用原则**: ForEach key generator 中声明的所有参数都必须在函数体中使用。
> 如果只需要 index，可以用 `(_item: Type)` 前缀下划线但仍需在 key 中使用。

### ❌ 组件属性链顺序错误
```
报错: 编译失败
```
```typescript
// ❌ 错误
Column() {
  Text('内容')
}
.width('100%')  // 属性在子组件之后

// ✅ 正确
Column() { Text('内容') }
  .width('100%')  // 先写属性，在子组件前
```

### ❌ @State 写在 struct 外面
```
报错: 装饰器只能在组件类内部使用
```
```typescript
// ❌ 错误
@State globalCount: number = 0  // struct 外面
@Component struct Index { }

// ✅ 正确
@Component struct Index {
  @State count: number = 0  // struct 内部
}
```

### ❌ List / Grid / Scroll 等容器组件缺少显式高宽
```
报错: "You are advised to initialize the width and height attributes of the List component"
原因: ArkTS 编译器要求 List/Grid/Scroll 等滚动容器必须显式声明 width 和 height。
      仅靠父容器的 layoutWeight 或自适应缩放在严格模式下不满足要求。
```
```typescript
// ❌ 警告
List({ space: 12 }) { }

// ✅ 正确 —— width/height 显式声明（layoutWeight 配合 height(0) 占满剩余空间）
List({ space: 12 }) { }
  .width('100%')
  .height(0)
  .layoutWeight(1)  // 运行时覆盖 height(0)，填充 Column 剩余空间
```

### ❌ 非文本组件使用 fontSize / fontColor / fontWeight
```
报错: "Property 'fontSize' does not exist on type 'ColumnAttribute'"
原因: API 12+ 中 fontSize/fontColor/fontWeight/fontStyle 不是通用属性，
      仅 Text/Span/Button/TextInput/TextArea 等文本渲染组件支持。
      Column/Row/Flex/Stack/List 等容器组件上无效。
```
```typescript
// ❌ 错误 —— Column 没有 fontSize
Column() { Text('内容') }
  .backgroundColor('#EEE')
  .fontSize(11)       // 报错！

// ✅ 正确 —— fontSize 写在 Text 上
Column() {
  Text('内容').fontSize(11)
}
.backgroundColor('#EEE')
```

### ❌ 函数可能抛异常，未显式处理
```
报错: "Function may throw exceptions. Special handling is required."
原因: ArkTS 严格模式要求所有可能抛出异常的函数调用必须显式处理。
      同步方法（router.getParams、router.back、JSON.parse 等）必须用 try-catch 包裹。
      异步方法（router.pushUrl、http.request 等 Promise 返回的）可以用 try-catch 或 .catch()。
```

**同步方法 —— 必须用 try-catch：**
```typescript
// ❌ 未处理异常
const params = router.getParams() as Record<string, Object>
router.back()

// ✅ 正确 —— try-catch
try {
  const params = router.getParams() as Record<string, Object>
} catch (e) {
  console.error(JSON.stringify(e))
}

try {
  router.back()
} catch (e) {
  console.error(JSON.stringify(e))
}
```

**异步方法 —— 优先用 .catch() 链式调用（简洁）：**
```typescript
// ❌ 未处理拒绝的 Promise
router.pushUrl({ url: route }, router.RouterMode.Standard)

// ✅ 正确 —— .catch() 链式（简洁推荐）
router.pushUrl({ url: route }, router.RouterMode.Standard)
  .catch((err: Error) => { console.error(JSON.stringify(err)) })

// ✅ 正确 —— try-catch（更严格但啰嗦）
try {
  router.pushUrl({ url: route }, router.RouterMode.Standard)
    .catch((err: Error) => { console.error(JSON.stringify(err)) })
} catch (err) {
  console.error(JSON.stringify(err))
}
```
> **通用原则**：同步调用用 try-catch；Promise 返回的异步调用优先用 `.catch()`。
> 涉及 `router`、`http`、`JSON.parse` 的方法体需显式处理。

---

## 模块/路径错误

### ❌ 导入路径错误（最高频错误）
```
报错: "Cannot find module" / "Module not found"
原因: API 12+ 导入用 @kit.*，非 @ohos.*，且 API 可能在不同 kit 中
```
```typescript
// ❌ 错误（旧版路径）
import router from '@ohos.router'
import http from '@ohos.net.http'

// ✅ 正确（API 12+）
import { router } from '@kit.ArkUI'
import { http } from '@kit.NetworkKit'
```

### ❌ 路径大小写不匹配
```
原因: 编译环境大小写敏感，Windows 上开发习惯导致
```
```typescript
// ❌ 如果文件名是 MyComponent.ets
import { MyComponent } from './mycomponent'  // 报错
import { MyComponent } from './Mycomponent'  // 报错

// ✅ 正确
import { MyComponent } from './MyComponent'
```

### ❌ router.pushUrl 使用旧版回调签名或缺少 RouterMode 参数
```
报错: "The signature '(options: RouterOptions): Promise<void>' of 'router.pushUrl' is deprecated."
      或 "The signature '(options, RouterOptions, mode, RouterMode, callback)' is deprecated."
原因: API 12+ 中 router.pushUrl 有两个变更：
      (1) 必须传 RouterMode 第二参数，单参数签名已废弃；
      (2) 返回 Promise，旧的三参数回调式签名已废弃。
```
```typescript
// ❌ 废弃（单参数，缺 RouterMode）
router.pushUrl({ url: route })

// ❌ 废弃（三参数回调式）
router.pushUrl({ url: route }, router.RouterMode.Standard, (err) => {
  if (err) { console.error(err.message) }
})

// ✅ 正确（Promise 链式）
router.pushUrl({ url: route }, router.RouterMode.Standard)
  .then((): void => { /* 成功 */ })
  .catch((err: Error): void => { console.error(err.message) })

// ⚠️ catch 必须始终存在——Promise 不处理拒绝会触发 unhandledRejection
```

### ❌ animateTo 全局函数废弃
```
报错: "The signature '(value: AnimateParam, event: () => void): void' of 'animateTo' is deprecated."
原因: API 12+ 中全局 animateTo 函数已废弃（API 18 将彻底移除），必须改用 UIContext 实例方法调用。
```
```typescript
// ❌ 废弃（全局函数）
animateTo({ duration: 500, curve: Curve.EaseInOut }, () => {
  this.widthSize = 150
})

// ✅ 正确（UIContext 实例方法）
this.getUIContext().animateTo({ duration: 500, curve: Curve.EaseInOut }, () => {
  this.widthSize = 150
})
```
> **注意**: AnimateParam 对象（duration、curve、delay、iterations、playMode、onFinish 等）完全不变。仅仅是调用前缀从全局改为 `this.getUIContext().`。
> 不要在 `aboutToAppear` / `aboutToDisappear` 中调用 animateTo，组件可能尚未就绪或正在销毁。

### ❌ getUIContext() 在异步回调中失效（setInterval / setTimeout）

```
现象: 在 setInterval/setTimeout 中使用 animateTo 驱动动画，动画完全不运行；
      界面上"暂停""重置"等按钮点击后似乎无效果（@State 不变），方块/图形静止不动。
根因: getUIContext() 必须在 UI 线程的同步执行上下文中调用。
      在 setInterval / setTimeout 等异步回调内部调用时，UIContext 可能已失效，
      导致 animateTo 静默失败 —— 不报错也不执行，动画从未真正启动。
      因此依赖动画推进的 UI 状态（旋转角度、位置、缩放等）也从未变化，
      按钮看起来"不工作"实际是因为没有动画可暂停/重置。
```

```typescript
// ❌ 错误：在 setInterval 异步回调中直接调用 getUIContext()
startAnimation(): void {
  this.isAnimating = true
  this.timer = setInterval(() => {
    // 🔥 异步回调中 getUIContext() 可能返回无效上下文，animateTo 静默失败
    this.getUIContext().animateTo({ duration: 100, curve: Curve.Linear }, () => {
      this.angle = (this.angle + 10) % 360   // 永远不会执行
      this.offsetX = (this.offsetX + 5) % 200
    })
  }, 100)
}

// ✅ 正确：在同步代码中先捕获 UIContext 引用，再在回调中使用
startAnimation(): void {
  if (this.isAnimating) { return }
  this.isAnimating = true
  // 🔑 同步捕获 UIContext —— 此时在 UI 线程的同步上下文中
  const uiContext: UIContext = this.getUIContext()
  this.timer = setInterval(() => {
    // 安全守卫：防止 clearInterval 后残留的 tick 继续执行
    if (!this.isAnimating) { return }
    // 使用已捕获的引用，稳定可靠
    uiContext.animateTo({ duration: 100, curve: Curve.Linear }, () => {
      this.angle = (this.angle + 10) % 360
      this.offsetX = (this.offsetX + 5) % 200
    })
  }, 100)
}
```

> **注意**: 
> - 此问题同样影响 `setTimeout`、`Promise.then()` 等所有异步回调。
> - 在 onClick、onChange 等事件处理器中 `getUIContext()` 调用是同步的，无需捕获。
> - 不仅影响 `animateTo`，其他依赖 UIContext 的 API（如 `focusControl.requestFocus`）也需同样处理。
> - **典型诊断方法**：在 interval 回调中加 `console.log`，如果日志输出正常但 UI 不变，就是此问题。

### ❌ 页面未注册
```
报错: "The uri of router is not exist"
```
```typescript
// 修复: 在 resources/base/profile/main_pages.json 添加:
{ "src": [ "pages/Index", "pages/NewPage" ] }

// router URL 必须与注册完全一致，不要以 / 开头
router.pushUrl({ url: 'pages/NewPage' })        // ✅
router.pushUrl({ url: '/pages/NewPage' })       // ❌
```

---

## 工程配置错误

### ❌ 网络请求无权限
```
报错: 网络请求失败，无明确错误
```
```json
// module.json5 添加:
{ "module": { "requestPermissions": [
  { "name": "ohos.permission.INTERNET" }
]}}
```

### ❌ 直接调用受保护 API 无权限
```
报错: "Permission denied"
```
```typescript
// 运行时申请（相机为例）
import { abilityAccessCtrl } from '@kit.AbilityKit'
const atManager = abilityAccessCtrl.createAtManager()
try {
  const result = await atManager.requestPermissionsFromUser(
    getContext(), ['ohos.permission.CAMERA']
  )
} catch (err) {
  console.error('权限申请失败:', JSON.stringify(err))
}
```

### ❌ JSON.parse 大整数精度丢失
```
原因: 后端 Long ID 超过 16 位时 JS Number 丢失精度
```
```typescript
// ❌ 后端发 1234567890123456789 (17位)
const data = JSON.parse(response)
console.log(data.id)  // 1234567890123456700  — 精度丢失！

// ✅ 后端传 String，或前端用 json-bigint
```

---

---

## 图形绘制错误

### ❌ Line/Polyline/Polygon 不设置 stroke 无边框
```
现象: 图形绘制出但看不到边界/内容
原因: 图形组件默认无边框（stroke），必须显式设置 stroke 后才可见
```
```typescript
// ❌ 错误 —— 看不到线
Line()
  .width(200).height(150)
  .startPoint([0, 0]).endPoint([50, 100])

// ✅ 正确 —— 设置 stroke
Line()
  .width(200).height(150)
  .startPoint([0, 0]).endPoint([50, 100])
  .stroke(Color.Red)       // 必须
  .strokeWidth(3)
```

### ❌ Path commands 坐标单位用 vp 但实际是 px
```
现象: Path 图形大小与预期不符
原因: commands 中坐标为 px 单位，非 vp
```
```typescript
// commands 里的数字单位是 px，不是 vp
Path()
  .width('600px')               // 容器宽度
  .height('10px')
  .commands('M0 0 L600 0')      // 画600px长的线（单位px）
  .stroke(Color.Black)
```

### ❌ Color.xxx 枚举值不存在
```
报错: "Property 'Purple' does not exist on type 'typeof Color'"
原因: ArkTS 的 Color 枚举只包含少量预定义颜色（Red/Blue/Green/Yellow/Black/White/
      Gray/Grey/Orange/Pink/Transparent），没有 Purple/Brown/Cyan 等扩展色。
      遇到不存在的枚举值直接用十六进制字符串替代。
```
```typescript
// ❌ 报错 —— Color.Purple 不存在
.fill(Color.Purple)

// ✅ 正确 —— 用十六进制字符串
.fill('#9B59B6')   // 紫色
.fill('#8B4513')   // 棕色
.fill('#00BCD4')   // 青色
```
> **最佳实践**：除最常用的 Red/Blue/Black/White 外，统一用十六进制字符串 `'#XXXXXX'`，
>  既避免枚举缺失问题，也便于设计稿色值直译。

### ❌ Polyline 和 Polygon 混淆
```
Polyline: 折线 — 不自动闭合，终点不连起点
Polygon:  多边形 — 自动闭合，终点自动连起点
```
```typescript
// 三角形用 Polygon（自动闭合）
Polygon({ width: 100, height: 100 })
  .points([[0, 0], [50, 100], [100, 0]])  // 3个点自动闭合

// 折线用 Polyline（不闭合）
Polyline({ width: 100, height: 100 })
  .points([[0, 0], [20, 60], [100, 100]]) // 3个点不闭合
```

### ❌ 标题栏组件使用通用属性
```
现象: .width()/ .height() 等属性在标题栏上不生效
原因: ComposeTitleBar/SelectTitleBar/TabTitleBar 不支持通用属性
```
```typescript
// ❌ 错误
ComposeTitleBar({ title: "标题" })
  .width('100%')       // 无效
  .height(56)          // 无效

// ✅ 正确 —— 不链式调用任何通用属性
ComposeTitleBar({ title: "标题" })
```

### ❌ TabTitleBar 用于二级页面
```
现象: 返回功能异常或页面布局错乱
原因: TabTitleBar 仅一级页面适用
```
```typescript
// ❌ 二级页面使用 TabTitleBar → 故障
// ✅ 二级页面用 ComposeTitleBar 或 SelectTitleBar（自动显示返回键）
```

---

## 通用属性常见错误

### ❌ layoutWeight 在非 Row/Column/Flex 容器中不生效
```
原因: layoutWeight 仅在 Row/Column/Flex 的布局中生效
```
```typescript
// ❌ 无效 —— Stack 不支持 layoutWeight
Stack() {
  Text('内容').layoutWeight(1)
}

// ✅ 有效
Row() {
  Text('A').layoutWeight(1)  // 占剩余空间1/3
  Text('B').layoutWeight(2)  // 占剩余空间2/3
}
```

### ❌ position 和 offset 混淆
```
position: 绝对定位，相对父容器左上角。在Row/Column/Flex中不占位。
offset:   相对偏移，仅绘制位置偏移。不影响布局，仍占原位置。
```
```typescript
// position —— 脱离布局流，不占位
Text('定位').position({ x: 30, y: 10 })

// offset —— 仍在布局流中占位，仅视觉偏移
Text('偏移').offset({ x: 15, y: 30 })
```

### ❌ Alignment 枚举使用 Left/Right 而非 Start/End
```
报错: "Property 'TopLeft' does not exist on type 'typeof Alignment'"
原因: ArkTS Alignment 枚举采用语义化 Start/End（兼容 RTL 布局方向），
      不存在 TopLeft / TopRight / BottomLeft / BottomRight 这些值。
      与 Android/iOS 习惯不同，是 HarmonyOS 最高频的枚举错误之一。
```
```typescript
// ❌ 错误 —— Left/Right 不存在
Stack({ alignContent: Alignment.TopLeft })
Stack({ alignContent: Alignment.TopRight })
Stack({ alignContent: Alignment.BottomLeft })
Column().align(Alignment.TopLeft)

// ✅ 正确 —— 用 Start/End
Stack({ alignContent: Alignment.TopStart })
Stack({ alignContent: Alignment.TopEnd })
Stack({ alignContent: Alignment.BottomStart })
Stack({ alignContent: Alignment.BottomEnd })
Column().align(Alignment.TopStart)
```

完整有效值表：

| Alignment 值 | 九宫格位置 |
|-------------|----------|
| `TopStart` | 左上 |
| `Top` | 中上 |
| `TopEnd` | 右上 |
| `Start` | 左中 |
| `Center` | 正中（默认） |
| `End` | 右中 |
| `BottomStart` | 左下 |
| `Bottom` | 中下 |
| `BottomEnd` | 右下 |

> **规则**：HarmonyOS 所有布局对齐一律用 Start/End，没有例外。Left/Right 是无效值。

### ❌ Visibility.None 和 Visibility.Hidden 混淆
```
Hidden: 隐藏但参与布局占位（占着位置看不到）
None:   隐藏且不参与布局，不占位（彻底消失）
```
```typescript
// 用 Hidden → 位置还留着，有空白
Row().visibility(Visibility.Hidden).height(80)   // 空白80vp还在

// 用 None → 位置也不占
Row().visibility(Visibility.None).height(80)      // 彻底消失

// ⚠️ 如需条件不渲染，优先用 if/else 条件渲染
```

### ❌ opacity 父子叠加产生意外效果
```
原因: 子组件继承父透明度并叠加。父opacity(0.1) × 子opacity(0.8) = 实际0.08
```
```typescript
// ❌ 可能意外 —— 子组件几乎看不到
Column() { Text('看不清').opacity(0.8) }
  .opacity(0.1)  // 实际Text透明度=0.08

// ✅ 明确计算或分开控制
```

### ❌ rotate/translate/scale 忘记设置变换中心
```
原因: 默认变换中心是组件左上角，旋转效果可能不符合预期
```
```typescript
// ❌ 绕左上角旋转 —— 可能跑出屏幕
Row().rotate({ x: 0, y: 0, z: 1, angle: 300 })

// ✅ 绕组件中心旋转
Row().rotate({
  x: 0, y: 0, z: 1,
  angle: 300,
  centerX: '50%',
  centerY: '50%'
})
```

### ❌ enabled(false) 与 stateStyles.disabled 不联动
```
原因: enabled(false) 只是禁用交互，不会自动触发 disabled 样式。
      需要配合 stateStyles 一起使用。
```
```typescript
// ✅ 正确联动方式
Text('按钮')
  .enabled(this.isDisabled)
  .stateStyles({
    normal: { .backgroundColor('#007DFF') },
    disabled: { .backgroundColor('#CCC') }
  })
```

### ❌ blur 与 backgroundBlurStyle 混淆
```
blur:                  对组件自身内容进行模糊
backgroundBlurStyle:   对组件背景（透过组件看到的下层内容）进行模糊
```

---

## 内置组件错误

### ❌ Span 写在 Text 外面
```
现象: Span 不显示或编译报错
原因: Span/ImageSpan 必须是 Text 的子组件
```
```typescript
// ❌ 错误
Span('文字')  // 单独使用不显示

// ✅ 正确
Text() { Span('文字') }
```

### ❌ Text 同时有内容 + Span 子组件时 Span 覆盖 Text
```
Span 内容会覆盖 Text 自身内容
```
```typescript
Text('这段不会显示') {
  Span('实际显示这段')  // 覆盖 Text 的内容
}
```

### ❌ ContainerSpan 属性限制
```
仅支持 textBackgroundStyle({ color, radius })，不支持 width/height 等
```

### ❌ TextInput 双向绑定未用 $$
```
现象: 输入框中输入内容不会同步回变量
原因: 必须使用 $$ 语法双向绑定
```
```typescript
// ❌ 单向 —— 变量变输入框跟着变，但输入框输入不会回写
TextInput({ text: this.inputValue })

// ✅ 双向绑定
TextInput({ text: $$this.inputValue })
```

### ❌ 像素单位混用
```
现象: 布局在真机和Previewer表现不一致
原因: px在不同设备上大小不同；vp保证跨设备一致
```
```typescript
// ❌ 不推荐
.width(100)      // 默认vp，但如果是 '100px' 则跨设备不一致

// ✅ 推荐
.width(100)      // 默认vp
.fontSize('16fp') // 字体用fp，随系统字体缩放
```

### ❌ Image 资源引用错误
```
报错: "Unknown resource name 'xxx'"
$r('app.media.xxx')  → 不加后缀名，不能放子文件夹，资源名必须在 resources/base/media/ 中存在
$rawfile('xxx.jpeg') → 必须加后缀名，支持子文件夹路径
```

```typescript
// ❌ 错误 —— 项目中无此资源
$r('app.media.app_icon')       // 编译报错: Unknown resource name
$r('app.media.poster_1')       // 编译报错（除非真有 poster_1.png）

// ✅ 正确 —— 先检查 media 目录下有对应文件
$r('app.media.background')     // 需要 background.png 存在
$r('app.media.startIcon')      // 需要 startIcon.png 存在

// ✅ 安全做法 —— 先用项目自带的已知资源占位
// ls resources/base/media/ → background.png, startIcon.png
// 生成代码前确认资源文件名，不要猜测
```
> **原则**：$r('app.media.xxx') 中的 xxx 必须对应 resources/base/media/ 目录下的文件（不含后缀）。
> 生成代码前先 ls 确认媒体目录，不要凭空写资源名。
> 同理，$rawfile 路径必须在 resources/rawfile/ 下。

### ❌ 使用废弃的 @system 导入
```
import Notification from '@system.notification'  // API 12+ 已废弃
// 所有系统API应从 @kit.* 或 @ohos.* 导入
```

### ❌ Button 自定义内容时用错语法
```
// ✅ 自定义按钮（内嵌子组件）
Button() {
  Image($r('app.media.icon')).width(20)
  Text('文字')
}
// 注意 Button() 后面是 {} 不是 ()，内嵌子组件后不能再链式设文字
```

---

## Previewer 渲染限制

DevEco Studio Previewer 是实机的功能子集，以下组件/模式会静默失败（无编译错误，无运行时异常，仅渲染空白）。

### ❌ GridRow / GridCol 不支持

```
现象: GridRow/GridCol 区域完全空白，编译成功无报错
原因: Previewer 渲染引擎未实现 GridRow/GridCol（API 10+ 组件）
排查: 用 Flex({ wrap: FlexWrap.Wrap }) 临时替换，能显示即确认
```

```typescript
// ❌ Previewer 不渲染
GridRow({ columns: { xs: 1, sm: 2, md: 2, lg: 4 }, gutter: { x: 14, y: 14 } }) {
  ForEach(this.cells, (cell: CellData) => {
    GridCol({ span: 1 }) { this.buildCell(cell) }
  })
}

// ✅ Previewer 兼容 — Flex wrap 模拟 2×2 田字格
Flex({ direction: FlexDirection.Row, wrap: FlexWrap.Wrap, justifyContent: FlexAlign.SpaceBetween }) {
  ForEach(this.cells, (cell: CellData) => {
    this.buildCell(cell)
  })
}
// 每个卡片设置 width('48%') + margin({ bottom: 14 }) 形成双列
```

### ❌ Flex 嵌套 Flex（双重 Flex）阻断后续渲染

```
现象: 双重 Flex 之后的全部 UI 组件消失（标题、状态栏可见，卡片区域空白）
原因: Flex → Flex 嵌套导致 Previewer 组件栈静默损坏，后续内容不再渲染
排查: 将内层 Flex({ direction: FlexDirection.Column }) 替换为 Column，能显示即确认
```

```typescript
// ❌ Previewer 阻断 — 外层 Flex Row，内层 Flex Column
Flex({ direction: FlexDirection.Row, justifyContent: FlexAlign.SpaceAround }) {
  Flex({ direction: FlexDirection.Column, alignItems: ItemAlign.Center }) {  // ❌
    Text('标签')
    Text('值')
  }
  // ... 更多 Flex Column
}
// 此后的所有组件全部不可见

// ✅ Previewer 兼容 — 内层用 Column（不是 Flex）
Flex({ direction: FlexDirection.Row, justifyContent: FlexAlign.SpaceAround }) {
  Column() {  // ✅
    Text('标签')
    Text('值')
  }
  .alignItems(HorizontalAlign.Center)
  // ... 更多 Column
}
```

**阻断规则总结：**

| 外层 | 内层 | Previewer |
|------|------|-----------|
| Flex Row | Column | ✅ 正常 |
| Flex Row | Flex Column | ❌ 阻断后续渲染 |
| Column | Flex Column | ✅ 正常 |
| Column | Column | ✅ 正常 |
| Flex Row | Text（直接） | ✅ 正常 |

### ❌ @Builder 嵌套调用触发相同阻断

```
现象: buildA() 内调用 buildB()，buildA() 之后的内容不可见
原因: 本质同上 — @Builder 内部 Flex 嵌套被调用方插入时，
     等同于双重 Flex 嵌套
```

```typescript
// ❌ Previewer 阻断
@Builder
buildChip(label: string, value: string) {
  Flex({ direction: FlexDirection.Column }) {  // 这个 Flex 是罪魁
    Text(label)
    Text(value)
  }
}

@Builder
buildStatusBar() {
  Flex({ direction: FlexDirection.Row }) {
    this.buildChip('状态', '正常')  // 内嵌 Flex Column → 阻断
    this.buildChip('等级', '低')
    this.buildChip('扫描', '2分钟')
  }
  // buildStatusBar 之后的内容全部消失
}

// ✅ 修复方案 A: 将 buildChip 内联（Column 替代 Flex Column）
// ✅ 修复方案 B: buildChip 内部用 Column（如果不需要 Flex 的特性）
```

### Debug 方法论 — 定位 Previewer 阻断点

```
1. 把可疑区域替换为简单 Text (亮色背景) — 过滤布局问题
2. 把 Text 分别放在阻断点之前/中间/之后 — 二分定位精确行
3. 检查阻断点是否包含 Flex → Flex 嵌套
4. 用 Column 替换内层 Flex Column
```

---

## 路由相关陷阱

### ❌ router.getParams() 返回 undefined

```
报错: "Cannot read property 'xxx' of undefined" / 参数丢失
原因: 未传递参数时 getParams() 返回 undefined，直接访问属性会崩溃
```

```typescript
// ❌ 直接访问属性
const title = router.getParams().title  // 无参数时崩溃

// ✅ 先判空
const params = router.getParams() as Record<string, Object>
if (params) {
  const title = params.title as string
}
```

### ❌ router.back({url}) 目标页不在页面栈中

```
现象: router.back({url: 'pages/Target'}) 无效 / 无任何反应
原因: back 到指定页面时，目标页必须已经存在于页面栈中（之前通过 pushUrl 进入过）
```

```typescript
// ❌ Target 页从未 pushUrl 进入过，back 失败
router.back({ url: 'pages/Target' })

// ✅ 用 pushUrl 跳转到目标页（而不是 back）
router.pushUrl({ url: 'pages/Target' })
```

> **规则**：回到栈中已有的页面用 `back`，首次跳转到新页面用 `pushUrl` 或 `replaceUrl`。

### ❌ 页面栈超过 32 页限制

```
报错: "The pages are pushed too much"
原因: 页面栈最大容量为 32 页，长时间连续 pushUrl 不返回会爆栈
```

```typescript
// ✅ 适时清空栈（如回到首页时）
router.clear()
router.pushUrl({ url: 'pages/Index' })
```

---

## 组件结构陷阱

### ❌ TabContent 不是 Tabs 的直接子节点

```
报错: 编译失败 / TabBar 不显示
原因: TabContent 必须作为 Tabs 的直接子组件，不能包裹在 Column/Row/Flex 中
```

```typescript
// ❌ TabContent 被 Column 包裹
Tabs() {
  Column() {  // ❌ 中间层！
    TabContent() { Text('A') }.tabBar('A')
  }
}

// ✅ TabContent 直接作为 Tabs 子节点
Tabs() {
  TabContent() { Text('A') }.tabBar('A')
  TabContent() { Text('B') }.tabBar('B')
}
```

### ❌ Grid 未声明显式宽高

```
现象: Grid 组件渲染空白或尺寸为 0
原因: 与 List/Scroll 相同，Grid 内部算法依赖显式容器尺寸才能布局
```

```typescript
// ❌ 无宽高，渲染空白
Grid() { GridItem() { Text('A') } }
  .columnsTemplate('1fr 1fr')

// ✅ 声明显式尺寸
Grid() { GridItem() { Text('A') } }
  .columnsTemplate('1fr 1fr')
  .width('100%')
  .height(300)

// ✅ 或用 layoutWeight 占满剩余空间
Column() {
  Grid() { GridItem() { Text('A') } }
    .columnsTemplate('1fr 1fr')
    .width('100%')
    .height(0).layoutWeight(1)
}
```

### ❌ 跨文件组件缺少 export default

```
报错: "Cannot find module" / import 后无法使用组件
原因: ArkTS 中可复用组件（非 @Entry 页面）必须用 export default 显式导出
```

```typescript
// ❌ components/MyComp.ets — 缺少导出
@Component
struct MyComp { build() { Text('hello') } }

// ✅ components/MyComp.ets — 正确导出
@Component
struct MyComp { build() { Text('hello') } }
export default MyComp

// ✅ pages/Index.ets — 默认导入
import MyComp from '../components/MyComp'
```

> **规则**：只有 `@Entry` 页面不需要 export default。非 Entry 组件一律加 export default。

---

## 快速排查流程

1. 看 DevEco Studio **Build/Problems 面板**，从第一个错误开始修
2. 检查导入路径：是否用了 `@kit.*` 格式，模块名是否正确
3. 检查 `main_pages.json`：新页面是否注册
4. 检查 `module.json5`：权限是否声明
5. 搜索 `any` / `var` 关键词，逐一替换
6. 检查 `ForEach` 是否有第三个参数
7. 检查 `@State` 对象修改是否整体替换引用
8. **Previewer 渲染空白但无报错** → 检查以上 "Previewer 渲染限制" 三个陷阱
   - GridRow/GridCol → 换 Flex wrap
   - Flex 嵌套 Flex → 内层换 Column
   - @Builder 嵌套 → 内联或换 Column
9. **V2 组件编译报错** → 检查以下常见错误：

---

## V2 状态管理常见错误（API 12+）

### V2-1: V1 和 V2 装饰器混用

```typescript
// ❌ 错误：V1 @Component 内使用 V2 @Local
@Component
struct MyPage {
  @Local count: number = 0   // 编译报错！@Local 仅 V2 组件可用
}

// ❌ 错误：V2 @ComponentV2 内使用 V1 @State
@ComponentV2
struct MyPage {
  @State count: number = 0   // 编译报错！@State 仅 V1 组件可用
}
```

**修复**：`@ComponentV2` 统一用 `@Local/@Param/@Event`；`@Component` 统一用 `@State/@Prop/@Link`。**不可混用**。

### V2-2: `!!` 和 `$$` 混淆

```typescript
@ComponentV2
struct Parent {
  @Local text: string = ''
  build() {
    Child({ paramText: this!!.text })   // ✅ V2 双向绑定用 !!（两个感叹号）
    //                                  // ❌ 不能用 $$ || this.text
  }
}
```

> V1 用 `$var` 传给 `@Link`；V2 用 `this!!.var` 传给 `@Param`。**`$$` 是 V1 语法，在 V2 中无效**。

### V2-3: `@Param` 接收值后直接修改

```typescript
@ComponentV2
struct Child {
  @Param count: number = 0
  build() {
    Button('+1').onClick(() => { this.count++ })  // ❌ 运行时可能不更新父组件
  }
}
```

**修复**：子组件不应直接修改 `@Param`。需回传父组件用 `@Event`：

```typescript
@ComponentV2
struct Child {
  @Param count: number = 0
  @Event onCountChange: (newVal: number) => void
  build() {
    Button('+1').onClick(() => {
      this.onCountChange(this.count + 1)  // ✅ 通过 @Event 通知父
    })
  }
}
```

### V2-4: `@Computed` 依赖未追踪

```typescript
@ComponentV2
struct Page {
  @Local items: string[] = []
  @Computed
  get itemCount(): number {
    // ✅ @Local items 变化 → @Computed 自动重算
    return this.items.length
  }
  @Computed
  get firstItem(): string {
    // ✅ 访问另一个 @Computed → 自动追踪依赖链
    return this.items[0] ?? ''
  }
}
```

> `@Computed` 自动追踪 getter 内访问的所有 `@Local/@Param/@Consumer/@Computed`。**无需手动声明依赖列表**。

### V2-5: `@Event` 参数类型不匹配

```typescript
@ComponentV2
struct Child {
  @Event onSelect: (id: number, name: string) => void  // 声明两个参数
  build() {
    Button('Select').onClick(() => { this.onSelect(1) })  // ❌ 缺第二个参数 → 类型报错
  }
}
```

**修复**：`@Event` 回调的参数数量和类型必须完全匹配声明。

### V2-6: `@Provider` key 重复

```typescript
@ComponentV2
struct AncestorA {
  @Provider('theme') theme: string = 'dark'
  build() { ... }
}

@ComponentV2
struct AncestorB {
  @Provider('theme') theme: number = 0  // ❌ key 'theme' 重复且类型不同
  build() { ... }
}
```

**修复**：同一个 key 在组件树中只能有一个 `@Provider`。多主题系统用不同 key 名（如 `'themeColor'` / `'themeMode'`）。

### V2-7: `@Consumer` 缺少对应 `@Provider`

```typescript
@ComponentV2
struct DeepChild {
  @Consumer('userInfo') user: UserInfo | null = null
  // 如果祖先中没有 @Provider('userInfo') → 编译报错
  build() { ... }
}
```

**修复**：确保组件树上至少有一个祖先组件声明了 `@Provider('userInfo')`。

### V2-8: V1 `@Observed` 在 V2 中无效

```typescript
@Observed   // ❌ V2 中此装饰器无效果，浪费代码
class DataModel {
  name: string = ''
}

@ComponentV2
struct Page {
  @Local data: DataModel = new DataModel()
  build() {
    Text(this.data.name)
    Button('Change').onClick(() => {
      this.data.name = 'New'  // ✅ UI 自动更新（V2 @Local 自动深度追踪）
    })
  }
}
```

**修复**：V2 中 `@Local` 自动深度追踪对象/数组变化，无需 `@Observed`。直接删除 `@Observed` 装饰器即可。

---

## 三层架构依赖错误

### 3L-1: 循环依赖

**现象**：关闭项目重新打开后报错 `Circular dependency detected`

```json5
// common/basic 依赖 features/home，features/home 又依赖 common/basic
// common/basic/oh-package.json5
{ "dependencies": { "home": "file:../../features/home" } }  // ❌ 反向依赖
```

**规则**：依赖方向只能是 products → features → common。common 不得依赖 features 或 products，features 不得依赖 products。

**修复**：检查所有 `oh-package.json5` 的 dependencies，确保无反向引用。配置完依赖后关闭项目重新打开确认无报错。

### 3L-2: common 层包含业务逻辑

**现象**：公共能力层的组件/工具被多个 feature 引用但包含了特定业务的判断逻辑。

```typescript
// common/basic/.../ButtonCom.ets
if (this.btn === 'home页按钮') { ... }  // ❌ 业务逻辑不应在 common 层
```

**规则**：common 层仅提供与业务无关的公共代码：通用 UI 组件、工具类、网络封装、公共配置。业务逻辑属于 features 层。

**修复**：将业务相关的条件/数据处理移到 features 层，common 层只保留纯通用逻辑。

### 3L-3: 包类型选错

**现象**：common 层创建为 HAR 包，被多个 feature 引用后总包体积膨胀。

**规则**：
- common（被大量模块引用）→ **HSP**（动态共享，运行时加载，避免重复打包）
- features（仅被产品层引用）→ **HAR**（静态共享，编译时集成，加载更快）
- products → **Entry HAP**（应用主入口）

**修复**：如果 common 层已经被多个模块依赖且项目包体积明显偏大，考虑重建为 HSP 包并迁移代码。

---

## 网络请求错误

### NET-1: localhost 模拟器不可达

**现象**：模拟器中 HTTP 请求报错 `Failed to connect to localhost/127.0.0.1`

```typescript
// ❌ 模拟器中 localhost 指向模拟器自身，不是开发机
httpRequest.request('http://localhost:9988/data')
```

**修复**：
1. 打开 cmd/terminal，执行 `ipconfig` (Win) 或 `ifconfig` (Mac) 获取本机局域网 IP
2. 启动 json-server 时指定本机 IP：`json-server --watch db.json --port 9988 --host 192.168.x.x`
3. 将代码中 localhost 替换为 `http://192.168.x.x:9988/data`

### NET-2: 忘记声明 INTERNET 权限

**现象**：模拟器/真机运行时报错 `Permission denied`，网络请求无响应。预览器正常（预览器不检查权限）。

**修复**：在 `entry/src/main/module.json5` 中声明：

```json5
"module": {
  "requestPermissions": [
    { "name": "ohos.permission.INTERNET" }
  ]
}
```

### NET-3: 每次请求创建新的 http 实例

**现象**：频繁请求时性能下降、内存泄漏

```typescript
Button("请求").onClick(() => {
  const req = http.createHttp()  // ❌ 每次点击创建新实例
  req.request('http://...')
})
```

**修复**：在组件或单例中复用 httpRequest 实例：

```typescript
private httpReq = http.createHttp()  // ✅ 组件生命周期内复用

Button("请求").onClick(() => {
  this.httpReq.request('http://...')
})
```

### NET-4: json-server 端口被占用

**现象**：启动 json-server 报错 `address already in use`

**修复**：更换端口号 `--port 9989`，同时更新代码中的 URL 端口。

---

## 第三方 SDK 错误

### SDK-1: 忘记在 UIAbility 中初始化

**现象**：调用 SDK 方法时崩溃或返回 undefined

```typescript
// ❌ 未初始化就直接调用
PickerUtil.cameraEasy()
```

**修复**：在 `EntryAbility.ts` 的 `onCreate` 中初始化：

```typescript
import { AppUtil } from '@pura/harmony-utils';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam) {
    AppUtil.init(this.context);   // ✅ 必须最先调用
  }
}
```

### SDK-2: 预览器中调用 Camera/Picker

**现象**：预览器中调用相机/相册无反应或报错

**规则**：Camera、Picker、扫码等硬件相关 API 在预览器中不支持，必须在模拟器或真机上测试。

**修复**：开发阶段用条件判断跳过预览器不可用的功能，集成测试时用模拟器验证。

### SDK-3: ohpm 安装后未重新打开项目

**现象**：`ohpm i @pura/harmony-dialog` 执行成功，但 import 仍然报找不到模块

**修复**：安装第三方依赖后，关闭 DevEco Studio 项目再重新打开，让 IDE 重新索引 `oh_modules`。

### SDK-4: harmony-dialog 弹窗在 async 回调中失效

**现象**：在 `setTimeout`、`setInterval` 或 Promise 回调中调用 `DialogHelper.showToast()` 无效果

**修复**：确保弹窗调用在主线程上下文中。如果必须在异步回调中使用，先通过 `getContext()` 获取 UIContext 再调用。

---

## 自适应布局+手势错误

### ADAPT-1: displayPriority 小数误解

**现象**：设置了 `displayPriority(1.5)` 期望它比 `displayPriority(1)` 优先级更高

```typescript
Image(...).displayPriority(1.5)  // ❌ 与 displayPriority(1) 优先级相同！
```

**规则**：`[x, x+1)` 区间内视为同优先级。1.0 和 1.9 优先级完全相同。应使用整数区分优先级。

**修复**：使用整数：`displayPriority(1)`、`displayPriority(2)`、`displayPriority(3)`。

### ADAPT-2: Scroll 子组件缺固定宽高

**现象**：Scroll 容器中的子元素宽度塌陷或显示不全

```html
Scroll() {
  Row() { ... }  // ❌ 未设置固定宽度，水平滚动时塌陷
}
.scrollable(ScrollDirection.Horizontal)
```

**修复**：水平 Scroll 中 Row 需设置固定宽度或子元素有确定宽度：

```html
Scroll() {
  Row() {
    ForEach(arr, item => {
      Column() { ... }.width(100).height(50)  // ✅ 固定尺寸
    })
  }
}
.scrollable(ScrollDirection.Horizontal)
```

### ADAPT-3: PinchGesture + PanGesture 组合不跟手

**现象**：图片缩放后拖拽位移"跳跃"或"不跟手"

```typescript
PanGesture()
  .onActionUpdate((event: PanGestureEvent) => {
    this.offsetX += event.offsetX  // ❌ 未除以缩放因子
  })
```

**修复**：拖拽位移必须除以当前缩放比例：

```typescript
PanGesture()
  .onActionUpdate((event: PanGestureEvent) => {
    this.offsetX += event.offsetX / this.scaleValue   // ✅
    this.offsetY += event.offsetY / this.scaleValue
  })
```

### ADAPT-4: FlexWrap 在 Column 容器中无效

**现象**：在 Column 中设置 `wrap: FlexWrap.Wrap` 不换行

**规则**：`FlexWrap.Wrap` 只在 `Flex` 容器中生效，在 `Row`/`Column` 中不工作。

**修复**：需要换行能力时使用 `Flex({ wrap: FlexWrap.Wrap })` 替代 `Row`。
