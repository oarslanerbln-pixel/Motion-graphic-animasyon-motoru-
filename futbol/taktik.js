// 09 — Taktik Tahta (Gece Maçı) · deterministik render(T) motoru
// Görsel dil: gece stadı, projektör hüzmeleri ve toz, perspektifli cam saha,
// ışıklı oyuncu jetonları, pas izleri, pres ısı bölgeleri, kinetik tipografi, karaoke altyazı.
(() => {
'use strict';
const Q = new URLSearchParams(location.search);
const W = +Q.get('w') || 1920, H = +Q.get('h') || 1080, S = +(Q.get('s') || 1);
const V = H > W;                          // dikey mi
const U = Math.min(W, H) / 1080;          // ölçek birimi
const EP = window.EP;
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

// ---------- arka plan: gece stadı + projektörler + toz ----------
const DUST = (() => { const r = rng(11), a = []; for (let i = 0; i < 260; i++) a.push({ x: r(), y: r(), z: .3 + r() * .7, ph: r() * 6.28, sp: .004 + r() * .012 }); return a; })();
function beams(T, inten) {
  const src = [[-.06 * W, -.10 * H, 1], [1.06 * W, -.10 * H, -1]];
  const L = Math.hypot(W, H) * 1.5;
  g.save(); g.globalCompositeOperation = 'lighter';
  const axes = [];
  for (const [sx, sy, sd] of src) {
    const base = Math.atan2(H * .62 - sy, W * .5 - sx);
    const ang = base + Math.sin(T * .23 + sd) * .035;
    axes.push([sx, sy, ang]);
    for (const [hw, al] of [[.20, .05], [.11, .07], [.05, .09]]) {
      const a1 = ang - hw, a2 = ang + hw;
      const gr = g.createLinearGradient(sx, sy, sx + Math.cos(ang) * L * .7, sy + Math.sin(ang) * L * .7);
      gr.addColorStop(0, `rgba(205,225,255,${al * inten})`); gr.addColorStop(1, 'rgba(205,225,255,0)');
      g.fillStyle = gr; g.beginPath(); g.moveTo(sx, sy);
      g.lineTo(sx + Math.cos(a1) * L, sy + Math.sin(a1) * L); g.lineTo(sx + Math.cos(a2) * L, sy + Math.sin(a2) * L); g.closePath(); g.fill();
    }
    const rg = g.createRadialGradient(sx + sd * W * .04, sy + H * .06, 0, sx + sd * W * .04, sy + H * .06, 260 * U);
    rg.addColorStop(0, `rgba(235,242,255,${.55 * inten})`); rg.addColorStop(1, 'rgba(235,242,255,0)');
    g.fillStyle = rg; g.fillRect(0, 0, W, H);
  }
  // ışıkta asılı toz
  for (const d of DUST) {
    const x = ((d.x + Math.sin(T * .1 + d.ph) * .01) % 1) * W;
    const y = (((d.y - T * d.sp) % 1) + 1) % 1 * H;
    let lit = 0;
    for (const [sx, sy, ang] of axes) { const a = Math.atan2(y - sy, x - sx); lit = Math.max(lit, cl(1 - Math.abs(a - ang) / .16)); }
    if (lit <= 0) continue;
    g.fillStyle = `rgba(230,238,255,${.35 * lit * d.z * inten})`;
    g.beginPath(); g.arc(x, y, (1 + d.z * 1.6) * U, 0, 6.283); g.fill();
  }
  g.restore();
}
function bg(T) {
  const gr = g.createRadialGradient(W * .5, H * .42, 0, W * .5, H * .5, Math.hypot(W, H) * .65);
  gr.addColorStop(0, '#111B2C'); gr.addColorStop(.55, '#070B14'); gr.addColorStop(1, '#020306');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  // uzak tribün ışıkları: yatay bant halinde yumuşak noktalar
  const r = rng(3); g.save(); g.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 90; i++) {
    const x = r() * W, y = H * (.16 + r() * .1), tw = .5 + .5 * Math.sin(T * (1 + r() * 2) + i);
    g.fillStyle = `rgba(255,${200 + r() * 55 | 0},${150 + r() * 80 | 0},${.05 + .06 * tw})`;
    g.beginPath(); g.arc(x, y, (2 + r() * 4) * U, 0, 6.283); g.fill();
  }
  g.restore();
}
function vignette() {
  const gr = g.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .35, W / 2, H / 2, Math.hypot(W, H) * .62);
  gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,.62)');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
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
  g.save(); g.globalAlpha = a;
  const x = V ? W / 2 : 64 * U, y = V ? 130 * U : 70 * U;
  g.font = F(800, (V ? 30 : 24) * U, 'Unbounded'); g.letterSpacing = 3 * U + 'px'; g.textAlign = V ? 'center' : 'left';
  g.fillStyle = '#F2F4F7'; g.fillText(EP.brand, x, y);
  const w = g.measureText(EP.brand).width;
  const dx = V ? x + w / 2 + 16 * U : x + w + 16 * U;
  g.fillStyle = '#F4C653'; g.beginPath(); g.arc(dx, y - 8 * U, 5 * U * (.8 + .2 * Math.sin(T * 3)), 0, 6.283); g.fill();
  g.restore();
}

