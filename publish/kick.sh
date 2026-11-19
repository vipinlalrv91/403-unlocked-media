#!/bin/bash
# Kick the GitHub Actions publisher for every due outbox item, then print results.
cd "$(dirname "$0")/.." && git pull -q
DUE=$(mktemp)
python3 - "$DUE" <<'PY'
import json,glob,sys,datetime as dt
now=dt.datetime.now(dt.timezone.utc); due=[]
for f in glob.glob('outbox/*.json'):
    d=json.load(open(f,encoding='utf-8'))
    if dt.datetime.fromisoformat(d['publish_at'])<=now:
        d['kick']=now.isoformat(); json.dump(d,open(f,'w',encoding='utf-8'),ensure_ascii=False,indent=1); due.append(f)
open(sys.argv[1],'w').write("\n".join(due))
PY
[ -s "$DUE" ] || { echo "nothing due"; exit 0; }
git add outbox && git -c user.name="403 UNLOCKED bot" -c user.email="noreply@anthropic.com" commit -q -m "Kick publisher" && git push -q origin main
for i in $(seq 1 40); do git pull -q 2>/dev/null; left=0; for f in $(cat "$DUE"); do [ -f "$f" ] && left=1; done; [ $left -eq 0 ] && break; sleep 15; done
for f in $(cat "$DUE"); do p=posted/$(basename $f); if [ -f $p ]; then python3 -c "
import json;d=json.load(open('$p'));r=d['result'];y=r.get('youtube',{});i=r.get('instagram',{})
print(d['channel'],'|',d['title'][:55],'| YT',y.get('url') or y.get('error','')[:80],'thumb:',y.get('thumbnail'),'| IG',i.get('url') or str(i.get('error',''))[:80])"; else echo "still queued: $f"; fi; done
