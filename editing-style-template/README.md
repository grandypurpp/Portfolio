# Signature Edit Style: Remotion template

Recreates the house edit style from a timeline JSON: word-by-word kinetic punch text, "The 1st" title cards, screen recordings in floating rounded cards, thumbnail-chip cards, and the motion-blurred red-edge swipe. Style rules live in `.claude/skills/signature-edit-style/`.

## Quick start

```bash
npm install
npm run studio                       # preview the sample in the browser
npm run render                       # 16:9 → out/edit.mp4
npm run render:vertical              # 9:16 → out/edit-vertical.mp4
```

## Your own edit

1. Put your voiceover, music and screen recordings in `public/`.
2. Generate a draft timeline from the VO (word timestamps + beat grid + cut suggestions):
   ```bash
   pip install faster-whisper librosa
   python3 ../.claude/skills/signature-edit-style/scripts/analyze.py public/vo.wav --music public/bed.mp3 --out timeline.json
   ```
3. Edit `timeline.json`. Fill each `screen` scene's `src`. Set `"size": "xl"` on keywords and `"accent": true` on 1–2 italic-serif words per line. Add `chips`/`swipe` scenes where you want them. Set `audio.voice` / `audio.music` to the file names in `public/`.
4. Render: `npx remotion render SignatureEdit out/edit.mp4 --props=timeline.json`.

## Scene types

| type | fields | look |
|------|--------|------|
| `words` | `lines: Word[][]` | Off-white canvas. Each word pops in at its `start` (3-frame pop; `xl` words get a 4-frame slam). |
| `screen` | `src` (image or video), `trimStart?` | Rounded floating card at 76% width, slow 100→104% push |
| `chips` | `title`, `chips[]`, `chipTimes[]`, `caption?` | "5 websites" card. Thumbnails pop in on the beats. |
| `swipe` | `src` | Overlay. The card flies right→left with a red edge and a motion trail. Keep it ~0.2–0.3s, spanning a cut. |

`Word = { text, start, size?: "sm"|"md"|"lg"|"xl", accent?: boolean }`. Times are seconds from the start of the edit.

The music bed loops at `audio.musicVolume` (default 0.22) and ducks ~5 dB while words are on screen.

## Fonts

Inter Tight 800 + Instrument Serif Italic load from Google Fonts automatically. To use Satoshi (Fontshare), install it locally and change `tokens.sans` in `src/style.ts`.
