; SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
; SPDX-License-Identifier: MIT
; Instruments for scripts/compose_music.py. Instrument numbers and p-fields are part of the score contract:
;   melodic  p4 freq, p5 amp, p6 pan 0..1, p7 brightness 0..1, p8 sidechain depth, p9 reverb send,
;            p10 delay send, p11 attack, p12 release
;   drum     p4 amp, p5 pan 0..1, p6 tone 0..1, p7 reverb send
;   effects  signatures listed above each instrument
; Channels 1-2 carry music and effects; drums go to channels 3-4 so the mixer can compress them as a bus.

sr = 48000
ksmps = 16
nchnls = 4
0dbfs = 1
; A fixed seed keeps random and dust noise identical between renders.
seed 2026

gaRevL init 0
gaRevR init 0
gaDelL init 0
gaDelR init 0
gkDuck init 0
giSine ftgen 1, 0, 16384, 10, 1

opcode Out, 0, aaii
  aL, aR, irev, idel xin
  outch 1, aL, 2, aR
  gaRevL = gaRevL + aL * irev
  gaRevR = gaRevR + aR * irev
  gaDelL = gaDelL + aL * idel
  gaDelR = gaDelR + aR * idel
endop

opcode DrumOut, 0, aai
  aL, aR, irev xin
  outch 3, aL, 4, aR
  gaRevL = gaRevL + aL * irev
  gaRevR = gaRevR + aR * irev
endop

; Equal-power balance for instruments that are already stereo.
opcode Balance, aa, aai
  aL, aR, ipan xin
  xout aL * cos(ipan * $M_PI_2) * 1.414, aR * sin(ipan * $M_PI_2) * 1.414
endop

opcode SnareCore, a, i
  itone xin
  kp expseg 230 + itone * 60, 0.04, 175, 0.1, 165
  abody poscil 1, kp, giSine
  abenv expseg 1, 0.11, 0.001
  anz rand 1
  anenv expseg 1, 0.12 + itone * 0.12, 0.0005
  ahp butterhp anz, 1800
  abp butterbp anz, 5000 + itone * 2000, 4000
  xout abody * abenv * 0.55 + (ahp * 0.5 + abp * 0.6) * anenv * (0.6 + itone * 0.5)
endop

opcode CymbalCore, a, 0
  ; The six square partials of an analogue cymbal give the metallic body.
  a1 vco2 1, 205.3, 10
  a2 vco2 1, 304.4, 10
  a3 vco2 1, 369.6, 10
  a4 vco2 1, 522.7, 10
  a5 vco2 1, 540.0, 10
  a6 vco2 1, 800.0, 10
  amet butterhp a1 + a2 + a3 + a4 + a5 + a6, 7000
  anz rand 1
  ahiss butterhp anz, 5000
  xout amet * 0.12 + ahiss * 0.5
endop

; Sidechain value: cleared every control cycle, then raised by duck events.
instr 2
  gkDuck = 0
endin

; Duck event: p4 depth
instr 3
  kenv expseg 1, p3, 0.001
  gkDuck = max(gkDuck, kenv * p4)
endin

; Kick
instr 4
  itop = 150 + p6 * 60
  ibase = 38 + p6 * 12
  kpitch expseg itop, 0.035, ibase * 1.5, 0.2, ibase * 1.1, 0.3, ibase
  aenv expseg 1, 0.34, 0.0005
  abody poscil 1, kpitch, giSine
  aclickenv expseg 1, 0.006, 0.0005
  anoise rand 1
  aclick butterhp anoise * aclickenv, 3500
  aout = (tanh(abody * aenv * 1.5) * 0.85 + aclick * 0.45 * (0.4 + p6)) * p4 * 0.8
  aL, aR pan2 aout, p5
  DrumOut aL, aR, p7
endin

; Pulse bass
instr 10
  aenv madsr max(p11, 0.004), 0.12, 0.7, max(p12, 0.06)
  icut = 250 + p7 * 1500
  kcut expseg icut * 4, 0.09, icut, p3, icut * 0.9
  asaw vco2 1, p4
  asq vco2 0.6, p4 * 1.003, 10
  asub poscil 1, p4, giSine
  afilt moogladder (asaw + asq) * 0.5, kcut, 0.25
  aout = (afilt * 0.75 + asub * 0.32) * aenv * p5 * 0.62 * (1 - gkDuck * p8)
  aL, aR pan2 aout, p6
  Out aL, aR, p9, p10
