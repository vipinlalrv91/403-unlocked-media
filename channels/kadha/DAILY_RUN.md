# Kadha Petti: daily run (1 story/day, posts 19:30 IST to Instagram @kadha_petti_malayalam + YouTube Kadhapetti)
> STATUS: from 19 Nov 2026 the daily 19:30 slot is the RAMAYANAM series (channels/kadha/ramayanam.md), one episode per day, starting with episode 1 (already rendered: channels/kadha/videos/ramayanam-01.mp4, just queue it on 19 Nov). Moral stories (stories.md) are paused until the series ends.
> Visuals: painted characters/backgrounds in channels/kadha/art (chars/*.png, bg/*.jpg). In story scenes use "bgimg": <bg name> and chars {"img": <char name>, "x", "y"≈0.76, "h" 700-900 adults / 480 children, "label"}. If a needed character/background is missing, add a prompt to art/generate.py and run it (free Cloudflare FLUX). Owner rule: NO episode counter bar and NO next-episode time in the video (no "series", no "next_time"); teaser starts "അടുത്ത ഭാഗത്തിൽ, ...". Music: set "music": "indian" and give every scene a "mood" (devotional | calm | happy | sad | adventure) matching the story beat (pipeline/music.py composes tanpura, bansuri, bells, tabla). Shorts may be up to 90 s; Ramayanam narration+dialogue 900-1200 chars (more detail, owner 19 Nov). Instagram public; YouTube Private until the API audit passes.

1. Next unchecked story in channels/kadha/stories.md. Write channels/kadha/episodes/ep-NNN-<slug>.json copying ep-001's fields
   (theme "kids", brand "KADHA PETTI", tagline, voice_id TX3LPaxmHKxFdv7VOQHJ, madeForKids true, source_note).
2. Scenes: hook (title + "ഇന്നത്തെ കഥ" + icon 🎁) → 3-5 "story" scenes (bg forest|race|river|night; chars = emoji animals/people
   with x, y≈0.66-0.69, s 240-340, anim still|bounce|walk|run|sleep, flip true = facing right; short caption ≤ 30 chars)
   → "moral" (3 short lines + icon) → cta. CTA narration exactly:
   "ഇനിയും കഥകൾ കേൾക്കാൻ കഥപ്പെട്ടി സബ്സ്ക്രൈബ് ചെയ്യൂ! നാളെ പുതിയ കഥയുമായി വരാം!"
3. Narration 600-800 chars (55-70 s), very simple Kerala Malayalam a 5-8 year old understands, warm storyteller tone.
4. Render: python3 pipeline/make_short.py channels/kadha/episodes/ep-NNN-<slug>.json ; QC frames (no tofu, characters on the grass,
   captions readable). Copy to channels/kadha/videos/ep-NNN-<slug>.mp4.
5. Publish: (do NOT put Kadha videos in videos/approved/, that folder is 403 UNLOCKED only) push channels/kadha/videos/ep-NNN-<slug>.mp4, confirm its raw URL returns 200, write outbox/<date>_kadha-ep-NNN.json:
   {"channel": "KADHA", "publish_at": "<date>T19:30:00+05:30", "video_url": raw URL, "title", "description": caption + "\n\n" + hashtags,
    "caption": same, "tags", "categoryId": "1", "madeForKids": true, "privacy": "public"}
   (YouTube for KADHA verified 17 Nov 2026: token saved in YT_REFRESH_STOIC, mapped in publish/run_outbox.py.). Push.
6. Mark the story [x], log channels/kadha/runs/log.csv, push.
Credits: priority 403 UNLOCKED > Kadha Petti > The Stoic Bull. Skip Kadha if ElevenLabs remaining < 5000.


## Voice (owner, 19 Nov 2026, ALL channels)
Use ElevenLabs voice TX3LPaxmHKxFdv7VOQHJ (premade, young male, confident) with model eleven_v3, language_code ml. Set "voice_id": "TX3LPaxmHKxFdv7VOQHJ" in every episode JSON.
Pronunciation: in NARRATION write English words in Malayalam script so they are said the Kerala way (e.g. ഗൈഡഡ് ആക്സസ് for Guided Access, സബ്സ്ക്രൈബ് for Subscribe, ചാനൽ, ആപ്പ്, സെറ്റിങ്സ്, ഗൂഗിൾ ലെൻസ്, ഡീമാറ്റ് അക്കൗണ്ട്). Keep on-screen captions/items in normal English where clearer. Numbers: write in Malayalam words when spoken.


## RAMAYANAM voice (owner, 19 Nov 2026), overrides the all-channel voice for Ramayanam only
Use the muthashi (grandmother) storyteller voice n4fEDQwxuAjplyp0aJy4 ("Solly Rajan - Narration", ElevenLabs shared library, female, old) with eleven_v3, language_code ml: set "voice_id": "n4fEDQwxuAjplyp0aJy4" in every ramayanam-NN.json. Write narration as a grandmother telling the story to grandchildren (e.g. open with "മക്കളേ, ..."), warm and slow. Other Kadha content (moral stories) keeps TX3LPaxmHKxFdv7VOQHJ.


## Volume (owner, 19 Nov 2026, latest): 2 RAMAYANAM episodes per day, NO moral stories until Ramayanam is complete
- 17:00 IST and 19:30 IST: the next two unchecked Ramayanam episodes (muthashi narration + lip-sync dialogue). Reuse an existing ramayanam-NN.json if present.
- Moral stories (stories.md) resume only after episode 36 is posted.
YouTube quota: all channels together post 6 videos/day = the whole daily quota; never queue extra test uploads to YouTube.


## Thumbnails (owner, 19 Nov 2026), every video
Add "thumb_text": ["BIG LINE (≤18 chars)", "small line"] to every episode JSON. make_short.py writes videos/<slug>_thumb.jpg (1080x1920). Copy it next to the published video with the same name + "_thumb.jpg" (403: videos/approved/<date>_<slug>_thumb.jpg; Stoic: export.py copies it; Kadha: channels/kadha/videos/<name>_thumb.jpg), push, and put its raw URL in the outbox request as "thumbnail_url". The publisher sets it as the Instagram Reel cover and the YouTube custom thumbnail.



## Lip-sync dialogue (owner, 19 Nov 2026), all Ramayanam episodes
Story scenes use "lines" instead of a single "narration": [{"who": "narrator"|<character image name>, "text": ...}, ...]. The muthashi narrates (who "narrator"), characters speak their own short lines (1-2 sentences, simple Malayalam). Voices come from channels/kadha/voices.json automatically. The speaking character's mouth moves and everyone blinks (faces in channels/kadha/art/faces.json; if you generate a new character, add its eyes/mouth with art/detect_faces.py and check). No extra body movement (owner). Keep 3-6 lines per scene; hook, teaser and CTA scenes stay narrator-only.


## Forest costume (owner, 23 Nov 2026): valkalam for Rama, Lakshmana and Sita
From the exile onward (episode 12+), in every forest / ashram / river / hermitage scene (bgimg forest, night_forest, ashram,
chitrakoot, ganga_bank, river, ahalya_ashram, and any new forest background) use the bark-cloth (valkalam) versions:
{"img": "rama_forest", "who": "rama"}, {"img": "lakshmana_forest", "who": "lakshmana"}, {"img": "sita_forest", "who": "sita"}
(no crowns, hair tied up, brown bark clothes; Rama stays dusky brown). Their FACES are the original royal faces pasted onto the forest bodies (owner: keep the same faces) — never regenerate these sprites without re-pasting the original face. Keep "who" as the base name so dialogue lines
("who": "rama") still drive the lip sync and voice. Palace / Ayodhya scenes keep the royal images (e.g. the return and coronation).


## Cinematic 2.5D look (owner chose option A, 23 Nov 2026), every Ramayanam episode
Set "cinematic": true in every ramayanam-NN.json. pipeline/cinema.py adds a camera push-in + drift, parallax on the characters,
soft rise-in, and atmosphere chosen from the background (leaves/petals + light rays in forests, fireflies at night, glints + mist
on rivers, golden dust + lamp glow in palaces). Override per scene with "cine_fx": ["petals", "rays", ...]. Character bodies stay
still (owner), lip sync and blink as before. Render takes ~8 min per episode. Add new backgrounds to cinema.FX_FOR.


## How Bharata/others address Rama (owner, 24 Nov 2026)
Never write "രാമേട്ടാ / രാമേട്ടൻ". Bharata (and others) call him "രാമാ" (and say രാമനെ / രാമന്റെ). Lakshmana may still say "ചേട്ടാ".


## Remotion ACTION scenes (owner, 24 Nov 2026) — every Ramayanam episode from ep 17
Set "remotion": true (keep "cinematic": true). Story scenes are rendered by pipeline/remotion (installed with npm on first use);
hook / moral / CTA / audio / thumbnail stay in make_short.py. Give each story scene real ACTIONS that follow the narration:
- chars[i].enter: "left" | "right" (walk/run in) | "fade" (default); "t0": seconds delay
- chars[i].moves: [{"at": "L1+2.5" (2.5 s into line 1) | seconds, "x": 0.45 (walk/run there), "pose": "<pose image>", "dur": 1.0}]
- chars[i].exit: {"at": "L2+1" | "end-1.5", "to": "left"|"right"}
Action poses MUST keep the original face: make them with channels/kadha/art/make_pose.py <char> kneel|bow (folds the original
sprite; adds face + voice). Never use FLUX for a pose of an existing character (faces change). Use 1-3 actions per episode where
the story has them (arrivals, departures, bowing to elders/feet, embraces = step closer). Lip sync / blink work in every pose.
Characters still stand still while talking (owner: no extra body motion).


## Weekly long video (owner, 25 Nov 2026): owner uploads it manually — see channels/kadha/long/PLAN.md
On Saturdays build the next part and send it to the owner. Daily shorts are unchanged (Sunday 19:30 short posts to YouTube too).
