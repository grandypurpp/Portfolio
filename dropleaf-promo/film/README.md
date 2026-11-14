# Drop Leaf Wall Table: cinematic product film (16:9, 40.5s)

A retailer and product-page cut. It uses the media and build sheet from sevenseasvans.com/drop-leaf-wall-table, and a Three.js model built to the page's own geometry: a 14 × 9 in top with 4.5 in self-bracing leaves.

- `film.html`: the whole film as a frame-accurate timeline. `SHOTS` sets the edit, `SH3D` sets the 3D camera and mechanism moves, `TX` and `CALLS` hold the copy.
- `render.js 16x9`: renders the full film in headless Chromium. `--stills 120,480` writes test PNGs, and `--range 240,500` re-renders one segment to splice in.
- `sound.py`: the fully synthesized score (pads, felt piano, pulse) and foley (hinge creak, wood knocks, steel clicks, whooshes), with a convolution reverb.
- `finish.sh 16x9`: adds the audio and normalizes it to -14 LUFS / -1.5 dBTP, then writes the poster frame.

Spec copy follows the site: Baltic birch, black steel hinges, 13 × 9 in braced top, 23 × 9 in flat on the wall, about 6 lb. The plywood thickness is left off on purpose (the site says 3/8").
