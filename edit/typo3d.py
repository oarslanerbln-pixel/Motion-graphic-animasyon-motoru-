"""3D krom/altın tipografi: ekstrüzyon, bevel ışığı, ışık süpürmesi, zemin yansıması,
perspektif dönüş ve görüntü-doldurma (track matte)."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw
import lib

# Malzemeler: tint (yansıma rengi), floor/sky tonları, yan yüz rengi
CHROME = dict(tint=(0.94, 0.95, 0.98), sky=((0.84, 0.86, 0.90), (0.36, 0.40, 0.48)), floor=((0.05, 0.05, 0.07), (0.55, 0.50, 0.47)),
              side=((0.55, 0.57, 0.62), (0.05, 0.05, 0.07)), hl=(0.92, 0.93, 0.96))
GOLD = dict(tint=(0.96, 0.72, 0.32), sky=((0.95, 0.88, 0.72), (0.62, 0.42, 0.16)), floor=((0.10, 0.05, 0.01), (0.80, 0.55, 0.22)),
            side=((0.62, 0.40, 0.12), (0.07, 0.035, 0.005)), hl=(1.0, 0.93, 0.75))
ROSE = dict(tint=(1.0, 0.70, 0.62), sky=((1.0, 0.92, 0.90), (0.62, 0.38, 0.36)), floor=((0.10, 0.04, 0.04), (0.78, 0.48, 0.42)),
            side=((0.60, 0.34, 0.30), (0.07, 0.03, 0.03)), hl=(1.0, 0.92, 0.88))
OBSIDIAN = dict(tint=(0.9, 0.92, 1.0), sky=((0.75, 0.78, 0.85), (0.10, 0.10, 0.13)), floor=((0.0, 0.0, 0.01), (0.12, 0.12, 0.14)),
                side=((0.10, 0.10, 0.12), (0.0, 0.0, 0.0)), hl=(1.0, 1.0, 1.0))


def ramp(stops, t):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (t >= a) & (t <= b)
        u = ((t - a) / (b - a))[m][:, None]
        out[m] = np.array(ca) * (1 - u) + np.array(cb) * u
    return out


class Text3D:
    def __init__(self, text, fnt, tracking=0, depth=40, lines=None, line_gap=0.92, align='m'):
        lines = lines or [text]
        tmp = ImageDraw.Draw(Image.new('L', (8, 8)))
        asc, desc = fnt.getmetrics()
        lh = int((asc + desc) * line_gap)
        widths = []
        for ln in lines:
            ws = [tmp.textlength(ch, font=fnt) for ch in ln]
            widths.append(sum(ws) + tracking * max(len(ln) - 1, 0))
        Wt = int(max(widths)); Ht = lh * len(lines) + desc
        self.pad = pad = int(depth * 1.6 + 30)
        Wc, Hc = Wt + 2 * pad, Ht + 2 * pad
        im = Image.new('L', (Wc, Hc), 0); d = ImageDraw.Draw(im)
        for li, ln in enumerate(lines):
            x = pad + (Wt - widths[li]) / 2 if align == 'm' else pad
            for ch in ln:
                d.text((x, pad + li * lh), ch, font=fnt, fill=255)
                x += tmp.textlength(ch, font=fnt) + tracking
        a = np.asarray(im).astype(np.float32) / 255
        self.a = a
        self.h, self.w = a.shape
        self.depth = depth
        # bevel normali
        sz = fnt.size
        binm = (a > 0.5).astype(np.uint8)
        dist = cv2.distanceTransform(binm, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        bw = max(2.0, sz * 0.055)
        x = np.clip(dist / bw, 0, 1)
        hgt = np.sqrt(np.clip(1 - (1 - x) ** 2, 0, 1)) * bw          # yuvarlak profil
        hgt = cv2.GaussianBlur(hgt.astype(np.float32), (0, 0), max(1.2, bw * 0.14))
        gx = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3) / 8
        gy = cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3) / 8
        n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
        self.n = (n / np.linalg.norm(n, axis=-1, keepdims=True)).astype(np.float32)
        # dikey konum (harf yüksekliği içinde)
        ys = np.where(a.max(1) > 0.5)[0]
        y0, y1 = (ys.min(), ys.max()) if len(ys) else (0, self.h)
        self.v = np.clip((np.arange(self.h, dtype=np.float32) - y0) / max(y1 - y0, 1), 0, 1)[:, None] * np.ones((1, self.w), np.float32)
        er = cv2.erode(a, np.ones((3, 3), np.uint8), iterations=max(1, int(sz * 0.012)))
        self.edge = np.clip(a - er, 0, 1)
        self.text_w, self.text_h = Wt, y1 - y0

    # ------------------------------------------------------------ katmanlar
    def env(self, rx, ry, mat, light):
        """stüdyo ortamı: gökyüzü/ufuk/zemin + iki softbox + süpüren dikey ışık şeridi."""
        t = np.clip(ry, -1, 1)
        sk0, sk1 = (np.array(c, np.float32) for c in mat['sky'])
        fl0, fl1 = (np.array(c, np.float32) for c in mat['floor'])
        up = np.clip(-t, 0, 1)[..., None]; dn = np.clip(t, 0, 1)[..., None]
        sky = sk1 * (1 - up ** 0.6) + sk0 * up ** 0.6
        flo = fl0 * (1 - dn ** 0.7) + fl1 * dn ** 0.7
        e = np.where(t[..., None] < 0, sky, flo)
        # ufuk çizgisi: keskin koyu bant (kromun karakteri)
        e = e * (1 - 0.75 * np.exp(-((t - 0.02) / 0.05) ** 2))[..., None]
        hl = np.array(mat['hl'], np.float32)
        sb = 0.9 * np.exp(-((t + 0.55) / 0.10) ** 2) + 0.5 * np.exp(-((t + 0.85) / 0.06) ** 2)
        sweep = 1.2 * np.exp(-((rx - (light * 2.4 - 1.2)) / 0.11) ** 2) * np.clip(1 - np.abs(t) * 0.6, 0, 1)
        return e + (sb + sweep)[..., None] * hl

    def layers(self, mat=CHROME, light=0.0, ry=0.0, rx=0.0, spec_w=0.07):
        """yerel uzayda: yüz rengi, yüz shade, spec, ekstrüzyon rgba."""
        if isinstance(mat, list):
            mat = CHROME
        H, W = self.h, self.w
        if not hasattr(self, '_xp'):
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            self._xp = xx / W * 2 - 1
        n = self.n
        # yansıma vektörü (bakış -z): r = v - 2(v·n)n, v=(0,0,-1)
        rxv = 2 * n[..., 2] * n[..., 0]
        ryv = 2 * n[..., 2] * n[..., 1]
        # düz yüzde de gradyan olsun: konumla karıştır (büyük yüzey eğriliği hissi)
        yrot = math.sin(math.radians(rx)) * 0.4
        ry_eff = ryv * 0.9 + (self.v * 2 - 1) * 0.62 - 0.02 + yrot
        rx_eff = rxv * 0.9 + self._xp * 0.55 + math.sin(math.radians(ry)) * 0.5
        e = self.env(rx_eff, ry_eff, mat, light)
        tint = np.array(mat['tint'], np.float32)
        fres = (1 - n[..., 2]) ** 2.5
        face = e * tint * (1 - 0.35 * fres[..., None]) + fres[..., None] * 0.35 * np.array(mat['hl'], np.float32)
        face = face / (1 + 0.55 * face) * 1.4                     # yumuşak omuz: beyaza patlamasın
        spec = (self.edge * 0.35)[..., None] * np.array(mat['hl'], np.float32)
        L = np.array([-0.45, -0.6, 0.66], np.float32); L /= np.linalg.norm(L)
        ndl = np.clip((n * L).sum(-1), 0, 1)
        shade = (0.62 + 0.5 * ndl)[..., None]       # görüntü-dolgu için
        # ekstrüzyon
        dx = math.sin(math.radians(ry)) * self.depth + 0.22 * self.depth
        dy = -math.sin(math.radians(rx)) * self.depth + 0.5 * self.depth
        N = max(8, int(self.depth / 1.5))
        ea = np.zeros_like(self.a); ec = np.zeros((H, W, 3), np.float32)
        s0, s1 = (np.array(c, np.float32) for c in mat['side'])
        for i in range(N, 0, -1):
            u = i / N
            ox, oy = int(round(dx * u)), int(round(dy * u))
            sl = np.zeros_like(self.a)
            ys0, ys1 = max(0, oy), min(H, H + oy); xs0, xs1 = max(0, ox), min(W, W + ox)
            sl[ys0:ys1, xs0:xs1] = self.a[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
            col = s0 * (1 - u) ** 1.6 + s1 * (1 - (1 - u) ** 1.6)
            new = sl * (1 - ea)
            ec += new[..., None] * col
            ea += new
        ec = ec / np.maximum(ea[..., None], 1e-4)
        # yan yüzde dikey ışık: üst kenarlar parlak, alt koyu
        ec = ec * (0.75 + 0.5 * (1 - self.v[..., None]))
        return face, shade, spec, ec, ea

    # ------------------------------------------------------------ çizim
    def draw(self, img, cx, cy, height, ry=0.0, rx=0.0, rz=0.0, light=0.0, mat=CHROME, fill=None,
             opacity=1.0, reflect=0.0, floor_gap=0.0, glow=0.0, glow_col=(1, 1, 1), f=2200.0, max_w=None, shadow=0.45):
        """height: yazının ekrandaki harf yüksekliği (px). fill: tam kare görüntü (matte)."""
        if opacity <= 0.003:
            return img
        Hs, Ws = img.shape[:2]
        face, shade, spec, ec, ea = self.layers(mat, light, ry, rx)
        s = height / max(self.text_h, 1)
        if max_w is not None:
            s = min(s, max_w / max(self.text_w, 1))
        # 3D köşe projeksiyonu
        w2, h2 = self.w / 2, self.h / 2
        src = np.float32([[0, 0], [self.w, 0], [self.w, self.h], [0, self.h]])
        cy_, sy_ = math.cos(math.radians(ry)), math.sin(math.radians(ry))
        cx_, sx_ = math.cos(math.radians(rx)), math.sin(math.radians(rx))
        cz_, sz_ = math.cos(math.radians(rz)), math.sin(math.radians(rz))
        dst = []
        for X, Y in src:
            x, y, z = (X - w2) * s, (Y - h2) * s, 0.0
            x, y = x * cz_ - y * sz_, x * sz_ + y * cz_
            x, z = x * cy_ + z * sy_, -x * sy_ + z * cy_
            y, z = y * cx_ - z * sx_, y * sx_ + z * cx_
            k = f / (f + z)
            dst.append([cx + x * k, cy + y * k])
        dst = np.float32(dst)
        M = cv2.getPerspectiveTransform(src, dst)
        wp = lambda x: cv2.warpPerspective(x, M, (Ws, Hs), flags=cv2.INTER_LINEAR, borderValue=0)
        A = wp(self.a) * opacity
        EA = wp(ea) * opacity
        EC = wp(ec)
        SH = wp(shade)
        SP = wp(spec)
        if fill is None:
            FC = wp(face)
        else:
            FC = fill * SH[..., None] if SH.ndim == 2 else fill * SH
        if SH.ndim == 2:
            SH = SH[..., None]
        if glow > 0:
            g = cv2.GaussianBlur(np.maximum(A, EA), (0, 0), height * 0.12)[..., None]
            img = img + g * np.array(glow_col, np.float32) * glow
        if shadow > 0 and fill is None:
            sa = cv2.GaussianBlur(np.maximum(A, EA), (0, 0), height * 0.06)
            M2 = np.float32([[1, 0, height * 0.03], [0, 1, height * 0.08]])
            sa = cv2.warpAffine(sa, M2, (Ws, Hs))
            img = img * (1 - shadow * sa[..., None])
        if reflect > 0:
            # zemin yansıması: dikey ayna, soluklaşan
            base = int(dst[:, 1].max() + floor_gap)
            comp = img.copy()
            comp = comp * (1 - EA[..., None]) + EC * EA[..., None]
            fc = FC if fill is None else FC
            comp = comp * (1 - A[..., None]) + np.clip(fc + SP, 0, 1.4) * A[..., None]
            alpha = np.maximum(A, EA)
            top = max(0, int(dst[:, 1].min()))
            hgt = base - top
            if hgt > 4 and base < Hs:
                seg = comp[top:base][::-1]; sa = alpha[top:base][::-1]
                n = min(len(seg), Hs - base)
                fade = np.linspace(reflect, 0, n, dtype=np.float32)[:, None]
                ra = sa[:n] * fade
                rs = cv2.GaussianBlur(seg[:n], (0, 0), 2.0)
                img[base:base + n] = img[base:base + n] * (1 - ra[..., None]) + rs * ra[..., None]
        img = img * (1 - EA[..., None]) + EC * EA[..., None]
        img = img * (1 - A[..., None]) + np.clip(FC + SP, 0, 1.6) * A[..., None]
        return img


def bg_gradient(W, H, c0, c1, angle=90, center=None):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if center is not None:
        r = np.sqrt((xx - center[0] * W) ** 2 + (yy - center[1] * H) ** 2) / math.hypot(W, H) * 1.6
        u = np.clip(r, 0, 1)[..., None]
    else:
        a = math.radians(angle)
        p = (xx * math.cos(a) + yy * math.sin(a))
        u = ((p - p.min()) / (p.max() - p.min()))[..., None]
    return np.array(c0, np.float32) * (1 - u) + np.array(c1, np.float32) * u
