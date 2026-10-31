# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys

from music21 import key as tonality, roman
import numpy as np
from pedalboard import (Bitcrush, Chorus, Distortion, Gain, HighpassFilter, LowpassFilter, Pedalboard, Reverb)
import pretty_midi
from pychord import Chord
import pyloudnorm
import soundfile

DESCRIPTION = ('Compose and render a soundtrack from a music plan and a style: harmony from roman numerals or chord '
               'symbols, track patterns chosen by section energy, Csound synths and SoundFont instruments, stems and a '
               'mixed float WAV. --preview renders short demos of the styles, --list prints them. '
               'See references/music.md.')
SKILL = Path(__file__).resolve().parents[1]
ORCHESTRA = SKILL / 'assets/music/promo.orc'
STYLES = SKILL / 'assets/music/styles'
RATE = 48000
SOUNDFONTS = [Path.home() / '.local/share/soundfonts/MuseScore_General.sf3',
              Path('/usr/share/sounds/sf3/MuseScore_General_Full.sf3'),
              Path('/usr/share/sounds/sf2/FluidR3_GM.sf2')]
MELODIC = {'bass': 10, 'pluck': 11, 'pad': 12, 'drone': 14, 'epiano': 40, 'supersaw': 41, 'sawbass': 42,
           'bass808': 43, 'lead': 44, 'mallet': 45, 'stab': 46, 'string': 47}
DRUMS = {'kick': 4, 'hat': 20, 'clap': 21, 'tick': 22, 'snare': 50, 'rim': 51, 'shaker': 52, 'softkick': 53,
         'tom': 54, 'crash': 55, 'gated': 57}
DRUM_LENGTH = {'kick': .5, 'hat': .5, 'clap': .5, 'tick': .06, 'snare': .5, 'rim': .1, 'shaker': .25,
               'softkick': .5, 'tom': .6, 'crash': 3.4, 'gated': .6}
TEXTURES = {'vinyl': 60}
GM_DRUMS = {'kick': 36, 'rim': 37, 'snare': 38, 'clap': 39, 'hat': 42, 'pedal': 44, 'tom': 45, 'open': 46,
            'crash': 49, 'tom-high': 50, 'ride': 51, 'tambourine': 54, 'cowbell': 56, 'shaker': 70}
TRACK = {'engine': 'csound', 'gain': 0.0, 'pan': .5, 'brightness': .5, 'reverb': .2, 'delay': 0.0, 'attack': .01,
         'release': .3, 'duck': 0.0, 'velocity': 1.0, 'register': [48, 72], 'voicing': 'close', 'gate': 1.0}
INTERVALS = {'root': [0], 'third': [4, 3, 5, 2], 'fifth': [7, 6, 8], 'seventh': [10, 11, 9], 'ninth': [2, 1, 3]}
CELLS = {'rest': [], 'half': [(0, 2.0)], 'quarter': [(0, 1.0)], 'eighths': [(0, .5), (.5, .5)],
         'dotted': [(0, .75), (.75, .25)], 'offbeat': [(.5, .5)], 'sixteenths': [(0, .25), (.25, .25), (.5, .25), (.75, .25)],
         'push': [(0, .25), (.25, .5), (.75, .25)]}


def merge(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    for name, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(name), dict):
            result[name] = merge(result[name], value)
        else:
            result[name] = copy.deepcopy(value)
    return result


def find_style(name: str, folders: list[Path]) -> Path:
    candidate = Path(name)
    if candidate.suffix == '.json' and candidate.exists():
        return candidate
    for folder in folders:
        path = folder / f'{name}.json'
        if path.exists():
            return path
    raise SystemExit(f'style {name!r} not found in {", ".join(str(folder) for folder in folders)}')


def load_style(name: str, folders: list[Path]) -> dict:
    return json.loads(find_style(name, folders).read_text(encoding='utf-8'))


def resolve(plan: dict, folders: list[Path]) -> dict:
    style = load_style(plan['style'], folders) if plan.get('style') else {}
    merged = merge(style, plan)
    for name, track in merged.get('tracks', {}).items():
        if 'from' not in track:
            continue
        # "orchestral.strings" borrows a track, and the pattern it names, from another style.
        source, _, source_track = track['from'].partition('.')
        other = load_style(source, folders)
        borrowed = copy.deepcopy(other['tracks'][source_track])
        if isinstance(borrowed.get('pattern'), str) and 'pattern' not in track:
            label = f'{source}.{borrowed["pattern"]}'
            merged.setdefault('patterns', {})[label] = other['patterns'][borrowed['pattern']]
            borrowed['pattern'] = label
        merged['tracks'][name] = merge(borrowed, {k: v for k, v in track.items() if k != 'from'})
    return merged


def pitch_class(name: str) -> int:
    return pretty_midi.note_name_to_number(f'{name}4') % 12


def find_soundfont(path: Path | None) -> Path | None:
    if path:
        return path
    return next((candidate for candidate in SOUNDFONTS if candidate.exists()), None)


