#!/usr/bin/env python3
"""
Generate MIDI file from a Composition object using midiutil.
Uses General MIDI program changes compatible with A320U.sf2 SoundFont.
"""

import os
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from midiutil import MIDIFile
from midi_types.music import Composition
from midi_types.gm_instruments import resolve_instrument


# Duration mapping: string notation to beats
DURATION_MAP = {
    "1": 4.0,      # whole note
    "2": 2.0,      # half note
    "d2": 3.0,     # dotted half
    "4": 1.0,      # quarter note
    "d4": 1.5,     # dotted quarter
    "8": 0.5,      # eighth note
    "d8": 0.75,    # dotted eighth
    "16": 0.25,    # sixteenth note
    "32": 0.125,   # thirty-second note
    "T4": 1/3,     # triplet quarter
    "T8": 1/6,     # triplet eighth
}


# Pitch sentinels that mean "rest" (silence). A rest advances the time cursor by
# its duration without sounding a note. Matched case-insensitively after stripping.
REST_TOKENS = {"r", "rest", "-"}


def is_rest(pitch_str: str) -> bool:
    """Return True if a Note's pitch denotes a rest rather than an audible pitch."""
    return isinstance(pitch_str, str) and pitch_str.strip().lower() in REST_TOKENS


def parse_pitch(pitch_str: str) -> int:
    """
    Convert pitch string to MIDI note number.

    Examples:
        "C4" -> 60
        "A4" -> 69
        "F#5" -> 78
        "Bb3" -> 58

    Args:
        pitch_str: Pitch in format like "C4", "F#5", "Bb3"

    Returns:
        MIDI note number (0-127)
    """
    # Note names to semitones from C
    note_map = {
        'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
    }

    # Parse the pitch string
    match = re.match(r'^([A-Ga-g])([#b]?)(-?\d+)$', pitch_str)
    if not match:
        raise ValueError(f"Invalid pitch format: {pitch_str}")

    note, accidental, octave = match.groups()
    note = note.upper()
    octave = int(octave)

    # Calculate MIDI note number
    # MIDI note 60 = C4 (Middle C)
    midi_note = (octave + 1) * 12 + note_map[note]

    # Apply accidental
    if accidental == '#':
        midi_note += 1
    elif accidental == 'b':
        midi_note -= 1

    return max(0, min(127, midi_note))


def parse_pitches(pitch) -> list:
    """
    Convert a pitch spec into a list of MIDI note numbers (a chord).

    Accepts a single pitch ("C4"), a "+"-joined chord string ("C2+G2+C3"), or a
    list of pitches (["C2", "G2", "C3"]). All resulting notes are sounded together
    on one track -- this is how a power chord lives in a single track rather than
    being faked with parallel tracks. Reuses parse_pitch for each token.
    """
    if isinstance(pitch, (list, tuple)):
        tokens = [str(p) for p in pitch]
    else:
        tokens = str(pitch).split("+")
    return [parse_pitch(tok.strip()) for tok in tokens if tok.strip()]


def parse_time_signature(time_signature: str):
    """
    Parse a "num/den" time signature into midiutil's (numerator, denominator_power).

    midiutil expresses the denominator as a power of two: 4/4 -> (4, 2) since 2**2=4,
    6/8 -> (6, 3), 2/2 -> (2, 1). Falls back to 4/4 on bad input.
    """
    try:
        num_str, den_str = time_signature.split("/")
        numerator = int(num_str)
        denominator = int(den_str)
        if numerator > 0 and denominator > 0 and (denominator & (denominator - 1)) == 0:
            return numerator, denominator.bit_length() - 1
    except (ValueError, AttributeError):
        pass
    return 4, 2  # default 4/4


def parse_duration(duration_str: str) -> float:
    """
    Convert duration string to beats.

    Args:
        duration_str: Duration notation (e.g., "4", "8", "d4", "T8")

    Returns:
        Duration in beats
    """
    # Try direct lookup
    if duration_str in DURATION_MAP:
        return DURATION_MAP[duration_str]

    # Try to parse as a number (assume it's the note division)
    try:
        division = float(duration_str)
        if division > 0:
            return 4.0 / division  # 4 beats = whole note
    except ValueError:
        pass

    # Default to quarter note
    return 1.0