endin

; Synth pluck
instr 11
  aenv expseg 0.001, 0.004, 1, p3 - 0.004, 0.001
  kcut expseg 500 + p7 * 5200, 0.16, 320 + p7 * 900, p3, 260
  a1 vco2 0.5, p4
  a2 vco2 0.45, p4 * 1.006, 10
  af moogladder a1 + a2, kcut, 0.22
  aout = af * aenv * p5 * 1.5 * (1 - gkDuck * p8)
  aL, aR pan2 aout, p6
  Out aL, aR, p9, p10
endin

; Analogue pad
instr 12
  aenv linsegr 0, max(p11, 0.01), 1, max(p12, 0.1), 0
  irate random 0.07, 0.14
  iphase random 0, 1
  klfo poscil 1, irate, giSine, iphase
  kcut = (600 + p7 * 3400) * (1 + 0.22 * klfo)
  a1 vco2 1, p4 * 0.9962
  a2 vco2 1, p4 * 1.0041
  a3 vco2 1, p4 * 1.0016
  a4 vco2 1, p4 * 0.9983
  aL moogladder a1 + a3 * 0.7, kcut, 0.12
  aR moogladder a2 + a4 * 0.7, kcut, 0.12
  aL butterhp aL, 150
  aR butterhp aR, 150
  kduck = 1 - gkDuck * p8
  aL, aR Balance aL * aenv * p5 * kduck * 0.6, aR * aenv * p5 * kduck * 0.6, p6
  Out aL, aR, p9, p10
endin

; FM bell for effects: p4 freq, p5 amp, p6 pan, p7 modulator ratio, p8 index
instr 13
  kidx expseg p8, p3, 0.15
  aenv expseg 0.001, 0.004, 1, p3 - 0.004, 0.0005
  a1 foscili aenv, p4, 1, p7, kidx, giSine
  a2 poscil aenv * 0.25, p4 * 2.001, giSine
  aout = (a1 + a2) * p5 * 1.2
  aL, aR pan2 aout, p6
  Out aL, aR, 0.55, 0.3
endin

; Drone with a slowly opening filter
instr 14
  aenv linsegr 0, max(p11, 0.05), 1, max(p12, 0.1), 0
  kcut expseg 140, p3, 300 + p7 * 1200
  klfo poscil 0.15, 0.09, giSine
  a1 vco2 1, p4
  a2 vco2 1, p4 * 1.007
  asub poscil 1, p4 * 0.5, giSine
  af moogladder a1 + a2, kcut * (1 + klfo), 0.3
  aout = (af * 0.45 + asub * 0.3) * aenv * p5 * (1 - gkDuck * p8)
  aL, aR pan2 aout, p6
  Out aL, aR, p9, p10
endin

; Hat: tone sets the decay, from closed to open
instr 20
  aenv expseg 1, 0.03 + p6 * 0.4, 0.0005
  anoise rand 1
  ahp butterhp anoise, 7200
  abp butterbp ahp, 10500, 7000
  aout = abp * aenv * p4 * 1.6
  aL, aR pan2 aout, p5
  DrumOut aL, aR, p7
endin

; Clap
instr 21
  anoise rand 1
  aburst linseg 0, 0.001, 1, 0.008, 0.18, 0.001, 1, 0.008, 0.18, 0.001, 1, 0.19, 0
  atail expseg 0.0001, 0.02, 1, 0.24, 0.0005
  abp butterbp anoise, 1100 + p6 * 600, 900
  ahp butterhp anoise, 2600
  aout = (abp * aburst * 0.9 + ahp * atail * 0.3) * p4
  aL, aR pan2 aout, p5
  DrumOut aL, aR, p7
endin

; Tick
instr 22
  aenv expseg 1, 0.03, 0.0005
  a1 poscil aenv * p4, 2000 + p6 * 2000, giSine
  aL, aR pan2 a1, p5
  DrumOut aL, aR, p7
endin

