#!/usr/bin/env python3
"""
Analyze a Guitar Pro file (or a whole folder of them) and write reusable style cards.

    python analyze_song.py "path/to/song.gp4"          # parse -> analyze -> write card
    python analyze_song.py "path/to/song.gp4" --json   # also dump raw features as JSON
    python analyze_song.py "path/to/tabs_folder"        # analyze every supported file in the folder
    python analyze_song.py "path/to/tabs_folder" --json # same, plus a features JSON per file
    python analyze_song.py "song.gp" --out resources/styles/doom   # write the card into a subfolder

This is the end-to-end driver for the analysis pipeline (parallel to compose_*.py
and render_wav.py): it does no analysis itself, it just wires parse_guitarpro ->
analyze -> style_card. The style card lands in resources/styles/<artist-title>.md by
default (override the directory with --out, e.g. to keep a genre's cards together),
where the composition step can read it like any other theory reference. Each run also
(re)writes a single CLAUDE.md in that output directory explaining what the cards'
headings mean and how to apply them — kept out of the per-song cards so that text
isn't repeated in every file.

Supported: .gp3/.gp4/.gp5/.gtp (PyGuitarPro) and .gp (GP7/8, stdlib XML).
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from analysis.parse_guitarpro import load
from analysis.analyze import analyze
from analysis.style_card import write_card, write_guide, STYLES_DIR

SUPPORTED_EXTS = {".gp3", ".gp4", ".gp5", ".gtp", ".gp"}


def analyze_one(path, dump_json, out_dir=None):
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

    perc = features.get("percussion")
    if perc:
        voices = ", ".join(f"{cat} {pct}%" for cat, pct in
                            list(perc["voice_percentages"].items())[:4])
        print(f"  drums: {perc['hits_per_bar']} hits/bar | {voices} | "
              f"pattern repeats {perc['pattern_top_repeats']}x "
              f"({perc['pattern_repetition_ratio']:.0%})")

    riffs = features.get("riffs") or []
    pedal = features.get("pedal")
    if riffs or pedal:
        widths = ", ".join(f"{r['bars']}-bar x{r['repeats']}" for r in riffs[:3]) or "none"
        ped = (f" | pedal x{pedal['repeats']} ({features.get('pedal_ratio', 0):.0%} of bars)"
               if pedal else "")
        print(f"  riffs: {widths}{ped}")

    voc = features.get("vocals")
    if voc:
        print(f"  vocals: {voc['track_name'][:28]} | range {voc['range_low']}–{voc['range_high']} | "
              f"{voc['phrase_count']} phrases (avg {voc['avg_notes_per_phrase']} notes)")

    arr = features.get("arrangement") or []
    if arr:
        print(f"  arrangement: {len(arr)} sections | "
              + " → ".join(s["label"] for s in arr[:6]) + (" …" if len(arr) > 6 else ""))

    card = write_card(features, out_dir=out_dir) if out_dir else write_card(features)
    try:
        shown = card.resolve().relative_to(REPO)
    except ValueError:
        shown = card
    print(f"  style card -> {shown}")

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
    rest = argv[1:]
    dump_json = "--json" in rest
    out_dir = None
    if "--out" in rest:
        i = rest.index("--out")
        if i + 1 < len(rest):
            out_dir = Path(rest[i + 1]).resolve()
    for a in rest:
        if a.startswith("--out="):
            out_dir = Path(a.split("=", 1)[1]).resolve()

    if path.is_dir():
        files = sorted(f for f in path.iterdir() if f.suffix.lower() in SUPPORTED_EXTS)
        if not files:
            print(f"No supported Guitar Pro files found in '{path}'.")
            return 1

        print(f"Found {len(files)} file(s) in '{path}'. Analyzing...\n")
        succeeded, failed = 0, 0
        for f in files:
            try:
                analyze_one(f, dump_json, out_dir)
                succeeded += 1
            except Exception as exc:
                print(f"  FAILED: {f.name} -> {exc}")
                failed += 1
            print()

        print(f"Done: {succeeded} succeeded, {failed} failed.")
        if succeeded:
            write_guide(out_dir or STYLES_DIR)
        return 1 if failed and not succeeded else 0

    if not path.exists():
        print(f"Error: '{path}' does not exist.")
        return 1

    analyze_one(path, dump_json, out_dir)
    write_guide(out_dir or STYLES_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
