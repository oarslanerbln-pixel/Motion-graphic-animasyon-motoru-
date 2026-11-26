// Deterministic frame renderer: pauses all CSS animations and seeks them per frame.
// usage: node render.js page.html W H scale fps dur out.mp4 [workers] [outW outH]
//        node render.js page.html W H scale --stills t1,t2,... outprefix
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path'); const fs = require('fs');
const [,, file, W, H, SCALE, a5, a6, a7, a8, a9, a10] = process.argv;
const w = +W, h = +H, sc = +SCALE;
async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: sc });
  await page.goto('file://' + path.resolve(file));
  await page.evaluate(async () => { await document.fonts.ready; });
  await page.waitForTimeout(300);
  await page.evaluate(() => { window.__a = document.getAnimations(); window.__a.forEach(a => a.pause()); });
  return page;
}
async function seek(page, t) {
  await page.evaluate((ms) => { for (const a of window.__a) a.currentTime = ms; }, t * 1000);
  await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
}
(async () => {
  const browser = await chromium.launch();
  if (a5 === '--stills') {
    const page = await openPage(browser);
    for (const t of a6.split(',').map(Number)) {
      await seek(page, t);
      await page.screenshot({ path: `${a7}_${t.toFixed(2)}.jpg`, type: 'jpeg', quality: 90 });
    }
    await browser.close(); return;
  }
  const fps = +a5, dur = +a6, out = a7, workers = +(a8 || 2);
  const ow = +(a9 || w * sc / 1.5), oh = +(a10 || h * sc / 1.5);
  const total = Math.round(fps * dur), per = Math.ceil(total / workers);
  const parts = [];
  const t0 = Date.now();
  await Promise.all([...Array(workers).keys()].map(async (k) => {
    const s = k * per, e = Math.min(total, s + per); if (s >= e) return;
    const seg = `${out}.part${k}.mp4`; parts[k] = seg;
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
      '-vf', `scale=${ow}:${oh}:flags=lanczos`, '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-tune', 'grain',
      '-pix_fmt', 'yuv420p', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
    const page = await openPage(browser);
    for (let f = s; f < e; f++) {
      await seek(page, f / fps);
      const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - s) % 30 === 0) console.log(`w${k} frame ${f}/${e}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }));
  await browser.close();
  const list = out + '.txt';
  fs.writeFileSync(list, parts.filter(Boolean).map(p => `file '${path.resolve(p)}'`).join('\n'));
  await new Promise(r => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', out], { stdio: 'inherit' }).on('close', r));
  parts.filter(Boolean).forEach(p => fs.unlinkSync(p)); fs.unlinkSync(list);
  console.log('done', out, ((Date.now() - t0) / 1000).toFixed(0) + 's');
})();
