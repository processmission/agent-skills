---
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
name: promo-video
description: >-
  Produce frame-exact promotional, comparison, and explainer videos from code and real data. Starts with a
  requirements discussion and creative brief, then a fact-checked storyboard and a motion plan composed from a GSAP
  transition and effect library (SplitText, DrawSVG, MorphSVG, MotionPath, Flip, ScrambleText), a deterministic
  HTML compositor rendered frame by frame in headless Chromium at 1080p or 4K, an original score in a style chosen
  with the requester (eleven styles from cinematic electronic and techno to lo-fi, acoustic, piano and strings, and
  orchestral, rendered with Csound synths and SoundFont instruments) with cue-driven sound effects on a shared bar
  grid, lookahead-limited mastering, picture and audio QA, covers, publishing copy, and a Process Mission watermark
  by default. Use for product films, OS or simulator comparisons, platform showcases, and Bilibili or YouTube
  uploads.
---

# 代码渲染宣传片

画面由代码逐帧算出，每一帧都是时间的纯函数；画面、数据、配乐与音效共用一份时间轴；片中的命令、输出和数字全部来自可以复现的记录。
动画使用 GSAP，转场与效果按每支片子的目的和内容组合；配乐从风格库出发，按简报选择风格并为本片编写段落、和声与动机。成片与封面默认加进程使命（Process Mission）水印。

## 成片标准

- **贴合需求**：风格、节奏和动效来自与需求方讨论后确认的创意简报；每支片子有自己的叙事结构、转场词汇和动效组合。
- **真实**：每个数字在事实核对表中有出处；对比双方的配置差异写进画面脚注；测量范围写进文案文档。无法核实的产品说法交给用户确认后再使用。
- **确定**：任意帧可以单独渲染，随机顺序与连续顺序渲染的结果一致，中断后可以接着渲染。
- **同一时间轴**：场景起点、转场、画面事件、配乐小节与音效提示点从同一个文件读取。修改时间只改这个文件。
- **可读**：每一刻只有一个视觉焦点；字幕一次一句完整的话；文字不重叠、不出画，停留时间足够读完。
- **声音**：原创配乐，风格与需求方试听样例后确定；程序合成音效；无旁白的成片约 −15 LUFS，有旁白约 −14 LUFS，真峰值不高于 −1 dBTP。
- **可重建**：交付时附带简报、分镜、动效计划、音乐计划、数据来源、测量范围与重新生成命令。

## 工作流程

1. **需求讨论**：与需求方分轮讨论目的、观众、平台、时长、必须出现的事实、品牌、风格参考、配乐、声音与交付；用转场与效果的联系表、配乐风格样例帮助对方表达偏好。结果写成创意简报，确认后再开始。见 [需求讨论与创意简报](references/brief.md)。
2. **收集事实与素材**：找到实验记录、日志、仓库文件和已有渲染结果；列出每个候选数字的来源、条件和负载。产品能力的描述单独列出，交给用户核实。
3. **叙事与分镜**：按简报选择叙事结构，写分镜表、事实核对表与字幕。见 [叙事、分镜与事实核对](references/storyboard.md)。
4. **动效计划**：按简报确定动效性格与 3–5 种转场的用途，逐场景选择效果、参数与节拍，写成动效计划表并确认；库里没有合适的效果时编写新效果。见 [动效与转场](references/motion.md)。
5. **时间轴**：选定速度（120 BPM 时一小节 2 秒），用 `scripts/tempo_grid.py` 把场景起点放到小节线或半小节上；转场与画面内事件的时间写进同一个时间轴文件。
6. **画面素材**：机器人、物理场景、芯片等三维画面用实际记录离线渲染成图片序列（目标分辨率的 2 倍超采样）；网页界面、终端与控制面板按视频风格重新绘制，数值逐帧回放记录。需要 4K 时素材按 2 倍尺寸渲染。
7. **合成页面**：页面按 [合成页面约定](references/page-contract.md) 实现，动画用 `assets/motion/motion.js` 与 GSAP 编写。`assets/page-template/` 演示约定与组合方式，场景内容、版式和动效按本片的分镜与动效计划重新编写。
8. **风格确认与画面质检**：先渲染风格帧与 10–20 秒样片请用户确认；再在每个转场前后与每段中间截帧拼成联系表，运行 `qaText`、`render_frames.py check` 与 `subtitles`。见 [质检](references/qa.md)。
9. **配乐、音效与旁白**：按需求讨论中试听选定的风格写音乐计划（风格与覆盖、段落能量、和弦、动机、音效），`scripts/compose_music.py` 合入页面提示点后用 Csound 与 FluidSynth 渲染；`scripts/master_audio.py` 做电平推子、旁白闪避与母带；`scripts/analyze_audio.py` 检查分段响度、频段分布与调内占比。见 [配乐](references/music.md) 与 [配乐、音效与旁白](references/audio.md)。
10. **渲染与合成**：`scripts/render_frames.py full` 分块并行渲染（`--scale 2` 输出 3840×2160），`mux` 合入音轨；`scripts/qa_frames.py` 扫描单帧闪烁与长黑场，`scripts/av_sync.py` 测量重击处音画偏移。
11. **水印**：`scripts/watermark.py video` 与 `scripts/watermark.py image` 给成片和封面加水印，默认使用进程使命标志，按所在角落的亮度自动选择浅色或深色版本。
12. **封面与发布文案**：用实测同一时刻的真实画面制作 16:9 与 4:3 封面，在缩略图尺寸检查可读性；写标题、简介、章节与标签。见 [封面、水印与发布](references/delivery.md)。
13. **交付**：成片（按需 1080p 与 4K）、音乐文件与分轨、封面、文案文档（简报、分镜与旁白、动效计划、音乐计划与结构、数据来源、测量范围、重新生成命令）。

