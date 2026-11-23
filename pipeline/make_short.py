#!/usr/bin/env python3
"""403 UNLOCKED Shorts generator: episode JSON -> Malayalam voice (ElevenLabs) -> 1080x1920 MP4.

Usage: python3 pipeline/make_short.py episodes/<slug>.json
Output: videos/<slug>.mp4 and videos/<slug>_thumb.jpg

Episode JSON:
{
  "slug": "ac-modes",
  "scenes": [
    {"type": "hook",    "title": "AC MODES?", "sub": "Malayalam line", "icon": "❄️", "narration": "..."},
    {"type": "bullets", "title": "...", "items": ["...", "..."], "icon": "💧", "narration": "..."},
    {"type": "compare", "title": "...", "left": ["✓ ..."], "right": ["⚠ ..."], "narration": "..."},
    {"type": "steps",   "title": "...", "items": ["Settings", "Privacy"], "note": "...", "narration": "..."},
    {"type": "cta",     "keyword": "PRIVACY", "narration": "..."}
  ]
}
The ElevenLabs key is injected by the network proxy (header xi-api-key).
"""
import json, math, os, random, re, subprocess, sys, time, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf"
EN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
VOICE = os.environ.get("VOICE_ID", "TX3LPaxmHKxFdv7VOQHJ")  # owner choice 19 Nov 2026: ElevenLabs premade young male "social media" voice, all channels
MODEL = "eleven_v3"
GREEN, CYAN, MAG, WHITE, RED, GREY = (40, 235, 110), (0, 220, 255), (255, 60, 200), (240, 245, 255), (255, 90, 90), (160, 170, 200)
PANEL = (24, 30, 64)

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]

# ---------- background ----------
random.seed(403)
PARTS = [(random.random() * W, random.random() * H, random.uniform(1, 3), random.uniform(20, 70)) for _ in range(90)]
BRAND, TAGLINE, PART_COL = "403 UNLOCKED", "BREAK THE LIMITS. EXPLORE THE FUTURE.", (0, 220, 255)
SUB_COL = (240, 245, 255)

def make_base(top, bottom, grid):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    if grid:
        for x in range(0, W, 90):
            d.line([(x, 0), (x, H)], fill=grid)
        for y in range(0, H, 90):
            d.line([(0, y), (W, y)], fill=grid)
    return im

BASE = make_base((6, 10, 28), (18, 8, 48), (20, 30, 70))

THEMES = {
    # 403 UNLOCKED: neon green/cyan on deep blue (default)
    "tech": None,
    # Stock market series: gold + market green on deep navy/teal
    "stocks": dict(GREEN=(0, 200, 120), CYAN=(255, 196, 0), MAG=(0, 150, 90), RED=(240, 70, 70), PANEL=(14, 34, 44),
                   PART_COL=(255, 196, 0), base=((4, 14, 22), (6, 34, 40), (14, 40, 50))),
    # Kadha Petti kids stories: bright sky, candy colours
    "kids": dict(GREEN=(255, 120, 40), CYAN=(120, 60, 200), MAG=(230, 40, 120), RED=(230, 60, 60), PANEL=(255, 250, 235),
                 PART_COL=(255, 255, 255), base=((120, 200, 255), (255, 236, 200), None)),
}

def apply_theme(name, brand=None, tagline=None):
    global GREEN, CYAN, MAG, RED, PANEL, PART_COL, BASE, BRAND, TAGLINE, SUB_COL
    if name == "kids": SUB_COL = (90, 40, 160)
    th = THEMES.get(name)
    if th:
        GREEN, CYAN, MAG, RED, PANEL, PART_COL = th["GREEN"], th["CYAN"], th["MAG"], th["RED"], th["PANEL"], th["PART_COL"]
        BASE = make_base(*th["base"])
    if brand: BRAND = brand
    if tagline is not None: TAGLINE = tagline

PHOTO = None   # (prepared PIL image, scene duration) for the scene being rendered; set by main() when the scene has "photo"
def bg(t):
    if PHOTO:
        src, D = PHOTO; k = min(1.0, t / max(0.1, D))          # slow pan across the slightly larger photo
        x0 = int((src.width - W) * (0.5 + 0.5 * math.sin(k * 1.4 - 0.7))); y0 = int((src.height - H) * k)
        return src.crop((x0, y0, x0 + W, y0 + H))
    im = BASE.copy(); d = ImageDraw.Draw(im)
    for x, y, r, sp in PARTS:
        yy = (y - sp * t) % H
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=PART_COL)
    return im

def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

# ---------- text (mixed Malayalam + Latin) ----------
ML_RE = re.compile(r"[ഀ-ൿ‌‍]")
def segs(s, size):
    out = []
    for m in re.finditer(r"[ഀ-ൿ‌‍]+[\s!?.,]*|[^ഀ-ൿ]+", s):
        p = m.group(0)
        out.append((p, font(ML, size) if ML_RE.match(p) else font(EN, int(size * 0.85))))
    return out

def tw(d, s, size):
    return sum(d.textlength(p, font=f) for p, f in segs(s, size))