; Impact: p4 amp, p5 shimmer amount
instr 30
  kpitch expseg 72, 0.08, 46, 1.8, 26
  aenv expseg 1, p3, 0.0005
  aboom poscil 1, kpitch, giSine
  aboom = tanh(aboom * 1.7) * aenv
  anoise rand 1
  anenv expseg 1, 0.9, 0.0005
  anz butterlp anoise * anenv, 1100
  ashenv expseg 0.0001, 0.01, 1, 2.6, 0.0005
  ash butterhp anoise * ashenv, 6500
  amono = (aboom * 0.85 + anz * 0.3) * p4
  ashL = ash * p5 * p4 * 0.22
  outch 1, amono + ashL, 2, amono + ashL * 0.9
  gaRevL = gaRevL + (amono * 0.3 + ashL * 0.6)
  gaRevR = gaRevR + (amono * 0.3 + ashL * 0.6)
endin

; Riser: p4 amp, p5 start pitch, p6 end pitch
instr 31
  kcf expseg 300, p3, 9000
  kamp expseg 0.01, p3, 1
  kgate linseg 1, p3 - 0.01, 1, 0.01, 0
  anoise rand 1
  abp butterbp anoise, kcf, kcf * 0.6
  kp expseg p5, p3, p6
  asaw vco2 0.3, kp
  asf moogladder asaw, kcf * 0.5, 0.3
  aout = (abp * 0.75 + asf * 0.45) * kamp * kgate * p4
  Out aout * 0.9, aout, 0.3, 0
endin

; Reverse swell: p4 freq, p5 amp
instr 32
  kamp expseg 0.001, p3 - 0.012, 1, 0.012, 0.001
  kcut expseg 400, p3, 5000
  a1 vco2 1, p4
  a2 vco2 1, p4 * 1.005
  af moogladder a1 + a2, kcut, 0.15
  aout = af * kamp * p5 * 0.5
  Out aout, aout, 0.35, 0
endin

; Downlifter: p4 amp
instr 33
  kcf expseg 6000, p3, 180
  kamp expseg 1, p3, 0.001
  anoise rand 1
  abp butterbp anoise, kcf, kcf * 0.7
  aout = abp * kamp * p4
  Out aout, aout * 0.92, 0.3, 0
endin

; Body thud for on-screen collisions: p4 amp
instr 34
  kp expseg 140, 0.09, 52
  aenv expseg 1, 0.24, 0.0005
  a1 poscil 1, kp, giSine
  anoise rand 1
  aknockenv expseg 1, 0.06, 0.0005
  aknock butterbp anoise * aknockenv, 850, 600
  aout = (a1 * aenv * 0.9 + aknock * 0.7) * p4
  Out aout, aout, 0.15, 0
endin

; Electric piano: an FM pair whose index falls after the strike, a short metallic tine, and tremolo
instr 40
  xtratim 0.3
  kidx expseg 1 + p7 * 3, 0.9, 0.35, p3 + 0.3, 0.2
  aenv expsegr 0.001, 0.003, 1, 2.8, 0.05, max(p12, 0.15), 0.0001
  a1 foscili 1, p4, 1, 1, kidx, giSine
  ktine expseg 1, 0.06, 0.001
  a2 foscili ktine * (0.1 + p7 * 0.2), p4, 1, 14, 1.2, giSine
  ab butterlp a1 + a2, 2500 + p7 * 5000
  klfo poscil 0.5, 4.6, giSine
  aout = ab * aenv * p5 * 0.42 * (1 - gkDuck * p8)
  aL = aout * (1 - 0.18 * (0.5 + klfo))
  aR = aout * (1 - 0.18 * (0.5 - klfo))
  aL, aR Balance aL, aR, p6
  Out aL, aR, p9, p10
endin

; Supersaw: seven detuned saws spread across the stereo field
instr 41
  aenv linsegr 0, max(p11, 0.005), 1, max(p12, 0.08), 0
  kcut = 700 + p7 * 7000
  a1 vco2 1, p4 * 0.988
  a2 vco2 1, p4 * 0.994
  a3 vco2 1, p4
  a4 vco2 1, p4 * 1.006
  a5 vco2 1, p4 * 1.012
  a6 vco2 1, p4 * 0.997
  a7 vco2 1, p4 * 1.003
  aL moogladder a1 + a2 * 0.8 + a3 * 0.6 + a6 * 0.7, kcut, 0.1
  aR moogladder a5 + a4 * 0.8 + a3 * 0.6 + a7 * 0.7, kcut, 0.1
  aL butterhp aL, 180
  aR butterhp aR, 180
  kgain = aenv * p5 * 0.16 * (1 - gkDuck * p8)
  aL, aR Balance aL * kgain, aR * kgain, p6
  Out aL, aR, p9, p10
