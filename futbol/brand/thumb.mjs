// node futbol/brand/thumb.mjs --img out/x.jpg --l1 "PLAN NET" --l2 "BATUM'DA" --l3 "BEŞİKTAŞ × HAPOEL BEER SHEVA" --out out/thumb.jpg
import fs from 'node:fs'; import path from 'node:path';
import { ROOT, serve, args, chromium } from '../lib.mjs';
const a = args({ img: '', l1: '', l2: '', l3: '', acc: '#C9A2FF', out: path.join(ROOT, 'out', 'thumb.jpg') });
const rel = path.relative(ROOT, path.resolve(a.img));
const srv = await serve(); const b = await chromium.launch(); const pg = await b.newPage();
const q = new URLSearchParams({ img: '/' + rel, l1: a.l1, l2: a.l2, l3: a.l3, acc: a.acc });
await pg.goto(`${srv.base}/futbol/brand/thumb.html?${q}`); await pg.waitForFunction('window.DONE', null, { timeout: 20000 });
fs.writeFileSync(a.out, Buffer.from((await pg.evaluate('window.DONE')).split(',')[1], 'base64')); console.log(a.out);
await b.close(); srv.close();
