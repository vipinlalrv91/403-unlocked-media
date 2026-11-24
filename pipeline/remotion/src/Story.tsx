// Kadha Petti story scene with ACTIONS (owner chose Remotion action scenes, 24 Nov 2026).
// Props come from pipeline/make_short.py (remotion_scene). Characters can enter, walk/run to new spots,
// switch to action poses (kneel, bow, bless, draw bow...), and exit. Lip sync + blink as in the Python renderer.
import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';

export type Face = {eyes: number[][]; eye_w: number; eye_h: number; mouth: number[]; mouth_w: number; skin: number[][]};
export type Pose = {src: string; w: number; h: number; face?: Face | null};
export type Move = {t: number; x?: number; pose?: string; dur?: number; h?: number};
export type Char = {label?: string; who: string; x: number; y: number; h: number; pose: string; poses: Record<string, Pose>;
  enter?: string; t0: number; moves?: Move[]; exit?: {t: number; to: string}; flip?: boolean};
export type Spec = {bg: string; seed: number; fx: string[]; caption?: string; segs: [number, number, string][]; amp: number[];
  chars: Char[]; delay: number};

const W = 1080, H = 1920;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = Easing.inOut(Easing.cubic);
const rnd = (i: number, s: number) => { const x = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return x - Math.floor(x); };

function speakerAt(segs: [number, number, string][], t: number) {
  for (const [a, b, w] of segs) if (t >= a && t <= b) return w; return null;
}

// position / pose / height of a character at time t
function state(c: Char, t: number) {
  let x = c.x, pose = c.pose, h = c.h, moving = 0, prevPose = c.pose, switchT = -10;
  for (const m of c.moves || []) {
    const d = m.dur ?? 1.0;
    if (t < m.t) break;
    const k = interpolate(t, [m.t, m.t + d], [0, 1], {...clamp, easing: ease});
    if (m.x !== undefined) { const nx = m.x; if (k < 1) moving = Math.abs(nx - x) > 0.01 ? 1 : 0; x = x + (nx - x) * k; }
    if (m.pose && m.pose !== pose) { const st = m.t + d * 0.75; if (t >= st) { prevPose = pose; pose = m.pose; switchT = st; } }
    if (m.h !== undefined && t >= m.t + d * 0.75) h = m.h;
  }
  return {x, pose, h, moving, prevPose, switchT};
}

