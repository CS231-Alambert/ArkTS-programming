# harmonyos-arkts Skill 设计说明

## 文件结构

```
harmonyos-arkts/
├── SKILL.md       (331行) — 总是注入 system prompt，密度最高
├── REFERENCE.md   (797行) — 按需 Read，顶部索引 22 条
├── PITFALLS.md   (1044行) — 按需 Read，顶部索引 48 条
├── EXAMPLES.md   (2421行) — 按需 Read，顶部索引 36 条
└── README.md      — 本文件
```

## 为什么拆成 4 个文件

**核心原则**：SKILL.md 是 session 启动时就完整注入的，其他三个文件仅在 Agent 需要时通过 Read 工具加载。

| 文件 | 加载方式 | 体积策略 |
|------|----------|----------|
| SKILL.md | **始终全量注入** | 控制 < 250 行，只放规则、速查、检查清单、指针 |
| REFERENCE.md | 按需 Read | 可大，但有索引引导精准跳转 |
| PITFALLS.md | 按需 Read | 可大，但有索引引导精准跳转 |
| EXAMPLES.md | 按需 Read | 最大（~2000行），必须有索引，否则 Agent 会全量读取撑爆 context |

## 为什么每个子文件顶部要有索引

1. **Agent 倾向"读完再说"**。没有索引时，Agent 对着一个 2000 行的 EXAMPLES.md 可能直接 `Read` 全量，消耗 ~5000 token 上下文，挤压对用户实际需求的判断空间。

2. **索引让 Agent 知道自己该读多少**。看到索引表后，Agent 能先定位到具体行号，用 `Read offset=行号 limit=30` 精准获取需要的块，只消耗 ~800 token。

3. **SKILL.md 底部有"定位指南"**，明确告诉 Agent：
   - 三个子文件顶部有索引
   - 用 `Read offset=行号` 精准跳转
   - **切勿全量读取**

## SKILL.md 内容选取原则

只放"每次生成代码都要检查"的东西：

- **禁止项**（any/var/dynamic property 等——错一次就是编译失败）
- **状态管理**（@State/$$/嵌套更新——对但 UI 不更新比编译失败更难排查）
- **导入路径**（@kit 格式——最高频错误）
- **项目结构 + 路由 + 权限**（新页面开发必用）
- **组件速查表**（Shape/TitleBar/通用属性——覆盖 80% 常见组件用法，不用去翻 REFERENCE）
- **生成检查清单**（11 条，相当于编译前 checklist）
- **子文件定位指南**（告诉 Agent 怎么高效读子文件）

不放：完整 API 参数表、完整错误示例、完整代码示例——这些分别归属 REFERENCE/PITFALLS/EXAMPLES。

## 内容来源

本 skill 的知识点提取自 `C:\Users\24559\Desktop\专业实习\` 下全部 .md 教学文件（共 9 个文件，去重后约 5 个独立内容源）：

| 源文件 | 提取内容 |
|--------|----------|
| `day6/day7.md` | 图形绘制组件（Circle/Ellipse/Line/Polyline/Polygon/Rect/Path）、fill/stroke 属性、Path commands、三个标题栏组件 |
| `day6/day8.md` | 通用属性全集：尺寸、位置、布局约束、边框、背景、透明度、显隐、禁用、图形变换、裁剪、多态样式 |
| `课堂素材/day3.md` | Flex 布局（justifyContent/alignItems/alignContent/alignSelf/wrap）、Stack 层叠布局（zIndex/alignContent）、GridRow/GridCol 栅格（columns/breakpoints/gutter/span/offset/order） |
| `day3/鸿蒙-副本(2).md` （≈ `鸿蒙-副本6_1/6_2/6_3.md`） | 像素单位（vp/fp/px/lpx）、颜色格式、Span/ImageSpan/ContainerSpan 行内组件、Button 类型/自定义/悬浮、TextInput/TextArea/InputType、国际化（资源限定词）、$$ 双向绑定、事件传参模式 |
| `day7/day.md` + `day7/ets/` | 路由完整 API（back/showAlertBeforeBackPage/clear/getParams、页面栈 32 限制）、Tabs+TabContent 页签导航（barPosition 底部导航）、Grid 网格组件（columnsTemplate/rowsTemplate fr 单位）、EntryAbility 生命周期 + hilog 日志、组件 `export default` 导出规范、`$r()` 资源引用实战、**影片详情页参数接收（例35）**、**完整视频App架构 Tabs+Grid+路由（例36）**、**router vs Navigation 架构建议**、**Tabs+Grid导航枢纽模式** |

**去重策略**：多个副本文件（`6_5上午/day3.md` ≈ `课堂素材/day3.md`、`鸿蒙-副本6_2.md` ≈ `鸿蒙-副本6_3.md` ≈ `day3/鸿蒙-副本(2).md`）仅提取一次，不重复写入。

**排除内容**：以下类型的内容未纳入 skill，因为它们属于概念性/历史性知识而非编程参考：
- 移动通讯发展史（1G→5G）
- HarmonyOS 版本命名史
- "1+8+N"战略背景
- DevEco Studio 安装步骤（属于开发环境配置，非 ArkTS 编程）
- 模拟器创建/启动/关闭操作（同上）
- ArkUI 框架设计理念（声明式 vs 命令式范式对比）

## 迭代原则

1. 新增内容先判断属于"每次必查"还是"偶尔需要"，前者进 SKILL.md，后者进子文件。
2. 每次给子文件加内容后，**同时更新顶部索引**。
3. SKILL.md 超过 250 行时，考虑把低频速查信息下沉到 REFERENCE.md。
