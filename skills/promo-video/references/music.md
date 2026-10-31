<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# 配乐

`scripts/compose_music.py` 按音乐计划生成配乐。计划选定一种风格，写出调性、速度、段落，以及每段的能量与和弦；风格文件提供音轨、节奏模式和每个能量等级的编配。
合成器与鼓由 Csound（`assets/music/promo.orc`）渲染；钢琴、弦乐、吉他、铜管、合唱等原声乐器由 FluidSynth 渲染 General MIDI SoundFont。两部分最后混成一条 48 kHz 浮点音轨。

## 与需求方讨论配乐

配乐在需求讨论中一并确定（见 [需求讨论与创意简报](brief.md)），需要问清：

| 主题 | 问题 |
| --- | --- |
| 作用 | 配乐用来推动节奏、托住旁白，还是承担情绪？哪些段落要让位给画面里的声音？ |
| 类型 | 想要的类型与参考曲目；明确不要的类型 |
| 情绪曲线 | 每个部分的能量高低；高潮放在哪里；结尾是收束还是在重击处结束 |
| 速度 | 期望的快慢；剪辑节奏是否已经确定 |
| 乐器 | 喜欢或要避开的音色，例如“不要电子鼓”“希望有钢琴” |
| 旁白 | 有旁白时，旁白段落的配乐保持稀疏，旋律让位 |
| 播放场景 | 展会循环播放要求首尾衔接；平台的版权检测要求配乐全部原创 |

需求方难以用文字描述时，渲染风格样例请对方试听挑选（见下文“风格样例”）。
需求方提供参考曲目时，用 `analyze_audio.py --profile` 测量它的速度、起音密度、亮度、响度范围与频段分布，作为计划的参数依据。
参考曲目只用于测量，旋律、和声进行与采样都不搬用。

## 风格库

`assets/music/styles/` 中每个 JSON 文件是一种风格，`python3 scripts/compose_music.py --list` 列出全部风格。

| 风格 | 速度 | 调式与和声 | 主要音色 | 适合 |
| --- | --- | --- | --- | --- |
| `cinematic-tech` | 110–128 | 小调 i–VI–III–VII | 模拟铺底、脉冲贝斯、拨弦琶音、四拍底鼓、侧链压缩 | 产品发布、技术对比 |
| `corporate` | 104–126 | 大调 I–V–vi–IV | 钢琴八分音符、钢弦吉他扫弦、拨弦、拍手与沙锤、钟琴主题 | 企业介绍、客户案例 |
| `lofi` | 70–92 | 大调七和弦 ii7–V7–Imaj7 | 电钢琴、低音提琴、摇摆节奏的软鼓、黑胶底噪、暗淡的高频 | 开发日常、教程、轻松讲解 |
| `orchestral` | 76–104 | 小调 | 弦乐长音与固定音型、大提琴、定音鼓、铜管、圆号主题、合唱、大鼓 | 愿景、里程碑、宏大叙事 |
| `synthwave` | 96–118 | 小调 | 八度锯齿波贝斯、模拟铺底、琶音、门限混响军鼓、颤音主奏 | 复古科技、游戏、硬件 |
| `ambient` | 56–84 | 大调，两小节一换 | 缓慢铺底、低音持续音、稀疏的马林巴与钢琴、长混响 | 旁白密集的讲解、展厅循环 |
| `future-bass` | 140–160 | 大调七和弦 | 侧链抽吸的超级锯齿波和弦、半拍鼓、808 低音、拨弦主题 | 面向年轻观众的发布、短视频 |
| `acoustic` | 84–112 | 大调 | 尼龙吉他分解和弦、钢弦吉他扫弦、低音提琴、马林巴、拍手与沙锤 | 人物故事、社区、教育 |
| `minimal-techno` | 120–130 | 小调，少量和弦 | 四拍底鼓、反拍踩镲、滚动低音、带延迟的和弦短音、咔嗒声 | 系统运行、数据流、工程演示 |
| `piano-strings` | 60–90 | 大调 vi–IV–I–V | 带延音踏板的钢琴分解和弦、抒情旋律、弦乐渐强、大提琴 | 情感段落、结尾、致谢 |
| `trap` | 130–150 | 小调 | 半拍鼓与滚动踩镲、808 长音、暗色铃音琶音 | 酷感预告、潮流产品 |

