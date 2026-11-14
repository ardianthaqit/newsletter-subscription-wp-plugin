import numpy as np, subprocess, wave, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT=sys.argv[1]; W,H=720,1280; FPS=30; SR=44100
rng=np.random.default_rng(7)
import os
MODELS=os.environ.get("KOKORO_DIR",os.path.join(sys.argv[2],"models"))
from kokoro_onnx import Kokoro
K=Kokoro(MODELS+"/kokoro-v1.0.onnx",MODELS+"/voices-v1.0.bin")
# (caption, spoken line, mode, voice, speed, extra seconds after speech)
SCRIPT=[("DAY 3 SINCE THE POWER DIED.","Day three... since the power died.","door","am_onyx",0.9,0.5),
 ("THE RADIO HAD ONE RULE:\nNEVER OPEN THE DOOR AFTER DARK.","The radio had one rule. Never open the door after dark.","door","am_onyx",0.9,0.4),
 ("TONIGHT...\nSOMEONE KNOCKED.","Tonight... someone knocked.","knock","am_onyx",0.85,2.0),
 ("\"IT'S ME. LET ME IN.\nIT'S SO COLD OUT HERE.\"","It's me. Let me in. It's so cold out here.","door","am_echo",0.8,0.6),
 ("IT WAS MY BROTHER'S VOICE.","It was my brother's voice.","door","am_onyx",0.9,0.5),
 ("MY BROTHER DIED ON DAY 1.","My brother died... on day one.","dark","am_onyx",0.85,1.0),
 ("I DIDN'T OPEN THE DOOR.","I didn't open the door.","knock","am_onyx",0.9,2.2),
 ("THEN THE KNOCKING STOPPED...","Then the knocking stopped.","door","am_onyx",0.85,1.4),
 ("\"THANK YOU,\" IT WHISPERED.","Thank you... it whispered.","door","am_onyx",0.8,0.4),
 ("FROM BEHIND ME.","From behind me.","eyes","am_onyx",0.8,1.6),
 ("WOULD YOU HAVE\nOPENED IT?","Would you have opened it?","end","am_onyx",0.9,2.0)]
VSR=24000; S=[]; VO=[]; t0=0.6; KNOCKS=[]
for cap,line,mode,voice,spd,extra in SCRIPT:
    a,_=K.create(line,voice=voice,speed=spd,lang="en-us"); a=a/np.max(np.abs(a))*0.85
    if voice!="am_onyx":  # ghostly echo for the brother
        e=a.copy()
        for d,g in((0.09,0.5),(0.2,0.35),(0.33,0.2)): e=np.concatenate([e,np.zeros(int(d*VSR))]); e[int(d*VSR):int(d*VSR)+len(a)]+=a*g
        a=e/np.max(np.abs(e))*0.75
    dur=len(a)/VSR; st=t0 if not S else S[-1][1]
    if mode=="knock":
        n=3 if not KNOCKS else 6
        KNOCKS+=[st+dur+0.25+i*(0.45 if n==3 else 0.32) for i in range(n)]
    S.append((st,st+dur+extra,cap,mode,dur)); VO.append((st,a))
S[0]=(0.0,)+S[0][1:]
T=S[-1][1]; N=int(T*FPS)
STING=[s for s in S if s[3]=="eyes"][0][0]
# ---------- base scene: door in dark hallway ----------
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
base=np.zeros((H,W,3),np.float32)+np.array([.10,.09,.08])
base+= (np.sin(xx*0.9)*0.008)[...,None]  # wallpaper texture
dx0,dx1,dy0,dy1=200,520,330,1080
door=(xx>dx0)&(xx<dx1)&(yy>dy0)&(yy<dy1)
grain_w=(np.sin(yy*0.05+np.sin(xx*0.02)*3)*0.03+0.0)
base[door]=np.array([.30,.19,.11])+grain_w[door][:,None]
for (a,b,c,d) in [(235,485,370,640),(235,485,700,1040)]:  # panels
    m=(xx>a)&(xx<b)&(yy>c)&(yy<d); base[m]*=0.8
    e=m&((abs(xx-a)<5)|(abs(yy-c)<5)); base[e]*=0.6
frame_m=door&((xx<dx0+12)|(xx>dx1-12)|(yy<dy0+12)); base[frame_m]*=0.55
knob=((xx-480)**2+(yy-720)**2)<15**2; base[knob]=[.6,.5,.25]
floor=yy>1080; base[floor]=[.06,.05,.045]
gap=(yy>1072)&(yy<1082)&(xx>dx0)&(xx<dx1)
vign=np.clip(1.25-np.sqrt(((xx-W/2)/W)**2+((yy-H/2)/H)**2)*1.9,0,1)[...,None]
font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",50)
small=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf",30)
def noise(): return rng.normal(0,0.035,(H//2,W//2)).astype(np.float32).repeat(2,0).repeat(2,1)[...,None]
def caption(img,text,p,col=(240,236,228)):
    d=ImageDraw.Draw(img); words=text.replace("\n"," \n ").split(" ")
    n=max(1,int(round(p*len([w for w in words if w!="\n"])+0.5)))
    shown=[];c=0
    for w in words:
        if w=="\n": shown.append(w);continue
        if c<n: shown.append(w); c+=1
    raw=" ".join(shown).split("\n"); lines=[]
    for r in raw:
        cur=""
        for w in r.split():
            tst=(cur+" "+w).strip()
            if d.textbbox((0,0),tst,font=font)[2]>640 and cur: lines.append(cur); cur=w
            else: cur=tst
        lines.append(cur)
    y=230
    for ln in lines:
        ln=ln.strip(); bb=d.textbbox((0,0),ln,font=font); tw=bb[2]-bb[0]
        x=(W-tw)//2
        d.text((x,y),ln,font=font,fill=col,stroke_width=6,stroke_fill=(0,0,0))
        y+=68
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
   "-vf","scale=1080:1920:flags=lanczos","-c:v","libx264","-pix_fmt","yuv420p","-crf","29","-preset","slow","-tune","grain","/tmp/v.mp4".replace("/tmp",sys.argv[2])],stdin=subprocess.PIPE)
