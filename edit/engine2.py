"""Set 2 motoru: keyframe'li hız rampası + kamera, maske geçişleri (iris, diyagonal,
panjur, harf-matte), özel render shot'ları. Set 1 motorunu genişletir."""
import math, numpy as np, cv2
import lib
from engine import Engine


def interp_keys(keys, u):
    """keys: [(u, değer...)] → ease_io ile parça parça; değer tuple döner."""
    if u <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if u <= b[0]:
            w = lib.ease_io((u - a[0]) / max(b[0] - a[0], 1e-6))
            return tuple(x + (y - x) * w for x, y in zip(a[1:], b[1:]))
    return keys[-1][1:]


def interp_lin(keys, u):
    if u <= keys[0][0]:
        return keys[0][1]
    for a, b in zip(keys, keys[1:]):
        if u <= b[0]:
            w = (u - a[0]) / max(b[0] - a[0], 1e-6)
            return a[1] + (b[1] - a[1]) * w
    return keys[-1][1]


def speed_keys_to_src(sh, u):
    """sh['speed']: [(u, hız)] keyframe'leri → kaynak zamanı (hızın integrali).
    Hız eğrisi yumuşak (smoothstep) interpolasyonlu; src0'dan başlar."""
    if '_lut' not in sh:
        n = 400
        us = np.linspace(0, 1, n)
        sp = np.array([interp_keys([(k[0], k[1]) for k in sh['speed']], x)[0] for x in us])
        d = sh['t1'] - sh['t0']
        cum = np.concatenate([[0], np.cumsum((sp[1:] + sp[:-1]) / 2 * np.diff(us) * d)])
        sh['_lut'] = (us, cum)
    us, cum = sh['_lut']
    return sh['src'][0] + float(np.interp(u, us, cum))


class Engine2(Engine):
    def shot_img(self, sh, t, W=None, H=None, extra_zoom=1.0, extra_dx=0.0):
        W = W or self.W; H = H or self.H
        if 'render' in sh:
            return sh['render'](self, sh, t, W, H)
        if 'speed' not in sh and 'cam' not in sh:
            return super().shot_img(sh, t, W, H, extra_zoom, extra_dx)
        c = lib.load(sh['clip'], self.src, self.W, self.H)
        d = sh['t1'] - sh['t0']
        u = (t - sh['t0']) / d
        st = speed_keys_to_src(sh, min(max(u, -0.5), 1.5)) if 'speed' in sh else sh['src'][0] + (t - sh['t0'])
        z, dx, dy, rot = 1.0, 0.0, 0.0, 0.0
        if 'cam' in sh:
            z, dx, dy, rot = interp_keys(sh['cam'], min(max(u, 0), 1))
        z *= extra_zoom; dx += extra_dx
        fx, fy = sh.get('fx'), sh.get('fy')
        if self.W > self.H:
            fx = sh.get('hfx', fx); fy = sh.get('hfy', lib.CLIPS[c.id].get('hfy', fy))
            if c.h > c.w:
                z = 1 + (z - 1) * 0.45 if z >= 1 else z
        img = c.frame(st)
        out = lib.place(img, c, st, W, H, max(z, 1.0), dx, dy, rot, fx, fy)
        if self.clip_fx:
            out = self.clip_fx(out, c.id)
        return out

    # ------------------------------------------------------------ maskeler
    def mask(self, kind, u, W, H, sh):
        yy, xx = self._grid(W, H)
        soft = sh.get('soft', 0.012) * max(W, H)
        if kind == 'iris':
            cx, cy = sh.get('mc', (0.5, 0.5))
            r = lib.ease_in_expo(u) * 0.3 + lib.ease_out_cubic(u) * 0.75
            r *= math.hypot(W, H)
            d = np.sqrt((xx - cx * W) ** 2 + (yy - cy * H) ** 2)
            return np.clip((r - d) / soft + 0.5, 0, 1)
        if kind == 'diag':
            ang = math.radians(sh.get('mang', 62))
            p = xx * math.cos(ang) + yy * math.sin(ang)
            lo, hi = p.min(), p.max()
            edge = lo + (hi - lo + 2 * soft) * lib.ease_io(u) - soft
            return np.clip((edge - p) / soft + 0.5, 0, 1)
        if kind == 'blinds':
            n = sh.get('mn', 7)
            band = (yy / H * n)
            idx = np.floor(band); f = band - idx
            delay = idx / n * 0.5
            v = np.clip((u - delay) / 0.5, 0, 1)
            v = v * v * (3 - 2 * v)
            return (f < v).astype(np.float32)
        if kind == 'split':   # ortadan iki yana açılan diyagonal yarık
            ang = math.radians(sh.get('mang', 70))
            p = (xx - W / 2) * math.cos(ang) + (yy - H / 2) * math.sin(ang)
            w = lib.ease_io(u) * math.hypot(W, H) * 0.55
            return np.clip((w - np.abs(p)) / soft + 0.5, 0, 1)
        return np.ones((H, W), np.float32)

    def _grid(self, W, H):
        k = (W, H)
        if getattr(self, '_gk', None) != k:
            self._gk = k
            self._g = np.mgrid[0:H, 0:W].astype(np.float32)
        return self._g

    def frame(self, t, fi=0):
        i = self.active(t)
        sh = self.shots[i]
        tin = sh.get('tin', 'cut')
        if tin in ('iris', 'diag', 'blinds', 'split') and i > 0 and t - sh['t0'] < sh.get('td', 0.4):
            prev = self.shots[i - 1]
            u = (t - sh['t0']) / sh.get('td', 0.4)
            pz = 1 + self.pulse(t)
            A = self.shot_img(prev, t, extra_zoom=pz)
            B = self.shot_img(sh, t, extra_zoom=pz * (1 + 0.08 * (1 - u)))
            m = self.mask(tin, u, self.W, self.H, sh)[..., None]
            img = A * (1 - m) + B * m
            if sh.get('medge'):   # maske kenarında renkli ince çizgi
                e = np.clip(1 - np.abs(m[..., 0] - 0.5) * 2, 0, 1) ** 3
                img = img + e[..., None] * np.array(sh['medge'], np.float32)
            img = self.grade(img, t, sh)
            return self.overlay(img, t, fi)
        return super().frame(t, fi)