风格是起点：计划可以覆盖风格中的任何字段，可以从其他风格借用音轨，也可以写新的风格文件。

## 风格样例

```sh
python3 scripts/compose_music.py --preview previews
python3 scripts/compose_music.py --preview previews --only lofi,acoustic,piano-strings --bars 12
```

每种风格渲染一段样例，从能量 1 逐段升到能量 4，使用风格默认的速度、调性与和弦。
把 2–3 个候选样例发给需求方试听；选定风格后，再按片子的内容写音乐计划。

## 音乐计划

```json
{
  "style": "lofi",
  "bpm": 84, "duration": 45.714, "key": "F", "mode": "major", "seed": 3,
  "tracks": {
    "strings": {"from": "orchestral.strings", "gain": -12},
    "theme": {"instrument": "mallet", "pattern": "motif", "register": [65, 84], "gain": -9}
  },
  "patterns": {
    "motif": {"type": "melody", "bars": 2, "snap": true,
              "motif": [[0, 4, 5, 1], [4, 2, 6, 0.8], [6, 2, 5, 0.8], [8, 8, 3, 0.9], [16, 4, 2, 0.9], [24, 8, 1, 0.9]]}
  },
  "sections": [
    {"name": "intro", "start": 0, "end": 5.714, "energy": 1, "chords": ["ii7", "V7"], "level": -3},
    {"name": "verse", "start": 5.714, "end": 17.143, "energy": 3, "chords": ["ii7", "V7", "Imaj7", "vi7"]},
    {"name": "lift", "start": 17.143, "end": 28.571, "energy": 4, "chords": ["IVmaj7", "iii7", "ii7", "Imaj7"],
     "tracks": {"lead": false, "theme": true, "strings": true}},
    {"name": "key-up", "start": 28.571, "end": 40, "energy": 4, "key": "G", "chords": ["ii7", "V7", "Imaj7", "vi7"],
     "tracks": {"theme": true, "drums": {"pattern": "rims"}}},
    {"name": "outro", "start": 40, "end": 45.714, "energy": 0, "key": "G", "chords": ["IVmaj7", "Imaj7"]}
  ],
  "hits": [{"t": 17.143, "amp": 0.5}],
  "risers": [{"end": 28.571, "duration": 2.857, "amp": 0.3}]
}
```

全局字段：

| 字段 | 含义 |
| --- | --- |
| `style` | 风格名称（在 `--styles` 指定的目录、计划目录下的 `styles/`、`assets/music/styles/` 中依次查找），或风格 JSON 的路径 |
| `bpm`、`meter`、`grid` | 速度；每小节拍数（默认 4）；每小节步数（默认 16，即十六分音符） |
| `key`、`mode` | 调性与调式（`major`、`minor`、`dorian`、`mixolydian`、`lydian`、`phrygian`），由 music21 解析 |
| `seed` | 随机种子。旋律生成与人性化偏移都由它决定，同一份计划总是生成同一首曲子 |
| `swing`、`swing_grid` | 摇摆比例（0.5 为平直，0.56–0.62 是常见的十六分音符摇摆）与摇摆作用的音符单位 |
| `humanize` | 时间（秒）与力度（比例）的随机偏移，例如 `{"time": 0.006, "velocity": 0.08}` |
| `bars_per_chord` | 每个和弦占几小节，段落可以单独设置 |
| `tail` | 结尾保留的混响尾音秒数，默认 5 |
| `tracks`、`patterns`、`arrangements`、`fills`、`entry`、`mix`、`fx`、`master` | 与风格逐层合并，计划中的值优先 |

段落字段：

