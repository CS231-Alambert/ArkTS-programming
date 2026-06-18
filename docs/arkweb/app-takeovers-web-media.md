Web组件提供了应用接管网页中媒体播放的能力，用来支持应用增强网页的媒体播放，如画质增强等。

## 使用场景

网页播放媒体时，存在以下问题：网页清晰度低、网页播放器播放控件功能有限、某些视频无法播放。

应用开发者可以使用该功能，通过自己或者第三方播放器接管网页媒体播放，从而改善播放体验。

## 实现原理

### ArkWeb内核播放媒体的框架

不开启该功能时，ArkWeb内核的播放架构如下所示：

说明
* 上图中1表示ArkWeb内核创建WebMediaPlayer来播放网页中的媒体资源。
* 上图中2表示WebMediaPlayer使用系统解码器来渲染媒体数据。

开启该功能后，ArkWeb内核的播放架构如下：

说明
* 上图中1表示ArkWeb内核创建WebMediaPlayer来播放网页中的媒体资源。
* 上图中2表示WebMediaPlayer使用应用提供的本地播放器（NativeMediaPlayer）来渲染媒体数据。

### ArkWeb内核与应用的交互

说明
* 上图中1的详细说明见。
* 上图中2的详细说明见。
* 上图中3的详细说明见。
* 上图中4的详细说明见。
* 上图中5的详细说明见。

## 开发指导

### 开启接管网页媒体播放

需要先通过enableNativeMediaPlayer接口开启接管网页媒体播放的功能。

```
// xxx.etsimport { webview } from '@kit.ArkWeb';
@Entry@Componentstruct WebComponent {  controller: webview.WebviewController = new webview.WebviewController();
  build() {    Column() {      Web({ src: 'www.example.com', controller: this.controller })        .enableNativeMediaPlayer({ enable: true, shouldOverlay: false })    }  }}
```

### 创建本地播放器(NativeMediaPlayer)

该功能开启后，网页中有媒体需要播放时，ArkWeb内核会触发onCreateNativeMediaPlayer注册的回调函数。

应用则需要调用onCreateNativeMediaPlayer来注册一个创建本地播放器的回调函数。

该回调函数需要根据媒体信息来判断是否要创建一个本地播放器来接管当前的网页媒体资源。

* 如果应用不接管当前的网页媒体资源， 需在回调函数里返回null。
* 如果应用接管当前的网页媒体资源， 需在回调函数里返回一个本地播放器实例。

本地播放器需要实现NativeMediaPlayerBridge接口，以便ArkWeb内核对本地播放器进行播控操作。

```
// xxx.etsimport { webview } from '@kit.ArkWeb';
// 实现 webview.NativeMediaPlayerBridge 接口。// ArkWeb 内核调用该类的方法来对 NativeMediaPlayer 进行播控。class NativeMediaPlayerImpl implements webview.NativeMediaPlayerBridge {  // ... 实现 NativeMediaPlayerBridge 里的接口方法 ...  constructor(handler: webview.NativeMediaPlayerHandler, mediaInfo: webview.MediaInfo) {}  updateRect(x: number, y: number, width: number, height: number) {}  play() {}  pause() {}  seek(targetTime: number) {}  release() {}  setVolume(volume: number) {}  setMuted(muted: boolean) {}  setPlaybackRate(playbackRate: number) {}  enterFullscreen() {}  exitFullscreen() {}}
@Entry@Componentstruct WebComponent {  controller: webview.WebviewController = new webview.WebviewController();
  build() {    Column() {      Web({ src: 'www.example.com', controller: this.controller })        .enableNativeMediaPlayer({ enable: true, shouldOverlay: false })        .onPageBegin((event) => {          this.controller.onCreateNativeMediaPlayer((handler: webview.NativeMediaPlayerHandler, mediaInfo: webview.MediaInfo) => {            // 判断需不需要接管当前的媒体。            if (!shouldHandle(mediaInfo)) {              // 本地播放器不接管该媒体。              // 返回 null 。ArkWeb 内核将用自己的播放器来播放该媒体。              return null;            }            // 接管当前的媒体。            // 返回一个本地播放器实例给 ArkWeb 内核。            let nativePlayer: webview.NativeMediaPlayerBridge = new NativeMediaPlayerImpl(handler, mediaInfo);            return nativePlayer;          });        })    }  }}
// stubfunction shouldHandle(mediaInfo: webview.MediaInfo) {  return true;}
```

