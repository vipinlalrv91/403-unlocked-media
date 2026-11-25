# Weekly long Ramayanam videos (owner, 25 Nov 2026)
- Every SUNDAY at 19:30 IST the long video replaces the 19:30 YouTube short (YouTube API allows ~6 uploads/day).
  On Sundays queue the 19:30 Ramayanam short with "only": ["instagram"] (Instagram still gets it); the 17:00 short posts normally.
- The long video is an outbox request with "compile": {part, first, last, title}, "only": ["youtube"], "long": true;
  the GitHub publisher builds it (pipeline/compile_kadha.py) from channels/kadha/videos/ramayanam-NN.mp4 and uploads it.
  Description contains {CHAPTERS} which the publisher fills in.
- Parts: 1 = ep 1-7 (29 Nov), 2 = ep 8-17 (6 Dec), 3 = ep 18-31 (13 Dec), then the next 14 episodes every Sunday.
- On each Saturday's daily run: write channels/kadha/long/part-N.json (copy part-2.json, change part/first/last/title) and
  queue it for Sunday 19:30. Only episodes that are already rendered (all have brown Rama since ep 1-7 were re-rendered 24 Nov).
