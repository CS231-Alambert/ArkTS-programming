从API version 14开始，支持使用Web组件的createPdf方法，为应用提供了保存前端页面为PDF的功能。

使用createPdf生成实例后，调用pdfArrayBuffer方法获取二进制数据流，再使用fileIo方法将二进制数据流保存为PDF文件。用户可以将前端页面内容保存为PDF以便分享或保存。例如，生成报告、发票等，方便用户保存和传输。

说明

通过pdfConfiguration的配置，可调整PDF每页大小、前端页面缩放比例等；推荐使用前端页面适配策略，通过CSS媒体查询（@media print）优化PDF排版。

## 需要权限

若涉及网络文档获取，需在module.json5中配置网络访问权限。具体添加方法请参考在配置文件中声明权限。

```
"requestPermissions": [  {    "name": "ohos.permission.INTERNET"  }],
```

[module.json5](https://gitcode.com/HarmonyOS_Samples/guide-snippets/blob/HarmonyOS-7.0-beta-20260514/ArkWeb/ArkWebCreatePdf/entry/src/main/module.json5#L64-L70)

## callback方式保存PDF

通过callback方式调用createPdf接口，获取到的result通过pdfArrayBuffer接口取得PDF二进制数据流，最后使用fileIo方法将二进制数据流保存为PDF文件。

```
import { fileIo } from '@kit.CoreFileKit';import { webview } from '@kit.ArkWeb';import { BusinessError } from '@kit.BasicServicesKit';import { common } from '@kit.AbilityKit';
@Entry@Componentstruct Index {  controller: webview.WebviewController = new webview.WebviewController();  pdfConfig: webview.PdfConfiguration = {    width: 8.27,    height: 11.69,    marginTop: 0,    marginBottom: 0,    marginRight: 0,    marginLeft: 0,    shouldPrintBackground: true  };
  build() {    Column() {      Button('SavePDF')        .onClick(() => {          // 触发PDF生成，需要确保页面渲染完成，可使用onPageEnd事件监听          this.controller.createPdf(            this.pdfConfig,            (error, result: webview.PdfData) => {              try {                // 获取到的result通过`pdfArrayBuffer`接口取得PDF二进制数据流，最后使用`fileIo`方法将二进制数据流保存为PDF文件                let context = this.getUIContext().getHostContext() as common.UIAbilityContext;                let filePath = context.filesDir + '/test.pdf';                let file = fileIo.openSync(filePath, fileIo.OpenMode.READ_WRITE | fileIo.OpenMode.CREATE);                fileIo.write(file.fd, result.pdfArrayBuffer().buffer).then((writeLen: number) => {                  console.info('createPDF write data to file succeed and size is:' + writeLen);                }).catch((err: BusinessError) => {                  console.error('createPDF write data to file failed with error message: ' + err.message +                      ', error code: ' + err.code);                }).finally(() => {                  // 关闭file                  fileIo.closeSync(file);                });              } catch (resError) {                console.error(                  `ErrorCode: ${(error as BusinessError).code},  Message: ${(error as BusinessError).message}`);              }            });        })      Web({ src: 'www.example.com', controller: this.controller })    }  }}
```

[WebCreatePdfCallback.ets](https://gitcode.com/HarmonyOS_Samples/guide-snippets/blob/HarmonyOS-7.0-beta-20260514/ArkWeb/ArkWebCreatePdf/entry/src/main/ets/pages/WebCreatePdfCallback.ets#L16-L68)

## Promise方式保存PDF

通过Promise方式调用createPdf接口，获取到的result通过pdfArrayBuffer接口取得PDF二进制数据流，最后使用fileIo方法将二进制数据流保存为PDF文件。

```
import { fileIo } from '@kit.CoreFileKit';import { webview } from '@kit.ArkWeb';import { BusinessError } from '@kit.BasicServicesKit';import { common } from '@kit.AbilityKit';
@Entry@Componentstruct Index {  controller: webview.WebviewController = new webview.WebviewController();  pdfConfig: webview.PdfConfiguration = {    width: 8.27,    height: 11.69,    marginTop: 0,    marginBottom: 0,    marginRight: 0,    marginLeft: 0,    shouldPrintBackground: true  };
  build() {    Column() {      Button('SavePDF')        .onClick(() => {          // 触发PDF生成，需要确保页面渲染完成，可使用onPageEnd事件监听          this.controller.createPdf(this.pdfConfig)            .then((result: webview.PdfData) => {              try {                // 获取到的result通过`pdfArrayBuffer`接口取得PDF二进制数据流，最后使用`fileIo`方法将二进制数据流保存为PDF文件                let context = this.getUIContext().getHostContext() as common.UIAbilityContext;                let filePath = context.filesDir + '/test.pdf';                let file = fileIo.openSync(filePath, fileIo.OpenMode.READ_WRITE | fileIo.OpenMode.CREATE);                fileIo.write(file.fd, result.pdfArrayBuffer().buffer).then((writeLen: number) => {                  console.info('createPDF write data to file succeed and size is:' + writeLen);                }).catch((err: BusinessError) => {                  console.error('createPDF write data to file failed with error message: ' + err.message +                      ', error code: ' + err.code);                }).finally(() => {                  // 关闭file                  fileIo.closeSync(file);                });              } catch (resError) {                console.error(                  `ErrorCode: ${(resError as BusinessError).code},  Message: ${(resError as BusinessError).message}`);              }            })        })      Web({ src: 'www.example.com', controller: this.controller })    }  }}
```

[WebCreatePdfPromise.ets](https://gitcode.com/HarmonyOS_Samples/guide-snippets/blob/HarmonyOS-7.0-beta-20260514/ArkWeb/ArkWebCreatePdf/entry/src/main/ets/pages/WebCreatePdfPromise.ets#L16-L67)