### 绘制本地播放器组件

应用接管网页媒体后，应用需要将本地播放器组件及视频画面绘制到ArkWeb内核提供的Surface上。ArkWeb内核再将Surface与网页进行合成并显示。

该流程与同层渲染绘制一致。

在应用启动阶段，应用应保存UIContext，以便后续的同层渲染绘制流程能够使用该UIContext。

应用使用ArkWeb内核创建的Surface进行同层渲染绘制。

动态创建组件并绘制到Surface上的详细介绍见同层渲染。

### 执行ArkWeb内核发送给本地播放器的播控命令

为了方便ArkWeb内核对本地播放器进行播控操作，应用需要令本地播放器实现NativeMediaPlayerBridge接口，并根据每个接口方法的功能对本地播放器进行相应操作。

```
// xxx.etsimport { webview } from '@kit.ArkWeb';
class ActualNativeMediaPlayerListener {  constructor(handler: webview.NativeMediaPlayerHandler) {}}
class NativeMediaPlayerImpl implements webview.NativeMediaPlayerBridge {  constructor(handler: webview.NativeMediaPlayerHandler, mediaInfo: webview.MediaInfo) {    // 1. 创建一个本地播放器的状态监听。    let listener: ActualNativeMediaPlayerListener = new ActualNativeMediaPlayerListener(handler);    // 2. 创建一个本地播放器。    // 3. 监听该本地播放器。    // ...  }
  updateRect(x: number, y: number, width: number, height: number) {    // <video> 标签的位置和大小发生了变化。    // 根据该信息变化，作出相应的改变。  }
  play() {    // 启动本地播放器播放。  }
  pause() {    // 暂停本地播放器播放。  }
  seek(targetTime: number) {    // 本地播放器跳转到指定的时间点。  }
  release() {    // 销毁本地播放器。  }
  setVolume(volume: number) {    // ArkWeb 内核要求调整本地播放器的音量。    // 设置本地播放器的音量。  }
  setMuted(muted: boolean) {    // 将本地播放器静音或取消静音。  }
  setPlaybackRate(playbackRate: number) {    // 调整本地播放器的播放速度。  }
  enterFullscreen() {    // 将本地播放器设置为全屏播放。  }
  exitFullscreen() {    // 将本地播放器退出全屏播放。  }}
```

### 将本地播放器的状态信息通知给ArkWeb内核

ArkWeb内核需要本地播放器的状态信息来更新到网页（例如：视频的宽高、播放时间、缓存时间等），因此，应用需要将本地播放器的状态信息通知给ArkWeb内核。

在onCreateNativeMediaPlayer接口中， ArkWeb内核传递一个NativeMediaPlayerHandler对象给应用。应用需要通过该对象，将本地播放器的最新状态信息通知给ArkWeb内核。

