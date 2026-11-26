# Motion Graphic Animasyon Motoru — Proje Hafızası

Bu repo, Türkçe seslendirmeli içeriklerden sese senkron, premium animasyon videoları üretmek içindir.
Tüm stil, teknik ve üretim hattı ayrıntıları: @docs/STIL_KITI.md

## Her oturumda geçerli kurallar (özet)
- SFX yok. Yalnızca seslendirme + yumuşak müzik yatağı. Ses her zaman önde (müzik konuşmada ≈0.13, aralarda ≈0.34; master `loudnorm=I=-14:TP=-1.2`).
- Türkçe karakterler (İ ı ş ğ Â) kusursuz: yerel `@fontsource`, `latin` + `latin-ext`.
- 30 fps, 1,5× süpersampling + lanczos. Karaoke altyazı, alt bant y≈1640, en fazla 2 satır.
- Kullanıcı izleyip onaylamadan "mükemmel" deme; kontrol noktalarını belirt.
- Ebru ve Kum stilleri kullanılmaz.

## Onaylı 7 stil
A 3D Işık Heykeli (Neon Partikül) · 02 Tek Çizgi · 04 Kâğıt Katmanlar · 05 Gölge Oyunu ·
06 Kutsal Geometri · 07 İpek Çizgiler · 08 Kinetik Tipografi

## Platformlar ve çıktı
| Platform | Format | Not |
|---|---|---|
| YouTube (uzun) | 1920×1080 yatay | Bölüm/belgesel/podcast |
| YouTube Shorts | 1080×1920 dikey | ≤60 sn |
| TikTok | 1080×1920 dikey | Altyazı ve önemli öğeler alt/sağ arayüz alanından uzak |
| Instagram Reels | 1080×1920 dikey | Kapak için 4:5 ortada güvenli alan |

Dosya adı: `<kanal>_<bölüm>_<stil>_<format>.mp4` — müzikli ve müziksiz iki versiyon.

## Stil ↔ kanal eşleşmesi (henüz kesinleşmedi — öneri)
- Kutsal Geometri → Tercüman-ı Ahval
- İpek Çizgiler veya 3D Partikül → Podcast
- Kinetik Tipografi → Reels / alıntılar
- Gölge Oyunu → Bizim Hikayemiz
- Tek Çizgi → WeltRadar
- Kâğıt Katmanlar → Gerçek mi Efsane mi

Kesinleşen eşleşmeleri bu tabloya işle.

## Futbol maç önü kanalı: KIRK SEKİZ (48)
- **Logo (onaylandı 26.11.2026): "İ Noktası"** — Playfair Display 900 serif "48" + altın top; yazı logosu Manrope 800 "KIRK SEKİZ", SEKİZ'deki İ'nin noktası altın top. Palet: fildişi `#F4EFE6`, lacivert `#14213D`, altın `#B08A3E` (videoda koyu zeminde `#D4AF5A`). Üretici: `futbol/brand/brand.html` (`brand.mjs`).
- **Tarafsız:** hiçbir takımın tarafı tutulmaz; "…'a başarılar" yok. Kapanış: "Skor tahminini yorumlara yaz; maçtan sonra birlikte bakalım."
- **Karizma:** TRİBÜN o bölümün Türk temsilcisinin taraftar sesi ("Haydi Kara Kartal, tarihinden al gücünü!"); her kulübe eşit doz, kulüpler birbirine karşı konumlanmaz. Banka: `docs/KANAL_FUTBOL.md` §9.
- **Format:** yatay uzun bölüm + dikey fragman (uzuna yönlendirir). **Analiz:** model arka planda (`futbol/model/`), ekranda/seste yüzde ve oran yok; anlatım "kim nasıl oynarsa avantajı alır".
- **Müzik yok (kullanıcı kararı, 26.11.2026):** KIRK SEKİZ videolarında müzik yatağı kullanılmaz; yalnızca seslendirme. Yüklenecek ana dosya `_muziksiz.mp4`.
- Ses: Chatterbox (`futbol/tts_chatterbox.py`), ANALİST = Fahrettin tınısı, TRİBÜN = Fettah tınısı, `--tempo 1.05`. Gemini anahtarı gelirse `tts_gemini.py`.
Strateji, bölüm şablonu ve üretim hattı: `docs/KANAL_FUTBOL.md` · Motor: `futbol/` (09 Taktik Tahta, video teması `neon`/lila). Taktik sahnesi veri dosyasındaki `beats` listesinden kurulur; kapanış yazısı `EP.wish` (sabit metin yok).
Python Playwright yok; önizleme/render Node ile: `node futbol/prev.mjs`, `node futbol/render.mjs`.
