<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# 动效与转场

动画由 [GSAP](https://github.com/greensock/GSAP)（GreenSock Animation Platform）驱动。`assets/motion/motion.js`
提供一组可组合的转场与效果，`assets/motion/gallery.html` 逐个演示它们。每支片子按创意简报重新选择、组合和定制，
需要时编写新的效果。

## GSAP 来源

| 来源 | 用途 |
| --- | --- |
| [greensock/GSAP](https://github.com/greensock/GSAP) | 动画库本体。通过 npm 安装 `gsap`（本技能使用 3.15），全部插件（SplitText、MorphSVG、DrawSVG 等）都在公开包中，可以免费用于商业项目。许可为 GreenSock 标准许可（<https://gsap.com/standard-license>），技能目录不附带 GSAP 文件，项目通过 npm 安装。 |
| [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | GreenSock 官方的智能体技能（MIT）。需要查 API 细节时安装：`npx skills add https://github.com/greensock/gsap-skills`。视频制作主要用到 `gsap-core`、`gsap-timeline`、`gsap-plugins`、`gsap-utils`、`gsap-performance`；`gsap-scrolltrigger`、`gsap-react`、`gsap-frameworks` 面向网页交互。 |
| [GSAP 文档](https://gsap.com/docs/v3/) 与 [缓动可视化](https://gsap.com/docs/v3/Eases) | 查参数、比较缓动曲线 |

## 逐帧渲染中的 GSAP 规则

gsap-skills 描述的是网页中实时播放的动画；逐帧渲染还要满足下面这些规则。

- **一条暂停的主时间轴**：`gsap.timeline({ paused: true })`，所有效果用位置参数放到绝对时间上；每帧调用 `motion.renderAt(tl, 秒, 种子, 帧号)`。
- **确定的随机数**：搭建场景前 `motion.seedRandom(种子)`；`renderAt` 每帧用帧号重新设置种子。ScrambleText、CustomWiggle 的 random 类型、RoughEase 都使用 `Math.random`。tween 参数里不使用 `"random(...)"` 字符串，随机值在搭建时用已设种子的 `Math.random` 算好。
- **ScrambleText**：经 `motion.scramble()` 使用。该插件每次刷新字符都依赖上一次的结果，`renderAt` 每帧把进行中的乱码 tween 恢复原文并 `invalidate()`，按当帧种子重新初始化。
- **`fromTo()` 两端写全**：GSAP 只补间 to-vars 中出现的属性。只写在 from-vars 里的属性（例如 `autoAlpha`）会随渲染顺序变化；`transformOrigin` 这类设置用 `gsap.set()` 在搭建时写入。
- **`immediateRender`**：入场效果用 `immediateRender: true`，让元素在开始前就处于起始状态；同一元素同一属性的后续 tween 用 `false`。
- **重复次数有限**：不用 `repeat: -1`，按场景长度计算重复次数（`motion.flow()` 的 `until` 参数）。
- **测量布局的插件在字体之后**：SplitText、Flip 在 `document.fonts` 加载完成后调用。中文按 `chars` 拆分，`words` 与 `lines` 依赖空格。
- **回调**：`tl.time(t, false)` 会触发 `onUpdate` / `onComplete` / `onReverseComplete`，计数器等写文本的效果三个回调都要写同一个函数。
- **不用于渲染的插件**：ScrollTrigger、ScrollSmoother、Draggable、Observer、Inertia 依赖滚动或输入；GSDevTools 只在预览时使用。
- **插件加载**：用 `node_modules/gsap/dist/*.min.js` 的 UMD 脚本按需加载，`motion.registerPlugins()` 注册已加载的插件。
- **场景不透明**：裁切类转场（wipe、iris、split、lineReveal）在旧场景上显示新场景，每个场景要有自己的背景。
- **验证**：`render_frames.py check` 对比直接跳转与逐帧推进的结果；新写的效果必须通过这项检查。

## 转场

签名：`transition(tl, at, from, to, options)`，返回结束时间。`at` 是转场开始时刻；
时间轴文件中用 `lead` 把转场中最显著的时刻放到小节线上（闪白、色带、形状变形的切换点在一半处）。

| 名称 | 画面 | 适合 | 主要参数 | 插件 |
| --- | --- | --- | --- | --- |
| `dissolve` | 叠化 | 同一段落内换镜头、平静的叙述 | `duration` | 核心 |
| `blurDissolve` | 模糊叠化 | 时间或地点变化、回忆、柔和过渡 | `blur` | 核心 |
| `wipe` | 擦除，可带强调色边线 | 章节推进、对比的下一项 | `direction`、`edge` | 核心 |
| `iris` | 圆形展开 | 从画面中的焦点进入下一段 | `x`、`y` | 核心 |
| `split` | 中缝对开，旧画面后退变暗 | 对比双方登场、揭示 | `axis` | 核心 |
| `push` | 推移 | 列表、步骤、时间线的下一项 | `direction` | 核心 |
| `zoomThrough` | 穿越缩放 | 从概览进入细节、进入系统内部 | `depth`、`blur` | 核心 |
| `band` | 斜向色带扫过 | 部分之间、品牌时刻 | `color`、`accent`、`angle` | 核心 |
| `flash` | 闪白硬切 | 与重击同拍的结果揭示 | `color`、`punch` | 核心 |
| `glitch` | 故障切换 | 系统、信号、错误、对比中的“旧方案” | `steps`、`offset`、`seed` | 核心 |
| `shapeMorph` | 圆点变形铺满全屏再收成细线 | 产品登场、标题 | `x`、`y`、`color` | MorphSVG |
| `lineReveal` | 线条画出后上下打开 | 技术图解、章节标题 | `color` | DrawSVG |

## 效果

签名：`effect(tl, at, targets, options)`，返回结束时间。

| 名称 | 画面 | 适合 | 主要参数 | 插件 |
| --- | --- | --- | --- | --- |
| `splitRise` | 逐字或逐词遮罩上升 | 标题、关键句 | `type`、`stagger`、`from` | SplitText |
| `blurIn` | 模糊中聚焦 | 产品名、口号 | `blur`、`from` | SplitText |
| `typewriter` | 打字与光标 | 命令、终端、代码 | `cps`、`cursor` | TextPlugin |
| `scramble` | 乱码解码成文字 | 状态切换、系统就绪 | `chars`、`revealDelay` | ScrambleText |
| `countUp` | 数字滚动 | 实测数据 | `to`、`decimals`、`suffix` | 核心 |
| `draw` | 描线 | 架构图、连线、流程 | `stagger`、`reverse` | DrawSVG |
| `flow` | 沿路径流动 | 数据包、信号、能量 | `duration`、`spacing`、`until` | MotionPath |
| `stack` | 逐层叠起 | 分层架构、步骤、列表 | `direction`、`distance` | 核心 |
| `gridReveal` | 网格按位置展开 | 功能列表、生态、合作方 | `from`、`grid`、`amount` | 核心（distribute） |
| `flipLayout` | 布局变换 | 一排变两列、排序、分组 | `change` 回调 | Flip |
| `shine` | 扫光 | 标志、卡片、结果强调 | `color`、`width` | 核心 |
| `shake` | 冲击抖动 | 推力、碰撞、报错 | `strength`、`wiggles` | CustomWiggle |
| `drift` | 缓推镜头 | 静态画面保持呼吸 | `scale`、`x`、`y` | 核心 |
| `parallax` | 多层视差 | 背景空间感 | `distance`，层的 `data-depth` | 核心 |
| `morph` | 形状变形 | 图标状态切换 | `type` | MorphSVG |
| `bars` | 柱状生长 | 指标对比 | `axis`、`stagger` | 核心 |
| `outline` | 圈注 | 指向关键数字 | `padding`、`radius` | DrawSVG |
| `drop` | 物理抛落 | 散落、释放、碰撞 | `velocity`、`angle`、`gravity` | Physics2D |

查看实际效果：把 `assets/motion/` 复制到页面目录后运行

```sh
python3 scripts/render_frames.py snap page/motion/gallery.html --root page --every 3 --out motion-sheet
python3 scripts/render_frames.py eval page/motion/gallery.html --root page "window.motionCatalog()"
```

联系表可以直接发给需求方挑选转场与效果。

## 动效计划

分镜确认后、写页面之前，按简报写一张动效计划表，并请用户确认：

```markdown
| 场景 | 进入转场（lead / 时长） | 主要效果 | 强调 | 节拍 |
| --- | --- | --- | --- | --- |
| 标题 | — | blurIn 产品名，shine | shapeMorph 收尾 | 第 3 小节重击 |
| 架构 | band（0.5 / 1.0） | stack 四层，draw 连线 | outline 实时域 | 每层落在一拍 |
| 实测 | flash（0.08 / 0.5） | countUp，bars | shake 推力时刻 | 数字在小节线出现 |
```

组合规则：

- **一支片子一套词汇**：从转场表里选 3–5 种，每种对应一种叙事功能（部分切换、段内换镜头、揭示、冲击），全片保持一致。
- **相邻不重复**：同一种转场不连续使用，作为主题反复出现的除外（例如每个实测段都用 `flash` 揭示结果）。
- **同一时刻一个主动作**：入场效果之间错开至少半拍，次要元素用更短的时长和更小的位移。
- **同一位置先退后进**：叠化、模糊叠化等两段画面同时可见的转场里，两段在同一位置都有标题时，旧标题先淡出，新标题在转场后半段进入，避免两行字叠在一起。
- **跟着节拍**：转场切换点放在小节线，效果起点放在拍点，时长用拍数表示（`motion.beats(2, 120)`）。
- **层次**：背景层缓慢（`drift`、`parallax`），主体层清晰，强调层短促（`outline`、`shine`、`shake`）。
- **变化来自参数**：同一个效果在不同场景改变方向、`from` 顺序、`stagger`、缓动和时长，避免整片同一种节奏。
- **内容决定效果**：数字用 `countUp`，连线用 `draw`，流动用 `flow`，层级用 `stack`，状态切换用 `scramble` 或 `morph`；没有合适的效果时编写新的效果。

## 定制与扩展

- 修改参数：每个函数的参数都有默认值，按场景覆盖；`motion.usePersonality()` 切换整片缓动基调，也可以传入自定义缓动组合。
- 组合效果：同一元素可以先 `blurIn` 再 `shine`；`draw` 画出路径后接 `flow` 在路径上流动；`flipLayout` 之后用 `outline` 标出结果。
- 品牌缓动：用 CustomEase 定义品牌曲线（`CustomEase.create('brand-in', '.2,.8,.2,1')`），作为参数传入。
- 新效果：沿用 `(tl, at, targets, options) => 结束时间` 的签名，只往主时间轴添加 tween，不创建独立运行的动画；加入后运行 `render_frames.py check`。
- 新转场：沿用 `(tl, at, from, to, options)` 的签名，负责新场景出现与旧场景隐藏；叠加层创建在 `#stage` 中并在结束时隐藏。
