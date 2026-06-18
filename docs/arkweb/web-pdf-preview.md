Web组件支持在网页中预览PDF。但受限于性能表现，部分场景存在掉帧现象。若对流畅度有要求，建议使用PdfView，或第三方解析库PDF.js。应用通过WebOptions的src参数和loadUrl()接口加载PDF文档。具体场景包括：网络PDF文档、应用沙箱内PDF文档和本地PDF文档。

若涉及网络文档获取，需在module.json5中配置网络访问权限。添加方法请参考在配置文件中声明权限。

```
"requestPermissions":[  {    "name" : "ohos.permission.INTERNET"  }],
```

[module.json5](https://gitcode.com/HarmonyOS_Samples/guide-snippets/blob/HarmonyOS-7.0-beta-20260514/ArkWeb/ProcessWebPageCont/entry/src/main/module.json5#L66-L79)

## 通过不同的方式加载PDF文档

在下面的示例中，Web组件创建时指定默认加载的网络PDF文档https://www.example.com/test.pdf。使用时需替换为真实的可访问URL。

```
import { webview } from '@kit.ArkWeb';
@Entry@Componentstruct WebComponent {  controller: webview.WebviewController = new webview.WebviewController();
  build() {    Column() {      Web({        src:        'https://www.example.com/test.pdf',                     // 方式一 加载网络PDF文档          // this.getUIContext().getHostContext()!.filesDir + '/test.pdf', // 方式二 加载本地应用沙箱内PDF文档          // 'resource://rawfile/test.pdf',                         // 方式三 本地PDF文档 (格式一)          // $rawfile('test.pdf'),                                 // 方式三 本地PDF文档 (格式二)          controller: this.controller      })        .domStorageAccess(true)    }  }}
```

[PreviewPDF.ets](https://gitcode.com/HarmonyOS_Samples/guide-snippets/blob/HarmonyOS-7.0-beta-20260514/ArkWeb/ProcessWebPageCont/entry/src/main/ets/pages/PreviewPDF.ets#L16-L38)

PDF预览页面会根据用户操作使用window.localStorage记录侧导航栏的展开状态，因此需要开启文档对象模型存储domStorageAccess权限:

```
Web().domStorageAccess(true)
```

在创建Web组件时，指定默认加载的PDF文档。默认PDF文档加载完成后，若需变更Web组件显示的PDF文档，通过调用loadUrl()接口加载指定的PDF文档。WebOptions的第一个参数变量src不能通过状态变量（例如：@State）动态更改地址，如需更改，请通过loadUrl()重新加载。

包含三种PDF文档加载预览场景：

预览加载网络PDF文档。

预览加载应用沙箱内PDF文档需要开启文件系统的fileAccess权限。

预览加载本地PDF文档。

## 通过配置PDF文件预览参数，控制打开预览时页面状态

当前支持如下参数:

| 语法 | 描述 |
|---|---|
| nameddest=destination | 指定PDF文档中的命名目标。 |
| page=pagenum | 使用整数指定文档中的页码，文档第一页的pagenum值为1。 |
| zoom=scale,left,top | 使用浮点或整数值设置缩放和滚动系数。例如：缩放值100表示缩放值为100%。 向左和向上滚动值位于坐标系中，0,0 表示可见页面的左上角，无论文档如何旋转。scale为必选参数。left,top为非必选参数。 |
| toolbar=1 or 0 | 1表示打开顶部工具栏。0表示关闭顶部工具栏。 |
| navpanes=1 or 0 | 1表示打开侧边导航窗格。0表示关闭侧边导航窗格。 |
| pdfbackgroundcolor=color | 从HarmonyOS 6.0系统版本开始，支持指定PDF文档背景色，color为标准的六位十六进制RGB（取值范围为000000~ffffff，例如白色为：ffffff）。 |

URL示例:

```
https://example.com/test.pdf#nameddest=Chapter6https://example.com/test.pdf#page=3https://example.com/test.pdf#zoom=50https://example.com/test.pdf#page=3&zoom=200,250,100https://example.com/test.pdf#toolbar=0https://example.com/test.pdf#navpanes=0https://example.com/test.pdf#pdfbackgroundcolor=ffffff
```

## PDF文档预览回调功能

从API version 20开始，PDF文档预览支持两种回调功能：加载成功/失败回调和滚动到底部事件回调。

在下面的示例中，Web组件创建时指定默认加载的网络PDF文档https://www.example.com/test.pdf。使用时需替换为真实的可访问URL。

加载成功/失败回调。

滚动到底部事件回调。

## 示例代码