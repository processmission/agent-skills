// SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
// SPDX-License-Identifier: MIT

// Composable GSAP transitions and effects for frame-exact video pages.
// Every function adds tweens to a paused master timeline `tl` at time `at` (seconds) and returns the end time.
// Transitions take the outgoing and incoming scene elements; effects take their targets.
// fromTo() lists every animated property on both ends: GSAP only tweens properties named in the to-vars, so a
// property given only in the from-vars would depend on which frames were rendered before.
// Load GSAP and the plugins as UMD scripts (node_modules/gsap/dist/*.min.js) before importing this module.

const gsap = window.gsap;
const PLUGINS = ['SplitText', 'DrawSVGPlugin', 'MorphSVGPlugin', 'MotionPathPlugin', 'ScrambleTextPlugin', 'TextPlugin',
  'CustomEase', 'CustomWiggle', 'CustomBounce', 'Flip', 'Physics2DPlugin', 'RoughEase', 'SlowMo', 'ExpoScaleEase'];
const SVG = 'http://www.w3.org/2000/svg';

export function registerPlugins() {
  const found = PLUGINS.filter(name => window[name]);
  gsap.registerPlugin(...found.map(name => window[name]));
  return found;
}

// Deterministic randomness: seed once before building scenes, and again from the frame number before every render.
export function mulberry32(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6D2B79F5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function hash(...values) {
  let h = 2166136261;
  for (const value of values) {
    h ^= Math.round(Number(value) * 1000) | 0;
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export function seedRandom(...values) {
  Math.random = mulberry32(hash(...values));
}

// Ease personalities: pick one per film so motion has a consistent character, then vary per scene.
export const PERSONALITIES = {
  precise: { enter: 'power3.out', exit: 'power2.in', move: 'power3.inOut', settle: 'expo.out' },
  energetic: { enter: 'back.out(1.5)', exit: 'power3.in', move: 'expo.inOut', settle: 'back.out(2.2)' },
  calm: { enter: 'sine.out', exit: 'sine.in', move: 'sine.inOut', settle: 'power1.out' },
  playful: { enter: 'elastic.out(1, .55)', exit: 'back.in(1.6)', move: 'power2.inOut', settle: 'bounce.out' },
};
let style = PERSONALITIES.precise;

export function usePersonality(name) {
  style = typeof name === 'string' ? PERSONALITIES[name] : { ...style, ...name };
  return style;
}

export function beats(count, bpm) {
  return count * 60 / bpm;
}

function stage() {
  return document.getElementById('stage');
}

function size() {
  const root = stage();
  return { width: root.offsetWidth, height: root.offsetHeight };
}

function list(targets) {
  return gsap.utils.toArray(targets);
}

function overlay(name) {
  const node = document.createElement('div');
  node.className = `motion-overlay motion-${name}`;
  Object.assign(node.style, { position: 'absolute', inset: '0', pointerEvents: 'none', zIndex: '50', visibility: 'hidden' });
  stage().appendChild(node);
  return node;
}

function svgOverlay(name, parent = stage()) {
  const { width, height } = size();
  const node = document.createElementNS(SVG, 'svg');
  node.setAttribute('class', `motion-overlay motion-${name}`);
  node.setAttribute('viewBox', `0 0 ${width} ${height}`);
  Object.assign(node.style, { position: 'absolute', inset: '0', width: '100%', height: '100%', pointerEvents: 'none',
    zIndex: '50', overflow: 'visible' });
  parent.appendChild(node);
  return node;
}

function enter(tl, at, scene) {
  if (scene) tl.fromTo(scene, { autoAlpha: 0 }, { autoAlpha: 1, duration: .001, immediateRender: false }, at);
}

function leave(tl, at, scene) {
  if (scene) tl.fromTo(scene, { autoAlpha: 1 }, { autoAlpha: 0, duration: .001, immediateRender: false }, at);
}

// Offset of an element inside the stage, ignoring transforms that entrance tweens apply at build time.
function stageBox(element) {
  const root = stage();
  let x = 0, y = 0, node = element;
  while (node && node !== root) {
    x += node.offsetLeft;
    y += node.offsetTop;
    node = node.offsetParent;
  }
  return { x, y, width: element.offsetWidth, height: element.offsetHeight };
}

/* ---------- Scene transitions: (tl, at, from, to, options) ---------- */

export function dissolve(tl, at, from, to, { duration = .6, ease = 'power1.inOut' } = {}) {
  tl.fromTo(to, { autoAlpha: 0 }, { autoAlpha: 1, duration, ease, immediateRender: false }, at);
  if (from) tl.fromTo(from, { autoAlpha: 1 }, { autoAlpha: 0, duration, ease, immediateRender: false }, at);
  return at + duration;
}

export function blurDissolve(tl, at, from, to, { duration = .8, blur = 14, ease = 'power2.inOut' } = {}) {
  tl.fromTo(to, { autoAlpha: 0, filter: `blur(${blur}px)` },
    { autoAlpha: 1, filter: 'blur(0px)', duration, ease, immediateRender: false }, at);
  if (from) {
    tl.fromTo(from, { autoAlpha: 1, filter: 'blur(0px)' },
      { autoAlpha: 0, filter: `blur(${blur}px)`, duration, ease, immediateRender: false }, at);
  }
  return at + duration;
}

const INSETS = { right: ['0% 100% 0% 0%'], left: ['0% 0% 0% 100%'], down: ['0% 0% 100% 0%'], up: ['100% 0% 0% 0%'] };

export function wipe(tl, at, from, to, { direction = 'right', duration = .8, ease = style.move, edge = null } = {}) {
  enter(tl, at, to);
  tl.fromTo(to, { clipPath: `inset(${INSETS[direction][0]})` },
    { clipPath: 'inset(0% 0% 0% 0%)', duration, ease, immediateRender: false }, at);
  if (edge) {
    const { width, height } = size();
    const line = overlay('wipe-edge');
    const vertical = direction === 'left' || direction === 'right';
    Object.assign(line.style, vertical ? { width: '4px', inset: '0 auto 0 0' } : { height: '4px', inset: '0 0 auto 0' },
      { background: edge, boxShadow: `0 0 24px ${edge}` });
    const span = vertical ? width : height;
    const [a, b] = direction === 'right' || direction === 'down' ? [0, span] : [span, 0];
    const axis = vertical ? 'x' : 'y';
    tl.fromTo(line, { autoAlpha: 1, [axis]: a }, { autoAlpha: 1, [axis]: b, duration, ease, immediateRender: false }, at);
    tl.fromTo(line, { autoAlpha: 1 }, { autoAlpha: 0, duration: .15, immediateRender: false }, at + duration);
  }
  leave(tl, at + duration, from);
  return at + duration;
}

export function iris(tl, at, from, to, { x = '50%', y = '50%', duration = .9, ease = 'power2.inOut' } = {}) {
  enter(tl, at, to);
  tl.fromTo(to, { clipPath: `circle(0% at ${x} ${y})` },
    { clipPath: `circle(150% at ${x} ${y})`, duration, ease, immediateRender: false }, at);
  leave(tl, at + duration, from);
  return at + duration;
}

export function split(tl, at, from, to, { axis = 'x', duration = .8, ease = style.move } = {}) {
  enter(tl, at, to);
  const closed = axis === 'x' ? 'inset(0% 50% 0% 50%)' : 'inset(50% 0% 50% 0%)';
  tl.fromTo(to, { clipPath: closed }, { clipPath: 'inset(0% 0% 0% 0%)', duration, ease, immediateRender: false }, at);
  if (from) tl.fromTo(from, { scale: 1, filter: 'brightness(1)' },
    { scale: .94, filter: 'brightness(.5)', duration, ease, immediateRender: false }, at);
  leave(tl, at + duration, from);
  return at + duration;
}

export function push(tl, at, from, to, { direction = 'left', duration = .8, ease = style.move } = {}) {
  const axis = direction === 'left' || direction === 'right' ? 'xPercent' : 'yPercent';
  const sign = direction === 'left' || direction === 'up' ? -1 : 1;
  enter(tl, at, to);
  tl.fromTo(to, { [axis]: -100 * sign }, { [axis]: 0, duration, ease, immediateRender: false }, at);
  if (from) tl.fromTo(from, { [axis]: 0 }, { [axis]: 100 * sign, duration, ease, immediateRender: false }, at);
  leave(tl, at + duration, from);
  return at + duration;
}

export function zoomThrough(tl, at, from, to, { duration = .9, depth = .4, blur = 12, ease = 'power2.inOut' } = {}) {
  if (from) {
    tl.fromTo(from, { scale: 1, autoAlpha: 1, filter: 'blur(0px)' },
      { scale: 1 + depth, autoAlpha: 0, filter: `blur(${blur}px)`, duration, ease, immediateRender: false }, at);
  }
  tl.fromTo(to, { scale: 1 - depth / 3, autoAlpha: 0, filter: `blur(${blur}px)` },
    { scale: 1, autoAlpha: 1, filter: 'blur(0px)', duration, ease, immediateRender: false }, at + duration * .25);
  return at + duration * 1.25;
}

export function band(tl, at, from, to, { color = '#ec4a22', accent = null, angle = -18, duration = 1, ease = 'power3' } = {}) {
  const { width } = size();
  const layers = [color, accent].filter(Boolean).map((fill, index) => {
    const node = overlay(`band-${index}`);
    Object.assign(node.style, { inset: '-20% auto -20% 0', width: `${width * 1.5}px`, background: fill, transformOrigin: '50% 50%' });
    gsap.set(node, { skewX: angle });
    return node;
  });
  const half = duration / 2;
  layers.forEach((node, index) => {
    const offset = index * .07;
    tl.fromTo(node, { autoAlpha: 1, x: -width * 1.9 }, { autoAlpha: 1, x: -width * .25, duration: half, ease: `${ease}.in`, immediateRender: false }, at + offset);
    tl.fromTo(node, { x: -width * .25 }, { x: width * 1.25, duration: half, ease: `${ease}.out`, immediateRender: false }, at + half + offset);
    tl.fromTo(node, { autoAlpha: 1 }, { autoAlpha: 0, duration: .001, immediateRender: false }, at + duration + offset);
  });
  enter(tl, at + half, to);
  leave(tl, at + half, from);
  return at + duration + (layers.length - 1) * .07;
}

export function flash(tl, at, from, to, { color = '#ffffff', peak = .08, fade = .45, punch = .04 } = {}) {
  const node = overlay('flash');
  node.style.background = color;
  tl.fromTo(node, { autoAlpha: 0 }, { autoAlpha: 1, duration: peak, ease: 'power2.in', immediateRender: false }, at);
  enter(tl, at + peak, to);
  leave(tl, at + peak, from);
  if (punch) tl.fromTo(to, { scale: 1 + punch }, { scale: 1, duration: fade + .2, ease: 'power3.out', immediateRender: false }, at + peak);
  tl.fromTo(node, { autoAlpha: 1 }, { autoAlpha: 0, duration: fade, ease: 'power2.out', immediateRender: false }, at + peak);
  return at + peak + fade;
}

export function glitch(tl, at, from, to, { duration = .45, steps = 9, offset = 28, seed = 7 } = {}) {
  const proxy = { progress: 0 };
  const apply = () => {
    const p = proxy.progress;
    const step = Math.min(steps - 1, Math.floor(p * steps));
    const random = mulberry32(hash(seed, step));
    const showNew = p >= 1 || (p > 0 && random() < p * 1.2);
    const active = p > 0 && p < 1;
    const top = Math.round(random() * 70), bottom = Math.round(random() * (90 - top));
    for (const [scene, visible] of [[from, !showNew], [to, showNew]]) {
      if (!scene) continue;
      scene.style.visibility = visible ? 'inherit' : 'hidden';
      scene.style.opacity = visible ? '1' : '0';
      scene.style.transform = active && visible ? `translateX(${((random() - .5) * 2 * offset).toFixed(1)}px)` : '';
      scene.style.clipPath = active && visible && random() < .5 ? `inset(${top}% 0% ${bottom}% 0%)` : '';
      scene.style.filter = active && visible ? `hue-rotate(${Math.round(random() * 90)}deg) saturate(1.6)` : '';
    }
  };
  tl.fromTo(proxy, { progress: 0 }, { progress: 1, duration, ease: 'none', immediateRender: false, onUpdate: apply,
    onComplete: apply, onReverseComplete: apply }, at);
  return at + duration;
}

export function shapeMorph(tl, at, from, to, { color = '#ec4a22', duration = 1.1, x = .5, y = .5, ease = 'power3' } = {}) {
  const { width, height } = size();
  const layer = svgOverlay('shape');
  const path = document.createElementNS(SVG, 'path');
  const cx = width * x, cy = height * y, r = Math.min(width, height) * .04;
  const dot = `M${cx - r},${cy} a${r},${r} 0 1,0 ${2 * r},0 a${r},${r} 0 1,0 ${-2 * r},0 Z`;
  const full = `M${-width * .1},${-height * .1} H${width * 1.1} V${height * 1.1} H${-width * .1} Z`;
  const slit = `M${-width * .1},${cy - 2} H${width * 1.1} V${cy + 2} H${-width * .1} Z`;
  path.setAttribute('d', dot);
  path.setAttribute('fill', color);
  layer.appendChild(path);
  gsap.set(layer, { autoAlpha: 0 });
  const half = duration / 2;
  tl.fromTo(layer, { autoAlpha: 0 }, { autoAlpha: 1, duration: .001, immediateRender: false }, at);
  tl.fromTo(path, { morphSVG: dot }, { morphSVG: full, duration: half, ease: `${ease}.in`, immediateRender: false }, at);
  enter(tl, at + half, to);
  leave(tl, at + half, from);
  tl.fromTo(path, { morphSVG: full }, { morphSVG: slit, duration: half, ease: `${ease}.out`, immediateRender: false }, at + half);
  tl.fromTo(layer, { autoAlpha: 1 }, { autoAlpha: 0, duration: .12, immediateRender: false }, at + duration);
  return at + duration;
}

export function lineReveal(tl, at, from, to, { color = '#ec4a22', duration = 1, ease = style.move } = {}) {
  const { width, height } = size();
  const layer = svgOverlay('line');
  const line = document.createElementNS(SVG, 'path');
  line.setAttribute('d', `M0,${height / 2} H${width}`);
  Object.entries({ stroke: color, 'stroke-width': 4, fill: 'none' }).forEach(([key, value]) => line.setAttribute(key, value));
  layer.appendChild(line);
  const draw = duration * .45;
  tl.fromTo(line, { drawSVG: '0% 0%', autoAlpha: 1 }, { drawSVG: '0% 100%', autoAlpha: 1, duration: draw, ease: 'power2.inOut', immediateRender: true }, at);
  enter(tl, at + draw, to);
  tl.fromTo(to, { clipPath: 'inset(50% 0% 50% 0%)' },
    { clipPath: 'inset(0% 0% 0% 0%)', duration: duration - draw, ease, immediateRender: false }, at + draw);
  tl.fromTo(line, { autoAlpha: 1 }, { autoAlpha: 0, duration: .25, immediateRender: false }, at + duration - .1);
  leave(tl, at + duration, from);
  return at + duration;
}

export const TRANSITIONS = { dissolve, blurDissolve, wipe, iris, split, push, zoomThrough, band, flash, glitch, shapeMorph, lineReveal };

/* ---------- Effects: (tl, at, targets, options) ---------- */

function splitUnits(element, type, mask) {
  const parts = SplitText.create(element, { type: type === 'lines' ? 'lines' : `${type}`, mask: mask ? type : undefined,
    aria: 'none' });
  return parts[type];
}

export function splitRise(tl, at, element, { type = 'chars', stagger = .035, duration = .8, ease = style.enter, mask = true, from = 'start' } = {}) {
  const units = splitUnits(element, type, mask);
  tl.fromTo(units, { yPercent: 110, autoAlpha: mask ? 1 : 0 },
    { yPercent: 0, autoAlpha: 1, duration, ease, stagger: { each: stagger, from }, immediateRender: true }, at);
  return at + duration + stagger * (units.length - 1);
}

export function blurIn(tl, at, element, { type = 'chars', stagger = .04, duration = .9, blur = 12, from = 'center', ease = style.settle } = {}) {
  const units = splitUnits(element, type, false);
  tl.fromTo(units, { autoAlpha: 0, filter: `blur(${blur}px)`, scale: 1.25 },
    { autoAlpha: 1, filter: 'blur(0px)', scale: 1, duration, ease, stagger: { each: stagger, from }, immediateRender: true }, at);
  return at + duration + stagger * (units.length - 1);
}

export function typewriter(tl, at, element, { text = element.textContent, cps = 22, cursor = true, hold = 1.2 } = {}) {
  const duration = text.length / cps;
  element.textContent = '';
  tl.fromTo(element, { text: '' }, { text: { value: text }, duration, ease: 'none', immediateRender: true }, at);
  if (cursor) {
    const caret = document.createElement('span');
    caret.className = 'motion-caret';
    caret.textContent = '▍';
    element.insertAdjacentElement('afterend', caret);
    const blinks = Math.max(1, Math.round(hold / .5));
    tl.fromTo(caret, { autoAlpha: 0 }, { autoAlpha: 1, duration: .001, immediateRender: true }, at);
    tl.fromTo(caret, { autoAlpha: 1 }, { autoAlpha: 0, duration: .5, ease: 'steps(1)', repeat: blinks, yoyo: true, immediateRender: false },
      at + duration);
  }
  return at + duration;
}

// speed 1 refreshes the scrambled characters on every render. ScrambleText chains each refresh off the previous one,
// so renderAt() re-initialises active scrambles from the frame seed; named pools become explicit strings because the
// plugin builds its named pools from unseeded randomness when it loads.
const CHAR_POOLS = { upperCase: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', lowerCase: 'abcdefghijklmnopqrstuvwxyz' };
CHAR_POOLS.upperAndLowerCase = CHAR_POOLS.upperCase + CHAR_POOLS.lowerCase;
const scrambles = [];

export function scramble(tl, at, element, { text = element.textContent, chars = 'upperCase', duration = 1.4, revealDelay = .35 } = {}) {
  element.textContent = '';
  const tween = gsap.to(element, { scrambleText: { text, chars: CHAR_POOLS[chars] || chars, revealDelay, speed: 1 },
    duration, ease: 'none' });
  tl.add(tween, at);
  scrambles.push({ tween, element, original: '' });
  return at + duration;
}

// Render the master timeline at `seconds` with frame-seeded randomness; use this inside window.renderFrame.
export function renderAt(tl, seconds, ...seed) {
  if (Math.abs(tl.time() - seconds) < 1e-9) tl.time(seconds + 1e-4, true);
  for (const item of scrambles) {
    const start = item.tween.startTime();
    if (seconds >= start && seconds <= start + item.tween.duration()) {
      item.element.textContent = item.original;
      item.tween.invalidate();
    }
  }
  seedRandom(...seed);
  tl.time(seconds, false);
}

export function countUp(tl, at, element, { to, from = 0, decimals = 0, duration = 1.4, ease = 'power2.out', prefix = '', suffix = '', group = false } = {}) {
  const format = value => {
    const fixed = Number(value).toFixed(decimals);
    const text = group ? Number(fixed).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) : fixed;
    return `${prefix}${text}${suffix}`;
  };
  const proxy = { value: from };
  const write = () => { element.textContent = format(proxy.value); };
  write();
  tl.fromTo(proxy, { value: from }, { value: to, duration, ease, immediateRender: false, onUpdate: write, onComplete: write,
    onReverseComplete: write }, at);
  return at + duration;
}

export function draw(tl, at, paths, { duration = 1.1, stagger = .12, ease = 'power2.inOut', from = 'start', reverse = false } = {}) {
  const items = list(paths);
  tl.fromTo(items, { drawSVG: reverse ? '100% 100%' : '0% 0%' },
    { drawSVG: '0% 100%', duration, ease, stagger: { each: stagger, from }, immediateRender: true }, at);
  return at + duration + stagger * (items.length - 1);
}

export function flow(tl, at, dots, path, { duration = 1.6, until = at + 4, spacing = .4, autoRotate = false, fade = .2 } = {}) {
  const items = list(dots);
  items.forEach((dot, index) => {
    const start = at + index * spacing;
    const repeat = Math.max(0, Math.floor((until - start) / duration) - 1);
    tl.fromTo(dot, { autoAlpha: 0 }, { autoAlpha: 1, duration: fade, immediateRender: true }, start);
    tl.to(dot, { motionPath: { path, align: path, alignOrigin: [.5, .5], autoRotate }, duration, ease: 'none', repeat,
      immediateRender: true }, start);
  });
  return until;
}

export function stack(tl, at, items, { direction = 'up', distance = 70, stagger = .12, duration = .75, ease = style.settle } = {}) {
  const axis = direction === 'up' || direction === 'down' ? 'y' : 'x';
  const sign = direction === 'up' || direction === 'left' ? 1 : -1;
  const targets = list(items);
  tl.fromTo(targets, { [axis]: distance * sign, autoAlpha: 0 },
    { [axis]: 0, autoAlpha: 1, duration, ease, stagger, immediateRender: true }, at);
  return at + duration + stagger * (targets.length - 1);
}

export function gridReveal(tl, at, items, { from = 'center', grid = 'auto', amount = .7, duration = .6, scale = .5, ease = style.enter } = {}) {
  const targets = list(items);
  tl.fromTo(targets, { scale, autoAlpha: 0 },
    { scale: 1, autoAlpha: 1, duration, ease, stagger: { amount, from, grid }, immediateRender: true }, at);
  return at + duration + amount;
}

// `change` mutates the DOM (reorder, classes, parents); Flip animates from the old layout to the new one.
export function flipLayout(tl, at, targets, change, { duration = 1, ease = style.move, absolute = true, stagger = .04 } = {}) {
  const state = Flip.getState(list(targets));
  change();
  tl.add(Flip.from(state, { duration, ease, absolute, stagger }), at);
  return at + duration + stagger * (list(targets).length - 1);
}

export function shine(tl, at, element, { duration = .9, color = 'rgba(255,255,255,.55)', width = 28, angle = 20 } = {}) {
  gsap.set(element, { position: 'relative', overflow: 'hidden' });
  const glare = document.createElement('span');
  glare.className = 'motion-shine';
  Object.assign(glare.style, { position: 'absolute', top: '-30%', bottom: '-30%', left: '0', width: `${width}%`, pointerEvents: 'none',
    background: `linear-gradient(90deg, transparent, ${color}, transparent)` });
  element.appendChild(glare);
  gsap.set(glare, { skewX: -angle, xPercent: -150 });
  tl.fromTo(glare, { xPercent: -150 }, { xPercent: 100 * (100 / width) + 50, duration, ease: 'power2.inOut', immediateRender: false }, at);
  return at + duration;
}

export function shake(tl, at, element, { strength = 16, duration = .5, wiggles = 7, axis = 'x' } = {}) {
  const name = `motion-shake-${wiggles}`;
  const ease = CustomEase.get(name) || CustomWiggle.create(name, { wiggles, type: 'easeOut' });
  tl.fromTo(element, { [axis]: 0 }, { [axis]: strength, duration, ease, immediateRender: false }, at);
  return at + duration;
}

export function drift(tl, at, element, { duration = 6, scale = [1, 1.06], x = [0, 0], y = [0, 0], ease = 'none' } = {}) {
  tl.fromTo(element, { scale: scale[0], x: x[0], y: y[0] }, { scale: scale[1], x: x[1], y: y[1], duration, ease, immediateRender: true }, at);
  return at + duration;
}

export function parallax(tl, at, layers, { duration = 6, distance = 160, ease = 'sine.inOut' } = {}) {
  list(layers).forEach(layer => {
    const depth = Number(layer.dataset.depth || 1);
    tl.fromTo(layer, { x: distance * depth / 2 }, { x: -distance * depth / 2, duration, ease, immediateRender: true }, at);
  });
  return at + duration;
}

export function morph(tl, at, path, shape, { duration = .9, ease = style.move, type = 'rotational' } = {}) {
  tl.to(path, { morphSVG: { shape, type }, duration, ease }, at);
  return at + duration;
}

export function bars(tl, at, items, { axis = 'y', stagger = .08, duration = .9, ease = 'power3.out' } = {}) {
  const prop = axis === 'y' ? 'scaleY' : 'scaleX';
  const origin = axis === 'y' ? '50% 100%' : '0% 50%';
  const targets = list(items);
  gsap.set(targets, { transformOrigin: origin });
  tl.fromTo(targets, { [prop]: 0 }, { [prop]: 1, duration, ease, stagger, immediateRender: true }, at);
  return at + duration + stagger * (targets.length - 1);
}

export function outline(tl, at, element, { color = '#ec4a22', padding = 12, radius = 12, stroke = 3, duration = .8, ease = 'power2.inOut' } = {}) {
  const box = stageBox(element);
  // Mounted in the element's scene, so the outline disappears with the scene.
  const layer = svgOverlay('outline', element.closest('.scene') || stage());
  const rect = document.createElementNS(SVG, 'rect');
  Object.entries({ x: box.x - padding, y: box.y - padding, width: box.width + padding * 2, height: box.height + padding * 2,
    rx: radius, fill: 'none', stroke: color, 'stroke-width': stroke }).forEach(([key, value]) => rect.setAttribute(key, value));
  layer.appendChild(rect);
  tl.fromTo(rect, { drawSVG: '0% 0%' }, { drawSVG: '0% 100%', duration, ease, immediateRender: true }, at);
  return at + duration;
}

export function drop(tl, at, items, { velocity = [380, 620], angle = [-110, -70], gravity = 1100, duration = 1.6, stagger = .05 } = {}) {
  const targets = list(items);
  targets.forEach((item, index) => {
    tl.to(item, { physics2D: { velocity: gsap.utils.interpolate(velocity[0], velocity[1], Math.random()),
      angle: gsap.utils.interpolate(angle[0], angle[1], Math.random()), gravity }, duration, ease: 'none' }, at + index * stagger);
  });
  return at + duration + stagger * (targets.length - 1);
}

export const EFFECTS = { splitRise, blurIn, typewriter, scramble, countUp, draw, flow, stack, gridReveal, flipLayout, shine, shake,
  drift, parallax, morph, bars, outline, drop };
