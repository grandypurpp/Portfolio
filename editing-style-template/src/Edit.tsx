import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import { ChipsCard, ScreenCard, Swipe, WordsCard } from "./components";
import { tokens } from "./style";
import type { Scene, Timeline } from "./types";

const DUCK = 0.55; // ≈ -5 dB under speech
const DUCK_RAMP_FRAMES = 6;

const spokenTimes = (scenes: Scene[]): number[] =>
  scenes.flatMap((s) =>
    s.type === "words" ? s.lines.flat().map((w) => w.start) : s.type === "chips" ? [...s.title, ...(s.caption ?? [])].map((w) => w.start) : [],
  );

export const Edit: React.FC<Timeline> = (timeline) => {
  const { fps } = useVideoConfig();
  const speech = spokenTimes(timeline.scenes).sort((a, b) => a - b);
  const musicVolume = timeline.audio?.musicVolume ?? 0.22;

  // Duck the bed while words are being spoken (each word counts as ~0.45s of speech), with a short ramp.
  const duckAt = (f: number) => {
    const t = f / fps;
    let nearest = Infinity;
    for (const s of speech) {
      if (t >= s && t <= s + 0.45) return DUCK;
      nearest = Math.min(nearest, Math.abs(t - s), Math.abs(t - (s + 0.45)));
    }
    const ramp = Math.min(1, (nearest * fps) / DUCK_RAMP_FRAMES);
    return DUCK + (1 - DUCK) * ramp;
  };

  return (
    <AbsoluteFill style={{ backgroundColor: tokens.bg }}>
      {timeline.scenes.map((scene, i) => {
        const from = Math.round(scene.start * fps);
        const dur = Math.max(1, Math.round(scene.end * fps) - from);
        return (
          <Sequence key={i} from={from} durationInFrames={dur} layout="none">
            <AbsoluteFill style={{ zIndex: scene.type === "swipe" ? 10 : 1 }}>
              {scene.type === "words" ? <WordsCard scene={scene} sceneStartFrame={from} /> : null}
              {scene.type === "screen" ? <ScreenCard scene={scene} /> : null}
              {scene.type === "chips" ? <ChipsCard scene={scene} sceneStartFrame={from} /> : null}
              {scene.type === "swipe" ? <Swipe scene={scene} /> : null}
            </AbsoluteFill>
          </Sequence>
        );
      })}
      {timeline.audio?.voice ? <Audio src={staticFile(timeline.audio.voice)} /> : null}
      {timeline.audio?.music ? (
        <Audio src={staticFile(timeline.audio.music)} volume={(f) => musicVolume * duckAt(f)} loop />
      ) : null}
    </AbsoluteFill>
  );
};
