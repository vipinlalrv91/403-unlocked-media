#!/usr/bin/env python3
"""Publish a Reel via the official Instagram Graph API (Facebook-Page-linked professional account)."""
import json, sys, time, urllib.parse, urllib.request
API = "https://graph.facebook.com/v21.0"

def _call(token, method, path, **params):
    params["access_token"] = token
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}" + ("" if method == "POST" else "?" + data.decode())
    req = urllib.request.Request(url, data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Instagram API {e.code}: {e.read().decode()[:400]}")

def publish_reel(ig_user_id, token, video_url, caption):
    cid = _call(token, "POST", f"{ig_user_id}/media", media_type="REELS", video_url=video_url, caption=caption, share_to_feed="true")["id"]
    for _ in range(60):
        st = _call(token, "GET", cid, fields="status_code").get("status_code")
        if st == "FINISHED": break
        if st in ("ERROR", "EXPIRED"): raise RuntimeError(f"Instagram processing {st}")
        time.sleep(10)
    else:
        raise RuntimeError("Instagram processing timed out")
    mid = _call(token, "POST", f"{ig_user_id}/media_publish", creation_id=cid)["id"]
    return {"id": mid, "url": _call(token, "GET", mid, fields="permalink").get("permalink", "")}
