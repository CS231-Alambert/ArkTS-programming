# HarmonyOS 开发者文档知识库

> 来源: [华为 HarmonyOS 开发者文档](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/)
> 抓取时间: 2026-06-18
> Kit 覆盖: ArkWeb (14 个内容页)

## 快速查阅

```bash
# 按关键词定位
grep -l "javaScriptProxy" docs/arkweb/*.md
grep -l "runJavaScript" docs/arkweb/*.md
grep -l "CSP\|网络安全" docs/arkweb/*.md

# 按 API 查找
grep -rn "import.*@kit" docs/arkweb/ | head -20
```

## 统计

| 指标 | 数值 |
|------|------|
| 总文件数 | 14 (ArkWeb) |
| 总行数 | 8,356 |
| 代码块总数 | 122 |
| @kit 模块引用 | 9 种 |

## 目录

### ArkWeb (`docs/arkweb/`)

| 文件 | 行数 | 代码块 | 用途 |
|------|------|--------|------|
| [00-INDEX.md](arkweb/00-INDEX.md) | — | — | 主题索引 |
| web-same-layer.md | 1,818 | 21 | 同层渲染 (核心) |
| arkweb-ndk-jsbridge.md | 1,592 | 27 | C/C++ JSBridge |
| web-in-page-app-function-invoking.md | 1,029 | 19 | **javaScriptProxy** (JSBridge 核心) |
| arkweb-ndk-page-data-channel.md | 1,011 | 7 | C/C++ 数据通道 |
| web-offline-mode.md | 798 | 14 | 离线 Web 组件 |
| web-native-messaging.md | 527 | 13 | 浏览器扩展通信 |
| arkweb-glossary.md | 414 | 0 | 术语表 |
| web-getpage-height.md | 266 | 6 | 页面高度 |
| web-event-sequence.md | 247 | 2 | Web 生命周期 |
| web_component_process.md | 228 | 6 | ArkWeb 进程模型 |
| web-app-page-data-channel.md | 202 | 3 | 数据通道 |
| web-in-app-frontend-page-function-invoking.md | 92 | 2 | runJavaScript |
| web-component-overview.md | 59 | 1 | ArkWeb 简介 |
| web-render-mode.md | 59 | 1 | 渲染模式 |

## 更新

```bash
# 检查文档更新
bash docs/scripts/crawl-all.sh --check-updates

# 全量重新转换
bash docs/scripts/convert-all.sh
```
