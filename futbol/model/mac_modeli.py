#!/usr/bin/env python3
"""KIRK SEKİZ maç modeli v1 — şeffaf, olasılıksal, kaynaklı.

1) Ön güç: Elo farkı (+ ev/tribün avantajı) → beklenen puan We.
2) We ve beklenen toplam golden iki takımın gol oranı (λ) çözülür (Poisson).
3) Güncel form, küçük örnek olduğu için lig ortalamasına büzülerek %25 ağırlıkla karıştırılır.
4) Bağlam çarpanları (eksikler, hava).
5) Parametre belirsizliği (Elo aralıkları) her simülasyonda yeniden çekilir; maç dakika dakika simüle edilir,
   öne geçen/geride kalan takımın atak oranı oyun durumuna göre değişir.
Çıktı: model/<ad>_sonuc.json + model/<ad>_rapor.md
    python3 futbol/model/mac_modeli.py futbol/model/bjk_hbs.json
"""
import json, sys, math
from pathlib import Path
import numpy as np

def we(dr): return 1 / (1 + 10 ** (-dr / 400))

def solve_lambdas(target_we, total):
    """Poisson iki takım: P(G)+0.5P(B) = target_we olacak şekilde λ_ev, λ_dep (λ_ev+λ_dep = total)."""
    k = np.arange(0, 15)
    lo, hi = -total * .95, total * .95
    for _ in range(60):
        s = (lo + hi) / 2; le, ld = (total + s) / 2, (total - s) / 2
        pe = np.exp(-le) * le ** k / np.array([math.factorial(i) for i in k]); pd = np.exp(-ld) * ld ** k / np.array([math.factorial(i) for i in k])
        M = np.outer(pe, pd); w = np.tril(M, -1).sum(); d = np.trace(M)
        if w + .5 * d < target_we: lo = s
        else: hi = s
    return (total + s) / 2, (total - s) / 2

