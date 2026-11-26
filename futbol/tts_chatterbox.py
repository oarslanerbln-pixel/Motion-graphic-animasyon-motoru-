#!/usr/bin/env python3
"""Doğal Türkçe TTS: Chatterbox Multilingual (Resemble AI, MIT lisans) → voice.wav + data/<ep>_tl.js

Çıktı biçimi tts_gemini.py / tts_piper.py ile aynıdır. CPU'da çalışır (yavaş ama yerel, anahtarsız).
Ses tınısı, kısa bir referans kayıttan (≈6–12 sn) alınır: --ref-A / --ref-T. Verilmezse modelin varsayılan sesi.
Referans kayıtların kullanım hakkı bizde olmalı (ör. CC0 Piper çıktısı ya da kendi kaydımız).

    /home/user/venv_cb/bin/python futbol/tts_chatterbox.py --ep pilot_bjk_hbs --ref-A refs/A.wav --ref-T refs/T.wav
    # tek satır deneme:  --only 0 --out-dir out/deneme
Gerekli ağ: huggingface.co (+ cdn-lfs / xethub) ilk indirmede.
"""
import argparse, json, re, subprocess, sys, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
STYLE = {'A': dict(exaggeration=.45, cfg_weight=.5, temperature=.7),    # sakin analist
         'T': dict(exaggeration=.65, cfg_weight=.4, temperature=.8)}    # canlı tribün

def load_segs(ep):
    js = (ROOT / 'futbol' / 'data' / f'{ep}.js').read_text(encoding='utf-8')
    block = js[js.index('segs:'):js.index('],', js.index('segs:'))]
    return [(m.group(1), m.group(2).replace("\\'", "'"))
            for m in re.finditer(r"spk:\s*'(\w)',\s*text:\s*'((?:[^'\\]|\\.)*)'", block)]

def norm(t):
    for a, b in {'Vlahović': 'Vlahoviç', 'Zlatanović': 'Zlatanoviç', 'Saint-Gilloise': 'Sen Jilvaz', 'Crystal Palace': 'Kristal Pelıs',
                 'Yehoshua': 'Yehoşua', 'Djalo': 'Calo', 'Agbadou': 'Agbadu', 'OFI': 'Ofi', 'Celtic': 'Seltik', 'Beer Sheva': 'Bir Şeva',
                 'Hoffenheim': 'Hofenhaym', 'Leverkusen': 'Leverkuzen', '≈': 'yaklaşık '}.items(): t = t.replace(a, b)
    return t

CHAIN = ('highpass=f=70,equalizer=f=3200:t=q:w=1.2:g=1.5,deesser=i=0.3,'
         'acompressor=threshold=-20dB:ratio=2:attack=10:release=150:makeup=1.5,alimiter=limit=0.89:level=disabled')

def to48(x, sr, af=CHAIN):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', '-af', f'aresample=48000:resampler=soxr,{af}',
                        '-f', 'f32le', '-ac', '1', '-'], input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()

def trim(x, thr=.01):
    idx = np.where(np.abs(x) > thr)[0]
    return x if not len(idx) else x[max(0, idx[0] - int(.03 * SR)):min(len(x), idx[-1] + int(.2 * SR))]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', default='pilot_bjk_hbs'); ap.add_argument('--ref-A'); ap.add_argument('--ref-T')
    ap.add_argument('--only', type=str, default=''); ap.add_argument('--out-dir', default='')
    ap.add_argument('--lead', type=float, default=.6); ap.add_argument('--gap', type=float, default=.26); ap.add_argument('--tail', type=float, default=2.0)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--tempo', type=float, default=1.0, help='perdeyi bozmadan hız (atempo), ör. 1.05')
    a = ap.parse_args()
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    torch.manual_seed(a.seed); torch.set_num_threads(4)
    t0 = time.time(); model = ChatterboxMultilingualTTS.from_pretrained(device='cpu'); print(f'model yüklendi {time.time() - t0:.0f} sn', flush=True)
    refs = {'A': a.ref_A, 'T': a.ref_T}
    segs = load_segs(a.ep); only = {int(i) for i in a.only.split(',')} if a.only else None
    out = Path(a.out_dir) if a.out_dir else ROOT / 'out' / a.ep; out.mkdir(parents=True, exist_ok=True)
    cache = out / 'cb_cache'; cache.mkdir(exist_ok=True)
    pcm = [np.zeros(int(a.lead * SR), np.float32)]; tl = []; t = a.lead; prev = None
    for i, (spk, text) in enumerate(segs):
        if only is not None and i not in only: continue
        cf = cache / f'seg{i:02d}_{spk}.npy'
        if cf.exists():
            y = np.load(cf)
        else:
            ts = time.time()
            kw = dict(language_id='tr', **STYLE[spk])
            if refs[spk]: kw['audio_prompt_path'] = refs[spk]
            wav = model.generate(norm(text), **kw)
            y = trim(to48(wav.squeeze(0).cpu().numpy(), model.sr)); np.save(cf, y)
            print(f'[{i}] {spk} {len(y) / SR:5.2f} sn ({time.time() - ts:.0f} sn işlem)  {text}', flush=True)
        if a.tempo != 1.0: y = to48(y, SR, f'atempo={a.tempo},alimiter=limit=0.89:level=disabled')
        if prev is not None and prev != spk: pcm.append(np.zeros(int(.12 * SR), np.float32)); t += .12
        d = len(y) / SR; tl.append({'t0': round(t, 3), 't1': round(t + d, 3)})
        pcm += [y, np.zeros(int(a.gap * SR), np.float32)]; t += d + a.gap; prev = spk
    pcm.append(np.zeros(int(a.tail * SR), np.float32))
    v = np.concatenate(pcm); dur = len(v) / SR
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s24le', str(out / 'voice.wav')],
                   input=v.tobytes(), check=True)
    if only is None:
        (ROOT / 'futbol' / 'data' / f'{a.ep}_tl.js').write_text(
            f'// tts_chatterbox.py tarafından üretildi — elle düzenleme\nwindow.TL = {json.dumps(tl)};\nwindow.TL.dur = {dur:.3f};\n', encoding='utf-8')
    print(f'voice.wav {dur:.2f} sn · {len(tl)} segment · tepe {np.abs(v).max():.2f} → {out}')

if __name__ == '__main__':
    main()
