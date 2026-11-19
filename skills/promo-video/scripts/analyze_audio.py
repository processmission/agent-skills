# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

import librosa
from music21 import key as tonality
import numpy as np
import pyloudnorm
from scipy.signal import welch
import soundfile

DESCRIPTION = ('Report loudness and the share of energy per frequency band for each section of a mix, and draw a '
               'spectrogram and waveform with FFmpeg. --profile adds tempo, onset density, brightness, loudness range '
               'and pitch-class balance, for describing a reference track or checking a render against one '
               '(--compare). Typical electronic mixes sit near: sub -8, bass -3, low-mid -7, mid -12, presence -18, '
               'air -24 dB of total power.')
BANDS = [(20, 60, 'sub'), (60, 250, 'bass'), (250, 1000, 'low-mid'), (1000, 4000, 'mid'),
         (4000, 10000, 'presence'), (10000, 20000, 'air')]
PITCHES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
PROFILE = ['tempo_bpm', 'onsets_per_s', 'centroid_hz', 'loudness_range_lu', 'lufs']


def bands(audio: np.ndarray, rate: int) -> dict:
    frequencies, power = welch(audio.mean(axis=1), rate, nperseg=8192)
    total = np.trapezoid(power, frequencies)
    result = {}
    for low, high, name in BANDS:
        mask = (frequencies >= low) & (frequencies < high)
        result[name] = round(float(10 * np.log10(np.trapezoid(power[mask], frequencies[mask]) / total + 1e-12)), 1)
    return result


def segments(plan: dict | None, duration: float, every: float | None) -> list[tuple[str, float, float]]:
    if plan:
        return [(s.get('name', f'{s["start"]:g}s'), s['start'], s['end']) for s in plan['sections']]
    step = every or duration
    starts = np.arange(0, duration, step)
    return [(f'{start:g}s', float(start), float(min(duration, start + step))) for start in starts]


def loudness_range(meter: pyloudnorm.Meter, audio: np.ndarray, rate: int) -> float:
    # Short-term loudness over 3 s windows every second, relative-gated like EBU R128 LRA.
    window, hop = 3 * rate, rate
    values = [meter.integrated_loudness(audio[start:start + window])
              for start in range(0, max(1, len(audio) - window + 1), hop)]
    values = np.array([v for v in values if np.isfinite(v) and v > -70])
    if values.size < 2:
        return 0.0
    gated = values[values > 10 * np.log10(np.mean(10 ** (values / 10))) - 20]
    return round(float(np.percentile(gated, 95) - np.percentile(gated, 10)), 1)


def profile(path: Path, audio: np.ndarray, rate: int, meter: pyloudnorm.Meter, plan: dict | None) -> dict:
    mono, sr = librosa.load(path, sr=22050, mono=True)
    tempo, _ = librosa.beat.beat_track(y=mono, sr=sr)
    onsets = librosa.onset.onset_detect(y=mono, sr=sr, units='time')
    # Pitch classes come from the harmonic part only, so drums and noise do not flatten the balance.
    chroma = librosa.feature.chroma_cqt(y=librosa.effects.harmonic(mono), sr=sr).sum(axis=1)
    share = chroma / chroma.sum()
    result = {'tempo_bpm': round(float(np.atleast_1d(tempo)[0]), 1),
              'onsets_per_s': round(len(onsets) / (len(mono) / sr), 2),
              'centroid_hz': round(float(np.median(librosa.feature.spectral_centroid(y=mono, sr=sr)[0])), 0),
              'loudness_range_lu': loudness_range(meter, audio, rate),
              'lufs': round(float(meter.integrated_loudness(audio)), 1),
              'pitch_classes': {PITCHES[i]: round(float(share[i]), 3) for i in np.argsort(share)[::-1][:7]}}
    if plan and plan.get('key'):
        scale = {p.pitchClass for p in tonality.Key(plan['key'], plan.get('mode', 'major')).getScale().getPitches()}
        result['in_key_share'] = round(float(sum(share[pc] for pc in scale)), 3)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('audio', type=Path)
    parser.add_argument('--plan', type=Path, help='music plan whose sections define the segments and whose key is checked')
    parser.add_argument('--every', type=float, help='segment length in seconds when no plan is given')
    parser.add_argument('--profile', action='store_true', help='add tempo, onsets, brightness, loudness range, pitch classes')
    parser.add_argument('--compare', type=Path, help='JSON report of a reference track made with --profile --json')
    parser.add_argument('--spectrum', type=Path, help='write a spectrogram PNG')
    parser.add_argument('--wave', type=Path, help='write a waveform PNG')
    parser.add_argument('--json', type=Path, help='write the report as JSON')
    args = parser.parse_args()
    audio, rate = soundfile.read(args.audio, dtype='float64', always_2d=True)
    meter = pyloudnorm.Meter(rate)
    plan = json.loads(args.plan.read_text(encoding='utf-8')) if args.plan else None
    report = {'whole': {'lufs': round(float(meter.integrated_loudness(audio)), 1), **bands(audio, rate)}}
    for name, start, end in segments(plan, len(audio) / rate, args.every):
        chunk = audio[int(start * rate):int(end * rate)]
        if len(chunk) < rate // 2:
            continue
        report[name] = {'lufs': round(float(meter.integrated_loudness(chunk)), 1), **bands(chunk, rate)}
    header = f'{"segment":12}{"LUFS":>8}' + ''.join(f'{band:>10}' for _, _, band in BANDS)
    print(header)
    for name, values in report.items():
        print(f'{name[:12]:12}{values["lufs"]:>8}' + ''.join(f'{values[band]:>10}' for _, _, band in BANDS))
    if args.profile or args.compare:
        report['profile'] = profile(args.audio, audio, rate, meter, plan)
        print(json.dumps(report['profile'], ensure_ascii=False))
    if args.compare:
        reference = json.loads(args.compare.read_text(encoding='utf-8'))
        print(f'\n{"measure":20}{"this":>12}{"reference":>12}')
        for name in PROFILE:
            print(f'{name:20}{report["profile"][name]:>12}{reference["profile"][name]:>12}')
        for _, _, name in BANDS:
            print(f'{name:20}{report["whole"][name]:>12}{reference["whole"][name]:>12}')
    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    ffmpeg = shutil.which('ffmpeg')
    if (args.spectrum or args.wave) and ffmpeg is None:
        sys.exit('ffmpeg is required for --spectrum and --wave')
    if args.spectrum:
        subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(args.audio), '-lavfi',
                        'showspectrumpic=s=1800x500:mode=combined:scale=log:fscale=log:legend=1', str(args.spectrum)], check=True)
    if args.wave:
        subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(args.audio), '-lavfi',
                        'showwavespic=s=1800x300:colors=#ec4a22', str(args.wave)], check=True)


if __name__ == '__main__':
    main()
