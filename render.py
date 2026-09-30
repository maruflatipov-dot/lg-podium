#!/usr/bin/env python3
"""Louis Gabor TOP-3 podium (X01). Usage: python3 render.py data.json out.png
data.json: {"title","sub","top":[{"name","net","units","bonus"}x3 (1,2,3-o'rin)],
 "congrats","note","el","er"}   (el/er = emoji chars, masalan 🎉 🔥)"""
import sys,json,math
from PIL import Image,ImageDraw,ImageFont,ImageFilter
R='/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf'
B='/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf'
E='/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
NAVY='#0A1F3D';N2='#12335F';N3='#2E5E8A';GOLD='#C9A24D';GOLD2='#E8C878';MUT='#6b7785';TXT='#15202b'
NV=[(N2,NAVY),('#1B4477',N2),(N3,'#1E4870')]
F=lambda s,b=False:ImageFont.truetype(B if b else R,s)
_ef=ImageFont.truetype(E,109)
def hexrgb(c):c=c.lstrip('#');return tuple(int(c[i:i+2],16) for i in (0,2,4))
def grad(w,h,c1,c2):
    a,b=hexrgb(c1),hexrgb(c2);g=Image.new('RGB',(w,h));d=ImageDraw.Draw(g)
    for k in range(h):
        t=k/max(1,h-1);d.line((0,k,w,k),fill=tuple(int(a[j]+(b[j]-a[j])*t) for j in range(3)))
    return g
def rmask(w,h,r):
    m=Image.new('L',(w,h),0);ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),radius=r,fill=255);return m
def shadow(im,box,r=22,blur=20,off=12,alpha=70):
    x0,y0,x1,y1=[int(v) for v in box];pad=blur*3
    s=Image.new('L',(x1-x0+2*pad,y1-y0+2*pad),0)
    ImageDraw.Draw(s).rounded_rectangle((pad,pad,pad+x1-x0,pad+y1-y0),radius=r,fill=alpha)
    s=s.filter(ImageFilter.GaussianBlur(blur));im.paste(Image.new('RGB',s.size,NAVY),(x0-pad,y0-pad+off),s)
def block(im,box,c1,c2,r=22):
    x0,y0,x1,y1=[int(v) for v in box];shadow(im,box,r)
    im.paste(grad(x1-x0,y1-y0,c1,c2),(x0,y0),rmask(x1-x0,y1-y0,r))
def shine(im,box,r=22):
    x0,y0,x1,y1=[int(v) for v in box]
    o=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0))
    ImageDraw.Draw(o).polygon([(0,0),((x1-x0)*0.45,0),(0,(y1-y0)*0.55)],fill=(255,255,255,38))
    base=im.crop((x0,y0,x1,y1)).convert('RGBA');base.alpha_composite(o)
    im.paste(base.convert('RGB'),(x0,y0),rmask(x1-x0,y1-y0,r))
def emo(im,ch,cx,cy,s):
    t=Image.new('RGBA',(136,128),(0,0,0,0));ImageDraw.Draw(t).text((0,0),ch,font=_ef,embedded_color=True)
    t=t.crop(t.getbbox());r=s/max(t.size);t=t.resize((int(t.width*r),int(t.height*r)),Image.LANCZOS)
    im.paste(t,(int(cx-t.width/2),int(cy-t.height/2)),t)
def fit(d,txt,size,maxw,bold=True,minsize=18):
    while size>minsize and d.textlength(txt,font=F(size,bold))>maxw: size-=1
    return F(size,bold)
def render(D,out,bg_only=False):
    im=grad(1080,1350,'#FFFFFF','#EEF3FA');d=ImageDraw.Draw(im)
    d.text((540,155),D.get('title','HAFTA YULDUZLARI'),font=fit(d,D.get('title','HAFTA YULDUZLARI'),88,1000),fill=NAVY,anchor='mm')
    if not bg_only: d.text((540,223),D.get('sub',''),font=F(30),fill=MUT,anchor='mm')
    BASE=1040;HH={0:420,1:310,2:230};XS={1:190,0:540,2:890}
    top=D.get('top') or [{}]*3
    for i in (1,0,2):
        cx=XS[i];h=HH[i];t=top[i];box=(cx-165,BASE-h,cx+165,BASE)
        block(im,box,*NV[i]);shine(im,box)
        yt=BASE-h
        emo(im,['🥇','🥈','🥉'][i],cx,yt-115,110)
        if not bg_only: d.text((cx,yt-30),t['name'],font=fit(d,t['name'],36,335),fill=TXT,anchor='mm')
        if not bg_only: d.text((cx,yt+66),t['net'],font=fit(d,t['net'],58,300),fill='white',anchor='mm')
        if not bg_only: d.text((cx,yt+122),t['units'],font=F(28),fill='#DCE5F2',anchor='mm')
        if not bg_only: d.text((cx,yt+176),t['bonus'],font=fit(d,t['bonus'],34,300),fill=GOLD2,anchor='mm')
    d.rectangle((30,BASE,1050,BASE+10),fill=GOLD)
    txt=D.get('congrats','Tabriklaymiz jamoa!');f=fit(d,txt,66,760);tw=d.textlength(txt,font=f)
    d.text((540,1145),txt,font=f,fill=NAVY,anchor='mm')
    emo(im,D.get('el','🎉'),540-tw/2-60,1145,64);emo(im,D.get('er','🔥'),540+tw/2+60,1145,64)
    d.text((540,1207),D.get('note',"Bonuslar oylikka qo'shiladi"),font=F(28),fill=MUT,anchor='mm')
    im.save(out)
if __name__=='__main__':
    render(json.load(open(sys.argv[1])),sys.argv[2])