| 字段 | 含义 |
| --- | --- |
| `name`、`start`、`end` | 段落名称与起止时间（秒），起止都放在小节线上 |
| `energy` | 0–4，选择风格中对应的编配 |
| `chords` | 罗马数字级数（`ii7`、`V7/V`、`bVI`，相对于本段调性），或和弦符号（`Bbmaj9`、`F/A`、`Bm7b5`） |
| `bars_per_chord` | 一个数字，或与 `chords` 一一对应的列表 |
| `tracks` | 在编配的基础上增删或修改音轨：`false` 去掉，`true` 加入，对象覆盖音轨字段（例如 `{"pattern": "rims", "gain": -6}`） |
| `key`、`mode` | 本段转调 |
| `fill` | 段尾加花。下一段能量更高时默认加入，`false` 关闭，`true` 强制加入 |
| `level` | 推子电平（dB），`master_audio.py` 在段落之间平滑过渡 |
| `role`、`progression` | 没有写 `chords` 时，取风格 `progressions[role]` 中的第 `progression` 条进行 |

`hits`、`risers` 等音效字段见 [配乐、音效与旁白](audio.md)。

## 音轨与模式

音轨字段：

| 字段 | 含义 |
| --- | --- |
| `engine` | `csound`（默认）或 `soundfont` |
| `instrument` | Csound 音色：`bass`、`pluck`、`pad`、`drone`、`epiano`、`supersaw`、`sawbass`、`bass808`、`lead`、`mallet`、`stab`、`string`；底噪音色 `vinyl` |
| `program`、`bank` | General MIDI 音色号：0 钢琴、9 钟琴、12 马林巴、24 尼龙吉他、25 钢弦吉他、32 低音提琴、33 电贝斯、40 小提琴、42 大提琴、47 定音鼓、48 弦乐合奏、49 慢弦乐、52 合唱、55 管弦乐重击、60 圆号、61 铜管组 |
| `kit` | 鼓的声部映射。Csound 鼓为 `kick`、`softkick`、`snare`、`gated`、`clap`、`rim`、`hat`、`shaker`、`tom`、`crash`、`tick`，可以附带 `tone`、`pan`、`gain`、`reverb`；SoundFont 鼓写 General MIDI 打击乐音符号 |
| `pattern` | 模式名称，或直接写模式对象 |
| `register` | 音域（MIDI 音符号的上下限） |
| `voicing` | `close`、`open`、`drop2`、`spread`（根音在低八度）、`shell`（根音、三音、七音）、`triad`、`power` |
| `gain`、`pan`、`brightness`、`attack`、`release`、`gate` | 电平（dB）、声像（0–1）、亮度（0–1）、起音与释音（秒）、音符时值比例 |
| `reverb`、`delay`、`duck` | 混响与延迟的发送量；底鼓侧链压缩的深度 |
| `swell`、`sustain` | SoundFont 音轨专用：每个和弦内的表情渐强（CC11）；随和弦更换的延音踏板（CC64） |
| `from` | 借用其他风格的音轨及其模式，例如 `"orchestral.strings"`；其余字段覆盖借来的设置 |

模式类型：

| `type` | 字段 | 用途 |
| --- | --- | --- |
| `chord` | `hits: [[步, 长度, 力度], ...]` 与 `bars`；或 `hold: true`，每个和弦奏一个长音 | 和弦节奏、铺底、长音 |
| `strum` | `hits: [[步, 长度, 力度, "down" 或 "up"], ...]`，`spread` 为相邻弦的间隔（秒） | 吉他扫弦 |
| `arp` | `rate`（每个音占几步）、`order`（和弦音序号，`null` 为休止）、`octaves`、`gate`、`velocity`（循环的力度重音） | 琶音、分解和弦、固定音型 |
| `bass` | `notes: [[步, 长度, 音, 力度], ...]`；音为 `root`、`third`、`fifth`、`seventh`、`octave`、`approach`（下一和弦根音的半音邻音）、`passing`（通往下一根音的音阶经过音）或相对根音的半音数 | 贝斯线、定音鼓、低音乐器 |
| `melody` | `generate: {density, phrase_bars, form, seed}` 按种子生成乐句，`form` 写成 `["A", "A2", "B", "A"]`（A2 是 A 的变奏）；或 `motif: [[步, 长度, 音级, 力度], ...]` 写出动机（音级 1 为主音），`snap: true` 让拍点上的音落在和弦音上 | 主题、主奏 |
| `drums` | 每个声部一个力度数组，长度为 `grid × bars` | 鼓组 |
| `drone` | `tone`（`root`、`fifth` 等），`follow: true` 时跟随和弦 | 持续低音 |
| `texture` | 无 | 黑胶底噪等贯穿整段的音色 |

