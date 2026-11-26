// YouTube bölüm zaman damgaları: sahnelerin başlangıcından (chapter alanı olanlar + giriş)
//   node futbol/chapters.mjs --ep bjk_hbs_uzun
import { serve, openEngine, args, chromium } from './lib.mjs';
const a = args({ ep: 'bjk_hbs_uzun' });
const srv = await serve(); const b = await chromium.launch();
const { pg } = await openEngine(b, srv.base, { ep: a.ep, w: 640, h: 360, s: 0.5, theme: 'neon' });
const rows = await pg.evaluate(() => window.EP.scenes.map(s => [s.t0, s.chapter ? s.chapter.t : (s.type === 'intro' ? 'Giriş' : s.type === 'outro' ? 'Tahmin Ligi' : null)]));
await b.close(); srv.close();
const fmt = t => { t = Math.max(0, Math.floor(t)); return `${String(Math.floor(t / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`; };
const tr = s => s.toLocaleLowerCase('tr-TR').replace(/(^|\s)\S/g, m => m.toLocaleUpperCase('tr-TR'));
for (const [t, n] of rows) if (n) console.log(`${fmt(t)} ${tr(n)}`);
