#!/bin/bash
cd "$(dirname "$0")"
M=../cikti/muzik
r(){ python3 render.py $1 $2 --music $M --out ../cikti/urban_set1_$1_$3.mp4 > ../cikti/log_$1_$2.txt 2>&1; }
(r urban v dikey; r trailer v dikey; r editorial v dikey) &
(r urban h yatay; r trailer h yatay; r editorial h yatay) &
wait
echo ALL_DONE
