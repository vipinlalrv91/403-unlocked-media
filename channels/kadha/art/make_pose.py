#!/usr/bin/env python3
"""Make an action pose FROM a character's original sprite, so the face stays identical (owner rule).
  python3 make_pose.py <char> kneel        -> chars/<char>_kneel.png   (lower body folded: kneeling / sitting low)
  python3 make_pose.py <char> bow          -> chars/<char>_bow.png     (kneel + leaning forward 14 deg)
Adds the face entry to faces.json and the voice to ../voices.json automatically."""
import json, sys, math
from PIL import Image
name, kind = sys.argv[1], sys.argv[2]
src = Image.open(f"chars/{name}.png").convert("RGBA"); W, H = src.size
y = int(H * 0.62); up = src.crop((0, 0, W, y)); lo = src.crop((0, y, W, H))
lo = lo.resize((int(W * 1.12), int(lo.height * 0.42)), Image.LANCZOS)
out = Image.new("RGBA", (int(W * 1.12), y + lo.height), (0, 0, 0, 0)); dx = (out.width - W) // 2
out.paste(up, (dx, 0), up); out.alpha_composite(lo, (0, y - 6))
F = json.load(open("faces.json")); f = F.get(name)
nf = {"eyes": [[a + dx, b] for a, b in f["eyes"]], "eye_w": f["eye_w"], "eye_h": f["eye_h"], "mouth": [f["mouth"][0] + dx, f["mouth"][1]], "mouth_w": f["mouth_w"]} if f else None
if kind == "bow":   # rotate around the knees (bottom centre)
    ang = -14; cx, cy = out.width / 2, out.height
    big = Image.new("RGBA", (out.width * 2, out.height * 2), (0, 0, 0, 0)); big.paste(out, (out.width // 2, out.height), out)
    rot = big.rotate(ang, center=(cx + out.width // 2, cy + out.height), resample=Image.BICUBIC)
    bb = rot.getbbox(); out2 = rot.crop(bb)
    if nf:
        def mp(px, py):
            X, Y = px + out.width // 2, py + out.height; ox, oy = cx + out.width // 2, cy + out.height; a = math.radians(-ang)
            rx = ox + (X - ox) * math.cos(a) - (Y - oy) * math.sin(a); ry = oy + (X - ox) * math.sin(a) + (Y - oy) * math.cos(a)
            return [int(rx - bb[0]), int(ry - bb[1])]
        nf = dict(nf, eyes=[mp(*e) for e in nf["eyes"]], mouth=mp(*nf["mouth"]))
    out = out2
pn = f"{name}_{kind}"; out.save(f"chars/{pn}.png")
if nf: F[pn] = nf; json.dump(F, open("faces.json", "w"), indent=1)
V = json.load(open("../voices.json"))
if name in V: V[pn] = V[name]; json.dump(V, open("../voices.json", "w"), ensure_ascii=False, indent=1)
print(pn, out.size, nf)
