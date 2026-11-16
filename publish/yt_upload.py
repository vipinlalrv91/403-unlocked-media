#!/usr/bin/env python3
"""Upload a Short to YouTube via the official YouTube Data API v3 (resumable upload).
Env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
Usage: yt_upload.py <video_file> <meta.json>   (meta: title, description, tags[], categoryId, privacy)
Note: until the Google Cloud project passes YouTube's API audit, YouTube forces uploads to Private."""
import json, os, sys, urllib.parse, urllib.request

def token():
    data = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                   "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=60) as r:
        return json.load(r)["access_token"]

def main(video, meta_file):
    m = json.load(open(meta_file, encoding="utf-8"))
    tok = token(); size = os.path.getsize(video)
    body = {"snippet": {"title": m["title"][:100], "description": m["description"][:5000], "tags": m.get("tags", []),
                        "categoryId": str(m.get("categoryId", "27")), "defaultLanguage": "ml", "defaultAudioLanguage": "ml"},
            "status": {"privacyStatus": m.get("privacy", "public"), "selfDeclaredMadeForKids": False}}
    req = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                                          "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            loc = r.headers["Location"]
        with open(video, "rb") as f:
            up = urllib.request.Request(loc, data=f.read(), method="PUT", headers={"Content-Type": "video/mp4"})
        with urllib.request.urlopen(up, timeout=600) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"YouTube API error {e.code}: {e.read().decode()[:500]}")
    print(json.dumps({"youtube_id": res["id"], "url": f"https://www.youtube.com/shorts/{res['id']}",
                      "privacy": res.get("status", {}).get("privacyStatus")}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
