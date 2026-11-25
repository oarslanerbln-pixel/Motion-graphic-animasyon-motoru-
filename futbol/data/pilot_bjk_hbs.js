// PİLOT — Beşiktaş × Hapoel Beer Sheva · UEFA Avrupa Ligi lig aşaması 5. hafta
// 30 sn'lik motor testi (uzun bölümün açılışı + Shorts kesiti olarak da kullanılabilir).
// [DOĞRULA] işaretli bilgiler yayından önce resmî kaynaktan (UEFA/kulüp) teyit edilmeli.
window.EP = {
  id: 'pilot_bjk_hbs',
  brand: 'MAÇ ÖNÜ',                 // kanal adı — henüz kesin değil
  kicker: 'UEFA AVRUPA LİGİ · 5. HAFTA',
  home: { name: 'BEŞİKTAŞ', short: 'BJK', c1: '#F4F4F2', c2: '#0B0B0C', ring: '#FFFFFF' },
  away: { name: 'HAPOEL BEER SHEVA', lines: ['HAPOEL', 'BEER SHEVA'], short: 'HBS', c1: '#D9252F', c2: '#FFFFFF', ring: '#FF6B73' },
  spk: {
    A: { name: 'ANALİST', col: '#7FE3FF' },   // sakin, veri odaklı ses
    T: { name: 'TRİBÜN',  col: '#F4C653' },   // enerjik, taraftar sesi
  },
  rate: 5.6, gap: 0.32, lead: 0.7, tail: 2.2,   // hece/sn — TTS gelince _tl.js gerçek zamanları yazar

  segs: [
    { spk: 'T', text: 'Beşiktaş yarın sahada. Ama ev sahibi olduğu hâlde İstanbul\'da değil, Batum\'da!' },
    { spk: 'A', text: 'Tarafsız saha, yirmi bin kişilik stat ve biletlerin büyük kısmı tükenmiş durumda.' },
    { spk: 'A', text: 'Plan net: Murillo ve Rıdvan kanatlardan bindirme, Orkun ile sabırlı pas, top kaybında beş saniye pres.' },
    { spk: 'T', text: 'Üç senaryo var. Erken gol gelirse maç tamamen bizim kontrolümüzde.' },
    { spk: 'T', text: 'Peki senin skor tahminin ne? Yorumlara yaz, Tahmin Ligi başlıyor!' },
  ],

  // Sahneler segmentlere bağlı: seg:[ilk, son]. Sahne, ilk segmentten ~0,35 sn önce başlar.
  scenes: [
    { type: 'intro', seg: [0, 0] },
    { type: 'card',  seg: [1, 1],
      tiles: [
        { k: 'TARİH',    v: '26 Kasım', s: 'Perşembe' },
        { k: 'SAAT',     v: '20:45', s: 'TSİ · [DOĞRULA]' },
        { k: 'STAT',     v: 'Batum', s: 'tarafsız saha · Gürcistan' },
        { k: 'KAPASİTE', v: '≈20.000', s: 'biletler büyük ölçüde tükendi' },
        { k: 'HAVA',     v: '≈11°C', s: 'Kasım iklim ort. · tahmin T-2' },
        { k: 'PUAN',     v: '7', s: 'Beşiktaş · galibiyet = 10' },
      ],
      route: { a: 'İSTANBUL', b: 'BATUM', km: '≈1.050 km', note: 'Sarp sınır kapısı ≈20 km' } },
    { type: 'tactic', seg: [2, 2], formation: '4-2-3-1',
      steps: [ { w: 'kanat', label: 'KANAT BİNDİRMESİ' }, { w: 'sabır', label: 'SABIRLI PAS' }, { w: 'pres', label: '5 SANİYE PRES' } ] },
    { type: 'scen', seg: [3, 3],
      items: [
        { t: 'Erken gol', d: 'Kontrol bizde, kontra alanı açılır', p: 45, c: '#78F0B4', w: 'erken' },
        { t: 'İlk yarı 0-0', d: 'Sabır ve duran toplar belirleyici', p: 35, c: '#F4C653' },
        { t: 'Geriye düşmek', d: 'Açık alan, kontra riski artar', p: 20, c: '#FF5D6C' },
      ] },
    { type: 'outro', seg: [4, 4] },
  ],

  // Taktik tahta: x 0→1 kendi kalesinden rakip kaleye, y 0→1 soldan sağa.
  // Muhtemel 11 — basın tahmini (Ajansspor/Türkgün/Duhuliye ortak listesi, 25.11.2026). Resmî kadro maç günü açıklanır.
  // Forma numaraları doğrulanmadığı için jetonda mevki (pos), altında isim (nm) gösterilir.
  lineupNote: 'MUHTEMEL 11 · basın tahmini · resmî kadro maç günü',
  lineup: [
    { pos: 'KL',  nm: 'NÜBEL',    x: .05, y: .50, px: .10, py: .50 },
    { pos: 'SĞB', nm: 'MURILLO',  x: .27, y: .88, px: .50, py: .90, run: [.62, .95] },
    { pos: 'STP', nm: 'DJALO',    x: .21, y: .63, px: .36, py: .62 },
    { pos: 'STP', nm: 'EMİRHAN',  x: .21, y: .37, px: .36, py: .38 },
    { pos: 'SLB', nm: 'RIDVAN',   x: .27, y: .12, px: .50, py: .10, run: [.62, .05] },
    { pos: 'ÖL',  nm: 'SALİH',    x: .38, y: .40, px: .55, py: .42 },
    { pos: 'ÖL',  nm: 'OLAITAN',  x: .38, y: .60, px: .55, py: .60 },
    { pos: '10',  nm: 'ORKUN',    x: .55, y: .50, px: .70, py: .52 },
    { pos: 'SĞK', nm: 'CERNY',    x: .57, y: .84, px: .74, py: .78, cut: [.70, .66] },
    { pos: 'SLK', nm: 'TROSSARD', x: .57, y: .16, px: .74, py: .22, cut: [.70, .34] },
    { pos: 'FV',  nm: 'VLAHOVIĆ', x: .69, y: .50, px: .82, py: .50 },
  ],
  passes: [ [5, 6], [6, 7], [7, 8] ],   // lineup index'leri: ÖN L → ÖN L → 10 → SĞK
  // Hapoel Beer Sheva muhtemel 11 (basın tahmini; mevki yerleşimi kanal yorumu)
  opp: [ [.95,.5,'MARCIANO'],[.82,.82,'MİZRAHİ'],[.84,.62,'VITOR'],[.84,.38,'ROTMAN'],[.82,.18,'AMADOR'],
         [.72,.64,'AMANKWAH'],[.72,.36,'YEHOSHUA'],[.63,.40,'EAST'],[.62,.72,'AHMED'],[.62,.28,'MALEDE'],[.47,.42,'ZLATANOVIĆ'] ],
};