def fit(d, s, size, maxw):
    while size > 28 and tw(d, s, size) > maxw:
        size -= 2
    return size

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")
def text(d, x, y, s, size, fill=WHITE, stroke=0, center=False, maxw=W - 120):
    s = EMOJI_RE.sub("", s).strip() if s.strip()[:1] not in "✓⚠" else s
    size = fit(d, s, size, maxw)
    if center:
        x = (W - tw(d, s, size)) / 2
    for p, f in segs(s, size):
        dy = (size - f.size) * 0.5 if f.path == EN else 0
        d.text((x, y + dy), p, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += d.textlength(p, font=f)

_ec = {}
def emoji(s, px):
    k = (s, px)
    if k not in _ec:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), s, font=f, embedded_color=True)
        bb = im.getbbox() or (0, 0, 160, 160)
        c = im.crop(bb); r = px / max(c.size)
        _ec[k] = c.resize((max(1, int(c.width * r)), max(1, int(c.height * r))), Image.LANCZOS)
    return _ec[k]

def glow(im, cx, cy, r, col, a=1.0):
    g = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (int(90 * a),))
    g = g.filter(ImageFilter.GaussianBlur(r * 0.4))
    im.paste(g, (0, 0), g)

# ---------- scene templates ----------
def sc_hook(s, t, D):
    im = bg(t)
    if not PHOTO:
        pulse = 0.6 + 0.4 * math.sin(t * 6)
        z = 1 + 0.08 * math.sin(t * 3)
        glow(im, W / 2, 1050, 330 * z, GREEN, pulse)
        e = emoji(s.get("icon", "⚡"), int(420 * z))
        im.paste(e, (int(W / 2 - e.width / 2), int(1050 - e.height / 2)), e)
    d = ImageDraw.Draw(im)
    text(d, 0, 230, s["title"], 100, GREEN, 5, center=True)
    if t > 0.8 and s.get("sub"):
        text(d, 0, 380, s["sub"], 70, SUB_COL, 3 if SUB_COL == WHITE or sum(SUB_COL) > 600 else 0, center=True)
    return im

def sc_bullets(s, t, D):
    im = bg(t); d = ImageDraw.Draw(im)
    text(d, 0, 200, s["title"], 74, CYAN, 4, center=True)
    if s.get("icon"):
        e = emoji(s["icon"], 220); im.paste(e, (int(W / 2 - 110), 360), e); d = ImageDraw.Draw(im)
    items = s["items"]; gap = (D * 0.75) / max(1, len(items))
    for i, it in enumerate(items):
        a = ease((t - 0.4 - i * gap) / 0.5)
        if a <= 0:
            continue
        y = 680 + i * 230; x = 90 + (1 - a) * 300
        d.rounded_rectangle([x, y, x + 900, y + 190], radius=40, fill=PANEL, outline=GREEN if i % 2 == 0 else CYAN, width=5)
        text(d, x + 50, y + 55, it, 60, WHITE, 0, maxw=800)
    return im

def sc_compare(s, t, D):
    im = bg(t); d = ImageDraw.Draw(im)
    text(d, 0, 200, s["title"], 80, WHITE, 4, center=True)
    for i, it in enumerate(s["left"]):
        a = ease((t - 0.3 - i * 0.6) / 0.5)
        if a > 0:
            y = 430 + i * 200
            d.rounded_rectangle([90, y, 990, y + 160], radius=36, fill=PANEL, outline=GREEN, width=5)
            text(d, 140, y + 45, it, 62, GREEN, 0, maxw=800)
    for i, it in enumerate(s["right"]):
        a = ease((t - D * 0.45 - i * 0.6) / 0.5)
        if a > 0:
            y = 1000 + i * 200
            d.rounded_rectangle([90, y, 990, y + 160], radius=36, fill=PANEL, outline=RED, width=5)
            text(d, 140, y + 45, it, 62, RED, 0, maxw=800)
    return im

def sc_steps(s, t, D):
    im = bg(t); d = ImageDraw.Draw(im)
    text(d, 0, 200, s["title"], 72, CYAN, 4, center=True)
    items = s["items"]; gap = (D * 0.7) / max(1, len(items))
    for i, it in enumerate(items):
        if t < 0.3 + i * gap:
            continue
        y = 420 + i * 220
        d.rounded_rectangle([110, y, 970, y + 160], radius=36, fill=PANEL, outline=CYAN, width=4)
        d.ellipse([140, y + 35, 230, y + 125], fill=GREEN)
        d.text((172, y + 45), str(i + 1), font=font(EN, 56), fill=(0, 30, 10))
        text(d, 270, y + 45, it, 58, WHITE, 0, maxw=670)
        if i < len(items) - 1:
            d.polygon([(540, y + 170), (570, y + 170), (555, y + 205)], fill=CYAN)
    if s.get("note"):
        text(d, 110, 1720, s["note"], 34, GREY)
    return im

