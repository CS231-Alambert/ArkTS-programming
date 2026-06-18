Web组件提供了视频进入全屏和退出全屏的事件功能，应用可通过监听这些事件实现进入和退出沉浸式全屏模式。

Web组件引用第三方H5页面加载的视频，当单击视频全屏时，视频仅扩展至整个Web组件区域，无法实现系统全屏显示（如图2所示）。若要达到系统全屏的沉浸式视频播放效果（如图3所示），则需应用监听进入全屏的事件并调整界面其他组件的属性。

| 图1 退出全屏模式 | 图2 非沉浸式全屏模式 | 图3 沉浸式全屏模式 |
|---|---|---|
|  |  |  |

Web组件可通过onFullScreenEnter和onFullScreenExit回调监听全屏按键的单击事件。其中，onFullScreenEnter表示Web组件进入全屏模式，onFullScreenExit表示Web组件退出全屏模式。在这两个监听事件中，可根据具体业务场景调整某些全局变量，例如组件的显隐状态、组件的margin属性等，以实现退出和进入沉浸式全屏模式的界面效果，如图1和图3所示。

可见性visibility是ArkUI提供的组件通用属性。开发者可通过设置组件属性visibility的不同值，控制组件的显隐状态。

```
import { webview } from '@kit.ArkWeb';
@Entry@Componentstruct ShortWebPage {  controller: webview.WebviewController = new webview.WebviewController();  CONSTANT_HEIGHT = 100;  @State marginTop: number = this.CONSTANT_HEIGHT;  @State isVisible: boolean = true; // 自定义标志位isVisible，来控制是否需要显示组件
  build() {    Column() {      Text('TextTextTextText')        .width('100%')        .height(this.CONSTANT_HEIGHT)        .backgroundColor('#e1dede') // 当isVisible标志位为true的时候，组件状态为可见，否则组件状态为不可见，不参与布局、不进行占位        .visibility(this.isVisible ? Visibility.Visible :          Visibility.None)      Web({        src: $rawfile('FullScreen.html'), // 示例网址        controller: this.controller      })        .onFullScreenEnter((event) => {          console.info('onFullScreenEnter...');          // 当全屏的时候，isVisible标志位为false，组件状态为不可见，不参与布局、不进行占位          this.isVisible = false;        })        .onFullScreenExit(() => {          console.info('onFullScreenExit...');          // 当退出全屏的时候，isVisible标志位为true，组件状态为可见          this.isVisible = true;        })        .width('100%')        .height('100%')        .zIndex(10)        .zoomAccess(true)    }.width('100%').height('100%')  }}
```

[Index.ets](https://gitcode.com/HarmonyOS_Samples/guide-snippets/blob/HarmonyOS-7.0-beta-20260514/ArkWeb/ArkWebPictureInPicture/entry1/src/main/ets/pages/Index.ets#L16-L56)