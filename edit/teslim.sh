#!/bin/bash
# teslim kopyası: ≈20-25 Mbit/sn H.264 + ses -14 LUFS
in="$1"; out="$(dirname "$in")/teslim/$(basename "$in")"
ffmpeg -v error -y -i "$in" -c:v libx264 -preset slow -crf 18 -maxrate 25M -bufsize 50M -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -af "loudnorm=I=-14:TP=-1.2:LRA=11" -ar 48000 -c:a aac -b:a 256k -movflags +faststart "$out" && ls -la "$out"
