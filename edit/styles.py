"""Üç stilin kurgu listeleri, grade'leri ve tipografisi."""
import math, numpy as np, cv2
import lib
from engine import TextBlock, env

UNB = 'Unbounded-VF.ttf'; MAN = 'Manrope-VF.ttf'; ANT = 'Anton-Regular.ttf'
SER = 'InstrumentSerif-Regular.ttf'; SERI = 'InstrumentSerif-Italic.ttf'

# metinler (kolayca değiştirilebilir)
TXT = dict(
    city='BERLİN', date='KASIM 2026', brand='URBAN', brand2='STYLE',
    u_line1='SOKAKLAR', u_line2='KONUŞUR.',
    t_card1='HER SOKAĞIN', t_card2='BİR HİKÂYESİ VAR.', t_flash='STİL.', t_soon='YAKINDA',
    e_no='No. 01', e_issue='SOKAK PORTRELERİ', e_caption='Kasım, Berlin.',
)


def S(W, H):
    return min(W, H) / 1080


# =================================================================== URBAN
def urban(W, H):
    b = 60 / 92; bar = 4 * b
    B = lambda n: n * b
    hor = W > H
    sh = [
        dict(t0=0, t1=bar, clip='0566', src=(0.3, 2.3), z0=1.12, z1=1.22, tin='dip', td=0.9),
        dict(t0=bar, t1=2 * bar, clip='0577', src=(0.1, 2.4), z0=1.05, z1=1.18, dx0=0.02, dx1=-0.02, tin='xfade', td=0.5),
        dict(t0=2 * bar, t1=2 * bar + B(2), clip='0575', src=(0.3, 1.6), z0=1.1, z1=1.0, tin='zoom', td=0.25),
        dict(t0=2 * bar + B(2), t1=3 * bar, clip='0560', src=(0.0, 1.28), z0=1.0, z1=1.1, tin='whip', td=0.2),
        dict(t0=3 * bar, t1=3 * bar + B(2), clip='0582', src=(0.2, 1.85), ramp=0.6, z0=1.15, z1=1.0),
        dict(t0=3 * bar + B(2), t1=3 * bar + B(3), clip='0577', src=(1.6, 2.3), z0=1.3, z1=1.35),
        dict(t0=3 * bar + B(3), t1=4 * bar, clip='0566', src=(1.2, 1.9), z0=1.5, z1=1.6),
        dict(t0=4 * bar, t1=5 * bar, clip='0558', src=(0.2, 3.0), ramp=0.35, ramp_kind='mid', z0=1.0, z1=1.12, tin='zoom', td=0.22),
        dict(t0=5 * bar, t1=5 * bar + B(2), clip='0575', src=(1.3, 2.8), z0=1.15, z1=1.05, tin='whip', td=0.2),
        dict(t0=5 * bar + B(2), t1=6 * bar, clip='0562', src=(1.2, 2.75), ramp=0.5, z0=1.05, z1=1.15),
        dict(t0=6 * bar, t1=6 * bar + B(1), clip='0560', src=(0.4, 1.0), z0=1.2, z1=1.25, tin='zoom', td=0.15),
        dict(t0=6 * bar + B(1), t1=6 * bar + B(2), clip='0582', src=(0.9, 1.55), z0=1.0, z1=1.05),
        dict(t0=6 * bar + B(2), t1=6 * bar + B(3), clip='0562', src=(0.0, 0.6), z0=1.3, z1=1.35),
        dict(t0=6 * bar + B(3), t1=7 * bar, clip='0566', src=(0.5, 1.2), z0=1.1, z1=1.2),
        dict(t0=7 * bar, t1=8 * bar, clip='0558', src=(1.2, 2.4), ramp=0.5, z0=1.0, z1=1.25, tin='whipv', td=0.2,
             freeze=7 * bar + B(3)),
        dict(t0=8 * bar, t1=8 * bar + 2.0, black=True),
    ]
    dur = 8 * bar + 2.0
    # kick zamanları → hafif zoom nabzı
    kicks = []
    for k in range(2, 8):
        t0 = k * bar
        kicks += [t0, t0 + 1.75 * b] + ([t0 + 2.5 * b] if k % 2 else [])

    def pulse(t):
        v = 0.0
        for tk in kicks:
            if 0 <= t - tk < 0.4:
                v += math.exp(-(t - tk) * 10)
        return 0.018 * v

    vig = lib.vignette(W, H, 0.42)
    grain = lib.Grain(W, H, 12, 3, 1.5)

    def grade(img, t, s):
        x = np.clip(img, 0, 1)
        x = lib.skin_protect_teal_orange(x, 0.75)
        x = lib.contrast(x, 1.14, 0.40)
        x = lib.split_tone(x, (-0.015, 0.008, 0.035), (0.03, 0.012, -0.006), 0.45)
        x = lib.sat(x, 0.86)
        x = lib.halation(x, 0.78, 0.18, 14 * S(W, H))
        x = x * 0.95 + 0.028                   # mat siyahlar
        x = lib.chroma_ab(x, 1.6)
        return x * vig

    s = S(W, H)
    f_small = lib.font(MAN, int(26 * s), 700)
    f_big = lib.font(ANT, int((300 if not hor else 240) * s))
    f_mid = lib.font(UNB, int(86 * s), 700)
    f_mid2 = lib.font(UNB, int(86 * s), 300)
    tb = dict(
        tag=TextBlock(f"{TXT['city']}   ·   {TXT['date']}", f_small, (0.95, 0.93, 0.88), tracking=int(8 * s)),
        l1=TextBlock(TXT['u_line1'], f_mid, (0.97, 0.96, 0.93), tracking=int(4 * s)),
        l2=TextBlock(TXT['u_line2'], f_mid2, (0.42, 0.86, 0.86), tracking=int(4 * s)),
        big=TextBlock(TXT['brand'], f_big, (0.97, 0.96, 0.93), tracking=int(6 * s), stroke=max(2, int(3 * s)), stroke_color='outline'),
        big2=TextBlock(TXT['brand2'], lib.font(UNB, int(54 * s), 300), (0.42, 0.86, 0.86), tracking=int(30 * s)),
        endA=TextBlock(TXT['brand'] + ' ' + TXT['brand2'], lib.font(ANT, int(150 * s)), (0.97, 0.96, 0.93), tracking=int(6 * s)),
        endB=TextBlock(f"{TXT['city']}  ·  2026", lib.font(MAN, int(28 * s), 600), (0.42, 0.86, 0.86), tracking=int(14 * s)),
    )
    line_y = H * (0.80 if not hor else 0.78)

    def overlay(img, t, fi):
        # üst etiket
        r, o = env(t, 0.6, 4.6, 0.6, 0.5)
        if o:
            img = tb['tag'].draw(img, W / 2, H * 0.085, o * 0.9, r)
        # SOKAKLAR / KONUŞUR.
        r, o = env(t, 1.0, 4.9, 0.5, 0.3)
        if o:
            img = tb['l1'].draw(img, W / 2, line_y, o, r, shadow_op=0.4)
        r, o = env(t, 3.1, 4.9, 0.5, 0.3)
        if o:
            img = tb['l2'].draw(img, W / 2, line_y + 105 * s, o, r)
        # drop sonrası marka
        t0 = 4 * bar
        r, o = env(t, t0 + 0.25, 5 * bar - 0.15, 0.55, 0.15)
        if o:
            img = tb['big'].draw(img, W / 2, H * (0.70 if not hor else 0.66), o, r, scale=1 + 0.04 * (t - t0))
        r, o = env(t, t0 + 0.6, 5 * bar - 0.15, 0.5, 0.15)
        if o:
            img = tb['big2'].draw(img, W / 2, H * (0.70 if not hor else 0.66) + 190 * s, o, r)
        # kapanış kartı
        te = 8 * bar
        if t >= te:
            u = t - te
            r = min(u / 0.45, 1)
            img = tb['endA'].draw(img, W / 2, H / 2 - 30 * s, 1, r, scale=1.0 + 0.03 * u)
            r2 = min(max(u - 0.25, 0) / 0.5, 1)
            img = tb['endB'].draw(img, W / 2, H / 2 + 85 * s, r2, r2)
            # ince ayraç çizgisi
            ll = int(180 * s * lib.ease_out_expo(r2))
            if ll > 2:
                y = int(H / 2 + 50 * s)
                img[y:y + max(1, int(2 * s)), int(W / 2 - ll):int(W / 2 + ll)] = (0.42, 0.86, 0.86)
            fo = min(max((dur - t) / 0.7, 0), 1)
            img = img * fo
        img = grain.apply(img, fi, 0.032)
        return img

    return sh, grade, overlay, pulse, 'urban', dur