## 规则

- 动手之前完成需求讨论；简报中的待确认事项清空后再进入分镜。
- 模板与图库用来理解约定和挑选效果，每支片子的场景、版式和动效组合都按本片重新设计；同一种转场不连续使用，作为主题反复出现的除外。
- 效果的选择由内容决定：数字、连线、层级、流动、状态切换各有对应的效果；参数随场景变化。
- 新写或修改的效果通过 `render_frames.py check` 后再用于成片。
- 配乐风格由简报与需求方试听决定；风格库提供起点，每支片子的段落能量、和弦进行、动机与编配按本片设计。参考曲目只用于测量，旋律、和声进行与采样都不搬用。
- 画面中的每个数字、命令和输出都能追溯到记录；记录里没有的量不画进画面。只有部分条件成立的结果，在同一画面写明条件。
- 对比双方的版本、配置或算法有差异时（例如一方启用了额外控制器或优化参数），在该段脚注中写明；结论只覆盖测量过的范围。
- 演示的系统与实际产品形态有区别时（例如只运行了产品的一部分），在文案文档的测量范围中写明，画面用词与实际运行内容一致。
- 用户提供的产品描述保持原意；扩写出的具体能力在交付说明中列出，请用户核实。
- 网页或终端画面按视频风格重绘时，保留原界面的结构与配色关系，数值来自运行记录；记录缺少的字段不显示。
- 修改时间后重新生成配乐，并在新画面上复查每个音画同步点。
- 不在交付内容中保留修改过程；文案只描述成片的最终状态。

## 资源

| 路径 | 内容 |
| --- | --- |
| `assets/motion/motion.js` | GSAP 转场 12 种、效果 18 种、确定的随机数、动效性格、`renderAt` |
| `assets/motion/gallery.html` | 逐个演示全部转场与效果的页面，用于挑选与向需求方展示 |
| `assets/page-template/` | 合成页面约定的示例：时间轴驱动的转场、效果组合、字幕、提示点、文字检查、音乐计划 |
| `assets/music/styles/` | 11 种配乐风格：音轨、节奏模式、各能量等级的编配、混音与音效设置 |
| `assets/music/promo.orc` | Csound 乐器：合成器、鼓组、音效、混响与延迟 |
| `assets/watermark/` | 进程使命标志的浅色与深色版本 |

GSAP 通过 npm 安装（`gsap` 3.15，全部插件免费可商用）；API 细节可以安装 GreenSock 官方的
[gsap-skills](https://github.com/greensock/gsap-skills)。原声乐器使用 General MIDI SoundFont，推荐 MIT 许可的 MuseScore_General.sf3，安装方法见 [配乐](references/music.md)。

## 脚本

| 脚本 | 作用 |
| --- | --- |
| `render_frames.py` | 截帧与联系表（`snap`）、分块并行渲染并在中断后继续渲染（`full`）、执行页面质检表达式（`eval`）、确定性对比（`check`）、字幕检查与 SRT 导出（`subtitles`）、合入音轨（`mux`） |
| `watermark.py` | 视频与图片水印；默认进程使命标志，可换标志、文字、位置、大小、透明度与显示时段 |
| `compose_music.py` | 读取音乐计划与风格，生成和声、编配、旋律与音效，用 Csound 与 FluidSynth 渲染并混音，输出分轨；`--preview` 渲染风格样例，`--list` 列出风格 |
| `master_audio.py` | 分段电平、旁白闪避、音效混合、均衡与压缩、响度标准化、前瞻限制器保持真峰值上限 |
| `analyze_audio.py` | 分段响度与六个频段的能量占比；速度、起音密度、亮度、响度范围、调内占比；与参考曲目对比；频谱图与波形图 |
| `qa_frames.py` | 成片单帧闪烁、整帧亮度跳变与长黑场扫描 |
| `av_sync.py` | 指定时间窗内画面亮度跳变与声音起音的偏移 |
| `tempo_grid.py` | 为场景起点寻找合适速度，或按给定速度把场景起点移到小节线与半小节上 |

依赖、参数与退出码见 [scripts/README.md](scripts/README.md)。
