export default (kit) => {
  const { O, room, cam, drift, prog, ease, lerp, clay, metal, glow, box, rbox, sphere, cyl, torus, panel, spill, motes } = kit;
  const Y = '#FFC83D';
  const rnd = (i) => { const x = Math.sin(i * 12.9898) * 43758.5453; return x - Math.floor(x); };
  const staticPaint = (x, w, h, t, clear, label) => {
    x.fillStyle = '#111'; x.fillRect(0, 0, w, h);
    const f = Math.floor(t * 24);
    for (let i = 0; i < 900; i++) { const v = rnd(i + f * 977) * 255 * (1 - clear); x.fillStyle = `rgb(${v},${v},${v})`; x.fillRect(rnd(i * 3 + f) * w, rnd(i * 7 + f * 3) * h, w * 0.02, h * 0.012); }
    if (clear > 0) { x.globalAlpha = clear; const g = x.createLinearGradient(0, 0, 0, h); g.addColorStop(0, '#5aa7e0'); g.addColorStop(1, '#f7d9a0'); x.fillStyle = g; x.fillRect(0, 0, w, h);
      x.fillStyle = '#2f7a3a'; x.beginPath(); x.moveTo(0, h); x.lineTo(w * 0.3, h * 0.55); x.lineTo(w * 0.6, h); x.fill(); x.beginPath(); x.moveTo(w * 0.4, h); x.lineTo(w * 0.75, h * 0.5); x.lineTo(w, h); x.fill();
      x.fillStyle = '#fff3c4'; x.beginPath(); x.arc(w * 0.75, h * 0.25, w * 0.08, 0, 7); x.fill();
      if (label) { x.fillStyle = '#ffffff'; x.font = `800 ${w * 0.09}px Inter`; x.textAlign = 'center'; x.fillText(label, w / 2, h * 0.18); }
      x.globalAlpha = 1; }
  };
  const tv = (g, x0, y0) => {
    const body = rbox(g, 1.5, 1.2, 1.1, 0.12, clay('#5a4636'), x0, y0, 0);
    const scr = panel(g, 1.05, 0.82, (x, w, h) => staticPaint(x, w, h, 0, 0), { power: 1.1 }); scr.position.set(x0 - 0.12, y0 + 0.02, 0.56);
    const k1 = cyl(g, 0.06, 0.06, 0.05, metal('#c9c9c9'), x0 + 0.6, y0 + 0.2, 0.56); k1.rotation.x = Math.PI / 2;
    const k2 = cyl(g, 0.06, 0.06, 0.05, metal('#c9c9c9'), x0 + 0.6, y0 - 0.05, 0.56); k2.rotation.x = Math.PI / 2;
    const ant = new kit.THREE.Group(); g.add(ant); ant.position.set(x0, y0 + 0.6, 0);
    const a1 = cyl(ant, 0.015, 0.015, 0.9, metal('#d9d9d9'), 0, 0, 0); a1.position.set(-0.22, 0.4, 0); a1.rotation.z = 0.5;
    const a2 = cyl(ant, 0.015, 0.015, 0.9, metal('#d9d9d9'), 0, 0, 0); a2.position.set(0.22, 0.4, 0); a2.rotation.z = -0.5;
    sphere(ant, 0.08, metal('#888'), 0, 0.02, 0);
    return { body, scr, ant };
  };
  const warm = (g, look = 'clay') => { if (kit.bloom) kit.bloom.strength = 0.4; const r = room(g, look, { keyPower: 65, fillPower: 0.9, keyX: -1.2, keyZ: 3, wallZ: -2.6, wallColor: '#6b4a32', floorColor: '#3b2a1e' }); const s = spill(g, 4, 3, '#ffb35c', 0.35); s.position.set(0, 1.8, r.wall.position.z + 0.05); return r; };

  return {
    b1: {
      build(g) { warm(g); const table = O.table(g, { color: '#4a3424' }); const t = tv(g, 0, table.top + 0.6); return { ...t }; },
      update({ scr, body }, t, k, d) {
        const on = prog(t, 0.15, 0.5, ease.out);
        scr.paint((x, w, h) => { x.fillStyle = '#0a0a0a'; x.fillRect(0, 0, w, h); if (on > 0) { x.save(); x.globalAlpha = on; staticPaint(x, w, h, t, 0); x.restore(); x.fillStyle = '#000'; x.fillRect(0, 0, w, h * (0.5 - on * 0.5)); x.fillRect(0, h * (0.5 + on * 0.5), w, h); } });
        const dr = drift(t, 0.01);
        cam(dr.x, 2.0 + dr.y, lerp(7.2, 6.0, prog(t, 0, d, ease.out)), 0, 2.0, 0, 32);
      },
    },
    b2: {
      build(g) {
        warm(g, 'sand');
        const cas = new kit.THREE.Group(); g.add(cas); cas.position.set(0, 1.7, 0);
        rbox(cas, 1.6, 1.0, 0.16, 0.05, clay('#202020'), 0, 0, 0);
        const lab = panel(cas, 1.4, 0.45, (x, w, h) => { x.fillStyle = '#f2e6c8'; x.fillRect(0, 0, w, h); x.fillStyle = '#d0402f'; x.fillRect(0, h * 0.1, w, h * 0.15); x.fillStyle = '#333'; x.font = `700 ${h * 0.28}px Inter`; x.fillText('SIDE A  ·  FILM SONGS', w * 0.06, h * 0.7); }, { power: 0.8 }); lab.position.set(0, 0.2, 0.085);
        const win = panel(cas, 0.9, 0.3, (x, w, h) => { x.fillStyle = '#3a2a20'; x.fillRect(0, 0, w, h); }, { power: 0.5 }); win.position.set(0, -0.17, 0.086);
        const s1 = torus(cas, 0.11, 0.03, clay('#f4f4f4'), -0.32, -0.17, 0.09), s2 = torus(cas, 0.11, 0.03, clay('#f4f4f4'), 0.32, -0.17, 0.09);
        const pencil = new kit.THREE.Group(); cas.add(pencil); pencil.position.set(-0.32, -0.17, 0.12);
        const pb = cyl(pencil, 0.045, 0.045, 1.3, clay(Y), 0, 0.65, 0); const tip = new kit.THREE.Mesh(new kit.THREE.ConeGeometry(0.045, 0.14, 12), clay('#e8c9a0')); tip.position.y = -0.05; tip.rotation.x = Math.PI; pencil.add(tip);
        cyl(pencil, 0.047, 0.047, 0.12, clay('#ff8fa3'), 0, 1.35, 0);
        return { cas, s1, s2, pencil };
      },
      update({ cas, s1, s2, pencil }, t, k, d) {
        const spin = t * 9;
        s1.rotation.z = spin; s2.rotation.z = spin * 0.8; pencil.rotation.z = Math.sin(spin) * 0.25; pencil.rotation.x = Math.cos(spin) * 0.25;
        cas.rotation.y = Math.sin(t * 0.7) * 0.15; cas.rotation.x = -0.15;
        const dr = drift(t, 0.012);
        cam(dr.x, 2.0 + dr.y, lerp(6.4, 5.8, k), 0, 2.05, 0, 32);
      },
    },
    b3: {
      build(g) { warm(g); const table = O.table(g, { color: '#4a3424' }); const t = tv(g, 0, table.top + 0.6); return { ...t }; },
      update({ scr, ant }, t, k, d) {
        const a = kit.at('antenna');
        ant.rotation.y = Math.sin(Math.max(0, t - a) * 3) * 0.9 * (1 - prog(t, a + 1.6, a + 2.2));
        const clear = prog(t, a + 1.2, a + 2.2, ease.out);
        scr.paint((x, w, h) => staticPaint(x, w, h, t, clear, 'വന്നു! 📺'));
        const dr = drift(t, 0.01);
        cam(dr.x, 2.1 + dr.y, lerp(6.8, 6.2, k), 0, 2.1, 0, 32);
      },
    },
    b4: {
      build(g) {
        warm(g, 'sand'); const table = O.table(g, { color: '#4a3424' });
        const ph = new kit.THREE.Group(); g.add(ph); ph.position.set(0, table.top, 0.1);
        rbox(ph, 1.0, 0.35, 0.8, 0.12, clay('#c4282d'), 0, 0.18, 0);
        const dial = cyl(ph, 0.26, 0.26, 0.05, clay('#f1eadf'), 0, 0.37, 0.12); dial.rotation.x = 0.35;
        for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 1.7 + 0.4; const hole = cyl(ph, 0.03, 0.03, 0.06, clay('#2a2a2a'), Math.cos(a) * 0.18, 0.39, 0.12 + Math.sin(a) * 0.18 * 0.94); hole.rotation.x = 0.35; }
        const hs = new kit.THREE.Group(); ph.add(hs); hs.position.set(0, 0.45, -0.05);
        rbox(hs, 1.05, 0.12, 0.18, 0.06, clay('#c4282d'), 0, 0.05, 0);
        rbox(hs, 0.2, 0.18, 0.24, 0.06, clay('#c4282d'), -0.45, -0.03, 0); rbox(hs, 0.2, 0.18, 0.24, 0.06, clay('#c4282d'), 0.45, -0.03, 0);
        const rs = [0, 1, 2].map(() => { const r = torus(g, 0.4, 0.012, glow(Y, 1.2), 0, table.top + 0.5, 0.1); r.material.transparent = true; return r; });
        return { ph, hs, rs, top: table.top };
      },
      update({ ph, hs, rs, top }, t, k, d) {
        const r = t >= kit.at('ring') - 0.2, lift = prog(t, kit.at('എടുക്കാൻ'), kit.at('എടുക്കാൻ') + 0.4, ease.out);
        const buzz = r && lift < 0.1 ? 1 : 0;
        hs.position.y = 0.45 + Math.abs(Math.sin(t * 40)) * 0.04 * buzz + lift * 0.6; hs.rotation.z = lift * 0.4;
        ph.rotation.z = Math.sin(t * 60) * 0.02 * buzz;
        rs.forEach((x, i) => { const p = (t * 1.3 + i / 3) % 1; x.scale.setScalar(buzz ? 0.6 + p * 2.2 : 0.001); x.material.opacity = buzz ? 1 - p : 0; });
        const dr = drift(t, 0.012);
        cam(dr.x + 0.2, 2.6 + dr.y, lerp(5.4, 4.8, k), 0, top + 0.6, 0, 32);
      },
    },
    b5: {
      build(g) {
        warm(g);
        const ph = new kit.THREE.Group(); g.add(ph); ph.position.set(0, 1.75, 0);
        rbox(ph, 0.8, 1.7, 0.22, 0.2, clay('#2f3a45'), 0, 0, 0);
        const lcd = panel(ph, 0.56, 0.44, (x, w, h) => {}, { power: 1.0 }); lcd.position.set(0, 0.42, 0.115);
        for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) rbox(ph, 0.16, 0.09, 0.04, 0.03, clay('#c9d1d9'), -0.2 + c * 0.2, -0.12 - r * 0.15, 0.12);
        return { ph, lcd };
      },
      update({ ph, lcd }, t, k, d) {
        lcd.paint((x, w, h) => {
          x.fillStyle = '#9bbc0f'; x.fillRect(0, 0, w, h); x.fillStyle = '#0f380f';
          const cell = w / 16, n = 6 + Math.floor(t * 1.5), head = Math.floor(t * 6);
          for (let i = 0; i < n; i++) { const p = head - i; const col = ((p % 16) + 16) % 16, row = 4 + Math.floor(p / 16) % 6; x.fillRect(col * cell + 1, row * cell * 0.7 + 1, cell - 2, cell * 0.7 - 2); }
          x.fillRect(11 * cell + 3, 8 * cell * 0.7 + 3, cell - 6, cell * 0.7 - 6);
          x.font = `700 ${h * 0.12}px Inter`; x.fillText(String(120 + Math.floor(t * 20)).padStart(4, '0'), w * 0.04, h * 0.14);
        });
        ph.rotation.y = Math.sin(t * 0.8) * 0.2; ph.rotation.x = -0.1;
        const dr = drift(t, 0.012);
        cam(dr.x, 1.95 + dr.y, lerp(5.0, 4.3, prog(t, 0, d, ease.out)), 0, 2.0, 0, 32);
      },
    },
    b6: {
      build(g) {
        warm(g, 'ink');
        const fl = new kit.THREE.Group(); g.add(fl); fl.position.set(0, 1.9, 0);
        rbox(fl, 1.2, 1.2, 0.06, 0.04, clay('#2b5fb3'), 0, 0, 0);
        rbox(fl, 0.62, 0.42, 0.065, 0.01, metal('#c8ccd2'), 0.05, 0.38, 0.003);
        const lab = panel(fl, 0.9, 0.5, (x, w, h) => { x.fillStyle = '#f4f1e8'; x.fillRect(0, 0, w, h); x.strokeStyle = '#9aa'; for (let i = 1; i < 4; i++) { x.beginPath(); x.moveTo(w * 0.08, h * i / 4); x.lineTo(w * 0.92, h * i / 4); x.stroke(); } x.fillStyle = '#333'; x.font = `700 ${h * 0.2}px Inter`; x.fillText('1.44 MB', w * 0.08, h * 0.2); }, { power: 0.8 }); lab.position.set(0, -0.28, 0.035);
        const icon = panel(g, 0.9, 0.9, (x, w, h) => { x.clearRect(0, 0, w, h); x.strokeStyle = Y; x.lineWidth = w * 0.06; x.lineJoin = 'round'; x.beginPath(); x.moveTo(w * 0.15, h * 0.12); x.lineTo(w * 0.72, h * 0.12); x.lineTo(w * 0.88, h * 0.28); x.lineTo(w * 0.88, h * 0.88); x.lineTo(w * 0.15, h * 0.88); x.closePath(); x.stroke(); x.strokeRect(w * 0.32, h * 0.12, w * 0.32, h * 0.22); x.strokeRect(w * 0.28, h * 0.55, w * 0.46, h * 0.33); }, { power: 1.3 });
        icon.position.set(0, 1.9, 0.2);
        return { fl, icon };
      },
      update({ fl, icon }, t, k, d) {
        const f = prog(t, kit.at('floppy') - 0.3, kit.at('floppy') + 0.5, ease.inOut);
        fl.rotation.y = f * Math.PI; fl.scale.setScalar(1 - f * 0.4); fl.position.x = -f * 0.55;
        icon.scale.setScalar(Math.max(0.001, prog(t, kit.at('floppy'), kit.at('floppy') + 0.5, ease.back))); icon.position.x = 0.3;
        const dr = drift(t, 0.01);
        cam(dr.x, 1.95 + dr.y, lerp(5.2, 4.6, k), 0, 1.9, 0, 32);
      },
    },
    b7: {
      build(g) {
        warm(g); const table = O.table(g, { color: '#4a3424' });
        const t1 = tv(g, -0.55, table.top + 0.6); t1.scr.paint((x, w, h) => staticPaint(x, w, h, 1, 1, ''));
        const cas = rbox(g, 0.8, 0.5, 0.08, 0.03, clay('#202020'), 0.75, table.top + 0.27, 0.45); cas.rotation.x = -0.15;
        const lab = panel(g, 0.7, 0.2, (x, w, h) => { x.fillStyle = '#f2e6c8'; x.fillRect(0, 0, w, h); x.fillStyle = '#d0402f'; x.fillRect(0, h * 0.15, w, h * 0.25); }, { power: 0.8 }); lab.position.set(0.75, table.top + 0.36, 0.5); lab.rotation.x = -0.15;
        const ph = rbox(g, 0.3, 0.65, 0.1, 0.08, clay('#2f3a45'), 0.25, table.top + 0.33, 0.75);
        const scr = panel(g, 0.2, 0.15, (x, w, h) => { x.fillStyle = '#9bbc0f'; x.fillRect(0, 0, w, h); }, { power: 1 }); scr.position.set(0.25, table.top + 0.5, 0.81);
        const fl = rbox(g, 0.5, 0.5, 0.03, 0.02, clay('#2b5fb3'), 1.05, table.top + 0.26, 0.2); fl.rotation.z = 0.2;
        const dust = motes(g, { box: [4, 3, 2], n: 26 });
        return { dust, top: table.top };
      },
      update({ dust, top }, t, k, d) {
        dust.set(t);
        const dr = drift(t, 0.012);
        cam(dr.x + lerp(-0.25, -0.05, k), top + 1.6 + dr.y, lerp(9.6, 8.9, k), -0.1, top + 0.45, 0, 32);
      },
    },
  };
};
