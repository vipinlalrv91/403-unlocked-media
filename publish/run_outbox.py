#!/usr/bin/env python3
"""Post every due request in outbox/*.json to Instagram + YouTube, then move it to posted/.

Request JSON: {"channel": "403" | "STOIC" | "KADHA", "publish_at": "2026-11-18T10:00:00+05:30", "video_url": "...",
               "title": "...", "description": "...", "caption": "...", "tags": [...], "categoryId": "28"}
Secrets per channel (GitHub Actions env): IG_USER_ID_<CH>, IG_TOKEN_<CH>, YT_REFRESH_<CH>; shared YT_CLIENT_ID, YT_CLIENT_SECRET.
A platform whose secrets are missing is skipped; a request with no configured platform stays in the outbox."""
import datetime as dt, glob, json, os, shutil, sys, tempfile, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ig_publish import publish_reel
from yt_upload import upload_short

YT_CHANNEL = {"403": "UCeS13InBe6Upz3qgMcAwgDA", "STOIC": "UCtMTEJfHGHxEeWn1rToKygA", "KADHA": "UC1rMC_lvwPFW6SgNsOsJLdQ"}
now = dt.datetime.now(dt.timezone.utc); changed = False
for path in sorted(glob.glob("outbox/*.json")):
    req = json.load(open(path, encoding="utf-8")); ch = req["channel"].upper()
    if dt.datetime.fromisoformat(req["publish_at"]) > now:
        print(f"{path}: not due yet ({req['publish_at']})"); continue
    env = lambda k: os.environ.get(k, "").strip()
    ig_ok = env(f"IG_USER_ID_{ch}") and env(f"IG_TOKEN_{ch}")
    yt_secret = req.get("yt_secret", ch).upper()  # temporary override when a token is saved under another name
    yt_ok = env(f"YT_REFRESH_{yt_secret}") and env("YT_CLIENT_ID") and env("YT_CLIENT_SECRET")
    if not (ig_ok or yt_ok):
        print(f"{path}: no secrets configured for channel {ch}; leaving in outbox"); continue
    result = {"posted_at": now.isoformat()}
    only = req.get("only") or ["instagram", "youtube"]
    ig_ok = ig_ok and "instagram" in only; yt_ok = yt_ok and "youtube" in only
    if ig_ok:
        try: result["instagram"] = publish_reel(env(f"IG_USER_ID_{ch}"), env(f"IG_TOKEN_{ch}"), req["video_url"], req["caption"])
        except Exception as e: result["instagram"] = {"error": str(e)}
    else: result["instagram"] = {"skipped": "no secrets"}
    if yt_ok:
        tmp = os.path.join(tempfile.gettempdir(), "v.mp4")
        try:
            urllib.request.urlretrieve(req["video_url"], tmp)
            result["youtube"] = upload_short(env("YT_CLIENT_ID"), env("YT_CLIENT_SECRET"), env(f"YT_REFRESH_{yt_secret}"), tmp, dict(req, expected_channel_id=YT_CHANNEL.get(ch)))
        except Exception as e: result["youtube"] = {"error": str(e)}
    else: result["youtube"] = {"skipped": "no secrets"}
    req["result"] = result
    json.dump(req, open(os.path.join("posted", os.path.basename(path)), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.remove(path); changed = True
    print(f"{path}: {json.dumps(result, ensure_ascii=False)}")
sys.exit(0)
