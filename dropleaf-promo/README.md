# Drop Leaf presale promo (Reel + Story)

Signature edit style: off-white canvas, one red accent, word-by-word pop text on a 112 BPM grid, floating photo cards, one swipe, and a Three.js breakdown of how the drop-leaf mechanism works.

- `edit.html`: the whole edit as a frame-accurate timeline (`?v=reel` 26s, `?v=story` 15.5s). Copy, timing and 3D moves are all in the `REEL` / `STORY` / `TRACKS` blocks at the top.
- `render.js`: renders frames in headless Chromium, then encodes them to `out/<v>_video.mp4` (`--stills 100,200` for test PNGs).
- `music.py`: an original lo-fi bed (no licensing) plus SFX placed from the edit's cue list.
- `finish.sh reel|story`: adds the music, normalizes to -14 LUFS / -1.5 dBTP, and writes `out/DropLeaf_<v>.mp4`.
- `img/`: product plates pulled from the original reel with the overlays inpainted out (`tools/plates.py`). Swap in raw photos or video at the same file names for higher quality.

```
npm install && node render.js reel && ./finish.sh reel
```
