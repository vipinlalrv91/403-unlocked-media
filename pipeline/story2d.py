#!/usr/bin/env python3
"""Flat 2D slice-of-life story reels (owner, 28 Nov 2026): simple cartoon characters, big Malayalam text lines, soft music, no voice.
  python3 pipeline/story2d.py stories/<name>.json   -> videos/<name>.mp4 (+ _thumb.jpg)
Story JSON: {"slug", "brand", "scenes": [{"bg": gate|classroom|canteen|night|sunset|room, "dur": s, "mood": calm|happy|sad,
             "lines": ["...", "..."], "chars": [{"x":0.5,"y":0.78,"s":1.0,"shirt":"#7aa6a1","walk":true,"wave":false,"glasses":false}]}]}"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, SS, FPS = 1080, 1920, 2, 30
ML = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf"
EN = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
import re
_fc = {}
def F(path, px):
    k = (path, px)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, px)
    return _fc[k]
EMO = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")
def runs(s):
    out = []
    for ch in s:
        ml = '\u0D00' <= ch <= '\u0D7F' or ch in '\u200c\u200d'
        kind = 'ml' if ml else ('sp' if ch == ' ' else 'en')
        if out and (out[-1][0] == kind or kind == 'sp'): out[-1][1] += ch
        else: out.append([kind, ch])
    return [(ML if k in ('ml', 'sp') else EN, t) for k, t in out]
def mwidth(d, s, px): return sum(d.textlength(t, font=F(f, px)) for f, t in runs(s))
def mtext(d, xy, s, px, fill, stroke=0, stroke_fill=(0, 0, 0), center_w=None, maxw=None):
    s = EMO.sub("", s).strip()
    if maxw:
        while px > 20 and mwidth(d, s, px) > maxw: px -= 2
    x, y = xy
    if center_w: x = (center_w - mwidth(d, s, px)) / 2
    for f, t in runs(s):
        d.text((x, y), t, font=F(f, px), fill=fill, stroke_width=stroke, stroke_fill=stroke_fill); x += d.textlength(t, font=F(f, px))
FONT = 64 * SS
SMALL = 34 * SS

def lerp(a, b, k): return a + (b - a) * k
def ease(k): k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)
def mix(c1, c2, k): return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))
def hx(c): c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

def sky(im, top, bot, y1=None):
    d = ImageDraw.Draw(im); y1 = y1 or im.height
    for y in range(0, y1, 4):
        d.rectangle([0, y, im.width, y + 4], fill=mix(top, bot, y / y1))

def palm(d, x, y, s, col=(58, 74, 48)):
    d.line([(x, y), (x - 20 * s, y - 520 * s)], fill=(86, 62, 44), width=int(26 * s))
    cx, cy = x - 20 * s, y - 520 * s
    for a in range(0, 360, 40):
        r = math.radians(a)
        d.line([(cx, cy), (cx + math.cos(r) * 230 * s, cy + math.sin(r) * 110 * s + 60 * s)], fill=col, width=int(22 * s))

def college(d, w, h, tone=(214, 198, 168), roof=(170, 140, 110)):
    s = SS
    d.polygon([(w * 0.08, h * 0.37), (w * 0.5, h * 0.23), (w * 0.92, h * 0.37)], fill=roof)
    d.rectangle([w * 0.1, h * 0.37, w * 0.9, h * 0.62], fill=tone)
    for i in range(5):
        x = w * (0.13 + i * 0.18)
        d.rectangle([x, h * 0.37, x + w * 0.06, h * 0.62], fill=mix(tone, (255, 255, 255), 0.25))
    for i in range(4):
        x = w * (0.2 + i * 0.17)
        d.rectangle([x, h * 0.41, x + w * 0.08, h * 0.47], fill=(120, 150, 110), outline=(70, 60, 50), width=6 * s)
    d.rectangle([w * 0.2, h * 0.47, w * 0.8, h * 0.485], fill=(220, 180, 80))
    d.rectangle([w * 0.25, h * 0.5, w * 0.75, h * 0.52], fill=(170, 70, 60))
    d.rectangle([w * 0.18, h * 0.47, w * 0.24, h * 0.64], fill=mix(tone, (255, 255, 255), 0.35))
    d.rectangle([w * 0.76, h * 0.47, w * 0.82, h * 0.64], fill=mix(tone, (255, 255, 255), 0.35))

def background(kind, w, h, t):
    im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im)
    if kind in ("gate", "sunset"):
        if kind == "gate": sky(im, (176, 186, 132), (214, 214, 170))
        else: sky(im, (240, 150, 90), (250, 210, 150))
        college(d, w, h, tone=(214, 198, 168) if kind == "gate" else (220, 170, 130), roof=(170, 140, 110) if kind == "gate" else (170, 100, 80))
        green = (96, 128, 80) if kind == "gate" else (120, 110, 70)
        d.rectangle([0, h * 0.6, w, h], fill=green)
        d.polygon([(w * 0.38, h * 0.62), (w * 0.62, h * 0.62), (w * 0.95, h), (w * 0.05, h)], fill=(205, 186, 140) if kind == "gate" else (210, 160, 110))
        for x in (0.02, 0.98): palm(d, w * x, h * 0.62, SS * 1.1, (58, 74, 48) if kind == "gate" else (80, 60, 40))
        for bx in (0.12, 0.88): d.ellipse([w * bx - 180, h * 0.57, w * bx + 180, h * 0.66], fill=mix(green, (0, 0, 0), 0.15))
    elif kind == "classroom":
        sky(im, (232, 220, 190), (210, 196, 166))
        d.rectangle([w * 0.12, h * 0.2, w * 0.88, h * 0.38], fill=(46, 72, 58), outline=(120, 90, 60), width=14 * SS)
        mtext(d, (w * 0.2, h * 0.26), "Welcome 1st Year", SMALL, (230, 230, 220))
        for x in (0.02, 0.84):
            d.rectangle([w * x, h * 0.1, w * x + w * 0.14, h * 0.2], fill=(170, 210, 230), outline=(120, 90, 60), width=8 * SS)
        d.rectangle([0, h * 0.62, w, h], fill=(150, 120, 90))
        for row in range(2):
            y = h * (0.66 + row * 0.14)
            d.rectangle([w * 0.06, y, w * 0.94, y + h * 0.03], fill=(120, 80, 50))
    elif kind == "canteen":
        sky(im, (246, 226, 180), (232, 200, 150))
        d.rectangle([0, h * 0.18, w, h * 0.22], fill=(200, 80, 60))
        mtext(d, (w * 0.06, h * 0.183), "CANTEEN", SMALL, (255, 245, 220))
        d.rectangle([w * 0.05, h * 0.3, w * 0.4, h * 0.45], fill=(180, 140, 100))
        for i in range(5): d.ellipse([w * (0.08 + i * 0.065), h * 0.27, w * (0.08 + i * 0.065) + 50 * SS, h * 0.3], fill=(240, 230, 210))
        d.rectangle([0, h * 0.62, w, h], fill=(190, 160, 120))
    elif kind == "night":
        sky(im, (24, 30, 60), (50, 50, 80))
        d.rectangle([w * 0.65, h * 0.12, w * 0.92, h * 0.28], fill=(30, 40, 80), outline=(90, 80, 70), width=10 * SS)
        d.ellipse([w * 0.78, h * 0.15, w * 0.85, h * 0.19], fill=(250, 240, 200))
        glow = Image.new("RGB", (w, h), (0, 0, 0)); gd = ImageDraw.Draw(glow)
        gd.ellipse([w * 0.1, h * 0.35, w * 0.9, h * 0.85], fill=(130, 100, 40)); glow = glow.filter(ImageFilter.GaussianBlur(160))
        import numpy as np
        im = Image.fromarray(np.clip(np.asarray(im, dtype=np.int16) + np.asarray(glow, dtype=np.int16), 0, 255).astype('uint8'))
        d = ImageDraw.Draw(im)
        d.rectangle([0, h * 0.64, w, h], fill=(70, 50, 40))
        d.rectangle([w * 0.05, h * 0.62, w * 0.95, h * 0.66], fill=(110, 80, 55))
        for i in range(4): d.rectangle([w * 0.62, h * (0.6 - i * 0.012), w * 0.84, h * (0.612 - i * 0.012)], fill=[(200, 60, 60), (60, 120, 200), (230, 190, 70), (90, 160, 90)][i])
        d.line([(w * 0.2, h * 0.62), (w * 0.2, h * 0.5)], fill=(60, 60, 60), width=10 * SS)
        d.polygon([(w * 0.14, h * 0.5), (w * 0.26, h * 0.5), (w * 0.23, h * 0.46), (w * 0.17, h * 0.46)], fill=(230, 200, 90))
    elif kind == "room":
        sky(im, (200, 214, 222), (176, 190, 200))
        d.rectangle([w * 0.1, h * 0.14, w * 0.5, h * 0.3], fill=(150, 190, 210), outline=(240, 240, 240), width=10 * SS)
        d.rectangle([0, h * 0.62, w, h], fill=(120, 130, 140))
        d.rectangle([w * 0.05, h * 0.6, w * 0.95, h * 0.64], fill=(90, 70, 60))
    return im

def person(d, x, y, s, shirt=(122, 166, 161), skin=(150, 100, 70), hair=(30, 24, 20), t=0.0, walk=False, wave=False,
           blink=False, glasses=False, bag=True, sad=False, seed=0):
    S = s * SS
    sw = math.sin(t * 7 + seed) if walk else math.sin(t * 1.5 + seed) * 0.15
    bob = abs(math.sin(t * 7 + seed)) * 8 * S if walk else math.sin(t * 2 + seed) * 2 * S
    y = y - bob
    pants = (60, 58, 70)
    # legs
    for k in (-1, 1):
        lx = x + k * 26 * S
        d.line([(lx, y - 150 * S), (lx + k * sw * 30 * S * (1 if k > 0 else -1), y)], fill=pants, width=int(30 * S))
        d.ellipse([lx - 22 * S + k * sw * 30 * S * (1 if k > 0 else -1), y - 10 * S, lx + 22 * S + k * sw * 30 * S * (1 if k > 0 else -1), y + 12 * S], fill=(40, 36, 40))
    # bag behind
    if bag: d.rounded_rectangle([x - 78 * S, y - 330 * S, x + 78 * S, y - 150 * S], radius=int(24 * S), fill=(70, 110, 180))
    # body
    d.rounded_rectangle([x - 62 * S, y - 330 * S, x + 62 * S, y - 140 * S], radius=int(26 * S), fill=shirt)
    if bag:
        for k in (-1, 1): d.line([(x + k * 34 * S, y - 330 * S), (x + k * 34 * S, y - 170 * S)], fill=(50, 70, 120), width=int(14 * S))
    # arms
    for k in (-1, 1):
        ax0, ay0 = x + k * 62 * S, y - 315 * S
        if wave and k == 1:
            ang = -1.9 + math.sin(t * 9) * 0.35
        else:
            ang = math.pi / 2 - k * 0.32 - (sw * 0.45 * k if walk else 0)
        ax1, ay1 = ax0 + math.cos(ang) * 185 * S, ay0 + math.sin(ang) * 185 * S
        d.line([(ax0, ay0), (ax1, ay1)], fill=shirt, width=int(26 * S))
        d.ellipse([ax1 - 14 * S, ay1 - 14 * S, ax1 + 14 * S, ay1 + 14 * S], fill=skin)
    # neck + head
    d.rectangle([x - 16 * S, y - 360 * S, x + 16 * S, y - 325 * S], fill=skin)
    hx0, hy0 = x, y - 430 * S
    d.ellipse([hx0 - 72 * S, hy0 - 72 * S, hx0 + 72 * S, hy0 + 72 * S], fill=skin)
    d.chord([hx0 - 76 * S, hy0 - 84 * S, hx0 + 76 * S, hy0 + 40 * S], 180, 360, fill=hair)
    for k in (-1, 1):
        ex = hx0 + k * 28 * S; ey = hy0 + 4 * S
        if blink: d.line([(ex - 16 * S, ey), (ex + 16 * S, ey)], fill=(30, 30, 30), width=int(6 * S))
        else:
            d.ellipse([ex - 20 * S, ey - 20 * S, ex + 20 * S, ey + 20 * S], fill=(255, 255, 255), outline=(30, 30, 30), width=int(4 * S))
            d.ellipse([ex - 9 * S, ey - 9 * S, ex + 9 * S, ey + 9 * S], fill=(25, 25, 25))
        if glasses: d.ellipse([ex - 26 * S, ey - 26 * S, ex + 26 * S, ey + 26 * S], outline=(30, 30, 30), width=int(5 * S))
    if sad: d.arc([hx0 - 20 * S, hy0 + 40 * S, hx0 + 20 * S, hy0 + 62 * S], 200, 340, fill=(60, 30, 30), width=int(6 * S))
    else: d.arc([hx0 - 22 * S, hy0 + 18 * S, hx0 + 22 * S, hy0 + 48 * S], 20, 160, fill=(60, 30, 30), width=int(6 * S))

def text_block(im, lines, t, dur):
    w, h = im.size; y0 = h * 0.70
    for i, line in enumerate(lines):
        a = ease((t - 0.3 - i * dur * 0.32) / 0.6)
        if a <= 0: continue
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        y = y0 + i * 100 * SS + (1 - a) * 30 * SS
        mtext(ld, (0, y), line, FONT, (255, 255, 255, int(255 * a)), stroke=7 * SS, stroke_fill=(20, 20, 20, int(255 * a)), center_w=w, maxw=w * 0.9)
        im.paste(layer, (0, 0), layer)

def dust(im, t, seed=1):
    d = ImageDraw.Draw(im); w, h = im.size
    for i in range(18):
        r = ((i * 7919 + seed * 104729) % 1000) / 1000
        x = (r * w + math.sin(t * 0.3 + i) * 40) % w
        y = (h * 0.6 - (t * 30 * SS + i * 97 * SS) % (h * 0.55))
        a = 4 * SS
        d.ellipse([x - a, y - a, x + a, y + a], fill=(255, 245, 200))

def render(path):
    st = json.load(open(path, encoding="utf-8")); slug = st["slug"]
    work = os.path.join("/tmp", "story2d_" + slug); os.makedirs(work, exist_ok=True)
    frames = os.path.join(work, "f"); os.makedirs(frames, exist_ok=True)
    for f in os.listdir(frames): os.remove(os.path.join(frames, f))
    n = 0; moods = []
    for si, sc in enumerate(st["scenes"]):
        D = sc["dur"]; moods.append((sc.get("mood", "calm"), D))
        bg = background(sc["bg"], W * SS, H * SS, 0)
        for fi in range(int(D * FPS)):
            t = fi / FPS
            z = 1 + 0.03 * t / D
            im = bg.resize((int(W * SS * z), int(H * SS * z)))
            ox = (im.width - W * SS) // 2; oy = (im.height - H * SS) // 2
            im = im.crop((ox, oy, ox + W * SS, oy + H * SS))
            d = ImageDraw.Draw(im)
            for ci, c in enumerate(sc.get("chars", [])):
                x = c.get("x", 0.5) * W * SS
                if c.get("walk_from") is not None: x = lerp(c["walk_from"], c.get("x", 0.5), ease(t / min(D, c.get("walk_time", 2.5)))) * W * SS
                walking = c.get("walk", False) and (c.get("walk_from") is None or t < c.get("walk_time", 2.5))
                blink = (int((t + ci * 0.7) * 10) % 37) == 0
                person(d, x, c.get("y", 0.62) * H * SS, c.get("s", 1.0), shirt=hx(c.get("shirt", "#7aa6a1")), skin=hx(c.get("skin", "#96644a")),
                       hair=hx(c.get("hair", "#1e1814")), t=t, walk=walking, wave=c.get("wave", False), blink=blink,
                       glasses=c.get("glasses", False), bag=c.get("bag", True), sad=c.get("sad", False), seed=ci)
            if sc["bg"] in ("classroom", "canteen"):
                ty = H * SS * 0.585
                d.rectangle([W * SS * 0.04, ty, W * SS * 0.96, ty + 40 * SS], fill=(120, 80, 50) if sc["bg"] == "classroom" else (160, 110, 70))
                d.rectangle([W * SS * 0.06, ty + 40 * SS, W * SS * 0.94, H * SS * 0.69], fill=(100, 66, 42) if sc["bg"] == "classroom" else (140, 95, 60))
                if sc["bg"] == "classroom":
                    for i in range(3): d.rectangle([W * SS * (0.18 + i * 0.25), ty - 14 * SS, W * SS * (0.27 + i * 0.25), ty], fill=[(220, 90, 80), (80, 130, 200), (240, 200, 90)][i])
            if sc["bg"] in ("canteen",) and sc.get("chai", True):
                for i in range(4):
                    cx = W * SS * (0.2 + i * 0.2); cy = H * SS * 0.585
                    d.rounded_rectangle([cx - 26, cy - 60, cx + 26, cy], radius=10, fill=(240, 220, 180), outline=(200, 170, 120), width=6)
                    for k in range(2):
                        sy = cy - 80 - ((t * 60 + k * 40 + i * 13) % 90); d.arc([cx - 20, sy - 30, cx + 20, sy + 30], 270, 90, fill=(255, 255, 255), width=5)
            if sc["bg"] == "room" and sc.get("phone", True):
                px, py = W * SS * 0.72, H * SS * 0.55
                d.rounded_rectangle([px - 90, py - 160, px + 90, py + 160], radius=24, fill=(30, 30, 40))
                d.rounded_rectangle([px - 76, py - 140, px + 76, py + 140], radius=14, fill=(255, 236, 180))
                for i in range(4):
                    gx = px - 52 + (i % 2) * 70; gy = py - 60 + (i // 2) * 90
                    d.ellipse([gx - 26, gy - 26, gx + 26, gy + 26], fill=[(150, 100, 70), (120, 80, 60), (170, 120, 90), (140, 95, 70)][i])
            dust(im, t, si)
            text_block(im, sc.get("lines", []), t, D)
            if si == len(st["scenes"]) - 1 and st.get("brand"):
                d = ImageDraw.Draw(im); mtext(d, (0, H * SS * 0.9), st["brand"], 48 * SS, (90, 255, 140), stroke=4 * SS, center_w=W * SS)
            fade = min(1, t / 0.4, (D - t) / 0.4)
            out = im.resize((W, H), Image.LANCZOS)
            if fade < 1: out = Image.blend(Image.new("RGB", (W, H)), out, max(0, fade))
            out.save(os.path.join(frames, f"{n:05d}.jpg"), quality=90); n += 1
            if si == 0 and fi == int(1.5 * FPS): out.save(os.path.join(ROOT, "videos", slug + "_thumb.jpg"), quality=90)
    wav = os.path.join(work, "music.wav"); music.write_wav(wav, music.score(moods, 7))
    out = os.path.join(ROOT, "videos", slug + ".mp4"); tot = n / FPS
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(frames, "%05d.jpg"), "-i", wav,
                    "-filter_complex", f"[1:a]volume=0.9,afade=t=in:d=1,afade=t=out:st={tot - 2.5}:d=2.5,loudnorm=I=-15:TP=-1.5[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", "-t", f"{tot:.2f}", "-movflags", "+faststart", out], check=True)
    print(json.dumps({"video": out, "seconds": round(tot, 1)}))

if __name__ == "__main__":
    render(sys.argv[1])
