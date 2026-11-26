// Galatasaray × AEK Atina (deplasman) · UEFA Şampiyonlar Ligi lig aşaması 6. hafta · 8 Aralık 2026 Salı 23:00 TSİ · AEK Arena, Atina
// Hazırlık: 26.11.2026. Yayın T-2 = 6 Aralık. [DOĞRULA] alanlar T-2'de güncellenecek (muhtemel 11, sakatlar, AEK kadrosu).
// Kaynaklar: Fotomaç, Milliyet, A Spor (fikstür); Habertürk, Yeni Şafak (Aston Villa 1-0, Deniz Gül 77', 9 puan).
window.EP = {
  id: 'gs_aek',
  brand: 'KIRK SEKİZ',   // kanal adı: KIRK SEKİZ (48) — maçtan 48 saat önce
  kicker: 'UEFA ŞAMPİYONLAR LİGİ · 6. HAFTA',
  infoLine: '8 ARALIK · 23:00 TSİ · ATİNA',
  wish: 'MAÇTAN SONRA BİRLİKTE BAKALIM', wishWord: 'birlikte',   // kanal tarafsız
  home: { name: 'GALATASARAY', short: 'GS', c1: '#A90432', c2: '#FDB912', ring: '#FDB912' },
  away: { name: 'AEK ATİNA', lines: ['AEK', 'ATİNA'], short: 'AEK', c1: '#F4C20D', c2: '#111111', ring: '#FFE36E' },
  spk: { A: { name: 'ANALİST', col: '#7FE3FF' }, T: { name: 'TRİBÜN', col: '#F4C653' } },
  rate: 5.6, gap: 0.3, lead: 0.6, tail: 2.0,

  segs: [
    { spk: 'T', text: 'Galatasaray, Şampiyonlar Ligi\'nde Atina deplasmanında kritik bir geceye çıkıyor.' },
    { spk: 'A', text: 'Aston Villa\'yı yenen Galatasaray dokuz puanda. Hedef ilk sekiz, bu yüzden Atina\'dan puan şart.' },
    { spk: 'T', text: 'AEK Arena, Avrupa\'nın en ateşli tribünlerinden biri. Bu baskıyı yönetmek ilk sınav olacak.' },
    { spk: 'A', text: 'Önce rakibin gözünden bakalım: AEK, evinde tribünün enerjisiyle yüksek pres yapmak isteyecek.' },
    { spk: 'A', text: 'Bu yüzden plan net: ilk yirmi dakika sakin kalmak, Torreira ve Lemina ile oyunun temposunu kontrol etmek.' },
    { spk: 'A', text: 'Top kazanıldığında ise hızlı çıkış: Barış Alper ve Yunus, kanatlardaki boş alanlara koşacak.' },
    { spk: 'T', text: 'Ve bitiricilik: Yunus içeri kat ettiğinde, Deniz Gül ceza sahasında fırsat kollayacak.' },
    { spk: 'T', text: 'Üç senaryo var. Erken gol gelirse, Galatasaray Atina\'da maçı soğutmayı bilir.' },
    { spk: 'A', text: 'Skor uzun süre eşit kalırsa, sabır ve duran toplar belirleyici olur.' },
    { spk: 'T', text: 'Haydi Cimbom, Aslan bu gece Atina\'da kükresin!' },
    { spk: 'T', text: 'Skor tahminini yorumlara yaz; maçtan sonra birlikte bakalım.' },
  ],

  scenes: [
    { type: 'intro', seg: [0, 0] },
    { type: 'card',  seg: [1, 2],
      tiles: [
        { k: 'TARİH',   v: '8 Aralık', s: 'Salı' },
        { k: 'SAAT',    v: '23:00', s: 'TSİ' },
        { k: 'STAT',    v: 'AEK Arena', s: 'Atina · deplasman' },
        { k: 'PUAN',    v: '9', s: 'Galatasaray · 5 maç' },
        { k: 'SON MAÇ', v: '1-0', s: 'Aston Villa · Deniz Gül 77\'' },
        { k: 'HEDEF',   v: 'İlk 8', s: 'kalan 3 maç' },
      ],
      route: { a: 'İSTANBUL', b: 'ATİNA', km: '≈560 km', note: 'kuş uçuşu · deplasman' } },
    { type: 'tactic', seg: [3, 6], formation: '4-2-3-1',
      beats: [
        { k: 'rakip', s: 3, w: 'rakib', w2: 'yüksek', label: 'RAKİBİN GÖZÜNDEN',
          arrows: [[[.47, .42], [.24, .42]], [[.58, .72], [.30, .74]], [[.58, .28], [.30, .26]]] },
        { k: 'kur',   s: 4, w: 'torreira', focus: 'TORREIRA', label: '1 · TEMPO KONTROLÜ' },
        { k: 'kanat', s: 5, w: 'barış', camSeg: true, label: '2 · HIZLI ÇIKIŞ' },
        { k: 'bitir', s: 6, w: 'yunus', camSeg: true, cutter: 'YUNUS', finisher: 'DENİZ GÜL', cross: 'kat', arrive: 'fırsat', label: '3 · BİTİRİCİLİK' },
      ] },
    { type: 'scen', seg: [7, 8], title: 'KİM NASIL OYNARSA', sub: 'taktik yollar · tahmin değil',
      items: [
        { t: 'Erken gol', d: 'Galatasaray maçı soğutur, kontra alanı açılır', adv: 'home', w: 'erken', s: 7 },
        { t: 'Uzun süre eşitlik', d: 'Sabır ve duran toplar belirleyici', adv: 'even', w: 'eşit', s: 8 },
        { t: 'Geriye düşmek', d: 'AEK tribünü oyuna girer, risk artar', adv: 'away' },
      ] },
    { type: 'outro', seg: [9, 10] },
  ],

  // Muhtemel 11 — [DOĞRULA] Aston Villa maçı kadro haberleri çelişkili (Osimhen dizinden ameliyatlı, sağ bek ve forvet belirsiz).
  // Yayından 2 gün önce (6 Aralık) basın tahminleriyle güncellenecek. Forma numarası yazılmaz.
  lineupNote: 'MUHTEMEL 11 · ön tahmin · maç haftası güncellenecek',
  lineup: [
    { pos: 'KL',  nm: 'UĞURCAN',    x: .05, y: .50 },
    { pos: 'SĞB', nm: 'SĞ BEK ?',   x: .27, y: .88 },
    { pos: 'STP', nm: 'SÁNCHEZ',    x: .21, y: .63 },
    { pos: 'STP', nm: 'ABDÜLKERİM', x: .21, y: .37 },
    { pos: 'SLB', nm: 'EREN',       x: .27, y: .12 },
    { pos: 'ÖL',  nm: 'TORREIRA',   x: .38, y: .40 },
    { pos: 'ÖL',  nm: 'LEMINA',     x: .38, y: .60 },
    { pos: '10',  nm: 'BATRAKOV',   x: .55, y: .50 },
    { pos: 'SĞK', nm: 'BARIŞ ALPER', x: .57, y: .84, run: [.80, .92] },
    { pos: 'SLK', nm: 'YUNUS',      x: .57, y: .16, run: [.80, .08] },
    { pos: 'FV',  nm: 'DENİZ GÜL',  x: .69, y: .50 },
  ],
  passes: [ [5, 6], [6, 7], [7, 8] ],   // TORREIRA → LEMINA → BATRAKOV → BARIŞ ALPER
  // AEK: kadro tahmini maç haftası; şimdilik isimsiz 4-3-3 yerleşimi
  opp: [ [.95,.5],[.82,.82],[.84,.62],[.84,.38],[.82,.18],[.72,.64],[.72,.36],[.66,.5],[.58,.72],[.58,.28],[.47,.42] ],
};
