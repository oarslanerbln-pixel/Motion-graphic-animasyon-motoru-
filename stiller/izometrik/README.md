# İzometrik Şehir (v3) — mevsim, hava, sevimli karakterler

10 sn'lik döngü: crane girişi → gün batımında sokak yakın planı (yayalar) → gece → tek pencereye 13× zoom (kitap okuyan karakter + kedi), alan derinliği bulanıklığı.

- `iso3.py <v|h> <kis|yagmur|bahar|sonbahar> <şablon>` — sahneyi üretir (binalar, gölgeler, trafik, yayalar, hava parçacıkları).
- `build3.py <v|h> <mevsim>` — mevsime göre gökyüzü, altyazı ve başlık şablonunu hazırlar.
- `uret.sh [klasör]` — 4 mevsim × dikey/yatay hepsini üretir; `.dc.html` (tasarım tuvali) + `.html` (render için).

Render (proje kökünden):
```bash
cd render
node render.js ../stiller/izometrik/out/Izo3_kis_v.html 540 960 3 30 10 ../cikti/test_mahalle-kis_izometrik_9x16_muziksiz.mp4 2 1080 1920
```
`render.js` tüm CSS animasyonlarını durdurup her kareye `currentTime` ile sarar (deterministik), 3× (=1,5× süpersampling) çekip lanczos ile küçültür. `muzik.py` re minör ambient pad üretir (SFX yok).
