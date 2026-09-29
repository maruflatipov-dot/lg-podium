#!/usr/bin/env python3
"""One-command pipeline for the TOP-3 podium picture.
  python3 publish.py render <data.json> <name>   -> renders out/<name>.png, checks it, commits, pushes;
                                                    prints RAW_URL=<url> on success (exit 0)
  python3 publish.py cleanup <name>              -> removes out/<name>.png from the repo and pushes
data.json: {"title","sub","el","er","note"(optional),"top":[{"name","net","units","bonus"} x3 — 1st, 2nd, 3rd]}
"""
import sys,os,json,subprocess,time
ROOT=os.path.dirname(os.path.abspath(__file__))
RAW="https://raw.githubusercontent.com/maruflatipov-dot/lg-podium/main/out/%s.png"
def git(*a,check=True):
    r=subprocess.run(['git','-C',ROOT,*a],capture_output=True,text=True)
    if check and r.returncode: raise SystemExit('GIT_ERROR %s: %s'%(' '.join(a),(r.stderr or r.stdout).strip()[-300:]))
    return r
def ident():
    git('config','user.email','maruflatipov@gmail.com'); git('config','user.name','LG podium bot')
def push(msg):
    git('commit','-q','-m',msg)
    for i in range(3):
        git('fetch','-q','origin','main',check=False); git('rebase','-q','origin/main',check=False)
        if git('push','-q','origin','HEAD:main',check=False).returncode==0: return
        time.sleep(5)
    raise SystemExit('GIT_ERROR push failed 3 times')
def validate(D):
    top=D.get('top') or []
    if len(top)!=3: raise SystemExit('DATA_ERROR need exactly 3 winners, got %d'%len(top))
    for i,t in enumerate(top):
        for k in ('name','net','units','bonus'):
            if not str(t.get(k,'')).strip(): raise SystemExit('DATA_ERROR top[%d].%s is empty'%(i,k))
def main():
    if len(sys.argv)<3: raise SystemExit(__doc__)
    cmd=sys.argv[1]; ident()
    if cmd=='render':
        D=json.load(open(sys.argv[2])); name=sys.argv[3]; validate(D)
        sys.path.insert(0,ROOT); import render
        os.makedirs(os.path.join(ROOT,'out'),exist_ok=True); out=os.path.join(ROOT,'out',name+'.png')
        render.render(D,out)
        from PIL import Image
        im=Image.open(out)
        if im.size!=(1080,1350): raise SystemExit('RENDER_ERROR bad size %s'%(im.size,))
        git('add','out/%s.png'%name); push('podium '+name)
        print('RAW_URL='+RAW%name+'?v=%d'%int(time.time()))
    elif cmd=='cleanup':
        name=sys.argv[2]; p='out/%s.png'%name
        git('pull','-q','--rebase','origin','main',check=False)
        if not os.path.exists(os.path.join(ROOT,p)): print('CLEANUP_OK (nothing to remove)'); return
        git('rm','-q',p); push('cleanup '+name); print('CLEANUP_OK')
    else: raise SystemExit(__doc__)
if __name__=='__main__': main()
