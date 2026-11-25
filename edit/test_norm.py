import lib, numpy as np, cv2, time, sys
src=lib.find_sources(); print(sorted(src))
lib.match_target(src); print(lib.TARGET)
W,H=1080,1920
tiles=[]
for cid in sorted(src):
    t0=time.time(); c=lib.load(cid,src,W,H); print(cid,c.w,c.h,c.n,round(time.time()-t0,1))
    raw=lib._decode(src[cid],216,384)[c.n//2].astype(np.float32)/65535
    a=lib.place(c.frame(c.dur/2),c,c.dur/2,W,H)
    b=cv2.resize(raw,(216,384)) if raw.shape[0]>raw.shape[1] else cv2.resize(raw,(216,int(216*raw.shape[0]/raw.shape[1])))
    bb=np.zeros((384,216,3),np.float32); bb[:b.shape[0]]=b
    tiles.append(np.vstack([bb,cv2.resize(a,(216,384))]))
im=np.hstack(tiles)
cv2.imwrite(sys.argv[1],(np.clip(im,0,1)[...,::-1]*255).astype(np.uint8))
