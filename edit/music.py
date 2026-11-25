"""Üç stil için sentezlenmiş müzik (numpy). SFX yok; tüm vuruşlar müziğin parçası.
python3 music.py <çıkış_klasörü>  → urban.wav trailer.wav editorial.wav + beats.json"""
import numpy as np, sys, os, json, subprocess
from scipy.signal import lfilter, butter, sosfilt, fftconvolve

SR = 48000
rng = np.random.default_rng(42)


def t_(d):
    return np.arange(int(d * SR)) / SR


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def env_adsr(n, a=0.005, d=0.1, s=0.7, r=0.2, hold=None):
    hold = n / SR if hold is None else hold
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-6),
                 np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-6), s))
    rel = np.clip((t - hold) / max(r, 1e-6), 0, 1)
    return e * (1 - rel)


def lp(x, fc, order=2):
    sos = butter(order, min(fc, SR / 2 * 0.98) / (SR / 2), 'low', output='sos')
    return sosfilt(sos, x, axis=0)


def hp(x, fc, order=2):
    sos = butter(order, fc / (SR / 2), 'high', output='sos')
    return sosfilt(sos, x, axis=0)


def bp(x, lo, hi, order=2):
    sos = butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos')
    return sosfilt(sos, x, axis=0)


def sweep_lp(x, f0, f1, curve=2.0):
    """zamanla açılan low-pass (blok blok)."""
    out = np.zeros_like(x)
    n = len(x); B = 1024
    zi = None
    for i in range(0, n, B):
        u = (i / max(n - 1, 1)) ** curve
        fc = f0 * (f1 / f0) ** u
        b, a = butter(2, min(fc, SR * 0.48) / (SR / 2), 'low')
        if zi is None:
            zi = np.zeros((max(len(a), len(b)) - 1,) + x.shape[1:])
        out[i:i + B], zi = lfilter(b, a, x[i:i + B], axis=0, zi=zi)
    return out


def saw(f, t, phase=0):
    p = (f * t + phase) % 1
    return 2 * p - 1


def supersaw(freq, d, n=5, det=0.12):
    t = t_(d)
    L = np.zeros_like(t); R = np.zeros_like(t)
    for k in range(n):
        c = (k - (n - 1) / 2) / max((n - 1) / 2, 1)
        f = freq * 2 ** (c * det / 12)
        s = saw(f, t, rng.random())
        pan = 0.5 + 0.4 * c
        L += s * (1 - pan); R += s * pan
    return np.stack([L, R], 1) / n


def reverb_ir(d=2.2, decay=3.0, pre=0.02, bright=6000):
    n = int(d * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-decay * t)[:, None]
    ir = lp(ir, bright)
    ir[: int(pre * SR)] = 0
    return ir / np.sqrt((ir ** 2).sum(0))


def reverb(x, ir, wet=0.25):
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet


def st(m, pan=0.0):
    return np.stack([m * (1 - pan) ** 0.5, m * (1 + pan) ** 0.5], 1) / np.sqrt(2) * 1.414 / 1.414


def put(buf, x, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    x = x if x.ndim == 2 else st(x)
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i]


# ---------------------------------------------------------------- davullar
def kick(d=0.45, f0=150, f1=46, punch=1.0, click=0.5):
    t = t_(d)
    f = f1 + (f0 - f1) * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    cl = rng.standard_normal(len(t)) * np.exp(-t * 400) * click
    x = np.tanh((body + hp(cl, 2000) * 0.4) * (1.6 * punch))
    return x * 0.9


