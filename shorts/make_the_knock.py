import numpy as np, subprocess, wave, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT=sys.argv[1]; W,H=720,1280; FPS=30; SR=44100
rng=np.random.default_rng(7)
# (start,end,text,mode)
S=[(0.0,3.2,"DAY 3 SINCE THE POWER DIED.","door"),
   (3.2,6.6,"THE RADIO HAD ONE RULE:\nNEVER OPEN THE DOOR AFTER DARK.","door"),
   (6.6,9.4,"TONIGHT...\nSOMEONE KNOCKED.","knock"),
   (9.4,13.4,"\"IT'S ME. LET ME IN.\nIT'S SO COLD OUT HERE.\"","door"),
   (13.4,16.4,"IT WAS MY BROTHER'S VOICE.","door"),
   (16.4,19.4,"MY BROTHER DIED ON DAY 1.","dark"),
   (19.4,22.6,"I DIDN'T OPEN THE DOOR.","door"),
   (22.6,25.6,"THEN THE KNOCKING STOPPED...","door"),
   (25.6,28.6,"\"THANK YOU,\" IT WHISPERED.","door"),
   (28.6,30.6,"FROM BEHIND ME.","eyes"),
   (30.6,34.0,"WOULD YOU HAVE\nOPENED IT?","end")]
T=S[-1][1]; N=int(T*FPS)
KNOCKS=[6.9,7.3,7.7,8.6,9.0,10.8,11.2,20.0,20.4,20.8,21.2,21.6]
STING=28.6
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
    n=max(1,int(round(p*len([w for w in words if w!="\n"])*3.0+0.5)))
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
    t=f/FPS; sc=[s for s in S if s[0]<=t<s[1]][0]; mode=sc[3]; prog=(t-sc[0])/(sc[1]-sc[0])
    lx=W/2+np.sin(t*0.9)*90+np.sin(t*2.3)*25; ly=700+np.sin(t*0.7)*80
    rad=260+np.sin(t*5)*6
    flick=1.0 if rng.random()>0.04 else 0.35
    shake=0
    for k in KNOCKS:
        if 0<=t-k<0.15: shake=18*(1-(t-k)/0.15); flick=1.25
    img=base.copy()
    if mode=="knock" or (KNOCKS[0]<t<9.4) or (19.4<t<22.6):
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
        caption(im,sc[2],prog,(220,30,30))
        d=ImageDraw.Draw(im); s="COMMENT BELOW  ▼"; bb=d.textbbox((0,0),s,font=small)
        if prog>0.4: d.text(((W-bb[2])//2,1050),s,font=small,fill=(200,200,200))
    else:
        caption(im,sc[2],min(1,prog*1.6),(255,70,60) if mode=="eyes" else (240,236,228))
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
x,e=env(1.5,3); add(25.8,np.convolve(rng.normal(0,1,len(x)),np.ones(30)/30,'same')*np.sin(np.pi*x/1.5)*0.5)  # whisper
a=a/np.max(np.abs(a))*0.9; a[int(33.2*SR):]*=np.linspace(1,0,n-int(33.2*SR))
pcm=(a*32767).astype(np.int16); st=np.stack([pcm,pcm],1)
with wave.open(sys.argv[2]+"/a.wav","wb") as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(st.tobytes())
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",sys.argv[2]+"/v.mp4","-i",sys.argv[2]+"/a.wav","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",OUT],check=True)