def main(cfg_path):
    C = json.load(open(cfg_path)); rng = np.random.default_rng(C['tohum']); N = C['sim']
    L = C['lig_ort_gol_takim']; f = C['form']; wf = C['form_agirligi']
    # form temelli λ (çarpımsal: atak × rakip savunma / lig ort.)
    fe = (f['ev']['atilan'] / f['ev']['mac']) * (f['dep']['yenilen'] / f['dep']['mac']) / L
    fd = (f['dep']['atilan'] / f['dep']['mac']) * (f['ev']['yenilen'] / f['ev']['mac']) / L
    # parametre belirsizliği: Elo ve ev avantajı her simülasyon partisinde çekilir
    B = 400; per = N // B
    res = {k: 0 for k in ('G', 'B', 'M')}; scores = {}; ht00 = 0; path = {'ev_ilk': [0, 0, 0, 0], 'golsuz': [0, 0, 0, 0], 'dep_ilk': [0, 0, 0, 0]}
    dep_once = 0; btts = 0; over25 = 0; first_ev_30 = 0; lam_log = []
    gs = C['oyun_durumu']; h2 = gs['ikinci_yari_payi']
    mins = np.arange(90); wmin = np.where(mins < 45, (1 - h2) / 45, h2 / 45)   # dakika ağırlıkları
    for b in range(B):
        dr = rng.normal(C['elo_ev']['ort'], C['elo_ev']['ss']) - rng.normal(C['elo_dep']['ort'], C['elo_dep']['ss']) \
             + rng.uniform(C['ev_avantaji_elo']['min'], C['ev_avantaji_elo']['max'])
        le0, ld0 = solve_lambdas(we(dr), C['toplam_gol_onsel'])
        le = (1 - wf) * le0 + wf * fe
        ld = ((1 - wf) * ld0 + wf * fd) * C['eksik_etkisi']['dep_gol_carpani']
        lam_log.append((le, ld))
        # dakika dakika simülasyon (per maç)
        ge = np.zeros(per, int); gd = np.zeros(per, int); first = np.full(per, -1); first_min = np.full(per, 99)
        led_dep = np.zeros(per, bool); ht = None
        for m in range(90):
            diff = ge - gd
            me = np.where(diff < 0, gs['geride_atak'], np.where(diff > 0, gs['onde_atak'], 1.0))
            md = np.where(diff > 0, gs['geride_atak'], np.where(diff < 0, gs['onde_atak'], 1.0))
            se = rng.random(per) < le * wmin[m] * me
            sd = rng.random(per) < ld * wmin[m] * md
            new_first_e = (first < 0) & se & ~sd; new_first_d = (first < 0) & sd & ~se
            first = np.where(new_first_e, 1, np.where(new_first_d, 2, first)); first_min = np.where(new_first_e | new_first_d, m, first_min)
            ge += se; gd += sd; led_dep |= (gd > ge)
            if m == 44: ht = (ge.copy(), gd.copy(), first.copy())
        dep_once += led_dep.sum(); btts += ((ge > 0) & (gd > 0)).sum(); over25 += ((ge + gd) > 2).sum()
        first_ev_30 += ((first == 1) & (first_min < 30)).sum()
        hte, htd, htf = ht; ht00 += ((hte == 0) & (htd == 0)).sum()
        for key, mask in (('ev_ilk', htf == 1), ('golsuz', htf == -1), ('dep_ilk', htf == 2)):
            path[key][0] += mask.sum(); path[key][1] += (mask & (ge > gd)).sum(); path[key][2] += (mask & (ge == gd)).sum(); path[key][3] += (mask & (ge < gd)).sum()
        res['G'] += (ge > gd).sum(); res['B'] += (ge == gd).sum(); res['M'] += (ge < gd).sum()
        for a, c in zip(*np.unique(np.minimum(ge, 6) * 10 + np.minimum(gd, 6), return_counts=True)): scores[int(a)] = scores.get(int(a), 0) + int(c)
    T = per * B; p = lambda x: round(100 * x / T, 1)
    lam = np.array(lam_log)
    out = {
        'mac': C['mac'], 'simulasyon': T,
        'lambda': {'ev_ort': round(float(lam[:, 0].mean()), 2), 'dep_ort': round(float(lam[:, 1].mean()), 2),
                   'ev_aralik80': [round(float(x), 2) for x in np.percentile(lam[:, 0], [10, 90])],
                   'dep_aralik80': [round(float(x), 2) for x in np.percentile(lam[:, 1], [10, 90])]},
        'sonuc': {'ev_galibiyet': p(res['G']), 'beraberlik': p(res['B']), 'dep_galibiyet': p(res['M'])},
        'en_olasi_skorlar': [{'skor': f'{k // 10}-{k % 10}', 'p': p(v)} for k, v in sorted(scores.items(), key=lambda x: -x[1])[:6]],
        'ilk_yari_0_0': p(ht00), 'ev_ilk_gol_30dk_once': p(first_ev_30), 'dep_bir_an_onde': p(dep_once),
        'karsilikli_gol': p(btts), 'ust_2_5': p(over25),
        'senaryolar': {k: {'p': p(v[0]), 'kosullu': {'ev_galibiyet': round(100 * v[1] / max(v[0], 1), 1), 'beraberlik': round(100 * v[2] / max(v[0], 1), 1), 'dep_galibiyet': round(100 * v[3] / max(v[0], 1), 1)}} for k, v in path.items()},
        'varsayimlar': [C['elo_dep']['kaynak'], C['ev_avantaji_elo']['not'], C['eksik_etkisi']['not'], C['hava']['not'], f"Form ağırlığı %{int(wf * 100)} (4 maç küçük örnek)"],
    }
    base = Path(cfg_path).with_suffix('')
    json.dump(out, open(f'{base}_sonuc.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main(sys.argv[1])
