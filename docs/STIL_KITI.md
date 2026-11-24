# Animasyon Stil Kiti — Claude Code Devir Belgesi

**Sahip:** Ömer Faruk Arslaner (16-18 Dijital) · **Durum:** Kasım 2026, onaylı stiller
**Amaç:** Türkçe seslendirmeli içeriklerden (podcast, belgesel, reels), sese senkron, premium kalitede animasyon videoları üretmek. Her stil ileride **farklı bir kanala** atanacak (eşleşme henüz belirlenmedi).

---

## 1. Değişmez kurallar

1. **Ses efekti (SFX) yok.** Yalnızca seslendirme + yumuşak müzik yatağı. Whoosh, parlama, çan, koro gibi sesler konuşmayı bastırdığı ve tınısı uymadığı için reddedildi.
2. **Ses her zaman önde.** Müzik konuşma sırasında ≈0.13, aralarda ≈0.34 (RMS konuşmaya eşitlendikten sonra). Master: `loudnorm=I=-14:TP=-1.2`.
3. **Türkçe karakterler kusursuz olmalı** (İ, ı, ş, ğ, Â). Fontlar yerel `@fontsource` paketleri; `latin` + `latin-ext` dosyaları `unicode-range` ile birlikte yüklenir.
4. **Format:** Dikey 1080×1920 ve yatay 1920×1080, 30 fps. Kalite için 1,5× süpersampling (1620×2880 render → lanczos ile küçült).
5. **Altyazı:** Karaoke tarzı. Konuşulan kelime vurgu rengiyle yanar, diğerleri soluk durur. Altyazı alt bantta (y≈1640) ve en fazla 2 satır.
6. Kullanıcı izleyip onaylamadan "mükemmel" deme; kontrol edilmesi gereken noktaları belirt.

---

## 2. Onaylı stiller (7)

| # | Stil | Görsel dil | Teknik çekirdek | Dosya |
|---|---|---|---|---|
| A | **3D Işık Heykeli (Neon Partikül)** | 18.000 ışık partikülü şekil ve figür oluşturur; neon pembe, mavi, altın ve turkuaz paletler | HDR splat + ACES, ışık/gölge, hareket bulanıklığı | `partikul_3d/engine6.html` |
| 02 | **Tek Çizgi** | Tek, kesintisiz altın kaligrafi çizgisi motif çizer (kalp → yol → kalp) | Yol örnekleme + kalem açısına bağlı genişlik | `stiller/s_cizgi.js` |
| 04 | **Kâğıt Katmanlar** | Papercut sahne, gölgeler, parallax; fabrika, bantlar, öne çıkan altın figür | Sprite + canvas shadow, katmanlar | `stiller/s_kagit.js` |
| 05 | **Gölge Oyunu** | Arkadan aydınlatılmış perde, Osmanlı kemeri, lale, kandil | Gerçek gölge fiziği: uzak = büyük + bulanık | `stiller/s_golge.js` |
| 06 | **Kutsal Geometri** | 8 köşeli Hatem/girih deseni merkezden büyür, ortada madalyon | Hankin yöntemi, 4.8.8 döşeme, 67,5° | `stiller/s_girih.js` |
| 07 | **İpek Çizgiler** | Binlerce ipek çizgi yağmur gibi akar, bir silueti (yüz profili) sarar | Akış alanı (curl) + SDF engeli | `stiller/s_ipek.js` |
| 08 | **Kinetik Tipografi** | Kelime kelime büyük tipografi, maske açılışları, zemin rengi değişimleri | Kelime zamanlarına bağlı sahneler | `stiller/s_kin.js` |

**Kullanılmayacaklar:** Ebru (`s_ebru.js`) ve Kum Animasyonu (`s_kum.js`). Bu iki dosya yalnızca `engine.html` bozulmasın diye kitte duruyor.