const Sprite: React.FC<{c: Char; poseName: string; h: number; t: number; amp: number; speaking: boolean; n: number; opacity: number}> =
  ({c, poseName, h, t, amp, speaking, n, opacity}) => {
  const p = c.poses[poseName]; if (!p) return null;
  const base = c.poses[c.pose]; h = h * p.h / base.h;   // poses keep the character's scale (a kneel is shorter)
  const sc = h / p.h, w = p.w * sc; const f = p.face;
  const blink = (t + n * 0.83) % 3.6 < 0.14;
  const talk = speaking ? amp : 0;
  return (
    <div style={{position: 'absolute', left: -w / 2, top: -h, width: w, height: h, opacity, transform: c.flip ? 'scaleX(-1)' : undefined}}>
      <Img src={staticFile(p.src)} style={{width: w, height: h}} />
      {f && blink && f.eyes.map((e, i) => {
        const s = f.skin[i] || f.skin[0];
        return <div key={i} style={{position: 'absolute', left: (e[0] - f.eye_w / 2 - 3) * sc, top: (e[1] - f.eye_h / 2 - 3) * sc,
          width: (f.eye_w + 6) * sc, height: (f.eye_h + 6) * sc, borderRadius: '50%', background: `rgb(${s[0]},${s[1]},${s[2]})`,
          borderBottom: `${Math.max(2, 3 * sc)}px solid rgb(60,30,25)`}} />;
      })}
      {f && talk >= 0.06 && (() => {
        const mw = f.mouth_w * sc, mh = (4 + f.mouth_w * 0.75 * Math.min(1, talk * 1.4)) * sc;
        const mx = f.mouth[0] * sc, my = f.mouth[1] * sc;
        return <div style={{position: 'absolute', left: mx - mw / 2, top: my - mh / 2, width: mw, height: mh, borderRadius: '50%',
          background: 'rgb(95,25,35)', overflow: 'hidden'}}>
          <div style={{position: 'absolute', left: mw * 0.22, top: mh * 0.55, width: mw * 0.56, height: mh * 0.45, borderRadius: '50%', background: 'rgb(205,90,100)'}} />
        </div>;
      })()}
      {!f && speaking && <div style={{position: 'absolute', left: -w * 0.1, top: h * 0.05, width: w * 1.2, height: h * 0.7, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(255,230,150,0.55), rgba(255,230,150,0) 70%)', opacity: 0.5 + 0.5 * Math.sin(t * 9)}} />}
    </div>
  );
};

const FX: React.FC<{kinds: string[]; t: number; seed: number; front?: boolean}> = ({kinds, t, seed, front}) => {
  const out: React.ReactNode[] = []; const S = seed + (front ? 7 : 0);
  if (!front && kinds.includes('rays')) out.push(<div key="rays" style={{position: 'absolute', inset: 0, opacity: 0.75 + 0.25 * Math.sin(t * 0.7),
    background: 'linear-gradient(115deg, rgba(255,240,190,0) 18%, rgba(255,240,190,0.2) 30%, rgba(255,240,190,0) 40%, rgba(255,240,190,0.14) 52%, rgba(255,240,190,0) 62%)'}} />);
  if (!front && kinds.includes('mist')) out.push(<div key="mist" style={{position: 'absolute', left: -200 + (t * 25) % 200, right: -200, top: H * 0.55, height: 380,
    background: 'radial-gradient(ellipse at 50% 50%, rgba(255,255,255,0.18), rgba(255,255,255,0) 70%)', filter: 'blur(20px)'}} />);
  if (kinds.includes('petals') || kinds.includes('leaves')) {
    const petals = kinds.includes('petals'); const n = front ? 5 : 16; const sc = front ? 1.9 : 1;
    for (let i = 0; i < n; i++) {
      const sp = (70 + rnd(i, S) * 80) * sc, ph = rnd(i, S + 1) * 100;
      const y = ((t + ph) * sp) % (H + 200) - 100, x = rnd(i, S + 2) * (W + 100) - 50 + 70 * Math.sin((t + ph) * 1.1);
      const s = (20 + rnd(i, S + 3) * 22) * sc;
      const col = petals ? ['#ffb6cb', '#ffd6e2', '#fff0f5', '#ffc878'][i % 4] : ['#78aa3c', '#aabe46', '#d2aa3c', '#5a8c32'][i % 4];
      out.push(<div key={'p' + i} style={{position: 'absolute', left: x, top: y, width: s, height: s * (petals ? 0.55 : 0.4), borderRadius: '50%',
        background: col, opacity: 0.92, transform: `rotate(${(t + ph) * 70}deg)`, filter: front ? 'blur(3px)' : undefined}} />);
    }
  }
  const glow = (key: string, x: number, y: number, r: number, col: string, a: number) =>
    out.push(<div key={key} style={{position: 'absolute', left: x - r, top: y - r, width: 2 * r, height: 2 * r, borderRadius: '50%',
      background: `radial-gradient(circle, ${col}, rgba(0,0,0,0) 70%)`, opacity: a}} />);
  if (kinds.includes('fireflies')) for (let i = 0; i < (front ? 6 : 26); i++) {
    const ph = rnd(i, S) * 10, a = Math.max(0, Math.sin(t * 2.2 + ph)) ** 1.5;
    glow('f' + i, rnd(i, S + 1) * W + 50 * Math.sin(t * 0.6 + ph), 300 + rnd(i, S + 2) * (H - 600) + 35 * Math.sin(t * 0.8 + ph * 1.7), front ? 18 : 10, 'rgba(255,240,120,1)', a);
  }
  if (kinds.includes('dust')) for (let i = 0; i < (front ? 4 : 22); i++) {
    const ph = rnd(i, S) * 10, sp = 8 + rnd(i, S + 3) * 17;
    glow('d' + i, (rnd(i, S + 1) * W + t * sp + 30 * Math.sin(t * 0.5 + ph)) % W, ((rnd(i, S + 2) * H - t * sp * 0.6) % H + H) % H, front ? 14 : 7, 'rgba(255,225,150,1)', 0.35 + 0.35 * Math.sin(t * 1.3 + ph));
  }
  if (!front && kinds.includes('glints')) for (let i = 0; i < 30; i++) {
    const ph = rnd(i, S) * 10, a = Math.max(0, Math.sin(t * 3 + ph)) ** 6;
    glow('g' + i, rnd(i, S + 1) * W + 10 * Math.sin(t + ph), H * (0.55 + rnd(i, S + 2) * 0.3), 9, 'rgba(255,255,230,1)', a);
  }
  if (!front && kinds.includes('lampglow')) for (let i = 0; i < 6; i++) {
    const f = 0.7 + 0.3 * Math.sin(t * (5 + i) + i * 2.1);
    glow('l' + i, 80 + rnd(i, S) * (W - 160), 250 + rnd(i, S + 1) * 650, 44 * f, 'rgba(255,200,90,1)', 0.9);
  }
  return <>{out}</>;
};

export const Story: React.FC<Spec> = (sp) => {
  const f = useCurrentFrame(); const {fps, durationInFrames} = useVideoConfig(); const t = f / fps; const D = durationInFrames / fps;
  const dirx = rnd(1, sp.seed) > 0.5 ? 1 : -1, diry = Math.floor(rnd(2, sp.seed) * 3) - 1;
  const p = interpolate(t, [0, D], [0, 1], {...clamp, easing: ease});
  const zoom = 1 + 0.11 * p, px = dirx * 70 * (p - 0.5), py = diry * 25 * (p - 0.5);
  const who = speakerAt(sp.segs, t); const amp = sp.amp[Math.min(f, sp.amp.length - 1)] || 0;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <style>{`@font-face{font-family:ML;src:url(${staticFile('fonts/ml.ttf')});}`}</style>
      <AbsoluteFill style={{transform: `scale(${zoom}) translate(${-px}px, ${-py}px)`, transformOrigin: '50% 62%'}}>
        <Img src={staticFile('bg/' + sp.bg)} style={{position: 'absolute', height: H * 1.02, top: -H * 0.01, left: '50%', transform: 'translateX(-50%)'}} />
        <FX kinds={sp.fx} t={t} seed={sp.seed} />
        {sp.chars.map((c, n) => {
          const st = state(c, t); const lt = t - c.t0;
          let x = st.x * W, y = c.y * H, op = 1;
          // entrance
          if (c.enter === 'left' || c.enter === 'right') {
            const k = interpolate(lt, [0, 1.2], [1, 0], {...clamp, easing: Easing.out(Easing.cubic)});
            x += (c.enter === 'left' ? -1 : 1) * k * 700; if (k > 0) st.moving = 1;
          } else {
            op = interpolate(lt, [0, 0.5], [0, 1], clamp); y += 60 * interpolate(lt, [0, 0.7], [1, 0], {...clamp, easing: Easing.out(Easing.cubic)});
          }
          if (lt < 0) op = 0;
          // exit
          if (c.exit && t > c.exit.t) { const k = interpolate(t, [c.exit.t, c.exit.t + 1.2], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
            x += (c.exit.to === 'left' ? -1 : 1) * k * 800; st.moving = k < 1 ? 1 : 0; }
          // walking / running bob while moving; tiny breathing otherwise (owner: no extra body motion)
          const bob = st.moving ? Math.abs(Math.sin(t * 11 + n)) * 30 : 6 * Math.abs(Math.sin(t * 2 + n));
          // pose crossfade + soft drop when switching to a lower pose (kneel/bow)
          const cf = interpolate(t, [st.switchT, st.switchT + 0.3], [0, 1], clamp);
          const drop = st.switchT > 0 ? spring({frame: f - Math.round(st.switchT * fps), fps, config: {damping: 12, mass: 0.6}}) : 1;
          const speaking = who === c.who;
          return (
            <div key={n} style={{position: 'absolute', left: x, top: y - bob - (1 - drop) * 40, opacity: op}}>
              {speaking && amp > 0.15 && <div style={{position: 'absolute', left: -st.h * 0.42, top: -st.h * 0.97, width: st.h * 0.84, height: st.h * 0.84,
                borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,230,150,0.55), rgba(255,230,150,0) 70%)', opacity: Math.min(1, amp)}} />}
              {cf < 1 && st.switchT > 0 && <Sprite c={c} poseName={st.prevPose} h={c.h} t={t} amp={amp} speaking={speaking} n={n} opacity={1 - cf} />}
              <Sprite c={c} poseName={st.pose} h={st.h} t={t} amp={amp} speaking={speaking} n={n} opacity={st.switchT > 0 ? cf : 1} />
              {c.label && <div style={{position: 'absolute', top: bob + (1 - drop) * 40 + 6, left: 0, transform: 'translateX(-50%)', whiteSpace: 'nowrap',
                background: 'rgb(255,245,210)', border: '3px solid rgb(200,120,20)', borderRadius: 26, padding: '4px 15px',
                fontFamily: 'ML', fontSize: sp.chars.length >= 4 ? 32 : 40, color: 'rgb(90,40,20)'}}>{c.label}</div>}
            </div>
          );
        })}
      </AbsoluteFill>
      <FX kinds={sp.fx} t={t} seed={sp.seed} front />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(20,10,0,0.45) 100%)'}} />
      {sp.caption && <div style={{position: 'absolute', left: 60, right: 60, top: 1640, height: 200, borderRadius: 50, background: '#fff',
        border: '6px solid rgb(255,150,40)', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center',
        fontFamily: 'ML', fontSize: 60, color: 'rgb(60,40,90)', whiteSpace: 'nowrap'}}>{sp.caption}</div>}
    </AbsoluteFill>
  );
};
