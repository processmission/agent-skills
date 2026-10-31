# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from pedalboard import Compressor, HighpassFilter, HighShelfFilter, LowShelfFilter, Pedalboard, PeakFilter
import pyloudnorm
from scipy.signal import resample_poly
import soundfile

DESCRIPTION = ('Mix and master the soundtrack: section level rides, optional narration with music ducking, optional '
               'effects stem, glue EQ (shelves from the plan style) and compression, then loudness normalisation with '
               'an FFmpeg lookahead limiter holding a true-peak ceiling.')
STYLES = Path(__file__).resolve().parents[1] / 'assets/music/styles'


def load(path: Path, rate: int, length: int | None) -> np.ndarray:
    audio, source_rate = soundfile.read(path, dtype='float64', always_2d=True)
    if source_rate != rate:
        raise SystemExit(f'{path} is {source_rate} Hz; resample it to {rate} Hz first')
    if audio.shape[1] == 1:
        audio = np.repeat(audio, 2, axis=1)
    if length is None:
        return audio
    out = np.zeros((length, 2))
    out[:min(length, len(audio))] = audio[:length]
    return out


def true_peak_db(audio: np.ndarray) -> float:
    return float(20 * np.log10(np.max(np.abs(resample_poly(audio, 4, 1, axis=0))) + 1e-12))


def loudness(meter: pyloudnorm.Meter, audio: np.ndarray) -> float:
    return float(meter.integrated_loudness(audio))


def rides(plan: dict | None, length: int, rate: int) -> np.ndarray:
    if not plan:
        return np.ones(length)
    points = [(section['start'], section.get('level', 0.0)) for section in plan['sections']]
    last = plan['sections'][-1]
    points.append((last['end'], last.get('level', 0.0)))
    times, gains = zip(*sorted(points))
    return 10 ** (np.interp(np.arange(length) / rate, times, gains) / 20)


def duck_envelope(voice: np.ndarray, rate: int, depth_db: float, attack: float = .06, release: float = .45) -> np.ndarray:
    hop = int(.01 * rate)
    frames = len(voice) // hop
    rms = np.sqrt(np.mean(voice[:frames * hop].reshape(frames, hop) ** 2, axis=1) + 1e-12)
    active = (20 * np.log10(rms) > -45).astype(float)
    env = np.zeros(frames)
    up, down = np.exp(-.01 / attack), np.exp(-.01 / release)
    for k in range(frames):
        previous = env[k - 1] if k else 0.0
        coefficient = up if active[k] > previous else down
        env[k] = coefficient * previous + (1 - coefficient) * active[k]
    gain = np.repeat(10 ** (depth_db * env / 20), hop)
    return np.concatenate([gain, np.full(len(voice) - len(gain), gain[-1] if len(gain) else 1.0)])


def style_master(plan: dict | None, folders: list[Path]) -> dict:
    if not plan or not plan.get('style'):
        return dict(plan.get('master', {})) if plan else {}
    for folder in folders:
        path = Path(plan['style']) if plan['style'].endswith('.json') else folder / f'{plan["style"]}.json'
        if path.exists():
            return {**json.loads(path.read_text(encoding='utf-8')).get('master', {}), **plan.get('master', {})}
    raise SystemExit(f'style {plan["style"]!r} not found')


def lookahead_limit(audio: np.ndarray, rate: int, limit_db: float, folder: Path) -> np.ndarray:
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        raise SystemExit('ffmpeg is required for the lookahead limiter')
    with tempfile.TemporaryDirectory(dir=folder) as work:
        source, target = Path(work) / 'in.wav', Path(work) / 'out.wav'
        soundfile.write(source, audio.astype(np.float32), rate, subtype='FLOAT')
        subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(source), '-af',
                        f'alimiter=limit={10 ** (limit_db / 20):.6f}:attack=5:release=80:level=false:latency=true',
                        '-c:a', 'pcm_f32le', str(target)], check=True)
        return load(target, rate, len(audio))


def limit(mix: np.ndarray, rate: int, meter: pyloudnorm.Meter, target: float, ceiling: float,
          folder: Path) -> tuple[np.ndarray, float]:
    # Raise the gain to the loudness target and let a lookahead limiter hold the peaks; lower the limit until the
    # oversampled true peak sits under the ceiling, and add back the loudness the limiter took.
    gain, limit_db = target - loudness(meter, mix), ceiling - .3
    for _ in range(16):
        staged = mix * 10 ** (gain / 20)
        limited = lookahead_limit(staged, rate, limit_db, folder)
        level, peak = loudness(meter, limited), true_peak_db(limited)
        if peak <= ceiling and abs(level - target) <= .1:
            return limited, round(max(0.0, true_peak_db(staged) - peak), 1)
        if peak > ceiling:
            limit_db -= peak - ceiling + .05
        gain += target - level
    raise SystemExit('the limiter could not reach both the loudness target and the true-peak ceiling; lower --target')


