// Tam render: 1,5× süpersampling → lanczos küçültme → libx264. 2 paralel worker, kareler diske yazılmaz.
//   node futbol/render.mjs --ep pilot_bjk_hbs --fmt v [--s 1.5] [--workers 2] [--audio mix.wav] [--name kanal_bolum_stil]
// Her worker kendi parçasını encode eder, sonunda concat edilir (yeniden başlatmada yarım parçayı tekrar render et).
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { ROOT, FMT, serve, openEngine, args, chromium } from './lib.mjs';

const a = args({ ep: 'pilot_bjk_hbs', fmt: 'v', s: '1.5', workers: '2', audio: '', name: '', crf: '17', preset: 'medium' });
const [w, h] = FMT[a.fmt], fps = 30, N = +a.workers;
const outDir = path.join(ROOT, 'out'); fs.mkdirSync(outDir, { recursive: true });
const name = a.name || `${a.ep}_taktik_${a.fmt === 'v' ? '1080x1920' : '1920x1080'}`;
const srv = await serve();
const browser = await chromium.launch();
const t0 = Date.now();
const first = await openEngine(browser, srv.base, { ep: a.ep, w, h, s: a.s });
const total = Math.ceil(first.info.dur * fps);
console.log(`${name}: ${total} kare, ${first.info.dur.toFixed(2)} sn, ${N} worker`);

async function worker(k, eng) {
  const f0 = Math.floor(total * k / N), f1 = Math.floor(total * (k + 1) / N);
  const part = path.join(outDir, `${name}.part${k}.mp4`);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-vf', `scale=${w}:${h}:flags=lanczos,format=yuv420p`, '-c:v', 'libx264', '-preset', a.preset, '-crf', a.crf, '-tune', 'grain',
    '-r', String(fps), '-movflags', '+faststart', part], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()));
  for (let f = f0; f < f1; f++) {
    const b64 = await eng.pg.evaluate(([t]) => window.ENGINE.frame(t, .95), [f / fps]);
    if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (k === 0 && (f - f0) % 60 === 0) console.log(`  %${Math.round((f - f0) / (f1 - f0) * 100)}  ${((Date.now() - t0) / 1000).toFixed(0)} sn`);
  }
  ff.stdin.end(); await done;
  if (eng.logs.some(l => l.includes('pageerror'))) console.error(`worker ${k}:`, eng.logs.join('\n'));
  return part;
}
const engines = [first];
for (let k = 1; k < N; k++) engines.push(await openEngine(browser, srv.base, { ep: a.ep, w, h, s: a.s }));
const parts = await Promise.all(engines.map((e, k) => worker(k, e)));
await browser.close(); srv.close();
const list = path.join(outDir, `${name}.txt`);
fs.writeFileSync(list, parts.map(p => `file '${p}'`).join('\n'));
const silent = path.join(outDir, `${name}_muziksiz.mp4`);
const video = a.audio ? path.join(outDir, `${name}.video.mp4`) : silent;
execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', video]);
if (a.audio) execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', video, '-i', a.audio, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', path.join(outDir, `${name}.mp4`)]);
for (const p of [...parts, list]) fs.unlinkSync(p);
const sec = (Date.now() - t0) / 1000;
console.log(`bitti: ${a.audio ? path.join(outDir, name + '.mp4') : video}  (${sec.toFixed(0)} sn, ${(total / sec).toFixed(2)} kare/sn)`);
