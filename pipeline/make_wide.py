#!/usr/bin/env python3
"""Render a Kadha Petti episode in full-screen 16:9 (1920x1080) for the weekly long YouTube videos (owner, 25 Nov 2026).
  python3 pipeline/make_wide.py channels/kadha/episodes/ramayanam-NN.json [--keep-cta]
-> videos/ramayanam-NN_wide.mp4. Reuses the cached voice clips of the Short (no ElevenLabs cost when cached).
Story scenes: Remotion at 1920x1080 (actions, lip sync, effects). Hook / moral / CTA: wide cards drawn here.
Without --keep-cta the closing 'subscribe' scene is dropped (only the last episode of a part keeps it)."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_short as ms
from PIL import Image, ImageDraw

W, H = 1920, 1080
ms.W, ms.H, ms.OUT_SUFFIX = W, H, "_wide"

def _base():
    if not hasattr(_base, "im"):
        im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
        for y in range(H):
            k = y / H; c = tuple(int(a + (b - a) * k) for a, b in zip((120, 200, 255), (255, 236, 200)))
            d.line([(0, y), (W, y)], fill=c)
        _base.im = im
    return _base.im.copy()

def wide_hook(s, t, D):
    im = _base(); z = 1 + 0.06 * math.sin(t * 3)
    ms.glow(im, W / 2, 680, 230 * z, (255, 200, 120), 0.8)
    e = ms.emoji(s.get("icon", "🏹"), int(300 * z)); im.paste(e, (int(W / 2 - e.width / 2), int(680 - e.height / 2)), e)
    d = ImageDraw.Draw(im)
    ms.text(d, 0, 150, s.get("title", "രാമായണം"), 130, (230, 80, 20), 6, center=True)
    if t > 0.5 and s.get("sub"): ms.text(d, 0, 340, s["sub"], 78, (90, 40, 160), 0, center=True)
    return im

def wide_moral(s, t, D):
    im = _base(); d = ImageDraw.Draw(im)
    for i in range(6):
        e = ms.emoji("⭐", 70); im.paste(e, (int(560 + i * 140), int(210 + 20 * math.sin(t * 2 + i))), e)
    d = ImageDraw.Draw(im)
    ms.text(d, 0, 70, s.get("heading", "ഗുണപാഠം"), 100, (230, 60, 120), 5, center=True)
    b = ms.ease(t / 0.8)
    if b > 0.05: d.rounded_rectangle([460, 320, 1460, 320 + 440 * b], radius=60, fill=(255, 255, 255), outline=(255, 150, 40), width=8)
    if b > 0.95:
        for i, line in enumerate(s["lines"]): ms.text(d, 0, 370 + i * 120, line, 66, (60, 40, 90), 0, center=True, maxw=900)
    if s.get("icon"): e = ms.emoji(s["icon"], 180); im.paste(e, (int(W / 2 - e.width / 2), 820), e)
    return im

def wide_cta(s, t, D):
    im = _base(); d = ImageDraw.Draw(im)
    p = ms.ease(t / 0.6)
    d.rounded_rectangle([W / 2 - 330 * p, 380, W / 2 + 330 * p, 520], radius=40, fill=(230, 30, 30))
    if p > 0.9: ms.text(d, 0, 412, "SUBSCRIBE", 74, (255, 255, 255), 0, center=True)
    if t > 0.8: e = ms.emoji("🔔", 150); im.paste(e, (int(W / 2 - 75), 570), e)
    d = ImageDraw.Draw(im)
    ms.text(d, 0, 150, "KADHA PETTI", 110, (230, 110, 20), 6, center=True)
    ms.text(d, 0, 800, "കുട്ടികളുടെ രാമായണം", 60, (90, 40, 160), 0, center=True)
    return im

ms.TEMPLATES.update(hook=wide_hook, moral=wide_moral, cta=wide_cta)

if __name__ == "__main__":
    path = sys.argv[1]; keep = "--keep-cta" in sys.argv
    ep = json.load(open(path, encoding="utf-8"))
    if not keep: ep["scenes"] = [s for s in ep["scenes"] if s["type"] != "cta"]
    ep["remotion"] = True; ep["cinematic"] = True
    tmp = os.path.join("/tmp", os.path.basename(path).replace(".json", "_wide.json"))
    json.dump(ep, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    ms.main(tmp)