// ---------- saha projeksiyonu ----------
// Dünya: X ∈ [-52.5, 52.5] (boy), Y ∈ [-34, 34] (en), metre.
const CAM = { tilt: .9, yaw: 0, k: 1, cx: W / 2, cy: H / 2, d: 1400 };
function proj(X, Y) {
  let x = V ? Y : X, y = V ? -X : Y;                 // dikeyde hücum yukarı
  const c = Math.cos(CAM.yaw), s = Math.sin(CAM.yaw);
  const xr = x * c - y * s, yr = x * s + y * c;
  const px = xr * CAM.k, py = yr * CAM.k;
  const z = -py * Math.sin(CAM.tilt);               // ekranda yukarısı uzak
  const sc = CAM.d / (CAM.d + z);
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
function drawPitch(a, draw) {
  g.save(); g.globalAlpha = a;
  // zemin + biçme şeritleri
  for (let i = 0; i < 14; i++) {
    const x0 = -52.5 + i * 7.5;
    polyW([[x0, -34], [x0 + 7.5, -34], [x0 + 7.5, 34], [x0, 34]], true);
    g.fillStyle = i % 2 ? 'rgba(18,58,44,.92)' : 'rgba(14,48,37,.92)'; g.fill();
  }
  // projektör ışık havuzları (zeminde)
  const [cx, cy] = proj(0, 0);
  const rg = g.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W, H) * .55);
  rg.addColorStop(0, 'rgba(160,255,210,.10)'); rg.addColorStop(1, 'rgba(0,0,0,.35)');
  polyW([[-52.5, -34], [52.5, -34], [52.5, 34], [-52.5, 34]], true); g.fillStyle = rg; g.fill();
  // çizgiler: çizim animasyonu (draw 0→1) + iki katmanlı glow
  g.lineCap = 'round'; g.lineJoin = 'round';
  for (const [lw, al] of [[7 * U, .10], [2.2 * U, .85]]) {
    g.strokeStyle = `rgba(214,255,236,${al})`; g.lineWidth = lw;
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
function token(X, Y, team, num, label, sz, a, hl = 0) {
  if (a <= 0) return;
  const [x, y, sc] = proj(X, Y); const r = sz * U * sc;
  g.save(); g.globalAlpha = a;
  // zemin gölgesi
  g.fillStyle = 'rgba(0,0,0,.45)'; g.beginPath(); g.ellipse(x + r * .25, y + r * .35, r * 1.15, r * 1.15 * Math.cos(CAM.tilt) * .9, 0, 0, 6.283); g.fill();
  // ışık halesi
  if (hl > 0) { g.globalCompositeOperation = 'lighter'; const rg = g.createRadialGradient(x, y, r * .5, x, y, r * 3.2);
    rg.addColorStop(0, hexA(team.ring, .45 * hl)); rg.addColorStop(1, hexA(team.ring, 0)); g.fillStyle = rg; g.beginPath(); g.arc(x, y, r * 3.2, 0, 6.283); g.fill(); g.globalCompositeOperation = 'source-over'; }
  const yy = y - r * .55;   // hafif yükselti
  const gr = g.createLinearGradient(x, yy - r, x, yy + r);
  gr.addColorStop(0, team.c1); gr.addColorStop(1, hexA(team.c1, .78));
  g.fillStyle = gr; g.beginPath(); g.arc(x, yy, r, 0, 6.283); g.fill();
  g.lineWidth = 2.2 * U * sc; g.strokeStyle = team.c2 === '#0B0B0C' ? 'rgba(0,0,0,.85)' : hexA(team.c2, .9); g.stroke();
  g.lineWidth = 1.2 * U * sc; g.strokeStyle = hexA(team.ring, .7); g.beginPath(); g.arc(x, yy, r * 1.22, 0, 6.283); g.stroke();
  if (num != null) {
    g.fillStyle = team.c2; g.font = F(800, r * 1.05); g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(String(num), x, yy + r * .06);
  }
  if (label) {
    g.font = F(700, 16 * U * sc, 'JetBrains Mono'); g.textBaseline = 'middle';
    const tw = g.measureText(label).width + 14 * U * sc, ly = yy + r * 2.05;
    g.fillStyle = 'rgba(4,8,14,.72)'; rrect(x - tw / 2, ly - 11 * U * sc, tw, 22 * U * sc, 11 * U * sc); g.fill();
    g.fillStyle = '#E8EEF5'; g.fillText(label, x, ly + 1);
  }
  g.restore();
}
// dünya uzayında eğri ok (pas/koşu). p: çizim ilerlemesi, dash: koşu çizgisi
function arrowW(A, B, bend, col, p, dash, wpx = 4) {
  if (p <= 0) return;
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
  // uç: ışıklı kafa
  const [hx, hy] = pts[pts.length - 1], [qx, qy] = pts[Math.max(0, pts.length - 3)];
  const an = Math.atan2(hy - qy, hx - qx), hs = 13 * U;
  g.setLineDash([]); g.globalCompositeOperation = 'source-over'; g.fillStyle = col;
  g.beginPath(); g.moveTo(hx + Math.cos(an) * hs, hy + Math.sin(an) * hs);
  g.lineTo(hx + Math.cos(an + 2.5) * hs, hy + Math.sin(an + 2.5) * hs); g.lineTo(hx + Math.cos(an - 2.5) * hs, hy + Math.sin(an - 2.5) * hs); g.closePath(); g.fill();
  g.restore();
}
function ball(X, Y, a) {
  const [x, y, sc] = proj(X, Y); g.save(); g.globalAlpha = a; g.globalCompositeOperation = 'lighter';
  const rg = g.createRadialGradient(x, y - 6 * U, 0, x, y - 6 * U, 26 * U * sc);
  rg.addColorStop(0, 'rgba(255,255,255,.95)'); rg.addColorStop(.25, 'rgba(255,250,220,.5)'); rg.addColorStop(1, 'rgba(255,250,220,0)');
  g.fillStyle = rg; g.beginPath(); g.arc(x, y - 6 * U, 26 * U * sc, 0, 6.283); g.fill(); g.restore();
}

// ---------- sahneler ----------
const SC = {};
SC.intro = (c) => {
  const { lt, a } = c, H2 = EP.home, A2 = EP.away;
  g.save(); g.globalAlpha = a;
  const push = 1.06 - .06 * eOut(cl(lt / 6));
  g.translate(W / 2, H / 2); g.scale(push, push); g.translate(-W / 2, -H / 2);
  const kp = win(lt, .15, 1.0);
  if (V) {
    maskText(EP.kicker, W / 2, H * .30, F(500, 26 * U, 'JetBrains Mono'), '#9FB3C8', kp, 'center', 4 * U);
    maskText(H2.name, W / 2, H * .42, F(800, 118 * U, 'Unbounded'), H2.c1, win(lt, .35, 1.3));
    const dp = eOut(win(lt, .8, 1.6));
    g.fillStyle = '#F4C653'; g.globalAlpha = a * dp; g.font = F(300, 70 * U, 'Unbounded'); g.textAlign = 'center'; g.fillText('×', W / 2, H * .49);
    g.globalAlpha = a;
    A2.lines.forEach((l, i) => maskText(l, W / 2, H * (.565 + i * .065), F(800, 92 * U, 'Unbounded'), '#FFFFFF', win(lt, .95 + i * .18, 1.9 + i * .18)));
    // kulüp renk çubukları
    const bw = 420 * U * eExpo(win(lt, .6, 1.6));
    g.fillStyle = H2.c1; g.fillRect(W / 2 - bw / 2, H * .438, bw, 5 * U);
    g.fillStyle = A2.c1; g.fillRect(W / 2 - bw / 2, H * .66, bw, 5 * U);
  } else {
    maskText(EP.kicker, W / 2, H * .24, F(500, 24 * U, 'JetBrains Mono'), '#9FB3C8', kp, 'center', 5 * U);
    const gap = 70 * U;
    maskText(H2.name, W / 2 - gap, H * .53, F(800, 104 * U, 'Unbounded'), H2.c1, win(lt, .35, 1.3), 'right');
    A2.lines.forEach((l, i) => maskText(l, W / 2 + gap, H * (.47 + i * .115), F(800, 72 * U, 'Unbounded'), '#FFFFFF', win(lt, .7 + i * .18, 1.6 + i * .18), 'left'));
    const lp = eExpo(win(lt, .5, 1.5)), lh = 260 * U * lp;
    const lg = g.createLinearGradient(0, H * .5 - lh / 2, 0, H * .5 + lh / 2);
    lg.addColorStop(0, 'rgba(244,198,83,0)'); lg.addColorStop(.5, 'rgba(244,198,83,1)'); lg.addColorStop(1, 'rgba(244,198,83,0)');
    g.fillStyle = lg; g.fillRect(W / 2 - 1.5 * U, H * .5 - lh / 2, 3 * U, lh);
    const bw = 360 * U * eExpo(win(lt, .7, 1.7));
    g.fillStyle = H2.c1; g.fillRect(W / 2 - gap - bw, H * .565, bw, 5 * U);
    g.fillStyle = A2.c1; g.fillRect(W / 2 + gap, H * .64, bw, 5 * U);
  }
  // alt bilgi şeridi
  const ip = win(lt, 1.6, 2.6);
  maskText('26 KASIM · 20:45 TSİ · BATUM', W / 2, V ? H * .75 : H * .76, F(700, (V ? 30 : 26) * U), '#C9D6E3', ip, 'center', 3 * U);
  g.restore();
};
SC.card = (c) => {
  const { lt, a, sc } = c;
  g.save(); g.globalAlpha = a;
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
    g.fillStyle = '#8EA3B8'; g.font = F(500, 19 * U, 'JetBrains Mono'); g.fillText(t.k, cx + 30 * U, cy + 46 * U);
    g.letterSpacing = '0px'; g.fillStyle = '#FFFFFF'; g.font = F(800, (V ? 58 : 50) * U); g.fillText(t.v, cx + 30 * U, cy + (V ? 118 : 106) * U);
    g.fillStyle = t.s.includes('DOĞRULA') ? '#FF9A9A' : '#B9C7D6'; g.font = F(500, 21 * U); g.fillText(t.s, cx + 30 * U, cy + (V ? 160 : 142) * U);
    g.restore();
  });
  // rota bandı: İstanbul → Batum
  const r = sc.route, rp = eIO(win(lt, 1.3, 2.6));
  if (rp > 0) {
    const rows = Math.ceil(tiles.length / cols);
    const by = y0 + rows * (th + gy) + (V ? 150 : 120) * U, bx0 = x0 + 40 * U, bx1 = x0 + cols * tw + (cols - 1) * gx - 40 * U;
    const arcH = (V ? 70 : 45) * U;
    g.save(); g.globalAlpha = a; g.lineCap = 'round';
    g.strokeStyle = 'rgba(244,198,83,.95)'; g.lineWidth = 3 * U; g.setLineDash([2 * U, 9 * U]);
    g.beginPath(); for (let i = 0; i <= 60 * rp; i++) { const t = i / 60, x = lerp(bx0, bx1, t), y = by - Math.sin(t * Math.PI) * arcH; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
    g.setLineDash([]);
    for (const [t, lab, al] of [[0, r.a, 'left'], [1, r.b, 'right']]) {
      const vis = t === 0 ? 1 : cl((rp - .95) * 20); if (vis <= 0) continue;
      const x = lerp(bx0, bx1, t); g.globalAlpha = a * vis;
      g.fillStyle = '#F4C653'; g.beginPath(); g.arc(x, by, 8 * U, 0, 6.283); g.fill();
      g.font = F(700, 22 * U, 'JetBrains Mono'); g.letterSpacing = 2 * U + 'px'; g.textAlign = al; g.fillStyle = '#E8EEF5';
      g.fillText(lab, x, by + 42 * U);
    }
    g.globalAlpha = a * cl((rp - .5) * 3); g.textAlign = 'center'; g.letterSpacing = '0px';
    g.font = F(800, 30 * U); g.fillStyle = '#FFFFFF'; g.fillText(r.km, (bx0 + bx1) / 2, by - arcH - 22 * U);
    g.font = F(500, 21 * U); g.fillStyle = '#B9C7D6'; g.fillText(r.note, (bx0 + bx1) / 2, by + 42 * U);
    g.restore();
  }
  g.restore();
};
SC.tactic = (c) => {
  const { lt, a, sc, T } = c, si = sc.seg[0];
  // kamera: yukarıdan → eğik, yavaş yaw salınımı
  const cp = eIO(win(lt, 0, 1.8));
  CAM.tilt = lerp(.12, V ? .92 : .98, cp);
  CAM.yaw = Math.sin(lt * .35) * .045 * cp + (1 - cp) * (V ? .25 : -.18);
  CAM.k = V ? W * .64 / 68 : W * .60 / 105;
  CAM.cx = W / 2; CAM.cy = V ? H * .465 : H * .50;
  g.save(); g.globalAlpha = a;
  drawPitch(1, win(lt, .1, 1.6));
  const t1 = wT(si, sc.steps[0].w), t2 = wT(si, sc.steps[1].w), t3 = wT(si, sc.steps[2].w);
  const press = eIO(win(T, t3, t3 + 1.0));
  // pres ısı bölgesi
  if (press > 0) { heat(...P(.84, .5), 26, '#F4C653', press * .9); heat(...P(.78, .2), 14, '#F4C653', press * .5); heat(...P(.78, .8), 14, '#F4C653', press * .5); }
  // rakip (soluk)
  const oa = win(lt, 1.2, 2.0) * (1 - .45 * press);
  EP.opp.forEach(([x, y], i) => token(...P(x, y), EP.away, null, null, V ? 10 : 9, oa * .55 * cl(win(lt, 1.2 + i * .03, 1.6 + i * .03) * 2)));
  // ev sahibi: diziliş ve pres şekli arasında geçiş
  const home = EP.lineup.map(p => P(lerp(p.x, p.px, press), lerp(p.y, p.py, press)));
  // 1) kanat bindirmesi: bekler koşu, kanatlar içe kat
  const k1 = win(T, t1, t1 + 1.1);
  EP.lineup.forEach((p, i) => {
    if (p.run) arrowW(home[i], P(...p.run), V ? -.18 * (p.y > .5 ? -1 : 1) : .18 * (p.y > .5 ? -1 : 1), '#7FE3FF', eOut(k1) * (1 - press), true, 3.2);
    if (p.cut) arrowW(home[i], P(...p.cut), 0, '#FFFFFF', eOut(win(T, t1 + .4, t1 + 1.3)) * (1 - press), false, 3);
  });
  // 2) sabırlı pas zinciri + top
  const k2 = win(T, t2, t2 + 1.8);
  EP.passes.forEach(([i0, i1], j) => {
    const pp = cl(k2 * EP.passes.length - j);
    arrowW(home[i0], home[i1], .12, '#F4C653', eOut(pp) * (1 - press * .8), false, 3.6);
  });
  if (k2 > 0 && press < 1) {
    const f = cl(k2 * EP.passes.length, 0, EP.passes.length - 1e-6), j = Math.floor(f), u = eIO(f - j);
    const [i0, i1] = EP.passes[j]; ball(lerp(home[i0][0], home[i1][0], u), lerp(home[i0][1], home[i1][1], u), 1 - press);
  }
  EP.lineup.forEach((p, i) => {
    const ap = eBack(win(lt, .4 + i * .07, .9 + i * .07));
    const hl = (p.run && k1 > 0 && k1 < 1) || (EP.passes.some(q => q.includes(i)) && k2 > 0 && k2 < 1) ? .8 : press * .5;
    token(home[i][0], home[i][1], EP.home, p.n, p.nm, (V ? 21 : 19) * cl(ap, 0, 1.2), cl(ap * 2), hl);
  });
  // başlık + adım etiketi
  const hy = V ? H * .14 : H * .165, hx = V ? W / 2 : 120 * U, al = V ? 'center' : 'left';
  maskText('OYUN PLANI', hx, hy, F(800, (V ? 50 : 42) * U, 'Unbounded'), '#FFFFFF', win(lt, .2, 1), al, 2 * U);
  maskText(sc.formation, V ? W / 2 : hx + 430 * U, V ? hy + 56 * U : hy, F(300, (V ? 40 : 42) * U, 'Unbounded'), '#F4C653', win(lt, .5, 1.3), V ? 'center' : 'left');
  const ts = [t1, t2, t3], cur = ts.filter(t => T >= t - .1).length - 1;
  if (cur >= 0) {
    const sp = win(T, ts[cur] - .1, ts[cur] + .5), lab = `${cur + 1} · ${sc.steps[cur].label}`;
    g.font = F(700, 24 * U, 'JetBrains Mono'); g.letterSpacing = 3 * U + 'px';
    const tw = g.measureText(lab).width + 44 * U, bx = V ? W / 2 - tw / 2 : hx, by = V ? hy + 96 * U : hy + 32 * U;
    g.save(); g.globalAlpha = a * eOut(sp);
    rrect(bx, by, tw, 46 * U, 23 * U); g.fillStyle = 'rgba(244,198,83,.14)'; g.fill(); g.strokeStyle = 'rgba(244,198,83,.7)'; g.lineWidth = 1.4 * U; g.stroke();
    g.fillStyle = '#F4C653'; g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillText(lab, bx + 22 * U, by + 24 * U);
    g.restore();
  }
  // pres sayacı halkası
  if (press > 0) {
    const [x, y] = proj(...P(.84, .5)); const tp = cl((T - t3 - .3) / 5);
    g.save(); g.globalAlpha = a * press; g.lineCap = 'round';
    g.strokeStyle = 'rgba(255,255,255,.18)'; g.lineWidth = 6 * U; g.beginPath(); g.arc(x, y - 150 * U, 44 * U, 0, 6.283); g.stroke();
    g.strokeStyle = '#F4C653'; g.beginPath(); g.arc(x, y - 150 * U, 44 * U, -Math.PI / 2, -Math.PI / 2 + 6.283 * (1 - tp)); g.stroke();
    g.fillStyle = '#FFF'; g.font = F(800, 32 * U); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(Math.max(0, Math.ceil(5 - tp * 5)) + 'sn', x, y - 148 * U);
    g.restore();
  }
  g.restore();
};
SC.scen = (c) => {
  const { lt, a, sc, T } = c, si = sc.seg[0];
  g.save(); g.globalAlpha = a;
  maskText('3 SENARYO', V ? W / 2 : 120 * U, V ? H * .17 : H * .17, F(800, (V ? 54 : 46) * U, 'Unbounded'), '#FFFFFF', win(lt, 0, .8), V ? 'center' : 'left', 2 * U);
  maskText('kanal tahmini · kesinlik değil', V ? W / 2 : 120 * U, V ? H * .17 + 50 * U : H * .17 + 44 * U, F(500, 22 * U, 'JetBrains Mono'), '#8EA3B8', win(lt, .3, 1.1), V ? 'center' : 'left', 1 * U);
  const n = sc.items.length, cw = V ? 900 * U : 520 * U, ch = V ? 250 * U : 430 * U, gp = 30 * U;
  const x0 = V ? (W - cw) / 2 : (W - (n * cw + (n - 1) * gp)) / 2, y0 = V ? H * .24 : H * .29;
  const hot = sc.items.findIndex(it => it.w && T >= wT(si, it.w));
  sc.items.forEach((it, i) => {
    const p = eOut(win(lt, .3 + i * .18, 1.2 + i * .18)); if (p <= 0) return;
    const x = V ? x0 : x0 + i * (cw + gp), y = (V ? y0 + i * (ch + gp) : y0) + (1 - p) * 50 * U;
    const isHot = i === hot, hp = isHot ? eOut(win(T, wT(si, it.w), wT(si, it.w) + .6)) : 0;
    g.save(); g.globalAlpha = a * p * (hot >= 0 && !isHot ? .55 : 1);
    glass(x, y, cw, ch, 26 * U, 1, isHot ? it.c : '#FFFFFF');
    if (hp > 0) { rrect(x, y, cw, ch, 26 * U); g.strokeStyle = hexA(it.c, .9 * hp); g.lineWidth = 2.5 * U; g.stroke(); }
    const pad = 36 * U;
    g.textAlign = 'left'; g.fillStyle = it.c; g.font = F(300, 40 * U, 'Unbounded'); g.fillText('0' + (i + 1), x + pad, y + 70 * U);
    g.fillStyle = '#FFFFFF'; g.font = F(800, (V ? 46 : 40) * U); g.fillText(it.t, x + pad + (V ? 100 * U : 0), y + (V ? 70 : 140) * U);
    g.fillStyle = '#B9C7D6'; g.font = F(500, (V ? 26 : 24) * U); g.fillText(it.d, x + pad + (V ? 100 * U : 0), y + (V ? 112 : 186) * U);
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
  maskText('LİGİ', W / 2, ty + (V ? 130 : 115) * U, F(300, (V ? 120 : 110) * U, 'Unbounded'), '#F4C653', win(lt, .2, 1.1));
  // skor kutuları
  const bp = eBack(win(lt, .8, 1.6)), bs = (V ? 150 : 130) * U, by = V ? H * .45 : H * .52;
  const items = [[H2.short, -1], [A2.short, 1]];
  items.forEach(([lab, sd]) => {
    const x = W / 2 + sd * (bs * .5 + 40 * U) - bs / 2;
    g.save(); g.globalAlpha = a * cl(bp); g.translate(x + bs / 2, by + bs / 2); g.scale(cl(bp, 0, 1.2), cl(bp, 0, 1.2)); g.translate(-bs / 2, -bs / 2);
    glass(0, 0, bs, bs, 24 * U, 1);
    const pul = .75 + .25 * Math.sin(T * 4 + sd);
    g.fillStyle = '#F4C653'; g.globalAlpha *= pul; g.font = F(800, bs * .55); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('?', bs / 2, bs * .52); g.globalAlpha /= pul;
    g.fillStyle = '#9FB3C8'; g.font = F(700, 24 * U, 'JetBrains Mono'); g.letterSpacing = 3 * U + 'px'; g.fillText(lab, bs / 2, bs + 34 * U);
    g.restore();
  });
  g.save(); g.globalAlpha = a * cl(bp); g.fillStyle = '#FFFFFF'; g.font = F(300, 70 * U, 'Unbounded'); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('–', W / 2, by + bs / 2); g.restore();
  maskText('Yorumlara yaz · sıralama bir sonraki bölümde', W / 2, by + bs + (V ? 120 : 100) * U, F(700, (V ? 32 : 28) * U), '#C9D6E3', win(lt, 1.4, 2.3));
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

// ---------- ana render ----------
function render(T) {
  g.setTransform(S, 0, 0, S, 0, 0);
  g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
  bg(T);
  const tac = EP.scenes.find(s => s.type === 'tactic');
  const inTac = tac ? win(T, tac.t0, tac.t0 + .6) * (1 - win(T, tac.t1, tac.t1 + .6)) : 0;
  beams(T, 1 - .35 * inTac);
  for (const sc of EP.scenes) {
    const fo = .55; if (T < sc.t0 || T > sc.t1 + fo) continue;
    const a = (sc.t0 === 0 ? 1 : eOut(win(T, sc.t0, sc.t0 + .5))) * (1 - eIO(win(T, sc.t1, sc.t1 + fo)));
    if (a <= 0) continue;
    SC[sc.type]({ T, lt: T - sc.t0, d: sc.t1 - sc.t0, a, sc });
  }
  brandBug(T, win(T, .3, 1.2) * (1 - win(T, EP.dur - .8, EP.dur)));
  subtitles(T);
  vignette();
  // tane + sona doğru karartma
  g.save(); g.globalAlpha = .06; g.globalCompositeOperation = 'overlay';
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
