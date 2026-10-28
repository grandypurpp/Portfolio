---
name: signature-edit-style
description: House video-editing style for all client and personal content: clean off-white canvas, single red accent, word-by-word kinetic "punch" text synced to voiceover, "The 1st / 2nd" title cards, screen recordings in floating rounded cards, motion-blurred swipe transitions, cuts driven by VO words that land on or off a ~112 BPM beat. Use whenever planning, scripting, cutting, captioning, animating, or rendering any video, reel, short, ad, or edit, or when the user asks for "my style", "the usual edit", a listicle/tools/tips video, or kinetic text.
---

# Signature Edit Style

The default look for every edit. Reference source: a 40s listicle reel ("5 websites pro editors use…", @rabinn.fx). Every number below was measured from that reel. See `references/reference-breakdown.md`.

## The look in one paragraph

Near-white canvas (`#FDFBFE`), one saturated red (`#E70001`), nothing else. Text appears **one word at a time, exactly when it's spoken**. Each word pops in over 2–3 frames (slightly smaller, pink and soft → full size, red and sharp). Key words are huge. Connector words ("The", "one", "but these are") are small. One or two emphasis words per line switch to a **condensed italic serif**. Demos are screen recordings in a **floating rounded card** (~24px radius, ~76% frame width) with a slow push-in. Section changes are a **hard cut to an empty canvas**, a 3–5 frame breath, then the title card builds word by word. A **motion-blurred swipe** (the next card flies in from the right with a red edge) marks the big beat after the hook. The music is a quiet ~112 BPM bed under the VO. SFX pops sit on the cuts.

## Rules (apply all of them by default)

1. **Voice drives the edit, not the music.** Cut on the first frame of the word that starts the new idea, 1–3 frames early (lead the word). If that word falls within ±2 frames of a beat, snap it to the beat (on-beat cut). Otherwise leave it off-beat. Aim for roughly a 50/50 mix. Never move a cut more than 3 frames just to hit a beat.
2. **Kinetic text = transcript.** Every on-screen word comes from word-level timestamps. A word appears at its `start` and stays until the line clears. Lines clear by hard cut, never by fade.
3. **Hierarchy per card**: small connector (≈40px at 1080p) / huge keyword (≈150–200px, weight 800) / small tail word. Example: `The` / `1st` / `one`.
4. **Italic serif accent**: 1–2 words per line (the "feeling" words: *never tell you about*, *frames*, *TOOLS*). Use a condensed italic serif, same red, set slightly smaller and tucked tight under or beside the sans.
5. **Pop-in keyframe** (per word, 3 frames at 30fps): scale 0.86→1.0, opacity 0→1, blur 6px→0, color `#F2A0A6`→`#E70001`, easing `cubic-bezier(0.2, 0.9, 0.1, 1)`. No bounce, no overshoot. Text stays still once it lands.
6. **Breath frames**: before each title card, hold 3–5 frames of empty canvas.
7. **Screen cards**: rounded corners, soft shadow, ~76% width, centered. Scale 1.00→1.04 over the shot (slow push). Cut inside a demo on each spoken list item ("footsteps", "ambience", "foley" each get their own search/result shot).
8. **Swipe transition** (use sparingly, once or twice per video): the next shot as a card with a 6px red border flies in from the right over ~4 frames with strong horizontal motion blur, overshoots off-frame left, and reveals the next shot. Add a whoosh SFX.
9. **Hook (0–5s)**: the claim builds word by word over a hero visual. Then a "N items" card shows thumbnail chips of every item popping in one per beat.
10. **CTA ending**: `comment` (sans) + `TOOLS` (huge italic serif) + small tail line (`and I'll DM you all five`). Hold until the VO ends.
11. **Music**: ~112 BPM minimal, soft-kick lo-fi / chill-electronic bed at about -18 to -22 LUFS under a VO at -14 LUFS. Duck 4–6 dB under speech. No vocals.
12. **SFX**: a soft pop/tick on every title-card cut and a whoosh on swipes. Optional quiet keyboard and mouse clicks in screen demos.
13. **Format**: 1920×1080 @ 29.97 for landscape. For 9:16, keep the same rules: text block centered at ~45% height, screen cards at 92% width.

## Workflow

1. **Analyze** the VO and music. Run `python3 scripts/analyze.py <voiceover_or_video> [--music music.mp3] --out timeline.json`. It writes word timestamps, the beat grid, and a suggested cut list with on/off-beat labels.
2. **Script the cards**: in the timeline JSON, group words into cards (`title`, `kinetic`, `screen`, `cta`) and mark `accent: true` on the serif words and `size: "xl"` on keywords.
3. **Render** with the Remotion template: `template/` next to this file once installed globally, or `editing-style-template/` in the Portfolio repo. See its README. Run `npx remotion render SignatureEdit out/edit.mp4 --props=timeline.json` (use `SignatureEditVertical` for 9:16).
4. **Self-check** before delivery. Is every word on screen within 1 frame of its spoken start? Are there no fades between sections? Is there only one accent color? Does each title card have a breath before it? Is the music ducked?

For Premiere/Resolve/CapCut/After Effects jobs, follow the same rules by hand. `references/style-spec.md` has the exact keyframe values for each NLE.

## Resources (the toolkit)

See `references/resources.md`: Freesound (SFX), Sketchfab (3D models), Grainrad (ASCII/dither/VHS looks in the browser), FILM LOOKS (free Super 8/16mm/35mm grain and burns), Fontshare (free fonts), plus music sources.