endin

; Mono saw bass with a filter envelope
instr 42
  aenv madsr max(p11, 0.003), 0.15, 0.6, max(p12, 0.05)
  kcut expseg 200 + p7 * 3800, 0.12, 120 + p7 * 900, p3, 110 + p7 * 700
  asaw vco2 1, p4
  asub vco2 0.5, p4 * 0.5, 10
  af moogladder asaw * 0.7 + asub * 0.5, kcut, 0.35
  aout = tanh(af * 1.4) * aenv * p5 * 1.1 * (1 - gkDuck * p8)
  aL, aR pan2 aout, p6
  Out aL, aR, p9, p10
endin

; 808 bass: sine with a pitch drop and saturation set by brightness
instr 43
  kpitch expseg p4 * 1.6, 0.03, p4, p3 + 0.2, p4 * 0.97
  aenv expsegr 0.001, 0.004, 1, 1.4, 0.25, max(p12, 0.08), 0.0001
  a1 poscil 1, kpitch, giSine
  aout = tanh(a1 * (1 + p7 * 3)) * aenv * p5 * 0.75 * (1 - gkDuck * p8)
  aL, aR pan2 aout, p6
  Out aL, aR, p9, p10
endin

; Mono lead with delayed vibrato
instr 44
  aenv madsr max(p11, 0.01), 0.2, 0.75, max(p12, 0.12)
  kvib linseg 0, 0.25, 0, 0.3, 1, p3, 1
  klfo poscil 0.006 * kvib, 5.4, giSine
  kf = p4 * (1 + klfo)
  a1 vco2 1, kf
  a2 vco2 0.6, kf * 1.004, 2, 0.4
  af moogladder a1 * 0.6 + a2 * 0.4, 900 + p7 * 6000, 0.2
  aout = af * aenv * p5 * 1.25 * (1 - gkDuck * p8)
  aL, aR pan2 aout, p6
  Out aL, aR, p9, p10
endin

; Mallet: an impulse rings three modes tuned like a marimba bar; brightness hardens the strike
instr 45
  xtratim 1.4
  aimp mpulse 1, 0
  anz rand 1
  anzenv expseg 1, 0.003 + (1 - p7) * 0.004, 0.0001
  aex = aimp + anz * anzenv * 0.3 * p7
  a1 mode aex, p4, 420
  a2 mode aex, p4 * 3.99, 260
  a3 mode aex, p4 * 10.65, 120
  krel linsegr 1, p3, 1, max(p12, 0.3), 0
  aout = (a1 + a2 * 0.35 * (0.5 + p7) + a3 * 0.12 * p7) * krel * p5 * 0.75 * (1 - gkDuck * p8)
  aL, aR pan2 aout, p6
  Out aL, aR, p9, p10
endin

; Chord stab
instr 46
  aenv expseg 0.001, 0.004, 1, 0.12 + p7 * 0.2, 0.001
  a1 vco2 1, p4
  a2 vco2 1, p4 * 1.007
  kcut expseg 400 + p7 * 5000, 0.15, 200 + p7 * 600
  af moogladder a1 + a2, kcut, 0.4
  aout = af * aenv * p5 * 0.8 * (1 - gkDuck * p8)
  aL, aR pan2 aout, p6
  Out aL, aR, p9, p10
endin

; Plucked string (Karplus-Strong waveguide)
instr 47
  xtratim 0.8
  astr wgpluck2 0.2 + (1 - p7) * 0.5, 1, p4, 0.1, 0.25 + p7 * 0.3
  krel linsegr 1, p3, 1, max(p12, 0.2), 0
  af butterlp astr, 1800 + p7 * 6000
  aout = af * krel * p5 * 2.7 * (1 - gkDuck * p8)
  aL, aR pan2 aout, p6
  Out aL, aR, p9, p10
endin

; Snare
instr 50
  aout = SnareCore(p6) * p4 * 0.8
  aL, aR pan2 aout, p5
  DrumOut aL, aR, p7
endin

