// PİLOT — Beşiktaş × Hapoel Beer Sheva · UEFA Avrupa Ligi lig aşaması 5. hafta
// 30 sn'lik motor testi (uzun bölümün açılışı + Shorts kesiti olarak da kullanılabilir).
// [DOĞRULA] işaretli bilgiler yayından önce resmî kaynaktan (UEFA/kulüp) teyit edilmeli.
window.EP = {
  id: 'bjk_hbs_fragman',
  brand: 'KIRK SEKİZ',   // kanal adı: KIRK SEKİZ (48) — maçtan 48 saat önce
  kicker: 'UEFA AVRUPA LİGİ · 5. HAFTA',
  infoLine: '26 KASIM · 20:45 TSİ · BATUM',
  wish: 'MAÇTAN SONRA BİRLİKTE BAKALIM', wishWord: 'birlikte',   // kanal tarafsız: takım tarafı tutulmaz
  home: { name: 'BEŞİKTAŞ', short: 'BJK', c1: '#F4F4F2', c2: '#0B0B0C', ring: '#FFFFFF' },
  away: { name: 'HAPOEL BEER SHEVA', lines: ['HAPOEL', 'BEER SHEVA'], short: 'HBS', c1: '#D9252F', c2: '#FFFFFF', ring: '#FF6B73' },
  spk: {
    A: { name: 'ANALİST', col: '#7FE3FF' },   // sakin, veri odaklı ses
    T: { name: 'TRİBÜN',  col: '#F4C653' },   // enerjik, taraftar sesi
  },
  rate: 5.6, gap: 0.32, lead: 0.7, tail: 2.4,   // hece/sn — TTS gelince _tl.js gerçek zamanları yazar

  segs: [
    { spk: 'T', text: 'Bu akşam Batum\'da iki farklı hikâye kesişiyor.' },
    { spk: 'A', text: 'İlk sekizi korumak isteyen Beşiktaş, ilk galibiyetini arayan Hapoel.' },
    { spk: 'A', text: 'Rakibin gözünden plan ne? Beşiktaş nerede üstünlük kurabilir?' },
    { spk: 'T', text: 'Üç kilit isim, tribün, hava ve kim nasıl oynarsa avantajı alır.' },
    { spk: 'T', text: 'Tam analiz kanalımızda. Uzun videoyu izle, skor tahminini yorumlara yaz!' },
  ],

  scenes: [
    { type: 'intro', seg: [0, 1] },
    { type: 'tactic', seg: [2, 2], formation: '4-2-3-1', title: 'PLAN NE?',
      beats: [
        { k: 'bitir', s: 2, w: 'rakib', camSeg: true, cutter: 'TROSSARD', finisher: 'FV', cross: 'beşiktaş', arrive: 'üstünlük', label: 'NEREDE ÜSTÜNLÜK?' },
      ] },
    { type: 'players', seg: [3, 3],
      items: [
        { nm: 'ORKUN', team: 'home', pos: '10', s: 3, w: 'üç', role: 'Oyun kurucu', ifc: 'Son pası doğru zamanda verirse', then: '?' },
        { nm: 'TROSSARD', team: 'home', pos: 'SLK', s: 3, w: 'tribün', role: 'Sol kanat', ifc: 'İçeri kat ederse', then: '?' },
        { nm: 'ZLATANOVIĆ', team: 'away', pos: 'FV', s: 3, w: 'kim', role: 'Forvet', ifc: 'Topu saklayabilirse', then: '?' },
      ] },
    { type: 'cta', seg: [4, 4], line1: 'TAM ANALİZ', line2: 'KANALDA · UZUN VİDEO', hint: 'aşağıdaki bağlantıdan izle' },
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