def sc_cta(s, t, D):
    im = bg(t); d = ImageDraw.Draw(im)
    b = ease(t / 0.8)
    if s.get("keyword"):  # comment-keyword CTA: only when a real guide link exists
        text(d, 0, 260, "SUBSCRIBE + COMMENT", 64, WHITE, 3, center=True)
        d.rounded_rectangle([170, 520 - 40 * b, 910, 760 - 40 * b], radius=60, fill=WHITE)
        d.polygon([(300, 720 - 40 * b), (260, 820 - 40 * b), (380, 720 - 40 * b)], fill=WHITE)
        text(d, 0, 565 - 40 * b, s["keyword"], 110, MAG, 0, center=True, maxw=680)
        if t > 1.5:
            ay = 1000 + 25 * math.sin(t * 6)
            d.polygon([(W / 2 - 60, ay), (W / 2 + 60, ay), (W / 2, ay + 110)], fill=CYAN)
            d.rounded_rectangle([250, 1150, 830, 1260], radius=55, outline=CYAN, width=5)
            text(d, 0, 1175, "PINNED COMMENT", 50, CYAN, center=True)
    else:  # subscribe-only CTA
        sc = 1 + 0.05 * math.sin(t * 5)
        w, h = 640 * sc * b, 170 * sc * b
        if b > 0.05:
            d.rounded_rectangle([W / 2 - w / 2, 640 - h / 2, W / 2 + w / 2, 640 + h / 2], radius=40, fill=(230, 30, 40))
            if b > 0.9:
                text(d, 0, 600, "SUBSCRIBE", 84, WHITE, 0, center=True)
        if t > 1.2:
            e = emoji("🔔", 160); im.paste(e, (int(W / 2 - 80), 800), e); d = ImageDraw.Draw(im)
    if NEXT_TIME and not s.get("keyword") and t > 0.8:
        time_badge(im, 1150, NEXT_TIME); d = ImageDraw.Draw(im)
    if t > D - 4.5:
        text(d, 0, 1460, BRAND, 110, GREEN, 5, center=True)
        if TAGLINE: text(d, 0, 1620, TAGLINE, 40, SUB_COL, 2 if sum(SUB_COL) > 600 else 0, center=True)
    return im

def sc_quiz(s, t, D):
    im = bg(t); d = ImageDraw.Draw(im)
    text(d, 0, 220, "QUIZ TIME", 96, CYAN, 5, center=True)
    text(d, 0, 420, s["question"], 62, WHITE, 3, center=True, maxw=960)
    for i, opt in enumerate(s["options"]):
        a = ease((t - 0.8 - i * 0.5) / 0.4)
        if a <= 0: continue
        y = 650 + i * 210; x = 120 + (1 - a) * 300
        d.rounded_rectangle([x, y, x + 840, y + 170], radius=40, fill=PANEL, outline=CYAN, width=5)
        d.ellipse([x + 30, y + 40, x + 120, y + 130], fill=CYAN)
        d.text((x + 55, y + 50), "ABCD"[i], font=font(EN, 60), fill=(10, 20, 20))
        text(d, x + 160, y + 50, opt, 60, WHITE, 0, maxw=640)
    if t > D * 0.55:
        e = emoji("💬", 150); im.paste(e, (int(W / 2 - 75), 1380), e); d = ImageDraw.Draw(im)
        text(d, 0, 1560, "Answer comment ചെയ്യൂ!", 60, GREEN, 3, center=True)
    return im

def sc_chart(s, t, D):
    im = bg(t); d = ImageDraw.Draw(im)
    text(d, 0, 200, s["title"], 74, CYAN, 4, center=True)
    rnd = random.Random(s.get("seed", 7)); n = 14; trend = s.get("trend", "up")
    price, candles = 100.0, []
    for i in range(n):
        drift = {"up": 2.2, "down": -2.2}.get(trend, 0) + rnd.uniform(-4, 4)
        o = price; c = price + drift; hi = max(o, c) + rnd.uniform(0.5, 3); lo = min(o, c) - rnd.uniform(0.5, 3)
        candles.append((o, c, hi, lo)); price = c
    lo_all = min(c[3] for c in candles); hi_all = max(c[2] for c in candles)
    y0, y1 = 1450, 520
    Y = lambda v: y0 - (v - lo_all) / (hi_all - lo_all) * (y0 - y1)
    shown = int(min(n, (t / (D * 0.7)) * n + 1))
    for i, (o, c, hi, lo) in enumerate(candles[:shown]):
        x = 110 + i * 62; col = GREEN if c >= o else RED
        d.line([x + 18, Y(hi), x + 18, Y(lo)], fill=col, width=4)
        d.rectangle([x, Y(max(o, c)), x + 36, Y(min(o, c)) + 2], fill=col)
    for lbl_i, lbl in enumerate(s.get("labels", [])):
        if t > D * (0.35 + 0.25 * lbl_i):
            text(d, 0, 1540 + lbl_i * 95, lbl, 56, WHITE, 3, center=True)
    if s.get("note"):
        text(d, 110, 1760, s["note"], 32, GREY)
    return im

SERIES, DISCLAIMER, NEXT_TIME = None, None, None

def time_badge(im, y, label):
    d = ImageDraw.Draw(im); w = min(1000, tw(d, label, 50) + 190)
    d.rounded_rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + 130], radius=65, fill=(255, 210, 60), outline=(200, 90, 20), width=6)
    e = emoji("⏰", 90); im.paste(e, (int(W / 2 - w / 2 + 35), y + 20), e)
    text(ImageDraw.Draw(im), W / 2 - w / 2 + 145, y + 34, label, 50, (90, 30, 10), 0, maxw=w - 160)
def overlay(im):
    if not (SERIES or DISCLAIMER): return im
    d = ImageDraw.Draw(im)
    if SERIES:
        day, total, name = SERIES["day"], SERIES["total"], SERIES["name"]
        d.rounded_rectangle([60, 60, 1020, 140], radius=40, fill=(0, 0, 0))
        d.rounded_rectangle([60, 60, 60 + 960 * day / total, 140], radius=40, fill=CYAN)
        text(d, 0, 75, f"{SERIES.get('label', 'DAY')} {day}/{total}  ·  {name}", 44, WHITE, 3, center=True)
    if DISCLAIMER:
        text(d, 0, 1850, DISCLAIMER, 28, GREY, 2, center=True, maxw=1000)
    return im