; Rim click
instr 51
  aenv expseg 1, 0.025, 0.0005
  a1 poscil 1, 1700 + p6 * 800, giSine
  a2 poscil 1, 480, giSine
  anz rand 1
  abp butterbp anz, 3200, 2000
  aout = (a1 * 0.3 + a2 * 0.4 + abp * 0.6) * aenv * p4
  aL, aR pan2 aout, p5
  DrumOut aL, aR, p7
endin

; Shaker
instr 52
  aenv expseg 0.001, 0.012, 1, 0.05 + p6 * 0.08, 0.0005
  anz rand 1
  ahp butterhp anz, 6000
  abp butterbp ahp, 9000, 6000
  aout = abp * aenv * p4 * 1.2
  aL, aR pan2 aout, p5
  DrumOut aL, aR, p7
endin

; Soft kick with a rounded attack
instr 53
  kpitch expseg 110, 0.05, 52, 0.25, 45
  aenv expseg 1, 0.3, 0.0005
  abody poscil 1, kpitch, giSine
  af butterlp tanh(abody * aenv * 1.2), 900 + p6 * 1500
  aout = af * p4 * 0.85
  aL, aR pan2 aout, p5
  DrumOut aL, aR, p7
endin

; Tom: tone sets the pitch
instr 54
  ibase = 70 + p6 * 140
  kp expseg ibase * 1.6, 0.04, ibase, 0.4, ibase * 0.85
  aenv expseg 1, 0.45, 0.0005
  a1 poscil 1, kp, giSine
  anz rand 1
  anzenv expseg 1, 0.03, 0.001
  abp butterbp anz * anzenv, ibase * 6, ibase * 4
  aout = (tanh(a1 * aenv * 1.3) * 0.8 + abp * 0.3) * p4
  aL, aR pan2 aout, p5
  DrumOut aL, aR, p7
endin

; Crash: tone sets the length
instr 55
  aenv expseg 1, 1.2 + p6 * 2, 0.0005
  aout = CymbalCore() * aenv * p4 * 0.6
  aL, aR pan2 aout, p5
  DrumOut aL, aR, p7
endin

; Snare through a gated reverb
instr 57
  adry = SnareCore(p6) * p4 * 0.8
  aL, aR reverbsc adry, adry, 0.9, 7000
  kgate linseg 1, 0.22, 1, 0.04, 0, 1, 0
  aoutL, aoutR pan2 adry, p5
  outch 3, aoutL + aL * kgate * 0.9, 4, aoutR + aR * kgate * 0.9
endin

; Reverse cymbal ending on the next section: p4 amp
instr 58
  aenv expseg 0.001, p3 - 0.01, 1, 0.01, 0.001
  aout = CymbalCore() * aenv * p4 * 0.6
  Out aout, aout * 0.95, 0.25, 0
endin

; Vinyl crackle over a band-limited hiss: p4 amp, p6 crackle density
instr 60
  adL dust2 0.6, 7 + p6 * 20
  adR dust2 0.6, 7 + p6 * 20
  acL butterbp adL, 3000, 2500
  acR butterbp adR, 3000, 2500
  anz pinkish 1, 0, 20, 0.37
  ahiss butterbp anz, 5000, 6000
  aenv linsegr 0, 0.5, 1, 0.5, 0
  outch 1, (acL * 0.8 + ahiss * 0.04) * aenv * p4, 2, (acR * 0.8 + ahiss * 0.04) * aenv * p4
endin

; Ping-pong delay: p4 time, p5 feedback
instr 98
  afbL init 0
  afbR init 0
  ain = (gaDelL + gaDelR) * 0.5
  abufL delayr 2
  atapL deltapi p4
  delayw ain + afbR
  abufR delayr 2
  atapR deltapi p4
  delayw afbL
  afbL = butterlp(atapL, 4800) * p5
  afbR = butterlp(atapR, 4800) * p5
  outch 1, atapL * 0.55, 2, atapR * 0.55
  gaRevL = gaRevL + atapL * 0.2
  gaRevR = gaRevR + atapR * 0.2
  gaDelL = 0
  gaDelR = 0
endin

; Reverb: p4 feedback, p5 wet level
instr 99
  aL, aR reverbsc gaRevL, gaRevR, p4, 8500
  outch 1, aL * p5, 2, aR * p5
  gaRevL = 0
  gaRevR = 0
endin