def b808(note, d=0.9, glide_from=None, drive=2.2):
    t = t_(d)
    f = np.full_like(t, midi(note))
    if glide_from is not None:
        f = midi(note) + (midi(glide_from) - midi(note)) * np.exp(-t * 18)
    f = f * (1 + 0.6 * np.exp(-t * 45))
    ph = 2 * np.pi * np.cumsum(f) / SR
    e = np.exp(-t * 1.6) * np.clip(t / 0.004, 0, 1)
    e[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return np.tanh(np.sin(ph) * e * drive) * 0.75


def snare(d=0.3, tone=190, bright=1.0):
    t = t_(d)
    n = rng.standard_normal(len(t))
    nz = bp(n, 1500, 9000) * np.exp(-t * 17) * bright
    body = np.sin(2 * np.pi * tone * t) * np.exp(-t * 30)
    return np.tanh((nz * 0.9 + body * 0.7) * 1.4) * 0.6


def clap(d=0.35):
    t = t_(d)
    n = bp(rng.standard_normal(len(t)), 900, 7000)
    e = np.zeros_like(t)
    for k, o in enumerate([0, 0.011, 0.022, 0.034]):
        e += np.where(t >= o, np.exp(-(t - o) * (180 if k < 3 else 16)), 0)
    return n * e * 0.5


def hat(d=0.06, open_=False):
    t = t_(0.35 if open_ else d)
    n = hp(rng.standard_normal(len(t)), 7500, 4)
    # metalik: kare dalga kümesi
    m = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (317, 421, 537, 691, 823, 1093)) / 6
    m = hp(m, 7000, 4)
    return (n * 0.7 + m * 0.5) * np.exp(-t * (9 if open_ else 70)) * 0.28


def shaker(d=0.09):
    t = t_(d)
    n = bp(rng.standard_normal(len(t)), 5000, 12000)
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return n * e * 0.15


def tom(note=45, d=0.9):
    t = t_(d)
    f = midi(note) * (1 + 0.8 * np.exp(-t * 20))
    ph = 2 * np.pi * np.cumsum(f) / SR
    b = np.sin(ph) * np.exp(-t * 5)
    nz = lp(rng.standard_normal(len(t)), 1200) * np.exp(-t * 25) * 0.5
    return np.tanh((b + nz) * 2.0) * 0.8


# ----------------------------------------------------------- melodik
def epiano(note, d=1.2, vel=0.6):
    t = t_(d)
    f = midi(note)
    idx = 1.8 * np.exp(-t * 4) * vel
    mod = np.sin(2 * np.pi * f * t) * idx
    car = np.sin(2 * np.pi * f * t + mod)
    tine = np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 14) * 0.15
    e = np.exp(-t * 1.4) * np.clip(t / 0.003, 0, 1)
    e *= np.clip((d - t) / 0.08, 0, 1)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    m = (car + tine) * e * vel * 0.35
    return np.stack([m * trem, m * (2 - trem)], 1)


def piano(note, d=2.0, vel=0.6):
    t = t_(d)
    f = midi(note)
    x = np.zeros_like(t)
    for h, a in ((1, 1), (2, 0.5), (3, 0.28), (4, 0.15), (5, 0.08), (6, 0.04)):
        fh = f * h * (1 + 0.0004 * h * h)
        x += a * np.sin(2 * np.pi * fh * t) * np.exp(-t * (1.2 + h * 0.9))
    ham = lp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 90) * 0.15
    e = np.clip(t / 0.002, 0, 1) * np.clip((d - t) / 0.1, 0, 1)
    return st((x * 0.3 + ham) * e * vel, (note - 64) / 60)


def pad(notes, d, cutoff=(500, 2400), att=0.8, rel=1.0, vol=0.18, det=0.14):
    x = sum(supersaw(midi(n), d, 5, det) for n in notes) / len(notes)
    x = sweep_lp(x, cutoff[0], cutoff[1], 1.0)
    e = env_adsr(len(x), att, 0.5, 0.85, rel, hold=d - rel)[:, None]
    return x * e * vol


def pluck(note, d=0.6, bright=0.5):
    """Karplus-Strong."""
    f = midi(note); N = int(SR / f)
    n = int(d * SR)
    buf = rng.uniform(-1, 1, N)
    buf = lp(buf, 2000 + 8000 * bright)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % N]
        buf[i % N] = 0.5 * (buf[i % N] + buf[(i + 1) % N]) * 0.996
    return out * 0.5


def pluck_fast(note, d=0.5, bright=0.5, vel=0.6):
    """hızlı 'pluck': filtre zarflı testere."""
    t = t_(d)
    x = saw(midi(note), t) * 0.6 + saw(midi(note) * 1.005, t) * 0.4
    fc = 300 + (1500 + 5000 * bright) * np.exp(-t * 12)
    # blok filtre
    out = np.zeros_like(x); B = 256; zi = np.zeros(2)
    for i in range(0, len(x), B):
        b, a = butter(2, fc[i] / (SR / 2), 'low')
        out[i:i + B], zi = lfilter(b, a, x[i:i + B], zi=zi)
    return out * np.exp(-t * 6) * np.clip(t / 0.002, 0, 1) * vel * 0.5


