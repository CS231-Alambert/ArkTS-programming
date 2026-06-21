// Contains multiple ArkTS violations
import router from '@ohos.router';   // @ohos old import
var badVar = 123;                      // var declaration
let badAny: any = 'test';             // any type

@Entry
@Component
struct BadPage {
  @State message: string = 'Bad Page';

  build() {
    Column() {
      ForEach([1, 2, 3], (item: number) => {   // missing key function
        Text(item.toString())
      })
      Text(this.message)
        .fontSize('16fp')  // non-text component has fontSize? actually this is OK for Text
    }
    .width('100%')
  }
}
