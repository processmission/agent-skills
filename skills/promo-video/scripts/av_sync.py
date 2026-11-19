# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

import numpy as np

DESCRIPTION = ('Measure the offset between the largest brightness jump and the loudest audio onset inside a time '
               'window of a finished video. Pick a window that contains one designed hit.')
RATE = 48000


def main() -> None:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('video')
    parser.add_argument('start', type=float)
    parser.add_argument('end', type=float)
    parser.add_argument('--fps', type=float, default=30.0)
    args = parser.parse_args()
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        sys.exit('ffmpeg is required')
    window = ['-ss', str(args.start), '-to', str(args.end), '-i', args.video]
    raw = subprocess.run([ffmpeg, '-v', 'error', *window, '-vf', 'scale=96:54,format=gray', '-f', 'rawvideo', '-'],
                         check=True, capture_output=True).stdout
    luma = np.frombuffer(raw, np.uint8).reshape(-1, 54 * 96).mean(axis=1)
    pcm = subprocess.run([ffmpeg, '-v', 'error', *window, '-ac', '1', '-ar', str(RATE), '-f', 'f32le', '-'],
                         check=True, capture_output=True).stdout
    audio = np.frombuffer(pcm, np.float32)
    hop = int(RATE / args.fps)
    rms = np.sqrt(np.array([np.mean(audio[i * hop:(i + 1) * hop] ** 2) for i in range(len(audio) // hop)]) + 1e-12)
    picture = int(np.argmax(np.abs(np.diff(luma)))) + 1
    sound = int(np.argmax(np.diff(20 * np.log10(rms)))) + 1
    print(f'picture jump at {args.start + picture / args.fps:.3f} s, audio onset at {args.start + sound / args.fps:.3f} s, '
          f'offset {(sound - picture) / args.fps * 1000:+.0f} ms')


if __name__ == '__main__':
    main()
