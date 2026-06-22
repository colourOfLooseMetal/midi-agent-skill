#!/usr/bin/env python3
"""
Parse a Guitar Pro file into a normalized intermediate representation (IR).

Why an IR: Guitar Pro is a far richer style-analysis source than MIDI -- it keeps
explicit bars, time signatures, a tempo map, exact note durations, and tab voicings
(string+fret => the exact chord shape). This module flattens those into one
format-agnostic IR so the analyzer in analyze.py never has to care which Guitar Pro
version a file came from.

Supported inputs:
  * .gp3 / .gp4 / .gp5 / .gtp  -> PyGuitarPro (the bulk of real-world tabs).
  * .gp (Guitar Pro 7/8)       -> stdlib zipfile + xml.etree on Content/score.gpif,
                                  no third-party dependency. Best-effort against the
                                  GPIF spec.
  * .gpx (Guitar Pro 6)        -> not supported (proprietary container).

The IR mirrors the skill's own Composition/Track/Note shape, so a parsed song could
later be turned back into a composition dict (style transfer) -- a future extension.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

_DRUM_NAME_RE = re.compile(r"drum|percussion|\bkit\b", re.IGNORECASE)


# --- IR ---------------------------------------------------------------------

@dataclass
class GPBeat:
    """One rhythmic event: a chord (>=2 pitches), a single note, or a rest."""
    pitches: List[int]            # MIDI note numbers; empty when is_rest
    duration_beats: float         # in quarter-note beats (quarter = 1.0)
    is_rest: bool = False


@dataclass
class GPMeasure:
    time_sig: Tuple[int, int]     # (numerator, denominator), e.g. (4, 4)
    beats: List[GPBeat] = field(default_factory=list)


@dataclass
class GPTrack:
    name: str
    gm_program: int               # General MIDI program (0-127)
    is_percussion: bool
    tuning: List[int]             # open-string MIDI pitches, high-to-low
    measures: List[GPMeasure] = field(default_factory=list)

    def iter_beats(self):
        for m in self.measures:
            for b in m.beats:
                yield m, b


@dataclass
class GPSong:
    title: str
    artist: str
    fmt: str
    initial_tempo: float
    tempo_map: List[Tuple[float, float]]   # (absolute_beat, bpm)
    tracks: List[GPTrack] = field(default_factory=list)

    def pitched_tracks(self) -> List[GPTrack]:
        """Tracks that carry pitched notes (drop percussion and empty tracks)."""
        return [t for t in self.tracks
                if not t.is_percussion and any(b.pitches for _, b in t.iter_beats())]


# --- public entry point -----------------------------------------------------

def load(path: str) -> GPSong:
    """Load any supported Guitar Pro file into the IR, dispatching on extension."""
    ext = Path(path).suffix.lower()
    if ext == ".gp":
        return _from_gpif(path)
    if ext == ".gpx":
        raise ValueError(
            ".gpx (Guitar Pro 6) is a proprietary container and is not supported. "
            "Re-export it as .gp (GP7/8) or .gp5 from Guitar Pro."
        )
    if ext in (".gp3", ".gp4", ".gp5", ".gtp"):
        return _from_pyguitarpro(path)
    raise ValueError(f"Unrecognized Guitar Pro extension: {ext!r}")


# --- PyGuitarPro path (gp3/gp4/gp5/gtp) -------------------------------------

def _dur_beats(duration) -> float:
    """PyGuitarPro Duration -> quarter-note beats, honoring dots and tuplets."""
    base = 4.0 / duration.value          # whole=4, half=2, quarter=1, eighth=0.5, ...
    if duration.isDotted:
        base *= 1.5
    tup = getattr(duration, "tuplet", None)
    if tup is not None and getattr(tup, "enters", 1):
        base *= tup.times / tup.enters   # triplet (3:2) -> *2/3
    return base


def _from_pyguitarpro(path: str) -> GPSong:
    try:
        import guitarpro
    except ImportError as e:  # pragma: no cover - environment-dependent
        raise ImportError(
            "Reading .gp3/.gp4/.gp5 needs PyGuitarPro. Install it with: "
            "pip install PyGuitarPro"
        ) from e

    song = guitarpro.parse(path)
    initial_tempo = float(song.tempo)
    tempo_map: List[Tuple[float, float]] = [(0.0, initial_tempo)]

    tracks: List[GPTrack] = []
    for ti, t in enumerate(song.tracks):
        is_perc = (getattr(t, "isPercussionTrack", False)
                   or t.channel.channel == 9
                   or bool(_DRUM_NAME_RE.search(t.name or "")))
        tuning = [s.value for s in t.strings]
        measures: List[GPMeasure] = []
        abs_beat = 0.0
        for m in t.measures:
            ts = (m.timeSignature.numerator, m.timeSignature.denominator.value)
            beats: List[GPBeat] = []
            voice = _lead_voice(m)
            for b in voice:
                db = _dur_beats(b.duration)
                is_rest = str(b.status).lower().endswith(("rest", "empty"))
                pitches = [] if is_rest else [n.realValue for n in b.notes]
                # capture tempo changes (mix-table) only from the first track's timeline
                if ti == 0:
                    mtc = getattr(b.effect, "mixTableChange", None)
                    tempo = getattr(mtc, "tempo", None) if mtc else None
                    if tempo is not None and tempo.value:
                        tempo_map.append((abs_beat, float(tempo.value)))
                beats.append(GPBeat(pitches=pitches, duration_beats=db, is_rest=is_rest or not pitches))
                abs_beat += db
            measures.append(GPMeasure(time_sig=ts, beats=beats))
        tracks.append(GPTrack(
            name=t.name or f"Track {ti + 1}",
            gm_program=t.channel.instrument,
            is_percussion=is_perc,
            tuning=tuning,
            measures=measures,
        ))

    return GPSong(
        title=song.title or Path(path).stem,
        artist=song.artist or "",
        fmt=Path(path).suffix.lower().lstrip("."),
        initial_tempo=initial_tempo,
        tempo_map=tempo_map,
        tracks=tracks,
    )


def _lead_voice(measure):
    """Return the first non-empty voice's beats (most GP tabs use voice 0)."""
    for v in measure.voices:
        if v.beats:
            return v.beats
    return []


