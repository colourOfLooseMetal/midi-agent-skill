"""
Type definitions for music composition.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Union


# A pitch can be a single note ("C4"), a chord written as a "+"-joined string
# ("C2+G2+C3"), or a list of notes (["C2", "G2", "C3"]). All notes in a chord
# share one start time and one duration -- this is how a power chord lives in a
# single track instead of being faked with parallel tracks. "R"/"rest"/"-" is a rest.
PitchSpec = Union[str, List[str]]


@dataclass
class Note:
    """A single musical note, a chord, or a rest."""
    pitch: PitchSpec  # "C4", a chord "C2+G2+C3" / ["C2","G2","C3"], or a rest "R"
    duration: str  # e.g., "4" (quarter), "8" (eighth), "2" (half), "1" (whole)
    velocity: Optional[int] = None  # 1-127; None -> generator default (100)


@dataclass
class Track:
    """A track containing notes for a single instrument."""
    notes: List[Note] = field(default_factory=list)
    instrument: Optional[str] = None  # GM instrument name


@dataclass
class TempoChange:
    """A tempo change at a given beat offset from the start of the piece."""
    beat: float
    bpm: float


@dataclass
class Composition:
    """A complete musical composition."""
    title: str
    bpm: int
    tracks: List[Track] = field(default_factory=list)
    # Optional tempo map for pacing (half-time feel, accel/rit, section shifts).
    # `bpm` remains the initial tempo; tempo_map entries are applied on top.
    tempo_map: List[TempoChange] = field(default_factory=list)
    time_signature: str = "4/4"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data: Dict[str, Any] = {
            "title": self.title,
            "bpm": self.bpm,
            "time_signature": self.time_signature,
            "tracks": [
                {
                    "instrument": t.instrument,
                    "notes": [_note_to_dict(n) for n in t.notes],
                }
                for t in self.tracks
            ],
        }
        if self.tempo_map:
            data["tempo_map"] = [{"beat": c.beat, "bpm": c.bpm} for c in self.tempo_map]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Composition":
        """Create from dictionary."""
        tracks = []
        for t in data.get("tracks", []):
            notes = [_note_from_dict(n) for n in t.get("notes", [])]
            tracks.append(Track(notes=notes, instrument=t.get("instrument")))

        tempo_map = [
            TempoChange(beat=float(c.get("beat", 0)), bpm=float(c.get("bpm", data.get("bpm", 90))))
            for c in data.get("tempo_map", [])
        ]

        return cls(
            title=data.get("title", "untitled"),
            bpm=data.get("bpm", 90),
            tracks=tracks,
            tempo_map=tempo_map,
            time_signature=data.get("time_signature", "4/4"),
        )


def _note_to_dict(n: Note) -> Dict[str, Any]:
    """Serialize a Note, omitting velocity when it is the default (None)."""
    d: Dict[str, Any] = {"pitch": n.pitch, "duration": n.duration}
    if n.velocity is not None:
        d["velocity"] = n.velocity
    return d


def _note_from_dict(n: Dict[str, Any]) -> Note:
    """Build a Note from a dict, preserving chord (str/list) pitch and velocity."""
    velocity = n.get("velocity")
    if velocity is not None:
        try:
            velocity = int(velocity)
        except (ValueError, TypeError):
            velocity = None
    return Note(pitch=n["pitch"], duration=str(n["duration"]), velocity=velocity)
