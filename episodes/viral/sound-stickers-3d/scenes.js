export default (kit) => {
  const { O, room, cam, drift, prog, ease, lerp, clamp, clay, metal, glow, box, rbox, sphere, cyl, torus, panel, sign, spill, motes } = kit;
  const G = '#39ff88';
  const COLS = ['#ffcf3f', '#ff7a59', '#7ad3ff', '#c792ff', '#8cf08a', '#ff9bd2'];
  // a cartoon sticker face (no real people): round face, eyes, mouth variant + green sound badge
  const face = (x, cx, cy, r, i) => {
    x.fillStyle = COLS[i % COLS.length]; x.beginPath(); x.arc(cx, cy, r, 0, 7); x.fill();
    x.fillStyle = '#1b1b1b';
    const v = i % 4;
    if (v === 1) { x.lineWidth = r * 0.12; x.strokeStyle = '#1b1b1b'; x.beginPath(); x.arc(cx - r * 0.35, cy - r * 0.15, r * 0.14, Math.PI, 0); x.stroke(); x.beginPath(); x.arc(cx + r * 0.35, cy - r * 0.15, r * 0.14, Math.PI, 0); x.stroke(); }
    else { x.beginPath(); x.arc(cx - r * 0.35, cy - r * 0.15, r * (v === 2 ? 0.2 : 0.12), 0, 7); x.arc(cx + r * 0.35, cy - r * 0.15, r * (v === 2 ? 0.2 : 0.12), 0, 7); x.fill(); }
    x.beginPath();
    if (v === 2) { x.ellipse(cx, cy + r * 0.4, r * 0.18, r * 0.24, 0, 0, 7); x.fill(); }
    else if (v === 3) { x.lineWidth = r * 0.1; x.strokeStyle = '#1b1b1b'; x.moveTo(cx - r * 0.35, cy + r * 0.42); x.lineTo(cx + r * 0.35, cy + r * 0.3); x.stroke(); }
    else { x.arc(cx, cy + r * 0.2, r * 0.42, 0.15, Math.PI - 0.15); x.fill(); x.fillStyle = '#ff5d73'; x.beginPath(); x.arc(cx, cy + r * 0.48, r * 0.15, 0, Math.PI); x.fill(); }
  };
  const badge = (x, cx, cy, r, on) => {
    x.fillStyle = '#0f3b25'; x.beginPath(); x.arc(cx, cy, r, 0, 7); x.fill();
    x.strokeStyle = on ? G : '#8fb8a0'; x.lineWidth = r * 0.18; x.lineCap = 'round';
    [-0.5, -0.17, 0.17, 0.5].forEach((o, j) => { const hh = r * [0.3, 0.6, 0.45, 0.25][j]; x.beginPath(); x.moveTo(cx + o * r, cy - hh); x.lineTo(cx + o * r, cy + hh); x.stroke(); });
  };
  const sticker = (x, w, h, i, on) => {
    x.clearRect(0, 0, w, h);
    x.fillStyle = '#ffffff'; x.beginPath(); x.roundRect(w * 0.04, h * 0.04, w * 0.92, h * 0.92, w * 0.14); x.fill();
    face(x, w * 0.5, h * 0.52, w * 0.36, i); badge(x, w * 0.2, h * 0.2, w * 0.13, on);
  };
  const chat = (x, w, h, title, n, opts = {}) => {
    x.fillStyle = '#0b1410'; x.fillRect(0, 0, w, h);
    x.fillStyle = '#16251d'; x.fillRect(0, 0, w, h * 0.11);
    x.fillStyle = '#e8f1ec'; x.font = `700 ${w * 0.07}px Inter`; x.textBaseline = 'middle'; x.fillText(title, w * 0.2, h * 0.06);
    x.fillStyle = G; x.beginPath(); x.arc(w * 0.1, h * 0.06, w * 0.05, 0, 7); x.fill();
    for (let i = 0; i < n; i++) {
      const col = i % 2, row = Math.floor(i / 2), s = w * 0.36;
      const sx = col ? w * 0.56 : w * 0.08, sy = h * 0.15 + row * (s + h * 0.03);
      if (sy + s > h * 0.9) break;
      x.save(); x.translate(sx, sy);
      x.fillStyle = col ? '#1f6b45' : '#1d2a23'; x.beginPath(); x.roundRect(-w * 0.02, -w * 0.02, s + w * 0.04, s + w * 0.04, w * 0.04); x.fill();
      x.fillStyle = '#fff'; x.beginPath(); x.roundRect(0, 0, s, s, w * 0.05); x.fill();
      face(x, s / 2, s * 0.53, s * 0.36, i + 1); badge(x, s * 0.2, s * 0.2, s * 0.12, opts.lit === i);
      x.restore();
    }
    x.fillStyle = '#16251d'; x.beginPath(); x.roundRect(w * 0.05, h * 0.92, w * 0.9, h * 0.06, w * 0.05); x.fill();
  };
  const rings = (g, n, x, y, z) => Array.from({ length: n }, () => { const r = torus(g, 0.32, 0.012, glow(G, 1.1), x, y, z); r.material.transparent = true; return r; });
  const pulse = (rs, t, on, speed = 1.1, grow = 2.6) => rs.forEach((r, i) => { const p = (t * speed + i / rs.length) % 1; r.scale.setScalar(on ? 0.6 + p * grow : 0.001); r.material.opacity = on ? (1 - p) : 0; });
  const darkroom = (g) => { if (kit.bloom) kit.bloom.strength = 0.45; const r = room(g, 'ink', { keyPower: 55, fillPower: 0.9, keyX: -1.2, keyZ: 3, wallZ: -3, wallColor: '#0a0d0c', floorColor: '#0a0d0c' }); const s = spill(g, 5, 4, '#1c6b44', 0.35); s.position.set(0, 1.6, r.wall.position.z + 0.05); return r; };

  return {
    b1: { // phone flies in, a sticker pops out with sound rings
      build(g) {
        darkroom(g);
        const phone = O.phone(g, { power: 1.1 }); phone.position.set(0, 1.6, 0);
        let lit = -1; phone.screen.paint((x, w, h) => chat(x, w, h, 'Stickers', 6, { lit }));
        const st = panel(g, 0.62, 0.62, (x, w, h) => sticker(x, w, h, 0, true), { power: 0.9 });
        const rs = rings(g, 3, 0.45, 1.95, 0.32);
        return { phone, st, rs };
      },
      update({ phone, st, rs }, t, k, d) {
        const fly = prog(t, 0, 0.45, ease.out);
        phone.position.y = lerp(0.9, 1.6, fly); phone.rotation.set(lerp(0.9, 0.12, fly), lerp(-1.2, -0.35, fly) + Math.sin(t * 0.8) * 0.04, lerp(0.3, 0.06, fly));
        const pop = prog(t, 0.45, 0.85, ease.back);
        st.scale.setScalar(Math.max(0.001, pop)); st.position.set(lerp(0.1, 0.45, pop), 1.95, 0.32); st.rotation.z = Math.sin(t * 6) * 0.05 * pop;
        rs.forEach((r) => r.position.copy(st.position));
        pulse(rs, t, t > kit.at('sound') - 0.1);
        const dr = drift(t, 0.01);
        cam(dr.x + 0.1, 1.7 + dr.y, lerp(5.2, 4.2, prog(t, 0, d, ease.out)), 0.15, 1.7, 0, 32);
      },
    },
    b2: { // a microphone; a wave travels into the sticker
      build(g) {
        darkroom(g);
        const head = sphere(g, 0.2, metal('#cfd6d3'), -0.55, 2.05, 0.2);
        const grille = torus(g, 0.2, 0.02, metal('#7d8a84'), -0.55, 2.05, 0.2); grille.rotation.y = Math.PI / 2;
        const stem = cyl(g, 0.05, 0.05, 0.9, metal('#4a5450'), -0.55, 1.6, 0.2);
        const base = cyl(g, 0.28, 0.32, 0.06, metal('#2c3330'), -0.55, 1.15, 0.2);
        const bars = Array.from({ length: 7 }, (_, i) => box(g, 0.045, 0.3, 0.045, glow(G, 1.2), -0.27 + i * 0.075, 1.95, 0.2));
        const st = panel(g, 0.55, 0.55, (x, w, h) => sticker(x, w, h, 2, true), { power: 0.9 }); st.position.set(0.5, 1.95, 0.2);
        const rs = rings(g, 3, 0.5, 1.95, 0.22);
        return { bars, st, rs, head };
      },
      update({ bars, st, rs }, t, k, d) {
        const go = t > kit.at('voice') - 0.2;
        bars.forEach((b, i) => { const a = go ? 0.25 + 0.75 * Math.abs(Math.sin(t * 9 - i * 0.7)) : 0.1; b.scale.y = a; });
        st.rotation.z = Math.sin(t * 2) * 0.05; st.scale.setScalar(1 + (go ? 0.04 * Math.sin(t * 12) : 0));
        pulse(rs, t, go, 1, 2.2);
        const dr = drift(t, 0.012);
        cam(dr.x, 1.95 + dr.y, lerp(6.2, 5.6, k), 0, 1.85, 0, 32);
      },
    },
    b3: { // a pointer taps a sticker in the chat; rings burst
      build(g) {
        darkroom(g);
        const phone = O.phone(g, { power: 1.1 }); phone.position.set(0, 1.6, 0); phone.rotation.y = -0.25;
        const ptr = new kit.THREE.Group(); g.add(ptr);
        const tip = kit.THREE; const cone = new tip.Mesh(new tip.ConeGeometry(0.1, 0.32, 3), clay('#f4f4f4')); cone.rotation.z = Math.PI * 0.8; ptr.add(cone);
        const rs = rings(g, 3, -0.17, 1.95, 0.12);
        return { phone, ptr, rs };
      },
      update({ phone, ptr, rs }, t, k, d) {
        const tapAt = kit.at('tap');
        phone.screen.paint((x, w, h) => chat(x, w, h, 'Stickers', 6, { lit: t > tapAt ? 0 : -1 }));
        const m = prog(t, 0, tapAt, ease.inOut);
        ptr.position.set(lerp(0.6, -0.12, m), lerp(1.0, 1.88, m), 0.25);
        const press = t > tapAt && t < tapAt + 0.2 ? 0.85 : 1; ptr.scale.setScalar(press);
        pulse(rs, t - tapAt, t > tapAt, 1.3, 2.4);
        const dr = drift(t, 0.01);
        cam(dr.x - 0.1, 1.75 + dr.y, lerp(4.4, 3.6, k), -0.05, 1.7, 0, 32);
      },
    },
    b4: { // making one by one is slow: progress stalls red, stopwatch spins
      build(g) {
        darkroom(g);
        const phone = O.phone(g, { power: 1.1 }); phone.position.set(0.28, 1.65, 0); phone.rotation.y = -0.3;
        const clock = O.clock(g, { r: 0.26 }); clock.position.set(-0.45, 2.3, 0.3);
        return { phone, clock };
      },
      update({ phone, clock }, t, k, d) {
        const p = Math.min(0.96, prog(t, 0, d * 0.55, ease.out) * 0.96), fail = t > d * 0.6;
        phone.screen.paint((x, w, h) => {
          x.fillStyle = '#0b1410'; x.fillRect(0, 0, w, h);
          x.fillStyle = '#e8f1ec'; x.font = `700 ${w * 0.08}px Inter`; x.textAlign = 'center'; x.fillText('Making sticker…', w / 2, h * 0.3);
          x.fillStyle = '#1d2a23'; x.fillRect(w * 0.1, h * 0.45, w * 0.8, h * 0.04);
          x.fillStyle = fail ? '#ff3b30' : G; x.fillRect(w * 0.1, h * 0.45, w * 0.8 * p, h * 0.04);
          x.font = `800 ${w * 0.16}px Inter`; x.fillStyle = fail ? '#ff3b30' : '#e8f1ec'; x.fillText(`${Math.round(p * 100)}%`, w / 2, h * 0.62);
          if (fail) { x.font = `700 ${w * 0.07}px Inter`; x.fillText('Try again', w / 2, h * 0.72); }
        });
        clock.set(t * 6);
        const dr = drift(t, 0.012);
        cam(dr.x, 1.95 + dr.y, lerp(6.0, 5.4, k), 0, 1.9, 0, 32);
      },
    },
    b5: { // stickers fly into the community chat; clock at 8
      build(g) {
        darkroom(g);
        const phone = O.phone(g, { power: 1.1 }); phone.position.set(0, 1.6, 0); phone.rotation.y = -0.2;
        const tiles = Array.from({ length: 8 }, (_, i) => { const p = panel(g, 0.36, 0.36, (x, w, h) => sticker(x, w, h, i, true), { power: 0.85 }); return p; });
        const clock = O.clock(g, { r: 0.26 }); clock.position.set(-0.5, 2.6, 0.25); clock.set(8);
        const dust = motes(g, { box: [4, 3, 2], n: 24 });
        return { phone, tiles, dust };
      },
      update({ phone, tiles, dust }, t, k, d) {
        dust.set(t);
        const n = Math.min(6, 1 + Math.floor(prog(t, 0.2, d * 0.8) * 6));
        phone.screen.paint((x, w, h) => chat(x, w, h, '403 UNLOCKED', n, { lit: n - 1 }));
        tiles.forEach((p, i) => {
          const a = (i / tiles.length) * Math.PI * 2, s0 = 0.2 + i * (d * 0.7 / tiles.length), f = prog(t, s0, s0 + 0.7, ease.inOut);
          p.position.set(lerp(Math.cos(a) * 1.1, 0, f), lerp(1.75 + Math.sin(a) * 0.95, 1.6, f), lerp(0.6, 0.05, f));
          p.scale.setScalar(Math.max(0.001, 1 - f * 0.9)); p.rotation.z = (1 - f) * Math.sin(a * 3) * 0.5;
        });
        const dr = drift(t, 0.012);
        cam(dr.x, 1.9 + dr.y, lerp(5.8, 5.2, k), 0, 1.85, 0, 32);
      },
    },
    b6: { // STICKER comment bubble + follow button
      build(g) {
        darkroom(g);
        const bub = panel(g, 1.7, 0.75, (x, w, h) => {
          x.clearRect(0, 0, w, h); x.fillStyle = '#ffffff'; x.beginPath(); x.roundRect(0, 0, w, h * 0.82, h * 0.2); x.fill();
          x.beginPath(); x.moveTo(w * 0.18, h * 0.8); x.lineTo(w * 0.12, h); x.lineTo(w * 0.32, h * 0.8); x.fill();
          x.fillStyle = '#12a150'; x.font = `900 ${h * 0.42}px Inter`; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('STICKER', w / 2, h * 0.42);
        }, { power: 0.75 });
        const btn = panel(g, 1.2, 0.34, (x, w, h) => { x.clearRect(0, 0, w, h); x.fillStyle = '#39ff88'; x.beginPath(); x.roundRect(0, 0, w, h, h / 2); x.fill(); x.fillStyle = '#062012'; x.font = `800 ${h * 0.5}px Inter`; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('FOLLOW', w / 2, h / 2); }, { power: 0.75 });
        const st = [0, 1].map((i) => panel(g, 0.34, 0.34, (x, w, h) => sticker(x, w, h, i + 3, true), { power: 0.85 }));
        const rs = rings(g, 3, 0, 2.45, 0.05);
        return { bub, btn, st, rs };
      },
      update({ bub, btn, st, rs }, t, k, d) {
        const f = prog(t, kit.at('follow') - 0.1, kit.at('follow') + 0.4, ease.back);
        btn.scale.setScalar(Math.max(0.001, f)); btn.position.set(0, 1.8, 0.1);
        const b = prog(t, 0, 0.45, ease.back), hit = prog(t, kit.at('STICKER') - 0.1, kit.at('STICKER') + 0.35, ease.out);
        bub.scale.setScalar(Math.max(0.001, b * (1 + 0.14 * Math.sin(hit * Math.PI)))); bub.position.set(0, 2.45, 0.1); bub.rotation.z = Math.sin(t * 3) * 0.03;
        pulse(rs, t, b > 0.5, 0.9, 3);
        st.forEach((s, i) => { s.position.set([-0.62, 0.62][i], 3.0 + Math.sin(t * 2 + i) * 0.04, 0); s.rotation.z = Math.sin(t * 1.5 + i) * 0.15; });
        const dr = drift(t, 0.01);
        cam(dr.x, 1.85 + dr.y, 5.6, 0, 1.85, 0, 32);
      },
    },
  };
};