```
// xxx.etsimport { webview } from '@kit.ArkWeb';
class ActualNativeMediaPlayerListener {  handler: webview.NativeMediaPlayerHandler;
  constructor(handler: webview.NativeMediaPlayerHandler) {    this.handler = handler;  }
  onPlaying() {    // 本地播放器开始播放。    this.handler.handleStatusChanged(webview.PlaybackStatus.PLAYING);  }  onPaused() {    // 本地播放器暂停播放。    this.handler.handleStatusChanged(webview.PlaybackStatus.PAUSED);  }  onSeeking() {    // 本地播放器开始执行跳转到目标时间点。    this.handler.handleSeeking();  }  onSeekDone() {    // 本地播放器 seek 完成。    this.handler.handleSeekFinished();  }  onEnded() {    // 本地播放器播放完成。    this.handler.handleEnded();  }  onVolumeChanged() {    // 获取本地播放器的音量。    let volume: number = getVolume();    this.handler.handleVolumeChanged(volume);  }  onCurrentPlayingTimeUpdate() {    // 更新播放时间。    let currentTime: number = getCurrentPlayingTime();    // 将时间单位换算成秒。    let currentTimeInSeconds = convertToSeconds(currentTime);    this.handler.handleTimeUpdate(currentTimeInSeconds);  }  onBufferedChanged() {    // 缓存发生了变化。    // 获取本地播放器的缓存时长。    let bufferedEndTime: number = getCurrentBufferedTime();    // 将时间单位换算成秒。    let bufferedEndTimeInSeconds = convertToSeconds(bufferedEndTime);    this.handler.handleBufferedEndTimeChanged(bufferedEndTimeInSeconds);
    // 检查缓存状态。    // 如果缓存状态发生了变化，则向 ArkWeb 内核通知缓存状态。    let lastReadyState: webview.ReadyState = getLastReadyState();    let currentReadyState: webview.ReadyState = getCurrentReadyState();    if (lastReadyState != currentReadyState) {      this.handler.handleReadyStateChanged(currentReadyState);    }  }  onEnterFullscreen() {    // 本地播放器进入了全屏状态。    let isFullscreen: boolean = true;    this.handler.handleFullscreenChanged(isFullscreen);  }  onExitFullscreen() {    // 本地播放器退出了全屏状态。    let isFullscreen: boolean = false;    this.handler.handleFullscreenChanged(isFullscreen);  }  onUpdateVideoSize(width: number, height: number) {    // 当本地播放器解析出视频宽高时， 通知 ArkWeb 内核。    this.handler.handleVideoSizeChanged(width, height);  }  onDurationChanged(duration: number) {    // 本地播放器解析到了新的媒体时长， 通知 ArkWeb 内核。    this.handler.handleDurationChanged(duration);  }  onError(error: webview.MediaError, errorMessage: string) {    // 本地播放器出错了，通知 ArkWeb 内核。    this.handler.handleError(error, errorMessage);  }  onNetworkStateChanged(state: webview.NetworkState) {    // 本地播放器的网络状态发生了变化， 通知 ArkWeb 内核。    this.handler.handleNetworkStateChanged(state);  }  onPlaybackRateChanged(playbackRate: number) {    // 本地播放器的播放速率发生了变化， 通知 ArkWeb 内核。    this.handler.handlePlaybackRateChanged(playbackRate);  }  onMutedChanged(muted: boolean) {    // 本地播放器的静音状态发生了变化， 通知 ArkWeb 内核。    this.handler.handleMutedChanged(muted);  }
  // ... 监听本地播放器其他的状态 ...}@Entry@Componentstruct WebComponent {  controller: webview.WebviewController = new webview.WebviewController();  @State show_native_media_player: boolean = false;
  build() {    Column() {      Web({ src: 'www.example.com', controller: this.controller })        .enableNativeMediaPlayer({enable: true, shouldOverlay: false})        .onPageBegin((event) => {          this.controller.onCreateNativeMediaPlayer((handler: webview.NativeMediaPlayerHandler, mediaInfo: webview.MediaInfo) => {            // 接管当前的媒体。
            // 创建一个本地播放器实例。            // let nativePlayer: NativeMediaPlayerImpl = new NativeMediaPlayerImpl(handler, mediaInfo);
            // 创建一个本地播放器状态监听对象。            let nativeMediaPlayerListener: ActualNativeMediaPlayerListener = new ActualNativeMediaPlayerListener(handler);            // 监听本地播放器状态。            // nativePlayer.setListener(nativeMediaPlayerListener);
            // 返回这个本地播放器实例给 ArkWeb 内核。            return null;          });        })    }  }}
// stubfunction getVolume() {  return 1;}function getCurrentPlayingTime() {  return 1;}function getCurrentBufferedTime() {  return 1;}function convertToSeconds(input: number) {  return input;}function getLastReadyState() {  return webview.ReadyState.HAVE_NOTHING;}function getCurrentReadyState() {  return webview.ReadyState.HAVE_NOTHING;}
```

## 完整示例

涉及网页媒体播放，需在配置文件中配置网络访问权限。添加方法请参考在配置文件中声明权限。

在应用启动阶段保存UIContext。

应用侧代码，视频托管使用示例。通过AVPlayer托管Web媒体的播放。

应用侧代码，视频播放示例, ./PlayerDemo.ets。

前端页面示例。通过AVPlayer托管Web媒体的播放，支持的媒体资源可以参考AVPlayer支持的格式与协议。