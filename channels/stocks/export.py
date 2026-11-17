#!/usr/bin/env python3
"""Render a Stoic Bull episode and store it in channels/stocks/videos/ with an upload-info file (no posting).
Usage: python3 channels/stocks/export.py channels/stocks/episodes/day-NN-<slug>.json"""
import json, os, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ep_path = sys.argv[1]; ep = json.load(open(ep_path, encoding="utf-8"))
out = subprocess.run([sys.executable, os.path.join(ROOT, "pipeline", "make_short.py"), ep_path], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1]
info = json.loads(out)
name = os.path.splitext(os.path.basename(ep_path))[0]          # day-02-nse-vs-bse
vdir = os.path.join(ROOT, "channels", "stocks", "videos"); os.makedirs(vdir, exist_ok=True)
shutil.copy(info["video"], os.path.join(vdir, name + ".mp4"))
with open(os.path.join(vdir, name + "_upload.txt"), "w", encoding="utf-8") as f:
    f.write(f"TITLE (YouTube):\n{ep['title']}\n\nDESCRIPTION / CAPTION:\n{ep['caption']}\n\n{ep['hashtags']}\n\n"
            f"TAGS (YouTube):\n{', '.join(ep['tags'])}\n\nYouTube settings: Short · Category: Education · Not made for kids\n"
            f"Quiz answer (for tomorrow / pinned reply): {ep.get('quiz_answer','')}\n\nSources checked:\n" + "\n".join(ep.get("sources", [])) + "\n")
print(json.dumps({"file": f"channels/stocks/videos/{name}.mp4", "seconds": info["seconds"], "tts_chars": info["tts_chars"]}))
