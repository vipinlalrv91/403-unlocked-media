#!/usr/bin/env python3
"""Upload a Short via the official YouTube Data API v3. Until the Cloud project passes YouTube's API audit, uploads are forced Private."""
import json, os, urllib.parse, urllib.request

def access_token(client_id, client_secret, refresh_token):
    data = urllib.parse.urlencode({"client_id": client_id, "client_secret": client_secret,
                                   "refresh_token": refresh_token, "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=60) as r:
        return json.load(r)["access_token"]

def upload_short(client_id, client_secret, refresh_token, video_path, meta):
    tok = access_token(client_id, client_secret, refresh_token); size = os.path.getsize(video_path)
    exp = meta.get("expected_channel_id")
    if exp:  # pre-check (works when the token also has youtube.readonly scope)
        try:
            r = urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true", headers={"Authorization": f"Bearer {tok}"})
            with urllib.request.urlopen(r, timeout=60) as resp:
                items = json.load(resp).get("items", [])
            if items and items[0]["id"] != exp:
                return {"error": f"WRONG CHANNEL (blocked before upload): token belongs to {items[0]['id']} ({items[0]['snippet']['title']}), expected {exp}"}
        except urllib.error.HTTPError:
            pass  # token has only youtube.upload scope; fall back to the post-upload check
    _c = lambda s: s.replace("<", "‹").replace(">", "→")  # YouTube rejects < and > in title/description
    body = {"snippet": {"title": _c(meta["title"])[:100], "description": _c(meta["description"])[:5000], "tags": meta.get("tags", []),
                        "categoryId": str(meta.get("categoryId", "28")), "defaultLanguage": "ml", "defaultAudioLanguage": "ml"},
            "status": {"privacyStatus": meta.get("privacy", "public"), "selfDeclaredMadeForKids": bool(meta.get("madeForKids", False))}}
    req = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                                          "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            loc = r.headers["Location"]
        with open(video_path, "rb") as f:
            up = urllib.request.Request(loc, data=f.read(), method="PUT", headers={"Content-Type": "video/mp4"})
        with urllib.request.urlopen(up, timeout=900) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"YouTube API {e.code}: {e.read().decode()[:400]}")
    out = {"id": res["id"], "url": f"https://www.youtube.com/shorts/{res['id']}", "privacy": res.get("status", {}).get("privacyStatus"),
           "channel_id": res.get("snippet", {}).get("channelId")}
    exp = meta.get("expected_channel_id")
    if exp and out["channel_id"] != exp:
        out["error"] = f"WRONG CHANNEL: token uploaded to {out['channel_id']}, expected {exp}. Fix the refresh token secret; delete this video in YouTube Studio."
    if meta.get("long"): out["url"] = f"https://www.youtube.com/watch?v={out['id']}"
    if (meta.get("thumbnail_url") or meta.get("thumbnail_file")) and "error" not in out:  # custom thumbnail (needs a phone-verified channel)
        try:
            if meta.get("thumbnail_file"):
                img = open(meta["thumbnail_file"], "rb").read()
            else:
                with urllib.request.urlopen(meta["thumbnail_url"], timeout=60) as r:
                    img = r.read()
            tr = urllib.request.Request(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={out['id']}", data=img, method="POST",
                                        headers={"Authorization": f"Bearer {tok}", "Content-Type": "image/jpeg"})
            urllib.request.urlopen(tr, timeout=120).read(); out["thumbnail"] = "set"
        except urllib.error.HTTPError as e:
            out["thumbnail"] = f"failed {e.code}: {e.read().decode()[:200]}"
        except Exception as e:
            out["thumbnail"] = f"failed: {e}"
    return out