# ---------- kids story scenes ----------
def story_bg(kind, t):
    top, bot = {"night": ((20, 24, 70), (60, 50, 120)), "river": ((130, 205, 255), (200, 240, 255))}.get(kind, ((125, 200, 255), (215, 240, 255)))
    im = make_base(top, bot, None); d = ImageDraw.Draw(im)
    if kind == "night":
        for i in range(40):
            x, y = (i * 263) % W, (i * 137) % 1000
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 255, 220))
        e = emoji("🌙", 180); im.paste(e, (800, 160), e)
    else:
        d.ellipse([770, 120 + 8 * math.sin(t), 970, 320 + 8 * math.sin(t)], fill=(255, 214, 60))
        for cx in (180 + (t * 25) % 1300 - 200, 650 + (t * 15) % 1300 - 400):
            for dx, r in ((0, 60), (60, 75), (130, 55)):
                d.ellipse([cx + dx - r, 300 - r, cx + dx + r, 300 + r], fill=(255, 255, 255))
    gy = 1250
    if kind == "river":
        d.rectangle([0, gy, W, H], fill=(90, 190, 90)); d.rectangle([0, gy + 120, W, gy + 330], fill=(70, 160, 230))
    else:
        d.rectangle([0, gy, W, H], fill=(70, 50, 90) if kind == "night" else (100, 200, 90))
    for x, sz in ((40, 300), (760, 340), (430, 220)) if kind in ("forest", "race", "night") else ((20, 220), (840, 220)) if kind == "palace" else ((60, 260),):
        e = emoji("🌳", sz); im.paste(e, (x, gy - e.height + 40), e)
    if kind == "race":
        e = emoji("🏁", 170); im.paste(e, (880, gy - 150), e)
    if kind == "palace":
        e = emoji("🏰", 560); im.paste(e, (int(W / 2 - e.width / 2), gy - e.height + 60), e)
    if kind == "river":
        pass
    return im

AMP = [0.0]  # per-frame narration loudness of the current scene (0..1), for lip sync
def amp_at(t):
    i = int(t * FPS)
    return AMP[i] if 0 <= i < len(AMP) else 0.0

ART = os.path.join(ROOT, "channels", "kadha", "art")
_faces = None
def face(name):
    global _faces
    if _faces is None:
        fp = os.path.join(ART, "faces.json")
        _faces = json.load(open(fp)) if os.path.exists(fp) else {}
    return _faces.get(name)

