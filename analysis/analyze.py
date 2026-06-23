#!/usr/bin/env python3
"""
Extract stylistic features from a parsed Guitar Pro song (the IR from
parse_guitarpro.py). The point is to turn a real track into *measured*
characteristics -- tempo/pacing, rhythm, harmony/scale, voicing, and structure --
that a composer (human or agent) can reuse instead of leaning on a generic genre
template. style_card.py renders these features into a markdown style card.

Nothing here is Guitar-Pro-version-specific; it all operates on the IR.
"""

from __future__ import annotations

import collections
from typing import Dict, List, Optional, Tuple

from analysis.parse_guitarpro import GPMeasure, GPSong, GPTrack

PITCH_CLASSES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Scale templates as semitone offsets from the root.
SCALES = {
    "major (Ionian)":      {0, 2, 4, 5, 7, 9, 11},
    "natural minor (Aeolian)": {0, 2, 3, 5, 7, 8, 10},
    "Dorian":              {0, 2, 3, 5, 7, 9, 10},
    "Phrygian":            {0, 1, 3, 5, 7, 8, 10},
    "Phrygian dominant":   {0, 1, 4, 5, 7, 8, 10},
    "minor pentatonic":    {0, 3, 5, 7, 10},
    "minor blues":         {0, 3, 5, 6, 7, 10},
    "harmonic minor":      {0, 2, 3, 5, 7, 8, 11},
}

# GM Level 1 percussion key map (note number -> drum-kit voice category).
# Unmapped notes (cowbell, claves, shakers, etc.) fall back to "other".
GM_PERCUSSION_MAP = {
    35: "kick", 36: "kick",
    37: "snare", 38: "snare", 40: "snare",
    42: "hihat-closed", 44: "hihat-pedal", 46: "hihat-open",
    41: "tom", 43: "tom", 45: "tom", 47: "tom", 48: "tom", 50: "tom",
    49: "crash", 55: "crash", 57: "crash",
    51: "ride", 53: "ride", 59: "ride",
}

_SIXTEENTH = 0.25

# Common duration values (in quarter beats) -> human label, for the histogram.
DURATION_LABELS = [
    (4.0, "whole"), (3.0, "dotted-half"), (2.0, "half"), (1.5, "dotted-quarter"),
    (1.0, "quarter"), (0.75, "dotted-eighth"), (2 / 3, "quarter-triplet"),
    (0.5, "eighth"), (1 / 3, "eighth-triplet"), (0.375, "dotted-16th"),
    (0.25, "16th"), (1 / 6, "16th-triplet"), (0.125, "32nd"),
]

# Same beat values as DURATION_LABELS, but mapped to this skill's own duration
# tokens (see CLAUDE.md) so a transcribed riff can be pasted straight into a
# composition dict's `notes` list instead of being read as prose.
SKILL_DURATION_TOKENS = [
    (4.0, "1"), (3.0, "d2"), (2.0, "2"), (1.5, "d4"),
    (1.0, "4"), (0.75, "d8"), (2 / 3, "T4"),
    (0.5, "8"), (1 / 3, "T8"), (0.375, "d16"),
    (0.25, "16"), (1 / 6, "T16"), (0.125, "32"),
]

# Scale-degree names by semitone distance from a root, using the common flat-degree
# vernacular (1, b2, 2, b3, ...). This is template-agnostic -- it just names *where*
# a pitch sits relative to the tonic, which is far more reusable across keys than a
# bag of absolute pitch-class letters.
DEGREE_NAMES = ["1", "b2", "2", "b3", "3", "4", "b5", "5", "b6", "6", "b7", "7"]


def _label_duration(beats: float) -> str:
    best = min(DURATION_LABELS, key=lambda x: abs(x[0] - beats))
    return best[1]


def _skill_duration(beats: float) -> str:
    best = min(SKILL_DURATION_TOKENS, key=lambda x: abs(x[0] - beats))
    return best[1]


def degree_label(root_pc: int, pc: int) -> str:
    """Scale-degree name of pitch class `pc` relative to `root_pc` (e.g. 1, b3, b5)."""
    return DEGREE_NAMES[(pc - root_pc) % 12]


