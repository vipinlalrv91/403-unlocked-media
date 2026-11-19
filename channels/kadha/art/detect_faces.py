#!/usr/bin/env python3
"""Auto-detect eyes + mouth on the cartoon character PNGs; writes candidates to faces_auto.json."""
import json, sys
import numpy as np
from PIL import Image

def components(mask):
    h, w = mask.shape; lab = np.zeros((h, w), np.int32); comps = []; cur = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not lab[y, x]:
                cur += 1; st = [(y, x)]; lab[y, x] = cur; pts = []
                while st:
                    cy, cx = st.pop(); pts.append((cy, cx))
                    for ny, nx in ((cy+1, cx), (cy-1, cx), (cy, cx+1), (cy, cx-1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = cur; st.append((ny, nx))
                ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
                comps.append(dict(area=len(pts), y0=min(ys), y1=max(ys), x0=min(xs), x1=max(xs), cy=sum(ys)/len(ys), cx=sum(xs)/len(xs)))
    return comps

def detect(path, child=False):
    im = Image.open(path).convert("RGBA"); W, H = im.size
    k = 2; a = np.asarray(im.resize((W // k, H // k)), dtype=np.int32); h, w = a.shape[:2]
    y0, y1 = int(h * (0.12 if not child else 0.18)), int(h * (0.45 if not child else 0.62))
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    dark = (al > 200) & (np.maximum(np.maximum(r, g), b) < 80)
    dark[:y0] = False; dark[y1:] = False
    cs = [c for c in components(dark) if 25 <= c["area"] <= 1500]
    cs = [c for c in cs if 0.4 <= (c["x1"] - c["x0"] + 1) / (c["y1"] - c["y0"] + 1) <= 2.5 and c["area"] / ((c["x1"]-c["x0"]+1)*(c["y1"]-c["y0"]+1)) > 0.45]
    best = None
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            A, B = cs[i], cs[j]
            dx = abs(A["cx"] - B["cx"]); dy = abs(A["cy"] - B["cy"])
            if dy < 0.03 * h and 0.06 * w < dx < 0.4 * w and 0.5 < A["area"] / B["area"] < 2:
                score = A["area"] + B["area"] - 40 * dy
                if not best or score > best[0]: best = (score, A, B)
    if not best: return None
    _, A, B = best
    if A["cx"] > B["cx"]: A, B = B, A
    ew = max(A["x1"] - A["x0"], B["x1"] - B["x0"]) + 1; eh = max(A["y1"] - A["y0"], B["y1"] - B["y0"]) + 1
    ey = (A["cy"] + B["cy"]) / 2; dx = B["cx"] - A["cx"]; mxc = (A["cx"] + B["cx"]) / 2
    red = (al > 200) & (r > 140) & (r - g > 45) & (r - b > 25)
    ys, xs = np.nonzero(red[int(ey + 0.45 * dx): int(ey + 1.3 * dx), int(mxc - 0.22 * dx): int(mxc + 0.22 * dx)])
    if len(ys) > 3:
        my = int(ey + 0.45 * dx) + ys.mean(); mx = int(mxc - 0.22 * dx) + xs.mean()
    else:
        my, mx = ey + 0.85 * dx, mxc
    return {"eyes": [[int(A["cx"] * k), int(A["cy"] * k)], [int(B["cx"] * k), int(B["cy"] * k)]],
            "eye_w": int(ew * k * 1.25), "eye_h": int(eh * k * 1.2), "mouth": [int(mx * k), int(my * k)], "mouth_w": int(0.42 * dx * k)}

if __name__ == "__main__":
    out = {}
    for n in sys.argv[1:]:
        out[n] = detect(f"chars/{n}.png", child=n.endswith("_child")); print(n, out[n], flush=True)
    json.dump(out, open("faces_auto.json", "w"), indent=1)
