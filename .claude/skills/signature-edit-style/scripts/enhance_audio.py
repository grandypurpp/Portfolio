#!/usr/bin/env python3
"""Final-pass speech enhancement: run it on the FINISHED cut, so only audio
that survived the edit gets processed (nothing wasted on trimmed footage).

    python3 enhance_audio.py final_cut.mp4 --out final.mp4
    python3 enhance_audio.py final_cut_voice_only.mp4 --music bed.mp3 --music-volume 0.22 --out final.mp4

Input should be the locked cut with dialogue only (no music yet). Enhancement
strips anything that isn't speech, so a baked-in music bed would be destroyed.
Pass the bed with --music and it's mixed back in after enhancement, ducked
under the voice.

Chain: extract 48k mono dialogue -> denoise (DeepFilterNet if installed, else
ffmpeg afftdn) -> voice polish (high-pass, presence EQ, gentle compression,
de-ess) -> two-pass loudnorm to -14 LUFS -> optional ducked music -> limiter
-> mux back onto the untouched video stream.

DeepFilterNet (free, local, no account): grab the `deep-filter` binary for your
OS from https://github.com/Rikorose/DeepFilterNet/releases, put it on PATH, or
pass --deep-filter /path/to/deep-filter. install-editing-style.sh does this.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TARGET_LUFS = -14.0
TRUE_PEAK = -1.0

# Voice polish after denoise: rumble cut, soft expander (pulls leftover noise down between
# words so the compressor can't lift it back up), body, presence, air, gentle comp, de-ess.
POLISH = ",".join([
    "highpass=f=80",
    "agate=threshold=0.02:ratio=1.6:range=0.3:attack=5:release=200",
    "equalizer=f=180:t=q:w=1:g=1.5",
    "equalizer=f=3200:t=q:w=1.2:g=2.5",
    "equalizer=f=9000:t=q:w=1:g=1.5",
    "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2",
    "deesser=i=0.4",
])

# Fallback denoise when DeepFilterNet isn't available: adaptive FFT denoise that tracks the noise floor.
FFMPEG_DENOISE = {
    "light": "afftdn=nr=14:nf=-40:tn=1",
    "medium": "afftdn=nr=18:nf=-35:tn=1,anlmdn=s=4",
    "strong": "afftdn=nr=28:nf=-30:tn=1,anlmdn=s=7,agate=threshold=0.015:ratio=2:attack=5:release=150",
}
# DeepFilterNet attenuation limit (dB) per strength; lower keeps more room tone, sounds more natural.
DF_ATTEN = {"light": 12, "medium": 24, "strong": 100}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def ffmpeg(*args):
    run(["ffmpeg", "-v", "error", "-y", *args])


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def has_video(path: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                          "stream=codec_type", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return "video" in out.stdout


def find_deep_filter(explicit: str | None) -> str | None:
    if explicit:
        return explicit if Path(explicit).exists() else None
    for name in ("deep-filter",):
        if shutil.which(name):
            return shutil.which(name)
    local = Path(__file__).resolve().parent.parent / "bin" / "deep-filter"
    return str(local) if local.exists() else None


def denoise(src: Path, dst: Path, engine: str, strength: str, df_bin: str | None, tmp: Path) -> str:
    if engine in ("auto", "deepfilter") and df_bin:
        outdir = tmp / "df"
        outdir.mkdir(exist_ok=True)
        # --compensate-delay keeps the cleaned voice sample-aligned with the picture (lip sync)
        cmd = [df_bin, "--compensate-delay", "--output-dir", str(outdir), str(src)]
        if strength != "strong":
            cmd[1:1] = ["--atten-lim-db", str(DF_ATTEN[strength])]
        try:
            run(cmd, capture_output=True)
            produced = next(outdir.glob("*.wav"))
            shutil.move(produced, dst)
            return f"DeepFilterNet ({df_bin})"
        except (subprocess.CalledProcessError, StopIteration) as e:
            if engine == "deepfilter":
                sys.exit(f"deep-filter failed: {e}")
            print("deep-filter failed, falling back to ffmpeg denoise", file=sys.stderr)
    elif engine == "deepfilter":
        sys.exit("deep-filter binary not found (see --help for where to get it)")
    ffmpeg("-i", str(src), "-af", FFMPEG_DENOISE[strength], str(dst))
    return f"ffmpeg afftdn ({strength})"


def loudnorm(src: Path, dst: Path, pre_filters: str) -> None:
    """Two-pass EBU R128 so the result lands on target instead of approximating it."""
    first = f"{pre_filters},loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11:print_format=json"
    res = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", first, "-f", "null", "-"],
                         capture_output=True, text=True, check=True)
    stats = json.loads(res.stderr[res.stderr.rindex("{"):res.stderr.rindex("}") + 1])
    second = (f"{pre_filters},loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11"
              f":measured_I={stats['input_i']}:measured_TP={stats['input_tp']}"
              f":measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}"
              f":offset={stats['target_offset']}:linear=true")
    ffmpeg("-i", str(src), "-af", second, "-ar", "48000", str(dst))


def mix_music(voice: Path, music: Path, volume: float, length: float, dst: Path) -> None:
    # Loop the bed to the cut length, duck it ~5 dB whenever the voice is present, then limit.
    graph = (f"[1:a]aloop=loop=-1:size=2147483647,atrim=0:{length:.3f},volume={volume},aresample=48000,"
             f"aformat=channel_layouts=stereo[bed];"
             f"[0:a]aformat=channel_layouts=stereo,asplit=2[vo][key];"
             f"[bed][key]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=300[ducked];"
             f"[vo][ducked]amix=inputs=2:normalize=0:duration=first,"
             f"alimiter=limit={10 ** (TRUE_PEAK / 20):.3f}[out]")
    ffmpeg("-i", str(voice), "-i", str(music), "-filter_complex", graph, "-map", "[out]", str(dst))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="finished cut (video or audio), dialogue only")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--music", type=Path, help="music bed to mix in after enhancement")
    ap.add_argument("--music-volume", type=float, default=0.22)
    ap.add_argument("--engine", choices=["auto", "deepfilter", "ffmpeg"], default="auto")
    ap.add_argument("--strength", choices=["light", "medium", "strong"], default="medium",
                    help="light: decent mic, slight hiss. medium: phone/camera mic. strong: loud room/street")
    ap.add_argument("--deep-filter", help="path to the deep-filter binary")
    ap.add_argument("--keep-stems", action="store_true", help="also write <out>.voice.wav (enhanced dialogue)")
    args = ap.parse_args()

    length = duration(args.input)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        raw, clean, voice = tmp / "raw.wav", tmp / "clean.wav", tmp / "voice.wav"
        ffmpeg("-i", str(args.input), "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(raw))
        used = denoise(raw, clean, args.engine, args.strength, find_deep_filter(args.deep_filter), tmp)
        loudnorm(clean, voice, POLISH)

        final_audio = voice
        if args.music:
            final_audio = tmp / "mix.wav"
            mix_music(voice, args.music, args.music_volume, length, final_audio)

        if args.keep_stems:
            shutil.copy(voice, args.out.with_suffix(".voice.wav"))

        if has_video(args.input):
            ffmpeg("-i", str(args.input), "-i", str(final_audio), "-map", "0:v:0", "-map", "1:a:0",
                   "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-t", f"{length:.3f}",
                   "-movflags", "+faststart", str(args.out))
        else:
            ffmpeg("-i", str(final_audio), "-t", f"{length:.3f}", str(args.out))

    print(f"{args.out}: {length:.1f}s enhanced with {used}, voice at {TARGET_LUFS:g} LUFS"
          + (f", music bed at {args.music_volume:g} ducked under voice" if args.music else ""))


if __name__ == "__main__":
    os.environ.setdefault("AV_LOG_FORCE_NOCOLOR", "1")
    main()
