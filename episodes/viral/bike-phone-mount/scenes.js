export default (kit) => {
  const { O, room, cam, drift, prog, ease, lerp, clay, metal, glow, box, rbox, sphere, cyl, torus, panel, spill, motes } = kit;
  const OR = '#FF8A3D';
  // dusk road picture for screens / backdrop
  const road = (x, w, h, t, blur = 0) => {
    const g = x.createLinearGradient(0, 0, 0, h * 0.55); g.addColorStop(0, '#2a2140'); g.addColorStop(0.7, '#a1554a'); g.addColorStop(1, '#e48a52');
    x.fillStyle = g; x.fillRect(0, 0, w, h * 0.55);
    x.fillStyle = '#2b2333'; x.fillRect(0, h * 0.52, w, h * 0.48);
    x.fillStyle = '#3a3640'; x.beginPath(); x.moveTo(w * 0.47, h * 0.52); x.lineTo(w * 0.53, h * 0.52); x.lineTo(w * 1.1, h); x.lineTo(-w * 0.1, h); x.fill();
    x.fillStyle = '#e8e2d0';
    for (let i = 0; i < 8; i++) { const k = ((i / 8) + (t * 0.6) % (1 / 8)) % 1; const y = h * 0.52 + k * k * h * 0.48, hh = (2 + k * 26) * h / 600; x.fillRect(w / 2 - (1 + k * 6) * w / 600, y, (2 + k * 12) * w / 600, hh); }
    x.strokeStyle = '#1b1520'; x.lineWidth = w * 0.006;
    for (let i = 0; i < 7; i++) { const side = i % 2 ? 1 : -1, k = ((i / 7 + t * 0.15) % 1), px = w / 2 + side * (0.08 + k * 0.7) * w, py = h * 0.52, ht = (0.08 + k * 0.4) * h;
      x.beginPath(); x.moveTo(px, py); x.lineTo(px - side * w * 0.01, py - ht); x.stroke();
      for (let a = 0; a < 6; a++) { const r = a / 6 * Math.PI * 2; x.beginPath(); x.moveTo(px - side * w * 0.01, py - ht); x.quadraticCurveTo(px + Math.cos(r) * ht * 0.25, py - ht - ht * 0.08, px + Math.cos(r) * ht * 0.35, py - ht + Math.abs(Math.sin(r)) * ht * 0.12); x.stroke(); } }
    if (blur) { x.fillStyle = `rgba(160,110,100,${blur * 0.55})`; x.fillRect(0, 0, w, h); }
  };
  const gauge = (g, x0, label) => {
    const grp = new kit.THREE.Group(); g.add(grp); grp.position.set(x0, 0.95, 0.35); grp.scale.setScalar(0.78);
    const ring = torus(grp, 0.42, 0.035, metal('#d8d8d8'), 0, 0, 0);
    const face = panel(grp, 0.82, 0.82, (x, w, h) => { x.clearRect(0, 0, w, h); x.fillStyle = '#141218'; x.beginPath(); x.arc(w / 2, h / 2, w * 0.49, 0, 7); x.fill(); x.strokeStyle = '#ddd'; x.lineWidth = w * 0.012;
      for (let i = 0; i <= 10; i++) { const a = Math.PI * 0.75 + i / 10 * Math.PI * 1.5; x.beginPath(); x.moveTo(w / 2 + Math.cos(a) * w * 0.38, h / 2 + Math.sin(a) * w * 0.38); x.lineTo(w / 2 + Math.cos(a) * w * 0.44, h / 2 + Math.sin(a) * w * 0.44); x.stroke(); }
      x.fillStyle = '#bbb'; x.font = `600 ${w * 0.08}px Inter`; x.textAlign = 'center'; x.fillText(label, w / 2, h * 0.75); }, { power: 0.9 });
    face.position.z = -0.01;
    const needle = new kit.THREE.Group(); grp.add(needle); needle.position.z = 0.02;
    const nb = box(needle, 0.3, 0.025, 0.01, glow(OR, 1.4), 0.15, 0, 0);
    return { grp, needle };
  };
  const rig = (g) => {
    if (kit.bloom) kit.bloom.strength = 0.5;
    room(g, 'night', { keyPower: 60, fillPower: 0.9, wallZ: -4 });
    const bgp = panel(g, 9, 6, (x, w, h) => road(x, w, h, 0), { power: 0.9 }); bgp.position.set(0, 2.6, -3.9);
    const bar = cyl(g, 0.06, 0.06, 4.2, metal('#3b3b40'), 0, 1.55, 0.25); bar.rotation.z = Math.PI / 2;
    const mount = new kit.THREE.Group(); g.add(mount); mount.position.set(0, 1.95, 0.35);
    rbox(mount, 2.0, 1.05, 0.08, 0.1, clay('#1a1a1e'), 0, 0, -0.02);
    const scr = panel(mount, 1.86, 0.92, (x, w, h) => road(x, w, h, 0), { power: 1.15 }); scr.position.z = 0.03;
    const clamp1 = rbox(mount, 0.12, 1.2, 0.18, 0.05, clay(OR), -1.05, 0, -0.05), clamp2 = rbox(mount, 0.12, 1.2, 0.18, 0.05, clay(OR), 1.05, 0, -0.05);
    const arm = rbox(g, 0.18, 0.45, 0.18, 0.05, clay('#2a2a30'), 0, 1.65, 0.3);
    const g1 = gauge(g, -0.72, 'km/h'), g2 = gauge(g, 0.72, 'RPM x1000');
    const rings = [0, 1, 2].map(() => { const r = torus(g, 0.75, 0.01, glow(OR, 0.8), 0, 1.95, 0.4); r.material.transparent = true; return r; });
    return { bgp, mount, scr, g1, g2, rings, arm };
  };
  const drive = (R, t, shake, rpm, opts = {}) => {
    R.bgp.paint((x, w, h) => road(x, w, h, t));
    R.scr.paint((x, w, h) => { road(x, w, h, t, opts.blur || 0); x.fillStyle = '#e5483b'; x.beginPath(); x.roundRect(w * 0.38, h * 0.05, w * 0.24, h * 0.12, h * 0.06); x.fill(); x.fillStyle = '#fff'; x.font = `700 ${h * 0.08}px Inter`; x.textAlign = 'center'; x.fillText('00:00:' + String(Math.floor(t) + 10).padStart(2, '0'), w / 2, h * 0.135);
      if (opts.check) { x.fillStyle = 'rgba(20,160,90,0.85)'; x.beginPath(); x.arc(w * 0.85, h * 0.78, h * 0.12, 0, 7); x.fill(); x.strokeStyle = '#fff'; x.lineWidth = h * 0.03; x.beginPath(); x.moveTo(w * 0.81, h * 0.78); x.lineTo(w * 0.84, h * 0.83); x.lineTo(w * 0.9, h * 0.72); x.stroke(); } });
    const s = shake * 0.03;
    R.mount.position.x = Math.sin(t * 83) * s; R.mount.position.y = 1.95 + Math.sin(t * 97 + 1) * s; R.mount.rotation.z = Math.sin(t * 71) * s * 0.6;
    R.g1.needle.rotation.z = Math.PI * 1.25 - lerp(0.2, 2.2, rpm) + Math.sin(t * 40) * 0.02 * shake;
    R.g2.needle.rotation.z = Math.PI * 1.25 - lerp(0.3, 3.4, rpm) + Math.sin(t * 50) * 0.05 * shake;
    R.rings.forEach((r, i) => { const p = (t * 1.6 + i / 3) % 1; r.scale.setScalar(shake > 0.3 ? 1.0 + p * 0.5 : 0.001); r.material.opacity = shake > 0.3 ? (1 - p) * 0.8 : 0; });
  };
  return {
    b1: { build: (g) => rig(g), update(R, t, k, d) { drive(R, t, 0.15, 0.25); const dr = drift(t, 0.01); cam(dr.x, 1.9 + dr.y, lerp(10.5, 9.4, prog(t, 0, d, ease.out)), 0, 1.6, 0, 34); } },
    b2: { build: (g) => rig(g), update(R, t, k, d) { const v = prog(t, kit.at('vibration') - 0.3, kit.at('vibration') + 0.4, ease.out); drive(R, t, lerp(0.2, 1.4, v), lerp(0.3, 0.95, v)); const dr = drift(t, 0.01); cam(dr.x + Math.sin(t * 60) * 0.015 * v, 1.9 + dr.y, lerp(9.6, 8.8, k), 0, 1.6, 0, 34); } },
    b3: {
      build(g) {
        if (kit.bloom) kit.bloom.strength = 0.6;
        room(g, 'ink', { keyPower: 60, fillPower: 0.9 });
        const body = rbox(g, 2.4, 2.4, 0.25, 0.4, metal('#2c2c33'), 0, 1.8, 0);
        const barrel = cyl(g, 0.75, 0.75, 0.3, metal('#111'), 0, 1.8, 0.2); barrel.rotation.x = Math.PI / 2;
        const ringm = torus(g, 0.75, 0.06, metal('#9aa0a8'), 0, 1.8, 0.36);
        const lens = sphere(g, 0.45, new kit.THREE.MeshPhysicalMaterial({ color: '#2b3b66', roughness: 0.05, metalness: 0.2, transmission: 0.3, clearcoat: 1 }), 0, 1.8, 0.3);
        lens.scale.z = 0.35;
        const glowr = torus(g, 0.5, 0.02, glow(OR, 1.5), 0, 1.8, 0.4);
        return { lens, glowr };
      },
      update({ lens, glowr }, t, k, d) {
        const j = prog(t, kit.at('OIS') - 0.2, kit.at('OIS') + 0.3);
        lens.position.x = Math.sin(t * 90) * 0.06 * j; lens.position.y = 1.8 + Math.sin(t * 77 + 2) * 0.06 * j;
        glowr.material.emissiveIntensity = 0.5 + j * 2 * Math.abs(Math.sin(t * 6));
        const dr = drift(t, 0.008); cam(dr.x, 1.8 + dr.y, lerp(8.0, 6.6, prog(t, 0, d, ease.out)), 0, 1.8, 0, 34);
      },
    },
    b4: { build: (g) => rig(g), update(R, t, k, d) { const b = prog(t, kit.at('blur') - 0.2, kit.at('blur') + 0.5, ease.out); drive(R, t, 0.9, 0.8, { blur: b }); const dr = drift(t, 0.01); cam(dr.x, 1.95 + dr.y, lerp(7.4, 6.8, k), 0, 1.9, 0, 34); } },
    b5: {
      build(g) { const R = rig(g); R.damp = rbox(g, 0.42, 0.28, 0.26, 0.1, clay('#2e8b57'), 0, 1.55, 0.3); R.damp.visible = false; return R; },
      update(R, t, k, d) { const a = prog(t, kit.at('damper') - 0.3, kit.at('damper') + 0.2, ease.back); R.damp.visible = a > 0.01; R.damp.scale.setScalar(Math.max(0.001, a)); R.arm.visible = a < 0.5;
        drive(R, t, lerp(1.2, 0.05, a), 0.8); const dr = drift(t, 0.01); cam(dr.x, 1.85 + dr.y, lerp(9.0, 8.4, k), 0, 1.6, 0, 34); },
    },
    b6: { build: (g) => rig(g), update(R, t, k, d) { drive(R, t, 0.05, 0.5, { check: t > 0.3 }); const dr = drift(t, 0.01); cam(dr.x, 1.9 + dr.y, lerp(9.4, 10.4, k), 0, 1.6, 0, 34); } },
  };
};
