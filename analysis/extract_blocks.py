#!/usr/bin/env python3
"""
Turn a real Guitar Pro song into a COMPACT, faithful set of reusable blocks plus a
section timeline -- the raw material for a `compose_*.py` driver in this repo's idiom.

Where analyze.py measures a song into a *statistical* style card, this module does the
other half: it transcribes the song **verbatim** and compresses it. For every track it

  1. normalizes each bar to skill note-dicts (empty bars -> a full-bar rest so the
     lanes stay sample-aligned -- see CLAUDE.md's rest rule),
  2. detects repeated multi-bar blocks (a 4-bar riff cycled 16x becomes one named
     block + a repeat count -- the "guitar repeats every bar for n bars / drums repeat
     over multiple bars" the user described), and
  3. lays the song out as an ordered SECTION timeline (driven by the rhythm guitar's
     riff changes) where each lane is a short `[(block, count), ...]` score.

`emit_driver()` then writes a self-contained, readable `compose_<slug>.py` in the same
shape as compose_doom_drowned_cathedral.py -- named block dicts, an `add()` section
timeline, a tempo plan -- but holding the REAL transcribed song instead of card-
synthesized content, so it can be opened and iterated the same way.

It is song-agnostic: point it at any supported Guitar Pro file (the analysis pipeline's
`.gp/.gp3/.gp4/.gp5/.gtp`). The recreation is exact on pitch, voicing, rhythm, drum
hits, tempo and arrangement; it does NOT carry per-note velocity (absent from the IR)
or notated meter changes (audio is unaffected -- durations are absolute beats).

CLI lives in transcribe_song.py at the repo root (parallel to analyze_song.py).
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from analysis.parse_guitarpro import load, GPSong, GPTrack, GPMeasure
from analysis.analyze import _midi_name, estimate_key, _pitch_class_weights
from midi_types.gm_percussion import DRUM_NOTES
from skills.generate_midi import parse_pitch, parse_duration

# --------------------------------------------------------------------------- #
# Duration tokens -- aligned to the CONSUMER (skills.generate_midi.parse_duration),
# NOT analyze._skill_duration. The two disagree on triplets: analyze emits "T16" for
# a 1/6-beat note, but parse_duration only knows "T8"(=1/6) and "T4"(=1/3) and would
# silently default an unknown token to a quarter note. So we pick from exactly what
# parse_duration accepts and assert the round-trip below.
# --------------------------------------------------------------------------- #
# Exact single-token values parse_duration accepts (incl. dotted + the two triplets).
_GEN_TOKENS: List[Tuple[float, str]] = [
    (4.0, "1"), (3.0, "d2"), (2.0, "2"), (1.5, "d4"), (1.0, "4"),
    (0.75, "d8"), (0.5, "8"), (1 / 3, "T4"), (0.25, "16"), (1 / 6, "T8"), (0.125, "32"),
]
# Pure-binary units (longest first) for decomposing a duration that ISN'T a single
# token -- e.g. a tie-folded 2.5/5.0/6.0-beat note (GPIF folds a tied note into the
# one it sustains, see parse_guitarpro._from_gpif) or a full odd-meter bar of rest.
_BIN_UNITS: List[Tuple[float, str]] = [
    (4.0, "1"), (2.0, "2"), (1.0, "4"), (0.5, "8"), (0.25, "16"), (0.125, "32"),
]
_EPS = 1e-6


def gen_dur(beats: float) -> str:
    """Nearest single token (last-resort only -- prefer dur_tokens, which is exact)."""
    return min(_GEN_TOKENS, key=lambda vt: abs(vt[0] - beats))[1]


def dur_tokens(beats: float) -> List[str]:
    """A beat value -> a list of tokens that sum EXACTLY to it (usually length 1).

    A single standard/dotted/triplet note returns one token; a tie-folded long note or
    an odd-meter full-bar rest decomposes into a binary chain (e.g. 2.5 -> ["2","8"]),
    so a note/rest is never silently mis-rounded and the bar always keeps its length.
    """
    for val, tok in _GEN_TOKENS:                 # exact single-token match first
        if abs(val - beats) < 1e-4:
            return [tok]
    out: List[str] = []
    rem = round(beats, 6)
    for val, tok in _BIN_UNITS:                  # binary decomposition (exact to 1/32)
        while rem >= val - _EPS:
            out.append(tok)
            rem = round(rem - val, 6)
    if rem > 1e-4 or not out:                    # residue (e.g. odd triplet fold): approx
        out.append(gen_dur(beats if not out else rem))
    return out


def rest_tokens(total_beats: float) -> List[str]:
    """Decompose `total_beats` of silence into valid rest tokens (uses dur_tokens)."""
    return dur_tokens(total_beats)


# --------------------------------------------------------------------------- #
# Percussion: MIDI note -> drum NAME (the reverse of gm_percussion.DRUM_NOTES, which
# is name->note and has several aliases per note). We pick one canonical readable name
# per note via this preference order; unknown notes fall back to the raw number string,
# which resolve_drum() accepts on the way back.
# --------------------------------------------------------------------------- #
_DRUM_PREFERRED = [
    "kick", "snare", "side-stick", "clap", "hihat-closed", "hihat-pedal", "hihat-open",
    "crash", "crash2", "splash", "china", "ride", "ride2", "ride-bell",
    "tom-floor-low", "tom-floor", "tom-low", "tom-mid", "tom-hi-mid", "tom-high",
    "tambourine", "cowbell", "vibraslap",
]
_NOTE_TO_DRUM: Dict[int, str] = {}
for _nm in _DRUM_PREFERRED:
    _note = DRUM_NOTES.get(_nm)
    if _note is not None and _note not in _NOTE_TO_DRUM:
        _NOTE_TO_DRUM[_note] = _nm


def drum_name(note: int) -> str:
    return _NOTE_TO_DRUM.get(note, str(note))


# --------------------------------------------------------------------------- #
# Per-bar transcription -> skill note dicts.
# --------------------------------------------------------------------------- #
def _beat_pitch(b, perc: bool) -> str:
    if b.is_rest or not b.pitches:
        return "R"
    if perc:
        return "+".join(drum_name(p) for p in sorted(set(b.pitches)))
    return "+".join(_midi_name(p) for p in sorted(set(b.pitches)))


def _snap_bar(measure: GPMeasure, bar_len: float, perc: bool) -> List[Dict[str, str]]:
    """Repair a bar whose beats don't sum to bar_len by snapping note ONSETS to the grid.

    The faithful path keeps every note's written duration. But some tabs carry sub-grid
    detail the skill can't hold -- a 64th-note flourish, tie-fold overshoot -- so a bar
    sums to a hair over/under nominal. Rounding a single note's *duration* up to the 32nd
    floor would shove every later note in the bar late and corrupt the groove. Instead we
    snap each note's *start* to the nearest 1/32, derive each duration from the gap to the
    next snapped onset (the last note runs to the barline), and drop any note whose onset
    collapses onto its neighbour (a true ornament). Onsets stay put, the bar lands exactly
    on bar_len, and the lanes stay locked.
    """
    GRID = 0.125
    onsets: List[float] = []
    t = 0.0
    for b in measure.beats:
        onsets.append(t)
        t += b.duration_beats
    snapped = [min(bar_len, round(o / GRID) * GRID) for o in onsets]
    out: List[Dict[str, str]] = []
    for i, b in enumerate(measure.beats):
        start = snapped[i]
        end = snapped[i + 1] if i + 1 < len(snapped) else bar_len
        dur = round(end - start, 6)
        if dur <= _EPS:
            continue                             # ornament collapsed onto the next onset
        pitch = _beat_pitch(b, perc)
        for tok in dur_tokens(dur):
            out.append({"pitch": pitch, "duration": tok})
    return out


def bar_to_notes(measure: GPMeasure, perc: bool) -> List[Dict[str, str]]:
    """One bar -> list of {"pitch","duration"} dicts; empty bar -> a full-bar rest.

    Faithful by default: each beat keeps its written duration (so ties/dots/triplets and
    clean bars round-trip exactly). Only when a bar's beats don't sum to its nominal
    length -- sub-grid ornaments or tie-fold overshoot the skill's 1/32 grid can't hold --
    do we repair it via onset-snapping (`_snap_bar`), which preserves where notes land
    while forcing the bar to bar_len so the lanes stay aligned over the whole song.
    """
    num, den = measure.time_sig
    bar_len = num * 4.0 / den
    if not measure.beats:
        return [{"pitch": "R", "duration": t} for t in rest_tokens(bar_len)]
    out: List[Dict[str, str]] = []
    for b in measure.beats:
        pitch = _beat_pitch(b, perc)
        for tok in dur_tokens(b.duration_beats):
            out.append({"pitch": pitch, "duration": tok})
    if abs(notes_beats(out) - bar_len) > 1e-4:    # off-length -> snap onsets to repair
        return _snap_bar(measure, bar_len, perc)
    return out


def bar_sig(notes: List[Dict[str, str]]) -> Tuple:
    """Hashable equality key for "is this the same bar" over transcribed notes."""
    return tuple((n["pitch"], n["duration"]) for n in notes)


def notes_beats(notes: List[Dict[str, str]]) -> float:
    return sum(parse_duration(n["duration"]) for n in notes)


# --------------------------------------------------------------------------- #
# Block detection: tile a bar-signature stream into repeated multi-bar windows.
# --------------------------------------------------------------------------- #
_WIDTHS = (16, 8, 4, 2)


def _occurrences(stream: List[Tuple], win: Tuple[Tuple, ...]) -> int:
    """Non-overlapping occurrences of `win` in `stream`."""
    w = len(win)
    i = c = 0
    while i + w <= len(stream):
        if tuple(stream[i:i + w]) == win:
            c += 1
            i += w
        else:
            i += 1
    return c


def tile(stream: List[Tuple], widths=_WIDTHS) -> List[Tuple[Tuple, ...]]:
    """Greedy widest-first tiling into block tuples; any block recurs (>=2x) or is 1 bar.

    Correctness does not depend on the heuristic: width-1 always matches, so every
    stream tiles, and segment_score() asserts the tiling reconstructs the input.
    """
    out: List[Tuple[Tuple, ...]] = []
    i, n = 0, len(stream)
    while i < n:
        chosen: Optional[Tuple[Tuple, ...]] = None
        for w in widths:
            if w <= 1 or i + w > n:
                continue
            win = tuple(stream[i:i + w])
            if _occurrences(stream, win) >= 2:
                chosen = win
                break
        if chosen is None:
            chosen = (stream[i],)
        out.append(chosen)
        i += len(chosen)
    return out


def _rle(blocks: List[Tuple[Tuple, ...]]) -> List[Tuple[Tuple[Tuple, ...], int]]:
    """Collapse consecutive identical block tuples -> [(block, count), ...]."""
    out: List[Tuple[Tuple[Tuple, ...], int]] = []
    for b in blocks:
        if out and out[-1][0] == b:
            out[-1] = (b, out[-1][1] + 1)
        else:
            out.append((b, 1))
    return out


def segment_score(sigs: List[Tuple], widths=_WIDTHS) -> List[Tuple[Tuple[Tuple, ...], int]]:
    """sig stream -> [(block, count)] (block = tuple of bar-sigs), verified exact."""
    score = _rle(tile(sigs, widths))
    rebuilt: List[Tuple] = []
    for block, count in score:
        rebuilt.extend(list(block) * count)
    assert rebuilt == sigs, "block segmentation failed to reconstruct the bar stream"
    return score


# --------------------------------------------------------------------------- #
# A parsed, normalized lane: per-bar notes + signatures + a name registry so the same
# musical block gets the same readable name everywhere it appears.
# --------------------------------------------------------------------------- #
ROLE_PREFIX = {"lead": "RIFF", "rhythm": "RIFF", "bass": "RIFF",
               "drums": "GROOVE", "vox": "PHRASE"}


def _col_name(i: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA, ... (spreadsheet-column letters; never punctuation)."""
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(ord("A") + r) + s
    return s


