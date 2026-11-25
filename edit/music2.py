"""Set 2 müzikleri: chrome (drill 142), poster (funk hip-hop 100), dream (ambient 72)."""
import sys, os, json, numpy as np
from music import *  # noqa


def drill():
    bpm = 142; b = 60 / bpm; bar = 4 * b
    bars = 11
    D = bars * bar + 2.2
    mix = np.zeros((int(D * SR), 2)); dr = np.zeros_like(mix); bass = np.zeros_like(mix); mel = np.zeros_like(mix)
    # C# minör: karanlık piyano/zil melodisi (2 bar döngü)
    motif = [(0, 73, 1.0), (0.75, 76, 0.5), (1.5, 75, 0.5), (2, 73, 1.5), (4, 71, 1.0), (4.75, 73, 0.5), (5.5, 68, 0.5), (6, 69, 1.8)]
    pads = [[49, 56, 61, 64], [45, 52, 57, 61]]
    for k in range(bars - 1):
        t0 = k * bar
        if k % 2 == 0:
            for beat, n, d in motif:
                put(mel, piano(n, d * b + 1.0, 0.55), t0 + beat * b)
                put(mel, st(pluck_fast(n + 12, 0.3, 0.6, 0.18), 0.35), t0 + beat * b)
        put(mel, pad(pads[k % 2], bar + 0.3, (400, 1200), 0.3, 0.4, 0.06), t0)
        if k >= 1 and k != 5:   # bar 6: kırılma (yalnız melodi + 808 kayması)
            # drill hi-hat: 8'lik + triplet rulolar
            for s in range(8):
                put(dr, hat(0.04) * (0.8 if s % 2 == 0 else 0.55), t0 + s * b / 2)
            if k % 2 == 1:
                for r in range(3):
                    put(dr, hat(0.03) * 0.5, t0 + 3 * b + r * b / 3)
                for r in range(4):
                    put(dr, hat(0.025) * 0.45, t0 + 1.5 * b + r * b / 8)
            put(dr, kick(0.45, 140, 45), t0)
            put(dr, kick(0.4, 140, 45) * 0.8, t0 + 2.5 * b)
            put(dr, snare(0.35, 200) * 1.0, t0 + 2 * b)
            put(dr, clap() * 0.7, t0 + 2 * b + 0.005)
            if k % 2:
                put(dr, snare(0.25, 210) * 0.5, t0 + 3.75 * b)
        if k >= 1:
            r = 25 if k % 2 == 0 else 21
            put(bass, b808(r + 12, 1.2 * b, drive=2.6), t0)
            put(bass, b808(r + 12, 0.9 * b, glide_from=r + 19, drive=2.6), t0 + 1.5 * b)
            put(bass, b808(r + 12 + (3 if k % 2 else 0), 1.4 * b, glide_from=r + 12, drive=2.6), t0 + 2.5 * b)
    T = (bars - 1) * bar
    put(dr, kick(0.8, 120, 36, 1.4), T)
    put(bass, b808(25 + 12, 2.0, drive=2.4), T)
    put(mel, piano(61, 2.5, 0.6), T); put(mel, piano(64, 2.5, 0.5), T); put(mel, piano(68, 2.5, 0.5), T)
    mel = reverb(mel, reverb_ir(2.6, 2.2), 0.3)
    dr = reverb(dr, reverb_ir(0.6, 9), 0.08)
    mix += mel * 0.85 + dr + bass * 0.95
    return mix, dict(bpm=bpm, beat=b, bar=bar, end=T, dur=D)


