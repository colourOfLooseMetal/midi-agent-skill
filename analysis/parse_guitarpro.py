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
_VOCAL_NAME_RE = re.compile(r"voc|voice|sing|lyric|\bvox\b|choir", re.IGNORECASE)


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
    is_vocal: bool = False        # a sung/vocal line (analyzed separately, like drums)
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
    sections: List[Tuple[int, str]] = field(default_factory=list)  # (bar_index, label)
    lyrics: str = ""                       # best-effort joined lyric text (often empty)

    def pitched_tracks(self) -> List[GPTrack]:
        """Tracks that carry pitched notes (drop percussion and empty tracks).

        Vocal tracks are pitched and are intentionally kept here (they belong to the
        song's harmony/key), but analyze.py excludes them from riff/representative
        selection so a sung line is never mistaken for the main instrumental riff.
        """
        return [t for t in self.tracks
                if not t.is_percussion and any(b.pitches for _, b in t.iter_beats())]

    def vocal_tracks(self) -> List[GPTrack]:
        """Pitched vocal tracks that actually carry notes."""
        return [t for t in self.tracks
                if t.is_vocal and not t.is_percussion
                and any(b.pitches for _, b in t.iter_beats())]


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
        is_vocal = (not is_perc
                    and (bool(_VOCAL_NAME_RE.search(t.name or ""))
                         or 52 <= t.channel.instrument <= 54))  # GM choir/voice programs
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
            is_vocal=is_vocal,
            measures=measures,
        ))

    # Section markers (rehearsal marks) live on the shared measure headers.
    sections: List[Tuple[int, str]] = []
    for i, mh in enumerate(getattr(song, "measureHeaders", []) or []):
        mk = getattr(mh, "marker", None)
        title = getattr(mk, "title", "") if mk is not None else ""
        if title:
            sections.append((i, title))

    return GPSong(
        title=song.title or Path(path).stem,
        artist=song.artist or "",
        fmt=Path(path).suffix.lower().lstrip("."),
        initial_tempo=initial_tempo,
        tempo_map=tempo_map,
        tracks=tracks,
        sections=sections,
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


def _is_tie_dest(note_el) -> bool:
    """True if this GPIF note ties INTO the previous one (a sustain, not a new onset)."""
    tie = note_el.find("Tie")
    return tie is not None and tie.get("destination") == "true"


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
        # Tuning lives in a <Property name="Tuning"><Pitches>..</Pitches></Property>
        # (low->high). The older `.//Tuning/Pitches` element form is kept as a fallback.
        tuning_lh = []
        for prop in tr.findall(".//Property"):
            if prop.get("name") == "Tuning":
                pit = prop.find("Pitches")
                if pit is not None and pit.text:
                    tuning_lh = [int(x) for x in pit.text.split()]
                break
        if not tuning_lh:
            pitches_el = tr.find(".//Tuning/Pitches")
            tuning_lh = [int(x) for x in pitches_el.text.split()] if pitches_el is not None and pitches_el.text else []
        instr_type = (tr.find(".//InstrumentSet/Type").text or "") \
            if tr.find(".//InstrumentSet/Type") is not None else ""
        is_perc = "Percussion" in instr_type or bool(_DRUM_NAME_RE.search(name))
        is_vocal = (not is_perc
                    and (bool(_VOCAL_NAME_RE.search(name)) or instr_type.lower() == "voice"))
        # Drum-kit articulation index -> output MIDI note (percussion notes reference
        # this instead of String/Fret/Midi properties). Non-percussion tracks also have
        # an InstrumentSet/Elements tree (used for notation), so only consult this for
        # percussion tracks -- otherwise melodic notes get misread as drum hits.
        artic_midi = ([int(_text(a, "OutputMidiNumber", "0"))
                       for a in tr.findall(".//InstrumentSet/Elements/Element/Articulations/Articulation")]
                      if is_perc else [])
        track_meta.append({"name": name, "gm": gm, "tuning_low_high": tuning_lh,
                            "perc": is_perc, "vocal": is_vocal, "artic_midi": artic_midi})

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
                        note_els = [notes[nid] for nid in note_ids if nid in notes]
                        midi = [m for m in (note_midi(ne, tuning, meta["artic_midi"]) for ne in note_els)
                                if m is not None]
                        # A beat whose every note ties INTO the previous note is a sustain,
                        # not a new attack. Within the bar, fold its time into the held note
                        # (so following onsets keep their grid position); across the barline,
                        # emit a rest that holds the time without registering as an onset.
                        if note_els and all(_is_tie_dest(ne) for ne in note_els):
                            if mbeats and not mbeats[-1].is_rest:
                                mbeats[-1].duration_beats += db
                            else:
                                mbeats.append(GPBeat(pitches=[], duration_beats=db, is_rest=True))
                            continue
                        mbeats.append(GPBeat(pitches=midi, duration_beats=db, is_rest=not midi))
            measures.append(GPMeasure(time_sig=(num, den), beats=mbeats))
        out_tracks.append(GPTrack(
            name=meta["name"], gm_program=meta["gm"], is_percussion=meta["perc"],
            tuning=tuning, is_vocal=meta["vocal"], measures=measures,
        ))

    # Section markers: a <Section> child of a MasterBar names that bar (Intro, Verse, ...).
    sections: List[Tuple[int, str]] = []
    for i, mb in enumerate(masterbars):
        sec = mb.find("Section")
        if sec is None:
            continue
        letter = sec.find("Letter")
        text = sec.find("Text")
        label = ((letter.text if letter is not None and letter.text else "")
                 or (text.text if text is not None and text.text else ""))
        if label:
            sections.append((i, label.strip()))

    # Lyrics: best-effort. The GPIF <Lyrics> block is often empty (oohs/instrumental
    # tabs), so this is a bonus signal, not the primary vocal feature.
    lyric_lines = []
    for ly in root.findall(".//Lyrics"):
        for ln in ly.findall(".//Line"):
            txt = ln.find("Text")
            if txt is not None and txt.text and txt.text.strip():
                lyric_lines.append(txt.text.strip())
    lyrics_text = " ".join(lyric_lines)

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
        sections=sections, lyrics=lyrics_text,
    )


if __name__ == "__main__":
    import sys
    song = load(sys.argv[1])
    print(f"{song.artist} - {song.title}  [{song.fmt}]  tempo {song.initial_tempo:.0f}")
    for t in song.tracks:
        nbeats = sum(len(m.beats) for m in t.measures)
        print(f"  track {t.name!r:24} GM {t.gm_program:3d}  perc={t.is_percussion}  "
              f"measures={len(t.measures)}  beats={nbeats}  tuning={t.tuning}")
