Web组件提供了两种可配置的渲染模式，能够根据不同的容器大小进行适配，从而满足使用场景中对容器尺寸的需求。

## 异步渲染模式（默认）

异步渲染模式下（renderMode: [RenderMode](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkts-basic-components-web-e#rendermode12).ASYNC\_RENDER），Web组件作为图形surface节点，独立送显。建议在仅由Web组件构成的应用页面中使用此模式，以提高性能并降低功耗。

* Web组件的高度不能超过7,680px（物理像素），超过会导致白屏。
* 不支持动态切换模式。

开发者预期Web组件作为主体显示应用页面，如图一所示，在此场景下，Web组件高度正好为一屏或接近一屏（内嵌在Navigation中）。加载的H5页面高度大于Web组件高度，Web内部将产生滚动条，用户可以通过在Web内部滑动来浏览H5页面的信息。只需使用Web组件即可实现应用业务主体内容，建议采用异步渲染模式以提升性能。

**图一 异步渲染模式场景**

![](https://contentcenter-vali-drcn.dbankcdn.cn/pvt_2/DeveloperAlliance_scene_100_1/3c/v3/S1FSTBC-QJajPRwCtC3U9Q/zh-cn_image_0000002626068838.png?HW-CC-KV=V1&HW-CC-Date=20260618T043037Z&HW-CC-Expire=86400&HW-CC-Sign=053B11F04818F0B813A0D884483B67695541107C4B5D0AED8BBC783E2B30E2CE)

## 同步渲染模式

同步渲染模式下（renderMode: [RenderMode](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkts-basic-components-web-e#rendermode12).SYNC\_RENDER），Web组件作为图形canvas节点，Web渲染跟随系统组件一起送显，可以渲染更长Web组件内容，但会增加性能消耗。

* 不支持DSS（显示子系统）合成。
* 不支持动态切换模式。
* Web组件的高度最大规格不超过500,000 px（物理像素）。

开发者预期Web组件作为富文本显示的载体，成为应用页面的一部分，与其他ArkUI组件共同滑动交互。如图二所示，H5页面与Web组件高度一致，Web内部不生成滚动条，作为一个超长组件展示，通过[Scroll](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/ts-container-scroll)组件实现应用内部的滚动，确保用户能够平滑浏览Web内容及其他ArkUI组件的内容。需要Web作为业务内容的一部分渲染超长组件，不允许Web内部生成滚动条，与其余ArkUI组件协同完成页面布局，建议采用同步渲染模式，支持超长页面的渲染。

**图二 同步渲染模式场景**

![](https://contentcenter-vali-drcn.dbankcdn.cn/pvt_2/DeveloperAlliance_scene_100_1/2e/v3/XfGVBBRZRG2Rsjrk2-RnTA/zh-cn_image_0000002656468115.png?HW-CC-KV=V1&HW-CC-Date=20260618T043037Z&HW-CC-Expire=86400&HW-CC-Sign=881EDF324267BD70A161C7374C84A1DBFFC52CC4E990E5B7B4B8609EB4BD33A0)

## 示例代码

收起

自动换行

深色代码主题

复制

```
1. import { webview } from '@kit.ArkWeb';

3. @Entry
4. @Component
5. struct WebHeightPage {
6. private webviewController: WebviewController = new webview.WebviewController()

8. build() {
9. Column() {
10. Web({
11. src: 'www.example.com',
12. controller: this.webviewController,
13. renderMode: RenderMode.ASYNC_RENDER // 设置渲染模式
14. })
15. }
16. }
17. }
```

[RenderMode.ets](https://gitcode.com/HarmonyOS_Samples/guide-snippets/blob/HarmonyOS-7.0-beta-20260514/ArkWeb/WebRenderLayout/entry/src/main/ets/pages/RenderMode.ets#L16-L34)