### A — 3D Işık Heykeli (son cila sürümü, v6)
- **Renderer:** Canvas 2D'de kendi HDR birikim tamponu var (Float32 RGB). Her partikül piksel altı hassasiyetle Gauss splat olarak eklenir. Ton eşleme %72 parlaklığı koruyan + %28 kanal başına ACES karışımıdır. Bu sayede yoğun bölgeler beyaza patlamaz, renk korunur.
- **Partiküller:** ≈18.000 (dikey). Çekirdek σ = r·0,42. Odak dışı partiküller σ·(1+bulanıklık·3,2) ile çizilir ve enerji korunur. Seyrek bokeh diskleri ve %0,8 yıldız parlaması vardır.
- **Işık:** Anahtar ışık sol üst önden, `LD=(-0.5,0.62,-0.6)`. Kenar ışığı `(1-|nz|)^2.2`. Normaller şekil merkezinden yaklaşık hesaplanır. Kelimelerde, gözde ve zemin gibi düz şekillerde ışık kapalıdır.
- **Diğer efektler:** Hareket bulanıklığı (1/30 sn obtüratör, hıza göre örnek sayısı), derinlik sisi, hafif curl akışı ("nefes alan ışık"), kenarlarda kromatik aberasyon (≈2 px), bloom, ayna zemin.
- **Kamera:** Serbest orbit. Kelime, göz ve el gibi "yüz" şekillerinde kamera önden bakar (`FACE` ağırlıkları). `PB` ile eğim ayarlanır. Ayrıca yavaş dolly vardır.
- **Şekil kütüphanesi:**
  - **Temel:** küre, galaksi, düğüm, terazi, göz, kalp (şişirilmiş 3D), iki kalp + yol, sarmal, DNA, yağmur, dalga, ızgara (fabrika), kapı, taç, çiçek, ağ, bölünme, dağılma, partiküllerle kelime (`word:METİN`).
  - **Figürler:**
    - `figure`: duran insan; kapsül ve elipsoidlerden, %30'u hacim dolgulu.
    - `figure_open`: kolları açık insan.
    - `figures2`: yan yana iki kişi.
    - `crowd`: 15 aynı figür.
    - `profile`: 2D profil şişirilerek elde edilen yüz.
    - `hands`: dua gibi açılan iki el; parmaklar 3 eklemli, açılma animasyonlu, avuçtan ışık yükselir.
- **Palet:** Sahne (cue) değişince partikül partikül yeni palete geçer. Stiller:
  - A: Eisweiß / turkuaz / altın
  - B: neon pembe / elektrik mavisi / mor (pleksus çizgileri, iz, retro ızgara zemin)
  - C: altın / krem (ışık hüzmeleri)
  - M: karma
- **Başlık tipografisi:** Unbounded (Eisweiß + turkuaz). Altyazı: Manrope 700.
- **Cue sistemi:** `build_data.py`, cümle → şekil eşlemesini (`CUE`) zaman çizelgesine çevirir. Şekil, segment başlangıcından ~0,35 sn önce değişir.

### 02 — Tek Çizgi
- Lacivert radyal zemin, altın çizgi `#E9C27D`.
- Kalem genişliği `w·(0.28+0.72·|sin(açı−0.62)|)` (geniş uçlu kalem hissi). Bulanık kopya ile glow, kalem ucunda kıvılcım ve iz.
- Çizim bitince yol boyunca ilerleyen bir ışık atımı; kalplerin içi yumuşak altın dolgu ile nabız atar.

### 04 — Kâğıt Katmanlar
- Krem kâğıt gökyüzü, gölgeli kâğıt bulutlar ve iki tepe katmanı, dişlili ve dumanlı fabrika, 3 konveyör bant, aynı gri kâğıt figürler.
- Anahtar kelimede bir figür durur, altına döner, yükselir; arkasında güneş ışınları açılır.
- Sonraki anahtar kelimede renk, mesafeye göre gecikmeyle diğer figürlere yayılır (pastel palet).
- Kâğıt lifi dokusu `multiply` ile eklenir; sprite gölgeleri önceden render edilir.

