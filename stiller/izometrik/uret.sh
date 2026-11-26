#!/usr/bin/env bash
# İzometrik şehir v3 — tüm mevsim artboard'larını ve render HTML'lerini üretir.
# kullanım: bash uret.sh [çıktı_klasörü]
set -e
cd "$(dirname "$0")"
OUT=${1:-out}; mkdir -p "$OUT"
for se in kis yagmur bahar sonbahar; do
  for m in v h; do
    python3 build3.py $m $se
    python3 iso3.py $m $se iso3_${m}_${se}.html > "$OUT/Izo3_${se}_${m}.dc.html"
    python3 ../../render/dc2html.py "$OUT/Izo3_${se}_${m}.dc.html" "$OUT/Izo3_${se}_${m}.html"
    rm -f iso3_${m}_${se}.html
  done
done
echo "Üretildi: $OUT"