for f in range(N):
    t=f/FPS; sc=[s for s in S if s[0]<=t<s[1]][0]; mode=sc[3]; prog=(t-max(sc[0],t0 if sc is S[0] else sc[0]))/max(sc[4],0.1)
    lx=W/2+np.sin(t*0.9)*90+np.sin(t*2.3)*25; ly=700+np.sin(t*0.7)*80
    rad=260+np.sin(t*5)*6
    flick=1.0 if rng.random()>0.04 else 0.35
    shake=0
    for k in KNOCKS:
        if 0<=t-k<0.15: shake=18*(1-(t-k)/0.15); flick=1.25
    img=base.copy()
    if mode=="knock":
        img[gap]=[.5,.4,.2] if int(t*3)%2 else [.05,.05,.05]  # shadow under door
    light=np.exp(-(((xx-lx)**2+(yy-ly)**2)/(2*rad**2)))[...,None]*1.9*flick+0.04
    if mode=="dark": light=light*0.18
    if mode in("eyes","end"): light=light*0.05
    out=img*light*vign
    if mode=="eyes":
        for ex in (W/2-55,W/2+55):
            e=np.exp(-(((xx-ex)/22)**2+((yy-760)/9)**2)); out[...,0]+=e*1.2; out[...,1]+=e*0.12; out[...,2]+=e*0.08
        if t-STING<0.25: out+=np.array([.5,0,0])*(1-(t-STING)/0.25)
    out=out+noise()
    if shake:
        out=np.roll(out,int(rng.uniform(-shake,shake)),1); out=np.roll(out,int(rng.uniform(-shake,shake)),0)
    out=np.clip(out*255,0,255).astype(np.uint8)
    im=Image.fromarray(out)
    if mode=="end":
        caption(im,sc[2],min(1,max(0,prog)),(220,30,30))
        d=ImageDraw.Draw(im); s="COMMENT BELOW  ▼"; bb=d.textbbox((0,0),s,font=small)
        if prog>0.4: d.text(((W-bb[2])//2,1050),s,font=small,fill=(200,200,200))
    else:
        caption(im,sc[2],min(1,max(0,prog)),(255,70,60) if mode=="eyes" else (240,236,228))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait()
# ---------- audio ----------
n=int(T*SR); ts=np.arange(n)/SR; a=np.zeros(n)
drone=(np.sin(2*np.pi*55*ts)+0.7*np.sin(2*np.pi*55.7*ts)+0.4*np.sin(2*np.pi*82.6*ts))*0.08
wn=rng.normal(0,1,n); lp=np.convolve(wn,np.ones(400)/400,'same')*0.6
a+=(drone+lp)*np.clip(ts/3,0,1)*np.where(ts<STING,1+ts/40,0.3)
def add(at,sig):
    i=int(at*SR); j=min(n,i+len(sig)); a[i:j]+=sig[:j-i]
def env(d,k): x=np.arange(int(d*SR))/SR; return x,np.exp(-x*k)
for k in KNOCKS:
    x,e=env(0.35,22); add(k,(np.sin(2*np.pi*90*x)*0.9+rng.normal(0,1,len(x))*0.35*np.exp(-x*60))*e*0.9)
bt=1.0
while bt<STING:
    rate=0.95-0.5*(bt/STING)
    for off,amp in((0,0.5),(0.14,0.35)):
        x,e=env(0.2,25); add(bt+off,np.sin(2*np.pi*48*x)*e*amp*(0.3+bt/STING))
    bt+=rate
x=np.arange(int(2.5*SR))/SR; e=np.exp(-x*1.5)
sting=sum(np.sin(2*np.pi*f*x) for f in(311,329,466,493,659))*0.12+rng.normal(0,1,len(x))*0.3*np.exp(-x*4)
add(STING,sting*e)
x=np.arange(int(1.2*SR))/SR; add(STING-1.2,rng.normal(0,1,len(x))*(x/1.2)**3*0.25)  # riser
x,e=env(1.5,3); add(STING-2.5,np.convolve(rng.normal(0,1,len(x)),np.ones(30)/30,'same')*np.sin(np.pi*x/1.5)*0.5)  # whisper
a=a/np.max(np.abs(a))*0.45
vo=np.zeros(n)
for st,v in VO:
    v=np.interp(np.arange(int(len(v)*SR/VSR))*VSR/SR,np.arange(len(v)),v); i=int(st*SR); j=min(n,i+len(v)); vo[i:j]+=v[:j-i]
duck=np.convolve(np.abs(vo)>0.02,np.ones(SR//5)/(SR//5),'same')
a=a*(1-0.45*duck)+vo
a=np.tanh(a*1.6)/np.tanh(1.6); f0=int((T-1.0)*SR); a[f0:]*=np.linspace(1,0,n-f0)
pcm=(a*32767).astype(np.int16); st=np.stack([pcm,pcm],1)
with wave.open(sys.argv[2]+"/a.wav","wb") as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(st.tobytes())
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",sys.argv[2]+"/v.mp4","-i",sys.argv[2]+"/a.wav","-c:v","copy","-af","loudnorm=I=-14:TP=-1:LRA=11","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",OUT],check=True)
