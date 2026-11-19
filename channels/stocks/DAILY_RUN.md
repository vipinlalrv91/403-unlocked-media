# The Stoic Bull (Stock Market Zero to Hero): daily automatic run (2 videos/day, auto-post to YouTube 14:00 + 18:00 IST)

> **STATUS (owner, 18 Nov 2026): AUTO-POST 2 videos/day to YouTube "The Stoic Bull" at 14:00 and 18:00 IST (Instagram too once IG_TOKEN_STOIC works).**
> After export.py, queue each video: outbox/<date>_stoic-<name>.json =
> {"channel": "STOIC", "publish_at": "<date>T14:00:00+05:30" (2nd: 18:00), "video_url": raw URL of channels/stocks/videos/<name>.mp4,
>  "title", "description": caption + "\n\n" + hashtags, "caption": same, "tags", "categoryId": "27", "madeForKids": false, "privacy": "public"}
> YouTube quota: about 6 uploads/day for all channels together; daily total = 403 (2) + Kadha (1) + Stoic (2) = 5.
>
> Per video: write the episode JSON (next two unchecked days in curriculum.md), then run
> `python3 channels/stocks/export.py channels/stocks/episodes/day-NN-<slug>.json`
> which renders and saves `channels/stocks/videos/day-NN-<slug>.mp4` + `_upload.txt` (title, caption, tags).
> QC the frames, mark the day [x], log to channels/stocks/runs/log.csv, commit and push.
> Credits: 403 UNLOCKED has priority. Before each Stoic Bull video, if ElevenLabs remaining characters < 8000, skip it and log `skipped: credits reserved for 403 UNLOCKED`.
> series.total = number of lines in curriculum.md (currently 64). Hook "sub" = "Yesterday: <previous quiz_answer>".

Same setup, QC, publishing and failure rules as pipeline/DAILY_RUN.md, with these differences:

- Posting: disabled (see STATUS).
- Topic: next unchecked line in channels/stocks/curriculum.md. Day number = line number in the course.
  Episode JSON goes in channels/stocks/episodes/day-NN-<slug>.json, copying the fields of day-01-what-is-share.json (brand "THE STOIC BULL")
  (theme "stocks", brand, tagline, voice_id, series {day, total 60, name}, disclaimer, quiz_answer).
- Structure: hook (sub = "Yesterday: <previous episode's quiz_answer>" from Day 2 on) → 3 teaching scenes
  (bullets/steps/compare/chart; Myth-vs-Fact days use compare) → quiz (2-3 options, answer in "quiz_answer") → cta.
  CTA narration exactly: "സീറോ ടു ഹീറോ സീരീസ് മിസ്സ് ചെയ്യാതിരിക്കാൻ ചാനൽ ഇപ്പോൾ തന്നെ സബ്സ്ക്രൈബ് ചെയ്യൂ!"
- Narration 500-650 characters. Kerala Malayalam with English market terms. Use everyday Kerala analogies.
- COMPLIANCE (hard rules, check before rendering):
  * Education only. Never name a stock/company as something to buy or sell, never give targets, tips or "best stock" lists.
  * Never promise or imply returns. Examples with numbers must be clearly hypothetical ("ഉദാഹരണത്തിന്").
  * Facts (rules, timings, taxes, SEBI data) must be verified on sebi.gov.in, nseindia.com, bseindia.com,
    amfiindia.com or incometax.gov.in; put URLs in "sources". If rates/rules may change, say "current rules check ചെയ്യൂ".
  * Caption always ends with the disclaimer: "⚠️ Educational content only. Not investment advice. We are not SEBI-registered advisers."
  * youtubeData.category "EDUCATION".
- After posting, mark the curriculum line [x] and log to channels/stocks/runs/log.csv.


## Voice (owner, 19 Nov 2026, ALL channels)
Use ElevenLabs voice TX3LPaxmHKxFdv7VOQHJ (premade, young male, confident) with model eleven_v3, language_code ml. Set "voice_id": "TX3LPaxmHKxFdv7VOQHJ" in every episode JSON.
Pronunciation: in NARRATION write English words in Malayalam script so they are said the Kerala way (e.g. ഗൈഡഡ് ആക്സസ് for Guided Access, സബ്സ്ക്രൈബ് for Subscribe, ചാനൽ, ആപ്പ്, സെറ്റിങ്സ്, ഗൂഗിൾ ലെൻസ്, ഡീമാറ്റ് അക്കൗണ്ട്). Keep on-screen captions/items in normal English where clearer. Numbers: write in Malayalam words when spoken.


## Thumbnails (owner, 19 Nov 2026), every video
Add "thumb_text": ["BIG LINE (≤18 chars)", "small line"] to every episode JSON. make_short.py writes videos/<slug>_thumb.jpg (1080x1920). Copy it next to the published video with the same name + "_thumb.jpg" (403: videos/approved/<date>_<slug>_thumb.jpg; Stoic: export.py copies it; Kadha: channels/kadha/videos/<name>_thumb.jpg), push, and put its raw URL in the outbox request as "thumbnail_url". The publisher sets it as the Instagram Reel cover and the YouTube custom thumbnail.
