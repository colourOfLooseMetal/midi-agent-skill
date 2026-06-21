#!/usr/bin/env python3
"""
Build a stoner-doom composition dict and render it via the midi-generation skill.

This script does NOT generate MIDI itself -- it only prepares the Composition
data (defining the riff once and turning it into power chords) and hands it to
skills.generate_midi.generate_midi_from_dict. All MIDI work (channels, program
changes, file writing) is done by the skill.

Genre choices follow resources/stoner-doom-composition.md:
  - C minor, 68 BPM felt in half-time, minor-blues scale (the b5 "money note").
  - Power chords live in ONE guitar track: each riff note becomes a stacked
    "root+5th+octave" chord (e.g. "C2+G2+C3"), not three parallel tracks. This
    reads cleanly in a DAW/MIDI as a single chordal guitar part.
  - Bass doubles the root an octave below; rock organ holds a low root drone,
    mixed quieter (velocity) so it sits underneath the wall of fuzz.
  - Downbeat accents (velocity) give the guitar metric weight instead of a flat
    velocity-100 wall; a tempo map drops into the "even slower" climax.
  - Riff worship: state the riff, cycle it, vary the tail, breather, return
    heavier, then an "even slower" climax, decay on the home chord.
"""

import sys
from pathlib import Path

REPO = Path(__file__).parent
sys.path.insert(0, str(REPO))

from skills.generate_midi import generate_midi_from_dict, parse_pitch, parse_duration

# --- pitch helpers (data prep only; transposition keeps the power chords aligned)
FLATS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
REST_TOKENS = ("r", "rest", "-")