class Lane:
    def __init__(self, name: str, track: GPTrack, instrument: str):
        self.name = name
        self.instrument = instrument
        self.perc = track.is_percussion
        self.bars: List[List[Dict[str, str]]] = [bar_to_notes(m, self.perc) for m in track.measures]
        self.sigs: List[Tuple] = [bar_sig(b) for b in self.bars]
        self.sig_notes: Dict[Tuple, List[Dict[str, str]]] = {}
        for sig, notes in zip(self.sigs, self.bars):
            self.sig_notes.setdefault(sig, notes)
        # name registry: block (tuple of sigs) -> block name; block name -> notes
        self._by_block: Dict[Tuple[Tuple, ...], str] = {}
        self.blocks: "collections.OrderedDict[str, List[Dict[str, str]]]" = collections.OrderedDict()
        self._counters: Dict[str, int] = collections.defaultdict(int)

    def _classify(self, block: Tuple[Tuple, ...]) -> str:
        notes = [n for sig in block for n in self.sig_notes[sig]]
        if all(n["pitch"] == "R" for n in notes):
            return "REST"
        if self.perc:
            return "MOVE"
        if len(block) == 1:
            pcs = {parse_pitch(tok) % 12
                   for n in notes if n["pitch"] != "R" for tok in n["pitch"].split("+")}
            if len(pcs) <= 1:
                return "PEDAL"
        return "MOVE"

    def name_block(self, block: Tuple[Tuple, ...]) -> str:
        """Stable readable name for a block; registers its notes in self.blocks."""
        if block in self._by_block:
            return self._by_block[block]
        kind = self._classify(block)
        if kind == "REST":
            base = "REST"
            nm = base if self._counters[base] == 0 else f"{base}{self._counters[base] + 1}"
        elif kind == "PEDAL":
            base = "PEDAL"
            nm = base if self._counters[base] == 0 else f"{base}{self._counters[base] + 1}"
        else:
            base = ROLE_PREFIX[self.name]
            nm = f"{base}_{_col_name(self._counters[base])}"
        self._counters[base] += 1
        self._by_block[block] = nm
        self.blocks[nm] = [n for sig in block for n in self.sig_notes[sig]]
        return nm

    def compute_score(self) -> List[Tuple[str, int]]:
        """Whole-lane song map: [(block_name, count)] over all bars, naming as it goes.

        One flat segmentation per lane (no per-section re-slicing) keeps block names
        consistent and avoids fragmenting a riff that straddles a section boundary.
        """
        self.score: List[Tuple[str, int]] = [
            (self.name_block(block), count) for block, count in segment_score(self.sigs)]
        return self.score


