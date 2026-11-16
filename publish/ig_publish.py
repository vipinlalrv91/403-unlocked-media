#!/usr/bin/env python3
"""Publish a Reel to Instagram via the official Instagram Graph API (Facebook Login flow).
Env: IG_USER_ID, IG_ACCESS_TOKEN (Page access token from a long-lived user token; does not expire).
Usage: ig_publish.py <public_video_url> <caption_file>"""
import json, os, sys, time, urllib.parse, urllib.request

API = "https://graph.facebook.com/v21.0"

def call(method, path, **params):
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}" + ("" if method == "POST" else "?" + data.decode())
    req = urllib.request.Request(url, data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Instagram API error {e.code}: {e.read().decode()[:500]}")

def main(video_url, caption_file):
    uid = os.environ["IG_USER_ID"]
    caption = open(caption_file, encoding="utf-8").read()
    c = call("POST", f"{uid}/media", media_type="REELS", video_url=video_url, caption=caption, share_to_feed="true")
    cid = c["id"]
    for _ in range(60):  # up to ~10 minutes of processing
        st = call("GET", cid, fields="status_code,status").get("status_code")
        if st == "FINISHED":
            break
        if st in ("ERROR", "EXPIRED"):
            sys.exit(f"Instagram processing failed: {st}")
        time.sleep(10)
    else:
        sys.exit("Instagram processing timed out")
    pub = call("POST", f"{uid}/media_publish", creation_id=cid)
    link = call("GET", pub["id"], fields="permalink").get("permalink", "")
    print(json.dumps({"instagram_media_id": pub["id"], "permalink": link}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