def sub_drone(note, d, vol=0.3):
    t = t_(d)
    x = np.sin(2 * np.pi * midi(note) * t) + 0.3 * np.sin(2 * np.pi * midi(note) * 2.003 * t)
    e = env_adsr(len(t), 1.5, 0.1, 1, 1.5, hold=d - 1.5)
    return st(x * e * vol)


def braam(notes, d=2.6, vol=0.5):
    """trailer 'braam': kalın pirinç benzeri akor, açılan filtre + distorsiyon."""
    x = sum(supersaw(midi(n), d, 7, 0.18) for n in notes) / len(notes)
    t = t_(d)
    out = np.zeros_like(x); B = 512; zi = np.zeros((2, 2))
    for i in range(0, len(x), B):
        tt = i / SR
        fc = 180 + 2200 * np.exp(-tt * 1.6) * (1 - np.exp(-tt * 40))
        b, a = butter(2, fc / (SR / 2), 'low')
        out[i:i + B], zi = lfilter(b, a, x[i:i + B], axis=0, zi=zi)
    e = np.clip(t / 0.02, 0, 1) * np.exp(-t * 0.9)
    return np.tanh(out * 3.0) * e[:, None] * vol


def riser_tone(note, d, vol=0.12):
    """tonal yükselen (gürültü/whoosh değil)."""
    t = t_(d)
    f = midi(note) * 2 ** (t / d * 1.0)  # bir oktav yükselir
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)) * (t / d) ** 2
    return st(x * vol)


def tick(d=0.04, f=2400):
    t = t_(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 160) * 0.25


def master(x, path):
    x = hp(x, 28)
    pk = np.abs(x).max()
    x = x / pk * 0.89
    # yumuşak saturasyon / glue
    x = np.tanh(x * 1.25) / np.tanh(1.25)
    tmp = path + '.tmp.wav'
    import soundfile as sf
    sf.write(tmp, x.astype(np.float32), SR, subtype='FLOAT')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af',
                    'loudnorm=I=-14:TP=-1.2:LRA=11', '-ar', str(SR), '-c:a', 'pcm_s24le', path], check=True)
    os.remove(tmp)


# ===================================================================== URBAN
def urban():
    bpm = 92; b = 60 / bpm; bar = 4 * b
    bars = 8
    D = bars * bar + 2.0
    mix = np.zeros((int(D * SR), 2)); drums = np.zeros_like(mix); bass = np.zeros_like(mix)
    keys = np.zeros_like(mix)
    # Fm9 – Dbmaj7 – Abmaj7 – Eb6 (F minör)
    chords = [[53, 56, 60, 63, 67], [49, 53, 56, 60, 65], [56, 60, 63, 67], [51, 55, 58, 60, 63]]
    roots = [29, 25, 32, 27]
    ir = reverb_ir(2.4, 2.6)
    for k in range(bars):
        t0 = k * bar
        ch = chords[k % 4]
        # keys: e-piano, swing'li vuruşlar
        for beat, dur, vel in ((0, 1.6, 0.55), (1.5, 0.6, 0.35), (2.5, 1.2, 0.45)):
            for j, n in enumerate(ch):
                put(keys, epiano(n, dur * b + 0.6, vel * (0.9 if j else 1)), t0 + beat * b + j * 0.008)
        put(mix, pad([n + 12 for n in ch[:3]], bar + 0.6, (400, 1400), 0.5, 0.6, 0.06), t0)
        if k >= 2:
            # davul
            swing = 0.06 * b
            for s in range(8):
                ts = t0 + s * b / 2 + (swing if s % 2 else 0)
                if k == 7 and s >= 6:
                    continue
                put(drums, hat(0.05) * (0.9 if s % 2 == 0 else 0.6), ts)
            if k in (3, 5):  # trap hat rulosu
                for r in range(6):
                    put(drums, hat(0.03) * 0.5, t0 + 3 * b + r * b / 6)
            put(drums, kick(0.5), t0)
            put(drums, kick(0.4) * 0.8, t0 + 1.75 * b)
            if k % 2:
                put(drums, kick(0.4) * 0.7, t0 + 2.5 * b)
            for bb in (1, 3):
                if k == 7 and bb == 3:
                    continue
                put(drums, snare(0.3) * 0.9 + 0, t0 + bb * b)
                put(drums, clap(0.35) * 0.8, t0 + bb * b + 0.004)
            put(drums, hat(open_=True) * 0.5, t0 + 3.5 * b)
            # 808
            r = roots[k % 4]
            put(bass, b808(r + 12 - 12, 1.6 * b), t0)
            put(bass, b808(r, 1.0 * b, glide_from=r + 7), t0 + 1.75 * b)
            put(bass, b808(r + 12 if k % 2 else r, 1.2 * b, glide_from=r), t0 + 2.5 * b)
    # son vuruş: her şey durur, tek 808 + keys tail
    put(drums, kick(0.6) * 1.1, 8 * bar)
    put(bass, b808(29, 1.8), 8 * bar)
    for j, n in enumerate(chords[0]):
        put(keys, epiano(n, 2.0, 0.5), 8 * bar + j * 0.01)
    # intro: davullar yokken keys low-pass
    nI = int(2 * bar * SR)
    keys[:nI] = sweep_lp(keys[:nI], 700, 6000, 3)
    keys = reverb(keys, ir, 0.3)
    drums = reverb(drums, reverb_ir(0.8, 7), 0.12)
    mix += keys * 0.9 + drums * 1.0 + bass * 0.9
    return mix, dict(bpm=bpm, beat=b, bar=bar, drop=2 * bar, end=8 * bar, dur=D)