# ================================================================= TRAILER
def trailer(W, H):
    hor = W > H
    sh = [
        dict(t0=0, t1=2.0, clip='0566', src=(0.2, 1.6), z0=1.25, z1=1.38, tin='dip', td=1.2),
        dict(t0=2.0, t1=4.0, black=True),
        dict(t0=4.0, t1=6.0, clip='0577', src=(0.3, 1.7), z0=1.08, z1=1.25, tin='flash', td=0.35),
        dict(t0=6.0, t1=8.0, black=True),
        dict(t0=8.0, t1=9.0, clip='0575', src=(0.2, 1.4), z0=1.2, z1=1.05, tin='flash', td=0.3),
        dict(t0=9.0, t1=10.0, clip='0560', src=(0.0, 1.25), z0=1.0, z1=1.1),
        dict(t0=10.0, t1=11.0, clip='0582', src=(0.0, 1.0), z0=1.12, z1=1.0, tin='whip', td=0.18),
        dict(t0=11.0, t1=11.5, black=True),
        dict(t0=11.5, t1=12.0, clip='0562', src=(0.0, 0.5), z0=1.2, z1=1.25),
        dict(t0=12.0, t1=13.0, clip='0558', src=(0.0, 1.0), z0=1.1, z1=1.2, tin='whip', td=0.18),
        dict(t0=13.0, t1=14.0, clip='0577', src=(1.5, 2.5), z0=1.15, z1=1.05),
        dict(t0=14.0, t1=14.5, clip='0566', src=(1.5, 2.0), z0=1.4, z1=1.5, tin='zoom', td=0.15),
        dict(t0=14.5, t1=15.0, clip='0582', src=(1.0, 1.5), z0=1.0, z1=1.08),
    ]
    rapid = [('0575', 1.8, None), ('0560', 0.8, None), ('0562', 1.0, None), ('0558', 1.5, None),
             ('0577', 0.8, 0.36), ('0566', 0.3, None), ('0582', 1.4, None), ('0575', 2.3, 0.30)]
    for k, (c, s0, hfy) in enumerate(rapid):
        d = dict(t0=15 + k * 0.125, t1=15 + (k + 1) * 0.125, clip=c, src=(s0, s0 + 0.12), z0=1.25, z1=1.3)
        sh.append(d)
    sh.append(dict(t0=16.0, t1=17.0, black=True))
    pul = [17.0, 17.75, 18.4, 18.95, 19.4, 19.75, 20.05, 20.3, 20.5, 20.65, 20.8, 21.0]
    seq = [('0558', 1.8, None), ('0575', 2.0, 0.30), ('0560', 0.3, 0.27), ('0582', 0.4, None), ('0562', 0.8, None),
           ('0577', 2.0, 0.36), ('0566', 2.2, None), ('0558', 0.6, None), ('0575', 0.6, 0.30), ('0562', 1.6, None),
           ('0560', 0.9, 0.27)]
    for k, (c, s0, hfy) in enumerate(seq):
        d0, d1 = pul[k], pul[k + 1]
        d = dict(t0=d0, t1=d1, clip=c, src=(s0, s0 + (d1 - d0)), z0=1.3, z1=1.15, tin='zoom', td=min(0.14, (d1 - d0) * 0.6))
        sh.append(d)
    dur = 24.6
    sh.append(dict(t0=21.0, t1=dur, clip='0562', src=(1.15, 2.75), ramp=0.3, z0=1.0, z1=1.16, tin='flash', td=0.5,
                   fade_out=1.1))
    hits = [4.0, 8.0, 21.0]

    def pulse(t):
        v = 0
        for tk in [8 + k * 0.5 for k in range(16)]:
            if 0 <= t - tk < 0.3:
                v += math.exp(-(t - tk) * 14) * 0.6
        for tk in hits:
            if 0 <= t - tk < 0.8:
                v += math.exp(-(t - tk) * 5) * 2
        return 0.02 * v

    vig = lib.vignette(W, H, 0.55, 1.8)
    grain = lib.Grain(W, H, 12, 9, 1.4)
    rng = np.random.default_rng(5)
    flick = rng.normal(0, 1, 2000)
    lb = int(round((H - W / 2.39) / 2)) if hor else 0

    def grade(img, t, s):
        x = np.clip(img, 0, 1)
        L = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
        # bleach bypass: lüminansla karıştır
        x = x * 0.62 + np.clip(L * 1.0, 0, 1) * 0.38
        x = lib.contrast(x, 1.28, 0.38)
        x = lib.split_tone(x, (-0.02, 0.02, 0.05), (0.02, 0.025, 0.035), 0.42)
        x = lib.sat(x, 0.72)
        x = lib.bloom(x, 0.72, 0.25, 30 * S(W, H))
        if t < 8:   # giriş: hafif ışık titremesi
            x = x * (1 + 0.025 * flick[int(t * 30) % 2000])
        x = np.clip(x, 0, None)
        x = lib.chroma_ab(x, 2.2)
        return x * vig

    s = S(W, H)
    card = lib.font(UNB, int((64 if not hor else 58) * s), 300)
    cardB = lib.font(UNB, int((64 if not hor else 58) * s), 700)
    tb = dict(
        c1=TextBlock(TXT['t_card1'], card, (0.92, 0.93, 0.95), tracking=int(14 * s)),
        c2a=TextBlock('BİR HİKÂYESİ', cardB, (0.92, 0.93, 0.95), tracking=int(14 * s)),
        c2b=TextBlock('VAR.', card, (0.55, 0.80, 0.86), tracking=int(14 * s)),
        fl=TextBlock(TXT['t_flash'], lib.font(ANT, int(220 * s)), (0.95, 0.95, 0.95), tracking=int(8 * s)),
        title=TextBlock(TXT['brand'], lib.font(ANT, int((330 if not hor else 300) * s)), (0.96, 0.96, 0.96), tracking=int(20 * s)),
        title2=TextBlock(TXT['brand2'], lib.font(UNB, int(44 * s), 300), (0.55, 0.80, 0.86), tracking=int(40 * s)),
        endA=TextBlock(TXT['brand'] + ' ' + TXT['brand2'], lib.font(ANT, int((150 if not hor else 130) * s)), (0.97, 0.97, 0.97), tracking=int(10 * s)),
        endB=TextBlock(TXT['t_soon'], lib.font(UNB, int(40 * s), 600), (0.55, 0.80, 0.86), tracking=int(34 * s)),
    )

    def overlay(img, t, fi):
        if lb:
            img[:lb] = 0; img[H - lb:] = 0
        # kart 1
        if 2.0 <= t < 4.0:
            u = t - 2.0
            img = tb['c1'].draw(img, W / 2, H / 2, min(1, (4.0 - t) / 0.25), min(u / 0.7, 1), blur=max(0, 6 * (1 - u / 0.6)) * s)
        if 6.0 <= t < 8.0:
            u = t - 6.0
            o = min(1, (8.0 - t) / 0.2)
            img = tb['c2a'].draw(img, W / 2, H / 2 - 45 * s, o, min(u / 0.6, 1))
            u2 = max(u - 0.6, 0)
            img = tb['c2b'].draw(img, W / 2, H / 2 + 45 * s, o * min(u2 / 0.3, 1), min(u2 / 0.6, 1))
        if 11.0 <= t < 11.5:
            u = (t - 11.0) / 0.5
            img = tb['fl'].draw(img, W / 2, H / 2, 1, 1, scale=1.12 - 0.12 * lib.ease_out_expo(u * 2))
        if 16.0 <= t < 17.0:
            u = t - 16.0
            # başlık: genişleyen tracking hissi için ölçek + parlama
            sc = 0.94 + 0.08 * lib.ease_out_cubic(u)
            img = tb['title'].draw(img, W / 2, H / 2 - 20 * s, 1.0, 1.0, scale=sc, blur=max(0, 10 * (1 - u / 0.15)) * s)
            img = tb['title2'].draw(img, W / 2, H / 2 + 165 * s * sc, min(max(u - 0.15, 0) / 0.3, 1), 1)
            if u < 0.12:
                img = img + (1 - u / 0.12) * 0.6
        if t >= 21.6:
            u = t - 21.6
            o = min(1, (dur - 0.3 - t) / 0.9) if t > dur - 1.2 else 1
            y = H * (0.80 if not hor else 0.70)
            img = tb['endA'].draw(img, W / 2, y, o, min(u / 0.6, 1), shadow_op=0.6)
            img = tb['endB'].draw(img, W / 2, y + 120 * s, o * min(max(u - 0.5, 0) / 0.5, 1), min(max(u - 0.5, 0) / 0.6, 1))
        img = grain.apply(img, fi, 0.04)
        if lb:
            img[:lb] = 0; img[H - lb:] = 0
        return img

    return sh, grade, overlay, pulse, 'trailer', dur