def face_overlay(spr, name, t, talk, seed):
    f = face(name)
    if not f: return spr
    blink = (t + seed * 0.83) % 3.6 < 0.14
    if not blink and talk < 0.06: return spr
    sp = spr.copy(); d = ImageDraw.Draw(sp)
    if blink:
        for ex, ey in f["eyes"]:
            # sample skin around the eye; take the median warm skin-tone sample (above-eye can hit eyebrow/hair)
            W_, H_ = sp.size; cands = []
            for px, py in ((ex, ey - f["eye_h"] - 6), (ex, ey + f["eye_h"] * 0.9), (ex - f["eye_w"] * 0.75, ey + f["eye_h"] * 0.6),
                           (ex + f["eye_w"] * 0.75, ey + f["eye_h"] * 0.6), (ex, ey - f["eye_h"] * 1.4)):
                px = int(min(max(px, 0), W_ - 1)); py = int(min(max(py, 0), H_ - 1)); c = sp.getpixel((px, py))
                if (len(c) < 4 or c[3] > 200) and c[0] > 120 and c[0] >= c[1] >= c[2] and c[0] - c[2] > 40: cands.append(c[:3])  # warm skin tones only
            cands.sort(key=sum)
            skin = cands[len(cands) // 2] if cands else sp.getpixel((ex, max(0, ey - f["eye_h"] - 6)))[:3]
            d.ellipse([ex - f["eye_w"] / 2 - 3, ey - f["eye_h"] / 2 - 3, ex + f["eye_w"] / 2 + 3, ey + f["eye_h"] / 2 + 3], fill=skin)
            d.arc([ex - f["eye_w"] / 2, ey - f["eye_h"] / 2, ex + f["eye_w"] / 2, ey + f["eye_h"] / 2 + 4], 20, 160, fill=(60, 30, 25), width=3)
    if talk >= 0.06:
        mx, my = f["mouth"]; mw = f["mouth_w"]; mh = int(4 + mw * 0.75 * min(1.0, talk * 1.4))
        d.ellipse([mx - mw / 2, my - mh / 2, mx + mw / 2, my + mh / 2], fill=(95, 25, 35))
        d.ellipse([mx - mw * 0.28, my + mh * 0.05, mx + mw * 0.28, my + mh / 2 - 1], fill=(205, 90, 100))
    return sp

SEGS = []  # [(start, end, who)] speaking turns in the current scene (seconds, scene time)
def speaker_at(t):
    for a, b, who in SEGS:
        if a <= t <= b: return who
    return None
_art = {}
def art(kind, name):
    k = (kind, name)
    if k not in _art:
        _art[k] = Image.open(os.path.join(ART, kind, name + (".png" if kind == "chars" else ".jpg"))).convert("RGBA" if kind == "chars" else "RGB")
    return _art[k]

def bg_image(name, t, D):
    src = art("bg", name); z = 1.0 + 0.08 * min(1, t / max(0.1, D))       # slow Ken Burns zoom
    h = int(H * z); w = int(src.width * h / src.height)
    im = src.resize((w, h), Image.LANCZOS)
    x0 = (w - W) // 2 + int(30 * math.sin(t * 0.3)); y0 = (h - H) // 2
    return im.crop((x0, y0, x0 + W, y0 + H))

CINE = False   # 2.5D cinematic mode for painted stories (ep "cinematic": true)
def sc_story(s, t, D):
    cam = (1.0, 0.0, 0.0); fxk = ()
    seed = sum(map(ord, s.get("caption", "") + s.get("bgimg", "")))
    if CINE and s.get("bgimg"):
        import cinema
        im, cam = cinema.bg(art("bg", s["bgimg"]), s["bgimg"], t, D, seed)
        fxk = tuple(s.get("cine_fx") or cinema.FX_FOR.get(s["bgimg"], ("dust",)))
        im = cinema.effects(im, fxk, t, seed, "back")
    else:
        im = bg_image(s["bgimg"], t, D) if s.get("bgimg") else story_bg(s.get("bg", "forest"), t)
    import characters
    for n, c in enumerate(s.get("chars", [])):
        if "img" in c:  # painted character image with movement
            hgt = c.get("h", 900); anim = c.get("anim", "idle")
            t0 = n * 0.35                                    # stagger
            lt = max(0.0, t - t0)
            who = speaker_at(t)
            speaking = (who in (c["img"], c.get("who"))) if SEGS else bool(c.get("talk"))  # "who" lets a costume image (rama_forest) speak as rama
            amp = amp_at(t) if speaking else 0.0
            spr = face_overlay(art("chars", c["img"]), c["img"], t, amp, n)
            amp = amp * float(c.get("talk_motion", 0.0))     # body motion off by default (owner); mouth still moves
            hb = hgt * (1 + 0.015 * math.sin(t * 2.4 + n) + 0.05 * amp)
            sx = 1.0; sy = 1.0
            x = c.get("x", 0.5) * W; fy = c.get("y", 0.78) * H
            if CINE and s.get("bgimg"):   # parallax: nearer layer drifts more than the background and grows a little
                z, px, py = cam; x = W / 2 + (x - W / 2) * (1 + (z - 1) * 0.6) - px * 0.55; hb *= 1 + (z - 1) * 0.5
                if lt < 0.7 and not c.get("enter"): fy += 60 * (1 - ease(lt / 0.7))   # soft rise-in
            if c.get("x2") is not None:
                x += (c["x2"] * W - x) * min(1, t / max(0.1, D * 0.85))
            if anim == "walk" or (c.get("x2") is not None and anim == "idle"):
                step = abs(math.sin(t * 6 + n)); fy -= 28 * step; rot = 4 * math.sin(t * 6 + n)
            elif anim == "jump":
                ph = (t * 1.6 + n * 0.3) % 1.0; up = math.sin(ph * math.pi)
                fy -= 160 * up; sy = 1 + 0.06 * up; sx = 1 - 0.04 * up
                if ph < 0.08 or ph > 0.92: sy, sx = 0.94, 1.05        # squash on landing
                rot = 0
            else:
                fy -= 10 * abs(math.sin(t * 2.0 + n)) + 40 * amp; rot = 2.0 * math.sin(t * 1.8 + n * 1.3) + 3 * amp * math.sin(t * 9)
            ent = c.get("enter")
            if ent and lt < 0.7:
                k = 1 - ease(lt / 0.7)
                if ent == "left": x -= k * 700
                elif ent == "right": x += k * 700
                elif ent == "pop": sx *= (1 - k) * 1.15 + 0.001; sy *= (1 - k) * 1.15 + 0.001
            w0 = max(2, int(spr.width * hb / spr.height * sx)); h0 = max(2, int(hb * sy))
            sp = spr.resize((w0, h0), Image.LANCZOS)
            if c.get("flip"): sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
            sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
            a = 1.0 if ent else (min(1.0, lt / 0.5) if t < t0 + 0.5 else 1.0)
            if t < t0: a = 0.0 if not ent else 0.0
            if a > 0:
                if amp > 0.15:  # speaking glow
                    glow(im, x, fy - h0 * 0.55, h0 * 0.42, (255, 230, 150), min(1, amp))
                if a < 1:
                    sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
                im.paste(sp, (int(x - sp.width / 2), int(fy - sp.height)), sp)
                if c.get("label"):
                    fs = 32 if len(s.get("chars", [])) >= 4 else 40
                    dl = ImageDraw.Draw(im); lw = tw(dl, c["label"], fs) + 30; ly = c.get("y", 0.78) * H + 6
                    dl.rounded_rectangle([x - lw / 2, ly, x + lw / 2, ly + fs + 22], radius=26, fill=(255, 245, 210), outline=(200, 120, 20), width=3)
                    text(dl, x - lw / 2 + 15, ly + 6, c["label"], fs, (90, 40, 20), 0, maxw=lw)
            continue
        if "c" in c:  # animated 2D character
            x = c.get("x", 0.5) * W
            if c.get("x2") is not None:
                x += (c["x2"] * W - x) * min(1, t / max(0.1, D * 0.85))
            child = c["c"].endswith("_child")
            characters.draw_character(im, c["c"], x, c.get("y", 0.70) * H, c.get("h", 520 if child else 760), t,
                                      talk=amp_at(t) if c.get("talk") else 0.0, seed=n * 1.7, flip=c.get("flip", False))
            if c.get("label"):
                fs = 30 if len(s.get("chars", [])) >= 4 else 40
                dl = ImageDraw.Draw(im); lw = tw(dl, c["label"], fs) + 30; ly = c.get("y", 0.70) * H + 8
                dl.rounded_rectangle([x - lw / 2, ly, x + lw / 2, ly + fs + 22], radius=26, fill=(255, 245, 210), outline=(200, 120, 20), width=3)
                text(dl, x - lw / 2 + 15, ly + 6, c["label"], fs, (90, 40, 20), 0, maxw=lw)
            continue
        px = c.get("s", 300); x, y = c.get("x", 0.5) * W, c.get("y", 0.62) * H
        a = c.get("anim", "still"); p = min(1, t / max(0.1, D * 0.85))
        if a in ("run", "walk"):
            x2 = c.get("x2", c.get("x", 0.5)) * W; x = x + (x2 - x) * p
            y += -abs(math.sin(t * (14 if a == "run" else 5))) * (40 if a == "run" else 12)
        elif a == "bounce":
            y += -abs(math.sin(t * 4)) * 35
        e = emoji(c["e"], px)
        if c.get("flip"): e = e.transpose(Image.FLIP_LEFT_RIGHT)
        if a == "sleep": e = e.rotate(-12, expand=True)
        im.paste(e, (int(x - e.width / 2), int(y - e.height / 2)), e)
        if c.get("label"):
            dl = ImageDraw.Draw(im); lw = tw(dl, c["label"], 40) + 40
            dl.rounded_rectangle([x - lw / 2, y + e.height / 2 + 10, x + lw / 2, y + e.height / 2 + 75], radius=30, fill=(255, 245, 210), outline=(200, 120, 20), width=3)
            text(dl, x - lw / 2 + 20, y + e.height / 2 + 18, c["label"], 40, (90, 40, 20), 0, maxw=lw)
        if a == "sleep":
            z = emoji("💤", 120); im.paste(z, (int(x + 60), int(y - 200 - 25 * math.sin(t * 3))), z)
    if fxk:
        import cinema
        im = cinema.effects(im, fxk, t, seed, "front")
    fx = s.get("fx")
    if fx:
        rnd = random.Random(hash(fx) & 0xffff); sym = {"petals": "🌸", "leaves": "🍃", "sparkles": "✨", "fireflies": "✨", "stars": "⭐"}.get(fx, "✨")
        for i in range(14):
            px0, sp_, sz = rnd.random() * W, rnd.uniform(60, 160), int(rnd.uniform(40, 90))
            if fx in ("petals", "leaves"):
                py = (rnd.random() * H + t * sp_) % H; px = px0 + 40 * math.sin(t * 1.5 + i)
            else:
                py = rnd.random() * 1400 + 30 * math.sin(t * 2 + i); px = px0 + 20 * math.cos(t * 1.7 + i)
            e = emoji(sym, sz)
            if fx in ("sparkles", "fireflies"):
                al = 0.5 + 0.5 * math.sin(t * 4 + i * 1.3)
                e = e.copy(); e.putalpha(e.split()[3].point(lambda v, al=al: int(v * al)))
            im.paste(e, (int(px), int(py)), e)
    d = ImageDraw.Draw(im)
    if s.get("caption"):
        cy = 1640 if s.get("bgimg") else 1480
        d.rounded_rectangle([60, cy, 1020, cy + 200], radius=50, fill=(255, 255, 255), outline=(255, 150, 40), width=6)
        text(d, 0, cy + 60, s["caption"], 60, (60, 40, 90), 0, center=True, maxw=880)
    return im

def sc_moral(s, t, D):
    im = bg(t); d = ImageDraw.Draw(im)
    for i in range(6):
        e = emoji("⭐", 90 + 10 * int(1 + math.sin(t * 3 + i)))
        im.paste(e, (int(80 + i * 160), int(330 + 30 * math.sin(t * 2 + i))), e)
    d = ImageDraw.Draw(im)
    text(d, 0, 180, s.get("heading", "ഗുണപാഠം"), 110, (230, 60, 120), 5, center=True)
    b = ease(t / 0.8)
    if b > 0.05:
        d.rounded_rectangle([70, 620, 1010, 620 + 520 * b], radius=60, fill=(255, 255, 255), outline=(255, 150, 40), width=8)
    if b > 0.95:
        for i, line in enumerate(s["lines"]):
            text(d, 0, 700 + i * 130, line, 68, (60, 40, 90), 0, center=True, maxw=860)
    if s.get("icon"):
        e = emoji(s["icon"], 260); im.paste(e, (int(W / 2 - e.width / 2), 1250), e)
    if NEXT_TIME and s.get("heading") and t > 0.6:
        time_badge(im, 1560, NEXT_TIME)
    return im

TEMPLATES = {"hook": sc_hook, "bullets": sc_bullets, "compare": sc_compare, "steps": sc_steps, "cta": sc_cta, "quiz": sc_quiz, "chart": sc_chart, "story": sc_story, "moral": sc_moral}

# ---------- audio ----------
def tts(textline, out, voice=None):
    body = {"text": textline, "model_id": MODEL, "language_code": "ml",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice or VOICE}?output_format=mp3_44100_128",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    import time
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == 3: raise
            time.sleep(10 * (attempt + 1))
    with open(out, "wb") as f:
        f.write(data)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))

