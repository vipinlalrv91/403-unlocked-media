import json,subprocess,os,re,sys
from PIL import Image,ImageDraw,ImageFont
B=json.load(open('/tmp/p1/bounds.json'))
W='/tmp/p1/seg';os.makedirs(W,exist_ok=True)
FLOW={(1,1):'S01',(1,2):'S02',(1,3):'S03',(1,4):'S04',(2,1):'S05',(2,2):'S06',(2,4):'S07',(3,4):'S08',(4,3):'S10',(5,3):'S09',(5,4):'S11',(6,2):'S12',(6,3):'S13',(7,3):'S14'}
F=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf',54)
def run(a): subprocess.run(a,check=True)
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]))
def cap(text,path):
    text=re.sub(r'[\U00010000-\U0010ffff☀-➿️]','',text).strip()
    im=Image.new('RGBA',(1920,1080),(0,0,0,0));d=ImageDraw.Draw(im)
    if text:
        w=d.textlength(text,font=F);d.rounded_rectangle([960-w/2-50,930,960+w/2+50,1030],radius=40,fill=(255,250,240,240),outline=(255,150,40),width=5);d.text((960-w/2,945),text,font=F,fill=(60,40,90))
    im.save(path)
ENC=["-r","30","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","44100","-ac","2"]
segs=[];chap=[];t=0.0
for n in range(1,8):
    ep=json.load(open(f'channels/kadha/episodes/ramayanam-{n:02d}.json'))
    wide=f'videos/ramayanam-{n:02d}_wide.mp4'
    scenes=[s for s in ep['scenes'] if s['type']!='cta' or n==7]
    bounds=B[str(n)]
    first=True
    for i,(s,(a,b,ty)) in enumerate(zip(scenes,bounds)):
        if ty=='hook' and n!=1: continue
        if ty=='moral' and n!=7: continue
        D=b-a; k=f'{n}_{i}'; out=f'{W}/{k}.mp4'
        if first: chap.append((t,n)); first=False
        fl=FLOW.get((n,i))
        af=f"afade=t=in:d=0.15,afade=t=out:st={max(0,D-0.15):.3f}:d=0.15"
        if not fl:
            run(["ffmpeg","-v","error","-y","-ss",f"{a:.3f}","-t",f"{D:.3f}","-i",wide,"-vf","scale=1920:1080,fps=30","-af",af,*ENC,out])
        else:
            src=f'/tmp/p1/P1-{fl}.mp4';L=dur(src);capp=f'{W}/{k}.png';cap(s.get('caption',''),capp)
            slow=min(1.3,max(1.0,D/L)); Lf=L*slow; use=min(Lf,D)
            fv=f"[0:v]delogo=x=1695:y=880:w=110:h=90,setpts={slow:.4f}*PTS,fps=30,scale=1920:1080,trim=0:{use:.3f},setpts=PTS-STARTPTS[f0];[f0][2:v]overlay=0:0[fv]"
            if D-use>0.6:
                rest=D-use+0.5
                fc=fv+f";[1:v]trim=start={a+use-0.5:.3f}:end={b:.3f},setpts=PTS-STARTPTS,scale=1920:1080,fps=30[rv];[fv][rv]xfade=transition=fade:duration=0.5:offset={use-0.5:.3f}[v]"
            else:
                fc=fv+";[fv]copy[v]"
            fc+=f";[1:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,{af}[aa]"
            run(["ffmpeg","-v","error","-y","-i",src,"-i",wide,"-i",capp,"-filter_complex",fc,"-map","[v]","-map","[aa]","-t",f"{D:.3f}",*ENC,out])
        segs.append(out); t+=dur(out)
open(f'{W}/list.txt','w').write(''.join(f"file '{p}'\n" for p in segs))
os.makedirs('videos/long',exist_ok=True)
run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f'{W}/list.txt',"-c","copy","-movflags","+faststart","videos/long/ramayanam-part-1-flow.mp4"])
json.dump(chap,open('/tmp/p1/chap.json','w'))
print(round(t/60,2),'min')
