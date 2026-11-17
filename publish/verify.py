#!/usr/bin/env python3
"""Check every configured secret WITHOUT posting. Writes verify/result.json (no secret values)."""
import datetime as dt, json, os, urllib.parse, urllib.request
def get(url, data=None):
    try:
        with urllib.request.urlopen(url, data, timeout=60) as r: return json.load(r), None
    except urllib.error.HTTPError as e: return None, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e: return None, str(e)[:200]
env = lambda k: os.environ.get(k, "").strip()
out = {"checked_at": dt.datetime.now(dt.timezone.utc).isoformat(), "secrets_present": {}, "instagram": {}, "youtube": {}}
names = ["YT_CLIENT_ID", "YT_CLIENT_SECRET"] + [f"{p}_{c}" for c in ("403", "STOIC", "KADHA") for p in ("IG_USER_ID", "IG_TOKEN", "YT_REFRESH")]
out["secrets_present"] = {n: bool(env(n)) for n in names}
for ch in ("403", "STOIC", "KADHA"):
    uid, tok = env(f"IG_USER_ID_{ch}"), env(f"IG_TOKEN_{ch}")
    if uid and tok:
        d, err = get(f"https://graph.facebook.com/v21.0/{uid}?fields=username,name&access_token={urllib.parse.quote(tok)}")
        out["instagram"][ch] = {"ok": True, "username": d.get("username")} if d else {"ok": False, "error": err}
        if d:  # does the token allow publishing? check limit endpoint (needs instagram_content_publish)
            q, err2 = get(f"https://graph.facebook.com/v21.0/{uid}/content_publishing_limit?fields=quota_usage&access_token={urllib.parse.quote(tok)}")
            out["instagram"][ch]["can_publish"] = bool(q) if q else f"no: {err2}"
    else:
        out["instagram"][ch] = {"ok": False, "error": "secret missing"}
    rt = env(f"YT_REFRESH_{ch}")
    if rt and env("YT_CLIENT_ID") and env("YT_CLIENT_SECRET"):
        d, err = get("https://oauth2.googleapis.com/token", urllib.parse.urlencode({"client_id": env("YT_CLIENT_ID"),
                     "client_secret": env("YT_CLIENT_SECRET"), "refresh_token": rt, "grant_type": "refresh_token"}).encode())
        if d:
            info, _ = get("https://oauth2.googleapis.com/tokeninfo?access_token=" + d["access_token"])
            scope = (info or {}).get("scope", d.get("scope", ""))
            out["youtube"][ch] = {"ok": "youtube.upload" in scope, "scope": scope}
            try:
                rq = urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true", headers={"Authorization": "Bearer " + d["access_token"]})
                with urllib.request.urlopen(rq, timeout=60) as rr:
                    it = json.load(rr).get("items", [])
                out["youtube"][ch]["channel"] = f'{it[0]["snippet"]["title"]} ({it[0]["id"]})' if it else "none"
            except Exception:
                out["youtube"][ch]["channel"] = "unknown (token lacks youtube.readonly scope)"
        else:
            out["youtube"][ch] = {"ok": False, "error": err}
    else:
        out["youtube"][ch] = {"ok": False, "error": "secret missing"}
os.makedirs("verify", exist_ok=True)
json.dump(out, open("verify/result.json", "w"), indent=1)
print(json.dumps(out, indent=1))