def mix(clips, sd, out, moods=None, seed=0):
    tot = sum(sd); inputs, filt, t = [], [], 0
    for i, (c, x) in enumerate(zip(clips, sd)):
        off = int((t + (0.3 if i == 0 else 0.1)) * 1000)
        inputs += ["-i", c]; filt.append(f"[{i}:a]adelay={off}|{off}[a{i}]"); t += x
    n = len(clips)
    fc = ";".join(filt) + ";" + "".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur={tot},asplit=2[nar][nar2];"
    if moods:  # story-matched Indian music composed in pipeline/music.py
        import music
        wav = out + ".music.wav"; music.write_wav(wav, music.score(list(zip(moods, sd)), seed))
        inputs += ["-i", wav]
        fc += (f"[{n}:a]volume=0.55,afade=t=in:d=1,afade=t=out:st={tot - 2}:d=2[mus];")
    else:
        fc += (f"aevalsrc='0.05*sin(2*PI*110*t)+0.035*sin(2*PI*164.8*t)+0.03*sin(2*PI*220*t)"
           f"+0.025*sin(2*PI*261.6*t)*(0.5+0.5*sin(2*PI*0.25*t))+0.04*sin(2*PI*55*t)*exp(-6*mod(t,0.5))':s=44100:d={tot}[m0];"
           f"[m0]lowpass=f=1800,afade=t=in:d=1,afade=t=out:st={tot - 2}:d=2[mus];")
    fc += (
           "[mus][nar]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];"
           "[duck][nar2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[out]", "-ar", "44100", "-t", str(tot), out], check=True)