def _pitch_class_weights(song: GPSong) -> Dict[int, float]:
    """Duration-weighted pitch-class histogram across all pitched tracks."""
    weights = collections.defaultdict(float)
    for t in song.pitched_tracks():
        for _, b in t.iter_beats():
            for p in b.pitches:
                weights[p % 12] += b.duration_beats
    return dict(weights)


def estimate_key(pc_weights: Dict[int, float]) -> Optional[Dict]:
    """Template-match the pitch-class histogram against every root+scale."""
    total = sum(pc_weights.values())
    if total <= 0:
        return None
    best = None
    for root in range(12):
        for name, template in SCALES.items():
            in_scale = sum(w for pc, w in pc_weights.items() if (pc - root) % 12 in template)
            out_scale = total - in_scale
            root_w = pc_weights.get(root, 0.0)
            fifth_w = pc_weights.get((root + 7) % 12, 0.0)
            # reward in-scale mass + tonic/fifth emphasis, penalize chromatic spill,
            # and lightly prefer tighter scales so pentatonic isn't always beaten by 7-note sets
            score = in_scale - 0.9 * out_scale + 0.5 * root_w + 0.2 * fifth_w - 0.02 * len(template)
            if best is None or score > best["score"]:
                best = {"root": root, "scale": name, "score": score,
                        "tonic": PITCH_CLASSES[root]}
    best["confidence"] = max(0.0, min(1.0, best["score"] / total))
    return best


def _representative_track(song: GPSong) -> Optional[GPTrack]:
    """The pitched track with the most note-bearing beats -- the main riff carrier.

    Vocal tracks are excluded here so a busy sung line is never picked as "the riff";
    they get their own analysis in `_analyze_vocals`.
    """
    pitched = [t for t in song.pitched_tracks() if not t.is_vocal] or song.pitched_tracks()
    if not pitched:
        return None
    return max(pitched, key=lambda t: sum(1 for _, b in t.iter_beats() if b.pitches))


def _interval_stats(song: GPSong) -> Dict:
    """Vertical (chord) interval prevalence + chord-shape classification."""
    tritone = minor2 = fifth = 0
    chord_beats = power_chords = triads = single_notes = rest_beats = 0
    for t in song.pitched_tracks():
        for _, b in t.iter_beats():
            if b.is_rest or not b.pitches:
                rest_beats += 1
                continue
            pcs = sorted(set(p % 12 for p in b.pitches))
            if len(b.pitches) == 1:
                single_notes += 1
            else:
                chord_beats += 1
                intervals = {(a - pcs[0]) % 12 for a in pcs}
                if intervals <= {0, 7} or intervals <= {0, 7, 12 % 12}:
                    power_chords += 1
                elif {0, 4, 7} <= intervals or {0, 3, 7} <= intervals:
                    triads += 1
                # pairwise interval flavor
                for i in range(len(pcs)):
                    for j in range(i + 1, len(pcs)):
                        iv = (pcs[j] - pcs[i]) % 12
                        if iv == 6:
                            tritone += 1
                        elif iv == 1 or iv == 11:
                            minor2 += 1
                        elif iv == 7 or iv == 5:
                            fifth += 1
    return {
        "chord_beats": chord_beats, "power_chords": power_chords, "triads": triads,
        "single_notes": single_notes, "rest_beats": rest_beats,
        "tritone_hits": tritone, "minor2_hits": minor2, "fifth_hits": fifth,
    }


def _bar_signature(measure: GPMeasure) -> Tuple:
    """Equality key for "is this the same bar" -- pitches (sorted) + durations."""
    return tuple((tuple(sorted(b.pitches)), round(b.duration_beats, 4)) for b in measure.beats)


def _structure(track: Optional[GPTrack]) -> Dict:
    """Repeated-bar detection on the representative track -> riff/repetition signal."""
    if track is None:
        return {"bars": 0, "unique_bars": 0, "repetition_ratio": 0.0, "top_riff_repeats": 0}
    sigs = [sig for m in track.measures if (sig := _bar_signature(m))]  # skip empty bars
    counts = collections.Counter(sigs)
    bars = len(sigs)
    unique = len(counts)
    top = counts.most_common(1)[0][1] if counts else 0
    return {
        "bars": bars,
        "unique_bars": unique,
        "repetition_ratio": round(1 - unique / bars, 3) if bars else 0.0,
        "top_riff_repeats": top,
    }


