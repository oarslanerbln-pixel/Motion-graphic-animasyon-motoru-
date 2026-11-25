"""Shot listesi → kare. Geçişler, hız rampaları, paneller, metin blokları."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
import lib


# --------------------------------------------------------------- zaman eşleme
def src_time(sh, u):
    s0, s1 = sh['src']
    k = sh.get('ramp', 0.0)
    kind = sh.get('ramp_kind', 'out')
    if kind == 'out':      # hızlı başla, yavaşla
        e = (1 - k) * u + k * (1 - (1 - u) ** 2)
    elif kind == 'in':     # yavaş başla, hızlan
        e = (1 - k) * u + k * u * u
    elif kind == 'mid':    # hızlı-yavaş-hızlı (klasik speed ramp)
        e = (1 - k) * u + k * (0.5 + 0.5 * (2 * u - 1) ** 3)
    else:
        e = u
    return s0 + (s1 - s0) * e


def lerp(a, b, u):
    return a + (b - a) * u


class Engine:
    def __init__(self, src, W, H, shots, grade, overlay, pulse=None, clip_fx=None):
        self.clip_fx = clip_fx
        self.src, self.W, self.H = src, W, H
        self.shots = sorted(shots, key=lambda s: s['t0'])
        self.grade, self.overlay = grade, overlay
        self.pulse = pulse or (lambda t: 0.0)

    # ---------------------------------------------------------- tek shot
    def shot_img(self, sh, t, W=None, H=None, extra_zoom=1.0, extra_dx=0.0):
        W = W or self.W; H = H or self.H
        if sh.get('black'):
            return np.zeros((H, W, 3), np.float32) + np.array(sh.get('color', (0, 0, 0)), np.float32)
        if 'panels' in sh:
            return self.panels(sh, t, W, H)
        c = lib.load(sh['clip'], self.src, *self.fmt_key())
        d = sh['t1'] - sh['t0']
        u = (t - sh['t0']) / d
        uc = min(max(u, 0), 1)
        st = src_time(sh, u)
        if 'freeze' in sh and t >= sh['freeze']:
            st = src_time(sh, (sh['freeze'] - sh['t0']) / d)
        e = lib.ease_io(uc) if sh.get('cam_ease', True) else uc
        z = lerp(sh.get('z0', 1.0), sh.get('z1', sh.get('z0', 1.0)), e) * extra_zoom
        dx = lerp(sh.get('dx0', 0.0), sh.get('dx1', sh.get('dx0', 0.0)), e) + extra_dx
        dy = lerp(sh.get('dy0', 0.0), sh.get('dy1', sh.get('dy0', 0.0)), e)
        rot = lerp(sh.get('r0', 0.0), sh.get('r1', sh.get('r0', 0.0)), e)
        img = c.frame(st)
        fx, fy = sh.get('fx'), sh.get('fy')
        if self.W > self.H:                    # yatay çıktı için ayrı odak
            fx = sh.get('hfx', fx); fy = sh.get('hfy', lib.CLIPS[c.id].get('hfy', fy))
            if c.h > c.w:                      # dikey kaynak yatayda zaten sıkı: zoom'u yumuşat
                z = 1 + (z - 1) * 0.45
        out = lib.place(img, c, st, W, H, z, dx, dy, rot, fx, fy)
        if self.clip_fx:
            out = self.clip_fx(out, c.id)
        return out

    def fmt_key(self):
        return (self.W, self.H)

    def panels(self, sh, t, W, H):
        out = np.zeros((H, W, 3), np.float32) + np.array(sh.get('bg', (0.94, 0.93, 0.9)), np.float32)
        gap = sh.get('gap', 0)
        for p in sh['panels']:
            x0, y0, x1, y1 = p['rect']             # normalize
            if (self.W > self.H) and 'hrect' in p:
                x0, y0, x1, y1 = p['hrect']
            # panel açılış animasyonu
            u = (t - sh['t0'] - p.get('delay', 0)) / max(p.get('in', 0.25), 1e-3)
            a = lib.ease_out_expo(u)
            if a <= 0:
                continue
            px0, py0 = int(x0 * W) + gap, int(y0 * H) + gap
            px1, py1 = int(x1 * W) - gap, int(y1 * H) - gap
            pw, ph = px1 - px0, py1 - py0
            sub = dict(p, t0=sh['t0'], t1=sh['t1'])
            img = self.shot_img(sub, t, pw, ph, extra_zoom=1 + 0.15 * (1 - a))
            # alttan maske ile kayarak açılış
            vis = int(ph * a)
            if vis <= 0:
                continue
            out[py1 - vis:py1, px0:px1] = img[ph - vis:ph]
        return out

    # ---------------------------------------------------------- geçişler
    def active(self, t):
        cur = None
        for i, s in enumerate(self.shots):
            if s['t0'] <= t < s['t1']:
                cur = i
        if cur is None:
            cur = len(self.shots) - 1 if t >= self.shots[-1]['t0'] else 0
        return cur

    def frame(self, t, fi=0):
        i = self.active(t)
        sh = self.shots[i]
        prev = self.shots[i - 1] if i > 0 else None
        tin = sh.get('tin', 'cut'); td = sh.get('td', 0.18)
        lt = t - sh['t0']
        pz = 1 + self.pulse(t)
        if tin == 'cut' or (prev is None and tin != 'dip') or lt >= td:
            img = self.shot_img(sh, t, extra_zoom=pz)
            # çıkış (sonraki shot'ın whip'i varsa giden de bulanıklaşır)
            nxt = self.shots[i + 1] if i + 1 < len(self.shots) else None
            if nxt is not None and nxt.get('tin') in ('whip', 'whipv') and sh['t1'] - t < nxt.get('td', 0.18) * 0.5:
                v = 1 - (sh['t1'] - t) / (nxt.get('td', 0.18) * 0.5)
                d = self.W * 0.35 * v * v
                if nxt['tin'] == 'whip':
                    img = lib.dir_blur(img, d, 0, 11)
                else:
                    img = lib.dir_blur(img, 0, d, 11)
            if nxt is not None and nxt.get('tin') == 'zoom' and sh['t1'] - t < 0.12:
                v = 1 - (sh['t1'] - t) / 0.12
                img = lib.radial_blur(self.shot_img(sh, t, extra_zoom=pz * (1 + 0.25 * v * v)), 0.25 * v, n=10)
        else:
            u = lt / td
            if tin == 'xfade':
                a = lib.ease_io(u)
                img = self.shot_img(prev, t, extra_zoom=pz) * (1 - a) + self.shot_img(sh, t, extra_zoom=pz) * a
            elif tin == 'dip':
                a = lib.ease_io(u)
                img = self.shot_img(sh, t, extra_zoom=pz) * a
            elif tin == 'zoom':
                v = 1 - lib.ease_out_cubic(u)
                img = self.shot_img(sh, t, extra_zoom=pz * (1 + 0.3 * v))
                img = lib.radial_blur(img, 0.3 * v, n=10)
            elif tin in ('whip', 'whipv'):
                v = 1 - lib.ease_out_cubic(u)
                d = self.W * 0.35 * v
                if tin == 'whip':
                    img = self.shot_img(sh, t, extra_zoom=pz, extra_dx=0.0)
                    M = np.float32([[1, 0, d * 0.25], [0, 1, 0]])
                    img = cv2.warpAffine(img, M, (self.W, self.H), borderMode=cv2.BORDER_REFLECT)
                    img = lib.dir_blur(img, d, 0, 11)
                else:
                    img = self.shot_img(sh, t, extra_zoom=pz)
                    M = np.float32([[1, 0, 0], [0, 1, d * 0.25]])
                    img = cv2.warpAffine(img, M, (self.W, self.H), borderMode=cv2.BORDER_REFLECT)
                    img = lib.dir_blur(img, 0, d, 11)
            elif tin == 'flash':
                a = 1 - lib.ease_out_cubic(u)
                img = self.shot_img(sh, t, extra_zoom=pz * (1 + 0.06 * a))
                img = img + a * 0.55
            else:
                img = self.shot_img(sh, t, extra_zoom=pz)
        if sh.get('fade_out'):
            fo = sh['fade_out']
            a = min(max((sh['t1'] - t) / fo, 0), 1)
            img = img * lib.ease_io(a)
        img = self.grade(img, t, sh)
        img = self.overlay(img, t, fi)
        return img


# ------------------------------------------------------------- metin blokları
class TextBlock:
    """Bir kez render edilen metin yaması; konum/opaklık/maske/bulanıklık ile çizilir."""

    def __init__(self, text, fnt, color=(1, 1, 1), tracking=0, pad=40, stroke=0, stroke_color=None, shadow=0):
        tmp = Image.new('L', (10, 10)); d = ImageDraw.Draw(tmp)
        widths = [d.textlength(ch, font=fnt) for ch in text]
        total = sum(widths) + tracking * max(len(text) - 1, 0)
        asc, desc = fnt.getmetrics()
        Wp, Hp = int(total + 2 * pad), int(asc + desc + 2 * pad)
        im = Image.new('L', (Wp, Hp), 0); d = ImageDraw.Draw(im)
        x = pad
        for ch, w in zip(text, widths):
            d.text((x, pad), ch, font=fnt, fill=255, stroke_width=stroke, stroke_fill=255)
            x += w + tracking
        a = np.asarray(im).astype(np.float32) / 255
        self.alpha = a
        self.col = np.array(color, np.float32)
        self.h, self.w = a.shape
        self.pad = pad
        self.text_h = asc + desc
        if shadow:
            self.shadow = cv2.GaussianBlur(a, (0, 0), shadow)
        else:
            self.shadow = None
        if stroke and stroke_color == 'outline':
            # yalnızca dış çizgi
            inner = Image.new('L', (Wp, Hp), 0); di = ImageDraw.Draw(inner); x = pad
            for ch, w in zip(text, widths):
                di.text((x, pad), ch, font=fnt, fill=255); x += w + tracking
            ia = np.asarray(inner).astype(np.float32) / 255
            self.alpha = np.clip(a - ia, 0, 1)

    def draw(self, img, cx, cy, opacity=1.0, reveal=1.0, slide=0.0, blur=0.0, scale=1.0,
             color=None, shadow_op=0.0, anchor='m', reveal_dir='up'):
        """reveal: 0..1 maske açılışı (alttan yukarı kayarak), slide: px ek kayma."""
        if opacity <= 0.003:
            return img
        a = self.alpha
        if scale != 1.0:
            a = cv2.resize(a, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        if blur > 0.3:
            a = cv2.GaussianBlur(a, (0, 0), blur)
        h, w = a.shape
        H, W = img.shape[:2]
        x0 = int(round(cx - (w / 2 if anchor == 'm' else (0 if anchor == 'l' else w))))
        y0 = int(round(cy - h / 2))
        if reveal < 1.0:
            # maske kutusu sabit; içerik alttan kayar
            off = int((1 - lib.ease_out_expo(reveal)) * h * 0.75) if reveal_dir == 'up' else 0
            m = np.zeros_like(a)
            if off < h:
                m[: h - off] = a[off:]
            a = m
        if slide:
            y0 += int(slide)
        # kırp
        ax0, ay0 = max(0, -x0), max(0, -y0)
        bx0, by0 = max(0, x0), max(0, y0)
        bx1, by1 = min(W, x0 + w), min(H, y0 + h)
        if bx1 <= bx0 or by1 <= by0:
            return img
        sub = a[ay0:ay0 + by1 - by0, ax0:ax0 + bx1 - bx0][..., None] * opacity
        col = self.col if color is None else np.array(color, np.float32)
        if shadow_op > 0 and self.shadow is not None:
            s = self.shadow
            if scale != 1.0:
                s = cv2.resize(s, (w, h))
            ss = s[ay0:ay0 + by1 - by0, ax0:ax0 + bx1 - bx0][..., None] * opacity * shadow_op
            img[by0:by1, bx0:bx1] *= (1 - ss)
        img[by0:by1, bx0:bx1] = img[by0:by1, bx0:bx1] * (1 - sub) + col * sub
        return img


def env(t, t0, t1, fin=0.35, fout=0.3):
    """t0'da açılır, t1'de kapanır → (reveal 0..1, opaklık)."""
    if t < t0 or t > t1 + fout:
        return 0.0, 0.0
    r = min((t - t0) / fin, 1.0)
    o = 1.0 if t <= t1 else 1 - (t - t1) / fout
    return r, max(0.0, min(1.0, o))
