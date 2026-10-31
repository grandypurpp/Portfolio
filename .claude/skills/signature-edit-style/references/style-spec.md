# Style spec: exact values per tool

All timings assume 30fps (29.97). At 60fps, double the frame counts.

## Design tokens

| Token | Value |
|-------|-------|
| `--bg` | `#FDFBFE` |
| `--accent` | `#E70001` |
| `--accent-in` (pop-in start tint) | `#F2A0A6` |
| `--ink` (rare, for UI text only) | `#111111` |
| Sans | Satoshi Black / Inter Tight 800, tracking −0.03em, line-height 0.9 |
| Serif accent | Instrument Serif Italic, tracking −0.02em, ~85% of the sans size |
| Sizes @1080p | connector 40px · body 64px · keyword 180px · CTA serif 150px |
| Screen card | 76% width, radius 24px, shadow `0 30px 80px rgba(20,0,30,.12)` |
| Thumbnail chip | 112×112, radius 10px, border 3px `--accent` |

## Keyframes

**Word pop-in** (3 frames): this is the house signature.
- f0: scale 86%, opacity 0, Gaussian blur 6, color `#F2A0A6`, y +6px
- f3: scale 100%, opacity 100, blur 0, color `#E70001`, y 0
- Ease: out-expo / `cubic-bezier(0.2,0.9,0.1,1)`. After f3, nothing moves.

**Keyword slam** ("1st", "2nd"…, 4 frames): scale 120%→100%, opacity 0→100, blur 10→0. Trigger a soft pop SFX on f0.

**Screen card push**: scale 100%→104% linear over the whole shot. Position fixed.

**Swipe** (6 frames): the incoming card starts at x = +110% width, 6px red border, directional blur 60px. f3 at center with blur 40. f6 exits at x = −110%, and the next shot is revealed underneath on f4. Whoosh SFX starts 2 frames before f0.

**Montage beats**: in list montages (models, fonts), hard-cut exactly on each beat (16 frames @112 BPM). No movement inside a shot except the 100→104% push.

## Premiere Pro

- Text: Essential Graphics, one layer per word. Keyframe Scale/Opacity in Motion and add Gaussian Blur. Copy-paste the 3-frame pop to every word. Easing: Bezier, ease-in on the outgoing handle at 85% influence.
- Beat markers: run `analyze.py` with `--markers-csv` and import as sequence markers (or press M on each beat while playing).
- Swipe: Transform effect (Position + Shutter Angle 360, uncheck "Use Composition's Shutter Angle"), or a Film Impact push.

## DaVinci Resolve

- Text+ per word in Fusion. Use Transform + Blur nodes and a 3-frame keyframe, then save as a Macro ("Pop Word").
- Use the timeline marker import from the CSV for beats.
- Swipe: Transform node with Motion Blur on (Quality 10, Shutter Angle 360).

## After Effects

- Text layer, Animator (Scale, Opacity, Blur, Fill Color) with Range Selector by Words. Easiest option: split per word with keyframes at word start times from the JSON.
- Swipe: Transform effect with shutter 360, or enable Motion Blur on the layer.

## CapCut

- Auto captions → split into one word per clip → per-word animation "Pop up", 0.1s. Set the font colors to the tokens above.
- Beat sync: Music → Beats (Auto, Mode 2), then cut to the markers. Keep any cut that lands on a spoken word even if it's off the marker.

## Grade & texture

- Footage: clean, neutral, slightly lifted blacks. No heavy LUTs.
- Optional analog pass on B-roll only: FILM LOOKS grain at 20% Overlay. Never put it on white text cards.
- Stylized inserts: Grainrad ASCII/dither renders, ≤1.5s, cut on the beat.
