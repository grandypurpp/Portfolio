# Reference reel: measured breakdown

Source: instagram.com/reel/DcYuWTST9U7 (@rabinn.fx, "5 websites pro editors use that nobody talks about"). 1916×1080, 29.97fps, 40.7s. Measured with ffmpeg scene detection, librosa beat tracking and Whisper word timestamps (`scripts/analyze.py`).

## Global numbers

- Background `#FDFBFE`. Accent red `#E70001`. Pop-in tint ≈ `#F2A0A6`.
- Music tempo **112.3 BPM** (beat every 0.534s ≈ 16 frames). Beat grid starts at 0.12s.
- VO pace ≈ 2.9 words/s. On-screen text tracks each word within **0–1 frame** of its spoken start (e.g. "No" spoken 23.66 → on screen 23.67; "plugins" 23.82 → 23.87).
- Average shot length ≈ 2.2s in demos, 0.5–0.6s in rapid list montages (3D models section).
- No fades or dissolves anywhere. Only hard cuts and one motion-blurred swipe.

## Structure

| Time | Section | Visual | Text on screen |
|------|---------|--------|----------------|
| 0.00–2.0 | Hook | Hero image (editor at monitors, cut out on white) | `Pro editors` (sans) + *never tell you about* (italic serif, tucked under) |
| 2.0–4.7 | Promise | "5 websites" + 5 thumbnail chips (red 3px border, 8px radius) popping in one per beat | `but these are the ones behind their best work` (small, word by word) |
| 4.73–4.93 | **Swipe** | Next card flies in from the right with red edge + heavy motion blur, ~6 frames | — |
| 5.0–5.9 | Title card | blank → `The` → `1st` → `one` | 3-tier hierarchy |
| 5.9–13.6 | Demo 1 (Freesound) | Screen card, sub-cuts per keyword typed in search: footsteps → ambience → foley | — |
| 13.67–14.33 | Title card | `The` / `2nd` | — |
| 14.33–19.0 | Demo 2 (Sketchfab) | Truck model (slow orbit) → rapid montage: plane / interior / cinema, one per beat | — |
| 19.02–19.55 | Title card | `The` / `3rd` | — |
| 19.55–23.5 | Demo 3 (Grainrad) | ASCII/VHS effect applied live | — |
| 23.56–26.0 | Kinetic line | `No plugins` → `runs at 60` *frames* `a second` | italic serif accent on "frames" |
| 26.0–26.46 | Title card | `The` / `4th` | — |
| 26.46–34.1 | Demo 4 (FILM LOOKS) | Scrolling film-strip page, then product pages | — |
| 34.13–34.5 | Title card | `The` (5th) | — |
| 34.5–38.3 | Demo 5 (Fontshare) | Font specimens swapping on the beat: Satoshi → Clash Display → General Sans → Cabinet → Ranade → Chillax → Clash Grotesk → Switzer | — |
| 38.4–40.7 | CTA | `comment` + *TOOLS* (big italic serif) + `and I'll DM you all five` | — |

## Cut list vs. beat grid (on-beat / off-beat)

Cut = first frame of new shot. Δ = cut minus nearest beat (frames @29.97).

| Cut (s) | Nearest beat | Δ frames | Type | VO word that triggers it |
|---------|--------------|----------|------|--------------------------|
| 14.35 | 14.44 | −3 | ON (leads beat) | "free"@14.48 |
| 16.88 | 16.90 | −1 | ON | "Objects"@16.96 |
| 17.42 | 17.44 | −1 | ON | "scenes"@17.52 |
| 18.08 | 17.97 | +3 | OFF | "whole"@18.04 |
| 19.02 | 19.04 | −1 | ON | "The third"@19.04 |
| 19.55 | 19.57 | −1 | ON | "turns"@19.60 |
| 23.56 | 23.78 | −7 | OFF | "No"@23.66 |
| 26.46 | 26.52 | −2 | ON | "real"@26.64 |
| 31.46 | 31.35 | +3 | OFF | end of "millimeters" |
| 34.13 | 33.95 | +5 | OFF | "And the fifth"@34.18 |

**Takeaway:** cuts are placed by the voice, 1–5 frames before the triggering word. About 60% happen to land on a beat because the VO is delivered roughly in time with the bed. Montages (3D models, fonts) are the exception and are cut strictly on the beat.

## Audio

- Strong transient hits (SFX/pops) at 5.9, 14.44, 16.9, 19.2 and 33.5s line up with cuts and title cards.
- The music bed's RMS is close to the VO's, but the VO stays fully intelligible: the bed is heavily low-passed and sparse.
- The VO is close-mic'd and dry, delivered fast and confident, with micro-pauses only before each "The Nth".

## Full transcript with word timings

See `reference-transcript.txt`.
