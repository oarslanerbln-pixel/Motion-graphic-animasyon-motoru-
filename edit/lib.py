"""Urban edit kütüphanesi: klip yükleme, renk eşitleme, slow-mo (optik akış),
kadraj/kamera, grade, gren, tipografi ve ffmpeg çıkışı."""
import subprocess, hashlib, glob, os, json, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPL = os.environ.get('UPL', '/root/.claude/uploads/32394b7e-4f29-547a-99a4-1c0cc1382169')
CACHE = os.environ.get('ECACHE', '/tmp/claude-0/-home-user-Motion-graphic-animasyon-motoru-/32394b7e-4f29-547a-99a4-1c0cc1382169/scratchpad/cache')
FONTS = os.path.join(ROOT, 'fonts', 'ttf')
FPS = 30
os.makedirs(CACHE, exist_ok=True)

# ---------------------------------------------------------------- klipler
# odak noktaları (kaynakta normalize x,y), zamanla anahtar kareler: [(t, x, y)]
CLIPS = {
    '0558': dict(log=False, hfy=0.42, focus=[(0, .47, .33)]),
    '0560': dict(log=False, hfy=0.3, focus=[(0, .40, .26)]),
    '0562': dict(log=False, hfy=0.42, focus=[(0, .36, .36), (2.8, .42, .36)]),
    '0566': dict(log=False, hfy=0.4, focus=[(0, .62, .40)]),
    '0575': dict(log=True, hfy=0.20,  focus=[(0, .60, .38)]),
    '0577': dict(log=True, hfy=0.4,  focus=[(0, .42, .40)]),
    '0582': dict(log=True,  focus=[(0, .44, .42), (0.9, .56, .42), (1.85, .66, .42)]),
}


