export type WordSize = "sm" | "md" | "lg" | "xl";

export type Word = {
  text: string;
  /** seconds from the start of the edit, i.e. when the word is spoken */
  start: number;
  size?: WordSize;
  /** italic serif accent word */
  accent?: boolean;
};

type Timed = { start: number; end: number };

export type WordsScene = Timed & { type: "words"; lines: Word[][] };
export type ScreenScene = Timed & {
  type: "screen";
  /** file in public/ or a URL; .mp4/.webm/.mov plays as video, anything else as an image */
  src: string;
  /** seconds into the source video to start from */
  trimStart?: number;
  note?: string;
};
export type ChipsScene = Timed & {
  type: "chips";
  title: Word[];
  /** thumbnails in public/, each pops in at the matching time in chipTimes */
  chips: string[];
  chipTimes: number[];
  caption?: Word[];
};
/** Overlay: the next shot flies across the frame with motion blur. Keep it ~0.2s. */
export type SwipeScene = Timed & { type: "swipe"; src: string };

export type Scene = WordsScene | ScreenScene | ChipsScene | SwipeScene;

export type Timeline = {
  fps: number;
  width: number;
  height: number;
  durationSec: number;
  bpm?: number;
  beats?: number[];
  audio?: { voice?: string | null; music?: string | null; musicVolume?: number };
  scenes: Scene[];
};
