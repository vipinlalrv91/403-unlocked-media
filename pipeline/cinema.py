"""2.5D 'cinematic' layer for painted story scenes (Kadha Petti, owner chose option A on 23 Nov 2026).

What it adds (characters' bodies stay still, as the owner asked; lip sync / blink untouched):
  * camera: eased push-in + slow lateral drift, different direction per scene
  * parallax: characters (nearer layer) drift a little more than the background and grow slightly
  * atmosphere by background: falling leaves / petals, fireflies, water glints, golden dust, light rays, mist
  * soft vignette for a film look
Everything is procedural and cached per scene, so render time stays reasonable.
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920

FX_FOR = {  # background name -> effects
    "forest": ("leaves", "rays"), "chitrakoot": ("petals", "rays"), "ashram": ("leaves", "rays", "smoke"),
    "ahalya_ashram": ("leaves", "rays"), "night_forest": ("fireflies",), "river": ("glints", "mist"),
    "ganga_bank": ("glints", "mist"), "ocean": ("glints", "mist"), "palace_hall": ("dust", "lampglow"),
    "mithila_court": ("dust", "lampglow"), "wedding_mandapam": ("petals", "lampglow"), "ayodhya": ("dust", "rays"),
    "chariot_road": ("dust", "rays"), "lanka": ("dust", "rays"),
}

_cache = {}


def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def camera(t, D, seed):
    """zoom, pan_x (px, + = camera moves right), pan_y"""
    r = random.Random(seed); dirx = r.choice([-1, 1]); diry = r.choice([-1, 0, 1])
    p = ease(t / max(0.1, D))
    return 1.0 + 0.11 * p, dirx * 70 * (p - 0.5), diry * 25 * (p - 0.5)


def bg(src, name, t, D, seed):
    key = ("bg", name)
    if key not in _cache:  # pre-scale once to cover the frame at max zoom + pan margin
        sc = max((W + 200) * 1.12 / src.width, (H + 80) * 1.12 / src.height)
        _cache[key] = src.resize((int(src.width * sc), int(src.height * sc)), Image.LANCZOS)
    big = _cache[key]; z, px, py = camera(t, D, seed)
    cw, ch = (W + 200) * 1.12 / z, (H + 80) * 1.12 / z       # crop size shrinks as we push in
    cw, ch = cw * W / (W + 200), ch * H / (H + 80)
    cx = big.width / 2 + px * big.width / (W * 1.4); cy = big.height / 2 + py * big.height / (H * 1.4)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return big.resize((W, H), Image.BILINEAR, box=box), (z, px, py)


def _glow_sprite(r, col):
    key = ("glow", r, col)
    if key not in _cache:
        g = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
        for i in range(r * 2, 0, -1):
            a = int(255 * (1 - i / (r * 2)) ** 2.2); d.ellipse([r * 2 - i, r * 2 - i, r * 2 + i, r * 2 + i], fill=col + (a,))
        _cache[key] = g
    return _cache[key]


def _leaf_sprite(kind, k):
    key = ("leaf", kind, k)
    if key not in _cache:
        r = random.Random(k); s = r.randint(26, 46)
        im = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        if kind == "petals":
            col = r.choice([(255, 182, 203), (255, 214, 226), (255, 240, 245), (255, 200, 120)])
            d.ellipse([s * 0.5, s * 0.75, s * 1.5, s * 1.25], fill=col + (235,))
        else:
            col = r.choice([(120, 170, 60), (170, 190, 70), (210, 170, 60), (90, 140, 50)])
            d.ellipse([s * 0.3, s * 0.78, s * 1.7, s * 1.22], fill=col + (235,))
            d.line([s * 0.35, s, s * 1.65, s], fill=(70, 90, 30, 200), width=2)
        _cache[key] = im.filter(ImageFilter.GaussianBlur(0.8))
    return _cache[key]


def _rays():
    if "rays" not in _cache:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
        for i in range(5):
            x = 120 + i * 230; w = 90 + 40 * (i % 2)
            d.polygon([(x, -50), (x + w, -50), (x + w + 520, H * 0.75), (x + 380, H * 0.75)], fill=(255, 240, 190, 38))
        _cache["rays"] = g.filter(ImageFilter.GaussianBlur(40))
    return _cache["rays"]


def _vignette():
    if "vig" not in _cache:
        m = Image.new("L", (W // 4, H // 4), 0); d = ImageDraw.Draw(m)
        d.ellipse([-W // 8, -H // 14, W // 4 + W // 8, H // 4 + H // 14], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(40)).resize((W, H), Image.BILINEAR)
        v = Image.new("RGBA", (W, H), (20, 10, 0, 0)); v.putalpha(m.point(lambda a: int((255 - a) * 0.45)))
        _cache["vig"] = v
    return _cache["vig"]


def effects(im, kinds, t, seed, layer):
    """layer 'back' = behind characters, 'front' = in front (fewer, bigger, softer)."""
    im = im.convert("RGBA")
    if layer == "back" and "rays" in kinds:
        r = _rays().copy(); a = 0.75 + 0.25 * math.sin(t * 0.7 + seed)
        r.putalpha(r.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(r, (int(25 * math.sin(t * 0.25)), 0))
    if layer == "back" and "mist" in kinds:
        if "mist" not in _cache:
            g = Image.new("RGBA", (W * 2, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
            rr = random.Random(7)
            for _ in range(40):
                x, y, w = rr.uniform(0, W * 2), rr.uniform(120, 300), rr.uniform(200, 500)
                d.ellipse([x - w, y - 60, x + w, y + 60], fill=(255, 255, 255, 18))
            _cache["mist"] = g.filter(ImageFilter.GaussianBlur(30))
        off = int((t * 25) % W); im.alpha_composite(_cache["mist"].crop((off, 0, off + W, 420)), (0, int(H * 0.55)))
    if "lampglow" in kinds and layer == "back":
        rr = random.Random(seed)
        for i in range(6):
            x, y = rr.uniform(80, W - 80), rr.uniform(250, 900)
            f = 0.7 + 0.3 * math.sin(t * (5 + i) + i * 2.1)
            g = _glow_sprite(int(38 * f) or 1, (255, 200, 90)); im.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
    rr = random.Random(seed * 31 + (1 if layer == "front" else 0))
    if "leaves" in kinds or "petals" in kinds:
        kind = "petals" if "petals" in kinds else "leaves"
        n = 16 if layer == "back" else 5; sc = 1.0 if layer == "back" else 1.9
        for i in range(n):
            x0, sp, ph = rr.uniform(-100, W + 100), rr.uniform(70, 150) * sc, rr.uniform(0, 100)
            y = ((t + ph) * sp) % (H + 200) - 100; x = x0 + 70 * math.sin((t + ph) * 1.1) + t * 15
            spr = _leaf_sprite(kind, i % 6).rotate((t + ph) * 70 % 360, expand=True, resample=Image.BICUBIC)
            if sc != 1.0:
                spr = spr.resize((int(spr.width * sc), int(spr.height * sc)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
            im.alpha_composite(spr, (int(x) % (W + 100) - 50, int(y)))
    if "fireflies" in kinds:
        n = 26 if layer == "back" else 6
        for i in range(n):
            x0, y0, ph = rr.uniform(0, W), rr.uniform(300, H - 300), rr.uniform(0, 10)
            x = x0 + 50 * math.sin(t * 0.6 + ph); y = y0 + 35 * math.sin(t * 0.8 + ph * 1.7)
            a = max(0.0, math.sin(t * 2.2 + ph)) ** 1.5
            if a < 0.05: continue
            g = _glow_sprite(8 if layer == "back" else 16, (255, 240, 120)).copy()
            g.putalpha(g.split()[3].point(lambda v, a=a: int(v * a))); im.alpha_composite(g, (int(x), int(y)))
    if "glints" in kinds and layer == "back":
        for i in range(30):
            x, y, ph = rr.uniform(0, W), rr.uniform(H * 0.55, H * 0.85), rr.uniform(0, 10)
            a = max(0.0, math.sin(t * 3.0 + ph)) ** 6
            if a < 0.05: continue
            g = _glow_sprite(7, (255, 255, 230)).copy(); g.putalpha(g.split()[3].point(lambda v, a=a: int(v * a)))
            im.alpha_composite(g, (int(x + 10 * math.sin(t + ph)), int(y)))
    if "dust" in kinds:
        n = 22 if layer == "back" else 4
        for i in range(n):
            x0, y0, ph, sp = rr.uniform(0, W), rr.uniform(0, H), rr.uniform(0, 10), rr.uniform(8, 25)
            x = (x0 + t * sp + 30 * math.sin(t * 0.5 + ph)) % W; y = (y0 - t * sp * 0.6) % H
            g = _glow_sprite(5 if layer == "back" else 12, (255, 225, 150)).copy()
            a = 0.35 + 0.35 * math.sin(t * 1.3 + ph); g.putalpha(g.split()[3].point(lambda v, a=a: int(v * a)))
            im.alpha_composite(g, (int(x), int(y)))
    if "smoke" in kinds and layer == "back":
        for i in range(5):
            ph = (t * 0.25 + i / 5) % 1.0; x = W * 0.22 + 40 * math.sin(ph * 6 + i); y = H * 0.55 - ph * 500
            g = _glow_sprite(int(30 + 60 * ph), (230, 230, 230)).copy()
            g.putalpha(g.split()[3].point(lambda v, a=(1 - ph) * 0.35: int(v * a))); im.alpha_composite(g, (int(x), int(y)))
    if layer == "front":
        im.alpha_composite(_vignette())
    return im.convert("RGB")
