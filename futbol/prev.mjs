// Önizleme: belirli zamanlarda kare + kontakt sayfası. Tam render'dan önce mutlaka çalıştır.
//   node futbol/prev.mjs --ep pilot_bjk_hbs --fmt v [--times 1,4.5,9] [--s 1]
//   --theme gece|neon|altin   --s 2 (süpersampling)
// --times yoksa her sahnenin %35 ve %80 noktası alınır.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { ROOT, FMT, serve, openEngine, args, chromium } from './lib.mjs';

const a = args({ ep: 'pilot_bjk_hbs', fmt: 'v', times: '', s: '1', theme: 'gece', js: 'taktik', clean: '', out: path.join(ROOT, 'out', 'prev') });
const [w, h] = FMT[a.fmt];
const key = `${a.ep}_${a.theme}_${a.fmt}`;
fs.mkdirSync(a.out, { recursive: true });
for (const f of fs.readdirSync(a.out)) if (f.startsWith(`${key}_`)) fs.unlinkSync(path.join(a.out, f));
const srv = await serve();
const browser = await chromium.launch();
const { pg, info, logs } = await openEngine(browser, srv.base, { ep: a.ep, w, h, s: a.s, theme: a.theme, js: a.js, clean: a.clean });
console.log(JSON.stringify(info));
if (info.fontsMissing.length) console.error('UYARI eksik font:', info.fontsMissing);
let ts = a.times ? a.times.split(',').map(Number) : info.scenes.flatMap(([, t0, t1]) => [t0 + (t1 - t0) * .35, t0 + (t1 - t0) * .8].map(x => +x.toFixed(2)));
for (const [i, t] of ts.entries()) {
  const b64 = await pg.evaluate(([t]) => window.ENGINE.frame(t, .9), [t]);
  fs.writeFileSync(path.join(a.out, `${key}_${String(i).padStart(2, '0')}_${t.toFixed(2)}.jpg`), Buffer.from(b64, 'base64'));
}
await browser.close(); srv.close();
if (logs.length) console.log(logs.join('\n'));
const cols = a.fmt === 'v' ? 4 : 3, rows = Math.ceil(ts.length / cols), sw = a.fmt === 'v' ? 360 : 640;
const sheet = path.join(a.out, `${key}_kontakt.jpg`);
execFileSync('ffmpeg', ['-v', 'error', '-y', '-pattern_type', 'glob', '-i', path.join(a.out, `${key}_[0-9][0-9]_*.jpg`),
  '-vf', `scale=${sw}:-1:flags=lanczos,tile=${cols}x${rows}:padding=6:color=0x222222`, '-frames:v', '1', '-q:v', '3', sheet]);
console.log('kontakt:', sheet);
