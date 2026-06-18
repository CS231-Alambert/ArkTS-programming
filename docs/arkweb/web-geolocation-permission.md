从API version 9开始，支持Web组件的GeolocationPermissions类和onGeolocationShow方法对网页进行位置权限管理。更多信息请参见应用数据安全。

Web组件根据GeolocationPermissions类和onGeolocationShow方法的响应结果，决定是否赋予前端页面权限。用户可以获取位置信息，以便使用出行导航、天气预报等服务。

## 需要权限

使用获取位置功能，需在module.json5中配置位置权限。具体添加方法请参考在配置文件中声明权限。

```
"requestPermissions":[   {     "name" : "ohos.permission.LOCATION" // 精准定位   },   {     "name" : "ohos.permission.APPROXIMATELY_LOCATION" // 模糊定位   },   {     "name" : "ohos.permission.LOCATION_IN_BACKGROUND" // 后台定位   } ]
```

## 申请位置权限

在下面的示例中，用户点击前端页面"获取位置"按钮，Web组件通过弹窗通知应用侧位置权限请求消息。

前端页面代码。

应用代码。

## 管理位置权限

通过Web组件的GeolocationPermissions类管理网页的位置权限，提供了新增（allowGeolocation）、查看（getAccessibleGeolocation）和删除（deleteGeolocation）网页位置权限的方法。例如查看网页是否已申请位置权限、将网页已申请的位置权限删除。

```
import { webview } from '@kit.ArkWeb';import { BusinessError } from '@kit.BasicServicesKit';
@Entry@Componentstruct WebComponent {  controller: webview.WebviewController = new webview.WebviewController();  origin: string = "www.example.com";
  build() {    Column() {      // 新增指定源的位置权限，再次获取位置信息时则不再触发onGeolocationShow的回调      Button('allowGeolocation')        .onClick(() => {          try {            webview.GeolocationPermissions.allowGeolocation(this.origin);          } catch (error) {            console.error(`ErrorCode: ${(error as BusinessError).code},  Message: ${(error as BusinessError).message}`);          }        })
      // 删除指定源的位置权限，再次获取位置信息时则触发onGeolocationShow的回调      Button('deleteGeolocation')        .onClick(() => {          try {            webview.GeolocationPermissions.deleteGeolocation(this.origin);          } catch (error) {            console.error(`ErrorCode: ${(error as BusinessError).code},  Message: ${(error as BusinessError).message}`);          }        })
      // 查询指定源的位置权限      Button('getAccessibleGeolocation')        .onClick(() => {          try {            webview.GeolocationPermissions.getAccessibleGeolocation(this.origin)              .then(result => {                console.info('getAccessibleGeolocationPromise result: ' + result);              }).catch((error: BusinessError) => {              console.error(`getAccessibleGeolocationPromise error, ErrorCode: ${error.code},  Message: ${error.message}`);            });          } catch (error) {            console.error(`ErrorCode: ${(error as BusinessError).code},  Message: ${(error as BusinessError).message}`);          }        })
      // 注意添加网络权限ohos.permission.INTERNET      Web({ src: 'www.example.com', controller: this.controller })    }  }}
```