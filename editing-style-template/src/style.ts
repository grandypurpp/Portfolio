import { loadFont as loadSans } from "@remotion/google-fonts/InterTight";
import { loadFont as loadSerif } from "@remotion/google-fonts/InstrumentSerif";

const sans = loadSans("normal", { weights: ["600", "800"], subsets: ["latin"] });
const serif = loadSerif("italic", { weights: ["400"], subsets: ["latin"] });

// Measured from the reference reel: see .claude/skills/signature-edit-style/references/style-spec.md
export const tokens = {
  bg: "#FDFBFE",
  accent: "#E70001",
  accentIn: "#F2A0A6",
  sans: sans.fontFamily,
  serif: serif.fontFamily,
  // font sizes at 1080px canvas height; scaled by height / 1080
  size: { sm: 40, md: 64, lg: 110, xl: 180 },
  popFrames: 3,
  slamFrames: 4,
  breathFrames: 4,
  cardWidth: 0.76,
  cardRadius: 24,
  pushScale: 0.04,
};

// cubic-bezier(0.2, 0.9, 0.1, 1): fast out, no overshoot
export const popEase = (t: number): number => {
  const c = Math.min(Math.max(t, 0), 1);
  return 1 - Math.pow(1 - c, 4);
};
