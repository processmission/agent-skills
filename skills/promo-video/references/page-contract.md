<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# 合成页面约定

合成页面是一个 HTML 页面，`scripts/render_frames.py` 通过本机 HTTP 服务打开它，逐帧调用
`window.renderFrame(frame)` 后截图。`assets/page-template/` 是一个可以直接渲染的 16 秒示例，用来演示约定；
每支片子的场景、版式与动效按本片的分镜和动效计划重新编写。

## 接口

| 名称 | 要求 |
| --- | --- |
| `window.ready` | 字体、图片、数据加载完成并渲染第 0 帧后设为 `true` |
| `window.FPS` | 帧率，默认 30；无旁白的动效片可以用 60 |
| `window.DURATION` | 总时长（秒） |
| `window.renderFrame(frame)` | 返回 Promise；完成时画面已经完全对应 `frame / FPS` 秒，图片已解码 |
| `window.getCues()` | 提示点 `[{type, t, ...}]`：音效类型见 [配乐、音效与旁白](audio.md)；`transition` 标记设计好的画面跳变，供 `qa_frames.py` 排除 |
| `window.getSubtitles()` | 字幕 `[[开始, 结束, 文本], ...]`，用于导出 SRT 与字幕检查 |
| `window.qaText(t0, t1, step)` | 返回文字重叠、出画、停留过短、从未出现的报告 |

渲染器在地址后附加 `?render=1&scale=N`；页面可以按 `scale` 选择 2 倍尺寸的图片序列。
预览时打开 `index.html?dev=1&t=秒数`，底部出现播放按钮与拖动条。

## 动画库

页面按顺序加载 GSAP 与用到的插件（`node_modules/gsap/dist/*.min.js` 的 UMD 脚本），再以模块方式加载页面脚本：

```html
<script src="node_modules/gsap/dist/gsap.min.js"></script>
<script src="node_modules/gsap/dist/SplitText.min.js"></script>
<script src="node_modules/gsap/dist/DrawSVGPlugin.min.js"></script>
<script type="module" src="main.js"></script>
```

页面脚本从 `motion/motion.js`（由 `assets/motion/` 复制而来）导入转场与效果：

```js
import * as motion from './motion/motion.js';
motion.registerPlugins();
motion.usePersonality(TIMELINE.personality);
await document.fonts.ready;          // SplitText and Flip measure laid-out text
motion.seedRandom(SEED);
const tl = gsap.timeline({ paused: true });
// build scenes, transitions and effects on tl ...
window.renderFrame = async frame => { motion.renderAt(tl, frame / FPS, SEED, frame); /* ... */ };
```

函数、参数与组合规则见 [动效与转场](motion.md)。

## 确定性

- 所有动画放在一条暂停的 GSAP 时间轴上，`renderFrame` 调用 `motion.renderAt(tl, 秒, 种子, 帧号)`：它按帧号重新设置随机数种子、重新初始化进行中的乱码文字，再执行 `tl.time(t, false)`。每帧需要计算的内容（计数器、数据回放、粒子位置）写成以时间为参数的函数。
- 不使用 `Date.now()`、未设种子的随机数、CSS `transition` / `animation`、`<video>` 元素、`repeat: -1`。视频素材先导出成 `00000.jpg` 起编号的图片序列，按帧号设置 `src` 并等待 `decode()`。
- `fromTo()` 的起始与结束参数写全同一组属性；只写在一端的属性会随渲染顺序变化。
- 每个场景有不透明的背景，裁切类转场才能完整盖住上一个场景。
- 截图前等待两次 `requestAnimationFrame`，确保合成完成。
- 字体使用本地字体包（例如 `@fontsource-variable/noto-sans-sc`），就绪前用 `document.fonts.load(字重, 样例文字)` 加载页面上与动态文字中出现的全部字符；分区字体只下载出现过的字符。SplitText 与 Flip 在字体加载后调用。
- 通过“随机访问与连续渲染对比”检查确定性：同一帧分别直接跳转渲染与从前一秒逐帧推进渲染，像素差应接近 0（`render_frames.py check`）。

## 时间轴文件

时间轴 JSON 同时被页面和配乐脚本读取：

```json
{
  "fps": 30, "bpm": 120, "duration": 168, "personality": "precise", "seed": 2026,
  "scenes": [
    {"id": "open", "start": 0},
    {"id": "title", "start": 6, "transition": {"type": "shapeMorph", "duration": 1.2, "lead": 0.6, "color": "#ec4a22"}},
    {"id": "arch", "start": 14, "transition": {"type": "wipe", "duration": 0.8, "lead": 0.4, "direction": "left", "edge": "#ec4a22"}}
  ],
  "subtitles": [[0.6, 5.6, "一句完整的字幕。"]]
}
```

- `personality` 选择整片的缓动基调，`seed` 是随机数种子。
- 每个场景的 `transition` 描述它如何接替上一个场景：`type` 是 `motion.TRANSITIONS` 中的名称或本片新写的转场，`duration` 是时长，`lead` 是转场开始到场景起点的提前量，其余字段原样传给转场函数。`lead` 让转场中最显著的时刻（色带盖满、闪白、形状铺满）落在场景起点。
- 画面内事件（推力出现、状态切换、完成时刻）的偏移量也写在这里，配乐脚本用同样的数值计算音效时间。
- 场景起点放在小节线上，见 `scripts/tempo_grid.py`。

## 素材

- **三维与物理画面**：从记录中的状态（关节角、位姿）离线渲染，不重新计算物理过程；渲染分辨率取显示尺寸的 2 倍再缩小，4K 成片时再乘 2。机器人类场景可以用暗色地面、雾效与软阴影统一风格。
- **透明抠像**：封面或叠加用的主体，使用渲染器的分割通道（例如 MuJoCo segmentation rendering）只保留主体几何，排除地面与场景中的其他刚体。
- **界面与终端**：按视频风格重绘，结构与配色参考原界面，数值逐帧回放运行记录；终端输出用 `pyte` 等终端模拟库解释 ANSI 序列后逐帧显示。
- **品牌**：标志使用透明 PNG；`assets/watermark/` 有深色与浅色两个版本。

## 文字检查

`qaText` 逐帧扫描选择器匹配的文字元素：

- `overlaps`：两段可见文字的包围盒相交。位于转场时段内、长度不超过转场时长的重叠来自转场，其余需要调整版式或时间。
- `offscreen`：文字超出画面。
- `brief`：可见时间少于 0.8 s 的文字。
- `never`：从未达到可见透明度的文字。

```sh
python3 scripts/render_frames.py eval page/index.html "window.qaText(0, window.DURATION, 0.2)"
```
