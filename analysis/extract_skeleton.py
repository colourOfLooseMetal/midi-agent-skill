#!/usr/bin/env python3
"""
Turn a real Guitar Pro song into a COMPACT, ITERABLE skeleton -- the "product B" to
extract_blocks.py's faithful "product A".

Where extract_blocks transcribes every bar verbatim and only dedups *perfect* repeats
(so a verse played 8 times with tiny per-take variation explodes into ~70 one-shot
blocks), this module trades exactness for a chart a musician could actually iterate:

  1. FUZZY bar clustering -- bars within `tol` note-differences collapse into one block
     family whose canonical form is the most common member. This is what merges the
     "differs by exactly one note" near-duplicates extract_blocks is forced to keep.
  2. SECTION detection -- the existing tile()/segment_score() block detector is run on
     the *combined cross-lane cluster stream*, recovering INTRO/VERSE/CHORUS-style
     sections that recur (SECTIONS = [("A", 4), ("B", 2), ...]) with shared names.
  3. Compact emit -- ln() note strings + a section expander, in the compose_*.py idiom.

The result is intentionally LOSSY: each clustered bar is snapped to its family's
canonical bar, so the recreation is approximate, not note-exact. The emitted driver
prints a fidelity report (% of bars left unchanged) so you can see -- and, via `tol`,
tune -- how far it drifts from the record. Use product A when you want the archive;
use this when you want a small structure to spin originals off.

CLI: transcribe_skeleton.py at the repo root (parallel to transcribe_song.py).
"""

from __future__ import annotations

import collections
from pathlib import Path
from typing import Dict, List, Tuple

from analysis.extract_blocks import (
    build_song, _clean_meta, _compact_body, _col_name, segment_score, _rle,
    ROLE_PREFIX,
)
from skills.generate_midi import parse_pitch, parse_duration


# --------------------------------------------------------------------------- #
# Fuzzy clustering of one lane's bars into block families.
# --------------------------------------------------------------------------- #
def _sig_beats(sig: Tuple) -> float:
    return sum(parse_duration(d) for _, d in sig)


def _can_merge(rep: Tuple, sig: Tuple, tol: int) -> bool:
    """True if `sig` may collapse into `rep`'s family.

    Requires the same number of events AND the same total bar length (so snapping a bar
    to its canonical never changes the bar's duration -- otherwise the lanes desync and
    the whole-song length drifts), with at most `tol` differing (pitch,duration) slots.
    """
    if len(rep) != len(sig):
        return False
    if abs(_sig_beats(rep) - _sig_beats(sig)) > 1e-6:
        return False
    return sum(1 for x, y in zip(rep, sig) if x != y) <= tol


