# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

DESCRIPTION = ('Fit scene starts to a musical grid. Major starts (title, section changes, big hits) snap to bar lines, '
               'the rest to beats. Prints the best tempos in a range, or the snapped timeline for one tempo.')


def load_starts(args) -> tuple[list[float], list[str]]:
    if args.timeline:
        data = json.loads(args.timeline.read_text(encoding='utf-8'))
        scenes = data['scenes']
        return [float(s['start']) for s in scenes], [s.get('id', str(i)) for i, s in enumerate(scenes)]
    starts = [float(value) for value in args.starts.split(',')]
    return starts, [str(i) for i in range(len(starts))]


def snap(starts: list[float], names: list[str], major: set[str], bpm: float, unit_beats: int) -> list[float]:
    beat = 60 / bpm
    result = []
    for start, name in zip(starts, names):
        grid = beat * (4 if name in major else unit_beats)
        result.append(round(round(start / grid) * grid, 4))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--timeline', type=Path, help='timeline JSON with scenes[].start (and scenes[].id)')
    source.add_argument('--starts', help='comma-separated scene starts in seconds')
    parser.add_argument('--major', default='', help='comma-separated scene ids or indices that must sit on bar lines')
    parser.add_argument('--bpm', type=float, help='report the snapped timeline for this tempo')
    parser.add_argument('--range', nargs=2, type=float, default=(90, 136), metavar=('LOW', 'HIGH'))
    parser.add_argument('--minor-beats', type=int, default=2, help='grid for other starts, in beats (default: half bar)')
    args = parser.parse_args()
    starts, names = load_starts(args)
    major = {item.strip() for item in args.major.split(',') if item.strip()} or set(names)
    if args.bpm:
        snapped = snap(starts, names, major, args.bpm, args.minor_beats)
        shifts = [b - a for a, b in zip(starts, snapped)]
        for name, a, b, shift in zip(names, starts, snapped, shifts):
            print(f'{name:>12}  {a:9.3f} -> {b:9.3f}  ({shift:+.3f} s){"  bar" if name in major else ""}')
        print(json.dumps({'bpm': args.bpm, 'bar_s': 240 / args.bpm, 'starts': dict(zip(names, snapped)),
                          'max_shift_s': round(max(abs(s) for s in shifts), 3)}, ensure_ascii=False))
        return
    rows = []
    tenth = int(args.range[0] * 10)
    while tenth <= int(args.range[1] * 10):
        bpm = tenth / 10
        snapped = snap(starts, names, major, bpm, args.minor_beats)
        shifts = [abs(b - a) for a, b in zip(starts, snapped)]
        rows.append((max(shifts), sum(shifts), bpm))
        tenth += 1
    rows.sort()
    print(f'{"bpm":>7} {"max shift":>10} {"total":>8}')
    for worst, total, bpm in rows[:10]:
        print(f'{bpm:7.1f} {worst:10.3f} {total:8.2f}')
    print('Moving scene starts onto the grid of a round tempo (120 BPM: 2 s bars) is usually cleaner than an odd tempo; '
          'rerun with --bpm to get the snapped starts.', file=sys.stderr)


if __name__ == '__main__':
    main()
