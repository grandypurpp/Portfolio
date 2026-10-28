#!/usr/bin/env python3
"""Final render with speech enhancement as the LAST step.

    python3 finalize.py timeline.json [--vertical] [--strength medium] [-- <extra remotion args>]

1. Renders the locked cut from the timeline with the music muted (dialogue only).
2. Enhances just that rendered audio, so only what survived the edit is processed.
3. Mixes the music bed back in, ducked under the voice, and muxes onto the video.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATES = [
    HERE.parent / "scripts" / "enhance_audio.py",  # installed: ~/.claude/skills/signature-edit-style/template
    HERE.parent / ".claude" / "skills" / "signature-edit-style" / "scripts" / "enhance_audio.py",  # Portfolio repo
]


def main():
    argv = sys.argv[1:]
    extra = argv[argv.index("--") + 1:] if "--" in argv else []
    argv = argv[: argv.index("--")] if "--" in argv else argv
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("timeline", type=Path)
    ap.add_argument("--vertical", action="store_true")
    ap.add_argument("--strength", choices=["light", "medium", "strong"], default="medium")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)

    enhance = next((p for p in CANDIDATES if p.exists()), None)
    if not enhance:
        sys.exit("enhance_audio.py not found next to this template")

    timeline = json.loads(args.timeline.read_text())
    audio = timeline.get("audio") or {}
    music = audio.get("music")
    comp = "SignatureEditVertical" if args.vertical else "SignatureEdit"
    out = args.out or HERE / "out" / ("final-vertical.mp4" if args.vertical else "final.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as t:
        dry_props = Path(t) / "props.json"
        dry_props.write_text(json.dumps({**timeline, "audio": {**audio, "music": None}}))
        dry = Path(t) / "dialogue-cut.mp4"
        subprocess.run(["npx", "remotion", "render", comp, str(dry), f"--props={dry_props}", *extra],
                       cwd=HERE, check=True)

        cmd = [sys.executable, str(enhance), str(dry), "--out", str(out), "--strength", args.strength]
        if music:
            cmd += ["--music", str(HERE / "public" / music), "--music-volume", str(audio.get("musicVolume", 0.22))]
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
