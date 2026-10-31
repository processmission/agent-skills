# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import asyncio
import base64
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse

from playwright.async_api import async_playwright

DESCRIPTION = ('Frame-exact renderer for a compositor page that follows the promo-video page contract: '
               'window.ready, window.DURATION, window.FPS and an async window.renderFrame(frame).')
SKIP_DIRS = {'node_modules', '.git', '__pycache__'}
OUTPUT_SUFFIXES = {'.mp4', '.mov', '.mkv', '.wav', '.m4a', '.aac', '.part'}
BROWSER_ARGS = ['--enable-gpu', '--ignore-gpu-blocklist', '--force-color-profile=srgb', '--hide-scrollbars',
                '--mute-audio', '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows', '--font-render-hinting=none']
if sys.platform == 'darwin':
    BROWSER_ARGS.insert(0, '--use-angle=metal')


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise SystemExit(f'{name} is required but was not found on PATH')
    return path


class Site:
    def __init__(self, page: Path, root: Path | None, size: tuple[int, int], scale: float):
        self.page = page.resolve()
        self.root = (root or self.page.parent).resolve()
        if self.root not in self.page.parents:
            raise SystemExit(f'{self.page} is outside the served root {self.root}')
        self.size = size
        self.scale = scale
        handler = functools.partial(QuietHandler, directory=str(self.root))
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        relative = urllib.parse.quote(self.page.relative_to(self.root).as_posix())
        self.url = f'http://127.0.0.1:{self.server.server_port}/{relative}?render=1&scale={scale:g}'

    def fingerprint(self) -> str:
        # Path, size and modification time of every served file; content hashing is too slow for frame folders.
        # The renderer itself is part of the key, so chunks from an older capture method are not reused.
        renderer = Path(__file__).resolve().stat()
        digest = hashlib.sha256(f'{self.size}|{self.scale}|{renderer.st_size}|{renderer.st_mtime_ns}'.encode())
        for folder, dirs, files in os.walk(self.root):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith('.'))
            for name in sorted(files):
                path = Path(folder) / name
                if path.suffix.lower() in OUTPUT_SUFFIXES:
                    continue
                stat = path.stat()
                digest.update(f'{path.relative_to(self.root)}|{stat.st_size}|{stat.st_mtime_ns}'.encode())
        return digest.hexdigest()[:12]


class Page:
    def __init__(self, playwright, site: Site, label: str = 'main'):
        self.playwright, self.site, self.label = playwright, site, label
        self.browser = self.page = self.cdp = None
        self.fps = 30.0
        self.duration = 0.0

    async def open(self) -> None:
        await self.close()
        self.browser = await self.playwright.chromium.launch(headless=True, args=BROWSER_ARGS)
        width, height = self.site.size
        self.page = await self.browser.new_page(viewport={'width': width, 'height': height},
                                                device_scale_factor=self.site.scale)
        self.page.on('console', lambda m: print(f'[{self.label}] {m.type}: {m.text}', file=sys.stderr)
                     if m.type in ('error', 'warning') else None)
        self.page.on('pageerror', lambda e: print(f'[{self.label}] pageerror: {e}', file=sys.stderr))
        await self.page.goto(self.site.url, wait_until='domcontentloaded', timeout=180_000)
        await self.page.wait_for_function('window.ready === true', timeout=300_000, polling=200)
        self.fps = float(await self.page.evaluate('window.FPS || 30'))
        self.duration = float(await self.page.evaluate('window.DURATION'))
        self.cdp = await self.page.context.new_cdp_session(self.page)

    async def close(self) -> None:
        if self.browser is not None:
            try:
                await asyncio.wait_for(self.browser.close(), 20)
            except Exception:
                pass
        self.browser = None

    async def grab(self, frame: int) -> bytes:
        await self.page.evaluate('f => window.renderFrame(f)', frame)
        # A raw CDP capture comes back at CSS size; the clip scale yields the device-pixel render at --scale.
        width, height = self.site.size
        shot = await self.cdp.send('Page.captureScreenshot', {
            'format': 'png', 'optimizeForSpeed': True,
            'clip': {'x': 0, 'y': 0, 'width': width, 'height': height, 'scale': self.site.scale}})
        return base64.b64decode(shot['data'])

    async def frame(self, frame: int) -> bytes:
        for attempt in range(5):
            try:
                if self.browser is None:
                    await self.open()
                return await asyncio.wait_for(self.grab(frame), 120)
            except Exception as error:
                print(f'[{self.label}] frame {frame} failed ({type(error).__name__}: {error}); reopening, attempt {attempt + 1}',
                      file=sys.stderr, flush=True)
                await self.close()
        raise RuntimeError(f'frame {frame} failed repeatedly')


