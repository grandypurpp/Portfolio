import React from "react";
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { popEase, tokens } from "./style";
import type { ChipsScene, ScreenScene, SwipeScene, Word, WordsScene } from "./types";

const resolveSrc = (src: string) => (/^https?:\/\//.test(src) ? src : staticFile(src));
const isVideo = (src: string) => /\.(mp4|webm|mov|m4v)$/i.test(src);

/** One word: invisible until spoken, then a 3-frame pop (or 4-frame slam for xl keywords). */
export const PopWord: React.FC<{ word: Word; sceneStartFrame: number }> = ({ word, sceneStartFrame }) => {
  const frame = useCurrentFrame() + sceneStartFrame;
  const { fps, width, height: h } = useVideoConfig();
  const height = Math.min(width, h); // type scales with the shorter side so 9:16 fits
  const at = Math.round(word.start * fps);
  if (frame < at) {
    // keep layout stable so earlier words don't jump when this one lands
    return <span style={{ ...wordStyle(word, height), visibility: "hidden" }}>{word.text}</span>;
  }
  const slam = word.size === "xl";
  const dur = slam ? tokens.slamFrames : tokens.popFrames;
  const t = popEase((frame - at) / dur);
  const scale = slam ? interpolate(t, [0, 1], [1.2, 1]) : interpolate(t, [0, 1], [0.86, 1]);
  const blur = interpolate(t, [0, 1], [slam ? 10 : 6, 0]);
  const y = slam ? 0 : interpolate(t, [0, 1], [6, 0]);
  return (
    <span
      style={{
        ...wordStyle(word, height),
        opacity: t,
        color: t >= 1 ? tokens.accent : mix(tokens.accentIn, tokens.accent, t),
        filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
        transform: `translateY(${y}px) scale(${scale})`,
      }}
    >
      {word.text}
    </span>
  );
};

const wordStyle = (word: Word, height: number): React.CSSProperties => {
  const k = height / 1080;
  const base = tokens.size[word.size ?? "md"] * k;
  return {
    display: "inline-block",
    fontFamily: word.accent ? tokens.serif : tokens.sans,
    fontStyle: word.accent ? "italic" : "normal",
    fontWeight: word.accent ? 400 : word.size === "sm" ? 600 : 800,
    fontSize: word.accent ? base * 1.05 : base,
    letterSpacing: word.accent ? "-0.02em" : "-0.03em",
    lineHeight: 0.95,
    color: tokens.accent,
    transformOrigin: "50% 70%",
    whiteSpace: "pre",
  };
};

const mix = (a: string, b: string, t: number) => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  return `rgb(${pa.map((v, i) => Math.round(v + (pb[i] - v) * t)).join(",")})`;
};

// word spacing scales with the biggest word on the line
const lineGap = (line: Word[], height: number) =>
  0.24 * Math.max(...line.map((w) => tokens.size[w.size ?? "md"])) * (height / 1080);

const Lines: React.FC<{ lines: Word[][]; sceneStartFrame: number }> = ({ lines, sceneStartFrame }) => {
  const { width, height: h } = useVideoConfig();
  const height = Math.min(width, h);
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 * (height / 1080) }}>
      {lines.map((line, i) => (
        <div key={i} style={{ display: "flex", alignItems: "baseline", justifyContent: "center", gap: lineGap(line, height) }}>
          {line.map((w, j) => (
            <PopWord key={j} word={w} sceneStartFrame={sceneStartFrame} />
          ))}
        </div>
      ))}
    </div>
  );
};

export const WordsCard: React.FC<{ scene: WordsScene; sceneStartFrame: number }> = ({ scene, sceneStartFrame }) => (
  <AbsoluteFill style={{ backgroundColor: tokens.bg, justifyContent: "center", alignItems: "center" }}>
    <Lines lines={scene.lines} sceneStartFrame={sceneStartFrame} />
  </AbsoluteFill>
);

