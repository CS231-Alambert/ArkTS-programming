# ArkTS 代码示例集 (API 12+)

> **快速定位**：用 Read offset=行号 limit=行数读取指定示例，无需全量加载。

| # | 示例 | 行号 | 场景关键词 |
|---|------|------|-----------|
| 1 | 完整页面模板 | 3 | 页面框架/Loading/空状态/Refresh/List |
| 2 | 网络请求 HTTP | 149 | http/createHttp/GET/POST/token |
| 3 | 本地存储 Preferences | 233 | preferences/get/put/flush |
| 4 | 传感器 | 288 | sensor/ACCELEROMETER |
| 5 | 相机预览 | 324 | camera/XComponent/权限申请 |
| 6 | 权限管理工具 | 384 | abilityAccessCtrl/requestPermissions |
| 7 | 详情页(路由参数) | 421 | router/getParams/onBackPress |
| 8 | V2组件 | 485 | @ComponentV2/@Local/@Param/@Event |
| 9 | 目录结构 | 535 | 项目模板 |
| 10 | Search 搜索框 | 569 | 搜索/cancelButton/searchButton |
| 11 | Swiper 轮播图 | 610 | 轮播/autoPlay/indicator |
| 12 | Tabs 标签页 | 644 | 底部导航/TabBar/@Builder |
| 13 | Grid 网格 | 705 | 网格/columnsTemplate/rowsTemplate |
| 14 | List 列表 | 738 | 分隔线/divider/scrollBar |
| 15 | Scroll 滚动 | 792 | 滚动容器/edgeEffect |
| 16 | @Styles/@Extend | 820 | 样式复用/传参样式 |
| 17 | stateStyles 多态 | 883 | 按压态/禁用态/焦点态 |
| 18 | 短信验证码倒计时 | 922 | setInterval/倒计时/验证码 |
| 19 | 组件通信全套 | 999 | @Prop/@Link/@Provide/@Consume |
| 20 | Radio/Checkbox/Toggle | 1090 | 单选框/复选框/开关 |
| 21 | Progress 进度条 | 1160 | 线性/环形/圆形/胶囊进度 |
| 22 | DatePicker | 1195 | 日期选择器 |
| 23 | 华为登录页 | 1227 | 登录页实战/TextInput/Button |
| 24 | 图形绘制 | 1323 | Circle/Ellipse/Line/Polygon/Polyline/Rect/Path |
| 25 | 标题栏 | 1425 | ComposeTitleBar/SelectTitleBar/TabTitleBar |
| 26 | 通用属性 | 1516 | layoutWeight/direction/position/offset/aspectRatio |
| 27 | 图形变换+动画 | 1605 | rotate/translate/scale/animateTo |
| 28 | 裁剪与遮罩 | 1677 | clip/clipShape/maskShape |
| 29 | Span/ImageSpan | 1726 | 富文本/行内图片/ContainerSpan |
| 30 | Flex 弹性布局 | 1780 | FlexDirection/Wrap/justifyContent/alignItems/alignSelf |
| 31 | GridRow 栅格 | 1851 | GridRow/GridCol/响应式/breakpoints |
| 32 | Stack+悬浮按钮 | 1894 | Stack/zIndex/Toggle/position |
| 33 | **路由返回确认框** | 1996 | showAlertBeforeBackPage/router.back/params |
| 34 | **Tabs 底部导航（组件化）** | 2045 | Tabs/TabContent/barPosition/默认导入 |
| 35 | **电影详情页（路由参数接收）** | 2152 | getParams/params判空/aboutToAppear/类型断言 |
| 36 | **完整视频App架构（Tabs+Grid+路由）** | 2230 | 组件解耦/数据驱动/navigateTo/全链路参数传递 |
| 37 | **HTTP GET + json-server** | **2425** | http/GET/json-server/模拟数据 |
| 38 | **harmony-dialog 弹窗合集** | **2510** | DialogHelper/各种弹窗/第三方库 |
| 39 | **三层架构脚手架** | **2660** | Common/Features/Products/HSP/HAR/依赖配置 |
| 40 | **自适应布局 displayPriority + FlexWrap** | **2795** | 响应式/displayPriority/FlexWrap/自适应 |
| 41 | **PinchZoom + Pan 组合手势** | **2885** | PinchGesture/PanGesture/GestureGroup/图片缩放拖拽 |

---

## 1. 完整页面模板

```typescript
// pages/HomePage.ets
import { router } from '@kit.ArkUI'

interface NewsItem {
  id: number
  title: string
  summary: string
  imageUrl: Resource
}

@Entry
@Component
struct HomePage {
  @State newsList: NewsItem[] = []
  @State isLoading: boolean = true
  @State refreshing: boolean = false

  aboutToAppear(): void {
    this.loadData()
  }

  async loadData(): Promise<void> {
    this.isLoading = true
    try {
      // 实际项目替换为网络请求
      await new Promise<void>((resolve: Function) => setTimeout(resolve, 1000))
      this.newsList = [
        {
          id: 1,
          title: '鸿蒙 NEXT 正式发布',
          summary: 'HarmonyOS NEXT 带来全新体验...',
          imageUrl: $r('app.media.placeholder')
        }
      ]
    } catch (err) {
      console.error('加载失败:', JSON.stringify(err))
    } finally {
      this.isLoading = false
    }
  }

  onItemClick(item: NewsItem): void {
    try {
      router.pushUrl({
        url: 'pages/Detail',
        params: { id: item.id, title: item.title }
      }, router.RouterMode.Standard)
        .then((): void => { /* 跳转成功 */ })
        .catch((err: Error): void => { console.error(err.message) })
    } catch (err) {
      console.error(`路由异常: ${JSON.stringify(err)}`)
    }
  }

  build() {
    Column() {
      // 标题栏
      Row() {
        Text('新闻列表')
          .fontSize(20)
          .fontWeight(FontWeight.Bold)
          .fontColor('#1A1A1A')
      }
      .width('100%')
      .height(56)
      .padding({ left: 16, right: 16 })
      .alignItems(VerticalAlign.Center)

      // 内容区
      if (this.isLoading) {
        Column() {
          LoadingProgress()
            .width(36)
            .height(36)
            .color('#007DFF')
          Text('加载中...')
            .fontSize(14)
            .fontColor('#999')
            .margin({ top: 12 })
        }
        .width('100%')
        .layoutWeight(1)
        .justifyContent(FlexAlign.Center)
      } else if (this.newsList.length === 0) {
        Column() {
          Text('暂无数据')
            .fontSize(16)
            .fontColor('#999')
        }
        .width('100%')
        .layoutWeight(1)
        .justifyContent(FlexAlign.Center)
      } else {
        Refresh({ refreshing: $$this.refreshing }) {
          List({ space: 12 }) {
            ForEach(this.newsList, (item: NewsItem) => {
              ListItem() {
                Row({ space: 12 }) {
                  Image(item.imageUrl)
                    .width(80)
                    .height(80)
                    .borderRadius(8)
                    .objectFit(ImageFit.Cover)
                  Column({ space: 8 }) {
                    Text(item.title)
                      .fontSize(16)
                      .fontWeight(FontWeight.Medium)
                      .fontColor('#1A1A1A')
                      .maxLines(2)
                      .textOverflow({ overflow: TextOverflow.Ellipsis })
                    Text(item.summary)
                      .fontSize(13)
                      .fontColor('#999')
                      .maxLines(2)
                      .textOverflow({ overflow: TextOverflow.Ellipsis })
                  }
                  .alignItems(HorizontalAlign.Start)
                  .layoutWeight(1)
                }
                .width('100%')
                .padding(12)
                .borderRadius(8)
                .backgroundColor(Color.White)
              }
              .onClick(() => { this.onItemClick(item) })
            }, (item: NewsItem) => item.id.toString())
          }
          .padding({ left: 16, right: 16 })
          .edgeEffect(EdgeEffect.Spring)
        }
        .onRefreshing(() => {
          this.refreshing = true
          this.loadData().finally(() => { this.refreshing = false })
        })
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}
```

---

## 2. 网络请求 (HTTP)

