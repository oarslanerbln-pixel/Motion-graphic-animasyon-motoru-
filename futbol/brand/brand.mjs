// node futbol/brand/brand.mjs --name "TAKTİK GECE" --mono TG --tag "..." --slug taktikgece
import fs from 'node:fs'; import path from 'node:path';
import { ROOT, serve, args, chromium } from '../lib.mjs';
const a = args({ name: 'TAKTİK GECE', mono: 'TG', tag: 'AVRUPA GECELERİ · MİLLİ TAKIM · MAÇ ÖNCESİ TAKTİK', slug: 'taktikgece', kinds: 'icon,watermark,banner' });
const out = path.join(ROOT, 'out', 'brand'); fs.mkdirSync(out, { recursive: true });
const srv = await serve(); const b = await chromium.launch(); const pg = await b.newPage();
for (const kind of a.kinds.split(',')) {
  await pg.goto(`${srv.base}/futbol/brand/brand.html?kind=${kind}&name=${encodeURIComponent(a.name)}&mono=${encodeURIComponent(a.mono)}&tag=${encodeURIComponent(a.tag)}`);
  await pg.waitForFunction('window.DONE', null, { timeout: 15000 });
  const d = await pg.evaluate('window.DONE');
  const f = path.join(out, `${a.slug}_${kind}.png`); fs.writeFileSync(f, Buffer.from(d.split(',')[1], 'base64')); console.log(f);
}
await b.close(); srv.close();
