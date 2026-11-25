"""python3 render.py <stil> <v|h> [--prev t1,t2,...] [--out dosya] [--range a,b]"""
import sys, os, time, argparse, numpy as np, cv2
import lib, styles2 as styles
from engine2 import Engine2 as Engine

ap = argparse.ArgumentParser()
ap.add_argument('style'); ap.add_argument('fmt')
ap.add_argument('--prev'); ap.add_argument('--out'); ap.add_argument('--music')
ap.add_argument('--every', type=float, default=0)
a = ap.parse_args()

W, H = (1080, 1920) if a.fmt == 'v' else (1920, 1080)
src = lib.find_sources(); lib.match_target(src)
res = styles.STYLES[a.style](W, H)
shots, grade, overlay, pulse, mus, dur = res[:6]
eng = Engine(src, W, H, shots, grade, overlay, pulse, res[6] if len(res) > 6 else None)

if a.prev or a.every:
    ts = [float(x) for x in a.prev.split(',')] if a.prev else list(np.arange(0.2, dur, a.every))
    tiles = []
    for t in ts:
        img = eng.frame(t, int(t * 30))
        sm = (cv2.resize(np.clip(img, 0, 1).astype(np.float32), (W // 4, H // 4), interpolation=cv2.INTER_AREA)[..., ::-1] * 255).astype(np.uint8).copy()
        cv2.putText(sm, f'{t:.2f}', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        tiles.append(sm)
    cols = 8 if a.fmt == 'v' else 5
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    out = a.out or f'prev_{a.style}_{a.fmt}.jpg'
    cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(out)
    sys.exit()

wav = os.path.join(a.music, mus + '.wav')
w = lib.Writer(a.out, W, H, wav, crf=16, dur=dur)
n = int(round(dur * lib.FPS))
t0 = time.time()
for i in range(n):
    w.write(eng.frame(i / lib.FPS, i))
    if i % 60 == 0:
        print(f'{a.style}-{a.fmt} {i}/{n} {i / max(time.time() - t0, 1e-3):.1f} fps', flush=True)
w.close()
print('done', a.out, round(time.time() - t0), 's')