```typescript
// services/ApiService.ets
import { http } from '@kit.NetworkKit'

interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

const BASE_URL: string = 'https://api.example.com'

export class ApiService {
  private httpRequest: http.HttpRequest

  constructor() {
    this.httpRequest = http.createHttp()
  }

  async get<T>(path: string): Promise<ApiResponse<T>> {
    try {
      const response = await this.httpRequest.request(
        `${BASE_URL}${path}`,
        {
          method: http.RequestMethod.GET,
          header: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getToken()}`
          },
          connectTimeout: 10000,
          readTimeout: 10000
        }
      )
      if (response.responseCode !== 200) {
        throw new Error(`HTTP ${response.responseCode}`)
      }
      const result: ApiResponse<T> = JSON.parse(response.result as string)
      if (result.code !== 0) {
        throw new Error(result.message)
      }
      return result
    } catch (err) {
      console.error(`请求失败 [${path}]:`, JSON.stringify(err))
      throw err
    }
  }

  async post<T>(path: string, body: Object): Promise<ApiResponse<T>> {
    try {
      const response = await this.httpRequest.request(
        `${BASE_URL}${path}`,
        {
          method: http.RequestMethod.POST,
          header: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getToken()}`
          },
          extraData: JSON.stringify(body),
          connectTimeout: 10000,
          readTimeout: 10000
        }
      )
      return JSON.parse(response.result as string) as ApiResponse<T>
    } catch (err) {
      console.error(`请求失败 [${path}]:`, JSON.stringify(err))
      throw err
    }
  }

  private getToken(): string {
    // 从 preferences 读取 token
    return ''
  }

  destroy(): void {
    this.httpRequest.destroy()
  }
}
```

---

## 3. 本地存储 (Preferences)

```typescript
// services/StorageService.ets
import { preferences } from '@kit.ArkData'
import { common } from '@kit.AbilityKit'

const STORE_NAME: string = 'app_preferences'

export class StorageService {
  private static instance: StorageService | null = null
  private store: preferences.Preferences | null = null

  static getInstance(): StorageService {
    if (!StorageService.instance) {
      StorageService.instance = new StorageService()
    }
    return StorageService.instance
  }

  async init(context: common.Context): Promise<void> {
    this.store = await preferences.getPreferences(context, STORE_NAME)
  }

  async getString(key: string, defaultValue: string = ''): Promise<string> {
    if (!this.store) { return defaultValue }
    return await this.store.get(key, defaultValue) as string
  }

  async getNumber(key: string, defaultValue: number = 0): Promise<number> {
    if (!this.store) { return defaultValue }
    return await this.store.get(key, defaultValue) as number
  }

  async getBoolean(key: string, defaultValue: boolean = false): Promise<boolean> {
    if (!this.store) { return defaultValue }
    return await this.store.get(key, defaultValue) as boolean
  }

  async put(key: string, value: preferences.ValueType): Promise<void> {
    if (!this.store) { return }
    await this.store.put(key, value)
    await this.store.flush()
  }

  async remove(key: string): Promise<void> {
    if (!this.store) { return }
    await this.store.delete(key)
    await this.store.flush()
  }
}
```

---

## 4. 传感器使用

```typescript
// services/SensorService.ets
import { sensor } from '@kit.SensorServiceKit'

interface SensorCallback {
  onData(x: number, y: number, z: number): void
  onError(code: number, message: string): void
}

export class SensorService {
  private started: boolean = false

  startAccelerometer(callback: SensorCallback, interval: number = 20000000): void {
    if (this.started) { return }
    this.started = true
    sensor.on(
      sensor.SensorId.ACCELEROMETER,
      (data: sensor.AccelerometerResponse) => {
        callback.onData(data.x, data.y, data.z)
      },
      { interval: interval }
    )
  }

  stopAccelerometer(): void {
    if (!this.started) { return }
    sensor.off(sensor.SensorId.ACCELEROMETER)
    this.started = false
  }
}
```

---

## 5. 相机预览

```typescript
// components/CameraPreview.ets
import { camera } from '@kit.CameraKit'
import { abilityAccessCtrl } from '@kit.AbilityKit'

@Component
export struct CameraPreview {
  private surfaceId: string = ''
  private cameraManager: camera.CameraManager | null = null
  @State hasPermission: boolean = false

  async aboutToAppear(): Promise<void> {
    await this.requestPermission()
    if (this.hasPermission) {
      this.initCamera()
    }
  }

  async requestPermission(): Promise<void> {
    const atManager = abilityAccessCtrl.createAtManager()
    try {
      const result = await atManager.requestPermissionsFromUser(
        getContext(), ['ohos.permission.CAMERA']
      )
      this.hasPermission = result.authResults[0] === 0
    } catch (err) {
      console.error('权限申请失败:', JSON.stringify(err))
      this.hasPermission = false
    }
  }

  async initCamera(): Promise<void> {
    this.cameraManager = camera.getCameraManager(getContext())
    // ... 相机初始化逻辑（创建预览、捕获会话等）
  }

  build() {
    if (this.hasPermission) {
      XComponent({ id: 'cameraSurface', type: XComponentType.SURFACE, libraryname: 'camera' })
        .width('100%')
        .height('100%')
        .onLoad(() => { this.initCamera() })
    } else {
      Column() {
        Text('需要相机权限')
          .fontSize(16)
          .fontColor('#999')
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
    }
  }
}
```

---

## 6. 权限管理工具

```typescript
// common/utils/PermissionUtil.ets
import { abilityAccessCtrl, Permissions } from '@kit.AbilityKit'
import { common } from '@kit.AbilityKit'

export class PermissionUtil {
  static async request(
    context: common.Context,
    permissions: Permissions[]
  ): Promise<boolean> {
    const atManager = abilityAccessCtrl.createAtManager()
    try {
      const result = await atManager.requestPermissionsFromUser(context, permissions)
      return result.authResults.every((r: number) => r === 0)
    } catch (err) {
      console.error('权限申请异常:', JSON.stringify(err))
      return false
    }
  }

  static async check(
    context: common.Context,
    permission: Permissions
  ): Promise<boolean> {
    const atManager = abilityAccessCtrl.createAtManager()
    const result = atManager.checkAccessTokenSync(
      context.applicationInfo.accessTokenId, permission
    )
    return result === abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED
  }
}
```

---

## 7. 详情页 (接收路由参数)

```typescript
// pages/Detail.ets
import { router } from '@kit.ArkUI'

interface DetailParams {
  id: number
  title: string
}

@Entry
@Component
struct Detail {
  @State title: string = ''

  aboutToAppear(): void {
    const params = router.getParams() as DetailParams
    if (params) {
      this.title = params.title
    }
  }

  onBackPress(): boolean {
    router.back()
    return true  // 拦截默认返回行为
  }

  build() {
    Column() {
      // 导航栏
      Row() {
        Button({ type: ButtonType.Circle }) {
          SymbolGlyph($r('sys.symbol.chevron_left'))
        }
        .width(40)
        .height(40)
        .backgroundColor('#00000000')
        .onClick(() => { router.back() })

        Text(this.title)
          .fontSize(18)
          .fontWeight(FontWeight.Bold)
          .layoutWeight(1)
          .textAlign(TextAlign.Center)
      }
      .width('100%')
      .height(56)
      .padding({ left: 8, right: 16 })

      // 内容
      Text('详情内容')
        .fontSize(16)
        .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}
```

---

## 8. V2 组件 (API 12+ 推荐)

```typescript
// components/CounterV2.ets
@ComponentV2
export struct Counter {
  @Param label: string = '计数'
  @Local count: number = 0
  @Event onCountChange?: (count: number) => void

  build() {
    Row({ space: 12 }) {
      Text(`${this.label}: ${this.count}`)
        .fontSize(16)

      Button('-')
        .width(36).height(36)
        .onClick(() => {
          this.count--
          this.onCountChange?.(this.count)
        })

      Button('+')
        .width(36).height(36)
        .onClick(() => {
          this.count++
          this.onCountChange?.(this.count)
        })
    }
    .padding(12)
  }
}

// 使用:
// @ComponentV2 struct Parent {
//   @Local total: number = 0
//   build() {
//     Column() {
//       Counter({
//         label: '点击次数',
//         count: this.total,      // V2 不需要 $$
//         onCountChange: (c: number) => { this.total = c }
//       })
//     }
//   }
// }
```

---

## 9. 标准目录结构生成提示

新建项目时按以下结构组织代码：

```
entry/src/main/ets/
├── entryability/
│   └── EntryAbility.ets         // UIAbility 入口
├── pages/                       // 页面（@Entry）
│   ├── Index.ets
│   └── Detail.ets
├── components/                  // 可复用组件（@Component）
│   ├── NavigationBar.ets
│   ├── LoadingView.ets
│   └── EmptyView.ets
├── viewmodel/                   // 业务状态逻辑
│   └── HomeViewModel.ets
├── model/                       // 纯数据模型
│   ├── NewsItem.ets
│   └── ApiResponse.ets
├── services/                    // 外部调用
│   ├── ApiService.ets
│   ├── StorageService.ets
│   └── SensorService.ets
└── common/
    └── utils/
        ├── PermissionUtil.ets
        └── DateUtil.ets
```

---

---

## 10. Search 搜索框

```typescript
@Component
struct SearchExample {
  @State searchValue: string = ''

  build() {
    Column({ space: 12 }) {
      // 基础搜索框
      Search({ value: this.searchValue, placeholder: '请输入搜索内容' })
        .width('90%')

      // 自定义搜索按钮文字与图标
      Search({
        value: this.searchValue,
        placeholder: '请输入搜索内容'
      })
        .searchButton('搜索', { fontSize: '16fp', fontColor: '#3789CC' })
        .searchIcon({ src: 'https://example.com/search-icon.png' })
        .width('90%')

      // 带取消按钮
      Search({
        value: this.searchValue,
        placeholder: '请输入搜索内容'
      })
        .cancelButton({
          style: CancelButtonStyle.CONSTANT,
          icon: { src: 'https://example.com/cancel-icon.png' }
        })
        .width('90%')
    }
    .width('100%')
    .padding(16)
  }
}
```

---

## 11. Swiper 轮播图

```typescript
@Component
struct SwiperExample {
  private banners: Resource[] = [
    $r('app.media.banner1'),
    $r('app.media.banner2'),
    $r('app.media.banner3')
  ]

  build() {
    Swiper() {
      ForEach(this.banners, (img: Resource) => {
        Image(img)
          .width('100%')
          .height(200)
          .objectFit(ImageFit.Cover)
          .borderRadius(12)
      })
    }
    .autoPlay(true)                     // 自动播放
    .interval(3000)                     // 3秒间隔
    .indicator(Indicator.dot())         // 圆点指示器
    .loop(true)                         // 循环播放
    .onChange((index: number) => {
      console.log(`当前第${index}张`)
    })
  }
}
```

---

## 12. Tabs 标签页切换（底部导航/顶部导航）

```typescript
@Entry
@Component
struct TabsExample {
  @State currentIndex: number = 0
  private tabTitles: string[] = ['首页', '分类', '购物车', '我的']

  // 自定义 TabBar 构建器
  @Builder
  TabBarBuilder(title: string, index: number) {
    Column({ space: 4 }) {
      Text(title)
        .fontSize(12)
        .fontColor(this.currentIndex === index ? '#007DFF' : '#999')
      // 选中指示线
      if (this.currentIndex === index) {
        Divider()
          .width(20)
          .height(3)
          .backgroundColor('#007DFF')
      }
    }
    .width('100%')
    .padding({ top: 8, bottom: 8 })
  }

  build() {
    Tabs({ barPosition: BarPosition.End }) {   // 底部导航
      TabContent() {
        Text('首页内容').fontSize(30)
      }
      .tabBar(this.TabBarBuilder('首页', 0))

      TabContent() {
        Text('分类内容').fontSize(30)
      }
      .tabBar(this.TabBarBuilder('分类', 1))

      TabContent() {
        Text('购物车内容').fontSize(30)
      }
      .tabBar(this.TabBarBuilder('购物车', 2))

      TabContent() {
        Text('我的内容').fontSize(30)
      }
      .tabBar(this.TabBarBuilder('我的', 3))
    }
    .barWidth('100%')
    .barHeight(56)
    .onChange((index: number) => {
      this.currentIndex = index
    })
  }
}
```

---

## 13. Grid 网格布局

```typescript
@Component
struct GridExample {
  private items: string[] = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

  build() {
    Grid() {
      ForEach(this.items, (item: string) => {
        GridItem() {
          Text(item)
            .fontSize(40)
            .width('100%')
            .height('100%')
            .textAlign(TextAlign.Center)
            .backgroundColor('#F0F0F0')
            .borderRadius(8)
        }
      }, (item: string) => item)
    }
    .columnsTemplate('1fr 1fr 1fr')   // 3 列等分
    .rowsTemplate('1fr 1fr 1fr')      // 3 行等分
    .columnsGap(10)                    // 列间距
    .rowsGap(10)                       // 行间距
    .width('100%')
    .height(350)
  }
}
```

---

## 14. List 列表 + 分隔线 + 滚动条

```typescript
interface ContactItem {
  name: string
  phone: string
}

@Component
struct ListExample {
  private contacts: ContactItem[] = [
    { name: '张三', phone: '13800001111' },
    { name: '李四', phone: '13800002222' },
    // ...
  ]

  build() {
    List() {
      ForEach(this.contacts, (item: ContactItem) => {
        ListItem() {
          Row({ space: 12 }) {
            Image($r('app.media.avatar'))
              .width(48)
              .height(48)
              .borderRadius(24)
            Column({ space: 4 }) {
              Text(item.name)
                .fontSize(16)
                .fontWeight(FontWeight.Medium)
              Text(item.phone)
                .fontSize(14)
                .fontColor('#999')
            }
            .alignItems(HorizontalAlign.Start)
          }
          .width('100%')
          .padding({ left: 16, right: 16, top: 12, bottom: 12 })
          .backgroundColor(Color.White)
        }
      }, (item: ContactItem) => item.phone)
    }
    .divider({
      strokeWidth: 1,
      color: '#F0F0F0',
      startMargin: 76,       // 分隔线起点缩进（绕过头像）
      endMargin: 16
    })
    .scrollBar(BarState.Auto) // 自动显示滚动条
  }
}
```

---

## 15. Scroll 滚动容器

```typescript
@Component
struct ScrollExample {
  build() {
    Scroll() {
      Column() {
        ForEach(new Array(20), (_: undefined, index: number) => {
          Text(`第 ${index + 1} 项`)
            .fontSize(16)
            .width('100%')
            .height(60)
            .backgroundColor(index % 2 === 0 ? '#F5F5F5' : Color.White)
            .textAlign(TextAlign.Center)
        })
      }
      .width('100%')
    }
    .scrollable(ScrollDirection.Vertical)  // 垂直滚动（默认）
    .scrollBar(BarState.Auto)
    .edgeEffect(EdgeEffect.Spring)         // 弹簧效果
  }
}
```

---

## 16. @Styles / @Extend 样式复用

```typescript
// === 全局 @Styles（仅支持通用属性） ===
@Styles
function cardStyle() {
  .width('100%')
  .borderRadius(12)
  .backgroundColor(Color.White)
  .padding(16)
}

// === 全局 @Extend（支持组件私有属性 + 传参） ===
@Extend(Text)
function titleText(size: number, color: ResourceColor) {
  .fontSize(size)
  .fontWeight(FontWeight.Bold)
  .fontColor(color)
}

@Extend(TextInput)
function inputStyle() {
  .width('80%')
  .height(50)
  .backgroundColor(Color.White)
  .border({ width: 1, color: Color.Gray })
  .borderRadius(8)
}

@Entry
@Component
struct StyleExample {
  // 组件内 @Styles（可访问组件状态变量）
  @State isActive: boolean = false

  @Styles
  activeStyle() {
    .backgroundColor(this.isActive ? '#007DFF' : '#CCC')
  }

  build() {
    Column({ space: 16 }) {
      Text('标题文字')
        .titleText(20, '#333')          // 使用 @Extend（传参）

      TextInput({ placeholder: '请输入手机号' })
        .inputStyle()                    // 使用 @Extend

      Text('按钮')
        .activeStyle()                   // 使用组件内 @Styles
        .fontColor(Color.White)
        .width(100).height(40)
        .textAlign(TextAlign.Center)
        .onClick(() => { this.isActive = !this.isActive })
    }
    .width('100%')
    .padding(16)
  }
}
```

---

## 17. stateStyles 多态样式（按压/禁用/焦点）

```typescript
@Entry
@Component
struct StateStylesExample {
  @State isDisabled: boolean = false

  build() {
    Column({ space: 20 }) {
      // 自定义按钮效果（用 Text + stateStyles 模拟）
      Text('删除')
        .width(100).height(50)
        .fontColor('#FFF')
        .borderRadius(25)
        .textAlign(TextAlign.Center)
        .focusable(true)
        .enabled(!this.isDisabled)
        .stateStyles({
          normal: { .backgroundColor(Color.Red) },
          pressed: { .backgroundColor('#990000') },
          disabled: { .backgroundColor('#CCC') }
        })
        .onClick(() => { console.log('clicked') })

      // 切换可用/禁用状态
      Button(this.isDisabled ? '启用' : '禁用')
        .onClick(() => { this.isDisabled = !this.isDisabled })

      Text(`当前状态: ${this.isDisabled ? '已禁用' : '正常'}`)
        .fontColor('#666')
    }
    .padding(30)
  }
}
```

---

## 18. 短信验证码倒计时

```typescript
@Entry
@Component
struct SmsVerification {
  @State buttonText: string = '获取验证码'
  @State isCounting: boolean = false
  private countdown: number = 10
  private timer: number = 0

  onSendCode(): void {
    // 防重复点击
    if (this.isCounting) return

    // 开始倒计时
    this.isCounting = true
    this.countdown--
    this.buttonText = `剩余${this.countdown}s`

    this.timer = setInterval(() => {
      if (this.countdown <= 1) {
        // 倒计时结束，还原
        clearInterval(this.timer)
        this.buttonText = '获取验证码'
        this.isCounting = false
        this.countdown = 10
        this.timer = 0
        return
      }
      this.countdown--
      this.buttonText = `剩余${this.countdown}s`
    }, 1000)

    // 调用接口发送验证码
    console.info('请求发送验证码接口...')
  }

  build() {
    Column({ space: 16 }) {
      TextInput({ placeholder: '请输入手机号' })
        .width('90%')
        .type(InputType.PhoneNumber)

      Row({ space: 12 }) {
        TextInput({ placeholder: '请输入验证码' })
          .layoutWeight(1)
          .type(InputType.Number)

        Text(this.buttonText)
          .fontSize(14)
          .fontColor(this.isCounting ? '#CCC' : '#007DFF')
          .padding({ left: 12, right: 12, top: 8, bottom: 8 })
          .border({ width: 1, color: this.isCounting ? '#CCC' : '#007DFF', style: BorderStyle.Solid })
          .borderRadius(4)
          .enabled(!this.isCounting)
          .stateStyles({
            normal: { .backgroundColor(Color.White) },
            disabled: { .backgroundColor('#F5F5F5') }
          })
          .onClick(() => { this.onSendCode() })
      }
      .width('90%')

      Button('登录')
        .type(ButtonType.Capsule)
        .width('90%')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

---

## 19. 组件通信全套（@Prop 单向 / @Link 双向 / @Provide/@Consume 跨层级）

### 父传子单向 (@Prop)

```typescript
// 子组件 components/Card.ets
@Component
export struct Card {
  @Prop title: string
  @Prop count: number = 0  // 可有默认值

  build() {
    Column() {
      Text(this.title).fontSize(18).fontWeight(FontWeight.Bold)
      Text(`数量: ${this.count}`).fontSize(14).fontColor('#999')
    }
    .padding(12)
    .borderRadius(8)
    .backgroundColor(Color.White)
  }
}

// 父组件使用
// Card({ title: '商品名称', count: 100 })
// Card({ title: '仅传标题' })  // count 用默认值
```

### 父子双向绑定 (@Link)

```typescript
// 子组件 components/Counter.ets
@Component
export struct Counter {
  @Link value: number  // 不可设默认值，父组件用 $ 传

  build() {
    Row({ space: 8 }) {
      Button('-').width(36).onClick(() => { this.value-- })
      Text(`${this.value}`).fontSize(18)
      Button('+').width(36).onClick(() => { this.value++ })
    }
  }
}

// 父组件使用
// @State count: number = 0
// Counter({ value: $count })   // 注意用 $ 不是 this.
```

### 跨层级 (@Provide / @Consume)

```typescript
// 祖先组件（爷爷 / @Entry 页面）
@Entry
@Component
struct Grandparent {
  @Provide('userName') username: string = '张三'  // 提供数据

  build() {
    Column() {
      Text('我是祖先组件')
      Parent()      // 中间层级不需要传递
    }
  }
}

// 父组件 components/Parent.ets
@Component
struct Parent {
  build() {
    Column() {
      Text('我是父组件')
      Child()
    }
  }
}

// 孙组件 components/Child.ets
@Component
struct Child {
  @Consume('userName') name: string  // 消费祖先提供的数据

  build() {
    Text(`我是孙组件，收到: ${this.name}`)
      .fontSize(16)
  }
}
```

---

## 20. Radio 单选框 / Checkbox 复选框 / Toggle 开关

```typescript
@Entry
@Component
struct FormControls {
  @State gender: string = ''
  @State hobbies: string[] = []

  build() {
    Column({ space: 20 }) {
      // === 单选框组 ===
      Text('请选择性别').fontSize(16).fontWeight(FontWeight.Bold)
      Row({ space: 20 }) {
        Row({ space: 4 }) {
          Radio({ value: 'male', group: 'gender' })
            .onChange((checked: boolean) => {
              if (checked) { this.gender = 'male' }
            })
          Text('男')
        }
        Row({ space: 4 }) {
          Radio({ value: 'female', group: 'gender' })
            .onChange((checked: boolean) => {
              if (checked) { this.gender = 'female' }
            })
          Text('女')
        }
      }

      // === 复选框组（带全选） ===
      Text('请选择爱好').fontSize(16).fontWeight(FontWeight.Bold)
      Row({ space: 8 }) {
        CheckboxGroup({ group: 'hobby' })
          .onChange((ev: CheckboxGroupResult) => {
            this.hobbies = ev.name
          })
        Text('全选')
      }
      Row({ space: 12 }) {
        Checkbox({ name: '篮球', group: 'hobby' })
        Text('篮球')
        Checkbox({ name: '足球', group: 'hobby' })
        Text('足球')
        Checkbox({ name: '游泳', group: 'hobby' })
        Text('游泳')
      }

      // === 开关 ===
      Row({ space: 8 }) {
        Toggle({ type: ToggleType.Switch, isOn: false })
          .selectedColor('#007DFF')
          .onChange((isOn: boolean) => {
            console.log(isOn ? '打开' : '关闭')
          })
        Text('开启通知')
      }

      Text(`性别: ${this.gender}, 爱好: ${this.hobbies.join(', ')}`)
        .fontSize(14).fontColor('#666')
    }
    .alignItems(HorizontalAlign.Start)
    .width('100%')
    .padding(20)
  }
}
```

---

## 21. Progress 进度条

```typescript
@Component
struct ProgressExample {
  build() {
    Column({ space: 20 }) {
      // 线性进度条
      Progress({ value: 60, total: 100, type: ProgressType.Linear })
        .width(300).height(50)

      // 环形进度条
      Progress({ value: 40, total: 150, type: ProgressType.Ring })
        .width(100).height(100)
        .color(Color.Grey)
        .style({ strokeWidth: 15 })

      // 圆形进度条
      Progress({ value: 20, total: 150, type: ProgressType.Eclipse })
        .width(100).height(100)

      // 胶囊进度条
      Progress({ value: 50, total: 150, type: ProgressType.Capsule })
        .width(100).height(50)
        .color(Color.Blue)
        .backgroundColor(Color.Gray)
    }
    .width('100%')
    .padding(20)
  }
}
```

---

## 22. DatePicker 日期选择器

```typescript
@Entry
@Component
struct DatePickerExample {
  @State selectedDate: Date = new Date()

  build() {
    Column({ space: 16 }) {
      Text(`选中日期: ${this.selectedDate.getFullYear()}年${this.selectedDate.getMonth() + 1}月${this.selectedDate.getDate()}日`)
        .fontSize(18)

      DatePicker({
        selected: this.selectedDate,
        start: new Date('1970-1-1'),
        end: new Date('2100-1-1')
      })
        .onDateChange((value: Date) => {
          this.selectedDate = value
          console.info('日期变更: ' + this.selectedDate.toString())
        })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

---

## 23. 华为登录页（综合实战）

```typescript
// entry/src/main/resources/base/element/string.json
// { "string": [{ "name": "login_title", "value": "华为账号登录" }] }

@Entry
@Component
struct HuaweiLogin {
  @State phoneNumber: string = ''
  @State password: string = ''

  build() {
    Column() {
      // Logo
      Image($r('app.media.w1'))
        .width(150).height(150)

      Text($r('app.string.login_title'))
        .fontSize(25)
        .fontWeight(FontWeight.Bold)

      Text('登录账号以使用更多服务')
        .fontSize(15)
        .fontColor('gray')
        .margin({ top: 8 })

      // 手机号输入
      TextInput({ placeholder: '请输入手机号', text: $$this.phoneNumber })
        .type(InputType.PhoneNumber)
        .width('85%')
        .height(48)
        .backgroundColor(Color.White)
        .borderRadius(8)
        .margin({ top: 40, bottom: 12 })

      // 密码输入
      TextInput({ placeholder: '请输入密码', text: $$this.password })
        .type(InputType.Password)
        .width('85%')
        .height(48)
        .backgroundColor(Color.White)
        .borderRadius(8)

      // 辅助链接
      Row() {
        Text('短信验证码登录')
          .fontColor('#0066CC')
          .fontWeight(FontWeight.Bold)
          .fontSize(14)
        Text('忘记密码')
          .fontColor('#0066CC')
          .fontWeight(FontWeight.Bold)
          .fontSize(14)
      }
      .width('85%')
      .margin({ top: 16 })
      .justifyContent(FlexAlign.SpaceBetween)

      // 登录按钮
      Button('登录')
        .type(ButtonType.Capsule)
        .width('85%')
        .height(48)
        .fontSize(18)
        .backgroundColor('#0066CC')
        .margin({ top: 80 })

      // 第三方登录
      Row({ space: 16 }) {
        Button() { Text('方式1').fontSize(13) }
          .type(ButtonType.Circle).width(44).height(44)
          .backgroundColor(Color.White).borderWidth(1).borderColor('#0066CC')

        Button() { Text('方式2').fontSize(13) }
          .type(ButtonType.Circle).width(44).height(44)
          .backgroundColor(Color.White).borderWidth(1).borderColor('#0066CC')

        Button() { Text('方式3').fontSize(13) }
          .type(ButtonType.Circle).width(44).height(44)
          .backgroundColor(Color.White).borderWidth(1).borderColor('#0066CC')
      }
      .margin({ top: 40 })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
    .alignItems(HorizontalAlign.Center)
  }
}
```

---

---

## 24. 图形绘制综合示例 (Circle / Ellipse / Line / Polyline / Polygon / Rect / Path)

```typescript
@Entry
@Component
struct ShapeDrawingExample {
  build() {
    Scroll() {
      Column({ space: 20 }) {
        Text('图形绘制示例').fontSize(20).fontWeight(FontWeight.Bold)

        // === 圆形 ===
        Text('Circle 圆形').fontSize(14).fontColor('#666')
        Circle({ width: 120, height: 120 })
          .fill(Color.Pink)
          .fillOpacity(0.6)
          .stroke(Color.Red)
          .strokeWidth(4)
          .strokeDashArray([8, 4])

        // === 椭圆 ===
        Text('Ellipse 椭圆').fontSize(14).fontColor('#666')
        Ellipse({ width: 200, height: 100 })
          .fill(Color.Orange)
          .fillOpacity(0.4)
          .stroke(Color.Blue)
          .strokeWidth(3)

        // === 直线 ===
        Text('Line 直线').fontSize(14).fontColor('#666')
        Line()
          .width(300)
          .height(50)
          .startPoint([0, 25])
          .endPoint([280, 25])
          .stroke(Color.Red)
          .strokeWidth(4)
          .strokeLineCap(LineCapStyle.Round)

        // === 折线 ===
        Text('Polyline 折线').fontSize(14).fontColor('#666')
        Polyline({ width: 300, height: 200 })
          .points([[30, 160], [100, 20], [180, 180], [270, 40]])
          .fillOpacity(0)
          .stroke(Color.Blue)
          .strokeWidth(4)
          .strokeLineJoin(LineJoinStyle.Round)
          .strokeLineCap(LineCapStyle.Round)

        // === 多边形 ===
        Text('Polygon 多边形').fontSize(14).fontColor('#666')
        Polygon({ width: 200, height: 200 })
          .points([[100, 10], [10, 150], [190, 150]])
          .fill(Color.Green)
          .fillOpacity(0.3)
          .stroke(Color.Green)
          .strokeWidth(3)

        // === 矩形（带圆角） ===
        Text('Rect 矩形').fontSize(14).fontColor('#666')
        Rect({ width: '80%', height: 80 })
          .radius([[30, 30], [10, 10], [30, 30], [10, 10]])
          .fill(Color.Purple)
          .fillOpacity(0.3)
          .stroke(Color.Purple)
          .strokeWidth(3)

        // === Path 路径 ===
        Text('Path 路径（三角形+正方形+弧线）').fontSize(14).fontColor('#666')
        // 三角形
        Path()
          .width('200px').height('150px')
          .commands('M100 0 L200 120 L0 120 Z')
          .fillOpacity(0)
          .stroke(Color.Red)
          .strokeWidth(2)
        // 正方形
        Path()
          .width('200px').height('200px')
          .commands('M0 0 H120 V120 H0 Z')
          .fillOpacity(0)
          .stroke(Color.Blue)
          .strokeWidth(2)
        // 弧线
        Path()
          .width('250px').height('200px')
          .commands('M0 150 S100 0 240 150 Z')
          .fillOpacity(0)
          .stroke(Color.Green)
          .strokeWidth(2)
      }
      .width('100%')
      .alignItems(HorizontalAlign.Center)
      .padding(16)
    }
    .scrollable(ScrollDirection.Vertical)
  }
}
```

---

## 25. 标题栏三种模式 (ComposeTitleBar / SelectTitleBar / TabTitleBar)

```typescript
import { ComposeTitleBar, SelectTitleBar, TabTitleBar, promptAction,
  ComposeTitleBarMenuItem, SelectTitleBarMenuItem, TabTitleBarTabItem, TabTitleBarMenuItem } from '@kit.ArkUI'

@Entry
@Component
struct TitleBarExample {
  @State selectedIndex: number = 0

  // TabTitleBar 关联的页面内容
  @Builder
  swiperContent() {
    Text('页签1 内容')
      .fontSize(16).width('100%').height(200)
      .textAlign(TextAlign.Center)
      .backgroundColor('#1ABC9C').fontColor(Color.White)
    Text('页签2 内容')
      .fontSize(16).width('100%').height(200)
      .textAlign(TextAlign.Center)
      .backgroundColor('#3498DB').fontColor(Color.White)
    Text('页签3 内容')
      .fontSize(16).width('100%').height(200)
      .textAlign(TextAlign.Center)
      .backgroundColor('#9B59B6').fontColor(Color.White)
  }

  build() {
    Column() {
      // === ComposeTitleBar 普通标题栏 ===
      ComposeTitleBar({
        title: '我的页面',
        subtitle: 'user@example.com',
        menuItems: [{
          value: $r('app.media.startIcon'),
          isEnabled: true,
          action: () => { promptAction.showToast({ message: '菜单点击' }) }
        }]
      })

      Divider().strokeWidth(1).color('#E0E0E0')

      // === SelectTitleBar 下拉切换标题栏 ===
      SelectTitleBar({
        selected: this.selectedIndex,
        options: [
          { value: '全部内容' },
          { value: '本地文件' },
          { value: '云存档' }
        ],
        onSelected: (index: number) => {
          this.selectedIndex = index
          console.log(`切换到: ${index}`)
        },
        hidesBackButton: false,
        subtitle: '3项可选',
        menuItems: [{
          value: $r('app.media.startIcon'),
          isEnabled: true,
          action: () => { promptAction.showToast({ message: '操作' }) }
        }]
      })

      Divider().strokeWidth(1).color('#E0E0E0')

      // === TabTitleBar 页签型标题栏（仅一级页面） ===
      TabTitleBar({
        tabItems: [
          { title: '页签1' },
          { title: '页签2' },
          { title: '页签3', icon: $r('app.media.startIcon') }
        ],
        swiperContent: this.swiperContent,
        menuItems: [
          {
            value: $r('app.media.startIcon'),
            isEnabled: true,
            action: () => { promptAction.showToast({ message: '右上操作' }) }
          }
        ]
      })
    }
    .width('100%')
    .height('100%')
  }
}
```

---

## 26. 通用属性综合示例 (layoutWeight / direction / position / offset / aspectRatio)

```typescript
@Entry
@Component
struct UniversalAttrExample {
  build() {
    Scroll() {
      Column({ space: 24 }) {
        Text('通用属性示例').fontSize(20).fontWeight(FontWeight.Bold)

        // === layoutWeight 权重分配 ===
        Text('layoutWeight 权重').fontSize(14).fontColor('#666')
        Row() {
          Text('权重1').width('30%').height(50).backgroundColor(0xFFEFD5)
            .textAlign(TextAlign.Center).layoutWeight(1)
          Text('权重2').width('30%').height(50).backgroundColor(0xF5DEB3)
            .textAlign(TextAlign.Center).layoutWeight(2)
          Text('无权重').width('30%').height(50).backgroundColor(0xD2B48C)
            .textAlign(TextAlign.Center)
        }
        .width('90%').height(60).backgroundColor(0xAFEEEE)

        // === direction 布局方向 ===
        Text('direction Rtl 从右到左').fontSize(14).fontColor('#666')
        Row() {
          Text('1').height(40).width('20%').backgroundColor(0xF5DEB3).textAlign(TextAlign.Center)
          Text('2').height(40).width('20%').backgroundColor(0xD2B48C).textAlign(TextAlign.Center)
          Text('3').height(40).width('20%').backgroundColor(0xF5DEB3).textAlign(TextAlign.Center)
        }
        .width('90%')
        .direction(Direction.Rtl)

        // === position 绝对定位 ===
        Text('position 绝对定位').fontSize(14).fontColor('#666')
        Row() {
          Text('默认内容').fontSize(16)
          Text('定位').size({ width: '60%', height: 30 }).backgroundColor(0xbbb2cb)
            .fontSize(16).position({ x: 30, y: 10 })
        }
        .width('90%').height(60).backgroundColor(Color.Gray)

        // === offset 相对偏移 ===
        Text('offset 相对偏移').fontSize(14).fontColor('#666')
        Row() {
          Text('1').size({ width: '15%', height: 50 }).backgroundColor(0xdeb887)
          Text('2 offset(15,30)').size({ width: 120, height: 50 }).backgroundColor(0xbbb2cb)
            .offset({ x: 15, y: 30 })
        }
        .width('90%').height(100).backgroundColor(Color.Gray)

        // === aspectRatio 宽高比 ===
        Text('aspectRatio 宽高比').fontSize(14).fontColor('#666')
        Row({ space: 12 }) {
          Text('1').backgroundColor(0xbbb2cb).fontSize(14)
            .aspectRatio(1.5).height(60)      // width = 60*1.5 = 90
          Text('2').backgroundColor(0xbbb2cb).fontSize(14)
            .aspectRatio(1.5).width(60)        // height = 60/1.5 = 40
        }

        // === displayPriority 显示优先级 ===
        Text('displayPriority（缩窄窗口看效果）').fontSize(14).fontColor('#666')
        Flex({ justifyContent: FlexAlign.SpaceBetween }) {
          Text('高优先级').width(120).height(50).fontSize(14).backgroundColor(0xbbb2cb)
            .textAlign(TextAlign.Center).displayPriority(2)
          Text('中优先级').width(120).height(50).fontSize(14).backgroundColor(0xAFEEEE)
            .textAlign(TextAlign.Center).displayPriority(1)
          Text('低优先级').width(120).height(50).fontSize(14).backgroundColor(0xF5DEB3)
            .textAlign(TextAlign.Center).displayPriority(1)
        }
        .width('90%')

        // === constraintSize 约束尺寸 ===
        Text('constraintSize 约束').fontSize(14).fontColor('#666')
        Text('这是一段很长的文字用来测试约束尺寸的效果看看它是如何在限定范围内变化的')
          .constraintSize({ maxWidth: 200, maxHeight: 80, minHeight: 40 })
          .backgroundColor(Color.Pink)
          .fontSize(14)
      }
      .width('100%')
      .alignItems(HorizontalAlign.Center)
      .padding(16)
    }
  }
}
```

---

## 27. 图形变换 + 动画 (rotate / translate / scale + animateTo)

```typescript
@Entry
@Component
struct TransformExample {
  @State angle: number = 0
  @State offsetX: number = 0
  @State scaleVal: number = 1
  @State isAnimating: boolean = false
  private timer: number = 0

  startAnimation(): void {
    if (this.isAnimating) { return }
    this.isAnimating = true
    this.timer = setInterval(() => {
      this.getUIContext().animateTo({ duration: 100, curve: Curve.Linear }, () => {
        this.angle += 10
        this.offsetX = (this.offsetX + 5) % 200
        this.scaleVal = this.scaleVal >= 2 ? 0.5 : this.scaleVal + 0.01
      })
    }, 100)
  }

  stopAnimation(): void {
    clearInterval(this.timer)
    this.timer = 0
    this.isAnimating = false
  }

  build() {
    Column({ space: 30 }) {
      Text('图形变换示例').fontSize(20).fontWeight(FontWeight.Bold)

      Row() {
        Row().size({ width: 100, height: 100 }).backgroundColor(Color.Pink)
          .rotate({
            x: 0, y: 0, z: 1,
            angle: this.angle,
            centerX: '50%', centerY: '50%'
          })
          .translate({ x: this.offsetX, y: 0, z: 0 })
          .scale({
            x: this.scaleVal, y: this.scaleVal,
            centerX: '50%', centerY: '50%'
          })
      }
      .width(300).height(150)
      .justifyContent(FlexAlign.Center)
      .backgroundColor(0xF5F5F5)
      .borderRadius(8)

      Button(this.isAnimating ? '停止' : '开始动画')
        .onClick(() => {
          if (this.isAnimating) { this.stopAnimation() }
          else { this.startAnimation() }
        })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
  }

  aboutToDisappear(): void {
    if (this.timer !== 0) { clearInterval(this.timer) }
  }
}
```

---

## 28. 裁剪与遮罩 (clip / clipShape / maskShape)

```typescript
@Entry
@Component
struct ClipMaskExample {
  build() {
    Column({ space: 24 }) {
      Text('裁剪与遮罩示例').fontSize(20).fontWeight(FontWeight.Bold)

      // === clip 边缘裁剪 ===
      Text('clip(true) 圆角裁剪').fontSize(14).fontColor('#666')
      Row() {
        Image('https://via.placeholder.com/500x280/FF6B6B/FFFFFF?text=Clip')
          .width('500px').height('280px')
      }
      .clip(true)
      .borderRadius(20)
      .width(200).height(200)

      // === clipShape 圆形裁剪 ===
      Text('clipShape 圆形裁剪').fontSize(14).fontColor('#666')
      Row() {
        Image('https://via.placeholder.com/500x280/4ECDC4/FFFFFF?text=Circle')
          .width('500px').height('280px')
      }
      .clipShape(new Circle({ width: '140px', height: '140px' }))
      .width(140).height(140)

      // === maskShape 矩形遮罩 ===
      Text('maskShape 矩形遮罩').fontSize(14).fontColor('#666')
      Row() {
        Image('https://via.placeholder.com/500x280/45B7D1/FFFFFF?text=Mask')
          .width('500px').height('280px')
      }
      .maskShape(new Rect({ width: '200px', height: '150px' }).fill(Color.Gray))
      .width(200).height(150)
    }
    .width('100%')
    .alignItems(HorizontalAlign.Center)
    .padding(16)
  }
}
```

---

---

## 29. Span / ImageSpan / ContainerSpan 行内富文本

```typescript
@Entry
@Component
struct SpanExample {
  build() {
    Column({ space: 20 }) {
      Text('Span 富文本示例').fontSize(20).fontWeight(FontWeight.Bold)

      // === 基础 Span: 不同样式文本 ===
      Text() {
        Span('红字').fontColor(Color.Red).fontSize(18)
        Span(' + 蓝粗体').fontColor(Color.Blue).fontWeight(FontWeight.Bold)
        Span(' + 删除线').decoration({ type: TextDecorationType.LineThrough, color: Color.Red })
      }
      .borderWidth(1).padding(10)

      // === Span 大小写 ===
      Text() {
        Span('I am Upper-span').fontSize(12)
          .textCase(TextCase.UpperCase)
        Span(' | I am default span').fontSize(12)
      }
      .borderWidth(1).padding(10)

      // === ImageSpan: 行内图片 ===
      Text() {
        ImageSpan('https://via.placeholder.com/40')
          .width(40).height(40)
          .verticalAlign(ImageSpanAlignment.CENTER)
        Span('  图文混排示例  ')
      }
      .borderWidth(1).padding(10)

      // === ContainerSpan: 统一背景 ===
      Text() {
        ContainerSpan() {
          ImageSpan('https://via.placeholder.com/40')
            .width(40).height(40)
            .verticalAlign(ImageSpanAlignment.CENTER)
          Span('  带背景的富文本  ').fontSize(16).fontColor(Color.White)
        }.textBackgroundStyle({ color: '#7F007DFF', radius: '12vp' })
      }
      .padding(10)
    }
    .width('100%')
    .padding(16)
  }
}
```

---

## 30. Flex 弹性布局综合示例

```typescript
@Entry
@Component
struct FlexLayoutExample {
  build() {
    Scroll() {
      Column({ space: 24 }) {
        Text('Flex 弹性布局').fontSize(20).fontWeight(FontWeight.Bold)

        // === 主轴方向 + 换行 ===
        Text('FlexDirection.Row + Wrap').fontSize(14).fontColor('#666')
        Flex({ wrap: FlexWrap.Wrap }) {
          Text('1').width('50%').height(40).backgroundColor(Color.Green).textAlign(TextAlign.Center)
          Text('2').width('50%').height(40).backgroundColor(Color.Red).textAlign(TextAlign.Center)
          Text('3').width('50%').height(40).backgroundColor(Color.Blue).textAlign(TextAlign.Center)
        }
        .width('100%').backgroundColor('#ccc')

        // === 主轴对齐 ===
        Text('justifyContent: SpaceAround').fontSize(14).fontColor('#666')
        Flex({ justifyContent: FlexAlign.SpaceAround }) {
          Text('A').width(50).height(50).backgroundColor(Color.Green).textAlign(TextAlign.Center)
          Text('B').width(50).height(50).backgroundColor(Color.Red).textAlign(TextAlign.Center)
          Text('C').width(50).height(50).backgroundColor(Color.Blue).textAlign(TextAlign.Center)
        }
        .width('100%').height(80).backgroundColor('#ccc')

        // === 交叉轴对齐 ===
        Text('alignItems: Center (Column direction)').fontSize(14).fontColor('#666')
        Flex({ direction: FlexDirection.Column, alignItems: ItemAlign.Center }) {
          Text('短').width(50).height(30).backgroundColor(Color.Green)
          Text('中等长度').width(80).height(30).backgroundColor(Color.Red)
          Text('比较长的文本').width(120).height(30).backgroundColor(Color.Blue)
        }
        .width('100%').height(120).backgroundColor('#ccc')

        // === alignSelf 子元素覆盖 ===
        Text('alignSelf 覆盖容器 alignItems').fontSize(14).fontColor('#666')
        Flex({ direction: FlexDirection.Row, alignItems: ItemAlign.Center }) {
          Text('居中').width('25%').height(60).backgroundColor('#a1b2c3').textAlign(TextAlign.Center)
          Text('顶部').width('25%').height(60).backgroundColor('#a2d3d1')
            .textAlign(TextAlign.Center)
            .alignSelf(ItemAlign.Start)
          Text('居中').width('25%').height(80).backgroundColor('#a1b2c3').textAlign(TextAlign.Center)
          Text('居中').width('25%').height(80).backgroundColor('#a2d3d1').textAlign(TextAlign.Center)
        }
        .width('100%').height(120).backgroundColor('#a4a1')

        // === alignContent 多行对齐 ===
        Text('alignContent: SpaceBetween (多行)').fontSize(14).fontColor('#666')
        Flex({ justifyContent: FlexAlign.SpaceBetween, wrap: FlexWrap.Wrap, alignContent: FlexAlign.SpaceBetween }) {
          Text('1').width('30%').height(20).backgroundColor(0xF5DEB3).textAlign(TextAlign.Center)
          Text('2').width('60%').height(20).backgroundColor(0xD2B48C).textAlign(TextAlign.Center)
          Text('3').width('40%').height(20).backgroundColor(0xD2B48C).textAlign(TextAlign.Center)
          Text('4').width('30%').height(20).backgroundColor(0xF5DEB3).textAlign(TextAlign.Center)
          Text('5').width('20%').height(20).backgroundColor(0xD2B48C).textAlign(TextAlign.Center)
        }
        .width('100%').height(120).backgroundColor(0xAFEEEE)
      }
      .width('100%')
      .alignItems(HorizontalAlign.Center)
      .padding(16)
    }
  }
}
```

---

## 31. GridRow 响应式栅格布局

```typescript
@Entry
@Component
struct GridRowExample {
  private products: string[] = ['商品1', '商品2', '商品3', '商品4', '商品5', '商品6', '商品7', '商品8', '商品9', '商品10', '商品11', '商品12']

  build() {
    Column({ space: 16 }) {
      Text('GridRow 响应式栅格').fontSize(20).fontWeight(FontWeight.Bold)

      // 不同断点不同列数: xs=1列, sm=2列, md=4列, lg=6列
      GridRow({
        columns: { xs: 1, sm: 2, md: 4, lg: 6 },
        gutter: { x: 12, y: 12 },
        breakpoints: { value: ['320vp', '520vp', '840vp'] }
      }) {
        ForEach(this.products, (item: string, index: number) => {
          GridCol() {
            Text(item)
              .width('100%')
              .height(60)
              .fontSize(14)
              .backgroundColor(index % 2 === 0 ? '#1ABC9C' : '#3498DB')
              .fontColor(Color.White)
              .textAlign(TextAlign.Center)
              .borderRadius(8)
          }
        }, (item: string, index: number) => index.toString())
      }

      Text('⚠️ Previewer不支持GridRow/GridCol，请用真机/模拟器测试')
        .fontSize(12).fontColor('#999')
    }
    .width('100%')
    .padding(16)
  }
}
```

---

## 32. Stack 层叠布局 + 悬浮按钮 + Toggle 开关

```typescript
@Entry
@Component
struct StackFloatingExample {
  @State isOn: boolean = false

  build() {
    Column() {
      // === Stack 层叠布局 ===
      Stack({ alignContent: Alignment.BottomEnd }) {
        // 底层背景
        Column()
          .width('90%').height(200)
          .backgroundColor('#58b87c')
          .borderRadius(12)

        // 中间层文字
        Text('层叠内容')
          .fontSize(18).fontColor(Color.White)

        // 顶层 - 右下角悬浮按钮
        Button('+')
          .width(48).height(48)
          .type(ButtonType.Circle)
          .fontSize(24)
          .margin(12)
          .zIndex(3)
      }
      .width('100%')
      .height(220)

      Divider().margin({ top: 20, bottom: 20 })

      // === Toggle 开关 ===
      Row({ space: 12 }) {
        Toggle({ type: ToggleType.Switch, isOn: this.isOn })
          .selectedColor('#007DFF')
          .onChange((value: boolean) => {
            this.isOn = value
          })
        Text(`通知已${this.isOn ? '开启' : '关闭'}`).fontSize(16)

        Toggle({ type: ToggleType.Checkbox, isOn: false })
          .selectedColor(Color.Red)

        Toggle({ type: ToggleType.Button, isOn: false }) {
          Text('按钮模式')
        }
        .selectedColor('#007DFF')
      }
    }
    .width('100%')
    .padding(16)
  }
}
```

---

## 33. 路由返回确认框 + 返回指定页面

```typescript
// pages/Payment.ets
import { router, ComposeTitleBar } from '@kit.ArkUI'

@Entry
@Component
struct Payment {
  @State amount: string = '99.00'

  aboutToAppear(): void {
    // 从路由参数获取金额
    const params = router.getParams() as Record<string, Object>
    if (params && params['amount'] !== undefined) {
      this.amount = params['amount'] as string
    }
  }

  build() {
    Column() {
      // 标题栏
      ComposeTitleBar({ title: '支付确认' })
        .width('100%')

      Column({ space: 20 }) {
        Text(`支付金额：¥${this.amount}`)
          .fontSize(24).fontWeight(FontWeight.Bold)

        // 确认支付
        Button('确认支付').width('80%')
          .onClick(() => {
            router.pushUrl({ url: 'pages/Result' })
          })

        // 返回按钮 — 弹出询问框
        Button('返回').width('80%')
          .backgroundColor('#ccc')
          .onClick(() => {
            router.showAlertBeforeBackPage({
              message: '您还没有完成支付，确定要返回吗？'
            })
            router.back()  // ← 会先弹确认框
          })
      }
      .width('100%')
      .layoutWeight(1)
      .justifyContent(FlexAlign.Center)
    }
    .width('100%')
    .height('100%')
  }
}
```

---

## 34. Tabs 底部导航（组件化，从 day7 项目提炼）

```typescript
// pages/Index.ets — 主页面，用 Tabs 承载 5 个独立组件
import HomeTab from '../components/HomeTab'
import DiscoverTab from '../components/DiscoverTab'
import VipTab from '../components/VipTab'
import PlanetTab from '../components/PlanetTab'
import MineTab from '../components/MineTab'

@Entry
@Component
struct MainPage {
  build() {
    Tabs() {
      TabContent() { HomeTab() }.tabBar('首页')
      TabContent() { DiscoverTab() }.tabBar('发现')
      TabContent() { VipTab() }.tabBar('VIP')
      TabContent() { PlanetTab() }.tabBar('星球')
      TabContent() { MineTab() }.tabBar('我的')
    }
    .barPosition(BarPosition.End)  // 底部导航
  }
}

// components/HomeTab.ets — 首页内容（含 Grid 导航）
import { router } from '@kit.ArkUI'

@Component
struct HomeTab {
  @State items: string[] = ['直播', '动漫', '体育', '小小优酷', '榜单']

  build() {
    Column() {
      // 图标导航栏（单行 5 列）
      Grid() {
        ForEach(this.items, (item: string, index: number) => {
          GridItem() {
            Column({ space: 4 }) {
              Image($r('app.media.startIcon'))
                .width(50).height(50)
                .borderRadius('50%')
              Text(item).fontSize(12)
            }
          }
          .onClick(() => {
            router.pushUrl({
              url: 'pages/Page' + String.fromCharCode('a'.charCodeAt(0) + index),
              params: { title: item }
            })
          })
        }, (item: string) => item)
      }
      .columnsTemplate('1fr 1fr 1fr 1fr 1fr')
      .rowsTemplate('1fr')
      .width('100%')
      .height(100)

      // 内容网格（2 列）
      Grid() {
        ForEach(this.items, (item: string) => {
          GridItem() {
            Column() {
              Image($r('app.media.startIcon'))
                .width('100%').height(100)
              Text(item).fontSize(14)
            }
          }
          .onClick(() => {
            router.pushUrl({
              url: 'pages/Movie',
              params: { title: item }
            })
          })
        }, (item: string) => item)
      }
      .columnsTemplate('1fr 1fr')
      .width('100%')
      .height(0).layoutWeight(1)
    }
    .width('100%')
    .height('100%')
  }
}
export default HomeTab
```

> **关键点**：
> 1. 每个 Tab 的内容拆成独立组件放在 `components/` 目录，用 `export default` 导出
> 2. 主页面用 `import Xxx from '../components/Xxx'` 默认导入
> 3. `barPosition(BarPosition.End)` 将页签栏定位到底部
> 4. `Grid` 必须声明宽高，第二个 Grid 用 `height(0).layoutWeight(1)` 占满剩余空间

---

## 35. 电影详情页 — 路由参数接收（来自 day7 Movie.ets）

```typescript
// pages/Movie.ets — 从首页 Grid 跳转过来，接收 params.title 展示详情
import { router, ComposeTitleBar } from '@kit.ArkUI'

@Entry
@Component
struct MovieDetail {
  @State movieTitle: string = ''
  @State isLoading: boolean = true

  aboutToAppear(): void {
    this.receiveParams()
  }

  receiveParams(): void {
    try {
      const params = router.getParams() as Record<string, Object>
      if (params && params['title'] !== undefined) {
        this.movieTitle = params['title'] as string
      } else {
        this.movieTitle = '未知影片'
      }
    } catch (err) {
      console.error(`获取路由参数失败: ${JSON.stringify(err)}`)
      this.movieTitle = '参数获取失败'
    }
    this.isLoading = false
  }

  build() {
    Column() {
      ComposeTitleBar({ title: '影片详情' })
        .width('100%')

      if (this.isLoading) {
        Column() {
          LoadingProgress()
            .width(40).height(40)
            .color('#007DFF')
          Text('加载中...')
            .fontSize(14)
            .fontColor('#999')
            .margin({ top: 10 })
        }
        .width('100%')
        .height(0).layoutWeight(1)
        .justifyContent(FlexAlign.Center)
      } else {
        Column({ space: 20 }) {
          // 影片封面
          Image($r('app.media.startIcon'))
            .width('80%')
            .height(200)
            .borderRadius(12)
            .objectFit(ImageFit.Cover)

          // 影片标题（从路由参数获取）
          Text(`《${this.movieTitle}》`)
            .fontSize(24)
            .fontWeight(FontWeight.Bold)
            .fontColor('#333333')

          // 影片描述
          Text(`${this.movieTitle} 是一部精彩的影片，点击下方按钮可查看播放详情。`)
            .fontSize(15)
            .fontColor('#666666')
            .maxLines(3)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
            .width('85%')
            .textAlign(TextAlign.Center)
        }
        .width('100%')
        .height(0).layoutWeight(1)
        .justifyContent(FlexAlign.Center)
        .padding({ left: 20, right: 20 })
      }
    }
    .width('100%')
    .height('100%')
  }
}
```

> **关键点**：
> 1. `router.getParams()` 返回 `Object | undefined`，**必须先判空**再访问属性
> 2. 用 `as Record<string, Object>` 类型断言后通过 `params['key']` 安全取值
> 3. 路由参数在 `aboutToAppear()` 中获取，赋值给 `@State` 变量驱动 UI 更新
> 4. 整段逻辑包裹在 `try-catch` 中，防止路由异常导致页面崩溃

---

## 36. 完整视频 App 架构（Tabs + Grid + 路由传参 + 详情页）

```typescript
// ==========================================
// 文件 1: pages/Index.ets — 主框架（Tabs 导航）
// ==========================================
import HomeTab from '../components/HomeTab'
import DiscoverTab from '../components/DiscoverTab'
import VipTab from '../components/VipTab'
import PlanetTab from '../components/PlanetTab'
import MineTab from '../components/MineTab'

@Entry
@Component
struct MainFrame {
  build() {
    Tabs() {
      TabContent() { HomeTab() }.tabBar('首页')
      TabContent() { DiscoverTab() }.tabBar('发现')
      TabContent() { VipTab() }.tabBar('VIP')
      TabContent() { PlanetTab() }.tabBar('星球')
      TabContent() { MineTab() }.tabBar('我的')
    }
    .barPosition(BarPosition.End)
  }
}

// ==========================================
// 文件 2: components/HomeTab.ets — 首页内容
// ==========================================
import { router } from '@kit.ArkUI'

@Component
struct HomeTab {
  // 图标导航数据
  @State categories: Array<{ name: string; page: string }> = [
    { name: '直播', page: 'pages/Pagea' },
    { name: '动漫', page: 'pages/Pageb' },
    { name: '体育', page: 'pages/Pagec' },
    { name: '小小优酷', page: 'pages/Paged' },
    { name: '榜单', page: 'pages/Pagee' }
  ]

  // 影片列表数据
  @State videos: string[] = [
    '大江大河', '大帅哥', '我的保姆手册',
    '经典电影4', '经典电影5', '经典电影6'
  ]

  navigateTo(url: string, title: string): void {
    try {
      router.pushUrl({
        url: url,
        params: { title: title }
      }, router.RouterMode.Standard)
    } catch (err) {
      console.error(`路由跳转异常: ${JSON.stringify(err)}`)
    }
  }

  build() {
    Column() {
      // ===== 第一层：5列图标导航栏 =====
      Grid() {
        ForEach(this.categories, (item: { name: string; page: string }) => {
          GridItem() {
            Column({ space: 4 }) {
              Image($r('app.media.startIcon'))
                .width(50).height(50)
                .borderRadius('50%')
              Text(item.name)
                .fontSize(12)
                .fontColor('#333333')
            }
          }
          .onClick(() => { this.navigateTo(item.page, item.name) })
        }, (item: { name: string; page: string }) => item.name)
      }
      .columnsTemplate('1fr 1fr 1fr 1fr 1fr')
      .rowsTemplate('1fr')
      .width('100%')
      .height(100)
      .padding({ top: 10, bottom: 10 })

      // ===== 第二层：2列影片列表 =====
      Grid() {
        ForEach(this.videos, (item: string) => {
          GridItem() {
            Column() {
              Image($r('app.media.startIcon'))
                .width('100%')
                .height(100)
                .borderRadius({ topLeft: 8, topRight: 8 })
                .objectFit(ImageFit.Cover)
              Text(item)
                .fontSize(14)
                .fontColor('#333333')
                .padding({ top: 6, bottom: 6, left: 8, right: 8 })
            }
            .backgroundColor(Color.White)
            .borderRadius(8)
          }
          .onClick(() => { this.navigateTo('pages/Movie', item) })
        }, (item: string) => item)
      }
      .columnsTemplate('1fr 1fr')
      .columnsGap(12)
      .rowsGap(12)
      .width('100%')
      .height(0).layoutWeight(1)
      .padding({ left: 12, right: 12 })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}
export default HomeTab

// ==========================================
// 文件 3: pages/Movie.ets — 影片详情页
// ==========================================
import { router, ComposeTitleBar } from '@kit.ArkUI'

@Entry
@Component
struct MovieDetail {
  @State movieTitle: string = ''

  aboutToAppear(): void {
    try {
      const params = router.getParams() as Record<string, Object>
      if (params && params['title'] !== undefined) {
        this.movieTitle = params['title'] as string
      }
    } catch (err) {
      console.error(`参数获取失败: ${JSON.stringify(err)}`)
    }
  }

  build() {
    Column() {
      ComposeTitleBar({ title: '影片详情' }).width('100%')

      Column({ space: 16 }) {
        Image($r('app.media.startIcon'))
          .width(200).height(200)
          .borderRadius(12)

        Text(this.movieTitle)
          .fontSize(28)
          .fontWeight(FontWeight.Bold)

        Button('获取传递的参数')
          .onClick(() => {
            console.log(JSON.stringify(router.getParams()))
          })
      }
      .width('100%')
      .height(0).layoutWeight(1)
      .justifyContent(FlexAlign.Center)
    }
    .width('100%')
    .height('100%')
  }
}
```

> **架构要点**：
> 1. **组件解耦**：HomeTab / DiscoverTab / VipTab / PlanetTab / MineTab 各自独立文件，MainFrame 只负责组装
> 2. **路由集中**：每个 GridItem 的 onClick 中调用统一的 `navigateTo()` 方法，便于统一错误处理和埋点
> 3. **数据驱动**：`categories` 和 `videos` 数组驱动 Grid 渲染，新增条目只需追加数据
> 4. **参数链路**：HomeTab → pushUrl(params) → Movie.ets → getParams() → @State → UI 渲染
> 5. **注册须知**：pages/Pagea, Pageb, Pagec, Paged, Pagee, Movie 均需在 `main_pages.json` 中注册
> 6. **错误处理**：路由跳转和参数获取均包裹在 try-catch 中，避免异常崩溃

---

## 37. HTTP GET + json-server

```typescript
// pages/ProductList.ets
import { http } from '@kit.NetworkKit';

interface Product {
  id: number;
  name: string;
  price: number;
}

@Entry
@Component
struct ProductList {
  @State products: Product[] = [];
  @State loading: boolean = true;
  @State errorMsg: string = '';
  private httpReq = http.createHttp();  // 复用实例
  private readonly BASE_URL: string = 'http://192.168.1.100:9988';  // 用本机 IP！

  aboutToAppear(): void {
    this.fetchProducts();
  }

  fetchProducts(): void {
    this.loading = true;
    this.httpReq.request(
      `${this.BASE_URL}/products`,
      { method: http.RequestMethod.GET }
    ).then((res: http.HttpResponse): void => {
      const data = JSON.parse(res.result as string) as Product[];
      this.products = data;
      this.loading = false;
    }).catch((err: Error): void => {
      this.errorMsg = `加载失败: ${err.message}`;
      this.loading = false;
    });
  }

  build() {
    Column() {
      if (this.loading) {
        Text('加载中...').fontSize(18)
      } else if (this.errorMsg) {
        Column() {
          Text(this.errorMsg).fontColor(Color.Red)
          Button('重试').onClick(() => this.fetchProducts())
        }
      } else {
        List() {
          ForEach(this.products, (item: Product, index: number) => {
            ListItem() {
              Row() {
                Text(item.name).fontSize(18).layoutWeight(1)
                Text(`￥${item.price}`).fontColor(Color.Red)
              }.width('100%').padding(15).border({ width: { bottom: 1 }, color: '#EEE' })
            }
          }, (item: Product, index: number): string => `${item.id}_${index}`)
        }.width('100%').layoutWeight(1)
      }
    }.width('100%').height('100%')
  }
}
```

> **配套 json-server 启动命令**：`json-server --watch db.json --port 9988 --host 192.168.x.x`

---

## 38. harmony-dialog 弹窗合集

```typescript
import { DialogHelper, DialogAction, DateType } from '@pura/harmony-dialog';
import { DateUtil, ToastUtil } from '@pura/harmony-utils';

@Entry
@Component
struct DialogDemo {
  // === 确认对话框 ===
  showAlert(): void {
    DialogHelper.showAlertDialog({
      title: '确认删除',
      content: '此操作不可恢复，确定吗？',
      primaryButton: '取消',
      secondaryButton: '确定',
      onAction: (action: number): void => {
        if (action === DialogAction.SURE) {
          ToastUtil.showToast('已删除');
        }
      }
    });
  }

  // === 提示框（带图标） ===
  showTips(): void {
    DialogHelper.showTipsDialog({
      imageRes: $r('sys.media.ohos_app_icon'),
      imageSize: { width: 80, height: 80 },
      content: '操作成功！',
      secondaryButton: { value: '知道了', fontColor: Color.Red },
      onAction: (action: number): void => { /* ... */ }
    });
  }

  // === 底部动作面板 ===
  showSheet(): void {
    DialogHelper.showBottomSheetDialog({
      title: '请选择',
      sheets: ['拍照', '从相册选择', '文件管理器'],
      onAction: (index: number): void => {
        console.log(`选中了第${index}项`);
      }
    });
  }

  // === 文本输入弹框 ===
  showInput(): void {
    DialogHelper.showTextInputDialog({
      title: '支付密码',
      placeholder: '请输入6位密码',
      inputType: InputType.Password,
      defaultFocus: true,
      alignment: DialogAlignment.Bottom,
      onAction: (action: number, dialogId: string, content: string): void => {
        console.log(`输入内容: ${content}`);
      }
    });
  }

  // === 日期选择器 ===
  showDatePicker(): void {
    DialogHelper.showDatePickerDialog({
      title: '选择日期',
      dateType: DateType.YmdHms,
      start: new Date('2020-01-01'),
      end: new Date(),
      onAction: (action: number, dialogId: string, date: Date): void => {
        if (action === DialogAction.SURE) {
          const str = DateUtil.getFormatDateStr(date, 'yyyy-MM-dd HH:mm:ss');
          ToastUtil.showToast(`选中: ${str}`);
        }
      }
    });
  }

  // === 进度条加载 ===
  showLoading(): void {
    DialogHelper.showLoadingProgress({
      progress: 50,
      content: '努力加载中...',
      loadColor: Color.White,
      autoCancel: false
    });
  }

  build() {
    Column({ space: 12 }) {
      Button('确认对话框').onClick(() => this.showAlert())
      Button('提示框').onClick(() => this.showTips())
      Button('底部动作面板').onClick(() => this.showSheet())
      Button('文本输入').onClick(() => this.showInput())
      Button('日期选择器').onClick(() => this.showDatePicker())
      Button('进度条加载').onClick(() => this.showLoading())
    }.width('100%').height('100%').justifyContent(FlexAlign.Center)
  }
}
```

> **前置条件**：`ohpm i @pura/harmony-dialog` + `ohpm i @pura/harmony-utils`，在 UIAbility.onCreate 中初始化。

---

## 39. 三层架构脚手架

```
项目根路径/
├── common/
│   └── basic/           ← HSP 动态共享包（公共能力层）
│       ├── src/main/ets/components/
│       │   ├── ButtonCom.ets      ← 通用按钮组件
│       │   └── index.ets          ← export * from './ButtonCom'
│       └── Index.ets              ← export * from '../basic/src/main/ets/components'
├── features/
│   ├── home/            ← HAR 静态共享包（首页模块）
│   │   ├── src/main/ets/views/
│   │   │   ├── HomeView.ets
│   │   │   └── index.ets
│   │   └── Index.ets
│   ├── shop/            ← HAR（商城模块）
│   └── user/            ← HAR（我的模块）
└── products/
    └── entry/            ← Entry HAP（手机端入口）
        └── src/main/ets/pages/
            └── Index.ets
```

**common/basic/src/main/ets/components/ButtonCom.ets**：
```typescript
@Component
export struct ButtonCom {
  @Prop btn: string = '';

  build() {
    Button('通用按钮')
      .backgroundColor(Color.Red)
      .onClick(() => console.log(`收到: ${this.btn}`))
  }
}
```

**features/home/src/main/ets/views/HomeView.ets**：
```typescript
import { ButtonCom } from 'basic';  // 引用 common 层

@Component
export struct HomeView {
  build() {
    Column() {
      Text('首页')
      ButtonCom({ btn: '来自首页的数据' })  // 使用通用组件
    }
  }
}
```

**products/entry/src/main/ets/pages/Index.ets**：
```typescript
import { HomeView } from 'home';
import { ShopView } from 'shop';
import { UserView } from 'user';

@Entry
@Component
struct Index {
  build() {
    Tabs() {
      TabContent() { HomeView() }.tabBar('首页')
      TabContent() { ShopView() }.tabBar('商城')
      TabContent() { UserView() }.tabBar('我的')
    }
    .barPosition(BarPosition.End)
    .height('100%').width('100%')
  }
}
```

**依赖配置（products/entry/oh-package.json5）**：
```json5
{
  "name": "entry",
  "version": "1.0.0",
  "dependencies": {
    "basic": "file:../../common/basic",   // HSP
    "home": "file:../../features/home",   // HAR
    "shop": "file:../../features/shop",
    "user": "file:../../features/user"
  }
}
```

> **关键规则**：依赖方向 products → features → common（不可反向）。配置完所有 oh-package.json5 后关闭项目重新打开验证无循环依赖报错。

---

## 40. 自适应布局 displayPriority + FlexWrap

```typescript
@Entry
@Component
struct AdaptiveDemo {
  @State isExpanded: boolean = false;

  build() {
    Column() {
      // === 切换容器宽度模拟不同屏幕 ===
      Button(this.isExpanded ? '模拟窄屏' : '模拟宽屏')
        .onClick(() => { this.isExpanded = !this.isExpanded; })
        .margin({ bottom: 20 });

      // === Part 1: displayPriority 隐藏能力 ===
      Text('隐藏能力 (displayPriority)').fontSize(16).fontWeight(700)
      Row() {
        Image($r('sys.media.ohos_app_icon'))
          .width(40).height(40).displayPriority(1)   // 低优先级，先隐藏
        Image($r('sys.media.ohos_app_icon'))
          .width(40).height(40).displayPriority(1)
        Image($r('sys.media.ohos_app_icon'))
          .width(40).height(40).displayPriority(2)   // 高优先级，后隐藏
        Text('重要操作').fontSize(14).displayPriority(3)  // 最高优先级
      }
      .width(this.isExpanded ? '90%' : '60%')
      .height(55).borderRadius(8)
      .backgroundColor('#F5F5F5')
      .justifyContent(FlexAlign.SpaceAround)
      .margin({ bottom: 20 })

      // === Part 2: FlexWrap 折行能力 ===
      Text('折行能力 (FlexWrap.Wrap)').fontSize(16).fontWeight(700)
      Flex({ wrap: FlexWrap.Wrap }) {
        ForEach(['HTML', 'CSS', 'JavaScript', 'ArkTS', 'ArkUI', 'TypeScript'],
          (item: string) => {
            Text(item)
              .width(this.isExpanded ? 90 : 70)
              .height(36)
              .margin(6)
              .textAlign(TextAlign.Center)
              .backgroundColor('#E3F2FD')
              .borderRadius(4)
              .fontSize(13)
          }, (item: string): string => item)
      }
      .width(this.isExpanded ? '90%' : '70%')
      .padding(10)
    }
    .width('100%').padding(16)
  }
}
```

> **要点**：① `displayPriority` 必须用整数区分优先级；② `FlexWrap` 仅在 `Flex` 容器中生效，`Row`/`Column` 中无效。

---

## 41. PinchZoom + Pan 组合手势

```typescript
@Entry
@Component
struct PinchPanDemo {
  @State scaleValue: number = 1;
  @State offsetX: number = 0;
  @State offsetY: number = 0;
  @State lastScale: number = 1;

  // 缩放到原始大小
  reset(): void {
    this.scaleValue = 1;
    this.lastScale = 1;
    this.offsetX = 0;
    this.offsetY = 0;
  }

  build() {
    Column() {
      Row() {
        Button('重置').onClick(() => this.reset())
      }.width('100%').padding(10)

      Column() {
        Image($r('sys.media.ohos_app_icon'))
          .width(200)
          .objectFit(ImageFit.Contain)
          .scale({ x: this.scaleValue, y: this.scaleValue })
          .translate({ x: this.offsetX, y: this.offsetY })
          .gesture(
            GestureGroup(GestureMode.Exclusive,
              // 双指缩放
              PinchGesture()
                .onActionStart((): void => {
                  this.lastScale = this.scaleValue;
                })
                .onActionUpdate((event: PinchGestureEvent): void => {
                  this.scaleValue = this.lastScale * event.scale;
                })
                .onActionEnd((): void => {
                  // 限制最小1倍，最大5倍
                  this.scaleValue = Math.max(1, Math.min(5, this.scaleValue));
                }),
              // 单指拖拽
              PanGesture()
                .onActionUpdate((event: PanGestureEvent): void => {
                  // 关键：除以当前缩放因子，保证拖拽跟手
                  this.offsetX += event.offsetX / this.scaleValue;
                  this.offsetY += event.offsetY / this.scaleValue;
                })
            )
          )
      }
      .width(300).height(300)
      .clip(true)
      .backgroundColor('#F0F0F0')
      .justifyContent(FlexAlign.Center)
    }
    .width('100%').height('100%')
  }
}
```

> **关键点**：① `GestureMode.Exclusive` 互斥模式，同一时间只响应一个手势；② 拖拽位移 ÷ 缩放因子，否则放大后拖拽跳跃；③ `onActionStart` 记录缩放起点，避免每次更新从 1 重新算。

---

> 所有示例基于 **HarmonyOS NEXT API 12+**，使用 Stage 模型。如需查阅完整 API 参数，访问 [华为官方文档](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/overview-0000001774121182)。
