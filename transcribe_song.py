#!/usr/bin/env python3
"""
Transcribe a real Guitar Pro song into a compact, faithful `compose_*.py` driver.

    python transcribe_song.py "path/to/song.gp"                       # print breakdown
    python transcribe_song.py "path/to/song.gp" --emit out.py          # write the driver
    python transcribe_song.py "path/to/song.gp" --emit compose_x.py    # (any output name)

This is the end-to-end driver for the transcription/block-compression tool (parallel to
analyze_song.py, which writes statistical style cards). It does no work itself -- it
wires analysis.extract_blocks: parse -> transcribe every bar -> detect repeated multi-bar
blocks -> lay out a section timeline -> optionally emit a self-contained driver in the
compose_doom_*.py idiom (named reusable blocks + an add()-style section timeline + a
tempo plan), holding the REAL song so it can be iterated like the other drivers.

Supported inputs: .gp/.gp3/.gp4/.gp5/.gtp (same as analyze_song.py). The recreation is
exact on pitch, voicing, rhythm, drum hits, tempo and arrangement; it does not carry
per-note velocity (absent from the IR) or notated meter changes (audio is unaffected).
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from analysis.extract_blocks import build_song, print_breakdown, emit_driver


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    path = Path(argv[0])
    if not path.exists():
        print(f"Error: '{path}' does not exist.")
        return 1

    out = None
    if "--emit" in argv:
        i = argv.index("--emit")
        if i + 1 < len(argv):
            out = argv[i + 1]
        else:
            print("Error: --emit needs an output path.")
            return 1

    data = build_song(str(path))
    print_breakdown(data)

    if out:
        emit_driver(data, out)
        print(f"\nDriver written: {out}")
        print(f"  Run it:    python {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
