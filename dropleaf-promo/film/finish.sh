#!/bin/bash
# finish.sh 16x9|9x16 -> out/DropLeaf_Film_<ar>.mp4 + poster
set -e; ar=$1; cd "$(dirname "$0")"
[ -f out/film_audio.wav ] || python3 -I sound.py out/film_audio.wav 40.5
ffmpeg -v error -y -i out/${ar}_video.mp4 -i out/film_audio.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=9" -ar 48000 -c:a aac -b:a 256k -shortest -movflags +faststart out/DropLeaf_Film_${ar}.mp4
ffmpeg -v error -y -ss 36.8 -i out/${ar}_video.mp4 -frames:v 1 -q:v 2 out/DropLeaf_Film_${ar}_poster.jpg
