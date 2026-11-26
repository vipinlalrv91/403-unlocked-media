import json,os,sys,hashlib,subprocess
sys.path.insert(0,'pipeline')
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]))
VOICE_DEF="TX3LPaxmHKxFdv7VOQHJ"
out={}
for n in range(1,8):
    ep=json.load(open(f'channels/kadha/episodes/ramayanam-{n:02d}.json'))
    V=ep.get('voice_id',VOICE_DEF); work=f'/tmp/short_ramayanam-{n:02d}'
    W=f'videos/ramayanam-{n:02d}_wide.mp4'; D=dur(W)
    res=[]
    for keep in (False,True):
        sc=[s for s in ep['scenes'] if keep or s['type']!='cta']; sd=[];ok=True
        for i,s in enumerate(ep['scenes']):
            if s not in sc: continue
            hk=hashlib.md5(json.dumps([s.get('narration'),s.get('lines'),V],ensure_ascii=False).encode()).hexdigest()[:8]
            c=os.path.join(work,f's{i+1}_{hk}.mp3')
            if not os.path.exists(c): ok=False;break
            sd.append(dur(c)+0.45)
        if not ok: res.append(None);continue
        sd[0]+=0.3; sd[-1]+=2.0; res.append((sum(sd),sd,[s['type'] for s in sc]))
    best=min([r for r in res if r],key=lambda r:abs(r[0]-D)) if any(res) else None
    print(n,round(D,2),[round(r[0],2) if r else None for r in res])
    if best:
        t=0;b=[]
        for x,ty in zip(best[1],best[2]): b.append((round(t,2),round(t+x,2),ty)); t+=x
        out[n]=b
json.dump(out,open('/tmp/p1/bounds.json','w'),indent=0)
