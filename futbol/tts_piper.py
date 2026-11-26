#!/usr/bin/env python3
"""Yerel Türkçe TTS (Piper / sherpa-onnx) → voice.wav + gerçek segment zamanları (data/<ep>_tl.js).

Gemini anahtarı yokken kullanılan geçici motor; çıktı biçimi tts_gemini.py ile aynıdır.
Sesler (CC0 lisans, ticari kullanım serbest — NabuCasa voice-datasets):
  ANALİST → tr_TR-fahrettin-medium (sakin, biraz yavaş)
  TRİBÜN  → tr_TR-fettah-medium   (daha canlı, biraz hızlı)
DFKI sesi CC BY-NC-SA olduğu için KULLANILMAZ.

    pip install sherpa-onnx soundfile --break-system-packages
    # modeller: github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models  (vits-piper-tr_TR-*-medium)
    python3 futbol/tts_piper.py --ep pilot_bjk_hbs --models /home/user/tts_models

Ses zinciri (kit §3'ün TTS'e uyarlanmış hafif hâli): 48 kHz'e çıkarma, highpass 70, hafif varlık EQ,
deesser, yumuşak kompresör, çok kısa oda yankısı, limiter.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
VOICE = {'A': ('fahrettin', 1.12, .6, .75), 'T': ('fettah', 1.10, .65, .8)}   # ASR ölçümüyle seçildi (Whisper eşleşme: yavaş = daha anlaşılır)   # model, length_scale(yavaşlık), noise, noise_w

def load_segs(ep):
    js = (ROOT / 'futbol' / 'data' / f'{ep}.js').read_text(encoding='utf-8')
    block = js[js.index('segs:'):js.index('],', js.index('segs:'))]
    return [(m.group(1), m.group(2).replace("\\'", "'"))
            for m in re.finditer(r"spk:\s*'(\w)',\s*text:\s*'((?:[^'\\]|\\.)*)'", block)]

def norm(t):
    """Okunuş düzeltmeleri: yabancı isimler Türkçe okunuşa, işaretler sözcüğe."""
    rep = {'Vlahović': 'Vlahoviç', 'Trossard': 'Trosar', '≈': 'yaklaşık '}
    for a, b in rep.items(): t = t.replace(a, b)
    return t

def tts(models, name):
    import sherpa_onnx
    d = Path(models) / f'vits-piper-tr_TR-{name}-medium'
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=str(d / f'tr_TR-{name}-medium.onnx'), tokens=str(d / 'tokens.txt'),
                                                   data_dir=str(d / 'espeak-ng-data')), num_threads=2))
    return sherpa_onnx.OfflineTts(cfg)

def synth(engine, text, ls, ns, nw):
    try:
        cfg = engine.config.model.vits; cfg.length_scale, cfg.noise_scale, cfg.noise_scale_w = ls, ns, nw
    except Exception:
        pass
    a = engine.generate(text, sid=0, speed=1.0 / ls)
    return np.asarray(a.samples, np.float32), a.sample_rate

def ff(x, sr_in, af):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(sr_in), '-ac', '1', '-i', '-', '-af', af,
                        '-ar', str(SR), '-f', 'f32le', '-ac', '1', '-'], input=x.tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()

CHAIN = ('aresample=48000:resampler=soxr,highpass=f=70,'
         'equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.2:g=2,equalizer=f=9000:t=h:w=2000:g=1.5,'
         'deesser=i=0.4,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,'
         'aecho=0.8:0.6:22|41:0.10|0.06,alimiter=limit=0.89')

def trim(x, thr=.008):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx): return x
    return x[max(0, idx[0] - int(.02 * SR)):min(len(x), idx[-1] + int(.18 * SR))]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', default='pilot_bjk_hbs'); ap.add_argument('--models', default='/home/user/tts_models')
    ap.add_argument('--lead', type=float, default=.7); ap.add_argument('--gap', type=float, default=.30)
    ap.add_argument('--tail', type=float, default=2.4)
    a = ap.parse_args()
    out = ROOT / 'out' / a.ep; out.mkdir(parents=True, exist_ok=True)
    engines = {}
    pcm = [np.zeros(int(a.lead * SR), np.float32)]; tl = []; t = a.lead; prev = None
    for i, (spk, text) in enumerate(load_segs(a.ep)):
        name, ls, ns, nw = VOICE[spk]
        if name not in engines: engines[name] = tts(a.models, name)
        x, sr = synth(engines[name], norm(text), ls, ns, nw)
        y = trim(ff(x, sr, CHAIN))
        if prev is not None and prev != spk:            # konuşmacı değişiminde biraz daha uzun nefes
            extra = np.zeros(int(.18 * SR), np.float32); pcm.append(extra); t += .18
        d = len(y) / SR
        tl.append({'t0': round(t, 3), 't1': round(t + d, 3)})
        print(f'[{i}] {spk} {d:5.2f} sn  {text}')
        pcm += [y, np.zeros(int(a.gap * SR), np.float32)]; t += d + a.gap; prev = spk
    pcm.append(np.zeros(int(a.tail * SR), np.float32))
    v = np.concatenate(pcm); dur = len(v) / SR
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s24le',
                    str(out / 'voice.wav')], input=v.tobytes(), check=True)
    (ROOT / 'futbol' / 'data' / f'{a.ep}_tl.js').write_text(
        f'// tts_piper.py tarafından üretildi — elle düzenleme\nwindow.TL = {json.dumps(tl)};\nwindow.TL.dur = {dur:.3f};\n', encoding='utf-8')
    print(f'voice.wav {dur:.2f} sn · {len(tl)} segment · tepe {np.abs(v).max():.2f}')

if __name__ == '__main__':
    main()
