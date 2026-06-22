#!/usr/bin/env python3
"""
Export a Composition to a Guitar Pro file (.gp3/.gp4/.gp5) so it can be opened in
TuxGuitar or Guitar Pro for tab viewing/playback. This is the reverse direction of
analysis/parse_guitarpro.py (which reads a GP file INTO the skill's data model) --
here we write the skill's own Composition OUT to one.

Needs PyGuitarPro (lazy-imported, same optional dependency as the analysis
pipeline -- core MIDI generation in generate_midi.py still works without it).

Tab realism is explicitly NOT the goal: there is no real guitar/tuning behind a
generated composition, so frets are assigned by a synthetic per-track tuning that
only guarantees correct pitch + rhythm playback, not idiomatic fingering. Treat the
output as a viewer/player file, not an engraved chart.

Bar splitting: GP measures are fixed-length containers, but a Composition's notes
are just a flat per-track timeline with no bar markers. This module cuts measures
at the nominal time-signature length wherever that lands exactly on a note boundary
shared by every track (which is the common case for this repo's compose_*.py
drivers -- see CLAUDE.md's "N bars / N beats" authoring style). If a note would
straddle the nominal boundary in any track, the cut is deferred to the next shared
note boundary instead, producing one longer (but always structurally valid) bar
rather than splitting a note.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from midi_types.music import Composition
from midi_types.gm_instruments import resolve_instrument
from midi_types.gm_percussion import is_percussion_track, parse_drum_hits
from skills.generate_midi import is_rest, parse_duration, parse_pitches, parse_time_signature

EPS = 1e-6

# Skill duration token -> (GP Duration value, isDotted, tuplet (enters, times)).
# Reverse of generate_midi.DURATION_MAP, kept in beat-for-beat agreement with it.
_DURATION_TOKENS = {
    "1": (1, False, None), "2": (2, False, None), "d2": (2, True, None),
    "4": (4, False, None), "d4": (4, True, None),
    "8": (8, False, None), "d8": (8, True, None),
    "16": (16, False, None), "32": (32, False, None),
    "T4": (8, False, (3, 2)), "T8": (16, False, (3, 2)),
}
_STD_DIVISIONS = (1, 2, 4, 8, 16, 32, 64)


def _gp_duration(gp, token: str):
    """Map one of the skill's duration tokens to a PyGuitarPro Duration."""
    token = str(token)
    if token in _DURATION_TOKENS:
        value, dotted, tup = _DURATION_TOKENS[token]
    else:
        try:
            division = float(token)
            value = next((v for v in _STD_DIVISIONS if v >= division), _STD_DIVISIONS[-1])
        except ValueError:
            value, dotted, tup = 4, False, None
        else:
            dotted, tup = False, None
    tuplet = gp.Tuplet(enters=tup[0], times=tup[1]) if tup else gp.Tuplet()
    return gp.Duration(value=value, isDotted=dotted, tuplet=tuplet)


