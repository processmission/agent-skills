# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SKILL = Path(__file__).resolve().parents[1]
LOGOS = {'light': SKILL / 'assets/watermark/process-mission-light.png',
         'dark': SKILL / 'assets/watermark/process-mission-dark.png'}
INK = {'light': (242, 242, 242), 'dark': (20, 20, 20)}
FONT_CANDIDATES = [
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/System/Library/Fonts/STHeiti Medium.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
    'C:/Windows/Fonts/msyh.ttc',
]
POSITIONS = ('br', 'bl', 'tr', 'tl', 'center')
DESCRIPTION = ('Add a logo or text watermark to a video or an image. The default mark is the Process Mission logo; '
               'its light or dark variant follows the brightness of the corner it covers unless --variant is given.')


def tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise SystemExit(f'{name} is required but was not found on PATH')
    return path


def probe(path: Path) -> dict:
    out = subprocess.run([tool('ffprobe'), '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=width,height,color_primaries,color_transfer,color_space:format=duration',
                          '-of', 'json', str(path)], check=True, capture_output=True, text=True).stdout
    info = json.loads(out)
    stream = info['streams'][0]
    return {'width': int(stream['width']), 'height': int(stream['height']),
            'duration': float(info['format'].get('duration', 0) or 0),
            'color': {key: stream.get(key) for key in ('color_primaries', 'color_transfer', 'color_space')}}


