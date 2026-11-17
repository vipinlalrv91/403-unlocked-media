# The Stoic Bull (Stock Market Zero to Hero): daily automatic run (2 videos/day, GENERATE ONLY)

> **STATUS (owner, 17 Nov 2026): GENERATE 2 videos/day and store them in GitHub. DO NOT POST anywhere (no Metricool, no outbox, no YouTube/Instagram). The owner uploads manually.**
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
  CTA narration exactly: "Zero to Hero series miss ചെയ്യാതിരിക്കാൻ channel ഇപ്പോൾ തന്നെ Subscribe ചെയ്യൂ!"
- Narration 500-650 characters. Kerala Malayalam with English market terms. Use everyday Kerala analogies.
- COMPLIANCE (hard rules, check before rendering):
  * Education only. Never name a stock/company as something to buy or sell, never give targets, tips or "best stock" lists.
  * Never promise or imply returns. Examples with numbers must be clearly hypothetical ("ഉദാഹരണത്തിന്").
  * Facts (rules, timings, taxes, SEBI data) must be verified on sebi.gov.in, nseindia.com, bseindia.com,
    amfiindia.com or incometax.gov.in; put URLs in "sources". If rates/rules may change, say "current rules check ചെയ്യൂ".
  * Caption always ends with the disclaimer: "⚠️ Educational content only. Not investment advice. We are not SEBI-registered advisers."
  * youtubeData.category "EDUCATION".
- After posting, mark the curriculum line [x] and log to channels/stocks/runs/log.csv.