def find_sources():
    """Yüklemelerden klip id → dosya (md5 ile tekrarlar elenir)."""
    seen, out = set(), {}
    for f in sorted(glob.glob(UPL + '/*.mp4')):
        h = hashlib.md5(open(f, 'rb').read()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        cid = os.path.basename(f).split('_')[4]
        out.setdefault(cid, f)
    return out


def _decode(f, w, h):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-map', '0:v:0',
                          '-vf', f'scale={w}:{h}:flags=lanczos', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb48le', '-'], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint16).reshape(-1, h, w, 3)
    return a


# ------------------------------------------------------- renk eşitleme (Lab)
def to_lab(x):
    return cv2.cvtColor(np.ascontiguousarray(x, np.float32), cv2.COLOR_RGB2Lab)


def from_lab(x):
    return np.clip(cv2.cvtColor(np.ascontiguousarray(x, np.float32), cv2.COLOR_Lab2RGB), 0, 1)


def lab_stats(frames):
    s = frames[:: max(1, len(frames) // 6)].astype(np.float32) / 65535
    L = np.concatenate([to_lab(f[::4, ::4]).reshape(-1, 3) for f in s])
    return L.mean(0), L.std(0), np.percentile(L[:, 0], [0.5, 99.5])


# filtreli kliplerin ortak hedefi (ölçülerek sabitlendi, bkz. match_target())
TARGET = None


def match_target(src):
    global TARGET
    p = os.path.join(CACHE, 'target.json')
    if os.path.exists(p):
        TARGET = json.load(open(p))
        return TARGET
    ms, ss = [], []
    for cid, c in CLIPS.items():
        if c['log']:
            continue
        a = _decode(src[cid], 216, 384)
        m, s, _ = lab_stats(a)
        ms.append(m); ss.append(s)
    TARGET = dict(mean=np.mean(ms, 0).tolist(), std=np.mean(ss, 0).tolist())
    json.dump(TARGET, open(p, 'w'))
    return TARGET


def filmic(x, k=1.0):
    """yumuşak omuzlu S-eğrisi (0..1)."""
    x = np.clip(x, 0, 1)
    s = x * x * (3 - 2 * x)
    return x + k * (s - x)


def normalize_clip(frames, log):
    """Tüm klibi ortak tabana getir: log → Reinhard (Lab) tam, filtreli → %35."""
    m, s, _ = lab_stats(frames)
    tm, ts = np.array(TARGET['mean']), np.array(TARGET['std'])
    w = 1.0 if log else 0.35
    out = np.empty(frames.shape, np.float16)
    for i, f in enumerate(frames):
        lab = to_lab(f.astype(np.float32) / 65535)
        g = (lab - m) / np.maximum(s, 1e-3) * ts + tm
        if log:
            # log tabanında ışıklar yumuşak kalsın: L için filmik sıkıştırma
            L = g[..., 0] / 100
            g[..., 0] = filmic(L, 0.25) * 100
        lab = lab * (1 - w) + g * w
        out[i] = from_lab(lab).astype(np.float16)
    return out


# ------------------------------------------------------------- klip önbelleği
class Clip:
    def __init__(self, cid, frames):
        self.id, self.f = cid, frames
        self.n = len(frames)
        self.h, self.w = frames.shape[1:3]
        self.dur = self.n / FPS
        self.flows = {}
        self.focus = CLIPS[cid]['focus']

    def focus_at(self, t):
        k = self.focus
        if len(k) == 1 or t <= k[0][0]:
            return k[0][1], k[0][2]
        for (t0, x0, y0), (t1, x1, y1) in zip(k, k[1:]):
            if t <= t1:
                u = (t - t0) / (t1 - t0)
                u = u * u * (3 - 2 * u)
                return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        return k[-1][1], k[-1][2]

    def _flow(self, i):
        if i not in self.flows:
            sc = 0.35
            a = cv2.cvtColor((self.f[i].astype(np.float32) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            b = cv2.cvtColor((self.f[i + 1].astype(np.float32) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            a = cv2.resize(a, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
            b = cv2.resize(b, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
            dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
            fw = dis.calc(a, b, None)
            bw = dis.calc(b, a, None)
            self.flows[i] = (fw / sc, bw / sc, sc)
        return self.flows[i]

    def frame(self, t):
        """Kaynak zamanı t (sn) → float32 RGB; ara karede optik akış interpolasyonu."""
        x = float(np.clip(t * FPS, 0, self.n - 1))
        i = int(math.floor(x)); u = float(x - i)
        if i >= self.n - 1 or u < 0.04:
            return self.f[min(i, self.n - 1)].astype(np.float32)
        if u > 0.96:
            return self.f[i + 1].astype(np.float32)
        fw, bw, sc = self._flow(i)
        H, W = self.h, self.w
        fw = cv2.resize(fw, (W, H)) ; bw = cv2.resize(bw, (W, H))
        if not hasattr(self, 'gx'):
            self.gx, self.gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        gx, gy = self.gx, self.gy
        A = self.f[i].astype(np.float32); B = self.f[i + 1].astype(np.float32)
        wa = cv2.remap(A, gx - fw[..., 0] * u, gy - fw[..., 1] * u, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        wb = cv2.remap(B, gx - bw[..., 0] * (1 - u), gy - bw[..., 1] * (1 - u), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return wa * (1 - u) + wb * u


_LRU = {}


def load(cid, src, out_w, out_h, headroom=1.3):
    """Klibi, çıkış kadrajına headroom'lu yetecek çözünürlükte yükle + normalize et."""
    key = (cid, out_w, out_h)
    if key in _LRU:
        return _LRU[key]
    pc = os.path.join(CACHE, f'{cid}_{out_w}x{out_h}.npy')
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=width,height', '-of', 'csv=p=0', src[cid]], capture_output=True, text=True).stdout
    sw, sh = map(int, probe.strip().split(',')[:2])
    cover = max(out_w / sw, out_h / sh)          # kaynağın çıkışı doldurduğu ölçek
    sc = min(1.0, cover * headroom)
    w, h = int(sw * sc) // 2 * 2, int(sh * sc) // 2 * 2
    if os.path.exists(pc):
        fr = np.load(pc, mmap_mode='r')
    else:
        raw = _decode(src[cid], w, h)
        fr = normalize_clip(raw, CLIPS[cid]['log'])
        np.save(pc, fr)
        del raw
        fr = np.load(pc, mmap_mode='r')
    c = Clip(cid, fr)
    if len(_LRU) > 3:
        _LRU.pop(next(iter(_LRU)))
    _LRU[key] = c
    return c


# ------------------------------------------------------------ kamera / kadraj
def place(img, clip, t, W, H, zoom=1.0, dx=0.0, dy=0.0, rot=0.0, fx=None, fy=None):
    """Kaynağı odak noktasına göre W×H'ye yerleştir (cover + zoom), sınır içinde tut."""
    h, w = img.shape[:2]
    cx, cy = clip.focus_at(t)
    if fx is not None: cx = fx
    if fy is not None: cy = fy
    s = max(W / w, H / h) * zoom
    # çıkış penceresinin kaynaktaki yarı boyutu
    hw, hh = W / s / 2, H / s / 2
    px = np.clip(cx * w + dx * w, hw, w - hw)
    py = np.clip(cy * h + dy * h, hh, h - hh)
    a = math.radians(rot)
    ca, sa = math.cos(a) * s, math.sin(a) * s
    M = np.array([[ca, -sa, W / 2 - (ca * px - sa * py)],
                  [sa, ca, H / 2 - (sa * px + ca * py)]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


# ------------------------------------------------------------- ease'ler
def ease_io(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def ease_out_expo(u):
    u = min(max(u, 0), 1); return 1 if u >= 1 else 1 - 2 ** (-10 * u)


def ease_in_expo(u):
    u = min(max(u, 0), 1); return 0 if u <= 0 else 2 ** (10 * u - 10)


def ease_out_cubic(u):
    u = min(max(u, 0), 1); return 1 - (1 - u) ** 3


# ------------------------------------------------------------- efektler
def vignette(W, H, strength=0.35, power=2.2):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    return (1 - strength * r ** power)[..., None].astype(np.float32)


class Grain:
    def __init__(self, W, H, n=12, seed=7, size=1.6):
        rng = np.random.default_rng(seed)
        self.t = []
        for _ in range(n):
            g = rng.standard_normal((int(H / size), int(W / size))).astype(np.float32)
            g = cv2.resize(g, (W, H), interpolation=cv2.INTER_CUBIC)
            g = cv2.GaussianBlur(g, (0, 0), 0.6)
            self.t.append(g / g.std())

    def apply(self, img, i, amt=0.035):
        g = self.t[i % len(self.t)][..., None]
        L = img.mean(2, keepdims=True)
        m = 4 * L * (1 - L) + 0.15          # orta tonlarda daha belirgin
        return img + g * amt * m


def radial_blur(img, amount, cx=0.5, cy=0.5, n=8):
    """zoom bulanıklığı (punch geçişleri için)."""
    if amount < 0.003:
        return img
    H, W = img.shape[:2]
    acc = img.copy()
    for k in range(1, n):
        z = 1 + amount * k / n
        M = np.array([[z, 0, (1 - z) * cx * W], [0, z, (1 - z) * cy * H]], np.float32)
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n


def dir_blur(img, dx, dy, n=9):
    """yönlü hareket bulanıklığı (whip geçişleri)."""
    if abs(dx) + abs(dy) < 1:
        return img
    H, W = img.shape[:2]
    acc = np.zeros_like(img)
    for k in range(n):
        u = k / (n - 1) - 0.5
        M = np.array([[1, 0, dx * u], [0, 1, dy * u]], np.float32)
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n


def chroma_ab(img, px):
    if px < 0.3:
        return img
    H, W = img.shape[:2]
    out = img.copy()
    for c, z in ((0, 1 + px / W), (2, 1 - px / W)):
        M = np.array([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]], np.float32)
        out[..., c] = cv2.warpAffine(np.ascontiguousarray(img[..., c]), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return out


def halation(img, thr=0.75, amt=0.25, sigma=18, tint=(1.0, 0.35, 0.15)):
    L = img.max(2)
    m = np.clip((L - thr) / (1 - thr), 0, 1)
    b = cv2.GaussianBlur(m, (0, 0), sigma)[..., None]
    return img + b * np.array(tint, np.float32) * amt


def bloom(img, thr=0.7, amt=0.2, sigma=25):
    m = np.clip(img - thr, 0, None)
    b = cv2.GaussianBlur(m, (0, 0), sigma)
    return img + b * amt


# ----------------------------------------------------------- grade araçları
def sat(img, k):
    L = (img @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    return L + (img - L) * k


def lift_gamma_gain(img, lift=(0, 0, 0), gamma=(1, 1, 1), gain=(1, 1, 1)):
    lift, gamma, gain = (np.array(v, np.float32) for v in (lift, gamma, gain))
    x = np.clip(img, 0, None) * gain + lift * (1 - np.clip(img, 0, 1))
    return np.power(np.clip(x, 0, None), 1 / gamma)


def split_tone(img, shadow=(0, 0.04, 0.06), high=(0.06, 0.03, -0.02), balance=0.5):
    L = (img @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    ws = np.clip(1 - L / balance, 0, 1) ** 1.5
    wh = np.clip((L - balance) / (1 - balance), 0, 1) ** 1.5
    return img + ws * np.array(shadow, np.float32) + wh * np.array(high, np.float32)


def contrast(img, k, pivot=0.45):
    return pivot + (img - pivot) * k


def skin_protect_teal_orange(img, amt=0.5):
    """Ten tonları korunur/hafif turuncuya, mavi-yeşil-camgöbeği teal'e çekilir.
    Dairesel hue mesafesi; kayma en fazla ~20°."""
    hsv = cv2.cvtColor(np.clip(img, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
    h, sa = hsv[..., 0], hsv[..., 1]
    def hd(a, b):
        return ((a - b + 180) % 360) - 180
    # ten (≈ -10°..45°): 25°'ye doğru hafif
    ds = hd(h, 22)
    ws = np.exp(-(ds / 26) ** 2) * 0.25
    # soğuk renkler (90°..260°): 195°'ye doğru
    dc = hd(h, 195)
    wc = np.exp(-(dc / 60) ** 2) * 0.45
    shift = -ds * ws - dc * wc
    shift = np.clip(shift, -20, 20) * amt * np.clip(sa * 4, 0, 1)
    hsv[..., 0] = (h + shift) % 360
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)


# ------------------------------------------------------------- tipografi
_FC = {}


def font(name, size, wght=None):
    key = (name, size, wght)
    if key in _FC:
        return _FC[key]
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    _FC[key] = f
    return f


def text_layer(W, H, items):
    """items: dict(text, font, x, y, anchor, fill(rgba), tracking) → RGBA float."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for it in items:
        f = it['font']; tr = it.get('tracking', 0)
        txt = it['text']
        if tr:
            # harf aralığı: tek tek çiz
            widths = [d.textlength(ch, font=f) for ch in txt]
            total = sum(widths) + tr * (len(txt) - 1)
            anc = it.get('anchor', 'mm')
            x0 = it['x'] - (total / 2 if anc[0] == 'm' else (total if anc[0] == 'r' else 0))
            for ch, cw in zip(txt, widths):
                d.text((x0, it['y']), ch, font=f, fill=it['fill'], anchor='l' + anc[1])
                x0 += cw + tr
        else:
            d.text((it['x'], it['y']), txt, font=f, fill=it['fill'], anchor=it.get('anchor', 'mm'))
    return np.asarray(im).astype(np.float32) / 255


def over(img, rgba, opacity=1.0):
    a = rgba[..., 3:4] * opacity
    return img * (1 - a) + rgba[..., :3] * a


# ------------------------------------------------------------- çıkış
class Writer:
    def __init__(self, path, W, H, audio=None, crf=16, dur=None):
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
        if audio:
            af = f'afade=t=out:st={dur-1.2:.3f}:d=1.2' if dur else 'anull'
            cmd += ['-i', audio, '-map', '0:v', '-map', '1:a', '-af', af, '-c:a', 'aac', '-b:a', '320k', '-shortest']
        cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-tune', 'grain',
                '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709',
                '-color_trc', 'bt709', '-movflags', '+faststart', path]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        self.rng = np.random.default_rng(1)

    def write(self, img):
        # 8-bit dither: bantlanmayı önler
        x = np.clip(img, 0, 1) * 255 + self.rng.random(img.shape[:2] + (1,), dtype=np.float32) - 0.5
        self.p.stdin.write(np.clip(x, 0, 255).astype(np.uint8).tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()
