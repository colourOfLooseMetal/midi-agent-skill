#!/usr/bin/env python3
"""
Analyze a Guitar Pro file (or a whole folder of them) and write reusable style cards.

    python analyze_song.py "path/to/song.gp4"          # parse -> analyze -> write card
    python analyze_song.py "path/to/song.gp4" --json   # also dump raw features as JSON
    python analyze_song.py "path/to/tabs_folder"        # analyze every supported file in the folder
    python analyze_song.py "path/to/tabs_folder" --json # same, plus a features JSON per file

This is the end-to-end driver for the analysis pipeline (parallel to compose_*.py
and render_wav.py): it does no analysis itself, it just wires parse_guitarpro ->
analyze -> style_card. The style card lands in resources/styles/<artist-title>.md,
where the composition step can read it like any other theory reference.

Supported: .gp3/.gp4/.gp5/.gtp (PyGuitarPro) and .gp (GP7/8, stdlib XML).
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from analysis.parse_guitarpro import load
from analysis.analyze import analyze
from analysis.style_card import write_card

SUPPORTED_EXTS = {".gp3", ".gp4", ".gp5", ".gtp", ".gp"}


def analyze_one(path, dump_json):
    song = load(path)
    features = analyze(song)

    key = features["harmony"].get("key_estimate") or {}
    t = features["tempo"]
    s = features["structure"]
    print(f"{features['artist'] or 'Unknown'} – {features['title']}  [{features['format']}]")
    print(f"  tempo: {t['initial_bpm']:.0f} BPM"
          + (" (half-time)" if t['half_time_feel'] else "")
          + f" | key: {key.get('tonic','?')} {key.get('scale','?')} ({key.get('confidence',0):.0%})")
    print(f"  meters: {', '.join(features['time_signatures']) or 'n/a'}"
          f" | density: {features['rhythm']['notes_per_bar']} notes/bar")
    print(f"  voicing: {features['harmony']['power_chords']} power chords / "
          f"{features['harmony']['triads']} triads")
    print(f"  structure: {s['bars']} bars, {s['unique_bars']} unique "
          f"({s['repetition_ratio']:.0%} repetition)")

    card = write_card(features)
    print(f"  style card -> {card.relative_to(REPO)}")

    if dump_json:
        out = REPO / "output" / (card.stem + ".features.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(features, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  features   -> {out.relative_to(REPO)}")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path = Path(argv[0])
    dump_json = "--json" in argv[1:]

    if path.is_dir():
        files = sorted(f for f in path.iterdir() if f.suffix.lower() in SUPPORTED_EXTS)
        if not files:
            print(f"No supported Guitar Pro files found in '{path}'.")
            return 1

        print(f"Found {len(files)} file(s) in '{path}'. Analyzing...\n")
        succeeded, failed = 0, 0
        for f in files:
            try:
                analyze_one(f, dump_json)
                succeeded += 1
            except Exception as exc:
                print(f"  FAILED: {f.name} -> {exc}")
                failed += 1
            print()

        print(f"Done: {succeeded} succeeded, {failed} failed.")
        return 1 if failed and not succeeded else 0

    if not path.exists():
        print(f"Error: '{path}' does not exist.")
        return 1

    analyze_one(path, dump_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