def midi_to_pitch(m: int) -> str:
    return FLATS[m % 12] + str(m // 12 - 1)


def is_rest(p: str) -> bool:
    return p.strip().lower() in REST_TOKENS


def transpose(seq, semitones):
    """Transpose a [(pitch, duration), ...] sequence, preserving rhythm and rests."""
    return [(p, d) if is_rest(p) else (midi_to_pitch(parse_pitch(p) + semitones), d)
            for p, d in seq]


def power_chord(seq):
    """Turn a single-note root line into root+5th+octave power chords in ONE track.

    Each "Cn" root becomes a stacked chord string "Cn+Gn+C(n+1)" the generator
    sounds together -- the readable replacement for parallel layered tracks.
    """
    out = []
    for p, d in seq:
        if is_rest(p):
            out.append((p, d))
        else:
            m = parse_pitch(p)
            out.append(("+".join([midi_to_pitch(m), midi_to_pitch(m + 7), midi_to_pitch(m + 12)]), d))
    return out


def beats(seq):
    return sum(parse_duration(d) for _, d in seq)


def with_velocity(seq, v):
    """Stamp a constant velocity on every note in a sequence (3-tuples)."""
    return [(p, d, v) for p, d in seq]


def accent_downbeats(seq, strong=115, normal=95, beats_per_bar=4):
    """Louder on bar downbeats, softer off them -- metric weight, not a flat wall."""
    out, pos = [], 0.0
    for p, d in seq:
        v = strong if abs(pos % beats_per_bar) < 1e-6 else normal
        out.append((p, d, v))
        pos += parse_duration(d)
    return out


# --- riffs (the root line; C minor blues, roots in octave 2 = the "down-tuning")
# Main riff (Iommi shape): pedal root -> climb to the b5 tritone -> fall home.
A      = [("C2", "d4"), ("Eb2", "8"), ("F2", "4"), ("Gb2", "2"), ("F2", "4"), ("Eb2", "4"), ("C2", "4")]
# Same riff, but let the home note ring (whole note) -- ends a cycle group.
A_ring = [("C2", "d4"), ("Eb2", "8"), ("F2", "4"), ("Gb2", "2"), ("F2", "4"), ("Eb2", "4"), ("C2", "1")]
# Variation: lean harder on the tritone, leave the tail darker/unresolved.
B      = [("C2", "d4"), ("Eb2", "8"), ("Gb2", "2"), ("F2", "4"), ("Gb2", "2"), ("Eb2", "4")]
# Psych "jam": a flowing bluesy quarter-note run for motion/contrast.
JAM    = [("C2", "4"), ("Eb2", "4"), ("F2", "4"), ("Gb2", "4"), ("G2", "4"), ("F2", "4"), ("Eb2", "4"), ("C2", "4")]
# The "even slower" trick: main riff at half speed for the heaviest section.
C      = [("C2", "d2"), ("Eb2", "4"), ("F2", "2"), ("Gb2", "1"), ("F2", "2"), ("Eb2", "2"), ("C2", "1")]
# Intro: sustained root statement, a hint of the b3, build anticipation.
INTRO  = [("C2", "1"), ("C2", "1"), ("Eb2", "2"), ("C2", "2")]
# Breather: sparse, tritone-laden, slow -- the dynamic dip before the return.
BREATH = [("C2", "1"), ("Gb2", "2"), ("F2", "2"), ("C2", "1"), ("Eb2", "2"), ("C2", "2")]
# Outro: hit the tritone, fall home, let the whole notes decay into "feedback".
OUTRO  = [("C2", "1"), ("Gb2", "2"), ("Eb2", "2"), ("C2", "1"), ("C2", "1")]

# --- arrangement (riff worship: commit and cycle before you change anything)
pre_climax = (
    INTRO
    + A * 5 + A_ring     # main riff, stated and cycled
    + B * 2              # variation (darker tail)
    + BREATH             # strip-down breather
    + A * 3 + A_ring     # return
    + JAM * 3            # psych jam
    + A * 3              # back into the main riff, building
)
climax = C * 3           # "even slower" climax -- the heaviest moment
root_seq = pre_climax + climax + OUTRO

# Pacing: ride 68 BPM, then drop into the climax for the "even slower" payoff.
INITIAL_BPM = 68
climax_start = beats(pre_climax)

# --- organ: low root drone (C2) under everything, in whole notes.
# Voiced an octave below the guitar action so the only near-collisions become
# spread 7ths/9ths across octaves, never a harsh same-octave semitone cluster.
total = beats(root_seq)
whole_count = int(total // 4)
rem = int(round(total - whole_count * 4))
organ = [("C2", "1")] * whole_count + [("C2", "4")] * rem


def to_notes(seq):
    """Accept (pitch, duration) or (pitch, duration, velocity) tuples."""
    out = []
    for item in seq:
        note = {"pitch": item[0], "duration": item[1]}
        if len(item) > 2 and item[2] is not None:
            note["velocity"] = item[2]
        out.append(note)
    return out


composition = {
    "title": "Stoner Doom - Riff Worship",
    "bpm": INITIAL_BPM,
    "time_signature": "4/4",
    "tempo_map": [
        {"beat": 0, "bpm": INITIAL_BPM},
        {"beat": climax_start, "bpm": 56},   # the "even slower" climax also gets slower
    ],
    "tracks": [
        # ONE chordal guitar track: root+5th+octave power chords, accented downbeats.
        {"instrument": "distortion-guitar",  "notes": to_notes(accent_downbeats(power_chord(root_seq)))},
        # Bass: root an octave below, solid and even.
        {"instrument": "electric-bass-pick", "notes": to_notes(with_velocity(transpose(root_seq, -12), 105))},
        # Organ drone: quiet, sits underneath the fuzz.
        {"instrument": "rock-organ",         "notes": to_notes(with_velocity(organ, 60))},
    ],
}

if __name__ == "__main__":
    note_count = sum(len(t["notes"]) for t in composition["tracks"])
    bar_count = total / 4.0
    seconds = total * 60.0 / composition["bpm"]
    print(f"Total: {total:.0f} beats / {bar_count:.0f} bars / ~{seconds:.0f}s "
          f"({int(seconds // 60)}:{int(seconds % 60):02d}) at {composition['bpm']} BPM "
          f"(climax slows to 56 at beat {climax_start:.0f})")
    print(f"Tracks: {len(composition['tracks'])} (1 chordal guitar + bass + organ), "
          f"note/chord events: {note_count}")
    path = generate_midi_from_dict(composition)
    print(f"MIDI written: {path}")