# --------------------------------------------------------------------------- #
# Tempo map: convert the IR tempo map to absolute BEATS.
# --------------------------------------------------------------------------- #
def _bar_start_beats(track: GPTrack) -> Tuple[List[float], float]:
    starts: List[float] = []
    acc = 0.0
    for m in track.measures:
        starts.append(acc)
        acc += m.time_sig[0] * 4.0 / m.time_sig[1]
    return starts, acc


def tempo_map_beats(song: GPSong) -> List[Dict[str, float]]:
    """IR tempo map -> [{"beat","bpm"}]. For .gp/GPIF the IR keys changes by BAR INDEX
    (not beat -- see parse_guitarpro._from_gpif), so convert through cumulative bar
    lengths; the PyGuitarPro path already accumulates true beats.
    """
    starts, _total = _bar_start_beats(song.tracks[0])
    n = len(starts)
    seen: "collections.OrderedDict[float, float]" = collections.OrderedDict()
    for pos, bpm in song.tempo_map:
        if song.fmt == "gp":
            idx = max(0, min(n - 1, int(round(pos))))
            beat = starts[idx]
        else:
            beat = float(pos)
        seen[round(beat, 4)] = float(bpm)
    if 0.0 not in seen:
        seen[0.0] = float(song.initial_tempo)
        seen.move_to_end(0.0, last=False)
    return [{"beat": b, "bpm": v} for b, v in sorted(seen.items())]


