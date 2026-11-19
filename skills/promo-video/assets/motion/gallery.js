// SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
// SPDX-License-Identifier: MIT

// A playable catalog of every transition and effect in motion.js, following the page contract of
// scripts/render_frames.py. Snapshot it to compare effects before choosing them for a film.

import * as motion from './motion.js';

const FPS = 30;
const TRANSITION_SLOT = 3;
const EFFECT_SLOT = 3.6;
const params = new URLSearchParams(location.search);
const root = document.getElementById('stage');
const label = document.getElementById('label');
const tl = gsap.timeline({ paused: true });
const labels = [];

motion.registerPlugins();
await document.fonts.load('800 40px "Noto Sans SC Variable"', '实时与确定性同一平台完成控制就绪进程使命');
await document.fonts.load('800 40px "Inter Tight Variable"', 'Process Simulation AB');
await document.fonts.load('600 40px "JetBrains Mono Variable"', '0123456789.HzCONTROL READY just run::microduck-cmp');
await document.fonts.ready;
motion.seedRandom(2026);

function add(html, parent = root) {
  const template = document.createElement('template');
  template.innerHTML = html.trim();
  const node = template.content.firstElementChild;
  parent.appendChild(node);
  return node;
}

function slot(start, end, html) {
  const node = add(`<section class="scene">${html}</section>`);
  tl.fromTo(node, { autoAlpha: 0 }, { autoAlpha: 1, duration: .001, immediateRender: false }, start);
  tl.fromTo(node, { autoAlpha: 1 }, { autoAlpha: 0, duration: .001, immediateRender: false }, end);
  return node;
}

const transitions = [
  ['dissolve', {}, '叠化 · 同一段落内换镜头'],
  ['blurDissolve', {}, '模糊叠化 · 柔和的时间或地点变化'],
  ['wipe', { direction: 'right', edge: '#ec4a22' }, '擦除 · 带强调色边线，适合章节推进'],
  ['iris', { x: '70%', y: '45%' }, '圆形展开 · 从画面焦点打开下一段'],
  ['split', { axis: 'x' }, '对开 · 对比双方登场'],
  ['push', { direction: 'left' }, '推移 · 列表或步骤的下一项'],
  ['zoomThrough', {}, '穿越缩放 · 从概览进入细节'],
  ['band', { color: '#ec4a22', accent: '#f3f2ef' }, '斜向色带 · 品牌色转场，适合部分之间'],
  ['flash', {}, '闪白 · 与重击同拍的硬切'],
  ['glitch', {}, '故障切换 · 系统、信号与错误主题'],
  ['shapeMorph', { x: .3, y: .6 }, '形状变形 · 从一个点扩成整屏'],
  ['lineReveal', {}, '线条展开 · 线条画出后上下打开'],
];

let time = 0;
transitions.forEach(([name, options, purpose], index) => {
  const start = time, end = time + TRANSITION_SLOT;
  const a = add(`<section class="scene panel-a"><div class="letter">A</div><div class="caption">${purpose}</div></section>`);
  const b = add(`<section class="scene panel-b"><div class="letter">B</div><div class="caption" style="color:#ffd9cc">${purpose}</div></section>`);
  tl.fromTo(a, { autoAlpha: 0 }, { autoAlpha: 1, duration: .001, immediateRender: false }, start);
  motion.TRANSITIONS[name](tl, start + .9, a, b, options);
  tl.fromTo(b, { autoAlpha: 1 }, { autoAlpha: 0, duration: .001, immediateRender: false }, end);
  labels.push([start, end, `TRANSITION ${String(index + 1).padStart(2, '0')}/${transitions.length} · <b>${name}</b>`,
    JSON.stringify(options), name]);
  time = end;
});