### 05 — Gölge Oyunu
- Sıcak, titreyen perde (radyal `#FFEAB8 → #3A1606`) ve dokuma dokusu.
- Sivri kemer çerçeve `evenodd`, lale ve çimen silüetleri, sallanan kandil.
- **Gölge fiziği:** Işığa yakın (perdeden uzak) figür daha büyük, bulanık ve soluk görünür. Perdeye yaklaşınca keskinleşip normal boya döner. Ardından el omza konur (`personPath`, `armL`/`reach`).

### 06 — Kutsal Geometri
- Hankin: 4.8.8 döşemede her kenar ortasından ±67,5°'lik iki ışın çıkar; komşu kenarların ışınları kesişir; yıldız `[m0,P0,m1,P1,…]` olarak kurulur.
- Sekizgen yıldızlar turkuaz ve lapis arasında dönüşümlü, kare yıldızlar fildişi. Çizgiler çift bant: altın 5,5 px + koyu 1,3 px. Lapis zemin.
- Desen dash animasyonuyla merkezden büyür, ardından dolgular gelir. Zoom 1,5 → 1 ve yavaş dönüş.
- Madalyon: 16 köşeli + 8 köşeli yıldız ve 8 yapraklı rozet, `eBack` ile girer. Anahtar kelimede ("sultan") ışık patlaması ve ışınlar.

### 07 — İpek Çizgiler
- Akış alanı: aşağı yönlü temel akış + 4 sinüslü potansiyelin curl'ü.
- Engel: siluetin SDF'i (chamfer, 1/4 çözünürlük). Engele dik bileşen silinir, teğetsel bileşen güçlendirilir; çizgiler siluetin etrafından akar.
- 2.300 akım çizgisi × 58 adım × 9 px. Tohumlar zamanla aşağı kayar (yağmur). Renk x'e göre turkuaz → altın → pembe. Additive çizim, uç kısım parlak, üç kademe alfa.
- Ek olarak ince yağmur damlaları, altın kontur ve göz pırıltısı.
- Anahtar kelimede ("nasıl düşüyor") curl genliği artar, girdaplar oluşur.

### 08 — Kinetik Tipografi
- Unbounded (300/500/700) + Manrope. Alttan maskeyle kayarak açılış (`eExpo`).
- Dev "2" kontur ve "?" (sarı `#F5C542`). Zemin geçişleri: siyah → kırmızı daire açılımı ("HATA") → petrol çapraz silme ("düzeltebilirim").
- Harfler bulanıktan nete düşerek gelir; altın dalgalı alt çizgi çizilir. Kelime zamanları heceye göre hesaplanır (bkz. §3).

---

## 3. Üretim hattı

1. **Transkripsiyon (ASR).** HuggingFace bu ortamda engelli; GitHub release'leri açık.
   ```bash
   pip install sherpa-onnx soundfile --break-system-packages
   curl -L -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2
   curl -L -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx
   ```
   `asr/run.py`: Silero VAD ile segmentler çıkarılır, Whisper-small (tr, int8) ile yazıya dökülür ve `asr.json` üretilir. ASR hatalarını elle düzelt (`ses/texts.py`); emin olunmayan yerleri kullanıcıya bildir.
2. **Ses temizliği.** `ses/audio.py` şu zinciri uygular:
   - `highpass 70 + adeclick`
   - RNNoise (`pyrnnoise`, %90 ıslak)
   - `noisereduce` (stationary, 0.6)
   - EQ, exciter, deesser, 4 bantlı mcompand, compressor, hafif yankı, limiter
   - Duraklamalar 0,25–0,95 sn'ye kısaltılır, "ııı" gibi dolgular atılır.
   - Çıktılar: `voice.wav` + `timeline.json` (segmentler, ses zarfı).