# --- GPIF path (.gp, Guitar Pro 7/8) ----------------------------------------
# Best-effort parse of the score.gpif XML. The GPIF model is reference-based:
# MasterBars -> Bars -> Voices -> Beats -> (Rhythm, Notes). We resolve those id
# maps and convert string+fret to MIDI via each track's tuning.

_NOTEVALUE_DIVISION = {
    "Whole": 1, "Half": 2, "Quarter": 4, "Eighth": 8,
    "16th": 16, "32nd": 32, "64th": 64, "128th": 128,
}


def _from_gpif(path: str) -> GPSong:
    with zipfile.ZipFile(path) as zf:
        name = next((n for n in zf.namelist() if n.lower().endswith("score.gpif")), None)
        if name is None:
            raise ValueError(f"No score.gpif inside {path} -- not a GP7/8 .gp file?")
        root = ET.fromstring(zf.read(name))

    def _text(el, tag, default=""):
        child = el.find(tag) if el is not None else None
        return child.text if child is not None and child.text is not None else default

    score = root.find("Score")
    title = _text(score, "Title") or Path(path).stem
    artist = _text(score, "Artist") or _text(score, "Music")

    # id -> element maps for the reference graph
    rhythms = {r.get("id"): r for r in root.findall("./Rhythms/Rhythm")}
    notes = {n.get("id"): n for n in root.findall("./Notes/Note")}
    beats = {b.get("id"): b for b in root.findall("./Beats/Beat")}
    voices = {v.get("id"): v for v in root.findall("./Voices/Voice")}
    bars = {b.get("id"): b for b in root.findall("./Bars/Bar")}

    def rhythm_beats(rhythm_el) -> float:
        division = _NOTEVALUE_DIVISION.get(_text(rhythm_el, "NoteValue", "Quarter"), 4)
        base = 4.0 / division
        dot = rhythm_el.find("AugmentationDot")
        if dot is not None:
            count = int(dot.get("count", "1"))
            base *= (2.0 - 0.5 ** count)        # 1 dot -> *1.5, 2 dots -> *1.75
        tup = rhythm_el.find("PrimaryTuplet")
        if tup is not None:
            num = int(tup.get("num", "1")); den = int(tup.get("den", "1"))
            if num:
                base *= den / num
        return base

    def note_midi(note_el, tuning, artic_midi) -> Optional[int]:
        # Percussion notes carry a flat index into the track's drum-kit articulation
        # list (built below) instead of a String/Fret/Midi property.
        artic_el = note_el.find("InstrumentArticulation")
        if artic_el is not None and artic_el.text is not None:
            idx = int(artic_el.text)
            if 0 <= idx < len(artic_midi):
                return artic_midi[idx]
        props = {p.get("name"): p for p in note_el.findall("./Properties/Property")}
        if "Midi" in props:
            return int(_text(props["Midi"], "Number", "0"))
        if "String" in props and "Fret" in props:
            string = int(_text(props["String"], "String", "0"))   # 0 = lowest in GPIF
            fret = int(_text(props["Fret"], "Fret", "0"))
            if 0 <= string < len(tuning):
                return tuning[string] + fret
        return None

    # tracks: name, GM program, tuning (GPIF lists tuning low->high; we store high->low)
    track_meta = []
    for tr in root.findall("./Tracks/Track"):
        name = _text(tr, "Name") or f"Track {len(track_meta) + 1}"
        prog_el = tr.find(".//GeneralMidi/Program")
        if prog_el is None:
            prog_el = tr.find(".//Programm") or tr.find(".//Program")
        gm = int(prog_el.text) if prog_el is not None and prog_el.text else 0
        pitches_el = tr.find(".//Tuning/Pitches")
        tuning_lh = [int(x) for x in pitches_el.text.split()] if pitches_el is not None and pitches_el.text else []
        is_perc = (tr.find(".//InstrumentSet/Type") is not None and
                   "Percussion" in (tr.find(".//InstrumentSet/Type").text or "")) or \
            bool(_DRUM_NAME_RE.search(name))
        # Drum-kit articulation index -> output MIDI note (percussion notes reference
        # this instead of String/Fret/Midi properties). Non-percussion tracks also have
        # an InstrumentSet/Elements tree (used for notation), so only consult this for
        # percussion tracks -- otherwise melodic notes get misread as drum hits.
        artic_midi = ([int(_text(a, "OutputMidiNumber", "0"))
                       for a in tr.findall(".//InstrumentSet/Elements/Element/Articulations/Articulation")]
                      if is_perc else [])
        track_meta.append({"name": name, "gm": gm, "tuning_low_high": tuning_lh,
                            "perc": is_perc, "artic_midi": artic_midi})

    masterbars = root.findall("./MasterBars/MasterBar")
    out_tracks: List[GPTrack] = []
    for tidx, meta in enumerate(track_meta):
        tuning = list(reversed(meta["tuning_low_high"]))   # store high->low like PyGuitarPro
        measures: List[GPMeasure] = []
        for mb in masterbars:
            time_txt = _text(mb, "Time", "4/4")
            try:
                num, den = (int(x) for x in time_txt.split("/"))
            except ValueError:
                num, den = 4, 4
            bar_ids = (mb.find("Bars").text or "").split() if mb.find("Bars") is not None else []
            mbeats: List[GPBeat] = []
            if tidx < len(bar_ids):
                bar = bars.get(bar_ids[tidx])
                voice_ids = (bar.find("Voices").text or "").split() if bar is not None and bar.find("Voices") is not None else []
                voice_ids = [vid for vid in voice_ids if vid != "-1"]
                if voice_ids:
                    voice = voices.get(voice_ids[0])
                    beat_ids = (voice.find("Beats").text or "").split() if voice is not None and voice.find("Beats") is not None else []
                    for bid in beat_ids:
                        beat = beats.get(bid)
                        if beat is None:
                            continue
                        rhythm = rhythms.get(beat.find("Rhythm").get("ref")) if beat.find("Rhythm") is not None else None
                        db = rhythm_beats(rhythm) if rhythm is not None else 1.0
                        note_ids = (beat.find("Notes").text or "").split() if beat.find("Notes") is not None else []
                        midi = [note_midi(notes[nid], tuning, meta["artic_midi"]) for nid in note_ids if nid in notes]
                        midi = [m for m in midi if m is not None]
                        mbeats.append(GPBeat(pitches=midi, duration_beats=db, is_rest=not midi))
            measures.append(GPMeasure(time_sig=(num, den), beats=mbeats))
        out_tracks.append(GPTrack(
            name=meta["name"], gm_program=meta["gm"], is_percussion=meta["perc"],
            tuning=tuning, measures=measures,
        ))

    # tempo: MasterTrack automations of type Tempo, positioned by bar
    initial_tempo = 120.0
    tempo_map: List[Tuple[float, float]] = []
    for auto in root.findall("./MasterTrack/Automations/Automation"):
        if (auto.find("Type") is not None and auto.find("Type").text == "Tempo"):
            val = (auto.find("Value").text or "120").split()[0] if auto.find("Value") is not None else "120"
            bar = float(auto.find("Bar").text) if auto.find("Bar") is not None else 0.0
            tempo_map.append((bar, float(val)))
    if tempo_map:
        tempo_map.sort()
        initial_tempo = tempo_map[0][1]
    else:
        tempo_map = [(0.0, initial_tempo)]

    return GPSong(
        title=title, artist=artist, fmt="gp",
        initial_tempo=initial_tempo, tempo_map=tempo_map, tracks=out_tracks,
    )


if __name__ == "__main__":
    import sys
    song = load(sys.argv[1])
    print(f"{song.artist} - {song.title}  [{song.fmt}]  tempo {song.initial_tempo:.0f}")
    for t in song.tracks:
        nbeats = sum(len(m.beats) for m in t.measures)
        print(f"  track {t.name!r:24} GM {t.gm_program:3d}  perc={t.is_percussion}  "
              f"measures={len(t.measures)}  beats={nbeats}  tuning={t.tuning}")
