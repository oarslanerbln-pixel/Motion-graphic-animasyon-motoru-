"""Yumuşak ambient pad (re minör) — SFX yok. usage: python3 muzik.py out.wav süre_sn"""
import sys, wave, numpy as np
out, dur = sys.argv[1], float(sys.argv[2]); sr = 48000
t = np.arange(int(sr*dur)) / sr
def note(n): return 440.0 * 2 ** ((n - 69) / 12)
# Dm9 → Bbmaj7 → Fmaj7 → C(add9) ; her biri dur/4
chords = [[50, 57, 62, 65, 69, 76], [46, 53, 58, 62, 65, 69], [41, 53, 57, 60, 64, 69], [48, 55, 60, 62, 64, 67]]
seg = dur / len(chords); sig = np.zeros_like(t)
for k, ch in enumerate(chords):
    env = np.clip((t - k*seg + 0.6) / 1.2, 0, 1) * np.clip(((k+1)*seg + 0.6 - t) / 1.2, 0, 1)
    env = np.sin(env * np.pi / 2) ** 2
    for n in ch:
        f = note(n)
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            ph = np.random.rand() * 6.28
            sig += env * (np.sin(2*np.pi*ff*t + ph) + 0.18*np.sin(4*np.pi*ff*t + ph)) / (1 + (n > 64) * 0.6)
lfo = 0.85 + 0.15 * np.sin(2*np.pi*0.18*t)
sig *= lfo
fade = np.clip(t / 1.2, 0, 1) * np.clip((dur - t) / 1.8, 0, 1)
sig *= fade; sig /= np.max(np.abs(sig)) + 1e-9; sig *= 0.6
st = np.stack([sig, np.roll(sig, int(sr*0.012))], 1)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