def encoder_args(fps: float, scale: float, crf: int | None) -> list[str]:
    preset = 'medium' if scale > 1 else 'slow'
    quality = crf if crf is not None else (15 if scale > 1 else 16)
    args = ['-c:v', 'libx264', '-preset', preset, '-crf', str(quality), '-pix_fmt', 'yuv420p', '-profile:v', 'high',
            '-r', f'{fps:g}', '-g', str(round(fps * 2)), '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-colorspace', 'bt709', '-movflags', '+faststart']
    if scale > 1:
        args += ['-level:v', '5.1']
    return args


async def page_info(site: Site) -> tuple[float, float]:
    async with async_playwright() as playwright:
        page = Page(playwright, site)
        await page.open()
        info = page.fps, page.duration
        await page.close()
        return info


async def snap(site: Site, times: list[float], out: Path, sheet: bool) -> None:
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        page = Page(playwright, site)
        await page.open()
        paths = []
        for seconds in times:
            path = out / f't{seconds:08.3f}.png'
            path.write_bytes(await page.frame(round(seconds * page.fps)))
            paths.append(path)
        await page.close()
    for path in paths:
        print(path)
    if sheet and len(paths) > 1:
        print(contact_sheet(paths, out / f'sheet-{times[0]:g}-{times[-1]:g}.jpg'))


