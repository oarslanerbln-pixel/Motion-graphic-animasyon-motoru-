// PİLOT — Beşiktaş × Hapoel Beer Sheva · UEFA Avrupa Ligi lig aşaması 5. hafta
// 30 sn'lik motor testi (uzun bölümün açılışı + Shorts kesiti olarak da kullanılabilir).
// [DOĞRULA] işaretli bilgiler yayından önce resmî kaynaktan (UEFA/kulüp) teyit edilmeli.
window.EP = {
  id: 'bjk_hbs_uzun',
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
    { spk: 'T', text: 'Avrupa Ligi\'nde iki farklı hikâye bu akşam Batum\'da kesişiyor.' },
    { spk: 'A', text: 'Bir yanda ilk sekiz yarışındaki Beşiktaş, diğer yanda hâlâ ilk galibiyetini arayan Hapoel Beer Sheva.' },
    { spk: 'T', text: 'Rakamlar, iki takımın planı, kilit oyuncular ve üç senaryo. Başlıyoruz.' },
    { spk: 'A', text: 'Maç, güvenlik gerekçesiyle İstanbul yerine Gürcistan\'ın Batum kentinde, tarafsız sahada oynanacak.' },
    { spk: 'A', text: 'Başlama saati Türkiye saatiyle yirmi kırk beş. Stat yaklaşık yirmi bin kişilik ve biletlerin büyük bölümü tükendi.' },
    { spk: 'T', text: 'Batum, Sarp sınır kapısına yaklaşık yirmi kilometre. Yani tribünde Türk taraftarların ağırlıkta olması bekleniyor.' },
    { spk: 'A', text: 'Hava açık, yağış beklenmiyor. Maç saatinde sıcaklık yaklaşık yedi derece, rüzgâr hafif.' },
    { spk: 'A', text: 'Puan tablosuna bakalım. Beşiktaş dört maçta yedi puan topladı ve şu an sekizinci sırada.' },
    { spk: 'A', text: 'Marsilya\'yı dört bir, Hoffenheim\'ı deplasmanda üç iki yendi. Crystal Palace ile iki iki berabere kaldı, Celtic\'e ise üç iki kaybetti.' },
    { spk: 'T', text: 'Hapoel\'in tablosu daha zor: dört maçta tek puan. Dinamo Zagreb ile golsüz berabere, ardından AZ, Union Saint-Gilloise ve OFI\'ye yenilgi.' },
    { spk: 'A', text: 'Yani iki takım için de bu maçın anlamı büyük. Beşiktaş ilk sekizi korumak, Hapoel ise ilk galibiyetini almak istiyor.' },
    { spk: 'A', text: 'Önce Hapoel\'in gözünden bakalım. Gol bulmakta zorlanan bir takım için en gerçekçi plan, kompakt savunup hızlı geçişlerle şans aramak.' },
    { spk: 'A', text: 'Orta sahada Amankwah ve Yehoshua\'nın önünde kalıp Beşiktaş\'ın top kayıplarını bekleyecek, sonra hızlı çıkmak isteyeceklerdir.' },
    { spk: 'T', text: 'Zlatanović ileride yalnız kalabilir, ama tek bir hızlı kontra bile maçın havasını değiştirebilir.' },
    { spk: 'A', text: 'Beşiktaş cephesinde Agbadou sakat, Ümit Akdağ cezalı. Rashica ve Mustafa Hekimoğlu da UEFA listesinde yok.' },
    { spk: 'A', text: 'Basına yansıyan muhtemel on bire göre kalede Nübel, savunmada Murillo, Djalo, Emirhan ve Rıdvan var.' },
    { spk: 'A', text: 'Plan net: Murillo ve Rıdvan kanatları genişletecek, Orkun oyunu sabırla kuracak.' },
    { spk: 'A', text: 'Top kaybedildiği an ilk beş saniye kritik. Anında pres, rakibe geçiş fırsatı vermemek.' },
    { spk: 'T', text: 'Ve bitiricilik: Trossard içeri kat ettiğinde, Vlahović ceza sahasında hazır bekliyor olacak.' },
    { spk: 'T', text: 'Şimdi maçın kaderini belirleyebilecek üç isme bakalım.' },
    { spk: 'A', text: 'Orkun oyunu sabırla kurar ve son pası doğru zamanda verirse, Hapoel\'in kompakt bloğu açılır.' },
    { spk: 'A', text: 'Trossard içeri kat edip şut tehdidi yaratırsa, bekler içeride kalır ve kanatlar boşalır.' },
    { spk: 'A', text: 'Hapoel tarafında Zlatanović topu saklayıp takımını öne taşıyabilirse, maç uzun süre dengede kalabilir.' },
    { spk: 'T', text: 'Tribünde ilginç bir tablo var: kâğıt üstünde ev sahibi Beşiktaş, ama saha tarafsız.' },
    { spk: 'T', text: 'Biletlerin büyük bölümü tükendi; yakın bölgelerden gelecek taraftarlar atmosferi belirleyecek.' },
    { spk: 'A', text: 'Soğuk ama açık bir hava, hızlı pas oyununa engel değil. Yağmur ya da ağır zemin faktörü beklenmiyor.' },
    { spk: 'A', text: 'Kâğıt üstünde favori Beşiktaş; güç farkı ve bu sezonki form aynı yönü gösteriyor. Ama bu tür maçlar çoğu zaman tek bir detayla döner.' },
    { spk: 'T', text: 'O yüzden asıl soru şu: kim nasıl oynarsa avantajı eline alır?' },
    { spk: 'A', text: 'Beşiktaş ilk yirmi dakikada kanatlardan sabırla yüklenir ve erken golü bulursa, Hapoel bloğunu bozup açılmak zorunda kalır. Bu, Beşiktaş\'ın en sevdiği senaryo.' },
    { spk: 'A', text: 'Ama Beşiktaş topa sahip olup ceza sahasına girmekte zorlanırsa, dakikalar ilerledikçe sabırsızlık başlar ve Hapoel\'in kontraları tehlikeli hale gelir.' },
    { spk: 'T', text: 'Hapoel savunma disiplinini altmışıncı dakikaya kadar korursa, maç bir duran topa ya da tek bir bireysel harekete kalabilir.' },
    { spk: 'A', text: 'Kilit an, top kayıplarından sonraki ilk saniyeler. Orada üstün gelen taraf maçın ritmini belirler.' },
    { spk: 'T', text: 'Bir sonraki durak: Beşiktaş on Aralık\'ta Leverkusen deplasmanında. O maçı da kırk sekiz saat önceden analiz edeceğiz.' },
    { spk: 'T', text: 'Skor tahminini yorumlara yaz; maçtan sonra birlikte bakalım.' },
  ],

  scenes: [
    { type: 'intro', seg: [0, 2] },
    { type: 'card', seg: [3, 6], chapter: { n: '01', t: 'MAÇ KARTI' },
      tiles: [
        { k: 'TARİH',    v: '26 Kasım', s: 'Perşembe' },
        { k: 'SAAT',     v: '20:45', s: 'TSİ · Batum 21:45' },
        { k: 'STAT',     v: 'Batum', s: 'tarafsız saha · Gürcistan' },
        { k: 'KAPASİTE', v: '≈20.000', s: 'biletler büyük ölçüde tükendi' },
        { k: 'HAVA',     v: '7°C', s: 'açık · yağış %0 · rüzgâr 7 km/sa' },
        { k: 'PUAN',     v: '7 – 1', s: 'Beşiktaş – Hapoel' },
      ],
      route: { a: 'İSTANBUL', b: 'BATUM', km: '≈1.050 km', note: 'Sarp sınır kapısı ≈20 km' } },
    { type: 'form', seg: [7, 10], chapter: { n: '02', t: 'TABLO VE FORM' },
      teams: [
        { side: 'home', pts: 7, rank: '8.', res: [ ['G', 'Marsilya', '4-1'], ['G', 'Hoffenheim (d)', '3-2'], ['B', 'Crystal Palace', '2-2'], ['M', 'Celtic (d)', '2-3'] ], w: 'beşiktaş', s: 7 },
        { side: 'away', pts: 1, rank: '33.', res: [ ['B', 'Dinamo Zagreb', '0-0'], ['M', 'AZ', '1-2'], ['M', 'Union SG', 'yenilgi'], ['M', 'OFI', '0-2'] ], w: 'hapoel', s: 9 },
      ] },
    { type: 'tactic', seg: [11, 13], formation: 'HAPOEL · KOMPAKT BLOK', title: 'RAKİBİN GÖZÜNDEN', chapter: { n: '03', t: 'RAKİBİN GÖZÜNDEN' },
      beats: [
        { k: 'rakip', s: 11, w: 'hapoel', w2: 'hızlı', label: 'KOMPAKT SAVUNMA · HIZLI GEÇİŞ' },
      ] },
    { type: 'tactic', seg: [14, 18], formation: '4-2-3-1', chapter: { n: '04', t: 'BEŞİKTAŞ\'IN PLANI' },
      beats: [
        { k: 'kanat', s: 16, w: 'kanat', camSeg: true, label: '1 · KANAT BİNDİRMESİ' },
        { k: 'kur',   s: 16, w: 'orkun', focus: 'ORKUN', label: '2 · SABIRLI OYUN KURMA' },
        { k: 'pres',  s: 17, w: 'pres', camSeg: true, label: '3 · 5 SANİYE PRES' },
        { k: 'bitir', s: 18, w: 'trossard', camSeg: true, cutter: 'TROSSARD', finisher: 'FV', cross: 'kat', arrive: 'hazır', label: '4 · BİTİRİCİLİK' },
      ] },
    { type: 'players', seg: [19, 22], chapter: { n: '05', t: 'ŞÖYLE OYNARSA' },
      items: [
        { nm: 'ORKUN', team: 'home', pos: '10', s: 20, w: 'orkun', role: 'Oyun kurucu', ifc: 'Son pası doğru zamanda verirse', then: 'Hapoel\'in kompakt bloğu açılır' },
        { nm: 'TROSSARD', team: 'home', pos: 'SLK', s: 21, w: 'trossard', role: 'Sol kanat', ifc: 'İçeri kat edip şut tehdidi yaratırsa', then: 'Bekler içeride kalır, kanatlar boşalır' },
        { nm: 'ZLATANOVIĆ', team: 'away', pos: 'FV', s: 22, w: 'zlatanovi', role: 'Forvet', ifc: 'Topu saklayıp takımı öne taşırsa', then: 'Maç uzun süre dengede kalır' },
      ] },
    { type: 'atmo', seg: [23, 25], chapter: { n: '06', t: 'TRİBÜN VE HAVA' },
      wx: { temp: '7°C', sky: 'Açık', rain: '%0', wind: '7 km/sa', hum: '%80', src: 'Open-Meteo tahmini · Batum 21:45 yerel' } },
    { type: 'balance', seg: [26, 27], chapter: { n: '07', t: 'FAVORİ VE GERÇEK' },
      lean: 0.68, note: 'arka planda: Elo + form + bağlam modeli · oran değil, eğilim' },
    { type: 'scen', seg: [28, 31], chapter: { n: '08', t: 'KİM NASIL OYNARSA' }, title: 'KİM NASIL OYNARSA', sub: 'taktik yollar · tahmin değil',
      items: [
        { t: 'Erken gol + kanat baskısı', d: 'Hapoel bloğu bozulur, açılmak zorunda kalır', adv: 'home', w: 'beşiktaş', s: 28 },
        { t: 'Kısır top hakimiyeti', d: 'Sabırsızlık başlar, kontralar tehlikeli', adv: 'away', w: 'ama', s: 29 },
        { t: '60. dakikaya kadar disiplin', d: 'Duran top ya da tek bireysel hareket', adv: 'even', w: 'hapoel', s: 30 },
      ] },
    { type: 'outro', seg: [32, 33] },
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