def _transcribe_measure(measure: GPMeasure, root_pc: Optional[int]) -> List[Dict]:
    """One bar's beats as skill-syntax note dicts (pitch/duration), with scale degrees."""
    out = []
    for b in measure.beats:
        token = _skill_duration(b.duration_beats)
        if b.is_rest or not b.pitches:
            out.append({"pitch": "R", "duration": token, "degree": None})
            continue
        pitches = sorted(set(b.pitches))
        pitch_str = "+".join(_midi_name(p) for p in pitches)
        degree = degree_label(root_pc, pitches[0] % 12) if root_pc is not None else None
        out.append({"pitch": pitch_str, "duration": token, "degree": degree})
    return out


def _bar_onset_row(measure: GPMeasure) -> str:
    """16th-grid onset row ('X' where a note starts, '.' elsewhere) for one bar.

    Uses the same grid convention as the percussion pattern below, so a riff's
    onset row can be lined up by eye against where the kick/snare actually land.
    """
    num, den = measure.time_sig
    slot_count = max(1, round(num * 4.0 / den / _SIXTEENTH))
    row = ["."] * slot_count
    pos = 0.0
    for b in measure.beats:
        if not b.is_rest and b.pitches:
            row[min(slot_count - 1, round(pos / _SIXTEENTH))] = "X"
        pos += b.duration_beats
    return "".join(row)


def _pitchclass_sets(measure: GPMeasure) -> List[frozenset]:
    """The pitch-class set of each sounding beat in a bar (octave-collapsed)."""
    return [frozenset(p % 12 for p in b.pitches)
            for b in measure.beats if not b.is_rest and b.pitches]


def _is_pedal_bar(measure: GPMeasure) -> bool:
    """A drone/pedal bar that sits on one chord/root rather than moving like a riff.

    True when every sounding beat collapses to the SAME pitch-class set, so octave
    leaps or re-articulations of one chord count as a pedal (e.g. `B1+Gb2 -> B2+Gb3`
    is the root oscillating octaves, not a melodic figure). This is what kept Empress
    Rising's held-chord bars at the top of the old most-repeated ranking.
    """
    pcsets = _pitchclass_sets(measure)
    return bool(pcsets) and len(set(pcsets)) <= 1   # must sound something; an all-rest bar is neither


def _riff_entry(bars: List[GPMeasure], repeats: int, root_pc: Optional[int], kind: str) -> Dict:
    """Render a 1+ bar phrase into the transcription shape the style card consumes."""
    transcription: List[Dict] = []
    grids: List[str] = []
    for m in bars:
        transcription.extend(_transcribe_measure(m, root_pc))
        grids.append(_bar_onset_row(m))
    degree_seq = " -> ".join(e["degree"] for e in transcription if e["degree"])
    return {
        "repeats": repeats,
        "bars": len(bars),
        "kind": kind,                       # "riff" (moving) or "pedal" (drone)
        "time_sig": f"{bars[0].time_sig[0]}/{bars[0].time_sig[1]}",
        "transcription": transcription,
        "onset_grid": " | ".join(grids),    # one grid per bar, joined for multi-bar phrases
        "degree_sequence": degree_seq,
    }


