#!/bin/bash
# finish.sh reel|story -> out/DropLeaf_<v>.mp4 (music + SFX, -14 LUFS, IG-ready)
set -e; v=$1; cd "$(dirname "$0")"
python3 -I music.py out/${v}_cues.json out/${v}_audio.wav $v
ffmpeg -v error -y -i out/${v}_video.mp4 -i out/${v}_audio.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=7" -ar 48000 -c:a aac -b:a 256k -shortest -movflags +faststart out/DropLeaf_${v}.mp4
