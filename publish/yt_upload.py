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
    body = {"snippet": {"title": meta["title"][:100], "description": meta["description"][:5000], "tags": meta.get("tags", []),
                        "categoryId": str(meta.get("categoryId", "28")), "defaultLanguage": "ml", "defaultAudioLanguage": "ml"},
            "status": {"privacyStatus": meta.get("privacy", "public"), "selfDeclaredMadeForKids": False}}
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
    return {"id": res["id"], "url": f"https://www.youtube.com/shorts/{res['id']}", "privacy": res.get("status", {}).get("privacyStatus")}