def _top_riffs(track: Optional[GPTrack], root_pc: Optional[int], n: int = 3) -> Dict:
    """Find the song's real riffs, separating moving figures from drones.

    Two failure modes of the old "top-N most-repeated single bars" approach are fixed:
      * **Drones dominated.** In doom the single most-repeated bar is usually a held
        chord. Pedal bars are now classified out of the riff ranking and summarized
        separately, so the figures that actually *move* surface.
      * **Phrases got chopped.** A riff that spans 2 or 4 bars could only ever show as
        one of its bars. We now look for repeated multi-bar windows (width 4, 2, 1) and
        prefer wider phrases, so the whole hook is captured.
    """
    empty = {"riffs": [], "pedal": None, "pedal_ratio": 0.0}
    if track is None:
        return empty
    measures = [m for m in track.measures if _bar_signature(m)]   # skip empty bars
    if not measures:
        return empty

    # --- pedal/drone summary (the song's root center, reported but not ranked as a riff)
    pedal_bars = [m for m in measures if _is_pedal_bar(m)]
    pedal_ratio = round(len(pedal_bars) / len(measures), 3)
    pedal = None
    if pedal_bars:
        pcounts = collections.Counter(_bar_signature(m) for m in pedal_bars)
        psig, preps = pcounts.most_common(1)[0]
        pmeas = next(m for m in pedal_bars if _bar_signature(m) == psig)
        pedal = _riff_entry([pmeas], preps, root_pc, kind="pedal")

    # --- candidate riffs: repeated windows of decreasing width that actually move
    candidates: List[Tuple[int, int, List[GPMeasure]]] = []   # (width, repeats, bars)
    for width in (4, 2, 1):
        counts = collections.Counter()
        examples: Dict[Tuple, List[GPMeasure]] = {}
        for start in range(len(measures) - width + 1):
            win = measures[start:start + width]
            sig = tuple(_bar_signature(m) for m in win)
            counts[sig] += 1
            examples.setdefault(sig, win)
        for sig, reps in counts.most_common():
            if width > 1 and reps < 2:
                continue                     # a multi-bar phrase must actually recur
            win = examples[sig]
            if not any(_pitchclass_sets(m) for m in win):
                continue                     # all-rest window -> not a riff
            if all(_is_pedal_bar(m) for m in win):
                continue                     # pure drone -> covered by the pedal summary
            if width > 1 and len(set(sig)) < 2:
                continue                     # just one bar tiled; the width-1 pass has it
            candidates.append((width, reps, win))

    # rank: more repeats wins, but reward width so whole phrases beat their own sub-bars
    candidates.sort(key=lambda c: (c[1] * (0.5 + 0.5 * c[0]), c[0], c[1]), reverse=True)

    riffs: List[Dict] = []
    accepted_sets: List[frozenset] = []      # distinct bar-sigs already shown
    for width, reps, win in candidates:
        bar_sigs = frozenset(_bar_signature(m) for m in win)
        # skip rotations / sub-windows of a phrase we already kept (we process widest-first)
        if any(bar_sigs <= s for s in accepted_sets):
            continue
        riffs.append(_riff_entry(win, reps, root_pc, kind="riff"))
        accepted_sets.append(bar_sigs)
        if len(riffs) >= n:
            break

    return {"riffs": riffs, "pedal": pedal, "pedal_ratio": pedal_ratio}


def _analyze_vocals(song: GPSong, root_pc: Optional[int]) -> Optional[Dict]:
    """Melodic profile of the vocal line: range, scale degrees, phrasing -- like drums.

    Vocals aren't in this skill's instrument set, but the contour + phrasing tell a
    composer where to leave space in the riff and suggest a lead line (clean guitar /
    organ) that tracks the vocal. Best-effort lyric text is attached when present.
    """
    tracks = song.vocal_tracks()
    if not tracks:
        return None
    track = max(tracks, key=lambda t: sum(1 for _, b in t.iter_beats() if b.pitches))
    pitches = [p for _, b in track.iter_beats() for p in b.pitches]
    if not pitches:
        return None
    low, high = min(pitches), max(pitches)

    # phrasing: a rest gap of >= a half note (2 beats) breaks one sung phrase from the next
    phrases: List[int] = []
    cur = 0
    gap = 0.0
    for _, b in track.iter_beats():
        if b.is_rest or not b.pitches:
            gap += b.duration_beats
            if gap >= 2.0 and cur:
                phrases.append(cur); cur = 0
        else:
            if gap >= 2.0 and cur:
                phrases.append(cur); cur = 0
            cur += 1
            gap = 0.0
    if cur:
        phrases.append(cur)

    deg_hist = collections.Counter()
    if root_pc is not None:
        for p in pitches:
            deg_hist[degree_label(root_pc, p % 12)] += 1
    dur_hist = collections.Counter(_label_duration(b.duration_beats)
                                   for _, b in track.iter_beats() if not b.is_rest and b.pitches)

    # representative phrase: the longest unbroken sung run, transcribed in skill syntax
    rep_phrase: List[Dict] = []
    run: List = []
    best: List = []
    gap = 0.0
    for _, b in track.iter_beats():
        if b.is_rest or not b.pitches:
            gap += b.duration_beats
            if gap >= 2.0:
                if len(run) > len(best):
                    best = run
                run = []
        else:
            if gap >= 2.0:
                if len(run) > len(best):
                    best = run
                run = []
            run.append(b); gap = 0.0
    if len(run) > len(best):
        best = run
    for b in best:
        ps = sorted(set(b.pitches))
        rep_phrase.append({
            "pitch": "+".join(_midi_name(p) for p in ps),
            "duration": _skill_duration(b.duration_beats),
            "degree": degree_label(root_pc, ps[0] % 12) if root_pc is not None else None,
        })

    return {
        "track_name": track.name,
        "range_low": _midi_name(low),
        "range_high": _midi_name(high),
        "range_semitones": high - low,
        "note_count": len(pitches),
        "phrase_count": len(phrases),
        "avg_notes_per_phrase": round(sum(phrases) / len(phrases), 1) if phrases else 0.0,
        "degree_histogram": dict(deg_hist.most_common()),
        "duration_histogram": dict(dur_hist.most_common()),
        "representative_phrase": rep_phrase,
        "lyrics": song.lyrics[:400] if song.lyrics else "",
    }


