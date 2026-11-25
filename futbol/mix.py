#!/usr/bin/env python3
"""Müzik yatağı + miks (kit kuralları): SFX yok, ses önde.

- Ambient pad: re minör akorlar (Dm – B♭ – F – C), yumuşak atak, hafif chorus ve yankı.
- Ducking: konuşma sırasında müzik ≈0.13, aralarda ≈0.34 (müzik RMS'i konuşmaya eşitlendikten sonra).
- Master: loudnorm=I=-14:TP=-1.2 → müzikli ve müziksiz iki versiyon.

    python3 futbol/mix.py --ep pilot_bjk_hbs
Girdi: out/<ep>/voice.wav + futbol/data/<ep>_tl.js   Çıktı: out/<ep>/mix.wav, out/<ep>/voice_master.wav
"""
import argparse, json, re, subprocess
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000

def read_wav(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def write_wav(p, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-i', '-', '-c:a', 'pcm_s24le', str(p)], input=x.astype(np.float32).tobytes(), check=True)

def pad(dur, seed=4):
    rng = np.random.default_rng(seed)
    t = np.arange(int(dur * SR)) / SR
    # re minör: Dm, B♭, F, C (MIDI)
    chords = [[50, 57, 62, 65], [46, 53, 58, 62], [41, 53, 57, 60], [48, 55, 60, 64]]
    seg = 6.0; out = np.zeros_like(t)
    for k in range(int(dur / seg) + 2):
        t0 = k * seg; ch = chords[k % 4]
        env = np.clip((t - t0 + 1.5) / 2.5, 0, 1) * np.clip((t0 + seg + 1.5 - t) / 2.5, 0, 1)
        env = np.sin(env * np.pi / 2) ** 2
        for n in ch:
            f = 440 * 2 ** ((n - 69) / 12)
            for det in (-0.12, 0.0, 0.11):           # chorus: hafif akortsuz kopyalar
                ph = rng.uniform(0, 2 * np.pi)
                ff = f * 2 ** (det / 12)
                out += env * (np.sin(2 * np.pi * ff * t + ph) + .18 * np.sin(4 * np.pi * ff * t + ph)) / 3
    # yumuşak alçak geçiren (tek kutuplu) + yavaş nefes modülasyonu
    a = np.exp(-2 * np.pi * 1800 / SR); y = np.empty_like(out); acc = 0.0
    for i, v in enumerate(out): acc = (1 - a) * v + a * acc; y[i] = acc
    y *= .85 + .15 * np.sin(2 * np.pi * t / 11)
    return y / (np.max(np.abs(y)) + 1e-9)

def load_tl(ep):
    js = (ROOT / 'futbol' / 'data' / f'{ep}_tl.js').read_text()
    return json.loads(re.search(r'window\.TL = (\[.*?\]);', js).group(1))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ep', default='pilot_bjk_hbs')
    ap.add_argument('--speech', type=float, default=.13); ap.add_argument('--gaps', type=float, default=.34)
    a = ap.parse_args()
    out = ROOT / 'out' / a.ep
    v = read_wav(out / 'voice.wav'); dur = len(v) / SR
    m = pad(dur)
    rms = lambda x: np.sqrt(np.mean(x ** 2) + 1e-12)
    speech = np.zeros(len(v), bool)
    for s in load_tl(a.ep): speech[int(s['t0'] * SR):int(s['t1'] * SR)] = True
    m *= rms(v[speech]) / rms(m)                       # müzik RMS'i konuşmaya eşitlenir
    g = np.where(speech, a.speech, a.gaps).astype(np.float32)
    k = int(.35 * SR); g = np.convolve(g, np.hanning(k) / np.hanning(k).sum(), 'same')   # yumuşak ducking geçişi
    fade = np.minimum(1, np.minimum(np.arange(len(m)) / (1.5 * SR), (len(m) - np.arange(len(m))) / (2.0 * SR)))
    write_wav(out / '_mix_raw.wav', v + m * g * fade)
    write_wav(out / '_voice_raw.wav', v)
    for src, dst in (('_mix_raw.wav', 'mix.wav'), ('_voice_raw.wav', 'voice_master.wav')):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out / src), '-af', 'loudnorm=I=-14:TP=-1.2:LRA=11', '-ar', str(SR), '-c:a', 'pcm_s24le', str(out / dst)], check=True)
        (out / src).unlink()
    print('hazır:', out / 'mix.wav', out / 'voice_master.wav')

if __name__ == '__main__':
    main()
