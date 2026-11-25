// Ortak: proje kökünü yerel HTTP ile sun + motoru Chromium'da aç.
// (file:// altında fontlar CORS yüzünden yüklenmeyebilir.)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const FMT = { v: [1080, 1920], h: [1920, 1080] };
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.woff2': 'font/woff2', '.json': 'application/json' };

export function serve() {
  return new Promise(res => {
    const srv = http.createServer((q, r) => {
      const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
      r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(r);
    }).listen(0, '127.0.0.1', () => res({ base: `http://127.0.0.1:${srv.address().port}`, close: () => srv.close() }));
  });
}

export async function openEngine(browser, base, { ep, w, h, s }) {
  const pg = await browser.newPage({ viewport: { width: w, height: h } });
  const logs = [];
  pg.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
  pg.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
  pg.on('requestfailed', r => logs.push(`[requestfailed] ${r.url()}`));
  await pg.goto(`${base}/futbol/engine.html?ep=${ep}&w=${w}&h=${h}&s=${s}`);
  try { await pg.waitForFunction('window.ENGINE && window.ENGINE.ready', null, { timeout: 20000 }); }
  catch (e) { console.error(logs.join('\n')); throw e; }
  const info = await pg.evaluate('window.ENGINE.ready');
  return { pg, info, logs };
}

export function args(def) {
  const o = { ...def };
  for (let i = 2; i < process.argv.length; i += 2) o[process.argv[i].replace(/^--/, '')] = process.argv[i + 1];
  return o;
}
export { chromium };
