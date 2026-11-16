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
import json, math, os, random, re, subprocess, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf"
EN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
VOICE = os.environ.get("VOICE_ID", "TyWXr0PTH6rgkJ5wKSZe")  # Abhilash S (ElevenLabs shared library)
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
BASE = Image.new("RGB", (W, H))
_d = ImageDraw.Draw(BASE)
for y in range(H):
    t = y / H
    _d.line([(0, y), (W, y)], fill=(int(6 + 12 * t), int(10 - 2 * t), int(28 + 20 * t)))
for x in range(0, W, 90):
    _d.line([(x, 0), (x, H)], fill=(20, 30, 70))
for y in range(0, H, 90):
    _d.line([(0, y), (W, y)], fill=(20, 30, 70))

def bg(t):
    im = BASE.copy(); d = ImageDraw.Draw(im)
    for x, y, r, sp in PARTS:
        yy = (y - sp * t) % H
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=CYAN)
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
        _ec[k] = im.crop(bb).resize((px, px), Image.LANCZOS)
    return _ec[k]

def glow(im, cx, cy, r, col, a=1.0):
    g = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (int(90 * a),))
    g = g.filter(ImageFilter.GaussianBlur(r * 0.4))
    im.paste(g, (0, 0), g)

# ---------- scene templates ----------
def sc_hook(s, t, D):
    im = bg(t)
    pulse = 0.6 + 0.4 * math.sin(t * 6)
    z = 1 + 0.08 * math.sin(t * 3)
    glow(im, W / 2, 1050, 330 * z, GREEN, pulse)
    e = emoji(s.get("icon", "⚡"), int(420 * z))
    im.paste(e, (int(W / 2 - e.width / 2), int(1050 - e.height / 2)), e)
    d = ImageDraw.Draw(im)
    text(d, 0, 230, s["title"], 100, GREEN, 5, center=True)
    if t > 0.8 and s.get("sub"):
        text(d, 0, 380, s["sub"], 70, WHITE, 3, center=True)
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
    text(d, 0, 260, "SUBSCRIBE + COMMENT", 64, WHITE, 3, center=True)
    d.rounded_rectangle([170, 520 - 40 * b, 910, 760 - 40 * b], radius=60, fill=WHITE)
    d.polygon([(300, 720 - 40 * b), (260, 820 - 40 * b), (380, 720 - 40 * b)], fill=WHITE)
    text(d, 0, 565 - 40 * b, s["keyword"], 110, MAG, 0, center=True, maxw=680)
    if t > 1.5:
        ay = 1000 + 25 * math.sin(t * 6)
        d.polygon([(W / 2 - 60, ay), (W / 2 + 60, ay), (W / 2, ay + 110)], fill=CYAN)
        d.rounded_rectangle([250, 1150, 830, 1260], radius=55, outline=CYAN, width=5)
        text(d, 0, 1175, "PINNED COMMENT", 50, CYAN, center=True)
    if t > D - 4:
        text(d, 0, 1460, "403 UNLOCKED", 110, GREEN, 5, center=True)
        text(d, 0, 1620, "BREAK THE LIMITS. EXPLORE THE FUTURE.", 40, WHITE, 2, center=True)
    return im

TEMPLATES = {"hook": sc_hook, "bullets": sc_bullets, "compare": sc_compare, "steps": sc_steps, "cta": sc_cta}

# ---------- audio ----------
def tts(textline, out):
    body = {"text": textline, "model_id": MODEL, "language_code": "ml",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    with urllib.request.urlopen(req, timeout=180) as r, open(out, "wb") as f:
        f.write(r.read())

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))

def mix(clips, sd, out):
    tot = sum(sd); inputs, filt, t = [], [], 0
    for i, (c, x) in enumerate(zip(clips, sd)):
        off = int((t + (0.3 if i == 0 else 0.1)) * 1000)
        inputs += ["-i", c]; filt.append(f"[{i}:a]adelay={off}|{off}[a{i}]"); t += x
    n = len(clips)
    fc = ";".join(filt) + ";" + "".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur={tot},asplit=2[nar][nar2];"
    fc += (f"aevalsrc='0.05*sin(2*PI*110*t)+0.035*sin(2*PI*164.8*t)+0.03*sin(2*PI*220*t)"
           f"+0.025*sin(2*PI*261.6*t)*(0.5+0.5*sin(2*PI*0.25*t))+0.04*sin(2*PI*55*t)*exp(-6*mod(t,0.5))':s=44100:d={tot}[m0];"
           f"[m0]lowpass=f=1800,afade=t=in:d=1,afade=t=out:st={tot - 2}:d=2[mus];"
           "[mus][nar]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];"
           "[duck][nar2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[out]", "-ar", "44100", "-t", str(tot), out], check=True)

# ---------- main ----------
def main(path):
    ep = json.load(open(path, encoding="utf-8"))
    slug = ep["slug"]; work = os.path.join("/tmp", "short_" + slug); os.makedirs(work, exist_ok=True)
    clips, sd = [], []
    for i, s in enumerate(ep["scenes"]):
        c = os.path.join(work, f"s{i + 1}.mp3")
        if not os.path.exists(c):
            tts(s["narration"], c)
        clips.append(c); sd.append(dur(c) + 0.45)
    sd[0] += 0.3; sd[-1] += 2.0
    total = sum(sd)
    if not 30 <= total <= 62:
        print(f"WARNING: duration {total:.1f}s outside 30-62s", file=sys.stderr)
    audio = os.path.join(work, "mix.m4a"); mix(clips, sd, audio)
    os.makedirs(os.path.join(ROOT, "videos"), exist_ok=True)
    out = os.path.join(ROOT, "videos", slug + ".mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                          "-preset", "medium", "-crf", "21", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for s, D in zip(ep["scenes"], sd):
        fn = TEMPLATES[s["type"]]
        for i in range(int(round(D * FPS))):
            im = fn(s, i / FPS, D)
            if i < 6:
                im = Image.blend(Image.new("RGB", (W, H)), im, (i + 1) / 6)
            p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    TEMPLATES[ep["scenes"][0]["type"]](ep["scenes"][0], 2.0, 6).save(os.path.join(ROOT, "videos", slug + "_thumb.jpg"), quality=90)
    chars = sum(len(s["narration"]) for s in ep["scenes"])
    print(json.dumps({"video": out, "seconds": round(total, 1), "tts_chars": chars}))

if __name__ == "__main__":
    main(sys.argv[1])