class SkeletonLane:
    """A lane's bars clustered into canonical block families + a per-bar name stream."""

    def __init__(self, name: str, lane, tol: int):
        self.name = name
        self.instrument = lane.instrument
        self.perc = lane.perc
        self.sigs: List[Tuple] = list(lane.sigs)
        self.sig_notes = lane.sig_notes
        self.tol = tol

        # Seed clusters from the most frequent bars first, so the canonical rep of every
        # family is its most common member and rarer near-dups attach to it.
        counts = collections.Counter(self.sigs)
        reps: List[Tuple] = []                       # cluster index -> canonical sig
        self.cluster_of: Dict[Tuple, int] = {}       # any sig -> cluster index
        for sig, _ in counts.most_common():
            placed = False
            for ci, rsig in enumerate(reps):
                if _can_merge(rsig, sig, tol):
                    self.cluster_of[sig] = ci
                    placed = True
                    break
            if not placed:
                self.cluster_of[sig] = len(reps)
                reps.append(sig)
        self.reps = reps

        # Name each cluster (REST / PEDAL / RIFF|GROOVE|PHRASE_x), in first-appearance order.
        self.block_name: Dict[int, str] = {}
        self.blocks: "collections.OrderedDict[str, List[Dict[str, str]]]" = collections.OrderedDict()
        counters: Dict[str, int] = collections.defaultdict(int)
        for sig in self.sigs:                        # first-appearance order across the song
            ci = self.cluster_of[sig]
            if ci in self.block_name:
                continue
            rep = reps[ci]
            notes = self.sig_notes[rep]
            base = self._classify(notes)
            if base in ("REST", "PEDAL"):
                nm = base if counters[base] == 0 else f"{base}{counters[base] + 1}"
            else:
                nm = f"{base}_{_col_name(counters[base])}"
            counters[base] += 1
            self.block_name[ci] = nm
            self.blocks[nm] = notes

        # Per-bar block-name stream + how many bars were snapped to a different canonical.
        self.bar_names: List[str] = [self.block_name[self.cluster_of[s]] for s in self.sigs]
        self.snapped = sum(1 for s in self.sigs if s != reps[self.cluster_of[s]])

    def _classify(self, notes: List[Dict[str, str]]) -> str:
        if all(n["pitch"] == "R" for n in notes):
            return "REST"
        if not self.perc and len(notes) and len({
            parse_pitch(tok) % 12
            for n in notes if n["pitch"] != "R" for tok in n["pitch"].split("+")
        }) <= 1:
            return "PEDAL"
        return ROLE_PREFIX[self.name]


# --------------------------------------------------------------------------- #
# Cross-lane section detection.
# --------------------------------------------------------------------------- #
def build_skeleton(path: str, tol: int = 1) -> Dict:
    """Parse + transcribe + fuzzy-cluster + section-segment a GP file."""
    data = build_song(path)                          # reuse product-A parse/transcribe
    lanes = collections.OrderedDict(
        (n, SkeletonLane(n, l, tol)) for n, l in data["lanes"].items())
    nbars = max(len(l.bar_names) for l in lanes.values())

    # Pad any short lane with a one-bar rest so all lanes share a bar grid for sectioning.
    REST_BAR = "_PAD_REST"
    for l in lanes.values():
        if len(l.bar_names) < nbars:
            if REST_BAR not in l.blocks:
                l.blocks[REST_BAR] = [{"pitch": "R", "duration": "1"}]
            l.bar_names += [REST_BAR] * (nbars - len(l.bar_names))

    # Sections follow the HARMONIC BACKBONE (rhythm guitar, else the first lane): recurring
    # multi-bar phrases of its fuzzy block stream become named, reusable sections. Driving
    # off one lane -- not all of them -- keeps drum/vocal variation from fragmenting the
    # form (requiring all 5 lanes to match made nearly every bar its own "section").
    driver = "rhythm" if "rhythm" in lanes else next(iter(lanes))
    sec_score = segment_score(lanes[driver].bar_names)   # [(tuple_of_driver_block_names, count)]

    section_name: Dict[Tuple, str] = {}
    section_defs: "collections.OrderedDict[str, Dict[str, List[Tuple[str, int]]]]" = collections.OrderedDict()
    sections: List[Tuple[str, int]] = []
    # Track, for the non-driver lanes, how much a repeated section's bars differ from the
    # first occurrence we froze as canonical (the extra loss the section layer introduces).
    section_drift = 0
    cursor = 0
    for block, count in sec_score:
        width = len(block)
        if block not in section_name:                    # first time: freeze canonical defs
            nm = _col_name(len(section_name))            # A, B, C, ...
            section_name[block] = nm
            section_defs[nm] = {
                n: _rle(lanes[n].bar_names[cursor:cursor + width]) for n in lanes}
        else:                                            # repeat: measure non-driver drift
            canon = section_defs[section_name[block]]
            for n in lanes:
                if n == driver:
                    continue
                here = _rle(lanes[n].bar_names[cursor:cursor + width])
                if here != canon[n]:
                    section_drift += width
        sections.append((section_name[block], count))
        cursor += width * count

    data.update(
        skeleton_lanes=lanes, n_bars=nbars, sections=sections,
        section_defs=section_defs, tol=tol, section_driver=driver,
        section_drift=section_drift,
    )
    return data