# --------------------------------------------------------------------------- #
# Whole-song build: lanes + a per-lane song map (flat [(block, count)] score).
# --------------------------------------------------------------------------- #
LANE_ORDER = ("lead", "rhythm", "bass", "vox", "drums")  # drums last -> ch.9


def _assign_lanes(song: GPSong) -> "collections.OrderedDict[str, Lane]":
    """Map the song's tracks onto named lanes (best-effort, role-based)."""
    guitars = [t for t in song.tracks if not t.is_percussion and not t.is_bass and not t.is_vocal]
    bass = song.bass_tracks()
    vox = song.vocal_tracks()
    perc = [t for t in song.tracks if t.is_percussion]
    # rhythm = busiest guitar (most note-bearing beats), lead = the other / next busiest
    guitars_sorted = sorted(guitars, key=lambda t: sum(1 for _, b in t.iter_beats() if b.pitches),
                            reverse=True)
    lanes: "collections.OrderedDict[str, Lane]" = collections.OrderedDict()
    if guitars_sorted:
        lanes["rhythm"] = Lane("rhythm", guitars_sorted[0], "distortion-guitar")
    if len(guitars_sorted) > 1:
        lanes["lead"] = Lane("lead", guitars_sorted[1], "distortion-guitar")
    if bass:
        lanes["bass"] = Lane("bass", bass[0], "electric-bass-pick")
    if vox:
        prog = vox[0].gm_program
        instr = "tenor-sax" if prog == 66 else "rock-organ"
        lanes["vox"] = Lane("vox", vox[0], instr)
    if perc:
        lanes["drums"] = Lane("drums", perc[0], "drum-kit")
    # re-order to LANE_ORDER for stable output
    return collections.OrderedDict(
        (k, lanes[k]) for k in LANE_ORDER if k in lanes)


