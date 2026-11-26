# Weekly long Ramayanam videos (owner, 25 Nov 2026): OWNER UPLOADS THEM MANUALLY in YouTube Studio
- No automatic upload, no change to the daily shorts (the Sunday 19:30 short posts to YouTube + Instagram as usual).
- Every SATURDAY daily run: build the next part with
    python3 pipeline/compile_kadha.py <N> <first> <last> "<Malayalam title>"
  first render each episode full-screen with python3 pipeline/make_wide.py <ep.json> (add --keep-cta for the LAST episode of the part), then send the owner videos/long/ramayanam-part-N.mp4, _thumb.jpg and the title / description / chapters text
  (write it to channels/kadha/long/part-N-upload.txt). Parts: 1 = ep 1-7, 2 = ep 8-17, 3 = ep 18-31, then 14 episodes per part.

- Google Flow (owner, 26 Nov 2026): for each part, prepare 2-4 hero-shot prompts in 16:9 (channels/kadha/flow/kit) for the biggest moments a few days before Saturday; the owner generates them in Flow and sends the clips; insert them into the matching episodes' _wide renders before compile_kadha.py. If no clips arrive, build the part without them.
