#!/usr/bin/env python3
"""Weekly long-form Ramayanam compilation for Kadha Petti (owner, 24 Nov 2026).
  python3 pipeline/compile_kadha.py <part_no> <first_ep> <last_ep> "<Malayalam part title>"
Makes videos/long/ramayanam-part-<N>.mp4 (1920x1080, vertical episodes centred on a blurred copy), a 1280x720 thumbnail and
a chapters text (one chapter per episode). Each episode's closing 'subscribe' scene is cut, except in the last episode.
No new TTS (no ElevenLabs cost)."""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KV = os.path.join(ROOT, "channels", "kadha", "videos")
OUT = os.path.join(ROOT, "videos", "long"); os.makedirs(OUT, exist_ok=True)
ML = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf"


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


def cta_start(p):
    """time of the last hard cut in the final 14 s (= start of the subscribe scene)."""
    D = dur(p)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-sseof", "-14", "-i", p, "-vf", "select='gt(scene,0.2)',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    ts = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", r)]
    if not ts: return D - 7.0
    return max(0.0, D - 14 + ts[-1])


def ep_titles():
    t = {}
    for line in open(os.path.join(ROOT, "channels", "kadha", "ramayanam.md"), encoding="utf-8"):
        m = re.match(r"- \[[x ]\] (\d+) (.+)$", line.strip())
        if m:
            s = re.sub(r"\s*\(.*?\)\s*", " ", m.group(2)).strip()
            t[int(m.group(1))] = s.split(":")[0].strip()
    return t


def thumb(part, title, first_ep, path):
    import glob
    cands = [os.path.join(KV, f"ramayanam-{n:02d}_thumb.jpg") for n in range(first_ep, first_ep + 20)]
    src = next((c for c in cands if os.path.exists(c)), None) or sorted(glob.glob(os.path.join(KV, "ramayanam-*_thumb.jpg")))[0]
    im = Image.open(src).convert("RGB"); bg = im.resize((1280, int(1280 * im.height / im.width))).crop((0, 300, 1280, 1020)).filter(ImageFilter.GaussianBlur(6))
    fg = im.resize((int(720 * im.width / im.height), 720)); bg.paste(fg, (1280 - fg.width - 40, 0))
    d = ImageDraw.Draw(bg); f1 = ImageFont.truetype(ML, 118); f2 = ImageFont.truetype(ML, 58); f3 = ImageFont.truetype(ML, 50)
    d.rounded_rectangle([30, 40, 860, 680], radius=40, fill=(255, 245, 225))
    d.text((70, 70), "രാമായണം", font=f1, fill=(230, 80, 20), stroke_width=4, stroke_fill=(255, 255, 255))
    d.text((70, 240), f"ഭാഗം {part}", font=f2, fill=(90, 30, 140))
    y = 330
    for line in wrap(title, 13):
        d.text((70, y), line, font=f2, fill=(60, 40, 90)); y += 80
    d.rounded_rectangle([70, 580, 600, 650], radius=30, fill=(230, 80, 20))
    d.text((95, 588), "കുട്ടികൾക്കുള്ള കഥ", font=f3, fill=(255, 255, 255))
    bg.save(path, quality=90)


def wrap(s, n):
    words, out, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out[:3]


def main(part, a, b, title):
    titles = ep_titles(); work = os.path.join("/tmp", f"long_part{part}"); os.makedirs(work, exist_ok=True)
    segs, chapters, t = [], [], 0.0
    for n in range(a, b + 1):
        wide = os.path.join(ROOT, "videos", f"ramayanam-{n:02d}_wide.mp4")   # full-screen 16:9 render (make_wide.py), preferred
        if os.path.exists(wide):
            seg = os.path.join(work, f"e{n:02d}.mp4")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wide, "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", seg], check=True)
            chapters.append((t, f"{n}. {titles.get(n, f'ഭാഗം {n}')}")); segs.append(seg); t += dur(seg); continue
        src = os.path.join(KV, f"ramayanam-{n:02d}.mp4")
        end = dur(src) if n == b else cta_start(src)
        seg = os.path.join(work, f"e{n:02d}.mp4")
        vf = ("[0:v]split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:3,eq=brightness=-0.12[bg];"
              "[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,format=yuv420p[v]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-t", f"{end:.3f}", "-filter_complex", vf, "-map", "[v]", "-map", "0:a",
                        "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", seg], check=True)
        chapters.append((t, f"{n}. {titles.get(n, f'ഭാഗം {n}')}")); segs.append(seg); t += dur(seg)
    lst = os.path.join(work, "list.txt"); open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    out = os.path.join(OUT, f"ramayanam-part-{part}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out], check=True)
    thumb(part, title, a, os.path.join(OUT, f"ramayanam-part-{part}_thumb.jpg"))
    ch = "\n".join(f"{int(s // 60)}:{int(s % 60):02d} {name}" for s, name in chapters)
    open(os.path.join(OUT, f"ramayanam-part-{part}_chapters.txt"), "w", encoding="utf-8").write(ch)
    print(json.dumps({"video": out, "minutes": round(t / 60, 1), "size_mb": round(os.path.getsize(out) / 1e6, 1), "chapters": ch}, ensure_ascii=False))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
