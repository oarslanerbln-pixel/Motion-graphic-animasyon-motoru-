"""Set 2: CHROME 3D · POSTER (dikey/diyagonal tipografi, duotone) · DREAM (abstrakt).
Temiz ve keskin: partikül/ağır gren yok."""
import math, numpy as np, cv2
import lib, typo3d
from engine import TextBlock

MON = 'Montserrat-VF.ttf'; MONI = 'Montserrat-Italic-VF.ttf'
ANT = 'Anton-Regular.ttf'; SERI = 'InstrumentSerif-Italic.ttf'; SER = 'InstrumentSerif-Regular.ttf'
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def S(W, H):
    return min(W, H) / 1080


# ------------------------------------------------------------------ yardımcılar
def clip_at(eng, cid, t, t0, src0, W, H, speed=1.0, z=1.0, dx=0.0, dy=0.0, rot=0.0, fx=None, fy=None):
    c = lib.load(cid, eng.src, eng.W, eng.H)
    st = src0 + (t - t0) * speed
    if eng.W > eng.H:
        fy = lib.CLIPS[cid].get('hfy', fy) if fy is None else fy
        if c.h > c.w:
            z = 1 + (z - 1) * 0.45
    return lib.place(c.frame(st), c, st, W, H, z, dx, dy, rot, fx, fy)


def clip_raw(eng, cid, idx):
    c = lib.load(cid, eng.src, eng.W, eng.H)
    return c, c.f[int(np.clip(idx, 0, c.n - 1))].astype(np.float32)


def duotone(img, dark, light, k=1.25):
    L = (np.clip(img, 0, 1) @ LUMA)[..., None]
    L = np.clip((L - 0.5) * k + 0.5, 0, 1)
    L = L * L * (3 - 2 * L)
    return np.array(dark, np.float32) * (1 - L) + np.array(light, np.float32) * L


def solid(W, H, c):
    return np.zeros((H, W, 3), np.float32) + np.array(c, np.float32)


def draw_rot(img, tb, cx, cy, ang=0.0, scale=1.0, op=1.0, color=None, reveal=1.0):
    """TextBlock'u açı ile çiz (maske açılışı yerel uzayda)."""
    a = tb.alpha
    if reveal < 1.0:
        h = a.shape[0]
        off = int((1 - lib.ease_out_expo(reveal)) * h * 0.8)
        m = np.zeros_like(a)
        if off < h:
            m[:h - off] = a[off:]
        a = m
    H, W = img.shape[:2]
    h, w = a.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, scale)
    M[0, 2] += cx - w / 2; M[1, 2] += cy - h / 2
    A = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)[..., None] * op
    col = tb.col if color is None else np.array(color, np.float32)
    return img * (1 - A) + col * A