def master(args) -> dict:
    plan = json.loads(args.plan.read_text(encoding='utf-8')) if args.plan else None
    folders = args.styles + ([args.plan.parent / 'styles'] if args.plan else []) + [STYLES]
    settings = style_master(plan, folders)
    low_shelf = args.low_shelf if args.low_shelf is not None else settings.get('low_shelf', -2.0)
    high_shelf = args.high_shelf if args.high_shelf is not None else settings.get('high_shelf', 1.2)
    info = soundfile.info(args.music)
    rate = info.samplerate
    duration = args.duration or (plan['duration'] if plan else info.duration)
    length = int(round(duration * rate))
    meter = pyloudnorm.Meter(rate)
    music = load(args.music, rate, length) * rides(plan, length, rate)[:, None]
    music *= 10 ** ((-20 - loudness(meter, music)) / 20)
    glue = Pedalboard([HighpassFilter(30), LowShelfFilter(cutoff_frequency_hz=110, gain_db=low_shelf),
                       PeakFilter(cutoff_frequency_hz=380, gain_db=-1.5, q=.9),
                       HighShelfFilter(cutoff_frequency_hz=7000, gain_db=high_shelf),
                       Compressor(threshold_db=-24, ratio=2.2, attack_ms=25, release_ms=220)])
    music = glue(music.T.astype(np.float32), rate).T.astype(np.float64)
    mix = music
    report = {'low_shelf_db': low_shelf, 'high_shelf_db': high_shelf}
    if args.voice:
        voice = load(args.voice, rate, length).mean(axis=1)
        chain = Pedalboard([HighpassFilter(75), PeakFilter(cutoff_frequency_hz=3200, gain_db=2.0, q=.8),
                            Compressor(threshold_db=-22, ratio=3, attack_ms=5, release_ms=80)])
        voice = chain(voice.astype(np.float32)[None, :], rate)[0].astype(np.float64)
        voice *= 10 ** ((-16.0 - loudness(meter, voice)) / 20)
        music *= 10 ** ((-16.5 - loudness(meter, music)) / 20)
        mix = np.stack([voice, voice], axis=1) + music * duck_envelope(voice, rate, args.duck)[:, None]
        report['ducking_db'] = args.duck
    if args.sfx:
        sfx = load(args.sfx, rate, length)
        sfx *= 10 ** ((args.sfx_lufs - loudness(meter, sfx)) / 20)
        mix = mix + sfx
    fade_in, fade_out = int(.01 * rate), int(args.fade_out * rate)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    if fade_out:
        mix[-fade_out:] *= (np.cos(np.linspace(0, np.pi, fade_out)) * .5 + .5)[:, None]
    limited, depth = limit(mix, rate, meter, args.target, args.ceiling, args.output.parent)
    soundfile.write(args.output, limited, rate, subtype='PCM_24')
    report.update({'output': str(args.output), 'lufs': round(loudness(meter, limited), 2),
                   'true_peak_db': round(true_peak_db(limited), 2), 'limiter_depth_db': depth,
                   'duration_s': length / rate, 'rate': rate})
    if plan:
        report['section_lufs'] = {section.get('name', f'{section["start"]:g}s'): round(loudness(
            meter, limited[int(section['start'] * rate):int(section['end'] * rate)]), 1)
            for section in plan['sections'] if section['end'] - section['start'] >= .5}
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('music', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--plan', type=Path, help='music plan; section "level" values (dB) become fader rides')
    parser.add_argument('--voice', type=Path, help='full-length narration track')
    parser.add_argument('--sfx', type=Path, help='full-length effects stem')
    parser.add_argument('--sfx-lufs', type=float, default=-24.0)
    parser.add_argument('--duck', type=float, default=-10.5, help='music gain under narration, dB')
    parser.add_argument('--target', type=float, default=-15.0, help='integrated loudness, LUFS')
    parser.add_argument('--ceiling', type=float, default=-1.5, help='true peak, dBTP')
    parser.add_argument('--duration', type=float)
    parser.add_argument('--fade-out', type=float, default=1.6)
    parser.add_argument('--low-shelf', type=float, help='dB at 110 Hz; default from the plan style "master", else -2')
    parser.add_argument('--high-shelf', type=float, help='dB at 7 kHz; default from the plan style "master", else 1.2')
    parser.add_argument('--styles', type=Path, action='append', default=[], help='extra folder of style JSON files')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = master(args)
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.report:
        args.report.write_text(text + '\n', encoding='utf-8')
    sys.stdout.write(text + '\n')


if __name__ == '__main__':
    main()
