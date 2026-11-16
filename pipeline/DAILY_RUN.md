# 403 UNLOCKED: daily automatic run

You are running unattended in a fresh cloud session. Nobody reviews the video before it goes public,
so you are the quality gate: when in doubt, DO NOT POST and log why.

## Setup
1. `git clone https://github.com/vipinlalrv91/403-unlocked-media` (attach with add_repo push access first if needed), cd into it.
2. Fonts: `apt-get install -y -q fonts-noto-core fonts-noto-color-emoji` if `/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf` is missing.
3. ElevenLabs key is injected by the network proxy for api.elevenlabs.io. Check `curl -sS https://api.elevenlabs.io/v1/user/subscription`.
   Remaining = character_limit - character_count.

## Per video (VIDEOS_PER_DAY = 2; slot times IST: 10:00 and 16:00)
Make one video per slot, each on a different topic. Credit check before EACH video: if fewer than 1500 characters remain, skip it and log `skipped: out of ElevenLabs credits`.
1. Topic: first `- [ ]` line in `topics/queue.md` whose slug is not in `runs/log.csv`.
   If fewer than 3 topics remain, refill the queue: run the yt-viral method on Malayalam tech Shorts
   (yt-dlp search "malayalam tech tips", "android tips malayalam", "mobile tricks malayalam"; rank by views / channel median)
   and add evergreen, explainer-friendly ideas. Never copy another creator's video, script or title.
2. If `episodes/<slug>.json` does not exist, write it (schema in pipeline/make_short.py docstring), following these rules:
   - 6 scenes: hook, then 3-4 of bullets/compare/steps, then cta. Total narration 500-600 characters (= 40-52 s; keeps 2 videos/day within the ElevenLabs Starter plan).
   - Kerala Malayalam, simple and conversational; common English tech words kept in English.
   - Hook question in the first 2 seconds. On-screen text short (max ~22 chars per item).
   - Every factual claim must be verified with a reliable source (official docs, government, manufacturer). Put URLs in "sources".
     If a claim cannot be verified, drop it. No fear-mongering, no health/financial advice beyond official guidance,
     no brand-specific UI claims (say "path may vary by phone"), no fake app screens presented as real.
   - CTA scene: no "keyword". Narration exactly: "ഇത്തരം കിടിലൻ ടെക് ടിപ്സുകൾക്കായി channel ഇപ്പോൾ തന്നെ Subscribe ചെയ്യൂ!"
     Never promise a guide, link, DM or pinned comment.
   - Also fill "title" (<= 70 chars, Malayalam hook + #shorts), "caption" (Malayalam + English), "hashtags", "tags".
3. `python3 pipeline/make_short.py episodes/<slug>.json` -> videos/<slug>.mp4
4. QC (all must pass, else do not post): duration 30-62 s; 1080x1920; audio stream present;
   extract frames at 3 points per scene and LOOK at them: no tofu boxes, no text overflow, nothing cut off.
5. Publish: `cp videos/<slug>.mp4 videos/approved/<YYYY-MM-DD>_<slug>.mp4`, commit, `git push`.
   Confirm https://raw.githubusercontent.com/vipinlalrv91/403-unlocked-media/main/videos/approved/<file> returns 200.
6. Schedule with Metricool createScheduledPost: blogId 8150228, timezone Asia/Calcutta, providers youtube + instagram,
   media [raw URL], text = caption + "\n\n🔔 403 UNLOCKED Subscribe ചെയ്യൂ!\nBREAK THE LIMITS. EXPLORE THE FUTURE.\n\n" + hashtags,
   youtubeData {title, type "short", privacy "public", tags, category "SCIENCE_TECHNOLOGY", madeForKids false, isAiGeneratedContent false},
   instagramData {type "REEL", showReelOnFeed true, isAiGenerated false}. If the slot time has passed, use now + 15 min.
7. Mark the topic `- [x]` in topics/queue.md, append a row to runs/log.csv, commit and push.

## Failure
Any step fails -> do not post, append `failed: <reason>` to runs/log.csv, push, and stop.