# =================================================================== TRAILER
def trailer():
    bpm = 120; b = 0.5
    D = 25.0
    mix = np.zeros((int(D * SR), 2))
    ir = reverb_ir(3.5, 1.6, 0.03, 5000)
    big = np.zeros_like(mix)
    # 0–8: drone + nabız + tik
    put(mix, sub_drone(26, 8.6, 0.35), 0)       # D1
    put(mix, pad([62, 65, 69], 8.4, (300, 1600), 3.0, 1.2, 0.07, 0.08), 0)
    for k in range(16):
        put(mix, st(tick(0.04, 2200 if k % 2 == 0 else 1700) * (0.5 + 0.5 * k / 16)), k * 0.5)
    for k in (0, 1, 2, 3, 5, 6, 7):  # kalp atışı benzeri sub nabız
        put(mix, st(kick(0.6, 90, 38, 0.6, 0.0) * 0.55), k * 1.0)
        put(mix, st(kick(0.5, 80, 36, 0.5, 0.0) * 0.35), k * 1.0 + 0.24)
    put(big, braam([38, 45, 50, 53], 3.5, 0.55), 4.0)
    put(mix, riser_tone(50, 4.0, 0.10), 4.0)
    put(big, braam([38, 45, 50, 53, 57], 3.0, 0.65), 8.0)
    # 8–16: ostinato + toms + kick
    arp = [62, 65, 69, 74, 69, 65, 62, 57]
    for s in range(32):
        tt = 8 + s * b / 2
        n = arp[s % 8] + (12 if s >= 24 else 0)
        put(mix, st(pluck_fast(n, 0.28, 0.3 + 0.7 * s / 32, 0.55), 0.3 if s % 2 else -0.3), tt)
    put(mix, pad([50, 57, 62, 65], 8.2, (500, 4000), 0.3, 0.4, 0.09), 8)
    for s in range(16):
        tt = 8 + s * b
        put(big, st(kick(0.5, 160, 44, 1.2, 0.6) * 0.9), tt)
        if s % 4 == 2:
            put(big, st(snare(0.4, 180, 1.2) * 0.9), tt)
        if s >= 8:
            put(big, st(tom(41 if s % 2 else 45, 0.7) * 0.6, 0.3 if s % 2 else -0.3), tt + b / 2)
    for r in range(8):  # 15–16 tom dolgusu
        put(big, st(tom(43 - r, 0.5) * (0.5 + r * 0.06), -0.4 + r * 0.1), 15 + r * 0.125)
    put(mix, riser_tone(57, 4.0, 0.12), 12)
    # 16: büyük vuruş + ani sessizlik
    put(big, braam([26, 38, 45, 50, 53, 57], 1.0, 0.8), 16.0)
    put(big, st(kick(0.8, 120, 34, 1.4, 0.3) * 1.1), 16.0)
    # 17–21: yeniden kurulum, hızlanan nabız
    times = [17.0, 17.75, 18.4, 18.95, 19.4, 19.75, 20.05, 20.3, 20.5, 20.65, 20.8]
    for i, tt in enumerate(times):
        put(big, st(kick(0.45, 150, 44, 1.0, 0.5) * (0.6 + i * 0.04)), tt)
        put(mix, st(pluck_fast(74 if i % 2 else 69, 0.25, 0.8, 0.45)), tt)
    put(mix, riser_tone(62, 4.0, 0.14), 17)
    # 21: final
    put(big, braam([26, 38, 45, 50, 53, 57, 62], 4.0, 0.9), 21.0)
    put(big, st(kick(1.0, 110, 32, 1.5, 0.3) * 1.2), 21.0)
    put(mix, pad([62, 65, 69, 74], 4.0, (2000, 500), 0.05, 2.0, 0.08), 21.0)
    # 16.0–17.0 arası sessizlik: braam 1 sn'de kesildi; kuyruğu reverb taşır
    mix += reverb(big, ir, 0.28) * 1.0
    mix = reverb(mix, ir, 0.15)
    return mix, dict(bpm=bpm, beat=b, hits=[4.0, 8.0, 16.0, 21.0], silence=[16.35, 17.0], end=21.0, dur=D)