def build_song(path: str) -> Dict:
    """Parse + transcribe + compress a GP file into a driver-ready structure."""
    song = load(path)
    if not song.tracks:
        raise ValueError(f"{path}: no tracks parsed")
    lanes = _assign_lanes(song)
    nbars = max(len(l.bars) for l in lanes.values())
    _starts, total_beats = _bar_start_beats(song.tracks[0])

    # One flat song map (block, count) per lane -- the reusable-blocks + structure.
    for lane in lanes.values():
        lane.compute_score()

    return {
        "title": song.title or Path(path).stem,
        "artist": song.artist or "",
        "fmt": song.fmt,
        "bpm": int(round(song.initial_tempo)),
        "time_signature": "4/4",
        "tempo_map": tempo_map_beats(song),
        "lanes": lanes,
        "n_bars": nbars,
        "total_beats": total_beats,
        "key": estimate_key(_pitch_class_weights(song)),
    }


# --------------------------------------------------------------------------- #
# Human-readable breakdown.
# --------------------------------------------------------------------------- #
def _score_str(score: List[Tuple[str, int]]) -> str:
    return " ".join(f"{nm}x{c}" if c > 1 else nm for nm, c in score)


def print_breakdown(data: Dict) -> None:
    key = data.get("key") or {}
    print(f"{data['artist'] or 'Unknown'} - {data['title']}  [{data['fmt']}]")
    print(f"  {data['bpm']} BPM  |  key {key.get('tonic', '?')} {key.get('scale', '?')}  |  "
          f"{data['n_bars']} bars / {data['total_beats']:.0f} beats")
    print(f"  tempo map: {len(data['tempo_map'])} changes")
    print("\n  Blocks per lane (unique named blocks) + song-map length:")
    for name, lane in data["lanes"].items():
        kinds = collections.Counter(
            "rest" if k.startswith("REST") else "pedal" if k.startswith("PEDAL") else "riff"
            for k in lane.blocks)
        print(f"    {name:7} ({lane.instrument:18}): {len(lane.blocks):3} blocks "
              f"{dict(kinds)}, song map {len(lane.score):3} entries")
    rhythm = data["lanes"].get("rhythm") or next(iter(data["lanes"].values()))
    print(f"\n  Song map (rhythm lane '{rhythm.name}'):")
    print(f"    {_score_str(rhythm.score)}")


