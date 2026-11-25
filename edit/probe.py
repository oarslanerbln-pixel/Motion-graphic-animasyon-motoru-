import subprocess, numpy as np, glob, os, sys
U=sys.argv[1]
for f in sorted(glob.glob(U+'/*.mp4')):
    raw=subprocess.run(['ffmpeg','-v','error','-ss','1','-i',f,'-map','0:v:0','-frames:v','1','-vf','scale=480:-2','-f','rawvideo','-pix_fmt','rgb48le','-'],capture_output=True).stdout
    a=np.frombuffer(raw,np.uint16).astype(np.float32)/65535
    a=a.reshape(-1,3); Y=a@[0.2126,0.7152,0.0722]
    p=np.percentile(Y,[0.5,5,50,95,99.5]); s=(a.max(1)-a.min(1)).mean()
    print(os.path.basename(f)[33:37], np.round(p,3), 'sat',round(float(s),3), 'rgbmean',np.round(a.mean(0),3))