def find_font(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    raise SystemExit('no CJK-capable font found; pass --font /path/to/font.ttf')


def build_mark(args, variant: str, frame_width: int, frame_height: int) -> Image.Image:
    if args.text:
        size = max(10, round(frame_height * args.text_size))
        font = ImageFont.truetype(find_font(args.font), size)
        left, top, right, bottom = font.getbbox(args.text)
        pad = max(2, size // 8)
        image = Image.new('RGBA', (right - left + pad * 2, bottom - top + pad * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        shadow = (0, 0, 0, 110) if variant == 'light' else (255, 255, 255, 110)
        draw.text((pad - left + max(1, size // 24), pad - top + max(1, size // 24)), args.text, font=font, fill=shadow)
        draw.text((pad - left, pad - top), args.text, font=font, fill=(*INK[variant], 255))
    else:
        image = Image.open(args.logo or LOGOS[variant]).convert('RGBA')
        width = max(8, round(frame_width * args.width))
        image = image.resize((width, max(1, round(image.height * width / image.width))), Image.Resampling.LANCZOS)
    if args.opacity < 1:
        alpha = np.asarray(image.getchannel('A'), dtype=np.float32) * args.opacity
        image.putalpha(Image.fromarray(alpha.round().astype(np.uint8)))
    return image


def place(position: str, frame: tuple[int, int], mark: tuple[int, int], margin: int) -> tuple[int, int]:
    width, height = frame
    mark_width, mark_height = mark
    x = {'l': margin, 'r': width - mark_width - margin}
    y = {'t': margin, 'b': height - mark_height - margin}
    if position == 'center':
        return (width - mark_width) // 2, (height - mark_height) // 2
    return x[position[1]], y[position[0]]


def region_luminance(images: list[Image.Image], box: tuple[int, int, int, int]) -> float:
    values = []
    for image in images:
        crop = np.asarray(image.convert('RGB').crop(box), dtype=np.float32) / 255
        values.append(float((crop @ np.array([.2126, .7152, .0722])).mean()))
    return float(np.median(values))


def video_samples(path: Path, duration: float, count: int = 9) -> list[Image.Image]:
    samples = []
    for index in range(count):
        seconds = duration * (index + .5) / count
        data = subprocess.run([tool('ffmpeg'), '-v', 'error', '-ss', f'{seconds:.3f}', '-i', str(path), '-frames:v', '1',
                               '-f', 'image2pipe', '-vcodec', 'png', '-'], check=True, capture_output=True).stdout
        if data:
            samples.append(Image.open(io.BytesIO(data)))
    return samples


def choose_variant(args, samples: list[Image.Image], frame: tuple[int, int]) -> tuple[str, float | None]:
    if args.variant != 'auto' or args.logo:
        return ('light' if args.variant == 'auto' else args.variant), None
    probe_args = argparse.Namespace(**{**vars(args), 'opacity': 1.0})
    mark = build_mark(probe_args, 'light', *frame)
    x, y = place(args.position, frame, mark.size, round(frame[0] * args.margin))
    luminance = region_luminance(samples, (x, y, x + mark.width, y + mark.height))
    return ('light' if luminance < args.threshold else 'dark'), luminance


def watermark_image(args) -> dict:
    source = Image.open(args.input)
    frame = source.size
    variant, luminance = choose_variant(args, [source], frame)
    mark = build_mark(args, variant, *frame)
    x, y = place(args.position, frame, mark.size, round(frame[0] * args.margin))
    result = source.convert('RGBA')
    result.alpha_composite(mark, (x, y))
    output = Path(args.output)
    if output.suffix.lower() in ('.jpg', '.jpeg'):
        result.convert('RGB').save(output, quality=args.jpeg_quality, subsampling=0)
    else:
        result.save(output)
    return {'output': str(output), 'variant': variant, 'region_luminance': luminance,
            'box': [x, y, x + mark.width, y + mark.height]}


def watermark_video(args) -> dict:
    info = probe(Path(args.input))
    frame = (info['width'], info['height'])
    variant, luminance = choose_variant(args, video_samples(Path(args.input), info['duration']), frame)
    mark = build_mark(args, variant, *frame)
    x, y = place(args.position, frame, mark.size, round(frame[0] * args.margin))
    output = Path(args.output).resolve()
    enable = ''
    if args.start is not None or args.end is not None:
        enable = f":enable='between(t,{args.start or 0},{args.end if args.end is not None else info['duration'] + 1})'"
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='.watermark-') as work:
        mark_path = Path(work) / 'mark.png'
        mark.save(mark_path)
        command = [tool('ffmpeg'), '-y', '-v', 'error', '-i', str(args.input), '-i', str(mark_path),
                   '-filter_complex', f'[0:v][1:v]overlay=x={x}:y={y}:format=auto{enable}[v]',
                   '-map', '[v]', '-map', '0:a?', '-c:v', 'libx264', '-preset', args.preset, '-crf', str(args.crf),
                   '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart']
        tags = {'color_primaries': '-color_primaries', 'color_transfer': '-color_trc', 'color_space': '-colorspace'}
        for key, flag in tags.items():
            if info['color'].get(key) and info['color'][key] != 'unknown':
                command += [flag, info['color'][key]]
        subprocess.run(command + [str(output)], check=True)
    return {'output': str(output), 'variant': variant, 'region_luminance': luminance,
            'box': [x, y, x + mark.width, y + mark.height], 'size': list(frame)}


def main() -> None:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('kind', choices=('video', 'image'))
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--logo', help='custom logo image; defaults to the Process Mission logo')
    parser.add_argument('--variant', choices=('auto', 'light', 'dark'), default='auto',
                        help='light marks for dark footage, dark marks for light footage (default: auto)')
    parser.add_argument('--text', help='draw this text instead of a logo')
    parser.add_argument('--font', help='font file for --text')
    parser.add_argument('--text-size', type=float, default=.026, help='text height as a fraction of frame height')
    parser.add_argument('--position', choices=POSITIONS, default='br')
    parser.add_argument('--width', type=float, default=.13, help='logo width as a fraction of frame width')
    parser.add_argument('--margin', type=float, default=.025, help='margin as a fraction of frame width')
    parser.add_argument('--opacity', type=float, default=.85)
    parser.add_argument('--threshold', type=float, default=.55, help='corner luminance below which the light mark is used')
    parser.add_argument('--start', type=float, help='video: first second showing the mark')
    parser.add_argument('--end', type=float, help='video: last second showing the mark')
    parser.add_argument('--crf', type=int, default=16)
    parser.add_argument('--preset', default='slow')
    parser.add_argument('--jpeg-quality', type=int, default=93)
    args = parser.parse_args()
    if not 0 < args.opacity <= 1 or not 0 < args.width < 1:
        parser.error('--opacity must be in (0, 1] and --width in (0, 1)')
    if Path(args.input).resolve() == Path(args.output).resolve():
        parser.error('output must differ from input')
    report = watermark_video(args) if args.kind == 'video' else watermark_image(args)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