const effects = [
  ['splitRise', '逐字遮罩上升 · 标题与关键句', start => {
    const node = slot(start, start + EFFECT_SLOT, '<div class="title">实时与确定</div>');
    motion.splitRise(tl, start + .4, node.querySelector('.title'), { type: 'chars', stagger: .06 });
  }],
  ['blurIn', '模糊聚焦 · 产品名与口号', start => {
    const node = slot(start, start + EFFECT_SLOT, '<div class="title" style="font-family:var(--sans)">Process Simulation</div>');
    motion.blurIn(tl, start + .4, node.querySelector('.title'), { stagger: .035 });
  }],
  ['typewriter', '打字机 · 命令与终端输出', start => {
    const node = slot(start, start + EFFECT_SLOT, '<div class="terminal"><span class="prompt">$ </span><span class="cmd">just run::microduck-cmp</span></div>');
    motion.typewriter(tl, start + .4, node.querySelector('.cmd'), { cps: 14 });
  }],
  ['scramble', '解码 · 状态切换、系统就绪', start => {
    const node = slot(start, start + EFFECT_SLOT, '<div class="big" style="font-size:150px">CONTROL READY</div>');
    motion.scramble(tl, start + .4, node.querySelector('.big'), { chars: 'XO01', duration: 1.8 });
  }],
  ['countUp', '数字滚动 · 实测数据揭示', start => {
    const node = slot(start, start + EFFECT_SLOT, '<div class="big">0.0 Hz</div>');
    motion.countUp(tl, start + .4, node.querySelector('.big'), { to: 101.5, decimals: 1, suffix: ' Hz', duration: 1.8 });
  }],
  ['draw', '描线 · 架构图、连线、流程', start => {
    const node = slot(start, start + EFFECT_SLOT, `<svg viewBox="0 0 1920 1080" style="position:absolute;inset:0">
      <g fill="none" stroke="#c9ced6" stroke-width="4"><rect class="d" x="260" y="420" width="380" height="220" rx="16"/>
      <rect class="d" x="770" y="420" width="380" height="220" rx="16" stroke="#ec4a22"/><rect class="d" x="1280" y="420" width="380" height="220" rx="16"/>
      <path class="d" d="M640 530 H770"/><path class="d" d="M1150 530 H1280"/><path class="d" d="M450 640 V760 H1470 V640" stroke-dasharray="0"/></g></svg>`);
    motion.draw(tl, start + .3, node.querySelectorAll('.d'), { stagger: .18 });
  }],
  ['flow', '路径流动 · 数据包、信号、能量', start => {
    const node = slot(start, start + EFFECT_SLOT, `<svg viewBox="0 0 1920 1080" style="position:absolute;inset:0">
      <path id="flow-path" d="M200 700 C600 300 1000 900 1720 380" fill="none" stroke="#3a3f47" stroke-width="4"/>
      ${[0, 1, 2, 3].map(i => `<circle class="dot" r="14" fill="${i % 2 ? '#63c6d8' : '#ffb020'}"/>`).join('')}</svg>`);
    motion.flow(tl, start + .3, node.querySelectorAll('.dot'), node.querySelector('#flow-path'), { duration: 1.4, until: start + EFFECT_SLOT, spacing: .35 });
  }],
  ['stack', '逐层叠起 · 分层架构、步骤', start => {
    const names = ['硬件平台', 'Hypervisor', 'Zephyr 实时域', 'Linux 域'];
    const node = slot(start, start + EFFECT_SLOT, names.map((name, i) =>
      `<div class="layer${i === 1 ? ' hot' : ''}" style="top:${760 - i * 140}px">${name}</div>`).join(''));
    motion.stack(tl, start + .3, node.querySelectorAll('.layer'), { stagger: .22 });
  }],
  ['gridReveal', '网格展开 · 功能列表、生态、合作方', start => {
    const tiles = Array.from({ length: 15 }, (_, i) => `<div class="tile" style="left:${370 + (i % 5) * 240}px;top:${280 + Math.floor(i / 5) * 180}px"></div>`);
    const node = slot(start, start + EFFECT_SLOT, `<div class="grid">${tiles.join('')}</div>`);
    motion.gridReveal(tl, start + .3, node.querySelectorAll('.tile'), { grid: [3, 5], from: 'center' });
  }],
  ['flipLayout', '布局变换 · 一排变两列、排序、分组', start => {
    const node = slot(start, start + EFFECT_SLOT, `<div class="flip-row">${['MuJoCo', 'XL330', 'QEMU', 'Zephyr'].map(name =>
      `<div class="card">${name}</div>`).join('')}</div>`);
    const row = node.querySelector('.flip-row');
    motion.flipLayout(tl, start + 1.2, row.querySelectorAll('.card'), () => row.classList.add('grid'), { duration: 1.2 });
  }],
  ['shine', '扫光 · 标志、卡片、结果强调', start => {
    const node = slot(start, start + EFFECT_SLOT, '<div class="card" style="left:560px;top:340px;width:800px;height:400px;font-size:80px">ProcessONE</div>');
    gsap.set(node.querySelector('.card'), { color: '#ec4a22' });
    motion.shine(tl, start + 1, node.querySelector('.card'), { duration: 1.1 });
  }],
  ['shake', '冲击抖动 · 推力、碰撞、报错', start => {
    const node = slot(start, start + EFFECT_SLOT, '<div class="card" style="left:760px;top:390px;width:400px;height:300px">4 N</div>');
    motion.shake(tl, start + 1, node.querySelector('.card'), { strength: 26, duration: .6 });
  }],
  ['drift', '缓推镜头 · 静态画面保持呼吸', start => {
    const node = slot(start, start + EFFECT_SLOT, '<div class="panel panel-b" style="position:absolute;inset:0"><div class="title" style="left:0;right:0;text-align:center">同一平台 同时运行</div></div>');
    motion.drift(tl, start, node.querySelector('.panel'), { duration: EFFECT_SLOT, scale: [1, 1.12] });
  }],
  ['parallax', '视差 · 多层背景的空间感', start => {
    const node = slot(start, start + EFFECT_SLOT, [1, 2, 3].map(depth => `<div class="layer-p" data-depth="${depth}" style="position:absolute;inset:0">
      ${Array.from({ length: 6 }, (_, i) => `<div style="position:absolute;left:${180 + i * 300}px;top:${220 + depth * 160}px;width:${40 * depth}px;height:${40 * depth}px;border-radius:50%;background:${depth === 3 ? '#ec4a22' : '#3a3f47'};opacity:${.3 * depth}"></div>`).join('')}</div>`).join(''));
    motion.parallax(tl, start, node.querySelectorAll('.layer-p'), { duration: EFFECT_SLOT, distance: 260 });
  }],
  ['morph', '形状变形 · 图标状态切换', start => {
    const node = slot(start, start + EFFECT_SLOT, `<svg viewBox="0 0 1920 1080" style="position:absolute;inset:0">
      <path id="morph-from" fill="#ec4a22" d="M960,340 a200,200 0 1,0 1,0 Z"/>
      <path id="morph-to" fill="none" d="M780,560 L900,680 L1150,400 L1200,450 L900,760 L730,610 Z"/></svg>`);
    motion.morph(tl, start + 1, node.querySelector('#morph-from'), node.querySelector('#morph-to'), { duration: 1.1 });
  }],
  ['bars', '柱状生长 · 指标对比', start => {
    const heights = [220, 340, 280, 460, 390, 520];
    const node = slot(start, start + EFFECT_SLOT, heights.map((h, i) => `<div class="bar" style="left:${520 + i * 160}px;height:${h}px"></div>`).join(''));
    motion.bars(tl, start + .3, node.querySelectorAll('.bar'), { stagger: .1 });
  }],
  ['outline', '圈注 · 指向画面中的关键数字', start => {
    const node = slot(start, start + EFFECT_SLOT, '<div class="card" style="left:660px;top:380px;width:600px;height:260px;font:700 120px/1 var(--mono);color:#ec4a22">1.57 s</div>');
    motion.outline(tl, start + .8, node.querySelector('.card'), { padding: 22 });
  }],
  ['drop', '物理抛落 · 散落、碰撞、释放', start => {
    const node = slot(start, start + EFFECT_SLOT, Array.from({ length: 14 }, () => '<div class="square"></div>').join(''));
    motion.drop(tl, start + .5, node.querySelectorAll('.square'), { duration: 2.2 });
  }],
];

effects.forEach(([name, purpose, build], index) => {
  const start = time, end = time + EFFECT_SLOT;
  build(start);
  labels.push([start, end, `EFFECT ${String(index + 1).padStart(2, '0')}/${effects.length} · <b>${name}</b>`, purpose, name]);
  time = end;
});

const DURATION = time;
let shown = -1;
function updateLabel(seconds) {
  const index = labels.findIndex(([a, b]) => seconds >= a && seconds < b);
  if (index === shown) return;
  shown = index;
  label.innerHTML = index < 0 ? '' : `${labels[index][2]}<small>${labels[index][3]}</small>`;
}

async function renderFrame(frame) {
  const seconds = frame / FPS;
  motion.renderAt(tl, seconds, 2026, frame);
  updateLabel(seconds);
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
}

window.FPS = FPS;
window.DURATION = DURATION;
window.renderFrame = renderFrame;
window.getCues = () => [];
window.getSubtitles = () => [];
window.motionCatalog = () => labels.map(([start, end, , note, name]) => ({ name, start, end, note }));
await renderFrame(params.has('t') ? Math.round(Number(params.get('t')) * FPS) : 0);
window.ready = true;
