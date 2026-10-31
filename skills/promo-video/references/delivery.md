<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# 封面、水印与发布

## 水印

`scripts/watermark.py` 默认使用进程使命（Process Mission）标志，放在右下角，宽度为画面宽度的 13%，透明度 0.85。
脚本抽取若干帧测量水印所在区域的平均亮度：低于 0.55 时用浅色标志（白字红标），否则用深色标志（黑字红标）。

```sh
python3 scripts/watermark.py video film.mp4 film-watermarked.mp4
python3 scripts/watermark.py image cover.png cover-watermarked.jpg --position tr
python3 scripts/watermark.py video film.mp4 out.mp4 --text "进程使命 · Process Mission" --position bl
python3 scripts/watermark.py video film.mp4 out.mp4 --logo partner.png --width .1 --start 6 --end 160
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--position` | `br` | `br`、`bl`、`tr`、`tl`、`center` |
| `--width` | `0.13` | 标志宽度占画面宽度的比例 |
| `--margin` | `0.025` | 边距占画面宽度的比例 |
| `--opacity` | `0.85` | 水印透明度 |
| `--variant` | `auto` | `light`（深色画面用）、`dark`（浅色画面用） |
| `--logo` / `--text` / `--font` | | 换成其他标志或文字；文字默认查找系统中文字体 |
| `--start` / `--end` | 全片 | 只在该时段显示 |
| `--crf` / `--preset` | `16` / `slow` | 视频重新编码质量；音轨直接复制 |

- 成片画面里已经有品牌标志的位置，水印放到另一个角落。
- B 站开启平台水印时会在右上角加上账号标识，自有水印放在其他角落。
- 4K 成片加水印时 `--crf 15`，保持与渲染时相同的质量。

## 封面

- 尺寸：16:9 为 1920×1080，4:3 为 1440×1080；分别排版，不直接裁切。
- 主体：使用实测中同一时刻的真实画面或抠像，例如一方已经恢复站立、另一方仍倒地，配上对应的实测数字。
- 标题：两行以内，一行白色一行品牌色，与视频标题一致。
- 标签放在主体旁边的空白处，数字使用实底标签保证可读；关键内容避开右下角，平台会在那里显示时长。
- 把封面缩小到 320×180 与 240×180 检查：标题、主体与产品名应能看清。
- 导出 PNG 原图与 JPG（质量 93）；需要时用 `watermark.py image` 加水印。

## 发布文案（B 站）

- **标题**（80 字以内）：一个问题或反差加对比对象与形式，例如“同一只机器鸭，换个操作系统差多少？官方固件 vs 新系统 仿真实测”。
- **简介**：开场一句、产品介绍、平台介绍、实测结果（双方数字与条件）、测试说明（测量范围与配置差异）、章节时间、原创配乐说明、公司名称。
- **章节**：按分镜段落写 `mm:ss 标题`，与视频中的段落标题一致。
- **标签**：不超过 10 个，覆盖领域（具身智能、操作系统）、技术（Zephyr、Linux、仿真）与对象。

## 交付清单

- 成片：`<名称>-1080p.mp4`，按需 `<名称>-4k.mp4`（H.264，AAC 320 kbps / 48 kHz）。
- 音乐：48 kHz / 24 bit WAV。
- 封面：16:9 与 4:3 的 PNG 和 JPG。
- 文案文档：分镜与旁白、音乐结构、数据来源、测量范围、重新生成命令。
- 交付说明列出需要用户确认的产品描述与自行补充的文字。