def funk():
    bpm = 100; b = 0.6; bar = 2.4
    bars = 8
    D = bars * bar + 2.0
    mix = np.zeros((int(D * SR), 2)); dr = np.zeros_like(mix); bs = np.zeros_like(mix); ky = np.zeros_like(mix)
    # E minör funk: Em9 – A13 (2'li)
    ch = [[52, 55, 59, 62, 66], [57, 61, 64, 66, 67]]
    bassline = [(0, 28), (0.75, 40), (1.5, 38), (2, 31), (2.75, 33), (3.5, 35)]
    for k in range(bars):
        t0 = k * bar
        c = ch[k % 2]
        # stab akorlar (16'lık senkop)
        for beat in ((0.5, 1.75, 2.5, 3.25) if k % 2 == 0 else (0.5, 1.5, 2.75, 3.5)):
            for j, n in enumerate(c):
                x = epiano(n, 0.35, 0.65)
                put(ky, np.tanh(x * 2.0) * 0.8, t0 + beat * b + j * 0.004)
        if k >= 1:
            sw = 0.07 * b
            for s in range(8):
                put(dr, hat(0.045) * (0.8 if s % 2 == 0 else 0.5), t0 + s * b / 2 + (sw if s % 2 else 0))
            put(dr, kick(0.4, 130, 50, 1.1, 0.6), t0)
            put(dr, kick(0.35, 130, 50, 1.0, 0.6) * 0.75, t0 + 1.25 * b)
            put(dr, kick(0.35, 130, 50, 1.0, 0.6) * 0.85, t0 + 2.5 * b)
            for bb in (1, 3):
                put(dr, snare(0.28, 185, 1.1), t0 + bb * b)
            if k % 2:
                put(dr, snare(0.15, 200, 0.6) * 0.35, t0 + 3.75 * b)
            put(dr, hat(open_=True) * 0.45, t0 + 3.5 * b + sw)
            for beat, n in bassline:
                nn = n + (5 if k % 2 else 0)
                x = pluck_fast(nn + 12, 0.32 * b * 2, 0.25, 0.9)
                put(bs, st(np.tanh(x * 2.5) * 0.7), t0 + beat * b)
        # brass benzeri yükselen stab: her 2 barda
        if k % 2 == 1 and k >= 3:
            for j, n in enumerate([64, 67, 71]):
                x = supersaw(midi(n), 0.3, 5, 0.1)
                x = lp(x, 2500) * np.exp(-np.arange(len(x)) / SR * 6)[:, None] * 0.25
                put(ky, x, t0 + 3.5 * b)
    T = bars * bar
    put(dr, kick(0.6, 120, 40, 1.2), T); put(bs, st(np.tanh(pluck_fast(40, 1.0, 0.3, 0.9) * 2.5) * 0.7), T)
    for j, n in enumerate(ch[0]):
        put(ky, epiano(n, 1.6, 0.5), T + j * 0.01)
    ky = reverb(ky, reverb_ir(1.4, 4), 0.2)
    mix += ky * 0.8 + dr + bs * 0.9
    return mix, dict(bpm=bpm, beat=b, bar=bar, end=T, dur=D)


def ambient():
    bpm = 72; b = 60 / bpm; bar = 4 * b
    bars = 6
    D = bars * bar + 3.0
    mix = np.zeros((int(D * SR), 2)); pn = np.zeros_like(mix); pd = np.zeros_like(mix)
    chords = [[50, 57, 62, 64, 69], [46, 53, 58, 62, 65], [43, 50, 55, 58, 62], [45, 52, 57, 61, 64]]
    for k in range(bars):
        t0 = k * bar
        c = chords[k % 4]
        put(pd, pad(c, bar + 1.5, (300, 1800) if k % 2 == 0 else (1800, 400), 1.4, 1.5, 0.12, 0.2), t0)
        # seyrek piyano notaları
        notes = [c[-1] + 12, c[-2] + 12, c[-3] + 12, c[-1] + 7]
        for i, beat in enumerate((0, 1.5, 2.5, 3.25)):
            if (k + i) % 3 == 2:
                continue
            put(pn, piano(notes[i], 3.0, 0.35), t0 + beat * b)
        if 2 <= k <= 4:
            put(mix, st(kick(0.7, 70, 34, 0.5, 0.0) * 0.35), t0)
            put(mix, st(kick(0.6, 65, 32, 0.4, 0.0) * 0.22), t0 + 0.3)
        put(mix, sub_drone(c[0] - 12, bar + 1.0, 0.18), t0)
    # yükselen ters-pad (tonal) bar 3 sonunda
    x = pad([62, 69, 74], 2.2, (200, 5000), 2.0, 0.05, 0.12)
    put(pd, x, 3 * bar - 2.1)
    T = bars * bar
    put(pn, piano(74, 4.0, 0.4), T); put(pn, piano(69, 4.0, 0.3), T + 0.02)
    pn = reverb(pn, reverb_ir(5.0, 1.0, 0.04, 6000), 0.5)
    pd = reverb(pd, reverb_ir(5.0, 1.0, 0.04, 4000), 0.4)
    mix += pn * 0.9 + pd
    return mix, dict(bpm=bpm, beat=b, bar=bar, end=T, dur=D)


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    meta = {}
    for name, fn in (('chrome', drill), ('poster', funk), ('dream', ambient)):
        x, m = fn()
        master(x, os.path.join(out, name + '.wav'))
        meta[name] = m
        print(name, m)
    json.dump(meta, open(os.path.join(out, 'beats2.json'), 'w'), indent=1)