# --------------------------------------------------------------------------- #
# Codegen: emit a compose_<slug>.py in the compose_doom_* idiom.
# --------------------------------------------------------------------------- #
def _slug(data: Dict) -> str:
    import re
    raw = f"{data['artist']}-{data['title']}" if data["artist"] else data["title"]
    return re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_") or "song"


def _compact_body(notes: List[Dict[str, str]], indent: str = "    ", width: int = 92) -> str:
    """Notes -> an `ln("P:dur ...")` literal, wrapped across adjacent string lines.

    Short blocks stay on one line; long ones split at token boundaries into
    implicitly-concatenated string literals (a trailing space keeps tokens apart).
    """
    toks = [f'{n["pitch"]}:{n["duration"]}' for n in notes]
    one = " ".join(toks)
    if len(one) <= width:
        return f'ln("{one}")'
    cont = indent + "    "
    lines: List[str] = []
    cur = ""
    for t in toks:
        if cur and len(cur) + 1 + len(t) > width:
            lines.append(cur)
            cur = t
        else:
            cur = f"{cur} {t}" if cur else t
    if cur:
        lines.append(cur)
    body = "\n".join(
        f'{cont}"{seg}{"" if i == len(lines) - 1 else " "}"'
        for i, seg in enumerate(lines))
    return f"ln(\n{body})"


def _block_bar_count(lane: Lane, block_name: str) -> int:
    """Bars in a named block, recovered from the block->name registry."""
    for block, name in lane._by_block.items():
        if name == block_name:
            return len(block)
    return 1


def _py_blocks(varname: str, lane: Lane) -> str:
    parts = [f"{varname} = {{"]
    for nm, notes in lane.blocks.items():
        bars = _block_bar_count(lane, nm)
        parts.append(
            f'    "{nm}": {_compact_body(notes)},'
            f'   # {bars} bar(s), {len(notes)} events')
    parts.append("}")
    return "\n".join(parts)


def _py_score(varname: str, score: List[Tuple[str, int]], per_line: int = 6) -> str:
    """A lane's song map -> `NAME_SCORE = [("RIFF_A", 8), ...]`, wrapped for reading."""
    items = [f'("{nm}", {c})' for nm, c in score]
    lines = [f"{varname} = ["]
    for i in range(0, len(items), per_line):
        lines.append("    " + ", ".join(items[i:i + per_line]) + ",")
    lines.append("]")
    return "\n".join(lines)


def _clean_meta(artist: str, title: str) -> Tuple[str, str]:
    """Tidy messy GP metadata: dedup a repeated artist, drop an artist prefix on title."""
    parts = [p.strip() for p in (artist or "").split(",") if p.strip()]
    artist = parts[0] if parts else ""
    if artist and title.lower().startswith(artist.lower()):
        rest = title[len(artist):].lstrip(" -")
        title = rest or title
    return artist, title


