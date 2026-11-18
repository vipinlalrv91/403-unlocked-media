# Kadha Petti: daily run (1 story/day, posts 19:30 IST to Instagram @kadha_petti_malayalam + YouTube Kadhapetti)
> STATUS: from 19 Nov 2026 the daily 19:30 slot is the RAMAYANAM series (channels/kadha/ramayanam.md), one episode per day, starting with episode 1 (already rendered: channels/kadha/videos/ramayanam-01.mp4, just queue it on 19 Nov). Moral stories (stories.md) are paused until the series ends.
> Visuals: painted characters/backgrounds in channels/kadha/art (chars/*.png, bg/*.jpg). In story scenes use "bgimg": <bg name> and chars {"img": <char name>, "x", "y"≈0.76, "h" 700-900 adults / 480 children, "label"}. If a needed character/background is missing, add a prompt to art/generate.py and run it (free Cloudflare FLUX). Owner rule: NO episode counter bar and NO next-episode time in the video (no "series", no "next_time"); teaser starts "അടുത്ത ഭാഗത്തിൽ, ...". Music: set "music": "indian" and give every scene a "mood" (devotional | calm | happy | sad | adventure) matching the story beat (pipeline/music.py composes tanpura, bansuri, bells, tabla). Shorts may be up to 90 s; Ramayanam narration 650-850 chars. Instagram public; YouTube Private until the API audit passes.

1. Next unchecked story in channels/kadha/stories.md. Write channels/kadha/episodes/ep-NNN-<slug>.json copying ep-001's fields
   (theme "kids", brand "KADHA PETTI", tagline, voice_id OVkoEbwxsYHiSRMFV9t3, madeForKids true, source_note).
2. Scenes: hook (title + "ഇന്നത്തെ കഥ" + icon 🎁) → 3-5 "story" scenes (bg forest|race|river|night; chars = emoji animals/people
   with x, y≈0.66-0.69, s 240-340, anim still|bounce|walk|run|sleep, flip true = facing right; short caption ≤ 30 chars)
   → "moral" (3 short lines + icon) → cta. CTA narration exactly:
   "ഇനിയും കഥകൾ കേൾക്കാൻ കഥപ്പെട്ടി Subscribe ചെയ്യൂ! നാളെ പുതിയ കഥയുമായി വരാം!"
3. Narration 600-800 chars (55-70 s), very simple Kerala Malayalam a 5-8 year old understands, warm storyteller tone.
4. Render: python3 pipeline/make_short.py channels/kadha/episodes/ep-NNN-<slug>.json ; QC frames (no tofu, characters on the grass,
   captions readable). Copy to channels/kadha/videos/ep-NNN-<slug>.mp4.
5. Publish: (do NOT put Kadha videos in videos/approved/, that folder is 403 UNLOCKED only) push channels/kadha/videos/ep-NNN-<slug>.mp4, confirm its raw URL returns 200, write outbox/<date>_kadha-ep-NNN.json:
   {"channel": "KADHA", "publish_at": "<date>T19:30:00+05:30", "video_url": raw URL, "title", "description": caption + "\n\n" + hashtags,
    "caption": same, "tags", "categoryId": "1", "madeForKids": true, "privacy": "public"}
   (YouTube for KADHA verified 17 Nov 2026: token saved in YT_REFRESH_STOIC, mapped in publish/run_outbox.py.). Push.
6. Mark the story [x], log channels/kadha/runs/log.csv, push.
Credits: priority 403 UNLOCKED > Kadha Petti > The Stoic Bull. Skip Kadha if ElevenLabs remaining < 5000.
