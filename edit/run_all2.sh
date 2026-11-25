#!/bin/bash
cd "$(dirname "$0")"
M=../cikti/muzik
r(){ python3 render2.py $1 $2 --music $M --out ../cikti/urban_set2_$1_$3.mp4 > ../cikti/log2_$1_$2.txt 2>&1 && ./teslim.sh ../cikti/urban_set2_$1_$3.mp4 >> ../cikti/log2_$1_$2.txt 2>&1; }
(r chrome v dikey; r poster v dikey; r dream v dikey) &
(r chrome h yatay; r poster h yatay; r dream h yatay) &
wait
echo ALL2_DONE
