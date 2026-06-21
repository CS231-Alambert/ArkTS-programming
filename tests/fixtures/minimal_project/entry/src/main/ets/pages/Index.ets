import { router } from '@kit.ArkUI';

@Entry
@Component
struct Index {
  @State message: string = 'Hello World';

  build() {
    Column() {
      Text(this.message)
        .fontSize(20)
        .fontColor('#333333')
    }
    .width('100%')
    .height('100%')
  }
}
