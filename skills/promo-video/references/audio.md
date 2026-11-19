<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# 配乐、音效与旁白

配乐的风格、计划与编曲见 [配乐](music.md)。本文说明小节网格、音效、旁白与母带。

## 小节网格

- 速度取整数：120 BPM 时一拍 0.5 s、一小节 2 s，场景起点、重击与段落切换都落在小节线上。
- `scripts/tempo_grid.py --timeline timeline.json --bpm 120 --major title,bridge,close` 给出移到小节网格后的起点与最大偏移；
  移动不超过 1 s 的起点通常不影响内容，移动后重新渲染画面。
- 有旁白时以旁白时长排布场景：每段结束时间向上取整到小节线，富余的小节分给可以拉长的段落。

## 音效

音乐计划中的音效列表与页面提示点由 `compose_music.py` 一起写进乐谱：

```json
{
  "hits": [{"t": 6, "amp": 0.95, "shimmer": 0.55}],
  "risers": [{"end": 6, "duration": 3, "amp": 0.22}],
  "swells": [{"end": 6, "duration": 1.6, "chord": "Dm", "amp": 0.16}],
  "rolls": [{"start": 156, "duration": 2, "low": 0.06, "high": 0.5}],
  "thuds": [{"t": 0.7, "amp": 0.85}],
  "bells": [{"t": 6.5, "note": "A5", "amp": 0.13, "duration": 1.6}],
  "chimes": [{"t": 99.63, "bright": true}]
}
```

| 字段 | 含义 |
| --- | --- |
| `hits` | 重击。叠加哪些层由风格的 `fx.hit` 决定：电影感低频重击（`impact`）、底鼓、镲片、门限军鼓，或 SoundFont 的定音鼓与管弦乐重击 |
| `risers` | 在 `end` 时刻结束、持续 `duration` 秒的上升音效。风格的 `fx.riser` 选择噪声上升（`riser`）、反向镲片（`reverse`）或和弦渐强（`swell`） |
| `swells` | 指定和弦的反向渐强 |
| `rolls` | 滚奏，从 `low` 渐强到 `high`；风格的 `fx.roll` 选择所用的鼓 |
| `thuds` / `bells` / `chimes` | 撞击声、铃音旋律、成功提示音（`bright` 为明亮版本） |

页面提示点的映射：`impact` → 重击，`thud` → 撞击声，`chime` → 提示音，`blip` → 吸附到当前调内音阶的短铃音，`riser` → 以该时刻结束的上升音效。
`transition` 提示点只用于画面质检，配乐脚本跳过它；转场需要的声音由页面另外发出 `riser` 或 `impact`，按转场的性格选择（色带、形状变形配上升音效，闪白、故障切换配重击，叠化可以不配音效）。

- 进入新段落前一小节放上升音效、加花或属和弦，下一段第一拍放重击；重击时底鼓、镲片与低频同时落下，落差更明显。
- 画面事件对应音效：推力出现配撞击声，“控制就绪”“恢复站立”“完成”配提示音（产品方明亮，基准方柔和），数据画面可以叠加高频节拍声。
- 重击与提示音的音色跟随风格：管弦乐风格用定音鼓和管弦乐重击，原声风格用底鼓和镲片，电子风格用低频重击。

## 旁白

- 文案按句写进脚本 JSON；`edge-tts` 合成时请求 `WordBoundary`，用词边界生成逐字字幕时间；以“音色 | 语速 | 文本”的哈希缓存音频。
- 用 Whisper 转写每句旁白，对照脚本检查读音与多音字。
- `master_audio.py --voice voice.wav` 把旁白单独压到 −16 LUFS，配乐压到 −16.5 LUFS，旁白出现时配乐闪避 10.5 dB。

## 母带与检查

```sh
python3 scripts/master_audio.py music.wav mix.wav --plan plan.json --target -15 --ceiling -1.5
python3 scripts/analyze_audio.py mix.wav --plan plan.json --profile --spectrum spectrum.png --wave wave.png
```

- 母带流程：段落推子、整体均衡（低频与高频搁架取自风格的 `master`）与压缩，然后用 FFmpeg 的前瞻限制器（`alimiter`）把响度提到目标，同时保持 4 倍过采样测得的真峰值不超过上限。
- 响度：无旁白 −15 LUFS，有旁白 −14 LUFS；真峰值不高于 −1.5 dBTP（AAC 编码后约 −1 dBTP）。
- 报告中的 `limiter_depth_db` 是峰值被压低的量，通常在 3 dB 以内；超过 6 dB 时检查重击、鼓组与起音很快的音色是否过响。
- 电子风格的频段能量占比参考值：sub −8、bass −3、low-mid −7、mid −12、presence −18、air −24 dB。其他风格与需求方的参考曲目对比（`--compare`）。
  低频过重时降低贝斯、808、持续音和重击；中高频不足时提高琶音、镲片和铃音，或在风格的 `master` 中提高高频搁架。
- 波形图应能看出段落起伏；频谱图上重击、上升音效与段落切换的位置应与分镜一致。
- 成片合成后用 `ffmpeg -i film.mp4 -map 0:a -af ebur128=peak=true -f null -` 复核成片响度。
- 智能体无法试听时，以响度、频段占比、调内占比、频谱图、波形图和音画同步测量作为验收依据，并在交付说明中写明检查方式。