def band(img, text_tb, cx, cy, ang, length, thick, bg, fg, offset):
    """diyagonal kayan bant (ticker)."""
    H, W = img.shape[:2]
    a = text_tb.alpha
    tw = a.shape[1]
    reps = int(length / tw) + 3
    strip_a = np.tile(a, (1, reps))
    o = int(offset) % tw
    strip_a = strip_a[:, o:o + int(length)]
    sh = strip_a.shape[0]
    th = int(thick)
    canvas_a = np.zeros((th, strip_a.shape[1]), np.float32)
    y0 = (th - sh) // 2
    if y0 >= 0:
        canvas_a[y0:y0 + sh] = strip_a
    else:
        canvas_a = strip_a[-y0:-y0 + th]
    bga = np.ones_like(canvas_a)
    M = cv2.getRotationMatrix2D((canvas_a.shape[1] / 2, th / 2), ang, 1.0)
    M[0, 2] += cx - canvas_a.shape[1] / 2; M[1, 2] += cy - th / 2
    BA = cv2.warpAffine(bga, M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    TA = cv2.warpAffine(canvas_a, M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    img = img * (1 - BA) + np.array(bg, np.float32) * BA
    return img * (1 - TA) + np.array(fg, np.float32) * TA


def poly_mask(W, H, pts, soft=1.5):
    m = np.zeros((H * 2, W * 2), np.uint8)
    cv2.fillPoly(m, [np.int32(np.array(pts) * 2)], 255, lineType=cv2.LINE_AA)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return m


# ================================================================== CHROME 3D
def chrome(W, H):
    b = 60 / 142; bar = 4 * b
    hor = W > H
    s = S(W, H)
    fB = lambda px: lib.font(MON, int(px), 900)
    T36 = typo3d.Text3D('36', fB(560), depth=70)
    TK = typo3d.Text3D('KREUZBERG', fB(260), tracking=-6, depth=34)
    TK2 = typo3d.Text3D('', fB(300), depth=40, lines=['KREUZ', 'BERG'], line_gap=0.86, tracking=-6)
    TM = typo3d.Text3D('MAHALLE', fB(240), tracking=-4, depth=30)
    TMs = TextBlock('M A H A L L E', lib.font(MON, int(30 * s), 600), (0.9, 0.9, 0.95), tracking=int(10 * s))
    bgcols = [(0.85, 0.08, 0.18), (0.08, 0.20, 0.85), (0.98, 0.55, 0.05), (0.45, 0.10, 0.75)]

    def r_intro(eng, sh, t, W, H):
        u = (t - sh['t0']) / (sh['t1'] - sh['t0'])
        img = typo3d.bg_gradient(W, H, (0.10, 0.05, 0.22), (0.0, 0.0, 0.01), center=(0.5, 0.42))
        ry = 70 * (1 - lib.ease_out_expo(u * 1.3))
        hgt = (520 if not hor else 430) * s * (0.92 + 0.08 * u)
        img = T36.draw(img, W / 2, H * 0.44, hgt, ry=ry, rx=6, light=-0.2 + 1.4 * u, reflect=0.32, floor_gap=10 * s,
                       glow=0.10, glow_col=(0.55, 0.3, 1.0), opacity=min(1, u * 4))
        o = lib.ease_io((u - 0.45) / 0.3)
        if o > 0:
            img = TMs.draw(img, W / 2, H * (0.70 if not hor else 0.80), o, o)
        return img

    def r_matte(eng, sh, t, W, H, clip, src0, text, push_at=0.62, light0=0.0, lines=False):
        u = (t - sh['t0']) / (sh['t1'] - sh['t0'])
        fill = clip_at(eng, clip, t, sh['t0'], src0, W, H, 1.0)
        img = typo3d.bg_gradient(W, H, (0.03, 0.03, 0.05), (0.0, 0.0, 0.0), center=(0.5, 0.5))
        base = (300 if not hor else 300) * s if not lines else (620 if not hor else 520) * s
        hgt = base * (1 + 0.12 * u)
        if u > push_at:   # harfin içinden geçerek görüntüye gir
            k = (u - push_at) / (1 - push_at)
            hgt *= math.exp(5.2 * lib.ease_in_expo(k) * 1.0 + 1.4 * k * k)
        ry = 18 * (1 - u) - 6
        img = text.draw(img, W / 2, H / 2, hgt, ry=ry, rx=4, light=light0 + 1.2 * u, fill=fill,
                        max_w=W * 0.92 * (hgt / base), f=2600)
        # sonda tam kareye karış
        if u > 0.9:
            a = (u - 0.9) / 0.1
            img = img * (1 - a) + fill * a
        return img

    def r_band(eng, sh, t, W, H):
        u = (t - sh['t0']) / (sh['t1'] - sh['t0'])
        k = int(u * 2)   # her vuruşta renk
        c0 = np.array(bgcols[k % 4]); c1 = c0 * 0.35
        img = typo3d.bg_gradient(W, H, c0, c1, angle=60)
        # arka planda içi görüntü dolu yuvarlak pencere
        win = clip_at(eng, '0566', t, sh['t0'], 0.6, W, H, 0.7, 1.2)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = min(W, H) * (0.30 + 0.05 * u)
        m = np.clip((r - np.sqrt((xx - W / 2) ** 2 + (yy - H * 0.45) ** 2)) / 2 + 0.5, 0, 1)[..., None]
        img = img * (1 - m) + win * m
        x = W * (1.25 - 1.5 * lib.ease_io(u))
        img = TM.draw(img, x, H * 0.5, (210 if not hor else 190) * s, ry=-25 + 50 * u, rz=-10, light=0.2 + u,
                      glow=0.2, glow_col=(1, 1, 1))
        return img

    def r_lower3d(eng, sh, t, W, H):
        u = (t - sh['t0']) / (sh['t1'] - sh['t0'])
        img = clip_at(eng, '0562', t, sh['t0'], 1.0, W, H, 0.5, 1.05 + 0.08 * u)
        img = lib.sat(img, 0.9)
        # alt gölge
        g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        img = img * (1 - 0.6 * np.clip((g - 0.6) / 0.4, 0, 1))
        o = lib.ease_out_expo(u * 2.2)
        img = TM.draw(img, W / 2, H * (0.80 if not hor else 0.78), (120 if not hor else 110) * s, ry=12 * (1 - o),
                      light=-0.3 + 1.6 * u, mat=typo3d.GOLD, reflect=0.3, floor_gap=6 * s, opacity=o)
        return img

    def r_end(eng, sh, t, W, H):
        u = (t - sh['t0'])
        img = typo3d.bg_gradient(W, H, (0.09, 0.05, 0.2), (0.0, 0.0, 0.0), center=(0.5, 0.45))
        o1 = lib.ease_out_expo(u / 0.8)
        y36 = H * (0.36 if not hor else 0.34)
        img = T36.draw(img, W / 2, y36, (380 if not hor else 300) * s, ry=25 * (1 - o1) - 4, light=-0.3 + 0.7 * u,
                       glow=0.15, glow_col=(0.55, 0.3, 1.0), opacity=o1)
        o2 = lib.ease_out_expo((u - 0.25) / 0.8)
        img = TK.draw(img, W / 2, y36 + (300 if not hor else 250) * s, 120 * s, ry=-20 * (1 - o2), light=0.6 * u - 0.1,
                      mat=typo3d.GOLD, reflect=0.3, floor_gap=8 * s, max_w=W * 0.86, opacity=max(o2, 0))
        o3 = lib.ease_io((u - 0.7) / 0.5)
        if o3 > 0:
            img = TMs.draw(img, W / 2, y36 + (640 if not hor else 470) * s, o3, o3)
        fo = min(1, max(0, (sh['t1'] - t) / 0.7))
        return img * fo

    def fast(t0, n, clips):
        out = []
        for k, (c, s0, z) in enumerate(clips[:n]):
            out.append(dict(t0=t0 + k * b, t1=t0 + (k + 1) * b, clip=c, src=(s0, 0),
                            speed=[(0, 1.4), (0.5, 0.5), (1, 1.4)], cam=[(0, z * 1.12, 0, 0, 0), (1, z, 0, 0, 0)],
                            tin=('iris' if k % 2 else 'blinds'), td=0.22, medge=(0.4, 0.9, 1.0)))
        return out

    B = lambda n: n * b
    T = 10 * bar
    sh = [
        dict(t0=0, t1=bar, render=r_intro),
        dict(t0=bar, t1=2 * bar, render=lambda e, s_, t, W, H: r_matte(e, s_, t, W, H, '0582', 0.0, TK2, 0.62, 0.0, True)),
        dict(t0=2 * bar, t1=2 * bar + B(2), clip='0582', src=(bar, 0), speed=[(0, 1.0), (0.55, 0.25), (1, 1.6)],
             cam=[(0, 1.0, 0, 0, 0), (0.55, 1.12, 0, 0, 0), (1, 1.05, 0, 0, 0)]),
        dict(t0=2 * bar + B(2), t1=3 * bar, clip='0560', src=(0.1, 0), speed=[(0, 1.2), (0.6, 0.35), (1, 1.0)],
             cam=[(0, 1.2, 0, 0, -3), (1, 1.05, 0, 0, 0)], tin='iris', td=0.3, medge=(0.4, 0.9, 1.0)),
        dict(t0=3 * bar, t1=3 * bar + B(2), clip='0575', src=(0.4, 0), speed=[(0, 1.6), (0.5, 0.4), (1, 1.2)],
             cam=[(0, 1.15, 0, 0, 0), (1, 1.0, 0, 0, 0)], tin='diag', td=0.28, mang=58, medge=(1.0, 0.3, 0.6)),
        dict(t0=3 * bar + B(2), t1=4 * bar, render=r_band, tin='split', td=0.25),
        dict(t0=4 * bar, t1=5 * bar, clip='0558', src=(0.2, 0), speed=[(0, 1.8), (0.35, 0.15), (0.7, 0.15), (1, 1.6)],
             cam=[(0, 1.0, 0, 0, 0), (0.4, 1.22, 0, 0, 0), (1, 1.1, 0, 0, 0)], tin='iris', td=0.3, medge=(1, 0.85, 0.4)),
        dict(t0=5 * bar, t1=6 * bar, render=r_lower3d, tin='diag', td=0.35, mang=120),
    ]
    sh += fast(6 * bar, 4, [('0577', 0.5, 1.15), ('0566', 1.3, 1.25), ('0560', 0.3, 1.1), ('0582', 0.9, 1.05)])
    sh += [
        dict(t0=7 * bar, t1=8 * bar, render=lambda e, s_, t, W, H: r_matte(e, s_, t, W, H, '0558', 1.0, T36, 0.66, 0.3, True),
             tin='iris', td=0.25),
        dict(t0=8 * bar, t1=9 * bar, clip='0562', src=(1.0, 0), speed=[(0, 1.2), (0.5, 0.3), (1, 0.9)],
             cam=[(0, 1.0, 0, 0, 0), (1, 1.18, 0, 0, 0)], tin='split', td=0.3, medge=(0.4, 0.9, 1.0)),
    ]
    sh += fast(9 * bar, 4, [('0582', 0.3, 1.05), ('0560', 0.7, 1.15), ('0577', 1.6, 1.2), ('0566', 2.0, 1.3)])
    dur = T + 2.4
    sh.append(dict(t0=T, t1=dur, render=r_end, tin='iris', td=0.3, medge=(0.6, 0.4, 1.0)))

    kicks = [k * bar + o for k in range(1, 10) if k != 5 for o in (0, 2.5 * b)]

    def pulse(t):
        v = sum(math.exp(-(t - tk) * 12) for tk in kicks if 0 <= t - tk < 0.3)
        return 0.022 * v

    vig = lib.vignette(W, H, 0.35)

    def grade(img, t, s_):
        x = np.clip(img, 0, 1.3)
        if 'clip' in s_:
            x = lib.contrast(x, 1.12, 0.42)
            x = lib.split_tone(x, (-0.01, 0.0, 0.04), (0.03, 0.01, 0.0), 0.45)
            x = lib.sat(x, 0.95)
        x = lib.bloom(x, 0.93, 0.10, 22 * s)
        return x * vig

    def overlay(img, t, fi):
        return img

    return sh, grade, overlay, pulse, 'chrome', dur


# ===================================================================== POSTER
def poster(W, H):
    b = 0.6; bar = 2.4
    hor = W > H
    s = S(W, H)
    RED, YEL, BLU, CRM, INK = (0.92, 0.16, 0.13), (0.99, 0.80, 0.08), (0.10, 0.25, 0.92), (0.95, 0.93, 0.87), (0.06, 0.06, 0.07)
    fA = lambda px: lib.font(ANT, int(px))
    fM = lambda px, w=900: lib.font(MON, int(px), w)
    letters = list('KREUZBERG')
    LH = (H * 0.86) / len(letters)
    Ltb = [TextBlock(ch, fA(LH * 1.18), INK, pad=10) for ch in letters]
    big36 = TextBlock('36', fA(1500 * s if not hor else 1250 * s), RED, pad=20)
    tick = TextBlock('MAHALLE  •  36 KREUZBERG  •  ', fM(64 * s, 900), INK, pad=6)
    w_kreuz = [TextBlock(ch, fA(230 * s), CRM, pad=8) for ch in 'KREUZ']
    w_berg = TextBlock('BERG', fA(300 * s), YEL, pad=10)
    w_36 = TextBlock('36', fA(420 * s), RED, pad=10)
    w_mah = TextBlock('MAHALLE', fM(150 * s, 900), CRM, pad=10)
    mah_v = [TextBlock(ch, fM(170 * s, 900), RED, pad=6) for ch in 'MAHALLE']
    end36 = TextBlock('36', fA(900 * s if not hor else 760 * s), RED, pad=10)
    endK = TextBlock('KREUZ', fA(260 * s), INK, pad=8)
    endB = TextBlock('BERG', fA(260 * s), INK, pad=8)
    endM = TextBlock('MAHALLE — 2026', fM(30 * s, 700), INK, tracking=int(8 * s), pad=6)

    def stack_letters(img, t, t0, col=INK, x=None, step=b / 2, scale=1.0, tbs=None, lh=None):
        tbs = tbs or Ltb; lh = lh or LH
        x = x if x is not None else W * 0.075 + lh * 0.2
        top = H / 2 - lh * len(tbs) / 2 + lh / 2
        for i, tb in enumerate(tbs):
            u = (t - t0 - i * step * 0.5) / 0.35
            if u <= 0:
                continue
            e = lib.ease_out_expo(u)
            img = tb.draw(img, x, top + i * lh - (1 - e) * lh * 0.8, min(1, u * 2), color=col, scale=scale)
        return img

    def r0(eng, sh, t, W, H):          # kırmızı afiş: dev 36 + dikey harfler
        u = t - sh['t0']
        img = solid(W, H, RED)
        # içinde duotone görüntü olan diyagonal pencere
        k = lib.ease_out_expo(u / 0.9)
        pts = [(W * (0.38 + 0.6 * (1 - k)), H * 0.08), (W * 1.02, H * 0.0), (W * 1.02, H * 0.94), (W * (0.30 + 0.6 * (1 - k)), H * 1.0)]
        m = poly_mask(W, H, pts)[..., None]
        v = clip_at(eng, '0566', t, sh['t0'], 0.3, W, H, 0.8, 1.15)
        img = img * (1 - m) + duotone(v, INK, CRM) * m
        img = big36.draw(img, W * (0.74 if not hor else 0.70), H * 0.55 + (1 - lib.ease_out_expo(u / 0.7)) * H * 0.3,
                         0.92, color=YEL, scale=1.0)
        lh_bg = int(LH * 0.95)
        img[:, :int(W * 0.075 + LH * 0.2 + lh_bg * 0.55)] = img[:, :int(W * 0.075 + LH * 0.2 + lh_bg * 0.55)] * 0 + np.array(INK, np.float32)
        img = stack_letters(img, t, sh['t0'] + 0.3, CRM)
        return img

    def r1(eng, sh, t, W, H):          # sarı: diyagonal bant içinde yürüyüş + ticker
        u = t - sh['t0']
        img = solid(W, H, YEL)
        k = lib.ease_out_expo(u / 0.6)
        wdt = (W if hor else H) * 0.36 * k
        cx, cy = W / 2, H / 2
        ang = math.radians(-18)
        dxv, dyv = math.cos(ang), math.sin(ang)
        nx, ny = -dyv, dxv
        L = math.hypot(W, H)
        pts = [(cx - dxv * L - nx * wdt, cy - dyv * L - ny * wdt), (cx + dxv * L - nx * wdt, cy + dyv * L - ny * wdt),
               (cx + dxv * L + nx * wdt, cy + dyv * L + ny * wdt), (cx - dxv * L + nx * wdt, cy - dyv * L + ny * wdt)]
        m = poly_mask(W, H, pts)[..., None]
        v = clip_at(eng, '0575', t, sh['t0'], 0.3, W, H, 0.9, 1.0, fy=0.3)
        img = img * (1 - m) + duotone(v, INK, (0.98, 0.95, 0.85)) * m
        off = u * 380 * s
        img = band(img, tick, W / 2, H * (0.18 if not hor else 0.16), 18, L * 1.2, 92 * s, INK, YEL, off)
        img = band(img, tick, W / 2, H * (0.84 if not hor else 0.86), 18, L * 1.2, 92 * s, RED, CRM, -off * 1.3 + 400)
        return img

    def r2(eng, sh, t, W, H):          # mavi diyagonal bölünmüş: iki portre
        u = t - sh['t0']
        img = solid(W, H, BLU)
        a = duotone(clip_at(eng, '0558', t, sh['t0'], 0.4, W, H, 0.8, 1.05), (0.04, 0.05, 0.25), (0.75, 0.85, 1.0))
        bimg = duotone(clip_at(eng, '0562', t, sh['t0'], 1.2, W, H, 0.8, 1.05, dx=0.0), (0.25, 0.02, 0.02), (1.0, 0.85, 0.7))
        k = lib.ease_out_expo(u / 0.7)
        sl = 0.25
        pts = [(W * (0.5 + sl) + (1 - k) * W, 0), (W * 1.1, 0), (W * 1.1, H), (W * (0.5 - sl) + (1 - k) * W, H)]
        m = poly_mask(W, H, pts)[..., None]
        img = a * (1 - m) + bimg * m
        # kesim çizgisi
        ln = poly_mask(W, H, [(p[0] - 5 * s, p[1]) if i in (0, 3) else (pts[0][0] + 5 * s, 0) if i == 1 else (pts[3][0] + 5 * s, H)
                               for i, p in enumerate(pts)])
        img = img * (1 - ln[..., None]) + np.array(YEL, np.float32) * ln[..., None]
        img = stack_letters(img, t, sh['t0'] + 0.2, YEL)
        return img

    def r3(eng, sh, t, W, H):          # krem duotone + her vuruşta farklı yönde kelime
        u = t - sh['t0']
        v = clip_at(eng, '0560', t, sh['t0'], 0.0, W, H, 0.55, 1.0 + 0.05 * u)
        img = duotone(v, INK, CRM)
        bi = int(u / b)
        if bi >= 0:   # 36 yatay
            img = w_36.draw(img, W * 0.72, H * 0.22, min(1, (u) / 0.15), min(1, u / 0.4))
        if bi >= 1:   # KREUZ dikey alt alta
            for i, tb in enumerate(w_kreuz):
                uu = (u - b - i * 0.06) / 0.3
                if uu > 0:
                    img = tb.draw(img, W * 0.14, H * 0.28 + i * 200 * s * (0.8 if hor else 1) - (1 - lib.ease_out_expo(uu)) * 80 * s,
                                  min(1, uu * 2), color=RED)
        if bi >= 2:   # BERG diyagonal
            uu = (u - 2 * b) / 0.4
            img = draw_rot(img, w_berg, W * 0.55, H * 0.55, 32, 1.0, min(1, uu * 2), reveal=min(1, uu))
        if bi >= 3:   # MAHALLE altta, dolu renkli zemin
            uu = (u - 3 * b) / 0.35
            k = lib.ease_out_expo(uu)
            y = H * 0.86
            hh = 190 * s
            img[int(y - hh / 2):int(y + hh / 2), :int(W * k)] = RED
            img = w_mah.draw(img, W / 2, y, min(1, uu * 2), min(1, uu))
        return img

    def r4(eng, sh, t, W, H):          # vuruş başına renk değişen duotone kesmeler
        u = t - sh['t0']
        k = int(u / b)
        clips = [('0582', 0.4), ('0566', 1.2), ('0577', 0.6), ('0575', 1.5)]
        pal = [(INK, YEL), ((0.3, 0.0, 0.05), (1, 0.6, 0.55)), ((0.0, 0.05, 0.3), (0.6, 0.9, 1.0)), (INK, RED)]
        c, s0 = clips[k % 4]
        v = clip_at(eng, c, t, sh['t0'] + k * b, s0, W, H, 1.0, 1.08 - 0.06 * ((u % b) / b))
        img = duotone(v, *pal[k % 4])
        # dev numara köşede
        img = w_36.draw(img, W * 0.80, H * 0.85, 0.9, 1, color=pal[k % 4][1] if k % 4 != 3 else CRM, scale=0.6)
        return img

    def r5(eng, sh, t, W, H):          # portre + sağda alt alta MAHALLE
        u = t - sh['t0']
        v = clip_at(eng, '0558', t, sh['t0'], 1.0, W, H, 0.6, 1.08, dx=-0.06 if not hor else -0.0)
        img = duotone(v, INK, CRM)
        lh = 190 * s if not hor else 140 * s
        x = W * (0.86 if not hor else 0.90)
        img = stack_letters(img, t, sh['t0'] + 0.1, RED, x=x, step=b / 2, tbs=mah_v, lh=lh,
                            scale=1.0 if not hor else 0.78)
        return img

    def r6(eng, sh, t, W, H):          # üç diyagonal şerit, üç renk
        u = t - sh['t0']
        img = solid(W, H, INK)
        items = [('0577', 1.0, ((0.02, 0.05, 0.3), (0.65, 0.8, 1.0))), ('0566', 0.5, (INK, YEL)), ('0560', 0.2, ((0.25, 0.0, 0.02), (1.0, 0.7, 0.62)))]
        for i, (c, s0, pal) in enumerate(items):
            uu = (u - i * b / 2) / 0.5
            if uu <= 0:
                continue
            k = lib.ease_out_expo(uu)
            if hor:
                x0 = int(W * i / 3); x1 = int(W * (i + 1) / 3); sk = int(W * 0.06)
                pw = x1 - x0 + 2 * sk
                v = duotone(clip_at(eng, c, t, sh['t0'], s0, pw, H, 0.8, 1.1), *pal)
                full = np.zeros((H, W, 3), np.float32)
                a0 = max(0, x0 - sk); a1 = min(W, x0 - sk + pw)
                full[:, a0:a1] = v[:, a0 - (x0 - sk):a1 - (x0 - sk)]
                pts = [(x0 + sk, 0), (x1 + sk, 0), (x1 - sk, H * k), (x0 - sk, H * k)]
            else:
                y0 = int(H * i / 3); y1 = int(H * (i + 1) / 3); sk = int(H * 0.04)
                ph = y1 - y0 + 2 * sk
                v = duotone(clip_at(eng, c, t, sh['t0'], s0, W, ph, 0.8, 1.1), *pal)
                full = np.zeros((H, W, 3), np.float32)
                a0 = max(0, y0 - sk); a1 = min(H, y0 - sk + ph)
                full[a0:a1] = v[a0 - (y0 - sk):a1 - (y0 - sk)]
                pts = [(0, y0 + sk), (W * k, y0 - sk + 2 * sk * (1 - k)), (W * k, y1 - sk), (0, y1 + sk)]
            m = poly_mask(W, H, pts)[..., None]
            img = img * (1 - m) + full * m
        return img

    def r7(eng, sh, t, W, H):          # duotone → gerçek renk geçişi + dev başlık
        u = t - sh['t0']
        v = clip_at(eng, '0562', t, sh['t0'], 1.0, W, H, 0.7, 1.0 + 0.1 * u / bar)
        d = duotone(v, INK, CRM)
        k = lib.ease_io((u - b) / (2 * b))
        img = d * (1 - k) + lib.sat(lib.contrast(v, 1.1, 0.45), 1.1) * k
        o = lib.ease_out_expo((u - 0.15) / 0.5)
        img = w_36.draw(img, W * 0.5, H * 0.18, o, o, color=YEL, scale=0.8)
        img = draw_rot(img, w_berg, W * 0.5, H * 0.84, -8, 0.8, o, color=CRM, reveal=o)
        return img

    def r_end(eng, sh, t, W, H):
        u = t - sh['t0']
        img = solid(W, H, CRM)
        o = lib.ease_out_expo(u / 0.6)
        img = end36.draw(img, W * (0.5 if not hor else 0.36), H * (0.38 if not hor else 0.5) + (1 - o) * 200 * s, 1, o)
        y = H * (0.68 if not hor else 0.40)
        x = W * (0.5 if not hor else 0.72)
        o2 = lib.ease_out_expo((u - 0.2) / 0.5)
        img = endK.draw(img, x, y, 1, o2)
        img = endB.draw(img, x, y + 230 * s, 1, lib.ease_out_expo((u - 0.35) / 0.5))
        o3 = lib.ease_io((u - 0.7) / 0.5)
        img = endM.draw(img, x, y + 400 * s, o3, o3)
        fo = min(1, max(0, (sh['t1'] - t) / 0.6))
        return img * fo

    fns = [r0, r1, r2, r3, r4, r5, r6, r7]
    tins = [None, 'diag', 'split', 'blinds', 'diag', 'iris', 'diag', 'split']
    sh = []
    for k, fn in enumerate(fns):
        d = dict(t0=k * bar, t1=(k + 1) * bar, render=fn)
        if tins[k]:
            d.update(tin=tins[k], td=0.35, mang=(60 if k % 2 else 120), soft=0.002)
        sh.append(d)
    T = 8 * bar
    dur = T + 2.0
    sh.append(dict(t0=T, t1=dur, render=r_end, tin='diag', td=0.3, mang=60, soft=0.002))

    def grade(img, t, s_):
        return np.clip(img, 0, 1)

    def overlay(img, t, fi):
        return img

    return sh, grade, overlay, None, 'poster', dur


# ====================================================================== DREAM
def dream(W, H):
    b = 60 / 72; bar = 4 * b
    hor = W > H
    s = S(W, H)
    rng = np.random.default_rng(11)
    # ışık sızıntısı alanları (düşük çözünürlükte yumuşak, büyütülmüş → pürüzsüz)
    leaks = []
    for i in range(4):
        f = rng.random((6, 4 if not hor else 7)).astype(np.float32)
        leaks.append(f)
    mah = TextBlock('mahalle', lib.font(SERI, int((300 if not hor else 260) * s)), (1.0, 0.95, 0.9), pad=30)
    kz = [TextBlock(ch, lib.font(SER, int(64 * s)), (1, 0.96, 0.92), pad=6) for ch in 'KREUZBERG']
    t36 = TextBlock('36', lib.font(MON, int((700 if not hor else 600) * s), 100), (1, 0.95, 0.9), pad=20)
    endA = TextBlock('mahalle', lib.font(SERI, int(220 * s)), (0.12, 0.1, 0.1), pad=20)
    endB = TextBlock('36  KREUZBERG', lib.font(MON, int(26 * s), 500), (0.12, 0.1, 0.1), tracking=int(14 * s), pad=6)

    def leak(t, W, H, amt=0.35):
        out = np.zeros((H, W, 3), np.float32)
        cols = [(1.0, 0.45, 0.15), (1.0, 0.2, 0.45), (0.2, 0.5, 1.0), (1.0, 0.8, 0.4)]
        for i, f in enumerate(leaks):
            ph = t * (0.25 + 0.1 * i) + i
            g = (np.sin(f * 6.28 + ph) * 0.5 + 0.5) ** 3
            g = cv2.resize(g, (W, H), interpolation=cv2.INTER_CUBIC)
            g = cv2.GaussianBlur(g, (0, 0), min(W, H) * 0.06)
            out += g[..., None] * np.array(cols[i], np.float32) * 0.5
        return out * amt

    def echo(eng, cid, t, t0, src0, W, H, speed, z, n=6, gap=3, prism=True, fy=None):
        c = lib.load(cid, eng.src, eng.W, eng.H)
        st = src0 + (t - t0) * speed
        acc = np.zeros((H, W, 3), np.float32); wsum = 0
        for k in range(n):
            idx = st * 30 - k * gap
            fr = c.f[int(np.clip(idx, 0, c.n - 1))].astype(np.float32)
            im = lib.place(fr, c, st, W, H, z, 0, 0, 0, None, fy if not hor else lib.CLIPS[cid].get('hfy'))
            w = 0.62 ** k
            if prism and k > 0:
                tint = np.array([(1.0, 0.5, 0.6), (0.5, 0.8, 1.0), (1.0, 0.85, 0.5)][k % 3], np.float32)
                im = im * tint
            acc = np.maximum(acc, im * (1 if k == 0 else 0.85 * w / 0.62)) if k else im.copy()
        return acc

    def r_double(eng, sh, t, W, H):
        u = (t - sh['t0']) / (sh['t1'] - sh['t0'])
        A = clip_at(eng, '0577', t, sh['t0'], 0.2, W, H, 0.6, 1.05 + 0.06 * u)
        B = clip_at(eng, '0582', t, sh['t0'], 0.1, W, H, 0.4, 1.3 - 0.15 * u, fx=0.5)
        L = (A @ LUMA)[..., None]
        m = np.clip((0.5 - L) / 0.25, 0, 1)
        m = cv2.GaussianBlur(m, (0, 0), 2.0)[..., None] if m.ndim == 2 else cv2.GaussianBlur(m[..., 0], (0, 0), 2.0)[..., None]
        bg = 0.66 + 0.3 * A
        img = bg * (1 - m) + (B * 1.15 + 0.03) * m
        return img * (0.75 + 0.25 * lib.ease_io(u * 3))

    def r_kaleido(eng, sh, t, W, H):
        u = (t - sh['t0']) / (sh['t1'] - sh['t0'])
        v = clip_at(eng, '0566', t, sh['t0'], 0.3, W, H, 0.5, 1.32, fx=0.30)
        ang = 8 * u - 4
        M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, 1.08)
        v = cv2.warpAffine(v, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        half = v[:, W - W // 2:]
        k = np.concatenate([half[:, ::-1], half], 1)
        if k.shape[1] < W:
            k = np.concatenate([k, k[:, -1:]], 1)
        k2 = k[:, :W]
        mix = lib.ease_io((u - 0.1) / 0.5)
        return v * (1 - mix) + k2 * mix

    def r_echo(eng, sh, t, W, H, cid, src0, speed, z):
        return echo(eng, cid, t, sh['t0'], src0, W, H, speed, z)

    def r_end(eng, sh, t, W, H):
        u = t - sh['t0']
        img = solid(W, H, (0.96, 0.93, 0.88))
        o = lib.ease_io(u / 1.2)
        img = endA.draw(img, W / 2, H / 2 - 20 * s, o, 1, blur=max(0, 8 * (1 - u / 1.0)) * s)
        o2 = lib.ease_io((u - 0.7) / 0.8)
        img = endB.draw(img, W / 2, H / 2 + 120 * s, o2, 1)
        fo = min(1, max(0, (sh['t1'] - t) / 0.9))
        return img * fo + np.array((0.96, 0.93, 0.88), np.float32) * 0 * (1 - fo)

    T = 6 * bar
    dur = T + 2.6
    sh = [
        dict(t0=0, t1=bar, render=r_double, tin='dip', td=1.2),
        dict(t0=bar, t1=2 * bar, render=r_kaleido, tin='xfade', td=1.0),
        dict(t0=2 * bar, t1=3 * bar, render=lambda e, s_, t, W, H: r_echo(e, s_, t, W, H, '0558', 0.3, 0.75, 1.05), tin='xfade', td=0.9),
        dict(t0=3 * bar, t1=4 * bar, render=lambda e, s_, t, W, H: r_echo(e, s_, t, W, H, '0575', 0.3, 0.7, 1.0), tin='xfade', td=0.9),
        dict(t0=4 * bar, t1=4 * bar + bar / 2, clip='0560', src=(0.0, 0), speed=[(0, 0.6), (0.6, 0.15), (1, 0.4)],
             cam=[(0, 1.05, 0, 0, 0), (1, 1.18, 0, 0, 0)], tin='xfade', td=0.9),
        dict(t0=4 * bar + bar / 2, t1=5 * bar, clip='0582', src=(0.4, 0), speed=[(0, 0.5), (1, 0.3)],
             cam=[(0, 1.2, 0, 0, 0), (1, 1.05, 0, 0, 0)], tin='xfade', td=0.8),
        dict(t0=5 * bar, t1=T, clip='0562', src=(1.1, 0), speed=[(0, 0.5), (0.5, 0.12), (1, 0.35)],
             cam=[(0, 1.0, 0, 0, 0), (1, 1.15, 0, 0, 0)], tin='xfade', td=1.0),
        dict(t0=T, t1=dur, render=r_end, tin='xfade', td=1.0),
    ]
    vig = lib.vignette(W, H, 0.45, 2.0)

    def grade(img, t, s_):
        x = np.clip(img, 0, 1.2)
        if s_.get('render') is r_end:
            return x
        # zamanla sıcak → soğuk
        k = np.clip(t / T, 0, 1)
        warm = np.array([1.06, 0.98, 0.88], np.float32); cool = np.array([0.88, 0.98, 1.08], np.float32)
        x = x * (warm * (1 - k) + cool * k)
        x = x * 0.97 + 0.02                    # hafif mat, keskin
        x = lib.sat(x, 0.85)
        x = x + leak(t, W, H, 0.2 if t < T else 0)
        x = lib.bloom(x, 0.82, 0.15, 30 * s)
        return x * vig

    def overlay(img, t, fi):
        if t >= T:
            return img
        # "mahalle" diyagonal süzülen
        for (t0, t1, x0, y0, x1, y1, ang) in ((1.0, 6.0, 0.2, 0.75, 0.7, 0.55, -18), (13.5, 19.5, 0.75, 0.3, 0.35, 0.5, 14)):
            if t0 <= t <= t1:
                u = (t - t0) / (t1 - t0)
                o = math.sin(math.pi * u) ** 1.5
                img = draw_rot(img, mah, W * (x0 + (x1 - x0) * u), H * (y0 + (y1 - y0) * u), ang, 1.0, o * 0.9)
        # ince 36 (6.7–13)
        if 6.8 <= t <= 13.0:
            u = (t - 6.8) / 6.2
            o = math.sin(math.pi * u) ** 2 * 0.55
            img = t36.draw(img, W * 0.5, H * 0.5, o, 1, scale=1.0 + 0.1 * u)
        # KREUZBERG dikey (sağ kenar)
        if 2.0 <= t <= T - 0.5:
            o = min(1, (t - 2.0) / 1.5) * min(1, (T - 0.5 - t) / 1.0) * 0.85
            lh = 72 * s
            top = H / 2 - lh * 4
            for i, tb in enumerate(kz):
                img = tb.draw(img, W - 70 * s, top + i * lh, o)
        return img

    return sh, grade, overlay, None, 'dream', dur


STYLES = dict(chrome=chrome, poster=poster, dream=dream)