def emit_driver(data: Dict, out_path: str) -> str:
    """Write a self-contained compose_<slug>.py recreating the song from blocks."""
    lanes: "collections.OrderedDict[str, Lane]" = data["lanes"]
    artist, song_title = _clean_meta(data["artist"], data["title"])
    title = f"{artist} - {song_title} (Recreation)".strip(" -")
    key = data.get("key") or {}
    lane_names = list(lanes.keys())
    rhythm = lanes.get("rhythm") or lanes[lane_names[0]]

    header = f'''#!/usr/bin/env python3
"""
{title}
=== a FAITHFUL recreation of a real doom song, written in the compose_doom_*.py idiom ===

Auto-generated by transcribe_song.py / analysis.extract_blocks from the Guitar Pro tab,
then iterable like compose_doom_drowned_cathedral.py. Each lane is expressed as named,
reusable BLOCKS (riffs / grooves / pedals / rests) plus a flat SONG MAP -- a
`[(block, count), ...]` score that cycles those blocks to rebuild the whole part. Tweak
a block, or re-order / re-count a song map, to spin a new piece off this structure.

  Key/feel : {key.get('tonic', '?')} {key.get('scale', '?')}, {data['bpm']} BPM, {data['n_bars']} bars / {data['total_beats']:.0f} beats
  Lanes    : {", ".join(f"{n}={l.instrument}" for n, l in lanes.items())}

FAITHFUL on pitch, voicing, rhythm, every drum hit, the tempo map and the arrangement.
NOT reproduced: per-note velocity (absent from the source IR -> flat) and notated meter
changes (kept as a global 4/4 -- audio is unaffected since durations are absolute beats).
"""

import sys
from pathlib import Path

REPO = Path(__file__).parent
sys.path.insert(0, str(REPO))

from skills.generate_midi import generate_midi_from_dict, parse_duration


def ln(s):
    """Compact "P:dur P:dur ..." note string -> [{"pitch","duration"}, ...].

    `P` is a pitch (`B1`), a chord (`B2+Gb3+B3`), a drum name, or a rest (`R`);
    `dur` is a skill duration token (`2`, `d4`, `T8`). Whitespace-separated, so a
    block that took dozens of dict lines is one readable string here.
    """
    return [dict(zip(("pitch", "duration"), t.rsplit(":", 1))) for t in s.split()]


def expand(blocks, score):
    """A lane's [(block_name, count), ...] song map -> a flat list of note dicts."""
    out = []
    for name, count in score:
        out += blocks[name] * count
    return out


def beats(notes):
    return sum(parse_duration(n["duration"]) for n in notes)
'''

    var_for = {n: n.upper() for n in lane_names}
    block_sections = []
    for name in lane_names:
        lane = lanes[name]
        block_sections.append(
            f"# ===================== {name.upper()} blocks "
            f"({lane.instrument}) =====================\n"
            + _py_blocks(var_for[name], lane)
            + "\n\n"
            + _py_score(f"{var_for[name]}_SCORE", lane.score))

    instr_map = "{\n" + "".join(
        f'    "{n}": "{lanes[n].instrument}",\n' for n in lane_names) + "}"
    blocks_map = "{\n" + "".join(f'    "{n}": {var_for[n]},\n' for n in lane_names) + "}"
    scores_map = "{\n" + "".join(f'    "{n}": {var_for[n]}_SCORE,\n' for n in lane_names) + "}"

    tempo_block = "TEMPO_MAP = [\n" + "".join(
        f'    {{"beat": {c["beat"]:.0f}, "bpm": {c["bpm"]:.0f}}},\n'
        for c in data["tempo_map"]) + "]"

    builder = f'''
# =========================== arrangement / plumbing ===========================
LANES = {tuple(lane_names)!r}
INSTRUMENTS = {instr_map}
BLOCKS = {blocks_map}
SONG_MAPS = {scores_map}

{tempo_block}

# Rebuild every lane from its song map; all lanes span the same bars, so they share
# one total length (asserted below) -- no manual rest-padding needed.
timeline = {{lane: expand(BLOCKS[lane], SONG_MAPS[lane]) for lane in LANES}}

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
    print(f"Title : {title}")
    print(f"Lanes : {{', '.join(LANES)}}")
    print(f"Length: {{total:.0f}} beats")
    print("Blocks: " + ", ".join(f"{{l}}={{len(BLOCKS[l])}}" for l in LANES))
    nev = sum(len(t["notes"]) for t in composition["tracks"])
    print(f"Events: {{nev}} notes/chords across {{len(composition['tracks'])}} tracks")
    path = generate_midi_from_dict(composition)
    print(f"MIDI written: {{path}}")
    stem = Path(path).stem
    print(f'Render to WAV:  python render_wav.py 0.7 "{{stem}}"')
'''

    src = header + "\n\n" + "\n\n".join(block_sections) + "\n\n" + builder
    Path(out_path).write_text(src, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    data = build_song(sys.argv[1])
    print_breakdown(data)