# ---------- AI photo backgrounds (403 UNLOCKED, owner 22 Nov 2026) ----------
PHOTO_STYLE = (", photorealistic candid photo, Kerala India, natural light, shallow depth of field, vertical composition, "
               "no text, no letters, no logos, no brand names, no watermark, phones are generic modern Android smartphones without any logo, "
               "any phone or laptop screen is turned away or blurred")
CF_ACCOUNT = "d93a3d51bd1c05e669119b7955ac7aba"

def photo_path(slug, k):
    return os.path.join(ROOT, "assets", "photos", f"{slug}-{k}.jpg")

def ensure_photos(ep):
    """Generate (once) a FLUX photo for every scene that has a "photo" prompt. Cached in assets/photos/."""
    import base64, urllib.request
    for k, s in enumerate(ep["scenes"]):
        if not s.get("photo"): continue
        pth = photo_path(ep["slug"], k)
        if os.path.exists(pth): continue
        os.makedirs(os.path.dirname(pth), exist_ok=True)
        for attempt in range(3):
            try:
                req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/@cf/black-forest-labs/flux-1-schnell",
                    data=json.dumps({"prompt": s["photo"] + PHOTO_STYLE, "steps": 8}).encode(),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer proxy-injected"})
                with urllib.request.urlopen(req, timeout=180) as r:
                    open(pth, "wb").write(base64.b64decode(json.load(r)["result"]["image"]))
                break
            except Exception as e:
                print(f"photo {k} attempt {attempt + 1} failed: {e}", file=sys.stderr); time.sleep(5)

def prep_photo(pth, dim=True):
    """Scale to cover 1080x1920 with 8% margin for panning; darken top/bottom so cards and titles stay readable."""
    src = Image.open(pth).convert("RGB"); sc = max(W * 1.08 / src.width, H * 1.04 / src.height)
    im = src.resize((int(src.width * sc), int(src.height * sc)), Image.LANCZOS)
    if dim:
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); hh = im.height
        for y in range(0, hh, 4):
            f = y / hh   # smooth: dark at the top (title), lighter in the middle, dark again at the bottom
            a = int(165 - 75 * min(1, f / 0.38)) if f < 0.6 else int(90 + 80 * min(1, (f - 0.6) / 0.35))
            d.rectangle([0, y, im.width, y + 4], fill=(4, 8, 24, a))
        im = im.convert("RGBA"); im.alpha_composite(ov); im = im.convert("RGB")
    return im

# ---------- thumbnail / cover ----------
def make_thumb(ep, path):
    """1080x1920 cover (Instagram Reel cover + YouTube thumbnail). Uses ep["thumb_text"] (2 short lines) if given."""
    hook = ep["scenes"][0]
    lines = ep.get("thumb_text") or [hook.get("title", ""), hook.get("sub", "")]
    story = next((sc for sc in ep["scenes"] if sc.get("bgimg")), None)
    if story:  # painted Kadha style
        im = bg_image(story["bgimg"], 0, 1)
        shade = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(shade).rectangle([0, 0, W, 760], fill=(255, 240, 210, 150))
        im = im.convert("RGBA"); im.alpha_composite(shade); im = im.convert("RGB")
        chars = [c for c in story.get("chars", []) if "img" in c][:3]
        for i, c in enumerate(chars):
            spr = art("chars", c["img"]); h = 1150 if len(chars) == 1 else 900
            sp = spr.resize((int(spr.width * h / spr.height), h), Image.LANCZOS)
            x = W / 2 if len(chars) == 1 else 200 + i * (680 / max(1, len(chars) - 1))
            im.paste(sp, (int(x - sp.width / 2), H - sp.height - 40), sp)
        d = ImageDraw.Draw(im)
        text(d, 0, 170, lines[0], 150, (230, 80, 20), 8, center=True, maxw=1000)
        if len(lines) > 1 and lines[1]: text(d, 0, 400, lines[1], 90, (90, 30, 140), 5, center=True, maxw=1000)
    elif hook.get("photo") and os.path.exists(photo_path(ep["slug"], 0)):
        src = prep_photo(photo_path(ep["slug"], 0)); x0 = (src.width - W) // 2; im = src.crop((x0, 0, x0 + W, H)); d = ImageDraw.Draw(im)
        text(d, 0, 230, lines[0], 140, (255, 225, 40), 8, center=True, maxw=1000)
        if len(lines) > 1 and lines[1]: text(d, 0, 470, lines[1], 92, WHITE, 6, center=True, maxw=1000)
    else:
        im = bg(0.0); d = ImageDraw.Draw(im)
        glow(im, W / 2, 1150, 420, GREEN, 1.0)
        e = emoji(hook.get("icon", "⚡"), 620); im.paste(e, (int(W / 2 - e.width / 2), int(1150 - e.height / 2)), e)
        d = ImageDraw.Draw(im)
        text(d, 0, 230, lines[0], 140, (255, 225, 40), 8, center=True, maxw=1000)
        if len(lines) > 1 and lines[1]: text(d, 0, 470, lines[1], 92, WHITE, 6, center=True, maxw=1000)
        if SERIES: text(d, 0, 1640, f"DAY {SERIES['day']}", 110, CYAN, 6, center=True)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([W / 2 - 330, 1790, W / 2 + 330, 1880], radius=45, fill=(0, 0, 0))
    text(d, 0, 1805, BRAND, 54, GREEN, 0, center=True, maxw=620)
    im.convert("RGB").save(path, quality=88)