/** Screen recording / image in a floating rounded card with a slow push-in. */
export const ScreenCard: React.FC<{ scene: ScreenScene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const total = Math.max(1, Math.round((scene.end - scene.start) * fps));
  const scale = interpolate(frame, [0, total], [1, 1 + tokens.pushScale], { extrapolateRight: "clamp" });
  const portrait = height > width;
  const cardW = width * (portrait ? 0.92 : tokens.cardWidth);
  const media: React.CSSProperties = { width: "100%", height: "100%", objectFit: "cover", display: "block" };
  return (
    <AbsoluteFill style={{ backgroundColor: tokens.bg, justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          width: cardW,
          aspectRatio: "16 / 9",
          borderRadius: tokens.cardRadius * (height / 1080),
          overflow: "hidden",
          boxShadow: "0 30px 80px rgba(20,0,30,.12)",
          transform: `scale(${scale})`,
          backgroundColor: "#0b0b0d",
        }}
      >
        {!scene.src ? (
          <Placeholder note={scene.note} />
        ) : isVideo(scene.src) ? (
          <OffthreadVideo src={resolveSrc(scene.src)} startFrom={Math.round((scene.trimStart ?? 0) * fps)} muted style={media} />
        ) : (
          <Img src={resolveSrc(scene.src)} style={media} />
        )}
      </div>
    </AbsoluteFill>
  );
};

const Placeholder: React.FC<{ note?: string }> = ({ note }) => (
  <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: 60, color: "#888", fontFamily: tokens.sans, fontSize: 28, textAlign: "center" }}>
    {note ? `[screen recording] ${note}` : "[screen recording]"}
  </AbsoluteFill>
);

/** "5 websites" card: title, thumbnail chips popping in one per beat, small caption. */
export const ChipsCard: React.FC<{ scene: ChipsScene; sceneStartFrame: number }> = ({ scene, sceneStartFrame }) => {
  const frame = useCurrentFrame() + sceneStartFrame;
  const { fps, width, height: h } = useVideoConfig();
  const height = Math.min(width, h);
  const k = height / 1080;
  return (
    <AbsoluteFill style={{ backgroundColor: tokens.bg, justifyContent: "center", alignItems: "center", gap: 36 * k, flexDirection: "column" }}>
      <Lines lines={[scene.title]} sceneStartFrame={sceneStartFrame} />
      <div style={{ display: "flex", gap: 18 * k }}>
        {scene.chips.map((src, i) => {
          const at = Math.round((scene.chipTimes[i] ?? scene.start) * fps);
          const t = popEase((frame - at) / tokens.popFrames);
          return (
            <div
              key={i}
              style={{
                width: 112 * k,
                height: 112 * k,
                borderRadius: 10 * k,
                border: `${3 * k}px solid ${tokens.accent}`,
                overflow: "hidden",
                opacity: frame < at ? 0 : t,
                transform: `scale(${interpolate(t, [0, 1], [0.8, 1])})`,
                backgroundColor: "#fff",
              }}
            >
              <Img src={resolveSrc(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            </div>
          );
        })}
      </div>
      {scene.caption ? <Lines lines={[scene.caption]} sceneStartFrame={sceneStartFrame} /> : null}
    </AbsoluteFill>
  );
};

/** Next shot flies right→left across the frame with a red edge and a motion trail. Overlay, no background. */
export const Swipe: React.FC<{ scene: SwipeScene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const total = Math.max(2, Math.round((scene.end - scene.start) * fps));
  const p = frame / total;
  const x = interpolate(p, [0, 0.5, 1], [1.1, 0, -1.1]) * width;
  const blur = interpolate(p, [0, 0.5, 1], [60, 40, 60]);
  const cardW = width * 0.62;
  const ghosts = 6;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      {Array.from({ length: ghosts }).map((_, g) => (
        <div
          key={g}
          style={{
            position: "absolute",
            width: cardW,
            aspectRatio: "16 / 9",
            borderRadius: 18 * (height / 1080),
            border: `${6 * (height / 1080)}px solid ${tokens.accent}`,
            overflow: "hidden",
            transform: `translateX(${x + g * blur * 1.5}px)`,
            opacity: (1 - g / ghosts) * 0.55,
            filter: `blur(${4 + g * 2}px)`,
          }}
        >
          <Img src={resolveSrc(scene.src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </div>
      ))}
    </AbsoluteFill>
  );
};