def _arrangement(song: GPSong, total_bars: int) -> List[Dict]:
    """Section markers -> an ordered song map with 1-based bar ranges."""
    if not song.sections:
        return []
    secs = sorted(song.sections)
    out = []
    for j, (bar, label) in enumerate(secs):
        end = secs[j + 1][0] - 1 if j + 1 < len(secs) else max(total_bars - 1, bar)
        out.append({"label": label, "start_bar": bar + 1,
                    "end_bar": end + 1, "bars": end - bar + 1})
    return out


def _percussion_track(song: GPSong) -> Optional[GPTrack]:
    """The percussion track with the most note-bearing beats."""
    perc = [t for t in song.tracks if t.is_percussion]
    perc = [t for t in perc if any(b.pitches for _, b in t.iter_beats())]
    if not perc:
        return None
    return max(perc, key=lambda t: sum(1 for _, b in t.iter_beats() if b.pitches))


def _bar_grid_signature(measure: GPMeasure) -> Tuple[int, Tuple]:
    """Quantize a measure's percussion beats onto a 16th-note grid.

    Returns (slot_count, signature), where signature is a tuple of
    (slot, frozenset(categories)) pairs for every slot that has at least one hit.
    """
    num, den = measure.time_sig
    slot_count = max(1, round(num * 4.0 / den / _SIXTEENTH))
    pos = 0.0
    hits: Dict[int, set] = collections.defaultdict(set)
    for b in measure.beats:
        if not b.is_rest and b.pitches:
            slot = min(slot_count - 1, round(pos / _SIXTEENTH))
            for p in b.pitches:
                hits[slot].add(GM_PERCUSSION_MAP.get(p, "other"))
        pos += b.duration_beats
    sig = tuple(sorted((slot, frozenset(cats)) for slot, cats in hits.items()))
    return slot_count, sig


def _analyze_percussion(song: GPSong) -> Optional[Dict]:
    """Drum-kit voice breakdown, density, dominant groove pattern, and fill signal."""
    track = _percussion_track(song)
    if track is None:
        return None

    voice_counts = collections.Counter()
    bar_sigs = []
    slot_count = 16
    tom_bars = 0
    total_bars = 0
    for m in track.measures:
        sc, sig = _bar_grid_signature(m)
        if sig:
            slot_count = sc
            bar_sigs.append(sig)
            if any("tom" in cats for _, cats in sig):
                tom_bars += 1
        total_bars += 1
        for b in m.beats:
            if not b.is_rest and b.pitches:
                for p in b.pitches:
                    voice_counts[GM_PERCUSSION_MAP.get(p, "other")] += 1

    total_hits = sum(voice_counts.values())
    if total_hits == 0:
        return None

    counts = collections.Counter(bar_sigs)
    bars = len(bar_sigs)
    unique = len(counts)
    dominant_sig, top_repeats = (counts.most_common(1)[0] if counts else ((), 0))

    pattern = {}
    for slot, cats in dominant_sig:
        for cat in cats:
            row = pattern.setdefault(cat, ["."] * slot_count)
            row[slot] = "X"
    pattern_rows = {cat: "".join(row) for cat, row in sorted(pattern.items())}

    return {
        "track_name": track.name,
        "hits_per_bar": round(total_hits / total_bars, 2) if total_bars else 0.0,
        "voice_counts": dict(voice_counts.most_common()),
        "voice_percentages": {cat: round(100 * n / total_hits, 1)
                               for cat, n in voice_counts.most_common()},
        "pattern_bars": bars,
        "pattern_unique_bars": unique,
        "pattern_repetition_ratio": round(1 - unique / bars, 3) if bars else 0.0,
        "pattern_top_repeats": top_repeats,
        "dominant_pattern": pattern_rows,
        "tom_fill_ratio": round(tom_bars / total_bars, 3) if total_bars else 0.0,
    }


