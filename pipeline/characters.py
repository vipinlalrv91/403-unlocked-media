"""Original 2D cartoon characters for Kadhapetti, drawn in code (no external art).

draw_character(im, name, cx, feet_y, height_px, t, talk=0.0, seed=0)
  - blinks every few seconds, gently sways/breathes, mouth opens with `talk` (0..1 audio level)
Characters are respectful, traditional-style (Ramayanam: Rama blue-skinned with crown and bow, etc.).
"""
import math
from PIL import Image, ImageDraw

GOLD, GOLD_D, RUBY, PEARL = (245, 190, 40), (190, 130, 20), (210, 30, 60), (250, 248, 235)
FAIR, WHEAT, BLUE = (243, 205, 168), (226, 180, 140), (72, 118, 205)

CHARS = {
    "rama":       dict(skin=BLUE, dhoti=(250, 200, 40), sash=(240, 120, 30), crown="tall", bow=True, tilak=True),
    "lakshmana":  dict(skin=FAIR, dhoti=(240, 130, 40), sash=(190, 50, 60), crown="tall", bow=True, tilak=True),
    "bharata":    dict(skin=WHEAT, dhoti=(70, 160, 90), sash=(250, 200, 40), crown="tall", tilak=True),
    "shatrughna": dict(skin=FAIR, dhoti=(130, 80, 180), sash=(250, 200, 40), crown="tall", tilak=True),
    "sita":       dict(skin=FAIR, saree=(205, 30, 70), border=GOLD, female=True, crown="small"),
    "dasharatha": dict(skin=WHEAT, dhoti=(245, 240, 230), top=(150, 30, 70), crown="tall", beard=(245, 245, 245), tilak=True),
    "kausalya":   dict(skin=FAIR, saree=(250, 175, 40), border=(200, 40, 60), female=True, crown="small"),
    "kaikeyi":    dict(skin=WHEAT, saree=(150, 60, 175), border=GOLD, female=True, crown="small"),
    "sumitra":    dict(skin=FAIR, saree=(40, 150, 110), border=GOLD, female=True, crown="small"),
    "sage":       dict(skin=WHEAT, dhoti=(235, 120, 30), top=(235, 120, 30), beard=(245, 245, 245), jata=True, staff=True, beads=True),
    "hanuman":    dict(skin=(205, 120, 60), dhoti=(220, 40, 40), sash=(250, 200, 40), crown="small", gada=True, tilak=True, muzzle=True),
}
for k in ("rama", "lakshmana", "bharata", "shatrughna"):
    CHARS[k + "_child"] = dict(CHARS[k], child=True, bow=False)


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def _sprite(spec, t, talk, seed):
    S = 2  # supersample
    Wd, Hd = 520 * S, 1100 * S
    im = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    child = spec.get("child"); hs = 1.25 if child else 1.0       # bigger head for kids
    cx = Wd // 2
    skin, skin_d = spec["skin"], _shade(spec["skin"], 0.82)
    sway = math.sin(t * 2.2 + seed) * 6 * S

    # ---- legs / lower body ----
    if spec.get("female"):
        sr = spec["saree"]
        d.polygon([(cx - 120 * S, 560 * S), (cx + 120 * S, 560 * S), (cx + 175 * S, 1060 * S), (cx - 175 * S, 1060 * S)], fill=sr)
        d.rectangle([cx - 175 * S, 1020 * S, cx + 175 * S, 1060 * S], fill=spec["border"])
        for i in range(-2, 3):  # pleats
            d.line([cx + i * 40 * S, 620 * S, cx + i * 55 * S, 1020 * S], fill=_shade(sr, 0.85), width=4 * S)
    else:
        dh = spec["dhoti"]
        d.polygon([(cx - 110 * S, 560 * S), (cx + 110 * S, 560 * S), (cx + 140 * S, 960 * S), (cx - 140 * S, 960 * S)], fill=dh)
        d.line([cx, 600 * S, cx, 950 * S], fill=_shade(dh, 0.8), width=5 * S)
        for fx in (-70, 70):
            d.rounded_rectangle([cx + (fx - 35) * S, 950 * S, cx + (fx + 35) * S, 1060 * S], radius=20 * S, fill=skin)
        d.rectangle([cx - 140 * S, 930 * S, cx + 140 * S, 960 * S], fill=_shade(dh, 0.85))

    # ---- torso ----
    top = spec.get("top")
    torso_col = spec["saree"] if spec.get("female") else (top or skin)
    d.rounded_rectangle([cx - 115 * S, 330 * S, cx + 115 * S, 590 * S], radius=50 * S, fill=torso_col)
    if spec.get("female"):  # pallu over shoulder
        d.polygon([(cx - 115 * S, 340 * S), (cx - 40 * S, 330 * S), (cx + 115 * S, 590 * S), (cx + 40 * S, 590 * S)], fill=_shade(spec["saree"], 0.88))
        d.line([(cx - 40 * S, 330 * S), (cx + 115 * S, 590 * S)], fill=spec["border"], width=10 * S)
    elif spec.get("sash"):
        d.line([(cx - 105 * S, 350 * S), (cx + 105 * S, 580 * S)], fill=spec["sash"], width=34 * S)
    d.rectangle([cx - 115 * S, 555 * S, cx + 115 * S, 590 * S], fill=GOLD if not spec.get("jata") else (120, 70, 30))  # belt
    # necklace / beads
    if spec.get("beads"):
        for i in range(9):
            a = math.pi * (0.15 + 0.7 * i / 8)
            d.ellipse([cx + math.cos(a) * 80 * S - 10 * S, 340 * S + math.sin(a) * 90 * S - 10 * S, cx + math.cos(a) * 80 * S + 10 * S, 340 * S + math.sin(a) * 90 * S + 10 * S], fill=(110, 50, 30))
    elif not spec.get("jata"):
        d.arc([cx - 70 * S, 300 * S, cx + 70 * S, 420 * S], 20, 160, fill=GOLD, width=10 * S)
        d.ellipse([cx - 12 * S, 405 * S, cx + 12 * S, 429 * S], fill=RUBY)

    # ---- arms (gentle wave) ----
    wave = math.sin(t * 3 + seed) * 8
    for side in (-1, 1):
        ang = math.radians(10 * side + (wave if side == 1 else 0))
        x0, y0 = cx + side * 115 * S, 350 * S
        x1, y1 = x0 + math.sin(ang) * 40 * S * side, y0 + math.cos(ang) * 230 * S
        d.line([x0, y0, x1, y1], fill=skin, width=50 * S)
        d.ellipse([x1 - 28 * S, y1 - 28 * S, x1 + 28 * S, y1 + 28 * S], fill=skin)
        d.rectangle([x0 - 25 * S + (x1 - x0) * 0.75, y0 + (y1 - y0) * 0.72, x0 + 25 * S + (x1 - x0) * 0.75, y0 + (y1 - y0) * 0.72 + 14 * S], fill=GOLD)  # bangle
        if side == 1:
            hand = (x1, y1)

    # ---- props ----
    hx, hy = hand
    if spec.get("bow"):
        d.arc([hx - 40 * S, hy - 330 * S, hx + 110 * S, hy + 170 * S], 270, 90, fill=(140, 80, 30), width=14 * S)
        d.line([hx + 35 * S, hy - 325 * S, hx + 35 * S, hy + 165 * S], fill=(230, 230, 230), width=3 * S)
    if spec.get("staff"):
        d.line([hx, hy - 420 * S, hx, hy + 330 * S], fill=(130, 80, 40), width=16 * S)
    if spec.get("gada"):
        d.line([hx, hy, hx, hy - 260 * S], fill=GOLD_D, width=16 * S)
        d.ellipse([hx - 55 * S, hy - 360 * S, hx + 55 * S, hy - 240 * S], fill=GOLD)

    # ---- head ----
    R = int(115 * hs * S); hy0 = int(205 * S - (R - 115 * S) * 0.5)
    hcx = cx
    if spec.get("female"):
        d.ellipse([hcx - R - 18 * S, hy0 - R - 10 * S, hcx + R + 18 * S, hy0 + R + 40 * S], fill=(25, 20, 25))  # hair
        d.ellipse([hcx + R - 30 * S, hy0 - 10 * S, hcx + R + 60 * S, hy0 + 80 * S], fill=(25, 20, 25))      # bun
    elif spec.get("jata"):
        d.ellipse([hcx - 70 * S, hy0 - R - 110 * S, hcx + 70 * S, hy0 - R + 30 * S], fill=(240, 240, 240))
    else:
        d.ellipse([hcx - R - 8 * S, hy0 - R - 5 * S, hcx + R + 8 * S, hy0 + R + 30 * S], fill=(25, 20, 25))
    d.rectangle([hcx - 38 * S, hy0 + R - 25 * S, hcx + 38 * S, hy0 + R + 45 * S], fill=skin_d)  # neck
    d.ellipse([hcx - R, hy0 - R, hcx + R, hy0 + R], fill=skin)
    if spec.get("muzzle"):
        d.ellipse([hcx - R * 0.65, hy0 + R * 0.05, hcx + R * 0.65, hy0 + R * 0.95], fill=(240, 205, 160))
    for ex in (-1, 1):  # ears + earrings
        d.ellipse([hcx + ex * R - 18 * S, hy0 - 15 * S, hcx + ex * R + 18 * S, hy0 + 35 * S], fill=skin)
        d.ellipse([hcx + ex * R - 10 * S, hy0 + 32 * S, hcx + ex * R + 10 * S, hy0 + 52 * S], fill=GOLD)

    # eyes with blink
    blink = (t + seed * 0.37) % 3.4 < 0.13
    ey = hy0 - 5 * S
    for ex in (-1, 1):
        x = hcx + ex * 42 * S * hs
        if blink:
            d.line([x - 22 * S, ey, x + 22 * S, ey], fill=(30, 20, 20), width=6 * S)
        else:
            d.ellipse([x - 24 * S, ey - 17 * S, x + 24 * S, ey + 17 * S], fill=PEARL)
            d.ellipse([x - 12 * S, ey - 13 * S, x + 12 * S, ey + 13 * S], fill=(40, 25, 20))
            d.ellipse([x - 4 * S, ey - 9 * S, x + 3 * S, ey - 2 * S], fill=(255, 255, 255))
        d.arc([x - 28 * S, ey - 45 * S, x + 28 * S, ey - 15 * S], 200, 340, fill=(40, 25, 20), width=6 * S)  # brow
    d.line([hcx, ey + 10 * S, hcx - 6 * S, ey + 45 * S], fill=skin_d, width=5 * S)  # nose
    if spec.get("female"):
        d.ellipse([hcx - 8 * S, ey - 52 * S, hcx + 8 * S, ey - 36 * S], fill=RUBY)  # bindi
    elif spec.get("tilak"):
        d.line([hcx, ey - 75 * S, hcx, ey - 30 * S], fill=(230, 60, 40), width=8 * S)
    if spec.get("beard"):
        d.chord([hcx - R * 0.85, hy0 + R * 0.05, hcx + R * 0.85, hy0 + R * 1.6], 0, 180, fill=spec["beard"])
        d.ellipse([hcx - 55 * S, ey + 50 * S, hcx + 55 * S, ey + 75 * S], fill=spec["beard"])  # moustache
    # mouth (lip sync)
    my = ey + 75 * S
    if talk > 0.08:
        h = int((8 + 34 * min(1, talk)) * S)
        d.ellipse([hcx - 22 * S, my - h // 2, hcx + 22 * S, my + h // 2], fill=(120, 30, 40))
    elif not spec.get("beard"):
        d.arc([hcx - 30 * S, my - 20 * S, hcx + 30 * S, my + 12 * S], 20, 160, fill=(150, 50, 50), width=6 * S)
    # rosy cheeks
    for ex in (-1, 1):
        d.ellipse([hcx + ex * 70 * S * hs - 18 * S, ey + 35 * S, hcx + ex * 70 * S * hs + 18 * S, ey + 55 * S], fill=_shade(skin, 1.08) if skin != BLUE else (95, 140, 220))

    # crown
    ct = spec.get("crown")
    if ct:
        top_y = hy0 - R + 18 * S
        if ct == "tall":
            d.polygon([(hcx - R * 0.8, top_y), (hcx + R * 0.8, top_y), (hcx + R * 0.55, top_y - 150 * S), (hcx, top_y - 200 * S), (hcx - R * 0.55, top_y - 150 * S)], fill=GOLD)
            d.rectangle([hcx - R * 0.85, top_y - 10 * S, hcx + R * 0.85, top_y + 22 * S], fill=GOLD_D)
            for jx in (-0.45, 0, 0.45):
                d.ellipse([hcx + jx * R - 14 * S, top_y - 85 * S, hcx + jx * R + 14 * S, top_y - 57 * S], fill=RUBY)
        else:
            for i in range(5):
                x = hcx + (i - 2) * 36 * S
                d.polygon([(x - 18 * S, top_y + 5 * S), (x + 18 * S, top_y + 5 * S), (x, top_y - 50 * S)], fill=GOLD)
            d.rectangle([hcx - 100 * S, top_y - 2 * S, hcx + 100 * S, top_y + 18 * S], fill=GOLD_D)

    im = im.rotate(math.degrees(math.atan2(sway, 900 * S)) * 3, resample=Image.BICUBIC, center=(cx, 1060 * S))
    return im


_cache = {}
def draw_character(im, name, cx, feet_y, height_px, t, talk=0.0, seed=0, flip=False):
    spec = CHARS[name]
    spr = _sprite(spec, t, talk, seed)
    breathe = 1 + 0.012 * math.sin(t * 2.6 + seed)
    h = int(height_px * breathe); w = int(spr.width * h / spr.height)
    spr = spr.resize((w, h), Image.LANCZOS)
    if flip: spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    im.paste(spr, (int(cx - w / 2), int(feet_y - h * 0.965)), spr)
