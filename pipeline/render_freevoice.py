#!/usr/bin/env python3
"""Render a Kadha episode with the FREE Microsoft Edge Malayalam voices instead of ElevenLabs (test / fallback).
  python3 pipeline/render_freevoice.py channels/kadha/episodes/ramayanam-NN.json  -> videos/ramayanam-NN-freevoice.mp4
Edge read-aloud is unofficial (edge-tts); check terms before commercial use."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_short as ms
PY = os.path.expanduser("~/.viral-agent/py/bin/python"); LINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "freevoice", "edge_tts_line.py")
V = json.load(open(os.path.join(ms.ROOT, "channels", "kadha", "voices.json")))
inv = {}
for name, vid in V.items():
    if not name.startswith("_"): inv.setdefault(vid, name)
FEMALE = {"sita", "kausalya", "kaikeyi", "sumitra", "ahalya", "manthara", "anasuya", "sita_forest"}
STYLE = {  # (voice, rate, pitch)
    "narrator": ("ml-IN-SobhanaNeural", "-10%", "-6Hz"),
    "rama": ("ml-IN-MidhunNeural", "-4%", "+0Hz"), "lakshmana": ("ml-IN-MidhunNeural", "+6%", "+6Hz"),
    "bharata": ("ml-IN-MidhunNeural", "+0%", "+4Hz"), "dasharatha": ("ml-IN-MidhunNeural", "-12%", "-10Hz"),
    "atri": ("ml-IN-MidhunNeural", "-14%", "-12Hz"), "vishwamitra": ("ml-IN-MidhunNeural", "-12%", "-10Hz"),
    "sita": ("ml-IN-SobhanaNeural", "+0%", "+6Hz"), "anasuya": ("ml-IN-SobhanaNeural", "-12%", "-8Hz"),
    "kausalya": ("ml-IN-SobhanaNeural", "-6%", "-2Hz"),
}
def free_tts(textline, out, voice=None):
    who = inv.get(voice or ms.VOICE, "narrator")
    v, rate, pitch = STYLE.get(who) or (("ml-IN-SobhanaNeural", "+0%", "+0Hz") if who in FEMALE else ("ml-IN-MidhunNeural", "+0%", "+0Hz"))
    mp3 = out if out.endswith(".mp3") else out + ".mp3"
    subprocess.run([PY, LINE, v, rate, pitch, mp3], input=textline, text=True, check=True)
    if mp3 != out: os.replace(mp3, out)
ms.tts = free_tts
if __name__ == "__main__":
    ep = json.load(open(sys.argv[1], encoding="utf-8")); ep["slug"] = ep["slug"] + "-freevoice"
    tmp = os.path.join("/tmp", ep["slug"] + ".json"); json.dump(ep, open(tmp, "w", encoding="utf-8"), ensure_ascii=False); ms.main(tmp)