# ================================================================ EDITORIAL
def editorial():
    bpm = 118; b = 60 / bpm; bar = 4 * b
    bars = 10
    D = bars * bar + 2.5
    mix = np.zeros((int(D * SR), 2)); drums = np.zeros_like(mix); keys = np.zeros_like(mix)
    bass = np.zeros_like(mix)
    # Am9 – Fmaj9 – Cmaj7 – G6/B (deep house)
    chords = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 67], [52, 55, 60, 64, 67], [55, 59, 62, 64, 67]]
    roots = [33, 29, 36, 31]
    for k in range(bars):
        t0 = k * bar
        ch = chords[k % 4]
        # piyano akorları (ilk 2 bar yalnız)
        for beat, vel in ((0, 0.6), (1.5, 0.4), (2.5, 0.45)) if k >= 2 else ((0, 0.55), (2.5, 0.4)):
            for j, n in enumerate(ch):
                put(keys, piano(n, 1.6 * b + 0.5, vel), t0 + beat * b + j * 0.006)
        put(keys, pad(ch[:4], bar + 0.4, (600, 1800), 0.4, 0.5, 0.05), t0)
        if k >= 2 and k < bars - 1 or k == bars - 1:
            for s in range(4):
                if k == bars - 1 and s > 0:
                    break
                put(drums, st(kick(0.4, 130, 48, 0.9, 0.3) * 0.85), t0 + s * b)
                put(drums, st(hat(open_=True) * 0.35, 0.2), t0 + s * b + b / 2)
                if s % 2 == 1:
                    put(drums, st(clap() * 0.55, -0.05), t0 + s * b)
            if k < bars - 1:
                for s in range(16):
                    put(drums, st(shaker() * (1 if s % 2 else 0.55), -0.3), t0 + s * b / 4)
                # bas: offbeat deep bas
                r = roots[k % 4]
                for s in (0.5, 1.5, 2.5, 3.25):
                    t = t_(0.28 * b * 2)
                    x = np.sin(2 * np.pi * midi(r + 12) * t) * np.exp(-t * 5) * np.clip(t / 0.005, 0, 1)
                    x = np.tanh(x * 1.6) * 0.55
                    put(bass, st(x), t0 + s * b)
        elif k < 2:
            # intro: yalnız shaker yumuşak
            for s in range(8):
                put(drums, st(shaker() * 0.5, -0.3), t0 + s * b / 2 + b / 4)
    put(keys, piano(45, 3.0, 0.6), bars * bar - bar + 0)  # son akorun bas notası
    keys = reverb(keys, reverb_ir(2.8, 2.2), 0.32)
    drums = reverb(drums, reverb_ir(0.7, 8), 0.1)
    mix += keys + drums + bass * 0.9
    # bar 10 (son): yalnız tek kick + piyano tail
    return mix, dict(bpm=bpm, beat=b, bar=bar, drop=2 * bar, end=(bars - 1) * bar, dur=D)


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    meta = {}
    for name, fn in (('urban', urban), ('trailer', trailer), ('editorial', editorial)):
        x, m = fn()
        master(x, os.path.join(out, name + '.wav'))
        meta[name] = m
        print(name, m)
    json.dump(meta, open(os.path.join(out, 'beats.json'), 'w'), indent=1)