def generate_midi(composition: Composition) -> str:
    """
    Generate a MIDI file from a Composition object.

    Each track is assigned to a different MIDI channel with its own instrument.
    Channel 10 (index 9) is skipped as it's reserved for drums in General MIDI.

    Args:
        composition: The composition to convert to MIDI

    Returns:
        The path to the generated MIDI file
    """
    num_tracks = len(composition.tracks)
    midi = MIDIFile(num_tracks)

    for track_idx, track in enumerate(composition.tracks):
        # Assign MIDI channel (0-15, skip channel 9 which is drums)
        # Channel 9 (index 9) is reserved for drums in GM
        if track_idx < 9:
            channel = track_idx
        else:
            channel = track_idx + 1  # Skip channel 9

        # Ensure we don't exceed 16 channels
        channel = channel % 16
        if channel == 9:
            channel = 10 if track_idx < 15 else 0

        # Set track name
        track_name = track.instrument or f"Track {track_idx + 1}"
        midi.addTrackName(track_idx, 0, track_name)

        # Set tempo, time signature, and the tempo map on the first track.
        if track_idx == 0:
            midi.addTempo(track_idx, 0, composition.bpm)
            numerator, denom_power = parse_time_signature(composition.time_signature)
            midi.addTimeSignature(track_idx, 0, numerator, denom_power, 24)
            # Tempo map: half-time feel, accel/rit, per-section tempo shifts.
            for change in composition.tempo_map:
                midi.addTempo(track_idx, change.beat, change.bpm)

        # Set instrument (program change)
        program = resolve_instrument(track.instrument) if track.instrument else 0
        midi.addProgramChange(track_idx, channel, 0, program)

        # Add notes
        time = 0.0  # Current time in beats
        for note in track.notes:
            try:
                duration = parse_duration(note.duration)

                # A rest advances the cursor without emitting a note, leaving
                # true silence. Check before parse_pitch (which would raise on a
                # rest sentinel and skip the note WITHOUT advancing time).
                if is_rest(note.pitch):
                    time += duration
                    continue

                # A chord = several pitches sounded together: one addNote per tone
                # at the same time and duration, then advance the cursor once.
                pitches = parse_pitches(note.pitch)
                velocity = note.velocity if note.velocity is not None else 100
                velocity = max(1, min(127, int(velocity)))

                for pitch in pitches:
                    midi.addNote(
                        track=track_idx,
                        channel=channel,
                        pitch=pitch,
                        time=time,
                        duration=duration,
                        volume=velocity
                    )

                time += duration
            except Exception as e:
                print(f"Warning: Skipping note {note.pitch} {note.duration}: {e}", file=sys.stderr)

    # Create output directory
    out_dir = Path(__file__).parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', composition.title)
    file_path = out_dir / f"{safe_title}.mid"

    # Write MIDI file
    with open(file_path, 'wb') as f:
        midi.writeFile(f)

    return str(file_path)


def generate_midi_from_dict(data: dict) -> str:
    """
    Generate MIDI from a dictionary representation.

    Args:
        data: Dictionary with title, bpm, and tracks

    Returns:
        Path to the generated MIDI file
    """
    composition = Composition.from_dict(data)
    return generate_midi(composition)


if __name__ == "__main__":
    import json

    # Example usage -- showcases chords-in-one-track, per-note velocity, and a
    # tempo map. The piano plays triads as single "C4+E4+G4" chord events; the
    # bass uses accents (velocity); the tempo eases from 120 down to 96.
    example = {
        "title": "Test Multi-Instrument",
        "bpm": 120,
        "time_signature": "4/4",
        "tempo_map": [
            {"beat": 0, "bpm": 120},
            {"beat": 8, "bpm": 96}
        ],
        "tracks": [
            {
                "instrument": "acoustic-grand-piano",
                "notes": [
                    {"pitch": "C4+E4+G4", "duration": "4"},
                    {"pitch": "D4+F4+A4", "duration": "4"},
                    {"pitch": "E4+G4+B4", "duration": "4"},
                    {"pitch": "C4+E4+G4+C5", "duration": "2"}
                ]
            },
            {
                "instrument": "acoustic-bass",
                "notes": [
                    {"pitch": "C2", "duration": "2", "velocity": 110},
                    {"pitch": "G2", "duration": "2", "velocity": 80},
                    {"pitch": "C2", "duration": "1", "velocity": 100}
                ]
            },
            {
                "instrument": "violin",
                "notes": [
                    {"pitch": "E5", "duration": "8"},
                    {"pitch": "F5", "duration": "8"},
                    {"pitch": "G5", "duration": "4"},
                    {"pitch": "E5", "duration": "2"}
                ]
            }
        ]
    }

    result = generate_midi_from_dict(example)
    print(f"Generated: {result}")