def contact_sheet(paths: list[Path], target: Path, columns: int = 4, width: int = 480) -> Path:
    from PIL import Image, ImageDraw
    images = [Image.open(path).convert('RGB') for path in paths]
    height = round(width * images[0].height / images[0].width)
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new('RGB', (columns * width, rows * (height + 24)), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    for index, (path, image) in enumerate(zip(paths, images)):
        x, y = (index % columns) * width, (index // columns) * (height + 24)
        sheet.paste(image.resize((width, height)), (x, y + 24))
        draw.text((x + 6, y + 5), path.stem, fill=(255, 140, 90))
    sheet.save(target, quality=90)
    return target


async def worker(index: int, site: Site, queue: asyncio.Queue, progress: dict, args) -> None:
    async with async_playwright() as playwright:
        page = Page(playwright, site, f'worker {index}')
        while True:
            try:
                first, last, target = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            partial = target.with_suffix('.part.mp4')
            fps = progress['fps']
            encoder = subprocess.Popen([tool('ffmpeg'), '-y', '-v', 'error', '-f', 'image2pipe', '-c:v', 'png',
                                        '-framerate', f'{fps:g}', '-i', '-', *encoder_args(fps, site.scale, args.crf),
                                        str(partial)], stdin=subprocess.PIPE)
            for frame in range(first, last):
                encoder.stdin.write(await page.frame(frame))
            encoder.stdin.close()
            if encoder.wait() != 0:
                raise RuntimeError(f'ffmpeg failed on {partial}')
            partial.replace(target)
            progress['done'] += last - first
            elapsed = time.time() - progress['started']
            print(f'worker {index}: {target.name} ({progress["done"]}/{progress["total"]} frames, '
                  f'{progress["done"] / max(elapsed, 1e-6):.1f} fps)', flush=True)
        await page.close()


async def full(site: Site, args) -> None:
    fps, duration = await page_info(site)
    start = args.start
    end = duration if args.end is None else args.end
    output = Path(args.output).resolve()
    work = Path(args.work).resolve() if args.work else output.parent / f'.{output.stem}-chunks'
    chunk_dir = work / f'{start:g}-{end:g}-{site.fingerprint()}'
    if args.fresh and work.exists():
        shutil.rmtree(work)
    chunk_dir.mkdir(parents=True, exist_ok=True)
    first, last = round(start * fps), round(end * fps)
    step = max(1, round(args.chunk * fps))
    chunks = [(a, min(last, a + step), chunk_dir / f'c{(a - first) // step:04d}.mp4') for a in range(first, last, step)]
    todo = [chunk for chunk in chunks if not chunk[2].exists()]
    queue: asyncio.Queue = asyncio.Queue()
    for chunk in todo:
        queue.put_nowait(chunk)
    progress = {'done': 0, 'total': sum(b - a for a, b, _ in todo), 'started': time.time(), 'fps': fps}
    print(f'{len(chunks)} chunks, {len(todo)} to render ({progress["total"]} frames at {fps:g} fps, '
          f'{site.size[0] * site.scale:g}x{site.size[1] * site.scale:g})', flush=True)
    await asyncio.gather(*(worker(i, site, queue, progress, args) for i in range(min(args.workers, max(1, len(todo))))))
    listing = chunk_dir / 'list.txt'
    listing.write_text(''.join(f"file '{chunk[2].name}'\n" for chunk in chunks), encoding='utf-8')
    subprocess.run([tool('ffmpeg'), '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(listing),
                    '-c', 'copy', '-movflags', '+faststart', str(output)], check=True)
    print(f'{last - first} frames in {time.time() - progress["started"]:.0f} s -> {output}')


async def evaluate(site: Site, expression: str) -> None:
    async with async_playwright() as playwright:
        page = Page(playwright, site)
        await page.open()
        result = await page.page.evaluate(f'async () => {{ return {expression}; }}')
        await page.close()
    print(json.dumps(result, ensure_ascii=False, indent=1))


def pixels(data: bytes):
    import io
    import numpy as np
    from PIL import Image
    return np.asarray(Image.open(io.BytesIO(data)).convert('RGB'), dtype=np.int16)


async def check(site: Site, times: list[float], limit: float) -> bool:
    # The same frame rendered by jumping to it and by stepping through the second before it must match.
    import numpy as np
    async with async_playwright() as playwright:
        page = Page(playwright, site)
        await page.open()
        jumped = {}
        for seconds in reversed(times):
            jumped[seconds] = pixels(await page.frame(round(seconds * page.fps)))
        rows = []
        for seconds in times:
            target = round(seconds * page.fps)
            for frame in range(max(0, target - round(page.fps)), target):
                await page.page.evaluate('f => window.renderFrame(f)', frame)
            delta = np.abs(pixels(await page.frame(target)) - jumped[seconds])
            rows.append({'t': seconds, 'mean_pixel_error': round(float(delta.mean()), 4),
                         'changed_fraction': round(float(np.any(delta > 3, axis=2).mean()), 5)})
        await page.close()
    print(json.dumps(rows, indent=1))
    return all(row['mean_pixel_error'] <= limit for row in rows)


async def subtitles(site: Site, output: Path, selector: str, safe: float) -> bool:
    import datetime
    import srt
    async with async_playwright() as playwright:
        page = Page(playwright, site)
        await page.open()
        lines = await page.page.evaluate('window.getSubtitles ? window.getSubtitles() : []')
        problems = []
        for index, (start, end, text) in enumerate(lines):
            await page.page.evaluate('f => window.renderFrame(f)', round((start + end) / 2 * page.fps))
            box = await page.page.evaluate('''selector => {
                const element = document.querySelector(selector);
                if (!element) return null;
                const r = element.getBoundingClientRect();
                return {text: element.textContent, x0: r.left, y0: r.top, x1: r.right, y1: r.bottom,
                        overflow: element.scrollWidth > element.clientWidth + 1};
            }''', selector)
            width, height = site.size
            if box is None or box['text'].strip() != text.strip():
                problems.append({'cue': index + 1, 'problem': 'text not shown', 'shown': box and box['text']})
            elif box['overflow'] or box['x0'] < width * safe or box['x1'] > width * (1 - safe) or box['y1'] > height * (1 - safe / 2):
                problems.append({'cue': index + 1, 'problem': 'outside the safe area or overflowing', 'box': box})
        await page.close()
    if lines:
        output.write_text(srt.compose([srt.Subtitle(i + 1, datetime.timedelta(seconds=a), datetime.timedelta(seconds=b), t)
                                       for i, (a, b, t) in enumerate(lines)]), encoding='utf-8')
    print(json.dumps({'subtitles': len(lines), 'srt': str(output) if lines else None, 'problems': problems},
                     ensure_ascii=False, indent=1))
    return not problems


def mux(video: str, audio: str, output: str) -> None:
    subprocess.run([tool('ffmpeg'), '-y', '-v', 'error', '-i', video, '-i', audio, '-map', '0:v:0', '-map', '1:a:0',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest',
                    '-movflags', '+faststart', output], check=True)
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    sub = parser.add_subparsers(dest='command', required=True)

    def page_options(command: argparse.ArgumentParser) -> None:
        command.add_argument('page', type=Path, help='compositor HTML page')
        command.add_argument('--root', type=Path, help='directory served over HTTP (default: the page directory)')
        command.add_argument('--size', default='1920x1080', help='CSS viewport size, e.g. 1920x1080')
        command.add_argument('--scale', type=float, default=1.0, help='device pixel ratio; 2 renders 3840x2160')

    snap_parser = sub.add_parser('snap', help='capture single frames and a contact sheet')
    page_options(snap_parser)
    snap_parser.add_argument('times', nargs='*', type=float)
    snap_parser.add_argument('--every', type=float, help='capture every N seconds between --from and --to')
    snap_parser.add_argument('--from', dest='start', type=float, default=0.0)
    snap_parser.add_argument('--to', dest='end', type=float)
    snap_parser.add_argument('--out', type=Path, default=Path('snaps'))
    snap_parser.add_argument('--no-sheet', action='store_true')

    full_parser = sub.add_parser('full', help='render frames in resumable parallel chunks')
    page_options(full_parser)
    full_parser.add_argument('output')
    full_parser.add_argument('--from', dest='start', type=float, default=0.0)
    full_parser.add_argument('--to', dest='end', type=float)
    full_parser.add_argument('--workers', type=int, default=4)
    full_parser.add_argument('--chunk', type=float, default=10.0, help='seconds per chunk')
    full_parser.add_argument('--crf', type=int)
    full_parser.add_argument('--work', help='chunk directory (default: .<output>-chunks beside the output)')
    full_parser.add_argument('--fresh', action='store_true', help='discard finished chunks first')

    eval_parser = sub.add_parser('eval', help='evaluate a JavaScript expression on the page, e.g. QA reports')
    page_options(eval_parser)
    eval_parser.add_argument('expression')

    check_parser = sub.add_parser('check', help='compare jumped and stepped renders of the same frames')
    page_options(check_parser)
    check_parser.add_argument('times', nargs='+', type=float)
    check_parser.add_argument('--limit', type=float, default=.5, help='largest acceptable mean pixel error')

    subtitle_parser = sub.add_parser('subtitles', help='export window.getSubtitles() as SRT and check placement')
    page_options(subtitle_parser)
    subtitle_parser.add_argument('output', type=Path)
    subtitle_parser.add_argument('--selector', default='#subtitles span')
    subtitle_parser.add_argument('--safe', type=float, default=.05, help='side safe area as a fraction of the width')

    mux_parser = sub.add_parser('mux', help='add the final mix to the silent render')
    mux_parser.add_argument('video')
    mux_parser.add_argument('audio')
    mux_parser.add_argument('output')

    args = parser.parse_args()
    if args.command == 'mux':
        mux(args.video, args.audio, args.output)
        return
    width, height = (int(value) for value in args.size.lower().split('x'))
    site = Site(args.page, args.root, (width, height), args.scale)
    if args.command == 'snap':
        times = list(args.times)
        if args.every:
            end = args.end if args.end is not None else asyncio.run(page_info(site))[1]
            value = args.start
            while value <= end + 1e-9:
                times.append(round(value, 3))
                value += args.every
        if not times:
            parser.error('give times or --every')
        asyncio.run(snap(site, times, args.out, not args.no_sheet))
    elif args.command == 'full':
        asyncio.run(full(site, args))
    elif args.command == 'check':
        sys.exit(0 if asyncio.run(check(site, args.times, args.limit)) else 1)
    elif args.command == 'subtitles':
        sys.exit(0 if asyncio.run(subtitles(site, args.output, args.selector, args.safe)) else 1)
    else:
        asyncio.run(evaluate(site, args.expression))


if __name__ == '__main__':
    main()