def analyze(song: GPSong) -> Dict:
    """Compute the full feature set for a parsed song."""
    pc_weights = _pitch_class_weights(song)
    key = estimate_key(pc_weights)

    # rhythm: duration histogram + time-signature distribution + density
    dur_hist = collections.Counter()
    timesig_hist = collections.Counter()
    total_bars = 0
    note_beats = 0
    for t in song.pitched_tracks():
        for m in t.measures:
            for b in m.beats:
                dur_hist[_label_duration(b.duration_beats)] += 1
                if not b.is_rest and b.pitches:
                    note_beats += 1
    rep = _representative_track(song)
    if rep is not None:
        for m in rep.measures:
            timesig_hist[f"{m.time_sig[0]}/{m.time_sig[1]}"] += 1
            total_bars += 1

    # register / down-tuning signal
    all_pitches = [p for t in song.pitched_tracks() for _, b in t.iter_beats() for p in b.pitches]
    lowest = min(all_pitches) if all_pitches else None
    highest = max(all_pitches) if all_pitches else None
    lowest_tuning = min((min(t.tuning) for t in song.pitched_tracks() if t.tuning), default=None)

    intervals = _interval_stats(song)
    structure = _structure(rep)
    root_pc = key["root"] if key else None
    riff_data = _top_riffs(rep, root_pc, n=3)
    vocals = _analyze_vocals(song, root_pc)
    total_bars_all = max((len(t.measures) for t in song.tracks), default=0)
    arrangement = _arrangement(song, total_bars_all)
    pc_degrees = ({PITCH_CLASSES[pc]: degree_label(root_pc, pc) for pc in pc_weights}
                  if root_pc is not None else {})

    # pacing
    half_time = song.initial_tempo <= 85
    tempo_changes = [(round(beat, 1), bpm) for beat, bpm in song.tempo_map[1:]]

    return {
        "title": song.title,
        "artist": song.artist,
        "format": song.fmt,
        "tempo": {
            "initial_bpm": round(song.initial_tempo, 1),
            "changes": tempo_changes,
            "half_time_feel": half_time,
        },
        "time_signatures": dict(timesig_hist.most_common()),
        "rhythm": {
            "duration_histogram": dict(dur_hist.most_common()),
            "notes_per_bar": round(note_beats / total_bars, 2) if total_bars else 0.0,
        },
        "harmony": {
            "key_estimate": key,
            "pitch_class_weights": {PITCH_CLASSES[pc]: round(w, 1)
                                    for pc, w in sorted(pc_weights.items(), key=lambda x: -x[1])},
            "pitch_class_degrees": pc_degrees,
            **intervals,
        },
        "register": {
            "lowest_note": _midi_name(lowest),
            "highest_note": _midi_name(highest),
            "lowest_open_string": _midi_name(lowest_tuning),
            "down_tuned": lowest_tuning is not None and lowest_tuning < 40,  # below E2
        },
        "structure": {
            "bars": structure["bars"],
            "unique_bars": structure["unique_bars"],
            "repetition_ratio": structure["repetition_ratio"],
            "most_repeated_bar_count": structure["top_riff_repeats"],
            "representative_track": rep.name if rep else None,
        },
        "instrumentation": [
            {"name": t.name, "gm_program": t.gm_program,
             "percussion": t.is_percussion, "vocal": t.is_vocal}
            for t in song.tracks
        ],
        "percussion": _analyze_percussion(song),
        "riffs": riff_data["riffs"],
        "pedal": riff_data["pedal"],
        "pedal_ratio": riff_data["pedal_ratio"],
        "vocals": vocals,
        "arrangement": arrangement,
    }


def _midi_name(m: Optional[int]) -> Optional[str]:
    if m is None:
        return None
    return f"{PITCH_CLASSES[m % 12]}{m // 12 - 1}"


if __name__ == "__main__":
    import json
    import sys
    from analysis.parse_guitarpro import load
    print(json.dumps(analyze(load(sys.argv[1])), indent=2, ensure_ascii=False))
