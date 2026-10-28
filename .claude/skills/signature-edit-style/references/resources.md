# Toolkit: the 5 sites from the reference reel (+ music)

These were identified from the reel's screen recordings. The creator gated the list behind "comment TOOLS", but each site is visible on screen.

| # | Site | What it's for | How we use it |
|---|------|---------------|---------------|
| 1 | **Freesound**: https://freesound.org | ~600k free sound effects (footsteps, ambience, foley). The reel says "half a million". | Search the exact noun on screen ("footsteps", "ambience", "foley"). Filter by license: **CC0** for client work without attribution. CC-BY needs a credit line. Avoid CC-BY-NC on paid client work. Also good for pops, ticks and whooshes for cuts and swipes. |
| 2 | **Sketchfab**: https://sketchfab.com (filter: *Downloadable*) | Free 3D models: objects, scenes, whole environments | Download GLB/FBX, then Blender / After Effects (Element 3D) / Remotion `@remotion/three`. Check each model's license (CC-BY needs a credit). |
| 3 | **Grainrad**: https://grainrad.com | WebGPU, in-browser ASCII, dithering and retro/VHS looks at 60fps. No plugins. Exports PNG/JPEG/GIF/MP4/SVG/TXT/Three.js. | Drop footage in, pick ASCII / Dither / VHS (Distortion 0.5, Noise 0.3, Color Bleed 0.5, Scanlines 0.1), and export MP4 to use as a stylized insert or transition. Identified from the UI and the site's "WebGPU-powered ASCII, dithering, and retro effects at 60fps" tagline. |
| 4 | **FILM LOOKS**: https://filmlooks.com | Real film grain, burns and light leaks scanned from Super 8 / 16mm / 35mm. The free pack is $0. | Free pack: https://shop.filmlooks.com/p/film-grain-overlays-effects-8mm-16mm-35mm/. Lay grain in Overlay/Soft Light at 15–35% over footage. Use burns as transitions in Screen mode. Keep grain **off** the clean white text cards so the house look stays crisp. |
| 5 | **Fontshare**: https://www.fontshare.com | 100+ free fonts by Indian Type Foundry, sorted by mood, with pairings | Shown in the reel: Satoshi, Clash Display, General Sans, Cabinet Grotesk, Chillax, Ranade, Clash Grotesk, Switzer. Free for commercial use under the ITF Free Font License. Download per machine, don't commit font files to repos. |

## House fonts

- **Sans (keywords, connectors)**: Satoshi Black/Bold (Fontshare). Free fallback with no download: *Inter Tight* 800 (Google Fonts, OFL). Tracking −2% to −3%.
- **Italic serif accent**: *Instrument Serif Italic* (Google Fonts, OFL). It matches the reel's condensed italic serif. Alternatives: Ranade Italic (Fontshare), Times New Roman Condensed Italic.

## Music (recreating the bed without copying the track)

The reel's bed: ~**112 BPM**, minimal soft-kick chill/lo-fi electronic, sitting well under the VO, centered around G/F#. Instagram's metadata doesn't name the track, and we can't reuse a copyrighted song anyway. Use licensed tracks with the same feel:

- **YouTube Audio Library** (free, no attribution on most): search "chill", "lo-fi", tempo 105–118.
- **Pixabay Music** (free, commercial OK): "minimal lofi beat", "chill tech".
- **Uppbeat** (free tier with credit / paid for clients).
- **Artlist / Epidemic Sound / Musicbed** for client work that needs a clear commercial license.
- **Freesound** music loops: search "lofi loop 112 bpm", CC0 filter.

Selection checklist: 105–118 BPM. Clear, soft kick on every beat, which keeps beat detection reliable. No vocals. Sparse melody that won't fight the VO. Loopable 8-bar sections.
