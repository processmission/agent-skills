# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

DESCRIPTION = ('Scan a rendered video for one-frame flashes and long near-black gaps. Designed hits listed in a cue '
               'file (impact, flash and transition cues) are reported separately so intentional flashes do not hide '
               'real glitches.')
WIDTH, HEIGHT = 160, 90


def probe(path: Path) -> float:
    out = subprocess.run([shutil.which('ffprobe'), '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=avg_frame_rate', '-of', 'json', str(path)], check=True, capture_output=True, text=True).stdout
    numerator, denominator = json.loads(out)['streams'][0]['avg_frame_rate'].split('/')
    return float(numerator) / float(denominator)


def frames(path: Path) -> np.ndarray:
    raw = subprocess.run([shutil.which('ffmpeg'), '-v', 'error', '-i', str(path), '-vf',
                          f'scale={WIDTH}:{HEIGHT},format=gray', '-f', 'rawvideo', '-'], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, HEIGHT, WIDTH).astype(np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('video', type=Path)
    parser.add_argument('--cues', type=Path,
                        help='cue JSON (list or {"cues": [...]}) whose impact, flash and transition cues are designed hits')
    parser.add_argument('--flash', type=float, default=30.0,
                        help='block score that counts as a one-frame flash (ticking digits score 16-18, a terminal '
                             'scroll about 24, a flash 200+)')
    parser.add_argument('--black', type=float, default=1.2, help='mean luma below which a frame counts as black')
    parser.add_argument('--black-seconds', type=float, default=1.0, help='shortest black gap to report')
    args = parser.parse_args()
    if shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None:
        sys.exit('ffmpeg and ffprobe are required')
    fps = probe(args.video)
    video = frames(args.video)
    designed = []
    if args.cues:
        data = json.loads(args.cues.read_text(encoding='utf-8'))
        for cue in data['cues'] if isinstance(data, dict) else data:
            if cue['type'] not in ('impact', 'flash', 'transition'):
                continue
            # Transition cues carry their own span; point cues get a fixed window around the hit.
            if 'from' in cue and 'to' in cue:
                designed.append((cue['from'] - .1, cue['to'] + .1))
            else:
                designed.append((cue['t'] - .6, cue['t'] + .6))
    near_hit = lambda seconds: any(start <= seconds <= end for start, end in designed)
    flashes, designed_hits = [], []
    block = lambda image: image.reshape(HEIGHT // 10, 10, WIDTH // 10, 10).mean(axis=(1, 3))
    for k in range(1, len(video) - 1):
        # A flash departs from both neighbours in the same direction while the neighbours match each other;
        # motion fails the second test because the frames before and after differ as well.
        middle = video[k] - .5 * (video[k - 1] + video[k + 1])
        same = np.sign(video[k] - video[k - 1]) == np.sign(video[k] - video[k + 1])
        departure = block(np.abs(middle) * same)
        neighbours = block(np.abs(video[k + 1] - video[k - 1]))
        candidates = departure[neighbours < .35 * departure]
        score = float(candidates.max()) if candidates.size else 0.0
        if score > args.flash:
            (designed_hits if near_hit(k / fps) else flashes).append({'t': round(k / fps, 3), 'score': round(score, 1)})
    luma = video.mean(axis=(1, 2))
    middle = luma[1:-1] - .5 * (luma[:-2] + luma[2:])
    same = np.sign(luma[1:-1] - luma[:-2]) == np.sign(luma[1:-1] - luma[2:])
    jumps = [round((k + 1) / fps, 3) for k in np.nonzero(same & (np.abs(middle) > 1.5))[0] if not near_hit((k + 1) / fps)]
    gaps, start = [], None
    for k, value in enumerate(luma):
        if value < args.black and start is None:
            start = k
        if start is not None and (value >= args.black or k == len(luma) - 1):
            if (k - start) / fps >= args.black_seconds:
                gaps.append([round(start / fps, 2), round(k / fps, 2)])
            start = None
    report = {'frames': len(video), 'fps': fps, 'mean_luma': round(float(luma.mean()), 1),
              'one_frame_flashes': flashes, 'brightness_jumps': jumps, 'designed_hits': designed_hits, 'black_gaps': gaps}
    print(json.dumps(report, indent=1))
    sys.exit(1 if flashes or jumps or gaps else 0)


if __name__ == '__main__':
    main()
