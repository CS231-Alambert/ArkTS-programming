## 场景介绍

从5.1.1 (19)版本开始，新增支持资源注册。

适用于需要快速定制应用内Symbol图标，不想强依赖于系统版本中预制的系统Symbol图标资源。

## 约束条件

资源注册支持Phone、Tablet、PC/2in1设备。

## 开发步骤

将UX设计师提供的Symbol图标资源（TTF文件）与动效参数资源（JSON文件）放入entry/src/main/resources/rawfile下，可新建目录。

说明：Symbol资源设计流程参考

多语言场景，在entry/src/main/resources目录中对应语言目录下的string.json文件中配置对应的Symbol图标Unicode值。

导入相关模块。

在通过SymbolGlyph/SymbolSpan组件展示自定义Symbol图标前，需要注册加载图标资源与动效参数资源。

在需要展示自定义Symbol图标的页面通过SymbolGlyph/SymbolSpan组件展示该图标。

## 开发实例

```
import { symbolRegister } from '@kit.UIDesignKit'import { BusinessError } from '@kit.BasicServicesKit'
@Entry@Componentstruct test {  aboutToAppear(): void {    try {      let result = symbolRegister.registerSymbol($rawfile("symbol/symbol_register.ttf"), $rawfile("symbol/symbol_register.json"));    } catch (error) {      let err = error as BusinessError;      console.error("errCode: " + err.code)      console.error("error: " + err.message);    }  }  build() {    Column(){      SymbolGlyph($r('app.string.symbol_custom_phone_fill_1'))    }  }}
```