class Composer:
    def __init__(self, plan: dict, cues: list[dict] | None = None):
        self.plan = plan
        self.bpm = plan['bpm']
        self.meter = plan.get('meter', 4)
        self.grid = plan.get('grid', 4 * self.meter)
        self.beat = 60 / self.bpm
        self.bar = self.beat * self.meter
        self.step = self.bar / self.grid
        self.duration = plan['duration']
        self.tail = plan.get('tail', 5)
        self.seed = plan.get('seed', 1)
        self.swing = plan.get('swing', .5)
        self.swing_grid = plan.get('swing_grid', self.grid)
        self.humanize = plan.get('humanize', {})
        self.tracks = {name: merge(TRACK, track) for name, track in plan.get('tracks', {}).items()}
        self.patterns = plan.get('patterns', {})
        self.csound: list[tuple[int, float, float, tuple]] = []
        self.midi: dict[str, dict] = {}
        self.kicks: list[float] = []
        self.voicings: dict[str, list[int]] = {}
        self.pitches: dict[str, int] = {}
        self.number = 0
        if cues:
            self.merge_cues(cues)

    # ---------- harmony ----------

    def key_of(self, section: dict):
        return tonality.Key(section.get('key', self.plan.get('key', 'C')), section.get('mode', self.plan.get('mode', 'major')))

    def scale(self, section: dict) -> list[int]:
        return [pitch.pitchClass for pitch in self.key_of(section).getScale().getPitches()[:7]]

    def chord(self, figure: str, section: dict) -> dict:
        try:
            if figure[0] in 'ABCDEFG':
                head, _, bass = figure.partition('/')
                tones = [pitch_class(name) for name in Chord(head).components()]
                root, low = tones[0], pitch_class(bass) if bass else tones[0]
            else:
                numeral = roman.RomanNumeral(figure, self.key_of(section))
                root, low = numeral.root().pitchClass, numeral.bass().pitchClass
                order = [pitch.pitchClass for pitch in sorted(numeral.pitches, key=lambda pitch: pitch.ps)]
                tones = order[order.index(root):] + order[:order.index(root)]
        except Exception as error:
            raise SystemExit(f'section {section.get("name", "?")!r}: cannot read chord {figure!r} ({error})') from error
        return {'figure': figure, 'root': root, 'bass': low, 'tones': list(dict.fromkeys(tones))}

    def tone(self, chord: dict, name: str) -> int:
        intervals = {(pc - chord['root']) % 12: pc for pc in chord['tones']}
        for interval in INTERVALS[name]:
            if interval in intervals:
                return intervals[interval]
        return (chord['root'] + 7) % 12 if name == 'fifth' else chord['root']

    def timeline(self, section: dict) -> list[tuple[float, float, dict]]:
        figures = section.get('chords')
        if not figures:
            progressions = self.plan.get('progressions', {})
            options = progressions.get(section.get('role', section['name'])) or progressions.get('default')
            if not options:
                raise SystemExit(f'section {section["name"]!r} has no chords and the style has no matching progression')
            figures = options[section.get('progression', 0) % len(options)]
        spans = section.get('bars_per_chord', self.plan.get('bars_per_chord', 1))
        spans = spans if isinstance(spans, list) else [spans] * len(figures)
        chords = [self.chord(figure, section) for figure in figures]
        result, time, index = [], section['start'], 0
        while time < section['end'] - 1e-6:
            end = min(section['end'], time + spans[index % len(spans)] * self.bar)
            result.append((time, end, chords[index % len(chords)]))
            time, index = end, index + 1
        return result

    def voicing(self, chord: dict, track: dict, previous: list[int] | None) -> list[int]:
        low, high = track['register']
        kind = track['voicing']
        tones = chord['tones']
        if kind == 'shell':
            tones = list(dict.fromkeys([chord['root'], self.tone(chord, 'third'), self.tone(chord, 'seventh')]))
        elif kind == 'triad':
            tones = list(dict.fromkeys([chord['root'], self.tone(chord, 'third'), self.tone(chord, 'fifth')]))
        elif kind == 'power':
            tones = [chord['root'], self.tone(chord, 'fifth')]
        upper_low = low + 12 if kind == 'spread' else low
        upper_tones = tones
        candidates = []
        for inversion in range(len(upper_tones)):
            order = upper_tones[inversion:] + upper_tones[:inversion]
            for base in range(upper_low, high + 1):
                if base % 12 != order[0]:
                    continue
                notes = [base]
                for pc in order[1:]:
                    notes.append(notes[-1] + ((pc - notes[-1]) % 12 or 12))
                if kind == 'power':
                    notes.append(notes[0] + 12)
                if kind == 'drop2' and len(notes) >= 4:
                    notes[-2] -= 12
                if kind == 'open' and len(notes) >= 3:
                    notes[1] += 12
                notes.sort()
                if kind == 'spread':
                    bottom = next(m for m in range(low, high + 1) if m % 12 == chord['root'])
                    notes = [bottom] + [n for n in notes if n > bottom]
                if notes[0] >= low and notes[-1] <= high:
                    candidates.append(notes)
        if not candidates:
            base = next(m for m in range(low, low + 12) if m % 12 == tones[0])
            candidates = [[base + ((pc - base) % 12) for pc in tones]]
        if previous:
            def distance(notes):
                return (sum(min(abs(n - p) for p in previous) for n in notes)
                        + sum(min(abs(p - n) for n in notes) for p in previous))
            return min(candidates, key=distance)
        centre = (low + high) / 2
        return min(candidates, key=lambda notes: abs(sum(notes) / len(notes) - centre))

    def near(self, pc: int, track: dict, target: float) -> int:
        low, high = track['register']
        options = [m for m in range(low - 12, high + 13) if m % 12 == pc]
        inside = [m for m in options if low <= m <= high] or options
        return min(inside, key=lambda m: abs(m - target))

    def scale_step(self, pitch: int, move: int, scale: list[int]) -> int:
        pcs = sorted(scale)
        degree = min(range(len(pcs)), key=lambda i: min((pitch - pcs[i]) % 12, (pcs[i] - pitch) % 12))
        octave = (pitch - pcs[degree]) // 12
        index = degree + move
        return pcs[index % len(pcs)] + 12 * (octave + index // len(pcs))

    # ---------- timing ----------

    def grid_time(self, section: dict, step: int) -> float:
        return section['start'] + step * self.step

    def at(self, section: dict, step: int, rng: random.Random, track: dict) -> float:
        time = self.grid_time(section, step)
        unit = max(1, self.grid // self.swing_grid)
        if self.swing != .5 and step % unit == 0 and (step // unit) % 2 == 1:
            time += (self.swing - .5) * 2 * unit * self.step
        jitter = track.get('humanize', self.humanize).get('time', 0)
        return max(section['start'], time + (rng.uniform(-jitter, jitter) if jitter else 0))

    def level(self, velocity: float, rng: random.Random, track: dict) -> float:
        spread = track.get('humanize', self.humanize).get('velocity', 0)
        return max(0.05, velocity * track['velocity'] * (1 + (rng.uniform(-spread, spread) if spread else 0)))

    @staticmethod
    def chord_at(chords: list, time: float) -> int:
        for index, (start, end, _) in enumerate(chords):
            if start - 1e-6 <= time < end - 1e-6:
                return index
        return len(chords) - 1

    # ---------- output events ----------

    def midi_track(self, name: str, track: dict, drum: bool = False) -> dict:
        if name not in self.midi:
            instrument = pretty_midi.Instrument(program=track.get('program', 0), is_drum=drum, name=name)
            if track.get('bank'):
                instrument.control_changes.append(pretty_midi.ControlChange(0, track['bank'], 0))
            instrument.control_changes.append(pretty_midi.ControlChange(10, int(round(track['pan'] * 127)), 0))
            self.midi[name] = {'instrument': instrument, 'track': track}
        return self.midi[name]

    def note(self, name: str, track: dict, start: float, length: float, pitch: int, velocity: float) -> None:
        if track['engine'] == 'soundfont':
            midi = self.midi_track(name, track)['instrument']
            midi.notes.append(pretty_midi.Note(velocity=int(np.clip(round(velocity * 100), 1, 127)), pitch=int(pitch),
                                               start=start, end=start + max(length, .02)))
            return
        instrument = track['instrument']
        if instrument not in MELODIC:
            raise SystemExit(f'track {name!r}: unknown Csound instrument {instrument!r}; choose from {sorted(MELODIC)}')
        amp = velocity * 10 ** (track['gain'] / 20)
        self.csound.append((MELODIC[instrument], start, max(length, .02),
                            (pretty_midi.note_number_to_hz(pitch), amp, track['pan'], track['brightness'], track['duck'],
                             track['reverb'], track['delay'], track['attack'], track['release'])))

    def drum(self, name: str, track: dict, voice: str, start: float, velocity: float) -> None:
        spec = track.get('kit', {}).get(voice, voice if track['engine'] == 'csound' else GM_DRUMS.get(voice))
        spec = spec if isinstance(spec, dict) else {'drum' if track['engine'] == 'csound' else 'note': spec}
        if voice == 'kick' or spec.get('drum') in ('kick', 'softkick'):
            self.kicks.append(start)
        if track['engine'] == 'soundfont':
            if spec.get('note') is None:
                raise SystemExit(f'track {name!r}: no General MIDI note for drum voice {voice!r}; set it in "kit"')
            midi = self.midi_track(name, track, drum=True)['instrument']
            midi.notes.append(pretty_midi.Note(velocity=int(np.clip(round(velocity * 100), 1, 127)),
                                               pitch=int(spec['note']), start=start, end=start + .2))
            return
        drum = spec['drum']
        if drum not in DRUMS:
            raise SystemExit(f'track {name!r}: unknown drum {drum!r} for voice {voice!r}; choose from {sorted(DRUMS)}')
        tone = spec.get('tone', track.get('tone', {}).get(voice, .5))
        amp = velocity * 10 ** ((track['gain'] + spec.get('gain', 0)) / 20)
        self.csound.append((DRUMS[drum], start, DRUM_LENGTH[drum] + (tone * .45 if drum == 'hat' else 0),
                            (amp, spec.get('pan', track['pan']), tone, spec.get('reverb', track['reverb']))))

    # ---------- patterns ----------

    def pattern(self, track: dict, override: dict) -> dict:
        source = override.get('pattern', track.get('pattern'))
        if isinstance(source, dict):
            return source
        if source not in self.patterns:
            raise SystemExit(f'pattern {source!r} is not defined')
        return self.patterns[source]

    def play(self, name: str, track: dict, pattern: dict, section: dict, chords: list, rng: random.Random,
             skip_last_bar: bool = False) -> None:
        kind = pattern.get('type', 'chord')
        bars = round((section['end'] - section['start']) / self.bar)
        limit = (bars - (1 if skip_last_bar else 0)) * self.grid
        getattr(self, f'play_{kind}')(name, track, pattern, section, chords, rng, limit)

    def cycle(self, pattern: dict, limit: int):
        length = pattern.get('bars', 1) * self.grid
        for offset in range(0, limit, length):
            yield offset

    def chord_notes(self, name: str, track: dict, chords: list, index: int) -> list[int]:
        key = f'{name}:{self.number}:{index}'
        if key not in self.voicings:
            self.voicings[key] = self.voicing(chords[index][2], track, self.voicings.get(f'{name}:last'))
            self.voicings[f'{name}:last'] = self.voicings[key]
        return self.voicings[key]

    def play_chord(self, name, track, pattern, section, chords, rng, limit):
        if pattern.get('hold'):
            for index, (start, end, _) in enumerate(chords):
                if (start - section['start']) / self.step >= limit - 1e-6:
                    continue
                for pitch in self.chord_notes(name, track, chords, index):
                    self.note(name, track, start, end - start, pitch, self.level(pattern.get('velocity', .8), rng, track))
                if track.get('swell') and track['engine'] == 'soundfont':
                    midi = self.midi_track(name, track)['instrument']
                    peak = start + (end - start) * .6
                    for moment in np.linspace(start, end - .05, 24):
                        rise = min(1.0, (moment - start) / max(peak - start, 1e-3))
                        fall = max(0.0, (moment - peak) / max(end - .05 - peak, 1e-3))
                        value = 45 + 67 * rise - 32 * fall
                        midi.control_changes.append(pretty_midi.ControlChange(11, int(round(value)), float(moment)))
                if track.get('sustain') and track['engine'] == 'soundfont':
                    midi = self.midi_track(name, track)['instrument']
                    midi.control_changes += [pretty_midi.ControlChange(64, 127, start + .01),
                                             pretty_midi.ControlChange(64, 0, end - .02)]
            return
        for offset in self.cycle(pattern, limit):
            for step, length, velocity in pattern['hits']:
                position = offset + step
                if position >= limit:
                    continue
                index = self.chord_at(chords, self.grid_time(section, position))
                start = self.at(section, position, rng, track)
                for pitch in self.chord_notes(name, track, chords, index):
                    self.note(name, track, start, length * self.step * track['gate'], pitch,
                              self.level(velocity, rng, track))
        if track.get('sustain') and track['engine'] == 'soundfont':
            midi = self.midi_track(name, track)['instrument']
            for start, end, _ in chords:
                midi.control_changes += [pretty_midi.ControlChange(64, 127, start + .01),
                                         pretty_midi.ControlChange(64, 0, end - .02)]

    def play_strum(self, name, track, pattern, section, chords, rng, limit):
        spread = pattern.get('spread', .012)
        for offset in self.cycle(pattern, limit):
            for step, length, velocity, direction in pattern['hits']:
                position = offset + step
                if position >= limit:
                    continue
                index = self.chord_at(chords, self.grid_time(section, position))
                notes = self.chord_notes(name, track, chords, index)
                notes = notes if direction == 'down' else notes[::-1]
                start = self.at(section, position, rng, track)
                for order, pitch in enumerate(notes):
                    self.note(name, track, start + order * spread, length * self.step * track['gate'], pitch,
                              self.level(velocity * (1 - .04 * order), rng, track))

    def play_arp(self, name, track, pattern, section, chords, rng, limit):
        rate, order = pattern.get('rate', 2), pattern.get('order', [0, 1, 2, 3])
        accents = pattern.get('velocity', [1.0, .8])
        for position in range(0, limit, rate):
            index = self.chord_at(chords, self.grid_time(section, position))
            chord_start = round((chords[index][0] - section['start']) / self.step)
            count = (position - chord_start) // rate
            slot = order[count % len(order)]
            if slot is None:
                continue
            notes = self.chord_notes(name, track, chords, index)
            pool = [note + 12 * octave for octave in range(pattern.get('octaves', 1)) for note in notes]
            self.note(name, track, self.at(section, position, rng, track), rate * self.step * pattern.get('gate', .8),
                      pool[slot % len(pool)], self.level(accents[count % len(accents)], rng, track))

    def play_bass(self, name, track, pattern, section, chords, rng, limit):
        scale = self.scale(section)
        for offset in self.cycle(pattern, limit):
            for step, length, role, velocity in pattern['notes']:
                position = offset + step
                if position >= limit:
                    continue
                index = self.chord_at(chords, self.grid_time(section, position))
                chord = chords[index][2]
                upcoming = chords[min(index + 1, len(chords) - 1)][2]
                previous = self.pitches.get(name, track['register'][0] + 7)
                root = self.near(chord['bass'], track, previous)
                if role == 'root':
                    pitch = root
                elif role == 'octave':
                    pitch = root + 12 if root + 12 <= track['register'][1] else root
                elif role == 'approach':
                    target = self.near(upcoming['bass'], track, root)
                    pitch = target - 1 if target > root else target + 1
                elif role == 'passing':
                    target = self.near(upcoming['bass'], track, root)
                    pitch = self.scale_step(root, 1 if target >= root else -1, scale)
                elif isinstance(role, int):
                    pitch = root + role
                else:
                    pitch = self.near(self.tone(chord, role), track, root)
                self.pitches[name] = pitch if role not in ('approach', 'passing') else root
                self.note(name, track, self.at(section, position, rng, track), length * self.step * track['gate'],
                          pitch, self.level(velocity, rng, track))

    def play_drums(self, name, track, pattern, section, chords, rng, limit):
        length = pattern.get('bars', 1) * self.grid
        for offset in self.cycle(pattern, limit):
            for voice, steps in pattern.items():
                if voice in ('type', 'bars'):
                    continue
                for step in range(length):
                    velocity = steps[step % len(steps)]
                    if velocity and offset + step < limit:
                        self.drum(name, track, voice, self.at(section, offset + step, rng, track),
                                  self.level(velocity, rng, track))

    def play_drone(self, name, track, pattern, section, chords, rng, limit):
        end = section['start'] + limit * self.step
        for start, stop, chord in (chords if pattern.get('follow') else [(section['start'], end, chords[0][2])]):
            stop = min(stop, end)
            if stop <= start:
                continue
            pitch = self.near(self.tone(chord, pattern.get('tone', 'root')), track, track['register'][0])
            self.note(name, track, start, stop - start, pitch, self.level(pattern.get('velocity', .8), rng, track))

    def play_texture(self, name, track, pattern, section, chords, rng, limit):
        instrument = track['instrument']
        if instrument not in TEXTURES:
            raise SystemExit(f'track {name!r}: unknown texture {instrument!r}; choose from {sorted(TEXTURES)}')
        self.csound.append((TEXTURES[instrument], section['start'], limit * self.step,
                            (10 ** (track['gain'] / 20), track['pan'], track['brightness'])))

    def phrase(self, rng: random.Random, settings: dict) -> list[tuple[float, float, int, float]]:
        density = settings.get('density', .5)
        weights = {'rest': 1.4 - density, 'half': max(0, .9 - density), 'quarter': 1.0, 'eighths': .4 + density,
                   'dotted': .3 + density * .6, 'offbeat': .3, 'sixteenths': max(0, density - .45) * 1.5,
                   'push': max(0, density - .3)}
        names = list(weights)
        notes, beat, beats = [], 0, settings.get('phrase_bars', 2) * self.meter
        while beat < beats:
            cell = 'half' if beat >= beats - 2 else rng.choices(names, [weights[n] for n in names])[0]
            if cell == 'half' and beat > beats - 2:
                cell = 'quarter'
            for start, length in CELLS[cell]:
                move = rng.choice([-2, -1, -1, 0, 1, 1, 2, 3, -3]) if notes else 0
                notes.append((beat + start, length, move, 1.0 if start == 0 else .8))
            beat += 2 if cell == 'half' else 1
        return notes

    def play_melody(self, name, track, pattern, section, chords, rng, limit):
        scale = self.scale(section)
        beat_steps = self.grid // self.meter
        low, high = track['register']
        if 'motif' in pattern:
            tonic = self.near(scale[0], track, (low + high) / 2)
            phrases = [[(step / beat_steps, length / beat_steps, degree, velocity)
                        for step, length, degree, velocity in pattern['motif']]]
            form, absolute = ['A'], True
            phrase_steps = pattern.get('bars', 1) * self.grid
            labels = {'A': phrases[0]}
        else:
            settings = pattern.get('generate', {})
            phrase_rng = random.Random(f'{self.seed}:{name}:motif:{settings.get("seed", 0)}')
            labels = {}
            form = settings.get('form', ['A', 'A2', 'B', 'A'])
            for label in dict.fromkeys(item.rstrip('2') for item in form):
                labels[label] = self.phrase(phrase_rng, settings)
            for label in form:
                if label.endswith('2') and label not in labels:
                    varied = list(labels[label[:-1]])
                    tail = self.phrase(phrase_rng, settings)
                    for offset in range(1, min(3, len(varied), len(tail)) + 1):
                        beat, length, _, _ = varied[-offset]
                        varied[-offset] = (beat, length, tail[-offset][2], .9)
                    labels[label] = varied
            absolute = False
            phrase_steps = settings.get('phrase_bars', 2) * self.grid
        pitch = self.pitches.get(name)
        for number, offset in enumerate(range(0, limit, phrase_steps)):
            for beat, length, value, velocity in labels[form[number % len(form)]]:
                position = offset + round(beat * beat_steps)
                if position >= limit:
                    continue
                index = self.chord_at(chords, self.grid_time(section, position))
                chord = chords[index][2]
                if absolute:
                    pitch = self.scale_step(tonic, value - 1, scale)
                    snap = pattern.get('snap', False)
                else:
                    if pitch is None:
                        pitch = self.near(chord['root'], track, (low + high) / 2)
                    pitch = self.scale_step(pitch, value, scale)
                    snap = True
                if snap and position % beat_steps == 0:
                    pitch = min((m for m in range(pitch - 6, pitch + 7) if m % 12 in chord['tones']),
                                key=lambda m: abs(m - pitch))
                while pitch > high:
                    pitch -= 12
                while pitch < low:
                    pitch += 12
                self.note(name, track, self.at(section, position, rng, track),
                          length * beat_steps * self.step * track['gate'], pitch, self.level(velocity, rng, track))
        self.pitches[name] = pitch

    # ---------- arrangement ----------

    def section_tracks(self, section: dict) -> dict[str, dict]:
        arrangements = self.plan.get('arrangements', {})
        active = {}
        if 'energy' in section:
            level = str(section['energy'])
            if level not in arrangements:
                raise SystemExit(f'section {section["name"]!r}: no arrangement for energy {level}')
            active = copy.deepcopy(arrangements[level])
        for name, value in section.get('tracks', {}).items():
            if value is False:
                active.pop(name, None)
            elif value is True:
                active.setdefault(name, {})
            else:
                active[name] = merge(active.get(name, {}), value)
        for name in active:
            if name not in self.tracks:
                raise SystemExit(f'section {section["name"]!r} uses track {name!r}, which is not defined')
        return active

    def compose(self) -> None:
        sections = self.plan['sections']
        for number, section in enumerate(sections):
            self.number = number
            chords = self.timeline(section)
            active = self.section_tracks(section)
            upcoming = sections[number + 1] if number + 1 < len(sections) else None
            rising = upcoming is not None and upcoming.get('energy', 0) > section.get('energy', 0)
            fill = section.get('fill', rising)
            previous = sections[number - 1] if number else None
            entering = previous is not None and section.get('energy', 0) > previous.get('energy', 0)
            for name, override in active.items():
                track = merge(self.tracks[name], {k: v for k, v in override.items() if k != 'pattern'})
                pattern = self.pattern(track, override)
                rng = random.Random(f'{self.seed}:{name}:{number}')
                fill_pattern = self.plan.get('fills', {}).get(name) if fill else None
                self.play(name, track, pattern, section, chords, rng, skip_last_bar=bool(fill_pattern))
                if fill_pattern:
                    bars = round((section['end'] - section['start']) / self.bar)
                    last = dict(section, start=section['start'] + (bars - 1) * self.bar)
                    self.play(name, track, self.patterns[fill_pattern], last, chords, rng)
                if entering and name in self.plan.get('entry', {}):
                    for voice, velocity in self.plan['entry'][name].items():
                        self.drum(name, track, voice, section['start'], velocity)
        if self.kicks and any(track['duck'] > 0 for track in self.tracks.values()):
            for time in self.kicks:
                self.csound.append((3, time, self.beat * .9, (1.0,)))
        self.effects()

    # ---------- effects and cues ----------

    def effect_layer(self, layer: dict, time: float, amp: float, shimmer: float = .5) -> None:
        if 'program' in layer:
            track = merge(TRACK, {'engine': 'soundfont', 'program': layer['program'], 'gain': layer.get('gain', 0),
                                  'reverb': layer.get('reverb', .3)})
            midi = self.midi_track(f'fx-{layer["program"]}', track)['instrument']
            midi.notes.append(pretty_midi.Note(velocity=int(np.clip(round(amp * layer.get('velocity', 1) * 110), 1, 127)),
                                               pitch=layer.get('note', 48), start=time, end=time + layer.get('length', 2.0)))
            return
        name, scale = layer.get('instrument', 'impact'), amp * layer.get('amp', 1.0)
        if name == 'impact':
            self.csound.append((30, time, 3.2, (scale, layer.get('shimmer', shimmer))))
            self.csound.append((33, time, 1.6, (scale * .16,)))
        elif name == 'thud':
            self.csound.append((34, time, .5, (scale,)))
        elif name in DRUMS:
            self.csound.append((DRUMS[name], time, DRUM_LENGTH[name] + 1.0,
                                (scale, .5, layer.get('tone', .5), layer.get('reverb', .3))))
        else:
            raise SystemExit(f'unknown effect instrument {name!r}')

    def effects(self) -> None:
        fx = self.plan.get('fx', {})
        for item in self.plan.get('hits', []):
            for layer in fx.get('hit', [{'instrument': 'impact'}]):
                self.effect_layer(layer, item['t'], item.get('amp', .8), item.get('shimmer', .5))
        for item in self.plan.get('risers', []):
            start = item['end'] - item['duration']
            for layer in fx.get('riser', [{'instrument': 'riser'}]):
                kind, amp = layer.get('instrument', 'riser'), item.get('amp', .25) * layer.get('amp', 1.0)
                if kind == 'riser':
                    self.csound.append((31, start, item['duration'], (amp, 110, 440)))
                elif kind == 'reverse':
                    self.csound.append((58, start, item['duration'], (amp * 2,)))
                elif kind == 'swell':
                    section = self.section_at(item['end'])
                    chord = self.timeline(section)[0][2] if section else {'tones': [0, 4, 7]}
                    for pc in chord['tones'][:3]:
                        self.csound.append((32, start, item['duration'], (pretty_midi.note_number_to_hz(60 + pc), amp * .5)))
                else:
                    raise SystemExit(f'unknown riser instrument {kind!r}')
        for item in self.plan.get('swells', []):
            chord = self.chord(item['chord'], self.section_at(item['end']) or {})
            for pc in chord['tones'][:3]:
                self.csound.append((32, item['end'] - item['duration'], item['duration'],
                                    (pretty_midi.note_number_to_hz(60 + pc), item.get('amp', .12))))
        roll = DRUMS[fx.get('roll', 'snare')]
        for item in self.plan.get('rolls', []):
            count = int(round(item['duration'] / (self.step)))
            for step in range(count):
                level = item.get('low', .05) + (item.get('high', .4) - item.get('low', .05)) * (step / max(1, count - 1)) ** 1.6
                self.csound.append((roll, item['start'] + step * self.step, .4, (level, .5, .4, .25)))
        for item in self.plan.get('thuds', []):
            self.csound.append((34, item['t'], .5, (item.get('amp', .8),)))
        for item in self.plan.get('bells', []):
            self.csound.append((13, item['t'], item.get('duration', 1.6),
                                (pretty_midi.note_number_to_hz(pretty_midi.note_name_to_number(item['note'])),
                                 item.get('amp', .1), item.get('pan', .5), item.get('ratio', 1.0), item.get('index', 1.4))))
        for item in self.plan.get('chimes', []):
            notes = [('D6', .11, 0), ('A6', .09, .09)] if item.get('bright', True) else [('A5', .065, 0)]
            for note, amp, delay in notes:
                self.csound.append((13, item['t'] + delay, 1.5,
                                    (pretty_midi.note_number_to_hz(pretty_midi.note_name_to_number(note)), amp,
                                     .58 if item.get('bright', True) else .4, 2.0, 1.5)))

    def section_at(self, time: float) -> dict | None:
        return next((s for s in self.plan['sections'] if s['start'] - 1e-6 <= time < s['end'] + 1e-6), None)

    def merge_cues(self, cues: list[dict]) -> None:
        # Page cue types map onto score events, so a getCues() export can drive the effects directly.
        plan = self.plan
        for cue in cues:
            kind, time = cue['type'], cue['t']
            if kind == 'impact':
                plan.setdefault('hits', []).append({'t': time, 'amp': .8 * cue.get('size', 1.0)})
            elif kind == 'thud':
                plan.setdefault('thuds', []).append({'t': time, 'amp': cue.get('amp', .8)})
            elif kind == 'chime':
                plan.setdefault('chimes', []).append({'t': time, 'bright': cue.get('bright', True)})
            elif kind == 'blip':
                scale = self.scale(self.section_at(time) or {})
                target = pretty_midi.hz_to_note_number(cue.get('pitch', 2000.0))
                note = min((n for n in range(60, 100) if n % 12 in scale), key=lambda n: abs(n - target))
                plan.setdefault('bells', []).append({'t': time, 'note': pretty_midi.note_number_to_name(note), 'amp': .08,
                                                     'duration': 1.0, 'ratio': 3.5, 'index': 1.2})
            elif kind == 'riser':
                plan.setdefault('risers', []).append({'end': time, 'duration': cue.get('dur', 3.0), 'amp': cue.get('amp', .25)})
            elif kind == 'transition':
                continue
            else:
                print(f'cue type {kind!r} at {time} s has no score mapping; skipped', file=sys.stderr)

    # ---------- rendering ----------

    def score(self) -> list[str]:
        total = self.duration + self.tail
        mix = self.plan.get('mix', {})
        delay, reverb = mix.get('delay', {}), mix.get('reverb', {})
        lines = [f'i 2 0 {total:.4f}',
                 f'i 98 0 {total:.4f} {delay.get("beats", 1.5) * self.beat:.6g} {delay.get("feedback", .38):.6g}',
                 f'i 99 0 {total:.4f} {reverb.get("feedback", .87):.6g} {reverb.get("level", .62):.6g}']
        for number, start, length, fields in sorted(self.csound, key=lambda event: (event[1], event[0])):
            if start >= self.duration:
                continue
            values = ' '.join(f'{value:.6g}' for value in fields)
            lines.append(f'i {number} {start:.4f} {length:.4f} {values}')
        return lines

    def render(self, output: Path, orchestra: Path, soundfont: Path | None) -> dict:
        stems = output.with_suffix('.stems')
        stems.mkdir(parents=True, exist_ok=True)
        total = self.duration + self.tail
        csound = shutil.which('csound')
        if csound is None:
            raise SystemExit('csound is required (brew install csound / apt install csound)')
        score = output.with_suffix('.sco')
        score.write_text('\n'.join(self.score()) + '\ne\n', encoding='utf-8')
        synth = stems / 'synth.wav'
        subprocess.run([csound, '-d', '-W', '-f', '-m0', '-o', str(synth), str(orchestra), str(score)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rendered = []
        if self.midi:
            fluidsynth = shutil.which('fluidsynth')
            if fluidsynth is None:
                raise SystemExit('fluidsynth is required for SoundFont tracks (brew install fluid-synth / apt install fluidsynth)')
            if soundfont is None or not soundfont.exists():
                raise SystemExit('SoundFont tracks need a General MIDI SoundFont: pass --soundfont, or install '
                                 'MuseScore_General.sf3 (see scripts/README.md)')
            for name, entry in self.midi.items():
                song = pretty_midi.PrettyMIDI(initial_tempo=self.bpm)
                instrument = entry['instrument']
                instrument.notes = [n for n in instrument.notes if n.start < self.duration]
                instrument.control_changes.append(pretty_midi.ControlChange(7, 100, total))
                song.instruments.append(instrument)
                midi_path = stems / f'{safe(name)}.mid'
                wav_path = stems / f'{safe(name)}.wav'
                song.write(str(midi_path))
                subprocess.run([fluidsynth, '-ni', '-q', '-R', '0', '-C', '0', '-g', '1.0', '-r', str(RATE), '-O', 'float',
                                '-T', 'wav', '-F', str(wav_path), str(soundfont), str(midi_path)], check=True)
                rendered.append((name, wav_path, entry['track'], instrument.is_drum))
        audio = self.mix(synth, rendered, total, stems)
        soundfile.write(output, audio, RATE, subtype='FLOAT')
        peak = float(np.abs(audio).max())
        return {'output': str(output), 'style': self.plan.get('style'), 'bpm': self.bpm,
                'key': f'{self.plan.get("key", "C")} {self.plan.get("mode", "major")}', 'duration_s': round(total, 3),
                'csound_events': len(self.csound), 'soundfont_tracks': [name for name, _, _, _ in rendered],
                'soundfont': str(soundfont) if rendered else None, 'stems': str(stems), 'score': str(score),
                'peak_db': round(20 * np.log10(peak + 1e-12), 2)}

    def mix(self, synth: Path, rendered: list, total: float, stems: Path) -> np.ndarray:
        length = int(round(total * RATE))
        raw = fit(synth, length, channels=4)
        out, drums = raw[:, :2].copy(), raw[:, 2:4].copy()
        bus = np.zeros_like(out)
        for name, path, track, is_drum in rendered:
            audio = fit(path, length) * 10 ** (track['gain'] / 20)
            if track.get('highpass'):
                audio = process(Pedalboard([HighpassFilter(track['highpass'])]), audio)
            if track['duck'] > 0 and self.kicks:
                audio *= self.duck(track['duck'] * self.plan.get('mix', {}).get('sidechain', 1.0), length)[:, None]
            if is_drum:
                drums += audio
            else:
                out += audio
            bus += audio * track['reverb']
        mix = self.plan.get('mix', {})
        if np.any(drums):
            # Soft clipping on the drum bus trims kick and snare peaks by about `clip` dB; the bus then returns to
            # its tuned loudness, so the master limiter no longer has to absorb the transients.
            clip = mix.get('drum_bus', {}).get('clip', 6.0)
            meter = pyloudnorm.Meter(RATE)
            before = meter.integrated_loudness(drums)
            peak_db = 20 * np.log10(np.abs(drums).max() + 1e-12)
            processed = process(Pedalboard([Gain(-peak_db), Distortion(drive_db=clip)]), drums)
            after = meter.integrated_loudness(processed)
            if np.isfinite(before) and np.isfinite(after):
                processed *= 10 ** ((before - after) / 20)
            soundfile.write(stems / 'drums.wav', processed, RATE, subtype='FLOAT')
            out += processed
        if np.any(bus):
            room = mix.get('room', .6)
            out += process(Pedalboard([Reverb(room_size=room, damping=.5, wet_level=1.0, dry_level=0.0, width=1.0)]), bus)
        chain = [HighpassFilter(28)]
        if mix.get('wow'):
            chain.append(Chorus(rate_hz=.5, depth=mix['wow'], centre_delay_ms=6, feedback=0.0, mix=.5))
        if mix.get('drive'):
            chain.append(Distortion(drive_db=mix['drive']))
        if mix.get('bits'):
            chain.append(Bitcrush(bit_depth=mix['bits']))
        if mix.get('lowpass'):
            chain.append(LowpassFilter(mix['lowpass']))
        return process(Pedalboard(chain), out)

    def duck(self, depth: float, length: int) -> np.ndarray:
        gain = np.ones(length)
        span = int(self.beat * .9 * RATE)
        shape = 1 - depth * .001 ** (np.arange(span) / span)
        for time in self.kicks:
            start = int(time * RATE)
            segment = gain[start:start + span]
            np.minimum(segment, shape[:len(segment)], out=segment)
        return gain


def safe(name: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]', '_', name)


def fit(path: Path, length: int, channels: int = 2) -> np.ndarray:
    audio, rate = soundfile.read(path, dtype='float32', always_2d=True)
    if rate != RATE:
        raise SystemExit(f'{path} is {rate} Hz, expected {RATE} Hz')
    if audio.shape[1] == 1:
        audio = np.repeat(audio, 2, axis=1)
    out = np.zeros((length, channels), dtype=np.float32)
    out[:min(length, len(audio)), :min(channels, audio.shape[1])] = audio[:length, :channels]
    return out


def process(board: Pedalboard, audio: np.ndarray) -> np.ndarray:
    return board(audio.T.astype(np.float32), RATE).T


def check_grid(plan: dict) -> None:
    bar = plan.get('meter', 4) * 60 / plan['bpm']
    for section in plan['sections']:
        for edge in ('start', 'end'):
            offset = section[edge] / bar
            if abs(offset - round(offset)) > 1e-3:
                print(f'section {section["name"]!r} {edge} {section[edge]} s is {offset:.3f} bars; snap it with '
                      'tempo_grid.py', file=sys.stderr)


def preview(args, folders: list[Path]) -> None:
    names = args.only.split(',') if args.only else sorted(path.stem for path in STYLES.glob('*.json'))
    args.preview.mkdir(parents=True, exist_ok=True)
    soundfont = find_soundfont(args.soundfont)
    for name in names:
        style = load_style(name, folders)
        settings = style.get('preview', {})
        bars = args.bars or settings.get('bars', 8)
        energies = settings.get('energy', [1, 2, 3, 4])
        bpm = style.get('bpm', 120)
        bar = style.get('meter', 4) * 60 / bpm
        per = max(1, bars // len(energies))
        sections, start = [], 0
        for number, energy in enumerate(energies):
            length = per if number < len(energies) - 1 else bars - per * (len(energies) - 1)
            if length <= 0:
                break
            sections.append({'name': f'energy{energy}', 'role': settings.get('role', 'default'), 'energy': energy,
                             'start': start * bar, 'end': (start + length) * bar})
            start += length
        plan = resolve({'style': name, 'bpm': bpm, 'duration': start * bar, 'tail': 3, 'sections': sections}, folders)
        composer = Composer(plan)
        composer.compose()
        report = composer.render(args.preview / f'{name}.wav', args.orchestra, soundfont)
        print(f'{name:16} {bpm:>4} BPM  {plan.get("key", "C")} {plan.get("mode", "major"):10} '
              f'{report["duration_s"]:6.1f} s  peak {report["peak_db"]:6.1f} dB  -> {report["output"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('plan', type=Path, nargs='?', help='music plan JSON')
    parser.add_argument('output', type=Path, nargs='?', help='rendered float WAV; stems go to <output>.stems/')
    parser.add_argument('--cues', type=Path, help='JSON list of page cues, or an object with a "cues" list')
    parser.add_argument('--styles', type=Path, action='append', default=[], help='extra folder of style JSON files')
    parser.add_argument('--soundfont', type=Path, help='General MIDI SoundFont (.sf2/.sf3) for SoundFont tracks')
    parser.add_argument('--orchestra', type=Path, default=ORCHESTRA)
    parser.add_argument('--preview', type=Path, help='render a short demo of each style into this folder')
    parser.add_argument('--only', help='comma-separated styles for --preview')
    parser.add_argument('--bars', type=int, help='bars per preview')
    parser.add_argument('--list', action='store_true', help='print the available styles')
    parser.add_argument('--report', type=Path, help='write the render report as JSON')
    args = parser.parse_args()
    folders = args.styles + ([args.plan.parent / 'styles'] if args.plan else []) + [STYLES]
    if args.list:
        for path in sorted({p.stem: p for folder in reversed(folders) if folder.exists()
                            for p in folder.glob('*.json')}.values()):
            style = json.loads(path.read_text(encoding='utf-8'))
            print(f'{path.stem:16} {style.get("bpm", ""):>4} BPM  {style.get("description", "")}')
        return
    if args.preview:
        preview(args, folders)
        return
    if not args.plan or not args.output:
        parser.error('plan and output are required unless --preview or --list is given')
    plan = resolve(json.loads(args.plan.read_text(encoding='utf-8')), folders)
    check_grid(plan)
    cues = None
    if args.cues:
        data = json.loads(args.cues.read_text(encoding='utf-8'))
        cues = data['cues'] if isinstance(data, dict) else data
    composer = Composer(plan, cues)
    composer.compose()
    report = composer.render(args.output, args.orchestra, find_soundfont(args.soundfont))
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.report:
        args.report.write_text(text + '\n', encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