3. **Kelime zamanlaması.** Segment içinde **hece** (Türkçe ünlü sayısı) oranına göre dağıtılır. Noktalamadan sonra duraklama ağırlığı eklenir (`,;:` 0,55; `.?!` 0,75).
4. **Müzik yatağı.** `ses/sfxlib.py → pad()` re minör akorlarla ambient pad üretir. Ducking ve loudnorm uygulanır. SFX fonksiyonları bu dosyada duruyor ama **kullanılmayacak**.
5. **Render.** Tek HTML motoru, deterministik `render(T)` ve `frame(T) → JPEG`. Playwright (Chromium) 2 paralel worker çalıştırır; kareler image2pipe ile doğrudan ffmpeg'e gider, diske jpg yazılmaz.
   - Encode: `libx264 -preset medium/slow -crf 16-17 -tune grain`, 4:2:0, lanczos küçültme.
   - Önizleme: `prev*.py` belirli zamanlarda kare alır; kontakt sayfası `ffmpeg tile` ile yapılır. Taşma, çakışma ve okunurluk kontrolü yapılmadan tam render başlatma.
6. **Süre bilgisi (2 CPU).**
   - Stil kiti 1,5× ile ≈ 3–4 kare/sn (91 sn video ≈ 11 dk).
   - 3D HDR partikül 1,5× ile ≈ 1,6 kare/sn. 7 dk'lık bölüm tek format için ≈ 2 saat.
   - Uzun renderları parçalara böl; ortam yeniden başlarsa yarım kalan parçayı tekrar render et.

### Fontlar
```bash
cd fonts && npm pack @fontsource/unbounded @fontsource/manrope @fontsource/instrument-serif
# her .tgz'yi aç → fonts/fontsource-<ad>/files/*.woff2
```
HTML dosyaları fontları `../fonts/...` yolundan yükler.

---

## 4. Kit içeriği

```
stil-kiti/
├─ CLAUDE_HANDOFF.md        ← bu belge
├─ partikul_3d/
│  ├─ engine6.html           3D HDR partikül motoru (figürler dahil, son sürüm)
│  ├─ data.js                örnek zaman çizelgesi + cue'lar (İrade bölümü)
│  ├─ render6.py / prev6.py  render ve önizleme (URL parametreleri: w,h,s=A|B|C|M,test)
├─ stiller/
│  ├─ engine.html, common.js 7 stil + kartlar için ortak motor (altyazı, etiket, grain, insan/profil çizimi)
│  ├─ s_cizgi.js s_kagit.js s_golge.js s_girih.js s_ipek.js s_kin.js   ← onaylı stiller
│  ├─ s_ebru.js s_kum.js     ← kullanılmayacak
│  ├─ s_cards.js             başlık ve kapanış kartları
│  ├─ build_showcase.py      blokları + sesi + data.js'yi üretir
│  └─ render.py / prev.py
├─ ses/   audio.py texts.py mix.py sfxlib.py build_data.py
└─ asr/   run.py
```
Not: Scriptlerde mutlak yollar (`/home/claude/v/...`) var; yeni ortamda proje köküne göre güncelle. `voice.wav`, `timeline.json` ve `asr.json` her yeni kayıt için yeniden üretilir.

---

## 5. Yeni video için hızlı akış
1. Kullanıcının ses dosyası(ları) → ASR → metni düzelt → `texts.py`.
2. `audio.py` ile temizle ve zaman çizelgesini çıkar.
3. Stili seç (kanala göre) ve cümle → görsel eşlemesini yaz (cue'lar ya da blok tanımları).
4. Önizleme karelerini kontrol et, sonra 1,5× tam render al. Dikey ve yatay ayrı ayrı.
5. Müzikli ve müziksiz iki versiyon ver. Dosya adı: `<kanal>_<bölüm>_<stil>_<format>.mp4`.

## 6. Açık noktalar
- Stil ↔ kanal eşleşmesi henüz belirlenmedi. Öneri:
  - Kutsal Geometri → Tercüman-ı Ahval
  - İpek Çizgiler veya 3D Partikül → Podcast
  - Kinetik Tipografi → Reels / alıntılar
  - Gölge Oyunu → Bizim Hikayemiz
  - Tek Çizgi → WeltRadar
  - Kâğıt Katmanlar → Gerçek mi Efsane mi
- "İrade" bölümündeki belirsiz ifade: "…iradenle **seçtiğin** bir süreç" kullanıcıya teyit ettirilmeli.