def _track_tuning(pitches: List[int], min_strings: int) -> List[int]:
    """A synthetic tuning (high->low, GP convention) wide enough that every pitch
    used in the track is reachable on some string, with at least `min_strings`
    strings so simultaneous chord tones can each get their own string.
    """
    if not pitches:
        return [40] * max(min_strings, 1)
    lo, hi = min(pitches), max(pitches)
    n = max(min_strings, 1)
    if n == 1:
        return [hi]
    span = max(hi - lo, 1)
    step = -(-span // (n - 1))  # ceil division: guarantees the lowest string reaches `lo`
    return [hi - i * step for i in range(n)]


def _assign_strings(pitches: List[int], tuning: List[int]) -> List[Tuple[int, int]]:
    """Pick a distinct (1-based string, fret>=0) for each pitch in a chord."""
    used = set()
    out = []
    for p in sorted(pitches, reverse=True):
        opts = [(i, p - tuning[i - 1]) for i in range(1, len(tuning) + 1) if p - tuning[i - 1] >= 0]
        if not opts:
            opts = [(len(tuning), max(0, p - tuning[-1]))]
        opts.sort(key=lambda t: (t[0] in used, t[1]))
        i, fret = opts[0]
        used.add(i)
        out.append((i, fret))
    return out


def _flatten_track(track, perc: bool) -> List[Tuple[List[int], str, Optional[int]]]:
    """Note list -> [(pitches, duration_token, velocity)], pitches empty == rest."""
    events = []
    for note in track.notes:
        if is_rest(note.pitch):
            events.append(([], note.duration, None))
        else:
            pitches = parse_drum_hits(note.pitch) if perc else parse_pitches(note.pitch)
            events.append((pitches, note.duration, note.velocity))
    return events


def _edge_set(events) -> set:
    t = 0.0
    edges = {0.0}
    for _pitches, token, _vel in events:
        t += parse_duration(token)
        edges.add(round(t, 6))
    return edges


def _measure_bounds(beats_per_measure: float, track_events: List[list]) -> List[Tuple[float, float]]:
    """Shared (start, end) cut points across every track's event stream, never
    splitting a note: cuts only ever land on a note boundary common to ALL tracks.
    """
    edge_sets = [_edge_set(ev) for ev in track_events]
    common = sorted(set.intersection(*edge_sets)) if edge_sets else [0.0]
    total = max((max(e) for e in edge_sets), default=0.0)
    bounds = []
    prev = 0.0
    while prev < total - EPS:
        candidates = [e for e in common if e >= prev + beats_per_measure - EPS]
        nxt = candidates[0] if candidates else total
        bounds.append((prev, nxt))
        prev = nxt
    return bounds


def _time_signature(gp, length: float, nominal_num: int, nominal_denom: int, nominal_beats: float):
    if abs(length - nominal_beats) < EPS:
        return gp.TimeSignature(numerator=nominal_num, denominator=gp.Duration(value=nominal_denom))
    # Irregular (note-boundary-forced) bar: declare it in 16th-note resolution.
    numerator = max(1, int(round(length * 4)))
    return gp.TimeSignature(numerator=numerator, denominator=gp.Duration(value=16))


def _slice_events(events, bounds: List[Tuple[float, float]]) -> List[list]:
    """Cut a flat event list into per-measure sublists at the given bounds."""
    out: List[list] = [[] for _ in bounds]
    t = 0.0
    mi = 0
    for ev in events:
        if mi < len(bounds) and t >= bounds[mi][1] - EPS:
            mi += 1
        if mi >= len(bounds):
            break
        out[mi].append(ev)
        t += parse_duration(ev[1])
    return out


def export_guitarpro(composition: Composition, fmt: str = "gp5") -> str:
    """Write a Composition to output/<sanitized-title>.<fmt> via PyGuitarPro.

    fmt is one of "gp3", "gp4", "gp5" (the formats PyGuitarPro can write; TuxGuitar
    opens all three). Returns the path written.
    """
    try:
        import guitarpro as gp
    except ImportError as e:  # pragma: no cover - environment-dependent
        raise ImportError(
            "Exporting to Guitar Pro needs PyGuitarPro. Install it with: "
            "pip install PyGuitarPro"
        ) from e

    if fmt not in ("gp3", "gp4", "gp5"):
        raise ValueError(f"Unsupported Guitar Pro export format: {fmt!r} (use gp3/gp4/gp5)")

    nominal_num, denom_power = parse_time_signature(composition.time_signature)
    nominal_denom = 2 ** denom_power
    beats_per_measure = nominal_num * (4.0 / nominal_denom)

    percs = [is_percussion_track(t.instrument) for t in composition.tracks]
    track_events = [_flatten_track(t, p) for t, p in zip(composition.tracks, percs)]
    bounds = _measure_bounds(beats_per_measure, track_events) or [(0.0, beats_per_measure)]

    song = gp.Song()
    song.title = composition.title
    song.tempo = max(1, int(round(composition.bpm)))
    song.tracks = []

    headers = []
    for start, end in bounds:
        header = gp.MeasureHeader(number=len(headers) + 1)
        header.timeSignature = _time_signature(gp, end - start, nominal_num, nominal_denom, beats_per_measure)
        headers.append(header)
    song.measureHeaders = headers

    melodic_channel = 0
    for ti, (track, perc, events) in enumerate(zip(composition.tracks, percs, track_events)):
        gp_track = gp.Track(song, number=ti + 1, name=(track.instrument or f"Track {ti + 1}")[:40])
        max_chord = max((len(p) for p, _d, _v in events), default=1)
        if perc:
            # GP's note bitmask is one bit per STRING, so simultaneous drum hits
            # (e.g. "kick+crash+ride") each need a distinct string -- a single
            # string can't carry more than one note in the same beat. Open value 0
            # on every string so a note's fret IS its raw GM drum number.
            tuning = [0] * max(max_chord, 1)
            gp_track.isPercussionTrack = True
            gp_track.channel.channel = 9
            gp_track.channel.effectChannel = 9
            gp_track.channel.instrument = 0
        else:
            tuning = _track_tuning([p for ev in events for p in ev[0]], max(6, max_chord))
            channel = melodic_channel
            channel = channel + 1 if channel >= 9 else channel  # skip ch.9 (drums), like generate_midi.py
            gp_track.channel.channel = channel % 16
            gp_track.channel.effectChannel = gp_track.channel.channel
            gp_track.channel.instrument = resolve_instrument(track.instrument) if track.instrument else 0
            melodic_channel += 1
        gp_track.strings = [gp.GuitarString(number=i + 1, value=v) for i, v in enumerate(tuning)]

        sliced = _slice_events(events, bounds)
        measures = []
        for header, measure_events in zip(headers, sliced):
            measure = gp.Measure(gp_track, header)
            voice = measure.voices[0]
            for pitches, token, velocity in measure_events:
                duration = _gp_duration(gp, token)
                if not pitches:
                    beat = gp.Beat(voice, duration=duration, status=gp.BeatStatus.rest)
                    voice.beats.append(beat)
                    continue
                beat = gp.Beat(voice, duration=duration, status=gp.BeatStatus.normal)
                voice.beats.append(beat)
                vel = max(15, min(127, int(velocity))) if velocity is not None else gp.Velocities.default
                notes = [
                    gp.Note(beat, value=fret, string=string_idx, velocity=vel, type=gp.NoteType.normal)
                    for string_idx, fret in _assign_strings(pitches, tuning)
                ]
                beat.notes = notes
            measures.append(measure)
        gp_track.measures = measures
        song.tracks.append(gp_track)

    # Tempo map: stamp a MixTableChange on the first beat of the first track that
    # starts exactly at each tempo_map beat offset (these are always section-start
    # boundaries shared by every track, so they line up with a measure boundary).
    if song.tracks and composition.tempo_map:
        ref_track = song.tracks[0]
        starts = {}  # rounded beat offset -> (measure_idx, beat_idx)
        t = 0.0
        mi = 0
        bi = 0
        for pitches, token, _vel in track_events[0]:
            starts[round(t, 6)] = (mi, bi)
            t += parse_duration(token)
            bi += 1
            if mi < len(bounds) and t >= bounds[mi][1] - EPS:
                mi += 1
                bi = 0
        for change in composition.tempo_map:
            hit = starts.get(round(change.beat, 6))
            if hit is None:
                continue
            mi, bi = hit
            beat = ref_track.measures[mi].voices[0].beats[bi]
            beat.effect.mixTableChange = gp.MixTableChange(
                tempo=gp.MixTableItem(value=max(1, int(round(change.bpm)))),
                hideTempo=False,
            )

    out_dir = Path(__file__).parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    import re
    safe_title = re.sub(r"[^a-zA-Z0-9_-]", "_", composition.title)
    file_path = out_dir / f"{safe_title}.{fmt}"
    with open(file_path, "wb") as f:
        gp.write(song, f)
    return str(file_path)


def export_guitarpro_from_dict(data: Dict, fmt: str = "gp5") -> str:
    """Export a Composition dict (the same shape generate_midi_from_dict takes)."""
    composition = Composition.from_dict(data)
    return export_guitarpro(composition, fmt)


if __name__ == "__main__":
    # Reuses generate_midi.py's demo composition so the two exporters are directly
    # comparable (same data, .mid vs. .gp5).
    example = {
        "title": "Test Multi-Instrument",
        "bpm": 120,
        "time_signature": "4/4",
        "tempo_map": [
            {"beat": 0, "bpm": 120},
            {"beat": 8, "bpm": 96},
        ],
        "tracks": [
            {
                "instrument": "acoustic-grand-piano",
                "notes": [
                    {"pitch": "C4+E4+G4", "duration": "4"},
                    {"pitch": "D4+F4+A4", "duration": "4"},
                    {"pitch": "E4+G4+B4", "duration": "4"},
                    {"pitch": "C4+E4+G4+C5", "duration": "2"},
                ],
            },
            {
                "instrument": "acoustic-bass",
                "notes": [
                    {"pitch": "C2", "duration": "2", "velocity": 110},
                    {"pitch": "G2", "duration": "2", "velocity": 80},
                    {"pitch": "C2", "duration": "1", "velocity": 100},
                ],
            },
            {
                "instrument": "violin",
                "notes": [
                    {"pitch": "E5", "duration": "8"},
                    {"pitch": "F5", "duration": "8"},
                    {"pitch": "G5", "duration": "4"},
                    {"pitch": "E5", "duration": "2"},
                ],
            },
        ],
    }
    result = export_guitarpro_from_dict(example, fmt="gp5")
    print(f"Generated: {result}")
