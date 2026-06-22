"""
General MIDI Percussion Key Map (the channel-10 / index-9 drum kit).

This is the data model for a REAL drum kit -- the one thing the rest of the skill
deliberately avoids. A track whose instrument is one of PERCUSSION_KEYS is routed to
MIDI channel 9 by generate_midi.py, where its note "pitches" are read as DRUM NAMES
(kick / snare / hihat-open / crash / tom-mid / ...) via resolve_drum, not as musical
pitches. Simultaneous hits use the same "+"-joined chord syntax as melodic chords
("kick+crash"), and "R" is still a rest.

Note numbers follow the standard GM Percussion Key Map (notes 35-81 on channel 10).
Reference: https://en.wikipedia.org/wiki/General_MIDI#Percussion
"""

import re
from typing import Dict, List, Union

# Instrument keys that mark a track as a real drum kit on channel 9. Kept distinct
# from the existing "drums" alias (which resolves to the *pitched* synth-drum voice,
# program 118) so nothing already relying on that changes behaviour.
PERCUSSION_KEYS = {
    "drum-kit", "drums-kit", "drumkit", "drum-set", "kit",
    "percussion", "gm-drums", "gm-kit",
}

# Drum name -> GM percussion note number (channel 10). Names mirror the vocabulary
# the analysis pipeline emits in resources/styles/*.md (kick, snare, hihat-open,
# hihat-closed, crash, ride, tom) plus the common aliases.
DRUM_NOTES: Dict[str, int] = {
    # kicks
    "kick": 36, "bass-drum": 36, "kick2": 35, "acoustic-bass-drum": 35,
    # snares & rims
    "snare": 38, "acoustic-snare": 38, "snare-electric": 40, "electric-snare": 40,
    "side-stick": 37, "rimshot": 37, "clap": 39, "hand-clap": 39,
    # hi-hats
    "hihat": 42, "hat": 42, "hihat-closed": 42, "closed-hat": 42,
    "hihat-pedal": 44, "pedal-hat": 44, "hihat-open": 46, "open-hat": 46,
    # cymbals
    "crash": 49, "crash1": 49, "crash2": 57, "splash": 55, "china": 52,
    "ride": 51, "ride1": 51, "ride2": 59, "ride-bell": 53,
    # toms (low -> high)
    "tom-floor-low": 41, "tom-floor": 43, "tom-low": 45, "tom-mid": 47,
    "tom-hi-mid": 48, "tom-high": 50, "tom": 45,
    # extras
    "tambourine": 54, "cowbell": 56, "vibraslap": 58,
}

DEFAULT_DRUM = 38  # unknown token -> snare (audible, keeps the grid's timing intact)

_norm = lambda s: re.sub(r"[\s_]+", "-", str(s).strip().lower())


def is_percussion_track(instrument: str) -> bool:
    """True if this instrument name denotes the real GM kit (channel 9)."""
    return bool(instrument) and _norm(instrument) in PERCUSSION_KEYS


def resolve_drum(token: Union[str, int]) -> int:
    """Resolve a drum name (or raw note number) to a GM percussion note (0-127).

    Never raises -- an unknown token falls back to DEFAULT_DRUM so a typo can't
    desync the kit's timing by dropping a note without advancing the cursor.
    """
    t = _norm(token)
    if t in DRUM_NOTES:
        return DRUM_NOTES[t]
    try:
        n = int(t)
        if 0 <= n <= 127:
            return n
    except ValueError:
        pass
    for key, note in DRUM_NOTES.items():       # fuzzy: "kicks" -> kick, etc.
        if t and (t in key or key in t):
            return note
    return DEFAULT_DRUM


def parse_drum_hits(spec: Union[str, list, tuple]) -> List[int]:
    """A drum spec -> list of GM notes sounded together.

    Accepts a single name ("snare"), a "+"-joined stack ("kick+crash"), a raw
    note number, or a list of any of these. Mirrors parse_pitches for melodic
    chords so the generator can treat drum hits exactly like chord events.
    """
    if isinstance(spec, (list, tuple)):
        tokens = [str(p) for p in spec]
    else:
        tokens = str(spec).split("+")
    return [resolve_drum(tok) for tok in tokens if str(tok).strip()]
