#!/usr/bin/env python3
"""YouTube altyazısı (SRT): data/<ep>.js replikleri + data/<ep>_tl.js gerçek zamanları.

Kelime zamanları motorla aynı kuralla dağıtılır (hece oranı + noktalama duraklaması),
her blok en fazla 2 satır × 42 karakter.

    python3 futbol/srt.py --ep pilot_bjk_hbs   → out/<ep>/<ep>.tr.srt
"""
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOW = re.compile(r'[aeıioöuüâîûAEIİOÖUÜÂÎÛ]')

def segs(ep):
    js = (ROOT / 'futbol' / 'data' / f'{ep}.js').read_text(encoding='utf-8')
    block = js[js.index('segs:'):js.index('],', js.index('segs:'))]
    return [m.group(2).replace("\\'", "'") for m in re.finditer(r"spk:\s*'(\w)',\s*text:\s*'((?:[^'\\]|\\.)*)'", block)]

def tl(ep):
    t = (ROOT / 'futbol' / 'data' / f'{ep}_tl.js').read_text()
    return json.loads(re.search(r'window\.TL = (\[.*?\]);', t).group(1))

def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', default='pilot_bjk_hbs'); ap.add_argument('--maxc', type=int, default=42)
    a = ap.parse_args()
    out, n = [], 0
    for text, s in zip(segs(a.ep), tl(a.ep)):
        words = text.split()
        w = [max(1, len(VOW.findall(x))) + (.75 if re.search(r'[.?!…]$', x) else .55 if re.search(r'[,;:]$', x) else 0) for x in words]
        tot, acc, wt = sum(w), s['t0'], []
        for x in w: wt.append((acc, acc + x / tot * (s['t1'] - s['t0']))); acc = wt[-1][1]
        # blokla: 2 satır × maxc; cümle sonunda blok kır
        blocks, cur, lines, line = [], [], [], ''
        for i, x in enumerate(words):
            if len(line) + len(x) + (1 if line else 0) > a.maxc:
                lines.append(line); line = ''
                if len(lines) == 2: blocks.append((cur, lines)); cur, lines = [], []
            line = f'{line} {x}'.strip(); cur.append(i)
            if re.search(r'[.?!]$', x) and i < len(words) - 1:
                lines.append(line); blocks.append((cur, lines)); cur, lines, line = [], [], ''
        if line: lines.append(line)
        if cur: blocks.append((cur, lines))
        for bi, (idx, ls) in enumerate(blocks):
            pad = .15 if bi == len(blocks) - 1 else 0   # replik içi bloklar üst üste binmesin
            n += 1; out.append(f'{n}\n{ts(wt[idx[0]][0])} --> {ts(wt[idx[-1]][1] + pad)}\n' + '\n'.join(ls) + '\n')
    p = ROOT / 'out' / a.ep / f'{a.ep}.tr.srt'; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('\n'.join(out), encoding='utf-8'); print(p, n, 'blok')

if __name__ == '__main__':
    main()