# ---------- main ----------
def main(path):
    global VOICE, SERIES, DISCLAIMER, NEXT_TIME, PHOTO, CINE
    ep = json.load(open(path, encoding="utf-8"))
    CINE = bool(ep.get("cinematic"))
    ensure_photos(ep)
    apply_theme(ep.get("theme", "tech"), ep.get("brand"), ep.get("tagline"))
    VOICE = ep.get("voice_id", VOICE); SERIES = ep.get("series"); DISCLAIMER = ep.get("disclaimer"); NEXT_TIME = ep.get("next_time")
    slug = ep["slug"]; work = os.path.join("/tmp", "short_" + slug); os.makedirs(work, exist_ok=True)
    clips, sd = [], []
    for i, s in enumerate(ep["scenes"]):
        import hashlib
        hk = hashlib.md5(json.dumps([s.get("narration"), s.get("lines"), VOICE], ensure_ascii=False).encode()).hexdigest()[:8]  # cache key = text + voice
        c = os.path.join(work, f"s{i + 1}_{hk}.mp3")
        if s.get("lines") and s["type"] == "story":  # dialogue: each line its own voice, joined with short pauses
            parts, segs, tcur = [], [], 0.0
            for j, l in enumerate(s["lines"]):
                pj = os.path.join(work, f"s{i + 1}_{j}_{hk}.mp3")
                if not os.path.exists(pj):
                    vmap_p = os.path.join(ROOT, "channels", "kadha", "voices.json")
                    vmap = json.load(open(vmap_p)) if os.path.exists(vmap_p) else {}
                    tts(l["text"], pj, l.get("voice") or vmap.get(l.get("who") or "narrator") or None)
                dj = dur(pj); segs.append((tcur, tcur + dj, l.get("who"))); parts.append(pj); tcur += dj + 0.3
            if not os.path.exists(c):
                lst = os.path.join(work, f"s{i + 1}_list.txt")
                sil = os.path.join(work, "sil.mp3")
                if not os.path.exists(sil):
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.3", "-c:a", "libmp3lame", sil], check=True)
                open(lst, "w").write("".join(f"file '{p}'\nfile '{sil}'\n" for p in parts))
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", c], check=True)
            s["_segs"] = segs
            s["narration"] = " ".join(l["text"] for l in s["lines"])
        elif not os.path.exists(c):
            tts(s["narration"], c)
        clips.append(c); sd.append(dur(c) + 0.45)
    sd[0] += 0.3; sd[-1] += 2.0
    total = sum(sd)
    if not 30 <= total <= 62:
        print(f"WARNING: duration {total:.1f}s outside 30-62s", file=sys.stderr)
    moods = [sc.get("mood", "calm") for sc in ep["scenes"]] if ep.get("music") == "indian" else None
    audio = os.path.join(work, "mix.m4a"); mix(clips, sd, audio, moods, seed=sum(map(ord, slug)))
    os.makedirs(os.path.join(ROOT, "videos"), exist_ok=True)
    out = os.path.join(ROOT, "videos", slug + ".mp4")  # same folder for all channels
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                          "-preset", "medium", "-crf", "21", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    def envelope(clip, delay):
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", clip, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
        import array
        a = array.array("h", raw); step = 8000 // FPS; pad = int(delay * FPS)
        env = [0.0] * pad + [math.sqrt(sum(v * v for v in a[i:i + step]) / max(1, len(a[i:i + step]))) / 6000 for i in range(0, len(a), step)]
        return [min(1.0, e) for e in env]
    for k, (s, D) in enumerate(zip(ep["scenes"], sd)):
        fn = TEMPLATES[s["type"]]
        AMP[:] = envelope(clips[k], 0.3 if k == 0 else 0.1) if s["type"] == "story" else [0.0]
        dl0 = 0.3 if k == 0 else 0.1
        SEGS[:] = [(a + dl0, b + dl0, w) for a, b, w in s.get("_segs", [])]
        pp = photo_path(slug, k)
        PHOTO = (prep_photo(pp), D) if s.get("photo") and os.path.exists(pp) else None
        for i in range(int(round(D * FPS))):
            im = overlay(fn(s, i / FPS, D))
            if i < 6:
                im = Image.blend(Image.new("RGB", (W, H)), im, (i + 1) / 6)
            p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    make_thumb(ep, os.path.join(ROOT, "videos", slug + "_thumb.jpg"))
    chars = sum(len(s["narration"]) for s in ep["scenes"])
    print(json.dumps({"video": out, "seconds": round(total, 1), "tts_chars": chars}))

if __name__ == "__main__":
    main(sys.argv[1])
