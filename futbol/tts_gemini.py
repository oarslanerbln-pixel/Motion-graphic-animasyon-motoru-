#!/usr/bin/env python3
"""Gemini TTS → voice.wav + gerçek segment zamanları (data/<ep>_tl.js).

Her replik ayrı sentezlenir; böylece segment başı/sonu kesin bilinir (ASR hizalamaya gerek kalmaz).
Ses kişiliği için iki persona: ANALİST (sakin, veri) ve TRİBÜN (enerjik, taraftar).

    export GEMINI_API_KEY=...          # Google AI Studio anahtarı
    python3 futbol/tts_gemini.py --ep pilot_bjk_hbs [--model gemini-2.5-pro-preview-tts]

Gereken ağ erişimi: generativelanguage.googleapis.com
Çıktı PCM 24 kHz mono 16-bit; segmentler arasına --gap sn sessizlik eklenir.
"""
import argparse, base64, json, os, re, struct, sys, time, urllib.request, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SR = 24000

# Persona → ses + üslup yönergesi (doğal dilde stil kontrolü)
PERSONA = {
    'A': ('Charon', 'Türkçe konuşan, sakin, net ve güven veren bir futbol analisti gibi oku. '
                    'Tempo orta, vurgular sayılarda ve taktik terimlerde. İstanbul Türkçesi.'),
    'T': ('Puck',   'Türkçe konuşan, enerjik, esprili ve heyecanlı bir genç taraftar sunucu gibi oku. '
                    'Tempo canlı, gülümseyerek, ama bağırmadan. İstanbul Türkçesi.'),
}

def load_segs(ep):
    js = (ROOT / 'futbol' / 'data' / f'{ep}.js').read_text(encoding='utf-8')
    block = js[js.index('segs:'):js.index('],', js.index('segs:'))]
    return [(m.group(1), m.group(2).replace("\\'", "'"))
            for m in re.finditer(r"spk:\s*'(\w)',\s*text:\s*'((?:[^'\\]|\\.)*)'", block)]

def synth(text, spk, model, key, retries=4):
    voice, style = PERSONA[spk]
    body = {
        'contents': [{'parts': [{'text': f'{style}\n\nMetin: {text}'}]}],
        'generationConfig': {'responseModalities': ['AUDIO'],
                             'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}}},
    }
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    req = urllib.request.Request(url, json.dumps(body).encode(), {'Content-Type': 'application/json', 'x-goog-api-key': key})
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            return base64.b64decode(d['candidates'][0]['content']['parts'][0]['inlineData']['data'])
        except Exception as e:
            print(f'  deneme {i + 1}: {e}', file=sys.stderr); time.sleep(2 ** i)
    raise SystemExit('TTS başarısız')

def trim(pcm, thr=350):
    """Baş/sondaki sessizliği kırp (16-bit LE)."""
    n = len(pcm) // 2; s = struct.unpack(f'<{n}h', pcm)
    a = next((i for i in range(n) if abs(s[i]) > thr), 0)
    b = next((i for i in range(n - 1, -1, -1) if abs(s[i]) > thr), n - 1)
    a = max(0, a - int(.03 * SR)); b = min(n, b + int(.06 * SR))
    return pcm[a * 2:b * 2]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ep', default='pilot_bjk_hbs')
    ap.add_argument('--model', default='gemini-2.5-pro-preview-tts')
    ap.add_argument('--lead', type=float, default=.7)
    ap.add_argument('--gap', type=float, default=.32)
    ap.add_argument('--tail', type=float, default=2.2)
    a = ap.parse_args()
    key = os.environ.get('GEMINI_API_KEY') or sys.exit('GEMINI_API_KEY yok')
    out = ROOT / 'out' / a.ep; out.mkdir(parents=True, exist_ok=True)
    segs = load_segs(a.ep)
    pcm, tl, t = bytearray(b'\0\0' * int(a.lead * SR)), [], a.lead
    for i, (spk, text) in enumerate(segs):
        cache = out / f'seg{i:02d}_{spk}.pcm'
        if not cache.exists():
            print(f'[{i}] {spk}: {text}')
            cache.write_bytes(trim(synth(text, spk, a.model, key)))
        seg = cache.read_bytes(); d = len(seg) / 2 / SR
        tl.append({'t0': round(t, 3), 't1': round(t + d, 3)})
        pcm += seg; t += d
        pcm += b'\0\0' * int(a.gap * SR); t += a.gap
    pcm += b'\0\0' * int(a.tail * SR)
    dur = len(pcm) / 2 / SR
    with wave.open(str(out / 'voice.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(pcm))
    (ROOT / 'futbol' / 'data' / f'{a.ep}_tl.js').write_text(
        f'// tts_gemini.py tarafından üretildi — elle düzenleme\nwindow.TL = {json.dumps(tl)};\nwindow.TL.dur = {dur:.3f};\n', encoding='utf-8')
    print(f'voice.wav {dur:.2f} sn · {len(tl)} segment → data/{a.ep}_tl.js')

if __name__ == '__main__':
    main()