风格中的 `arrangements` 为每个能量等级列出要演奏的音轨与覆盖字段；`fills` 指定段尾加花的模式；`entry` 是能量上升的段落起点处加入的鼓声部（例如镲片）；
`mix` 设置混响、延迟、侧链深度、鼓组母线的削波量（`drum_bus.clip`，单位 dB）以及整体的低通、饱和、比特压缩和抖动效果；`master` 设置母带的低频与高频搁架滤波。

## 编曲规则

- **风格来自简报**：按情绪、观众与播放场景选择风格，或用 `from` 组合几种风格的音轨（例如 lofi 的鼓组加 orchestral 的弦乐）。同一产品的不同影片可以使用不同风格。
- **能量跟随叙事**：每个段落的 `energy` 对应分镜中的情绪曲线；开场与讲解段一般为 0–2，实测或高潮段为 3–4，结尾回落。相邻段落的能量变化与画面转场同步。
- **每支片子有自己的动机**：用 `motif` 写出 2 小节主题，或固定 `generate` 的 `seed`；动机在开场、高潮与结尾重复出现，每次更换乐器、音区或配器。
- **段落之间有变化**：相邻段落至少改变一项（编配、模式、音区、和弦节奏、调性）；重复出现的段落更换鼓型或加入新的声部。
- **旁白段落让位**：去掉主奏与旋律，或把旋律放在旁白的停顿处；避免 1–4 kHz 的密集声部。
- **与画面同步**：重击、上升音效与转场落在同一时刻，段落起点放在小节线上（见 [配乐、音效与旁白](audio.md)）。
- **结尾**：最后一段回到主和弦或同主音大调，用低能量收束，或在最后一拍重击后留出混响尾音。
- **原创**：和弦进行、动机与编配都为本片设计；参考曲目只提供速度、密度、亮度这类测量值。

## 定制与扩展

- **新风格**：复制一个风格文件改写，放进计划目录下的 `styles/`，或用 `--styles` 指定目录。字段与上面的表格相同；`preview` 设置样例的小节数和能量序列。
- **新音色**：在 `promo.orc` 中按旋律乐器或鼓的参数约定加入乐器，并在 `compose_music.py` 的 `MELODIC` 或 `DRUMS` 表中登记名称。
- **原声音色**：任何 General MIDI 音色都可以通过 `"engine": "soundfont"` 与 `program` 使用。
- **继续修改**：`<输出>.sco` 是 Csound 乐谱；`<输出>.stems/` 包含 Csound 输出（前两个声道为音乐，后两个声道为鼓组）、处理后的鼓组母线、每个 SoundFont 音轨的 MIDI 与 WAV，可以导入音频工作站。

## SoundFont

使用 SoundFont 音轨的风格需要 FluidSynth 与一个 General MIDI SoundFont。推荐 MuseScore_General.sf3（MIT 许可，约 38 MB）：

```sh
mkdir -p ~/.local/share/soundfonts
curl -L -o ~/.local/share/soundfonts/MuseScore_General.sf3 \
  https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf3
```

脚本依次查找 `--soundfont`、`~/.local/share/soundfonts/MuseScore_General.sf3`、
`/usr/share/sounds/sf3/MuseScore_General_Full.sf3`（Debian 包 `musescore-general-soundfont`）与 `/usr/share/sounds/sf2/FluidR3_GM.sf2`（Debian 包 `fluid-soundfont-gm`）。
换用其他音色库前，确认其许可允许商业使用。

## 检查

- `analyze_audio.py mix.wav --plan plan.json --profile` 报告速度、起音密度、频谱重心、响度范围，以及谐波部分落在调内的能量占比；调内占比明显偏低时，检查和弦符号、转调与旋律。
- 与参考曲目对比：先 `analyze_audio.py ref.wav --profile --json ref.json`，再 `analyze_audio.py mix.wav --compare ref.json`。速度检测可能给出实际速度的一半或两倍；弦乐长音、氛围铺底这类节拍不明显的音乐，检测值误差更大，以计划中的速度为准。
- 智能体无法试听，以这些测量值、频谱图和波形图作为验收依据；样例与初版都请需求方试听确认。