# --------------------------------------------------------------------------- #
# Codegen.
# --------------------------------------------------------------------------- #
def _slug(data: Dict) -> str:
    import re
    raw = f"{data['artist']}-{data['title']}" if data["artist"] else data["title"]
    return re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_") or "song"


def _py_blocks(varname: str, lane: SkeletonLane) -> str:
    parts = [f"{varname} = {{"]
    for nm, notes in lane.blocks.items():
        parts.append(f'    "{nm}": {_compact_body(notes)},   # {len(notes)} events')
    parts.append("}")
    return "\n".join(parts)


def _py_score(name: str, score: List[Tuple[str, int]]) -> str:
    items = ", ".join(f'("{nm}", {c})' for nm, c in score)
    return f"{name} = [{items}]"


def emit_skeleton(data: Dict, out_path: str) -> str:
    lanes: "collections.OrderedDict[str, SkeletonLane]" = data["skeleton_lanes"]
    artist, song_title = _clean_meta(data["artist"], data["title"])
    title = f"{artist} - {song_title} (Skeleton)".strip(" -")
    key = data.get("key") or {}
    lane_names = list(lanes.keys())

    total_bars = data["n_bars"]
    snapped = sum(l.snapped for l in lanes.values())
    drift = data.get("section_drift", 0)
    lane_bars = sum(len(l.bar_names) for l in lanes.values())
    exact_pct = 100.0 * (lane_bars - snapped - drift) / lane_bars if lane_bars else 100.0
    block_counts = ", ".join(f"{n}={len(l.blocks)}" for n, l in lanes.items())

    header = f'''#!/usr/bin/env python3
"""
{title}
=== an ITERABLE skeleton of a real doom song (lossy), in the compose_doom_*.py idiom ===

Auto-generated by transcribe_skeleton.py / analysis.extract_skeleton (fuzzy tol={data["tol"]}).
Unlike the faithful (Recreation) driver, near-identical bars are merged into one
canonical block, so this is APPROXIMATE -- but small enough to actually rework. Each
lane is a handful of named BLOCKS; the song is a SECTION map -- SECTIONS lists sections
in order (with repeat counts), and SECTION_DEFS gives each section's per-lane block
sequence. Re-order SECTIONS, re-count a repeat, or tweak a block to spin off an original.

  Key/feel : {key.get("tonic", "?")} {key.get("scale", "?")}, {data["bpm"]} BPM, {total_bars} bars
  Sections : driven by '{data["section_driver"]}' -- {len(data["sections"])} in order, {len(data["section_defs"])} unique
  Blocks   : {block_counts}
  Fidelity : {exact_pct:.0f}% of bars exact ({snapped} fuzzy-snapped + {drift} section-drift of {lane_bars} bars, tol={data["tol"]})
"""

import sys
from pathlib import Path

REPO = Path(__file__).parent
sys.path.insert(0, str(REPO))

from skills.generate_midi import generate_midi_from_dict, parse_duration


def ln(s):
    """Compact "P:dur P:dur ..." note string -> [{{"pitch","duration"}}, ...]."""
    return [dict(zip(("pitch", "duration"), t.rsplit(":", 1))) for t in s.split()]


def beats(notes):
    return sum(parse_duration(n["duration"]) for n in notes)
'''

    var_for = {n: n.upper() for n in lane_names}
    block_sections = [
        f"# ===================== {n.upper()} blocks ({lanes[n].instrument}) "
        f"=====================\n" + _py_blocks(var_for[n], lanes[n])
        for n in lane_names]

    # SECTION_DEFS: nested dict literal, readable per section.
    def_lines = ["SECTION_DEFS = {"]
    for sec, defs in data["section_defs"].items():
        def_lines.append(f'    "{sec}": {{')
        for n in lane_names:
            items = ", ".join(f'("{nm}", {c})' for nm, c in defs[n])
            def_lines.append(f'        "{n}": [{items}],')
        def_lines.append("    },")
    def_lines.append("}")
    section_defs_block = "\n".join(def_lines)

    instr_map = "{\n" + "".join(
        f'    "{n}": "{lanes[n].instrument}",\n' for n in lane_names) + "}"
    blocks_map = "{\n" + "".join(f'    "{n}": {var_for[n]},\n' for n in lane_names) + "}"
    sections_block = _py_score("SECTIONS", data["sections"])

    tempo_block = "TEMPO_MAP = [\n" + "".join(
        f'    {{"beat": {c["beat"]:.0f}, "bpm": {c["bpm"]:.0f}}},\n'
        for c in data["tempo_map"]) + "]"

    builder = f'''
# =========================== arrangement / plumbing ===========================
LANES = {tuple(lane_names)!r}
INSTRUMENTS = {instr_map}
BLOCKS = {blocks_map}

{sections_block}

{section_defs_block}

{tempo_block}


def build_lane(lane):
    """Expand SECTIONS + SECTION_DEFS into one lane's flat note list."""
    out = []
    for sec, count in SECTIONS:
        for _ in range(count):
            for blk, c in SECTION_DEFS[sec][lane]:
                out += BLOCKS[lane][blk] * c
    return out


timeline = {{lane: build_lane(lane) for lane in LANES}}

composition = {{
    "title": "{title}",
    "bpm": {data["bpm"]},
    "time_signature": "{data["time_signature"]}",
    "tempo_map": TEMPO_MAP,
    "tracks": [
        {{"instrument": INSTRUMENTS[lane], "notes": timeline[lane]}} for lane in LANES
    ],
}}


if __name__ == "__main__":
    total = beats(timeline[LANES[0]])
    for lane in LANES:
        assert abs(beats(timeline[lane]) - total) < 1e-6, \\
            f"{{lane}} misaligned ({{beats(timeline[lane])}} vs {{total}})"
    print(f"Title   : {title}")
    print(f"Sections: {{len(SECTIONS)}} in order, {{len(SECTION_DEFS)}} unique")
    print(f"Length  : {{total:.0f}} beats")
    print("Blocks  : " + ", ".join(f"{{l}}={{len(BLOCKS[l])}}" for l in LANES))
    path = generate_midi_from_dict(composition)
    print(f"MIDI written: {{path}}")
    stem = Path(path).stem
    print(f'Render to WAV:  python render_wav.py 0.7 "{{stem}}"')
'''

    src = header + "\n\n" + "\n\n".join(block_sections) + "\n\n" + builder
    Path(out_path).write_text(src, encoding="utf-8")
    return out_path


def print_breakdown(data: Dict) -> None:
    lanes = data["skeleton_lanes"]
    key = data.get("key") or {}
    print(f"{data['artist'] or 'Unknown'} - {data['title']}  (skeleton, tol={data['tol']})")
    print(f"  {data['bpm']} BPM | key {key.get('tonic','?')} {key.get('scale','?')} | {data['n_bars']} bars")
    print("\n  Blocks per lane (fuzzy-merged) + bars snapped to canonical:")
    for n, l in lanes.items():
        print(f"    {n:7} ({l.instrument:18}): {len(l.blocks):3} blocks, "
              f"{l.snapped:3}/{len(l.bar_names)} bars snapped")
    secs = " ".join(f"{nm}x{c}" if c > 1 else nm for nm, c in data["sections"])
    print(f"\n  Sections driven by '{data['section_driver']}': "
          f"{len(data['sections'])} in order, {len(data['section_defs'])} unique")
    print(f"  Section drift: {data['section_drift']} non-driver bars differ from their "
          f"section's frozen canonical")
    print(f"\n  {secs}")
