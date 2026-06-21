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

from analysis.parse_guitarpro import GPSong, GPTrack

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

# Common duration values (in quarter beats) -> human label, for the histogram.
DURATION_LABELS = [
    (4.0, "whole"), (3.0, "dotted-half"), (2.0, "half"), (1.5, "dotted-quarter"),
    (1.0, "quarter"), (0.75, "dotted-eighth"), (2 / 3, "quarter-triplet"),
    (0.5, "eighth"), (1 / 3, "eighth-triplet"), (0.375, "dotted-16th"),
    (0.25, "16th"), (1 / 6, "16th-triplet"), (0.125, "32nd"),
]


def _label_duration(beats: float) -> str:
    best = min(DURATION_LABELS, key=lambda x: abs(x[0] - beats))
    return best[1]


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
    """The pitched track with the most note-bearing beats -- the main riff carrier."""
    pitched = song.pitched_tracks()
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


def _structure(track: Optional[GPTrack]) -> Dict:
    """Repeated-bar detection on the representative track -> riff/repetition signal."""
    if track is None:
        return {"bars": 0, "unique_bars": 0, "repetition_ratio": 0.0, "top_riff_repeats": 0}
    sigs = []
    for m in track.measures:
        sig = tuple((tuple(sorted(b.pitches)), round(b.duration_beats, 4)) for b in m.beats)
        if sig:  # skip wholly empty bars
            sigs.append(sig)
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
            {"name": t.name, "gm_program": t.gm_program, "percussion": t.is_percussion}
            for t in song.tracks
        ],
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
