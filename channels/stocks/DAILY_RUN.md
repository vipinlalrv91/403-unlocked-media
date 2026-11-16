# Stock Market Zero to Hero: daily automatic run (1 video/day, 18:00 IST)

Same setup, QC, publishing and failure rules as pipeline/DAILY_RUN.md, with these differences:

- Metricool brand: STOCKS_BLOG_ID (fill in once the stock market brand is linked in Metricool; until then do NOT post, log `skipped: stocks brand not linked`).
- Topic: next unchecked line in channels/stocks/curriculum.md. Day number = line number in the course.
  Episode JSON goes in channels/stocks/episodes/day-NN-<slug>.json, copying the fields of day-01-what-is-share.json
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
