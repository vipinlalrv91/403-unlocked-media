# Kadha Petti: daily run (1 story/day, posts 19:30 IST to Instagram @kadha_petti_malayalam + YouTube Kadhapetti)
> STATUS: ACTIVE from 18 Nov 2026 (owner asked for daily kids moral stories). Instagram public; YouTube Private until the API audit passes.

1. Next unchecked story in channels/kadha/stories.md. Write channels/kadha/episodes/ep-NNN-<slug>.json copying ep-001's fields
   (theme "kids", brand "KADHA PETTI", tagline, voice_id OVkoEbwxsYHiSRMFV9t3, madeForKids true, source_note).
2. Scenes: hook (title + "ഇന്നത്തെ കഥ" + icon 🎁) → 3-5 "story" scenes (bg forest|race|river|night; chars = emoji animals/people
   with x, y≈0.66-0.69, s 240-340, anim still|bounce|walk|run|sleep, flip true = facing right; short caption ≤ 30 chars)
   → "moral" (3 short lines + icon) → cta. CTA narration exactly:
   "ഇനിയും കഥകൾ കേൾക്കാൻ കഥപ്പെട്ടി Subscribe ചെയ്യൂ! നാളെ പുതിയ കഥയുമായി വരാം!"
3. Narration 600-800 chars (55-70 s), very simple Kerala Malayalam a 5-8 year old understands, warm storyteller tone.
4. Render: python3 pipeline/make_short.py channels/kadha/episodes/ep-NNN-<slug>.json ; QC frames (no tofu, characters on the grass,
   captions readable). Copy to channels/kadha/videos/ep-NNN-<slug>.mp4.
5. Publish: copy to videos/approved/<date>_kadha-ep-NNN.mp4, push, confirm raw URL 200, write outbox/<date>_kadha-ep-NNN.json:
   {"channel": "KADHA", "publish_at": "<date>T19:30:00+05:30", "video_url": raw URL, "title", "description": caption + "\n\n" + hashtags,
    "caption": same, "tags", "categoryId": "1", "madeForKids": true, "privacy": "public", "only": ["instagram"]}
   (YouTube for KADHA is DISABLED until the owner fixes YT_REFRESH_KADHA and a verify run confirms the channel; then remove "only".). Push.
6. Mark the story [x], log channels/kadha/runs/log.csv, push.
Credits: priority 403 UNLOCKED > Kadha Petti > The Stoic Bull. Skip Kadha if ElevenLabs remaining < 5000.
