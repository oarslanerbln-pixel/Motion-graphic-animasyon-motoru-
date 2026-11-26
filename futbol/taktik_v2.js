// 09 — Taktik Tahta (Gece Maçı) · deterministik render(T) motoru
// Görsel dil: gece stadı, projektör hüzmeleri ve toz, perspektifli cam saha,
// ışıklı oyuncu jetonları, pas izleri, pres ısı bölgeleri, kinetik tipografi, karaoke altyazı.
(() => {
'use strict';
const Q = new URLSearchParams(location.search);
const W = +Q.get('w') || 1920, H = +Q.get('h') || 1080, S = +(Q.get('s') || 1);
const V = H > W;                          // dikey mi
const CLEAN = Q.get('clean') === '1';     // küçük resim için: altyazı, marka ve başlık yok
const U = Math.min(W, H) / 1080;          // ölçek birimi
const EP = window.EP;

// ---------- temalar (?theme=gece|neon|altin) ----------
const THEMES = {
  gece: { name: 'Gece Mavisi', bg: ['#14243F', '#070C18', '#010205'], beam: ['205,226,255', '205,226,255'], beamI: 1, flare: '150,190,255',
    dust: '225,235,255', crowd: '255,214,170', acc: '#F4C653', acc2: '#7FE3FF', txt: '#E8EEF5', mut: '#B9C7D6', mut2: '#8EA3B8',
    grass: ['rgba(20,62,47,.94)', 'rgba(15,51,39,.94)'], line: '214,255,236', pool: '160,255,210', slab: ['#0C2A20', '#020806'],
    rim: '#BFE4FF', grid: 0, gloss: 1, refl: .22, bloom: .55, vig: .62, grade: ['rgba(40,90,160,.10)', 'soft-light'] },
  neon: { name: 'Lila (minimal)', min: true, bg: ['#1E1036', '#0B0618', '#030107'], beam: ['196,170,255', '196,170,255'], beamI: .85, flare: '200,175,255',
    dust: '220,205,255', crowd: '170,140,255', acc: '#C9A2FF', acc2: '#7FE0F0', txt: '#F1EBFF', mut: '#C5B8E2', mut2: '#8F84AE',
    grass: ['rgba(24,15,48,.95)', 'rgba(20,12,41,.95)'], line: '226,214,255', pool: '150,110,255', slab: ['#24154A', '#05030C'],
    rim: '#D9C2FF', grid: .035, gloss: .9, refl: .25, bloom: .32, vig: .7, grade: ['rgba(120,80,255,.06)', 'soft-light'] },
  altin: { name: 'Altın Sinema', bg: ['#2E1D0E', '#120A05', '#030201'], beam: ['255,196,120', '255,210,150'], beamI: 1.1, flare: '255,165,80',
    dust: '255,225,180', crowd: '255,190,120', acc: '#FFB547', acc2: '#5FE3CB', txt: '#F6EBDD', mut: '#D9C7AF', mut2: '#A8937A',
    grass: ['rgba(24,60,36,.94)', 'rgba(19,50,29,.94)'], line: '255,238,205', pool: '255,200,120', slab: ['#1E2A14', '#050602'],
    rim: '#FFD08A', grid: 0, gloss: .9, refl: .18, bloom: .6, vig: .7, grade: ['rgba(255,140,40,.10)', 'soft-light'] },
};
const TH = THEMES[Q.get('theme')] || THEMES.gece;
EP.spk.A.col = TH.acc2; EP.spk.T.col = TH.acc;
let NOW = 0;
const cv = document.getElementById('c');
cv.width = Math.round(W * S); cv.height = Math.round(H * S);
cv.style.width = W + 'px'; cv.style.height = H + 'px';
const g = cv.getContext('2d');

// ---------- yardımcılar ----------
const cl = (x, a = 0, b = 1) => x < a ? a : x > b ? b : x;
const lerp = (a, b, t) => a + (b - a) * t;
const win = (T, a, b) => cl((T - a) / (b - a));
const eOut = t => 1 - Math.pow(1 - t, 3);
const eIO = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const eExpo = t => t >= 1 ? 1 : 1 - Math.pow(2, -10 * t);
const eBack = t => { const c = 1.70158, c3 = c + 1; return 1 + c3 * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
function rng(seed) { let s = seed >>> 0; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; }
const F = (w, px, fam = 'Manrope') => `${w} ${Math.round(px)}px '${fam}'`;
const lowTR = s => s.toLocaleLowerCase('tr-TR');
function rrect(x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }

// ---------- fontlar (yerel @fontsource, latin + latin-ext) ----------
const LAT = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD';
const LEX = 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF';
const FONTS = [['Unbounded', 'unbounded', [300, 500, 700, 800]], ['Manrope', 'manrope', [500, 700, 800]], ['JetBrains Mono', 'jetbrains-mono', [500, 700]]];
let css = '';
for (const [fam, dir, ws] of FONTS) for (const w of ws) for (const [sub, r] of [['latin', LAT], ['latin-ext', LEX]])
  css += `@font-face{font-family:'${fam}';font-weight:${w};font-display:block;src:url(../fonts/fontsource-${dir}/files/${dir}-${sub}-${w}-normal.woff2) format('woff2');unicode-range:${r}}\n`;
const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
const TRS = 'İıŞşĞğÂâÖöÜüÇç';
const fontsReady = Promise.all(FONTS.flatMap(([fam, , ws]) => ws.map(w => document.fonts.load(`${w} 40px '${fam}'`, TRS))));

// ---------- zaman çizelgesi: hece oranlı kelime zamanları ----------
const VOW = /[aeıioöuüâîûAEIİOÖUÜÂÎÛ]/g;
const syl = w => Math.max(1, (w.match(VOW) || []).length);
function buildTimeline() {
  const TL = window.TL;   // TTS sonrası: [{t0,t1}, ...]
  let t = EP.lead || .6;
  EP.segs.forEach((s, i) => {
    s.words = s.text.split(/\s+/).filter(Boolean);
    if (TL && TL[i]) { s.t0 = TL[i].t0; s.t1 = TL[i].t1; }
    else { s.t0 = t; s.t1 = t + s.words.reduce((a, w) => a + syl(w), 0) / (EP.rate || 5.5); }
    t = s.t1 + (EP.gap || .3);
    const wts = s.words.map(w => syl(w) + (/[.?!…]["'’]?$/.test(w) ? .75 : /[,;:]$/.test(w) ? .55 : 0));
    const tot = wts.reduce((a, b) => a + b, 0); let acc = s.t0;
    s.wt = wts.map(x => { const a = acc; acc += x / tot * (s.t1 - s.t0); return [a, acc]; });
  });
  const last = EP.segs[EP.segs.length - 1];
  EP.dur = (window.TL && window.TL.dur) || last.t1 + (EP.tail || 2);
  EP.scenes.forEach((sc, i) => {
    sc.t0 = i === 0 ? 0 : EP.segs[sc.seg[0]].t0 - .35;
    sc.t1 = i === EP.scenes.length - 1 ? EP.dur : EP.segs[EP.scenes[i + 1].seg[0]].t0 - .35;
  });
}
// segment si içinde key ile başlayan ilk kelimenin başlangıç zamanı
function wT(si, key) {
  const s = EP.segs[si]; const k = lowTR(key);
  const i = s.words.findIndex(w => lowTR(w).replace(/[^a-zçğıöşüâîû0-9]/g, '').startsWith(k));
  return i < 0 ? s.t0 : s.wt[i][0];
}

// ---------- tane (grain) ----------
const grain = document.createElement('canvas'); grain.width = grain.height = 256;
{ const gx = grain.getContext('2d'), id = gx.createImageData(256, 256), r = rng(7);
  for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (r() - .5) * 255 * .9; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
  gx.putImageData(id, 0, 0); }

// ---------- arka plan: stadyum + projektörler + lens parlaması + toz ----------
const DUST = (() => { const r = rng(11), a = []; for (let i = 0; i < 700; i++) a.push({ x: r(), y: r(), z: .3 + r() * .7, ph: r() * 6.28, sp: .004 + r() * .012 }); return a; })();
const SRC = () => [[-.06 * W, -.10 * H, 1, TH.beam[0]], [1.06 * W, -.10 * H, -1, TH.beam[1]]];
function beams(T, inten) {
  const L = Math.hypot(W, H) * 1.5;
  g.save(); g.globalCompositeOperation = 'lighter';
  const axes = [];
  for (const [sx, sy, sd, col] of SRC()) {
    const base = Math.atan2(H * .62 - sy, W * .5 - sx);
    const ang = base + Math.sin(T * .23 + sd) * .035;
    axes.push([sx, sy, ang, col]);
    for (const [hw, al] of [[.22, .035], [.13, .055], [.065, .08], [.025, .10]]) {
      const a1 = ang - hw, a2 = ang + hw;
      const gr = g.createLinearGradient(sx, sy, sx + Math.cos(ang) * L * .72, sy + Math.sin(ang) * L * .72);
      gr.addColorStop(0, `rgba(${col},${al * inten * TH.beamI})`); gr.addColorStop(.6, `rgba(${col},${al * .35 * inten * TH.beamI})`); gr.addColorStop(1, `rgba(${col},0)`);
      g.fillStyle = gr; g.beginPath(); g.moveTo(sx, sy);
      g.lineTo(sx + Math.cos(a1) * L, sy + Math.sin(a1) * L); g.lineTo(sx + Math.cos(a2) * L, sy + Math.sin(a2) * L); g.closePath(); g.fill();
    }
    // görünür lamba noktası + anamorfik çizgi + hayalet halkalar
    const fx = sx + sd * W * .075, fy = sy + H * .115;
    let rg = g.createRadialGradient(fx, fy, 0, fx, fy, 220 * U);
    rg.addColorStop(0, `rgba(255,255,255,${.9 * inten})`); rg.addColorStop(.08, `rgba(${col},${.55 * inten})`); rg.addColorStop(1, `rgba(${col},0)`);
    g.fillStyle = rg; g.beginPath(); g.arc(fx, fy, 220 * U, 0, 6.283); g.fill();
    g.save(); g.translate(fx, fy); g.scale(1, .018);
    rg = g.createRadialGradient(0, 0, 0, 0, 0, W * .7);
    rg.addColorStop(0, `rgba(${TH.flare},${(TH.min ? .22 : .55) * inten})`); rg.addColorStop(1, `rgba(${TH.flare},0)`);
    g.fillStyle = rg; g.beginPath(); g.arc(0, 0, W * .7, 0, 6.283); g.fill(); g.restore();
    const vx = W / 2 - fx, vy = H / 2 - fy;
    if (!TH.min) [[.32, 60, .028], [.62, 150, .016]].forEach(([t, r, al]) => {
      const gx = fx + vx * t + Math.sin(T * .23 + sd) * 30 * U, gy = fy + vy * t;
      const gg = g.createRadialGradient(gx, gy, 0, gx, gy, r * U);
      gg.addColorStop(0, `rgba(${TH.flare},${al * inten})`); gg.addColorStop(.7, `rgba(${TH.flare},${al * .6 * inten})`); gg.addColorStop(1, `rgba(${TH.flare},0)`);
      g.fillStyle = gg; g.beginPath(); g.arc(gx, gy, r * U, 0, 6.283); g.fill();
    });
  }
  for (let di = 0; di < DUST.length; di += TH.min ? 6 : 1) {
    const d = DUST[di];
    const x = ((d.x + Math.sin(T * .1 + d.ph) * .01) % 1) * W;
    const y = (((d.y - T * d.sp) % 1) + 1) % 1 * H;
    let lit = 0, col = TH.dust;
    for (const [sx, sy, ang, c] of axes) { const a = Math.atan2(y - sy, x - sx), l = cl(1 - Math.abs(a - ang) / .17); if (l > lit) { lit = l; col = c; } }
    if (lit <= 0) continue;
    g.fillStyle = `rgba(${col},${.45 * lit * d.z * inten})`;
    g.beginPath(); g.arc(x, y, (.8 + d.z * 1.5) * U, 0, 6.283); g.fill();
  }
  g.restore();
}
function bg(T) {
  const gr = g.createRadialGradient(W * .5, H * .42, 0, W * .5, H * .5, Math.hypot(W, H) * .65);
  gr.addColorStop(0, TH.bg[0]); gr.addColorStop(.55, TH.bg[1]); gr.addColorStop(1, TH.bg[2]);
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  // uzak tribün: katmanlı ışık bandı + titreşen flaşlar
  const r = rng(3); g.save(); g.globalCompositeOperation = 'lighter';
  const band = g.createLinearGradient(0, H * .12, 0, H * .3);
  band.addColorStop(0, 'rgba(0,0,0,0)'); band.addColorStop(.5, `rgba(${TH.crowd},.05)`); band.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = band; g.fillRect(0, H * .12, W, H * .18);
  for (let i = 0; i < (TH.min ? 0 : 140); i++) {
    const x = r() * W, y = H * (.15 + r() * .12), tw = .5 + .5 * Math.sin(T * (1 + r() * 2) + i), sz = (1.5 + r() * 4) * U;
    g.fillStyle = `rgba(${TH.crowd},${.05 + .08 * tw})`;
    g.beginPath(); g.arc(x, y, sz, 0, 6.283); g.fill();
  }
  g.restore();
}
function vignette() {
  const gr = g.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .35, W / 2, H / 2, Math.hypot(W, H) * .62);
  gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, `rgba(0,0,0,${TH.vig})`);
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
}


// ---------- partiküller: bokeh diskleri + saha üstü 3D ışık zerreleri ----------
const BOKEH = (() => { const r = rng(21), a = []; for (let i = 0; i < 38; i++) a.push({ x: r(), y: r(), r: 40 + r() * 150, ph: r() * 6.28, sp: .4 + r(), c: i % 2, fg: i < 7 }); return a; })();
function bokeh(T, front, k = 1) {
  if (TH.min) return;
  g.save(); g.globalCompositeOperation = 'lighter';
  for (const b of BOKEH) {
    if (b.fg !== front) continue;
    const x = (b.x + Math.sin(T * .05 * b.sp + b.ph) * .04) * W, y = ((((b.y - T * .006 * b.sp) % 1) + 1) % 1) * H * 1.2 - H * .1;
    const r = b.r * U * (front ? 1.8 : 1), col = TH.beam[b.c], al = (front ? .035 : .06) * k * (.7 + .3 * Math.sin(T * .6 + b.ph));
    const rg = g.createRadialGradient(x, y, 0, x, y, r);
    rg.addColorStop(0, `rgba(${col},${al * .5})`); rg.addColorStop(.82, `rgba(${col},${al * .8})`); rg.addColorStop(.93, `rgba(${col},${al * 1.15})`); rg.addColorStop(1, `rgba(${col},0)`);
    g.fillStyle = rg; g.beginPath(); g.arc(x, y, r, 0, 6.283); g.fill();
  }
  g.restore();
}
const MOTES = (() => { const r = rng(33), a = []; for (let i = 0; i < 420; i++) a.push({ X: (r() - .5) * 112, Y: (r() - .5) * 76, z: r(), sp: .25 + r() * .75, ph: r() * 6.28, c: r() < .5 ? 0 : 1, s: .6 + r() * 1.4 }); return a; })();
function motes(T, a) {
  if (a <= 0 || TH.min) return;
  g.save(); g.globalCompositeOperation = 'lighter';
  const cols = [TH.acc, TH.acc2], hs = Math.sin(CAM.tilt);
  for (const m of MOTES) {
    const h = ((m.z + T * .035 * m.sp) % 1);               // 0→1 yükselip başa döner
    const zM = h * 14;                                       // metre cinsinden yükseklik
    const X = m.X + Math.sin(T * .3 * m.sp + m.ph) * 1.2, Y = m.Y + Math.cos(T * .25 * m.sp + m.ph) * 1.2;
    const [x, y, sc] = proj(X, Y); const yy = y - zM * CAM.k * sc * hs;
    const tw = .55 + .45 * Math.sin(T * 3 * m.sp + m.ph * 3), fade = Math.sin(h * Math.PI);
    const al = a * fade * tw * .5, rad = m.s * U * sc * 1.6;
    if (al < .02) continue;
    g.fillStyle = hexA(cols[m.c], al * .25); g.beginPath(); g.arc(x, yy, rad * 3.2, 0, 6.283); g.fill();
    g.fillStyle = hexA(cols[m.c], al); g.beginPath(); g.arc(x, yy, rad, 0, 6.283); g.fill();
  }
  g.restore();
}

// ---------- tipografi ----------
// Maskeyle alttan kayarak açılan metin
function maskText(txt, x, y, font, col, p, align = 'center', ls = 0) {
  if (p <= 0) return;
  g.save(); g.font = font; g.letterSpacing = ls + 'px'; g.textAlign = align; g.textBaseline = 'alphabetic';
  const m = g.measureText(txt), asc = m.actualBoundingBoxAscent * 1.25, dsc = m.actualBoundingBoxDescent + 6 * U;
  const w = m.width, x0 = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
  g.beginPath(); g.rect(x0 - 40 * U, y - asc, w + 80 * U, asc + dsc); g.clip();
  const e = eExpo(p);
  g.fillStyle = col; g.globalAlpha *= cl(p * 3);
  g.fillText(txt, x, y + (1 - e) * asc * 1.1);
  g.restore();
}
function glass(x, y, w, h, r, a = 1, tint = '#FFFFFF') {
  g.save(); g.globalAlpha *= a;
  rrect(x, y, w, h, r);
  const gr = g.createLinearGradient(x, y, x, y + h);
  gr.addColorStop(0, hexA(tint, .11)); gr.addColorStop(1, hexA(tint, .035));
  g.fillStyle = gr; g.fill();
  g.lineWidth = 1.2 * U; g.strokeStyle = 'rgba(255,255,255,.16)'; g.stroke();
  // üst kenar parlaklığı
  rrect(x + 1, y + 1, w - 2, h * .5, r); g.clip();
  const hl = g.createLinearGradient(x, y, x, y + h * .5);
  hl.addColorStop(0, 'rgba(255,255,255,.08)'); hl.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = hl; g.fillRect(x, y, w, h * .5);
  g.restore();
}
function brandBug(T, a) {
  // KIRK SEKİZ yazı logosu: SEKİZ'deki İ'nin noktası altın top (seçilen kimlik: "İ Noktası")
  g.save(); g.globalAlpha = a;
  const fs = (V ? 30 : 24) * U, ls = fs * .14, y = V ? 130 * U : 70 * U;
  g.font = F(800, fs); g.letterSpacing = ls + 'px'; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  const b = EP.brand || '', k = b.lastIndexOf('İ'), pre = k >= 0 ? b.slice(0, k) : b, post = k >= 0 ? b.slice(k + 1) : '';
  const wPre = g.measureText(pre).width, wI = k >= 0 ? g.measureText('I').width : 0, wPost = g.measureText(post).width;
  const tw = wPre + wI + wPost - ls, x0 = V ? W / 2 - tw / 2 : 64 * U;
  g.fillStyle = '#F2F4F7'; g.fillText(pre, x0, y);
  if (k >= 0) {
    g.fillText('I', x0 + wPre, y); g.fillText(post, x0 + wPre + wI, y);
    const cx = x0 + wPre + (wI - ls) / 2 - fs * .04, r = fs * .13 * (1 + .06 * Math.sin(T * 2.4));
    g.fillStyle = '#D4AF5A'; g.beginPath(); g.arc(cx, y - fs * .92, r, 0, 6.283); g.fill();
  }
  g.restore();
}

// ---------- saha projeksiyonu ----------
// Dünya: X ∈ [-52.5, 52.5] (boy), Y ∈ [-34, 34] (en), metre.
const CAM = { tilt: .9, yaw: 0, k: 1, cx: W / 2, cy: H / 2, d: 1400, fx: 0, fy: 0, zm: 1 };
function proj(X, Y) {
  const X0 = X - CAM.fx, Y0 = Y - CAM.fy;            // kamera odağı
  let x = V ? Y0 : X0, y = V ? -X0 : Y0;             // dikeyde hücum yukarı
  const c = Math.cos(CAM.yaw), s = Math.sin(CAM.yaw);
  const xr = x * c - y * s, yr = x * s + y * c;
  const px = xr * CAM.k, py = yr * CAM.k;
  const z = -py * Math.sin(CAM.tilt);               // ekranda yukarısı uzak
  const sc = CAM.d / Math.max(CAM.d * .3, CAM.d + z);
  return [CAM.cx + px * sc, CAM.cy + py * Math.cos(CAM.tilt) * sc, sc];
}
const P = (x, y) => [(x - .5) * 105, (y - .5) * 68];   // normalize → metre
function polyW(pts, close) {
  g.beginPath(); pts.forEach(([X, Y], i) => { const [x, y] = proj(X, Y); i ? g.lineTo(x, y) : g.moveTo(x, y); }); if (close) g.closePath();
}
function arcW(cx, cy, r, a0, a1, n = 48) { const pts = []; for (let i = 0; i <= n; i++) { const a = lerp(a0, a1, i / n); pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } return pts; }
function segLine(X0, Y0, X1, Y1, n = 12) { const a = []; for (let i = 0; i <= n; i++) a.push([lerp(X0, X1, i / n), lerp(Y0, Y1, i / n)]); return a; }
function pitchLines() {
  const L = [];
  L.push([[-52.5, -34], [52.5, -34], [52.5, 34], [-52.5, 34], [-52.5, -34]]);
  L.push(segLine(0, -34, 0, 34));
  L.push(arcW(0, 0, 9.15, 0, 6.2832, 72));
  for (const sd of [-1, 1]) {
    const gx = 52.5 * sd;
    L.push([[gx, -20.16], [gx - 16.5 * sd, -20.16], [gx - 16.5 * sd, 20.16], [gx, 20.16]]);
    L.push([[gx, -9.16], [gx - 5.5 * sd, -9.16], [gx - 5.5 * sd, 9.16], [gx, 9.16]]);
    const a = Math.acos(5.5 / 9.15);
    L.push(sd > 0 ? arcW(gx - 11 * sd, 0, 9.15, Math.PI - a, Math.PI + a, 24) : arcW(gx - 11 * sd, 0, 9.15, -a, a, 24));
    L.push([[gx, -3.66], [gx + 2 * sd, -3.66], [gx + 2 * sd, 3.66], [gx, 3.66]]);   // kale
  }
  return L.map(l => l.length < 6 ? densify(l) : l);
}
function densify(l) { const o = []; for (let i = 0; i < l.length - 1; i++) { const s = segLine(l[i][0], l[i][1], l[i + 1][0], l[i + 1][1], 10); o.push(...(i ? s.slice(1) : s)); } return o; }
const PL = pitchLines();
const CORN = [[-52.5, -34], [52.5, -34], [52.5, 34], [-52.5, 34]];
function drawPitch(a, draw) {
  g.save(); g.globalAlpha = a;
  const pc = CORN.map(([X, Y]) => proj(X, Y));
  // altta yumuşak gölge + zemin ışıması
  const [cx0, cy0] = proj(0, 0);
  let rg = g.createRadialGradient(cx0, cy0 + 60 * U, 0, cx0, cy0 + 60 * U, Math.max(W, H) * .5);
  rg.addColorStop(0, `rgba(${TH.pool},.10)`); rg.addColorStop(1, `rgba(${TH.pool},0)`);
  g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = rg; g.fillRect(0, 0, W, H); g.restore();
  // 3D kalınlık: kenar yüzeyleri (arka kenarlar üst yüzeyin altında kalır)
  const th = 16 * U;
  for (let i = 0; i < 4; i++) {
    const p0 = pc[i], p1 = pc[(i + 1) % 4], d0 = th * p0[2], d1 = th * p1[2];
    const sg = g.createLinearGradient(0, Math.min(p0[1], p1[1]), 0, Math.max(p0[1], p1[1]) + d1);
    sg.addColorStop(0, TH.slab[0]); sg.addColorStop(1, TH.slab[1]);
    g.fillStyle = sg; g.beginPath(); g.moveTo(p0[0], p0[1]); g.lineTo(p1[0], p1[1]); g.lineTo(p1[0], p1[1] + d1); g.lineTo(p0[0], p0[1] + d0); g.closePath(); g.fill();
  }
  // üst yüzey: biçme şeritleri
  for (let i = 0; i < 14; i++) {
    const x0 = -52.5 + i * 7.5;
    polyW([[x0, -34], [x0 + 7.5, -34], [x0 + 7.5, 34], [x0, 34]], true);
    g.fillStyle = i % 2 ? TH.grass[0] : TH.grass[1]; g.fill();
  }
  g.save(); polyW(CORN, true); g.clip();
  // ince ızgara (holo temalarda belirgin)
  if (TH.grid > 0) {
    g.strokeStyle = `rgba(${TH.line},${TH.grid})`; g.lineWidth = 1 * U;
    for (let X = -50; X <= 50; X += 5) { polyW(segLine(X, -34, X, 34, 6)); g.stroke(); }
    for (let Y = -30; Y <= 30; Y += 5) { polyW(segLine(-52.5, Y, 52.5, Y, 12)); g.stroke(); }
  }
  // merkez ışık havuzu + kenarlara doğru kararma
  rg = g.createRadialGradient(cx0, cy0, 0, cx0, cy0, Math.max(W, H) * .55);
  rg.addColorStop(0, `rgba(${TH.pool},.14)`); rg.addColorStop(1, 'rgba(0,0,0,.42)');
  g.fillStyle = rg; g.fillRect(0, 0, W, H);
  // parlak zemin yansımaları: projektör sıcak noktaları + kayan parlama
  g.globalCompositeOperation = 'lighter';
  for (const [X, Y, k] of [[-38, -40, 0], [38, -40, 1]]) {
    const [hx, hy, hs] = proj(V ? Y * .9 : X, V ? -X * .9 : Y); // uzak köşeler
    const rr = 300 * U * hs;
    g.save(); g.translate(hx, hy); g.scale(1, .45);
    const hg = g.createRadialGradient(0, 0, 0, 0, 0, rr);
    hg.addColorStop(0, `rgba(${TH.beam[k]},${.20 * TH.gloss})`); hg.addColorStop(1, `rgba(${TH.beam[k]},0)`);
    g.fillStyle = hg; g.beginPath(); g.arc(0, 0, rr, 0, 6.283); g.fill(); g.restore();
  }
  const sw = (NOW * .06) % 1.6 - .3;
  const lg = g.createLinearGradient(W * (sw - .25), 0, W * (sw + .25), H * .6);
  lg.addColorStop(0, 'rgba(255,255,255,0)'); lg.addColorStop(.5, `rgba(255,255,255,${.05 * TH.gloss})`); lg.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = lg; g.fillRect(0, 0, W, H);
  g.restore();
  // ön kenar ışık çizgisi (cam kenarı)
  g.save(); g.globalCompositeOperation = 'lighter'; g.strokeStyle = `rgba(${TH.line},.35)`; g.lineWidth = 1.5 * U;
  g.beginPath(); pc.forEach(([x, y, s], i) => i ? g.lineTo(x, y + th * s) : g.moveTo(x, y + th * s)); g.closePath(); g.stroke(); g.restore();
  // çizgiler: çizim animasyonu + iki katmanlı glow
  g.lineCap = 'round'; g.lineJoin = 'round';
  for (const [lw, al] of TH.min ? [[4 * U, .10], [2 * U, 1]] : [[8 * U, .09], [3.4 * U, .22], [1.8 * U, .95]]) {
    g.strokeStyle = `rgba(${TH.line},${al})`; g.lineWidth = lw;
    PL.forEach((l, i) => {
      const p = cl(draw * 1.6 - i * .045); if (p <= 0) return;
      const n = Math.max(2, Math.ceil(l.length * p));
      polyW(l.slice(0, n)); g.stroke();
    });
  }
  g.restore();
}

// zemin üzerinde ısı bölgesi (perspektife göre basık elips)
function heat(X, Y, rM, col, a) {
  const [x, y, sc] = proj(X, Y); const r = rM * CAM.k * sc;
  g.save(); g.globalCompositeOperation = 'lighter'; g.translate(x, y); g.scale(1, Math.cos(CAM.tilt));
  const rg = g.createRadialGradient(0, 0, 0, 0, 0, r);
  rg.addColorStop(0, hexA(col, .55 * a)); rg.addColorStop(.5, hexA(col, .22 * a)); rg.addColorStop(1, hexA(col, 0));
  g.fillStyle = rg; g.beginPath(); g.arc(0, 0, r, 0, 6.283); g.fill(); g.restore();
}
function rgbOf(hex) { const n = parseInt(hex.slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; }
function shade(hex, f, a = 1) { const [r, gg, b] = rgbOf(hex); return `rgba(${r * f | 0},${gg * f | 0},${b * f | 0},${a})`; }
function tint(hex, f, a = 1) { const [r, gg, b] = rgbOf(hex); return `rgba(${r + (255 - r) * f | 0},${gg + (255 - gg) * f | 0},${b + (255 - b) * f | 0},${a})`; }
// 3D disk jeton: silindir gövde + parlak üst yüz + kenar ışığı + zemin yansıması
function token(X, Y, team, num, label, sz, a, hl = 0, ls = 1) {
  if (a <= 0) return;
  const [x, y, sc0] = proj(X, Y), sc = sc0 * CAM.zm; const r = sz * U * sc;
  const ky = .12 + .88 * Math.cos(CAM.tilt);           // üst yüz basıklığı
  const hgt = r * (.18 + .5 * Math.sin(CAM.tilt));      // gövde yüksekliği
  const dark = shade(team.c1, team.c1 === '#F4F4F2' ? .55 : .42);
  g.save(); g.globalAlpha = a;
  // zemin halesi (ışık havuzu)
  if (hl > 0) {
    g.save(); g.globalCompositeOperation = 'lighter'; g.translate(x, y); g.scale(1, ky);
    const rg = g.createRadialGradient(0, 0, r * .6, 0, 0, r * 3.6);
    rg.addColorStop(0, hexA(team.ring, .55 * hl)); rg.addColorStop(1, hexA(team.ring, 0));
    g.fillStyle = rg; g.beginPath(); g.arc(0, 0, r * 3.6, 0, 6.283); g.fill(); g.restore();
  }
  // gölge (ışık sol üstten → sağ alta düşer)
  g.save(); g.translate(x + r * .35, y + r * ky * .35); g.scale(1, ky);
  let rg = g.createRadialGradient(0, 0, r * .4, 0, 0, r * 1.7);
  rg.addColorStop(0, 'rgba(0,0,0,.6)'); rg.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = rg; g.beginPath(); g.arc(0, 0, r * 1.7, 0, 6.283); g.fill(); g.restore();
  // parlak zeminde ayna yansıması
  if (TH.refl > 0) {
    g.save(); g.globalAlpha = a * TH.refl;
    const fg = g.createLinearGradient(0, y, 0, y + hgt * 1.6);
    fg.addColorStop(0, shade(team.c1, .9, .9)); fg.addColorStop(1, shade(team.c1, .9, 0));
    g.fillStyle = fg; g.fillRect(x - r, y, r * 2, hgt * 1.6); g.restore();
  }
  // gövde
  const sg = g.createLinearGradient(x - r, 0, x + r, 0);
  sg.addColorStop(0, tint(team.c1, .1)); sg.addColorStop(.3, shade(team.c1, .92)); sg.addColorStop(.75, dark); sg.addColorStop(1, shade(team.c1, .25));
  g.fillStyle = sg;
  g.beginPath(); g.ellipse(x, y, r, r * ky, 0, 0, Math.PI); g.lineTo(x - r, y - hgt); g.ellipse(x, y - hgt, r, r * ky, 0, Math.PI, 0, true); g.closePath(); g.fill();
  // takım rengi şerit (gövde ortası)
  g.strokeStyle = hexA(team.c2 === '#0B0B0C' ? '#000000' : team.c2, .55); g.lineWidth = Math.max(1, hgt * .18);
  g.beginPath(); g.ellipse(x, y - hgt * .45, r * .995, r * ky, 0, 0, Math.PI); g.stroke();
  // üst yüz: speküler
  const ty = y - hgt;
  rg = g.createRadialGradient(x - r * .38, ty - r * ky * .45, r * .05, x, ty, r * 1.25);
  rg.addColorStop(0, tint(team.c1, .75)); rg.addColorStop(.45, team.c1); rg.addColorStop(1, shade(team.c1, .72));
  g.fillStyle = rg; g.beginPath(); g.ellipse(x, ty, r, r * ky, 0, 0, 6.283); g.fill();
  // iç halka + kenar ışığı
  g.lineWidth = 1.6 * U * sc; g.strokeStyle = team.c2 === '#0B0B0C' ? 'rgba(0,0,0,.55)' : hexA(team.c2, .7);
  g.beginPath(); g.ellipse(x, ty, r * .8, r * .8 * ky, 0, 0, 6.283); g.stroke();
  g.save(); g.globalCompositeOperation = 'lighter';
  g.lineWidth = 1.8 * U * sc; g.strokeStyle = hexA(TH.rim, .85);
  g.beginPath(); g.ellipse(x, ty, r, r * ky, 0, Math.PI * .95, Math.PI * 1.75); g.stroke();
  g.fillStyle = 'rgba(255,255,255,.55)'; g.beginPath(); g.ellipse(x - r * .42, ty - r * ky * .42, r * .22, r * .1 * ky + r * .04, -.5, 0, 6.283); g.fill();
  g.restore();
  if (num != null) {
    g.save(); g.translate(x, ty); g.scale(1, ky);
    const ns = String(num).length; g.fillStyle = team.c2; g.font = F(800, r * (ns <= 2 ? .95 : .72)); g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(String(num), 0, r * .06); g.restore();
  }
  if (label) {
    const q = sc * ls; g.font = F(700, 17 * U * q, 'JetBrains Mono'); g.textBaseline = 'middle'; g.textAlign = 'center';
    const tw = g.measureText(label).width + 16 * U * q, ly = y + r * ky + 20 * U * q;
    g.fillStyle = 'rgba(6,3,16,.82)'; rrect(x - tw / 2, ly - 12 * U * q, tw, 24 * U * q, 12 * U * q); g.fill();
    g.strokeStyle = hexA(team.ring, .45); g.lineWidth = 1 * U; g.stroke();
    g.fillStyle = TH.txt; g.fillText(label, x, ly + 1);
  }
  g.restore();
}

// dünya uzayında eğri ok (pas/koşu). p: çizim ilerlemesi, dash: koşu çizgisi
function arrowW(A, B, bend, col, p, dash, wpx = 4) {
  if (!(p > 0)) return;   // NaN da elenir
  const mx = (A[0] + B[0]) / 2, my = (A[1] + B[1]) / 2, dx = B[0] - A[0], dy = B[1] - A[1];
  const C = [mx - dy * bend, my + dx * bend];
  const pts = []; const n = 40, m = Math.ceil(n * cl(p));
  for (let i = 0; i <= m; i++) { const t = i / n, u = 1 - t; pts.push(proj(u * u * A[0] + 2 * u * t * C[0] + t * t * B[0], u * u * A[1] + 2 * u * t * C[1] + t * t * B[1])); }
  g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
  if (dash) g.setLineDash([10 * U, 10 * U]);
  for (const [lw, al, comp] of [[wpx * 3.2 * U, .18, 'lighter'], [wpx * U, .95, 'source-over']]) {
    g.globalCompositeOperation = comp; g.strokeStyle = hexA(col, al); g.lineWidth = lw;
    g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke();
  }
  // ok çizilirken uçtan geriye saçılan kıvılcımlar
  if (p < 1 && pts.length > 4 && !TH.min) {
    g.save(); g.globalCompositeOperation = 'lighter';
    const rr = rng((A[0] * 97 + B[1] * 31) | 0);
    for (let k = 0; k < 26; k++) {
      const idx = Math.max(0, pts.length - 1 - Math.floor(rr() * Math.min(12, pts.length - 1))), [sx, sy] = pts[idx];
      const age = (pts.length - 1 - idx) / 12, ang = rr() * 6.283, d = (4 + rr() * 26) * U * (.3 + age);
      g.fillStyle = hexA(col, .9 * (1 - age)); g.beginPath(); g.arc(sx + Math.cos(ang) * d, sy + Math.sin(ang) * d, (1 + rr() * 2.2) * U * (1 - age * .6), 0, 6.283); g.fill();
    }
    g.restore();
  }
  // uç: ışıklı kafa
  const [hx, hy] = pts[pts.length - 1], [qx, qy] = pts[Math.max(0, pts.length - 3)];
  const an = Math.atan2(hy - qy, hx - qx), hs = 13 * U;
  g.setLineDash([]); g.globalCompositeOperation = 'source-over'; g.fillStyle = col;
  g.beginPath(); g.moveTo(hx + Math.cos(an) * hs, hy + Math.sin(an) * hs);
  g.lineTo(hx + Math.cos(an + 2.5) * hs, hy + Math.sin(an + 2.5) * hs); g.lineTo(hx + Math.cos(an - 2.5) * hs, hy + Math.sin(an - 2.5) * hs); g.closePath(); g.fill();
  g.restore();
}
function ball(X, Y, a, sz = 1) {
  const [x, y, sc0] = proj(X, Y), sc = sc0 * sz * CAM.zm; g.save(); g.globalAlpha = a; g.globalCompositeOperation = 'lighter';
  const rg = g.createRadialGradient(x, y - 6 * U, 0, x, y - 6 * U, 26 * U * sc);
  rg.addColorStop(0, 'rgba(255,255,255,.95)'); rg.addColorStop(.25, 'rgba(255,250,220,.5)'); rg.addColorStop(1, 'rgba(255,250,220,0)');
  g.fillStyle = rg; g.beginPath(); g.arc(x, y - 6 * U, 26 * U * sc, 0, 6.283); g.fill(); g.restore();
}

// ---------- sahneler ----------
const SC = {};
function fitPx(txt, w, fam, px, maxW) { g.save(); g.font = F(w, px, fam); const m = g.measureText(txt).width; g.restore(); return m > maxW ? px * maxW / m : px; }
SC.intro = (c) => {
  const { lt, a } = c, H2 = EP.home, A2 = EP.away;
  g.save(); g.globalAlpha = a;
  const push = 1.06 - .06 * eOut(cl(lt / 6));
  g.translate(W / 2, H / 2); g.scale(push, push); g.translate(-W / 2, -H / 2);
  const kp = win(lt, .15, 1.0);
  if (V) {
    maskText(EP.kicker, W / 2, H * .30, F(500, 26 * U, 'JetBrains Mono'), TH.mut2, kp, 'center', 4 * U);
    maskText(H2.name, W / 2, H * .42, F(800, fitPx(H2.name, 800, 'Unbounded', 118 * U, W * .86), 'Unbounded'), H2.c1 === '#A90432' ? '#FFFFFF' : H2.c1, win(lt, .35, 1.3));
    const dp = eOut(win(lt, .8, 1.6));
    g.fillStyle = TH.acc; g.globalAlpha = a * dp; g.font = F(300, 70 * U, 'Unbounded'); g.textAlign = 'center'; g.fillText('×', W / 2, H * .49);
    g.globalAlpha = a;
    A2.lines.forEach((l, i) => maskText(l, W / 2, H * (.565 + i * .065), F(800, 92 * U, 'Unbounded'), '#FFFFFF', win(lt, .95 + i * .18, 1.9 + i * .18)));
    // kulüp renk çubukları
    const bw = 420 * U * eExpo(win(lt, .6, 1.6));
    g.fillStyle = H2.c1; g.fillRect(W / 2 - bw / 2, H * .438, bw, 5 * U);
    g.fillStyle = A2.c1; g.fillRect(W / 2 - bw / 2, H * .66, bw, 5 * U);
  } else {
    maskText(EP.kicker, W / 2, H * .24, F(500, 24 * U, 'JetBrains Mono'), TH.mut2, kp, 'center', 5 * U);
    const gap = 70 * U;
    maskText(H2.name, W / 2 - gap, H * .53, F(800, fitPx(H2.name, 800, 'Unbounded', 104 * U, W / 2 - gap - 80 * U), 'Unbounded'), H2.c1 === '#A90432' ? '#FFFFFF' : H2.c1, win(lt, .35, 1.3), 'right');
    A2.lines.forEach((l, i) => maskText(l, W / 2 + gap, H * (.47 + i * .115), F(800, 72 * U, 'Unbounded'), '#FFFFFF', win(lt, .7 + i * .18, 1.6 + i * .18), 'left'));
    const lp = eExpo(win(lt, .5, 1.5)), lh = 260 * U * lp;
    const lg = g.createLinearGradient(0, H * .5 - lh / 2, 0, H * .5 + lh / 2);
    lg.addColorStop(0, hexA(TH.acc, 0)); lg.addColorStop(.5, hexA(TH.acc, 1)); lg.addColorStop(1, hexA(TH.acc, 0));
    g.fillStyle = lg; g.fillRect(W / 2 - 1.5 * U, H * .5 - lh / 2, 3 * U, lh);
    const bw = 360 * U * eExpo(win(lt, .7, 1.7));
    g.fillStyle = H2.c1; g.fillRect(W / 2 - gap - bw, H * .565, bw, 5 * U);
    g.fillStyle = A2.c1; g.fillRect(W / 2 + gap, H * .64, bw, 5 * U);
  }
  // alt bilgi şeridi
  const ip = win(lt, 1.6, 2.6);
  maskText(EP.infoLine || '', W / 2, V ? H * .75 : H * .76, F(700, (V ? 30 : 26) * U), TH.mut, ip, 'center', 3 * U);
  g.restore();
};
SC.card = (c) => {
  const { lt, a, sc } = c;
  g.save(); g.globalAlpha = a;
  const pz = 1 + .035 * eIO(cl(lt / c.d));   // yavaş itme (dolly-in)
  g.translate(W / 2, H * .45); g.scale(pz, pz); g.translate(-W / 2, -H * .45);
  maskText('MAÇ KARTI', V ? W / 2 : 120 * U, V ? H * .17 : H * .17, F(800, (V ? 54 : 46) * U, 'Unbounded'), '#FFFFFF', win(lt, 0, .8), V ? 'center' : 'left', 2 * U);
  const tiles = sc.tiles, cols = V ? 2 : 3;
  const tw = V ? 430 * U : 520 * U, th = V ? 210 * U : 170 * U, gx = 26 * U, gy = 22 * U;
  const x0 = (W - (cols * tw + (cols - 1) * gx)) / 2, y0 = V ? H * .22 : H * .22;
  tiles.forEach((t, i) => {
    const p = eOut(win(lt, .25 + i * .12, 1.1 + i * .12)); if (p <= 0) return;
    const cx = x0 + (i % cols) * (tw + gx), cy = y0 + Math.floor(i / cols) * (th + gy) + (1 - p) * 40 * U;
    g.save(); g.globalAlpha = a * p;
    glass(cx, cy, tw, th, 22 * U, 1);
    g.textAlign = 'left'; g.letterSpacing = 3 * U + 'px';
    g.fillStyle = TH.mut2; g.font = F(500, 19 * U, 'JetBrains Mono'); g.fillText(t.k, cx + 30 * U, cy + 46 * U);
    g.letterSpacing = '0px'; g.fillStyle = '#FFFFFF'; g.font = F(800, (V ? 58 : 50) * U); g.fillText(t.v, cx + 30 * U, cy + (V ? 118 : 106) * U);
    g.fillStyle = t.s.includes('DOĞRULA') ? '#FF9A9A' : TH.mut; g.font = F(500, 21 * U); g.fillText(t.s, cx + 30 * U, cy + (V ? 160 : 142) * U);
    g.restore();
  });
  // rota bandı: İstanbul → Batum
  const rt = EP.segs[sc.seg[1]].t0, r = sc.route, rp = eIO(win(c.T, rt - .2, rt + 1.4));
  if (rp > 0) {
    const rows = Math.ceil(tiles.length / cols);
    const by = y0 + rows * (th + gy) + (V ? 150 : 120) * U, bx0 = x0 + 40 * U, bx1 = x0 + cols * tw + (cols - 1) * gx - 40 * U;
    const arcH = (V ? 70 : 45) * U;
    g.save(); g.globalAlpha = a; g.lineCap = 'round';
    g.strokeStyle = hexA(TH.acc, .95); g.lineWidth = 3 * U; g.setLineDash([2 * U, 9 * U]);
    g.beginPath(); for (let i = 0; i <= 60 * rp; i++) { const t = i / 60, x = lerp(bx0, bx1, t), y = by - Math.sin(t * Math.PI) * arcH; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
    g.setLineDash([]);
    for (const [t, lab, al] of [[0, r.a, 'left'], [1, r.b, 'right']]) {
      const vis = t === 0 ? 1 : cl((rp - .95) * 20); if (vis <= 0) continue;
      const x = lerp(bx0, bx1, t); g.globalAlpha = a * vis;
      g.fillStyle = TH.acc; g.beginPath(); g.arc(x, by, 8 * U, 0, 6.283); g.fill();
      g.font = F(700, 22 * U, 'JetBrains Mono'); g.letterSpacing = 2 * U + 'px'; g.textAlign = al; g.fillStyle = TH.txt;
      g.fillText(lab, x, by + 42 * U);
    }
    g.globalAlpha = a * cl((rp - .5) * 3); g.textAlign = 'center'; g.letterSpacing = '0px';
    g.font = F(800, 30 * U); g.fillStyle = '#FFFFFF'; g.fillText(r.km, (bx0 + bx1) / 2, by - arcH - 22 * U);
    g.font = F(500, 21 * U); g.fillStyle = TH.mut; g.fillText(r.note, (bx0 + bx1) / 2, by + 42 * U);
    g.restore();
  }
  g.restore();
};
// ---------- sinematik kamera: keyframe hareketleri + speed ramp ----------
const eRamp = t => t < .5 ? 16 * t ** 5 : 1 - Math.pow(-2 * t + 2, 5) / 2;   // sert hızlan, uzun yavaşla
const eLin = t => t;
const slowmo = (t, k = .82) => t + k / (2 * Math.PI) * Math.sin(2 * Math.PI * t); // uçlar hızlı, orta yavaş
// base: başlangıç durumu; moves: [{at, dur, e, to:{...}}] sırayla uygulanır
function camAt(T, base, moves) {
  const st = { ...base };
  for (const m of moves) {
    if (T <= m.at) break;
    const u = (m.e || eRamp)(cl((T - m.at) / m.dur));
    const from = { ...st };
    for (const k in m.to) st[k] = lerp(from[k], m.to[k], u);
  }
  return st;
}
function projH(X, Y, z) { const [x, y, sc] = proj(X, Y); return [x, y - z * CAM.k * sc * Math.sin(CAM.tilt), sc]; }
// Genel taktik sahnesi: kamera + efektler veri dosyasındaki beat listesinden gelir.
// beat: { k: 'rakip'|'kanat'|'kur'|'pres'|'bitir', s: segment, w: tetik kelime, label, camSeg?: true (kamera segment başında) ,
//         focus?: oyuncu adı (kur), cutter?, finisher?, cutTo?: [x,y], cross?: kelime (bitir: orta anı), arrive?: kelime (bitir: varış), arrows?: [[A,B],..] (rakip) }
SC.tactic = (c) => {
  const { lt, a, sc, T } = c;
  const seg = i => EP.segs[i];
  const idx = nm => EP.lineup.findIndex(p => p.nm === nm || p.pos === nm);
  const B = (sc.beats || []).map((b, i) => ({ ...b, t: wT(b.s, b.w) }));
  B.forEach(b => { b.cam = b.camSeg ? seg(b.s).t0 - .25 : b.t - .25; });
  B.forEach((b, i) => { b.end = i + 1 < B.length ? B[i + 1].cam + .3 : sc.t1 + 1; });
  const vStd = { yaw: 0, fx: 0, fy: 0, tilt: V ? .92 : .98, zm: 1, cy: V ? .45 : .50 };
  const base = { fx: 0, fy: 0, yaw: V ? .35 : -.25, tilt: .15, zm: .82, cy: V ? .45 : .50 };
  const mv = [{ at: sc.t0, dur: 2.0, to: { yaw: 0, tilt: vStd.tilt, zm: 1 } }];
  for (const b of B) {
    const nxt = b.end - .3, hold = Math.max(.5, nxt - b.cam - 1.6);
    if (b.k === 'rakip') {
      mv.push({ at: b.cam, dur: 1.7, to: { yaw: Math.PI * .94, fx: -10, fy: 0, tilt: 1.0, zm: V ? 1.08 : 1.18, cy: V ? .40 : .47 } });
      mv.push({ at: b.cam + 1.7, dur: hold, e: eLin, to: { yaw: Math.PI * 1.02 } });
    } else if (b.k === 'kanat') {
      mv.push({ at: b.cam, dur: 1.0, to: { ...vStd } });
    } else if (b.k === 'kur') {
      const i = idx(b.focus), p = i >= 0 ? P(EP.lineup[i].x + .03, EP.lineup[i].y) : [0, 0];
      mv.push({ at: b.cam, dur: 1.15, to: { fx: p[0], fy: p[1], zm: V ? 1.7 : 1.75, tilt: 1.06, yaw: .28, cy: V ? .40 : .56 } });
      mv.push({ at: b.cam + 1.15, dur: hold + .5, e: eLin, to: { yaw: .52 } });
    } else if (b.k === 'pres') {
      mv.push({ at: b.cam, dur: 1.25, to: { fx: 8, fy: 0, zm: .96, tilt: .52, yaw: 0, cy: V ? .45 : .50 } });
    } else if (b.k === 'bitir') {
      const ct = P(...(b.cutTo || [.76, .28])), fi = EP.lineup[idx(b.finisher)] || { x: .69, y: .5 }, fp = P(fi.x, fi.y);
      mv.push({ at: b.cam, dur: 1.35, to: { fx: (ct[0] + fp[0]) / 2, fy: (ct[1] + fp[1]) / 2, zm: V ? 1.75 : 1.85, tilt: 1.14, yaw: -.5, cy: V ? .40 : .56 } });
      mv.push({ at: b.cam + 1.35, dur: Math.max(1, nxt - b.cam - 1.35), e: eLin, to: { yaw: .32 } });
    }
  }
  const cs = camAt(T, base, mv);
  const kBase = V ? W * .64 / 68 : W * .60 / 105;
  CAM.fx = cs.fx; CAM.fy = cs.fy; CAM.yaw = cs.yaw + Math.sin(T * .3) * .012; CAM.tilt = cs.tilt; CAM.zm = cs.zm;
  CAM.k = kBase * cs.zm; CAM.d = 1500 * U * Math.max(1, cs.zm * .85);
  CAM.cx = W / 2; CAM.cy = H * cs.cy;
  g.save(); g.globalAlpha = a;
  drawPitch(1, win(lt, .1, 1.6));
  const life = b => b ? win(T, b.t - .1, b.t + .3) * (1 - win(T, b.end - .3, b.end + .3)) : 0;
  const bk = k => B.find(b => b.k === k);
  const bR = bk('rakip'), bK = bk('kanat'), bC = bk('kur'), bP = bk('pres'), bF = bk('bitir');
  const press = bP ? eIO(win(T, bP.t, bP.t + 1.0)) * (1 - eIO(win(T, bP.end - .3, bP.end + .7))) : 0;
  if (press > 0) { heat(...P(.84, .5), 26, TH.acc, press * .9); heat(...P(.78, .2), 14, TH.acc, press * .5); heat(...P(.78, .8), 14, TH.acc, press * .5); }
  const oppFocus = bR ? win(T, bR.t - .2, bR.t + .6) * (1 - win(T, bR.end - .6, bR.end)) : 0;
  const oa = win(lt, 1.2, 2.0) * (1 - .45 * press) * (.62 + .38 * oppFocus);
  const TOK = [];
  EP.opp.forEach(([x, y, nm], i) => TOK.push([...P(x, y), EP.away, null, nm || null, V ? 11 : 10, oa * cl(win(lt, 1.2 + i * .03, 1.6 + i * .03) * 2), oppFocus * .7, .72 + .2 * oppFocus]));
  if (oppFocus > 0) {
    (bR.arrows || [[[.62, .72], [.24, .70]], [[.62, .28], [.24, .30]], [[.47, .42], [.14, .48]]]).forEach(([A, Bp], j) =>
      arrowW(P(...A), P(...Bp), .1 * (j - 1), EP.away.ring, eOut(win(T, wT(bR.s, bR.w2 || bR.w) + .3 + j * .18, wT(bR.s, bR.w2 || bR.w) + 1.4 + j * .18)) * oppFocus, false, 3.4));
  }
  const home = EP.lineup.map(p => P(lerp(p.x, p.px ?? p.x, press), lerp(p.y, p.py ?? p.y, press)));
  const kK = bK ? win(T, bK.t, bK.t + 1.1) : 0, lK = life(bK);
  EP.lineup.forEach((p, i) => { if (p.run) arrowW(home[i], P(...p.run), V ? -.18 * (p.y > .5 ? -1 : 1) : .18 * (p.y > .5 ? -1 : 1), TH.acc2, eOut(kK) * lK, true, 3.2); });
  const kC = bC ? win(T, bC.t, bC.t + 2.6) : 0, lC = life(bC);
  EP.passes.forEach(([i0, i1], j) => arrowW(home[i0], home[i1], .12, TH.acc, eOut(cl(kC * EP.passes.length - j)) * lC, false, 3.6));
  if (kC > 0 && lC > 0) {
    const n = EP.passes.length, f = cl(kC * n, 0, n - 1e-6);
    for (let k = 8; k >= 0; k--) {
      const fk = cl(f - k * .03, 0, n - 1e-6), jk = Math.floor(fk), uk = slowmo(fk - jk), [a0, a1] = EP.passes[jk];
      ball(lerp(home[a0][0], home[a1][0], uk), lerp(home[a0][1], home[a1][1], uk), lC * (k ? .3 * (1 - k / 9) : 1), k ? .55 : 1);
    }
  }
  const iT = bF ? idx(bF.cutter) : -1, iV = bF ? idx(bF.finisher) : -1;
  const fin = bF ? win(T, bF.cam - .05, bF.cam + .55) : 0;
  let cutPos = null;
  if (fin > 0 && iT >= 0 && iV >= 0) {
    const cutTo = P(...(bF.cutTo || [.76, .28]));
    const kc = eOut(win(T, bF.t, bF.t + 1.0));
    cutPos = [lerp(home[iT][0], cutTo[0], kc), lerp(home[iT][1], cutTo[1], kc)];
    arrowW(home[iT], cutTo, -.15, '#FFFFFF', kc * fin, true, 3);
    const tC = wT(bF.s, bF.cross || bF.w), tA = wT(bF.s, bF.arrive || bF.w);
    const q = win(T, tC + .2, Math.max(tC + 1.2, tA + .1));
    if (q > 0 && q < 1) {
      const u = slowmo(q, .86), A = cutTo, Bv = home[iV];
      const X = lerp(A[0], Bv[0], u), Y = lerp(A[1], Bv[1], u), z = Math.sin(Math.PI * u) * 7;
      for (let k = 8; k >= 1; k--) {
        const uk = slowmo(cl(q - k * .012), .86), zk = Math.sin(Math.PI * uk) * 7;
        const [x, y, sk] = projH(lerp(A[0], Bv[0], uk), lerp(A[1], Bv[1], uk), zk);
        g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = `rgba(255,255,255,${.22 * (1 - k / 9)})`;
        g.beginPath(); g.arc(x, y, 6 * U * sk * CAM.zm * (1 - k / 12), 0, 6.283); g.fill(); g.restore();
      }
      const [gx, gy, gs] = proj(X, Y);
      g.save(); g.fillStyle = `rgba(0,0,0,${.45 * (1 - z / 10)})`; g.beginPath(); g.ellipse(gx, gy, 9 * U * gs * CAM.zm, 4 * U * gs * CAM.zm, 0, 0, 6.283); g.fill(); g.restore();
      const [bx, by, bs] = projH(X, Y, z);
      g.save(); g.globalCompositeOperation = 'lighter';
      const rg = g.createRadialGradient(bx, by, 0, bx, by, 24 * U * bs * CAM.zm);
      rg.addColorStop(0, 'rgba(255,255,255,1)'); rg.addColorStop(.3, 'rgba(255,255,255,.55)'); rg.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = rg; g.beginPath(); g.arc(bx, by, 24 * U * bs * CAM.zm, 0, 6.283); g.fill(); g.restore();
    }
  }
  const vHL = bF ? win(T, wT(bF.s, bF.arrive || bF.w) - .1, wT(bF.s, bF.arrive || bF.w) + .4) : 0;
  const iFocus = bC ? idx(bC.focus) : -1;
  EP.lineup.forEach((p, i) => {
    const ap = eBack(win(lt, .4 + i * .07, .9 + i * .07));
    let hl = (p.run && kK > 0 && kK < 1) || (EP.passes.some(q => q.includes(i)) && kC > 0 && kC < 1) ? .8 : press * .5;
    if (i === iFocus) hl = Math.max(hl, .6 * lC);
    if (i === iV) hl = Math.max(hl, vHL * (.8 + .2 * Math.sin(T * 6)));
    if (i === iT && fin > 0) hl = Math.max(hl, .6 * fin);
    const pos = i === iT && cutPos ? cutPos : home[i];
    TOK.push([pos[0], pos[1], EP.home, p.pos, p.nm, (V ? 22 : 20) * cl(ap, 0, 1.2), cl(ap * 2), hl, 1]);
  });
  TOK.sort((p, q) => proj(p[0], p[1])[1] - proj(q[0], q[1])[1]).forEach(t => token(...t));
  { const y0 = SUB.cy - SUB.fs * (V ? 3.4 : 2.9), y1 = SUB.cy + SUB.fs * .6, mg = g.createLinearGradient(0, y0, 0, y1);
    mg.addColorStop(0, hexA(TH.bg[2], 0)); mg.addColorStop(.55, hexA(TH.bg[2], .78)); mg.addColorStop(1, hexA(TH.bg[2], .94));
    g.fillStyle = mg; g.fillRect(0, y0, W, y1 - y0); g.fillStyle = hexA(TH.bg[2], .94); g.fillRect(0, y1, W, H - y1); }
  const dim = Math.max(cl((cs.zm - 1.2) / .8), 0) * .55;
  if (dim > 0) {
    const r0 = Math.min(W, H) * .32, rg = g.createRadialGradient(W / 2, CAM.cy, r0, W / 2, CAM.cy, Math.hypot(W, H) * .6);
    rg.addColorStop(0, 'rgba(0,0,0,0)'); rg.addColorStop(1, `rgba(3,1,8,${dim})`); g.fillStyle = rg; g.fillRect(0, 0, W, H);
  }
  { const y1 = V ? H * .25 : H * .34, tg = g.createLinearGradient(0, 0, 0, y1);
    tg.addColorStop(0, hexA(TH.bg[2], .9)); tg.addColorStop(.6, hexA(TH.bg[2], .55)); tg.addColorStop(1, hexA(TH.bg[2], 0));
    g.fillStyle = tg; g.fillRect(0, 0, W, y1); }
  const hy = V ? H * .14 : H * .165, hx = V ? W / 2 : 120 * U, al = V ? 'center' : 'left';
  if (!CLEAN) {
  maskText(sc.title || 'OYUN PLANI', hx, hy, F(800, (V ? 50 : 42) * U, 'Unbounded'), '#FFFFFF', win(lt, .2, 1), al, 2 * U);
  maskText(sc.formation, V ? W / 2 : hx + 430 * U, V ? hy + 56 * U : hy, F(300, (V ? 40 : 42) * U, 'Unbounded'), TH.acc, win(lt, .5, 1.3), V ? 'center' : 'left');
  if (EP.lineupNote) maskText(EP.lineupNote, V ? W / 2 : hx, V ? hy + 182 * U : hy + 112 * U, F(500, 19 * U, 'JetBrains Mono'), TH.mut2, win(lt, .9, 1.7) * (1 - dim * 1.5), al, 2 * U);
  const cur = B.filter(b => T >= b.t - .1).length - 1;
  if (cur >= 0) {
    const b = B[cur], col = b.k === 'rakip' ? EP.away.ring : TH.acc, sp = win(T, b.t - .1, b.t + .45);
    g.font = F(700, 24 * U, 'JetBrains Mono'); g.letterSpacing = 3 * U + 'px';
    const tw = g.measureText(b.label).width + 44 * U, bx = V ? W / 2 - tw / 2 : hx, by = V ? hy + 96 * U : hy + 32 * U;
    g.save(); g.globalAlpha = a * eOut(sp); g.translate(0, (1 - eExpo(sp)) * 14 * U);
    rrect(bx, by, tw, 46 * U, 23 * U); g.fillStyle = hexA(col, .14); g.fill(); g.strokeStyle = hexA(col, .75); g.lineWidth = 1.4 * U; g.stroke();
    g.fillStyle = col; g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillText(b.label, bx + 22 * U, by + 24 * U);
    g.restore();
  }
  }
  if (press > 0) {
    const [x, y] = proj(...P(.84, .5)); const tp = cl((T - bP.t - .3) / 5);
    g.save(); g.globalAlpha = a * press; g.lineCap = 'round';
    g.strokeStyle = 'rgba(255,255,255,.18)'; g.lineWidth = 6 * U; g.beginPath(); g.arc(x, y - 150 * U, 44 * U, 0, 6.283); g.stroke();
    g.strokeStyle = TH.acc; g.beginPath(); g.arc(x, y - 150 * U, 44 * U, -Math.PI / 2, -Math.PI / 2 + 6.283 * (1 - tp)); g.stroke();
    g.fillStyle = '#FFF'; g.font = F(800, 32 * U); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(Math.max(0, Math.ceil(5 - tp * 5)) + 'sn', x, y - 148 * U);
    g.restore();
  }
  g.restore();
};
SC.scen = (c) => {
  const { lt, a, sc, T } = c, si = sc.seg[0];
  g.save(); g.globalAlpha = a;
  maskText('3 SENARYO', V ? W / 2 : 120 * U, V ? H * .17 : H * .17, F(800, (V ? 54 : 46) * U, 'Unbounded'), '#FFFFFF', win(lt, 0, .8), V ? 'center' : 'left', 2 * U);
  maskText('kanal tahmini · kesinlik değil', V ? W / 2 : 120 * U, V ? H * .17 + 50 * U : H * .17 + 44 * U, F(500, 22 * U, 'JetBrains Mono'), TH.mut2, win(lt, .3, 1.1), V ? 'center' : 'left', 1 * U);
  const n = sc.items.length, cw = V ? 900 * U : 520 * U, ch = V ? 250 * U : 430 * U, gp = 30 * U;
  const x0 = V ? (W - cw) / 2 : (W - (n * cw + (n - 1) * gp)) / 2, y0 = V ? H * .24 : H * .29;
  if (TH.min) sc.items.forEach((it, i) => it.c = [TH.acc2, TH.acc, '#E58AA8'][i] || it.c);
  const hT = it => wT(it.s ?? si, it.w);
  let hot = -1; sc.items.forEach((it, i) => { if (it.w && T >= hT(it)) hot = i; });
  sc.items.forEach((it, i) => {
    const p = eOut(win(lt, .3 + i * .18, 1.2 + i * .18)); if (p <= 0) return;
    const x = V ? x0 : x0 + i * (cw + gp), y = (V ? y0 + i * (ch + gp) : y0) + (1 - p) * 50 * U;
    const isHot = i === hot, hp = isHot ? eOut(win(T, hT(it), hT(it) + .6)) : 0;
    g.save(); g.globalAlpha = a * p * (hot >= 0 && !isHot ? .55 : 1);
    glass(x, y, cw, ch, 26 * U, 1, isHot ? it.c : '#FFFFFF');
    if (hp > 0) { rrect(x, y, cw, ch, 26 * U); g.strokeStyle = hexA(it.c, .9 * hp); g.lineWidth = 2.5 * U; g.stroke(); }
    const pad = 36 * U;
    g.textAlign = 'left'; g.fillStyle = it.c; g.font = F(300, 40 * U, 'Unbounded'); g.fillText('0' + (i + 1), x + pad, y + 70 * U);
    g.fillStyle = '#FFFFFF'; g.font = F(800, (V ? 46 : 40) * U); g.fillText(it.t, x + pad + (V ? 100 * U : 0), y + (V ? 70 : 140) * U);
    g.fillStyle = TH.mut; g.font = F(500, (V ? 26 : 24) * U); g.fillText(it.d, x + pad + (V ? 100 * U : 0), y + (V ? 112 : 186) * U);
    // olasılık çubuğu + sayaç
    const bp = eIO(win(lt, .9 + i * .2, 2.2 + i * .2)), by = y + ch - (V ? 62 : 80) * U, bw = cw - pad * 2 - 130 * U;
    rrect(x + pad, by, bw, 12 * U, 6 * U); g.fillStyle = 'rgba(255,255,255,.08)'; g.fill();
    if (bp > 0) { rrect(x + pad, by, Math.max(12 * U, bw * it.p / 100 * bp), 12 * U, 6 * U); g.fillStyle = it.c; g.fill(); }
    g.fillStyle = '#FFFFFF'; g.font = F(800, 46 * U); g.textAlign = 'right'; g.fillText('%' + Math.round(it.p * bp), x + cw - pad, by + 16 * U);
    g.restore();
  });
  g.restore();
};
SC.outro = (c) => {
  const { lt, a, T } = c, H2 = EP.home, A2 = EP.away;
  g.save(); g.globalAlpha = a;
  const ty = V ? H * .30 : H * .26;
  maskText('TAHMİN', W / 2, ty, F(800, (V ? 120 : 110) * U, 'Unbounded'), '#FFFFFF', win(lt, 0, .9));
  maskText('LİGİ', W / 2, ty + (V ? 130 : 115) * U, F(300, (V ? 120 : 110) * U, 'Unbounded'), TH.acc, win(lt, .2, 1.1));
  // skor kutuları
  const bp = eBack(win(lt, .8, 1.6)), bs = (V ? 150 : 120) * U, by = V ? H * .45 : H * .40;
  const items = [[H2.short, -1], [A2.short, 1]];
  items.forEach(([lab, sd]) => {
    const x = W / 2 + sd * (bs * .5 + 40 * U) - bs / 2;
    g.save(); g.globalAlpha = a * cl(bp); g.translate(x + bs / 2, by + bs / 2); g.scale(cl(bp, 0, 1.2), cl(bp, 0, 1.2)); g.translate(-bs / 2, -bs / 2);
    glass(0, 0, bs, bs, 24 * U, 1);
    const pul = .75 + .25 * Math.sin(T * 4 + sd);
    g.fillStyle = TH.acc; g.globalAlpha *= pul; g.font = F(800, bs * .55); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('?', bs / 2, bs * .52); g.globalAlpha /= pul;
    g.fillStyle = TH.mut2; g.font = F(700, 24 * U, 'JetBrains Mono'); g.letterSpacing = 3 * U + 'px'; g.fillText(lab, bs / 2, bs + 34 * U);
    g.restore();
  });
  g.save(); g.globalAlpha = a * cl(bp); g.fillStyle = '#FFFFFF'; g.font = F(300, 70 * U, 'Unbounded'); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('–', W / 2, by + bs / 2); g.restore();
  if (EP.wish) { const tb = wT(EP.segs.length - 1, EP.wishWord || 'başarı'), bp2 = win(T, tb - .15, tb + .7), yb = by + bs + (V ? 230 : 185) * U;
    if (bp2 > 0) {
      g.save(); g.globalAlpha = a; const lw = 520 * U * eExpo(bp2);
      g.fillStyle = hexA(TH.acc, .9); g.fillRect(W / 2 - lw / 2, yb - (V ? 78 : 64) * U, lw, 2 * U); g.restore();
      maskText(EP.wish || '', W / 2, yb, F(800, (V ? 58 : 50) * U, 'Unbounded'), '#FFFFFF', bp2, 'center', 3 * U);
    } }
  maskText('Yorumlara yaz · sıralama bir sonraki bölümde', W / 2, by + bs + (V ? 120 : 92) * U, F(700, (V ? 32 : 28) * U), TH.mut, win(lt, 1.4, 2.3));
  g.restore();
};

// ---------- karaoke altyazı ----------
const SUB = { fs: (V ? 58 : 46) * U, maxW: V ? W - 2 * 120 * U : W * .62, cy: V ? 1640 * (H / 1920) : H * .885 };
function paginate() {
  g.save(); g.font = F(800, SUB.fs); const sp = g.measureText(' ').width;
  for (const s of EP.segs) {
    const lines = []; let cur = [], cw = 0;
    s.words.forEach((w, i) => { const ww = g.measureText(w).width;
      if (cur.length && cw + sp + ww > SUB.maxW) { lines.push(cur); cur = []; cw = 0; }
      cur.push(i); cw += (cur.length > 1 ? sp : 0) + ww; });
    if (cur.length) lines.push(cur);
    s.pages = []; for (let i = 0; i < lines.length; i += 2) s.pages.push(lines.slice(i, i + 2));
  }
  g.restore();
}
function subtitles(T) {
  const s = EP.segs.find(s => T >= s.t0 - .2 && T <= s.t1 + .4); if (!s) return;
  const a = win(T, s.t0 - .2, s.t0) * (1 - win(T, s.t1 + .15, s.t1 + .4));
  let wi = s.wt.findIndex(([a0, a1]) => T < a1); if (wi < 0) wi = s.words.length - 1;
  const page = s.pages.find(p => p.flat().includes(wi)) || s.pages[s.pages.length - 1];
  const spk = EP.spk[s.spk];
  g.save(); g.font = F(800, SUB.fs); g.textBaseline = 'middle'; g.textAlign = 'left';
  const sp = g.measureText(' ').width, lh = SUB.fs * 1.22;
  const y0 = SUB.cy - (page.length - 1) * lh / 2;
  // arkada okunurluk için yumuşak koyu bant
  const bg2 = g.createLinearGradient(0, SUB.cy - lh * 2.2, 0, SUB.cy + lh * 2);
  bg2.addColorStop(0, 'rgba(2,4,8,0)'); bg2.addColorStop(.5, `rgba(2,4,8,${.55 * a})`); bg2.addColorStop(1, 'rgba(2,4,8,0)');
  g.fillStyle = bg2; g.fillRect(0, SUB.cy - lh * 2.2, W, lh * 4.2);
  // konuşan etiketi
  g.globalAlpha = a; g.font = F(700, 20 * U, 'JetBrains Mono'); g.letterSpacing = 4 * U + 'px'; g.textAlign = 'center';
  g.fillStyle = spk.col; g.fillText('● ' + spk.name, W / 2, y0 - lh * .95);
  g.letterSpacing = '0px'; g.font = F(800, SUB.fs); g.textAlign = 'left';
  page.forEach((line, li) => {
    const ws = line.map(i => g.measureText(s.words[i]).width), tw = ws.reduce((x, y) => x + y, 0) + sp * (line.length - 1);
    let x = W / 2 - tw / 2; const y = y0 + li * lh;
    line.forEach((i, j) => {
      const [w0, w1] = s.wt[i], on = T >= w0 && T < w1 + .05, past = T >= w1;
      const k = on ? eOut(win(T, w0, w0 + .12)) : 0;
      if (on) { g.save(); g.shadowColor = hexA(spk.col, .6); g.shadowBlur = 18 * U * k; g.fillStyle = spk.col; g.fillText(s.words[i], x, y - 3 * U * k); g.restore(); }
      else { g.fillStyle = past ? 'rgba(242,244,247,.78)' : 'rgba(242,244,247,.36)'; g.fillText(s.words[i], x, y); }
      x += ws[j] + sp;
    });
  });
  g.restore();
}


// ---------- bloom: parlak alanlar 1/4 çözünürlükte eşiklenir, iki yarıçapta bulanıklaştırılır ----------
const BLa = document.createElement('canvas'), BLb = document.createElement('canvas');
BLa.width = BLb.width = Math.round(cv.width / 4); BLa.height = BLb.height = Math.round(cv.height / 4);
const ba = BLa.getContext('2d'), bb = BLb.getContext('2d');
function bloom() {
  if (TH.bloom <= 0) return;
  ba.filter = 'brightness(.85) contrast(3.2) saturate(1.35)'; ba.clearRect(0, 0, BLa.width, BLa.height);
  ba.drawImage(cv, 0, 0, BLa.width, BLa.height); ba.filter = 'none';
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'lighter';
  for (const [rad, k] of [[3, .55], [14, .75]]) {
    bb.clearRect(0, 0, BLb.width, BLb.height); bb.filter = `blur(${rad * S}px)`; bb.drawImage(BLa, 0, 0); bb.filter = 'none';
    g.globalAlpha = TH.bloom * k; g.drawImage(BLb, 0, 0, cv.width, cv.height);
  }
  g.restore();
}

// ---------- ana render ----------
function render(T) {
  NOW = T;
  g.setTransform(S, 0, 0, S, 0, 0);
  g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
  bg(T);
  const tac = EP.scenes.find(s => s.type === 'tactic');
  const inTac = tac ? win(T, tac.t0, tac.t0 + .6) * (1 - win(T, tac.t1, tac.t1 + .6)) : 0;
  beams(T, 1 - .35 * inTac);
  bokeh(T, false, 1 - .4 * inTac);
  for (const sc of EP.scenes) {
    const fo = .55; if (T < sc.t0 || T > sc.t1 + fo) continue;
    const a = (sc.t0 === 0 ? 1 : eOut(win(T, sc.t0, sc.t0 + .5))) * (1 - eIO(win(T, sc.t1, sc.t1 + fo)));
    if (a <= 0) continue;
    const zi = sc.t0 === 0 ? 0 : 1 - eExpo(win(T, sc.t0, sc.t0 + .8)), zo = Math.pow(win(T, sc.t1, sc.t1 + fo), 2);
    const zs = 1 + .07 * zi + .09 * zo;
    g.save(); g.translate(W / 2, H / 2); g.scale(zs, zs); g.translate(-W / 2, -H / 2);
    SC[sc.type]({ T, lt: T - sc.t0, d: sc.t1 - sc.t0, a, sc });
    g.restore();
  }
  bokeh(T, true);
  if (!CLEAN) brandBug(T, win(T, .3, 1.2) * (1 - win(T, EP.dur - .8, EP.dur)));
  bloom();
  g.save(); g.globalCompositeOperation = TH.grade[1]; g.fillStyle = TH.grade[0]; g.fillRect(0, 0, W, H); g.restore();
  if (!CLEAN) subtitles(T);
  vignette();
  // tane + sona doğru karartma
  g.save(); g.globalAlpha = .035; g.globalCompositeOperation = 'overlay';
  const f = Math.floor(T * 30), r = rng(f * 977 + 13);
  g.translate(-r() * 256, -r() * 256); g.fillStyle = g.createPattern(grain, 'repeat'); g.fillRect(0, 0, W + 256, H + 256);
  g.restore();
  const fade = win(T, EP.dur - .7, EP.dur);
  if (fade > 0) { g.fillStyle = `rgba(0,0,0,${fade})`; g.fillRect(0, 0, W, H); }
}

window.ENGINE = { W, H, S, V,
  ready: fontsReady.then(() => { buildTimeline(); paginate();
    const bad = FONTS.flatMap(([fam, , ws]) => ws.filter(w => !document.fonts.check(`${w} 40px '${fam}'`, TRS)).map(w => fam + ' ' + w));
    return { dur: EP.dur, fps: 30, fontsMissing: bad, segs: EP.segs.map(s => [+s.t0.toFixed(2), +s.t1.toFixed(2)]), scenes: EP.scenes.map(s => [s.type, +s.t0.toFixed(2), +s.t1.toFixed(2)]) }; }),
  render,
  frame: (T, q = .93) => { render(T); return cv.toDataURL('image/jpeg', q).slice(23); },
};
const T0 = Q.get('T'); if (T0 != null) window.ENGINE.ready.then(() => render(+T0));
})();
