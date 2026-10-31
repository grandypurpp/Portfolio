#!/usr/bin/env python3
"""Analyze a voiceover (and optional music bed) into a draft timeline for the
signature-edit-style Remotion template.

    pip install faster-whisper librosa
    python3 analyze.py voiceover.mp4 --music bed.mp3 --out timeline.json [--markers-csv beats.csv]

Outputs word timestamps, the beat grid, a suggested cut list labelled ON/OFF
beat, and draft "words" scenes (one per sentence, with "The first/second..."
lines turned into ordinal title cards).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FPS = 30
SNAP_FRAMES = 2  # snap a cut to the beat only if it is this close
LEAD_FRAMES = 2  # cuts lead the triggering word by this many frames
ORDINALS = {"first": "1st", "second": "2nd", "third": "3rd", "fourth": "4th",
            "fifth": "5th", "sixth": "6th", "seventh": "7th", "eighth": "8th",
            "ninth": "9th", "tenth": "10th"}
CONNECTORS = {"the", "a", "an", "of", "and", "but", "to", "in", "at", "on", "for",
              "your", "you", "is", "are", "it", "that", "with", "by", "these"}


def to_wav(src: Path, dst: Path) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1",
                    "-ar", "16000", str(dst)], check=True)


def transcribe(wav: Path, model_size: str):
    import librosa
    from faster_whisper import WhisperModel
    audio, _ = librosa.load(str(wav), sr=16000)
    model = WhisperModel(model_size, compute_type="int8")
    segments, _ = model.transcribe(audio, word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({"text": w.word.strip(), "start": round(w.start, 3),
                          "end": round(w.end, 3)})
    return words


def beat_grid(wav: Path):
    import librosa
    import numpy as np
    y, sr = librosa.load(str(wav), sr=22050)
    tempo, frames = librosa.beat.beat_track(y=y, sr=sr)
    beats = librosa.frames_to_time(frames, sr=sr)
    return round(float(np.atleast_1d(tempo)[0]), 2), [round(float(b), 3) for b in beats]


def clean(word: str) -> str:
    return re.sub(r"[^\w']", "", word).lower()


def sentences(words):
    cur = []
    for w in words:
        cur.append(w)
        if re.search(r"[.!?]$", w["text"]):
            yield cur
            cur = []
    if cur:
        yield cur


def suggest_cuts(words, beats):
    cuts = []
    for sent in sentences(words):
        t = max(0.0, sent[0]["start"] - LEAD_FRAMES / FPS)
        nearest = min(beats, key=lambda b: abs(b - t)) if beats else None
        delta = round((t - nearest) * FPS) if nearest is not None else None
        on = delta is not None and abs(delta) <= SNAP_FRAMES
        cuts.append({"time": round(nearest if on else t, 3),
                     "type": "ON" if on else "OFF",
                     "deltaFrames": delta,
                     "word": sent[0]["text"]})
    return cuts


def draft_scenes(words, cuts):
    scenes = []
    sents = list(sentences(words))
    for i, sent in enumerate(sents):
        start = cuts[i]["time"]
        end = cuts[i + 1]["time"] if i + 1 < len(cuts) else sent[-1]["end"] + 0.6
        tokens = [clean(w["text"]) for w in sent]
        if tokens and tokens[0] in {"and", "so", "now"}:  # "And the fifth" counts too
            sent, tokens = sent[1:], tokens[1:]
        if len(tokens) >= 2 and tokens[0] == "the" and tokens[1] in ORDINALS:
            # "The first one, ..." -> ordinal title card, rest of sentence follows as words
            lines = [[{"text": "The", "start": sent[0]["start"], "size": "md"}],
                     [{"text": ORDINALS[tokens[1]], "start": sent[1]["start"], "size": "xl"}]]
            rest = sent[2:]
            if rest and clean(rest[0]["text"]) == "one":
                lines.append([{"text": "one", "start": rest[0]["start"], "size": "md"}])
                rest = rest[1:]
            title_end = rest[0]["start"] - LEAD_FRAMES / FPS if rest else end
            scenes.append({"type": "words", "start": start, "end": round(title_end, 3), "lines": lines})
            if rest:
                scenes.append({"type": "screen", "start": round(title_end, 3), "end": end,
                               "src": "", "note": " ".join(w["text"] for w in rest)})
            continue
        line, lines = [], []
        for w in sent:
            size = "sm" if clean(w["text"]) in CONNECTORS else "md"
            line.append({"text": w["text"].strip(",."), "start": w["start"], "size": size})
            if len(line) == 4:
                lines.append(line)
                line = []
        if line:
            lines.append(line)
        scenes.append({"type": "words", "start": start, "end": end, "lines": lines})
    return scenes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("voice", type=Path, help="voiceover audio or video file")
    ap.add_argument("--music", type=Path, help="music bed (beat grid); defaults to the voice file's mix")
    ap.add_argument("--out", type=Path, default=Path("timeline.json"))
    ap.add_argument("--markers-csv", type=Path, help="also write beat + cut markers for NLE import")
    ap.add_argument("--model", default="small", help="whisper model size (tiny/base/small/medium)")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        vwav = Path(tmp) / "voice.wav"
        to_wav(args.voice, vwav)
        mwav = vwav
        if args.music:
            mwav = Path(tmp) / "music.wav"
            to_wav(args.music, mwav)
        print("transcribing…", file=sys.stderr)
        words = transcribe(vwav, args.model)
        print("tracking beats…", file=sys.stderr)
        bpm, beats = beat_grid(mwav)

    cuts = suggest_cuts(words, beats)
    duration = round(max(w["end"] for w in words) + 0.8, 3) if words else 5.0
    timeline = {
        "fps": FPS, "width": 1920, "height": 1080, "durationSec": duration,
        "bpm": bpm, "beats": beats, "words": words, "cuts": cuts,
        "audio": {"voice": args.voice.name, "music": args.music.name if args.music else None,
                  "musicVolume": 0.22},
        "scenes": draft_scenes(words, cuts),
    }
    args.out.write_text(json.dumps(timeline, indent=2))
    on = sum(c["type"] == "ON" for c in cuts)
    print(f"{args.out}: {len(words)} words, {bpm} BPM, {len(cuts)} cuts ({on} on-beat, {len(cuts) - on} off-beat)")

    if args.markers_csv:
        rows = ["time,type,label"] + [f"{b},beat," for b in beats] + \
               [f"{c['time']},cut-{c['type']},{c['word']}" for c in cuts]
        args.markers_csv.write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