# =============================================================== EDITORIAL
def editorial(W, H):
    b = 60 / 118; bar = 4 * b
    hor = W > H
    B = lambda n: n * b
    stack2 = [(0, 0, 1, 0.5), (0, 0.5, 1, 1)]
    side2 = [(0, 0, 0.5, 1), (0.5, 0, 1, 1)]
    stack3 = [(0, 0, 1, 1 / 3), (0, 1 / 3, 1, 2 / 3), (0, 2 / 3, 1, 1)]
    side3 = [(0, 0, 1 / 3, 1), (1 / 3, 0, 2 / 3, 1), (2 / 3, 0, 1, 1)]
    sh = [
        dict(t0=0, t1=2 * bar, clip='0558', src=(0.0, 3.2), z0=1.0, z1=1.08, tin='dip', td=0.8),
        dict(t0=2 * bar, t1=2 * bar + B(2), clip='0562', src=(0.3, 1.3), z0=1.08, z1=1.0),
        dict(t0=2 * bar + B(2), t1=3 * bar, clip='0575', src=(0.4, 1.4), z0=1.0, z1=1.06),
        dict(t0=3 * bar, t1=4 * bar, gap=6, bg=(0.93, 0.92, 0.89), panels=[
            dict(clip='0560', src=(0.0, 1.28), rect=stack2[0], hrect=side2[0], z0=1.0, z1=1.06, fy=0.30),
            dict(clip='0577', src=(0.4, 2.4), rect=stack2[1], hrect=side2[1], delay=B(0.5), z0=1.0, z1=1.06, fy=0.40),
        ]),
        dict(t0=4 * bar, t1=4 * bar + B(2), clip='0582', src=(0.2, 1.2), z0=1.06, z1=1.0),
        dict(t0=4 * bar + B(2), t1=5 * bar, clip='0566', src=(0.8, 1.8), z0=1.0, z1=1.1),
        dict(t0=5 * bar, t1=6 * bar, clip='0558', src=(1.0, 2.6), z0=1.05, z1=1.12, freeze=5 * bar + B(2)),
        dict(t0=6 * bar, t1=6 * bar + B(2), clip='0575', src=(1.6, 2.6), z0=1.1, z1=1.0),
        dict(t0=6 * bar + B(2), t1=7 * bar, clip='0562', src=(1.6, 2.6), z0=1.0, z1=1.08),
        dict(t0=7 * bar, t1=8 * bar, gap=6, bg=(0.93, 0.92, 0.89), panels=[
            dict(clip='0577', src=(1.0, 2.0), rect=stack3[0], hrect=side3[0], fy=0.36),
            dict(clip='0566', src=(0.4, 1.4), rect=stack3[1], hrect=side3[1], delay=B(0.5)),
            dict(clip='0560', src=(0.2, 1.2), rect=stack3[2], hrect=side3[2], delay=B(1), fy=0.27),
        ]),
        dict(t0=8 * bar, t1=9 * bar, clip='0582', src=(0.4, 1.85), ramp=0.5, z0=1.0, z1=1.1, freeze=8 * bar + B(3)),
        dict(t0=9 * bar, t1=9 * bar + 2.7, black=True, color=(0.93, 0.92, 0.89)),
    ]
    dur = 9 * bar + 2.7

    vig = lib.vignette(W, H, 0.38, 2.4)
    grain = lib.Grain(W, H, 12, 21, 1.2)

    def clip_fx(img, cid):
        x = np.clip(img, 0, 1)
        hsv = cv2.cvtColor(x.astype(np.float32), cv2.COLOR_RGB2HSV)
        h, sa, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
        dr = np.minimum(np.abs(h - 352), 360 - np.abs(h - 352))
        red = np.clip(1 - (dr - 7) / 5, 0, 1) * np.clip((sa - 0.42) / 0.12, 0, 1) * np.clip((v - 0.25) / 0.1, 0, 1)
        dor = np.abs(h - 24)
        orng = np.clip(1 - (dor - 6) / 6, 0, 1) * np.clip((sa - 0.78) / 0.08, 0, 1) * np.clip((v - 0.45) / 0.1, 0, 1)
        m = np.clip(red + orng, 0, 1) * (0.0 if cid in ('0577', '0560', '0575', '0566') else 1.0)
        m = cv2.GaussianBlur(m, (0, 0), 1.5)[..., None]
        bw = (x @ np.array([0.30, 0.55, 0.15], np.float32))[..., None]
        bw = lib.filmic(lib.contrast(bw, 1.22, 0.42), 0.35)
        bw = bw * np.array([1.0, 0.985, 0.955], np.float32) + 0.012   # hafif sıcak kâğıt tonu
        col = lib.sat(lib.contrast(x, 1.15, 0.42), 1.35)
        return bw * (1 - m) + col * m

    def grade(img, t, s):
        x = np.clip(img, 0, 1)
        if s.get('black'):
            return x
        return x * vig

    s = S(W, H)
    paper = (0.93, 0.92, 0.89)
    ink = (0.08, 0.08, 0.08)
    tb = dict(
        no=TextBlock(TXT['e_no'], lib.font(SERI, int(44 * s)), (0.97, 0.96, 0.94)),
        issue=TextBlock(TXT['e_issue'], lib.font(MAN, int(22 * s), 700), (0.97, 0.96, 0.94), tracking=int(9 * s)),
        big=TextBlock('Urban', lib.font(SERI, int((260 if not hor else 220) * s)), (0.97, 0.96, 0.94), shadow=8 * s),
        cap=TextBlock(TXT['e_caption'], lib.font(SERI, int(56 * s)), (0.97, 0.96, 0.94), shadow=6 * s),
        endA=TextBlock('Urban', lib.font(SERI, int((240 if not hor else 210) * s)), ink),
        endB=TextBlock(TXT['brand2'], lib.font(MAN, int(26 * s), 700), (0.75, 0.12, 0.12), tracking=int(30 * s)),
        endC=TextBlock(f"{TXT['date']}  —  {TXT['city']}", lib.font(MAN, int(22 * s), 500), ink, tracking=int(10 * s)),
    )
    m = int(36 * s)

    def frame_border(img, o):
        th = max(1, int(1.5 * s))
        c = np.array((0.97, 0.96, 0.94), np.float32) * o
        a = 1 - o
        for sl in (np.s_[m:m + th, m:W - m], np.s_[H - m - th:H - m, m:W - m], np.s_[m:H - m, m:m + th], np.s_[m:H - m, W - m - th:W - m]):
            img[sl] = img[sl] * a + c
        return img

    def overlay(img, t, fi):
        if t < 2 * bar:
            o = min(1, t / 0.8) * min(1, (2 * bar - t) / 0.2)
            img = frame_border(img, o * 0.9)
            img = tb['no'].draw(img, m + 30 * s, m + 50 * s, o, min(t / 0.6, 1), anchor='l')
            img = tb['issue'].draw(img, W - m - 30 * s, m + 50 * s, o, min(t / 0.6, 1), anchor='r')
            r, oo = env(t, 1.0, 2 * bar - 0.2, 0.7, 0.2)
            if oo:
                img = tb['big'].draw(img, W / 2, H * (0.82 if not hor else 0.74), oo, r, shadow_op=0.5)
        # dondurulmuş kare: fotoğraf çerçevesi + not
        fz = 5 * bar + B(2)
        if fz <= t < 6 * bar:
            u = t - fz
            k = lib.ease_out_expo(u / 0.4)
            inset = int((m * 1.4) * k)
            if inset > 0:
                img[:inset] = paper; img[H - inset:] = paper; img[:, :inset] = paper; img[:, W - inset:] = paper
                img[H - int(inset * 3.2):H - inset] = img[H - int(inset * 3.2):H - inset] * 0 + np.array(paper, np.float32) if not hor else img[H - int(inset * 3.2):H - inset]
            if u < 0.08:
                img = img + (1 - u / 0.08) * 0.5
            img = tb['cap'].draw(img, W / 2, H - inset * 2.1 if not hor else H * 0.84, min(max(u - 0.15, 0) / 0.4, 1),
                                 min(max(u - 0.15, 0) / 0.5, 1), color=ink if not hor else None,
                                 shadow_op=0 if not hor else 0.5)
        # son freeze: hafif flaş
        fz2 = 8 * bar + B(3)
        if fz2 <= t < fz2 + 0.1:
            img = img + (1 - (t - fz2) / 0.1) * 0.45
        if t >= 9 * bar:
            u = t - 9 * bar
            img = tb['endA'].draw(img, W / 2, H / 2 - 40 * s, 1, min(u / 0.7, 1))
            r = min(max(u - 0.35, 0) / 0.5, 1)
            img = tb['endB'].draw(img, W / 2, H / 2 + 110 * s, r, r)
            r2 = min(max(u - 0.6, 0) / 0.5, 1)
            img = tb['endC'].draw(img, W / 2, H / 2 + 165 * s, r2 * 0.8, r2)
            fo = min(max((dur - t) / 0.8, 0), 1)
            img = img * fo + np.array(paper, np.float32) * 0 * (1 - fo)
        img = grain.apply(img, fi, 0.045)
        return img

    return sh, grade, overlay, None, 'editorial', dur, clip_fx


STYLES = dict(urban=urban, trailer=trailer, editorial=editorial)
