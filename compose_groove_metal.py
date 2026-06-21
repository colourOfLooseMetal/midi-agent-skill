#!/usr/bin/env python3
"""
Build a groove-metal composition dict and render it via the midi-generation skill.

Like compose_stoner_doom.py, this script does NOT touch midiutil -- it only
prepares the Composition data and hands it to
skills.generate_midi.generate_midi_from_dict. All MIDI work (channels, program
changes, file writing) is done by the skill.

It exercises two skill features hard, the way groove metal actually needs them:

  * **The rest token** (`pitch "R"`), following resources/groove-metal-composition.md:
      - D Phrygian-dominant (D, Eb, F#, G, A, Bb, C), roots in octave 2 = "Drop D".
      - Gallop-and-slam built from the *rest* variant of the gallop ("16,R16,16,16")
        so the muted chug is staccato/gated, not ringing.
      - Power-chord slam layer that RESTS through the muted chug and blooms in only
        on the release -- "the cleanest way to make the slam open up".
      - A cold open, a subtraction breakdown, and a hard outro stab (not a fade).

  * **Single-track power chords + velocity.** The slam is ONE `distortion-guitar`
    track whose hits are stacked "root+5th+octave" chords (e.g. "C2+G2+C3"), not
    three parallel layer-tracks -- it reads as one chordal part. Velocity gives the
    gated chug a lower level than the exploding slam chords so the dynamic that
    *defines* the genre is real, not a flat velocity-100 wall.

Because groove metal needs each track doing different things (staccato chug vs.
slam chords that enter late), this builds per-track timelines section by section
and asserts every track in a section has identical length -- a leading/!trailing
rest is how a voice waits its turn while sharing the one t=0 timeline.
"""

import sys
from pathlib import Path

REPO = Path(__file__).parent
sys.path.insert(0, str(REPO))

from skills.generate_midi import generate_midi_from_dict, parse_pitch, parse_duration

FLATS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
REST_TOKENS = ("r", "rest", "-")


def midi_to_pitch(m: int) -> str:
    return FLATS[m % 12] + str(m // 12 - 1)


def is_rest(p: str) -> bool:
    return p.strip().lower() in REST_TOKENS


def T(seq, semitones):
    """Transpose a [(pitch, duration), ...] sequence, leaving rests untouched."""
    return [(p, d) if is_rest(p) else (midi_to_pitch(parse_pitch(p) + semitones), d)
            for p, d in seq]


def PC(seq):
    """Root line -> root+5th+octave power chords in ONE track (rests preserved).

    Each "Dn" root becomes a stacked chord string "Dn+An+D(n+1)" the generator
    sounds together -- the readable replacement for parallel slam/slam5/slamO tracks.
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


def R(d):
    return ("R", d)


def _rest_span(total):
    """Build a rest list summing to `total` beats out of whole/quarter/etc rests."""
    out = []
    remaining = round(total, 6)
    for tok, val in (("1", 4.0), ("2", 2.0), ("4", 1.0), ("8", 0.5), ("16", 0.25), ("32", 0.125)):
        while remaining >= val - 1e-9:
            out.append(("R", tok))
            remaining = round(remaining - val, 6)
    return out


# --------------------------------------------------------------------------
# Riff cells (the muted chug "lead" line; D Phrygian-dominant, roots in oct 2)
# --------------------------------------------------------------------------
# Gallop via a TRUE REST (16,R16,16,16) -> staccato/gated "long-short-short".
GALLOP = [("D2", "16"), R("16"), ("D2", "16"), ("D2", "16")]   # 1 beat

# Verse chug bar: two gated gallops, a syncopated push with a real gap, then
# the b7 "drop" stab (C2) as the release.
CHUG_VERSE = GALLOP + GALLOP + [("D2", "8"), R("8")] + [("C2", "4")]   # 4 beats

# Slam that lands ONLY on the release of the verse bar: rest through the chug
# (3 beats), then the C2 power chord rings a quarter.
SLAM_VERSE = _rest_span(3.0) + [("C2", "4")]                            # 4 beats

# Chorus: open, ringing power chords -- the catchiest, most "open" riff.
CHORUS_ROOT = [("D2", "2"), ("C2", "2"), ("Bb1", "2"), ("C2", "2")]    # 8 beats (2 bars)

# Breakdown crawl: one crushing, half-time chug per root, with a rest gap as the
# lurch and a 2-beat ring as the release. Same shape transposed down a half-step.
def crawl_bar(root):
    return [(root, "4"), R("8"), (root, "8"), (root, "2")]             # 4 beats


# --------------------------------------------------------------------------
# Section builder: each section is {track: seq}; all tracks must be equal length.
# Tracks: chug (muted gallop), slam (chordal power-chord hits), harm (pinch
# squeals), bass (locked an octave below). The three old slam layers are now one
# chordal slam track via PC().
# --------------------------------------------------------------------------
TRACK_ORDER = ["chug", "slam", "harm", "bass"]
tracks = {k: [] for k in TRACK_ORDER}


def add_section(name, **parts):
    lengths = {k: beats(v) for k, v in parts.items()}
    total = max(lengths.values())
    for k in TRACK_ORDER:
        seq = parts.get(k)
        if seq is None:
            seq = _rest_span(total)            # track sits this section out
        if abs(beats(seq) - total) > 1e-6:
            raise ValueError(f"[{name}] track '{k}' is {beats(seq)} beats, expected {total}")
        tracks[k].extend(seq)


# 1. COLD OPEN -- chug states the riff alone for 2 bars; the band rests in.
add_section("cold-open", chug=CHUG_VERSE * 2)

# 2/3. SLAM-IN + VERSE -- full band locks; the chordal slam blooms on each release.
for _ in range(4):
    add_section(
        "verse",
        chug=CHUG_VERSE,
        slam=PC(SLAM_VERSE),                   # root+5th+octave power chord, one track
        bass=T(CHUG_VERSE, -12),               # bass locks note-for-note, oct down
    )

# 4. PRE-CHORUS LIFT -- straighter, denser; harmonics squeal enters on the lift.
prelift = [("D2", "8")] * 6 + [("F2", "8"), ("F#2", "8")]              # 4 beats, climbing
add_section(
    "pre-chorus",
    chug=prelift * 2,
    bass=T(prelift * 2, -12),
    harm=_rest_span(7.0) + [("D5", "4")],      # one pinch-harmonic squeal on the &
)

# 5. CHORUS -- open power chords ring; chug rests so the chords breathe.
add_section(
    "chorus",
    slam=PC(CHORUS_ROOT),
    bass=T(CHORUS_ROOT, -12),
)

# 6. VERSE 2 -- variation; same engine, two bars.
for _ in range(2):
    add_section(
        "verse2",
        chug=CHUG_VERSE,
        slam=PC(SLAM_VERSE),
        bass=T(CHUG_VERSE, -12),
    )

# 7a. BREAKDOWN (subtraction) -- a single crushing chug exposed; slam goes SILENT.
for root in ("D2", "D2"):
    add_section(
        "breakdown-exposed",
        chug=crawl_bar(root),
        bass=T(crawl_bar(root), -12),
        # slam/harm omitted -> they rest. Real subtraction.
    )

# 7b. BREAKDOWN (crawl, slam returns) -- chromatic half-step crawl, full weight.
for root in ("D2", "Db2", "C2", "B1"):
    cb = crawl_bar(root)
    add_section(
        "breakdown-crawl",
        chug=cb,
        slam=PC(cb),
        bass=T(cb, -12),
    )

# 8. FINAL CHORUS -- heaviest restatement.
add_section(
    "final-chorus",
    chug=[("D2", "16"), R("16"), ("D2", "16"), ("D2", "16")] * 8,      # driving chug under
    slam=PC(CHORUS_ROOT),
    bass=T(CHORUS_ROOT, -12),
)

# 9. OUTRO STAB -- one hard hit, then dead silence. Abrupt, not a fade.
stab = [("D2", "2"), R("2")]
add_section(
    "outro",
    chug=stab,
    slam=PC(stab),
    bass=T(stab, -12),
)


# --------------------------------------------------------------------------
# Velocity: the genre is defined by dynamic contrast, so don't ship a flat wall.
# Gated chug sits lower with light downbeat accents; the slam chords explode;
# pinch squeals cut; bass stays solid. (Velocity on rests is harmless -- the
# generator skips rests before reading velocity.)
# --------------------------------------------------------------------------
def with_velocity(seq, v):
    return [(p, d, v) for p, d in seq]


def accent_downbeats(seq, strong=100, normal=84, beats_per_bar=4):
    out, pos = [], 0.0
    for p, d in seq:
        v = strong if abs(pos % beats_per_bar) < 1e-6 else normal
        out.append((p, d, v))
        pos += parse_duration(d)
    return out


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
    "title": "Groove Metal - Gallop and Crawl",
    "bpm": 132,
    "time_signature": "4/4",
    "tracks": [
        {"instrument": "electric-guitar-muted", "notes": to_notes(accent_downbeats(tracks["chug"]))},   # palm-mute chug
        {"instrument": "distortion-guitar",     "notes": to_notes(with_velocity(tracks["slam"], 122))},  # chordal slam (root+5th+oct)
        {"instrument": "guitar-harmonics",      "notes": to_notes(with_velocity(tracks["harm"], 115))},  # pinch accents
        {"instrument": "electric-bass-pick",    "notes": to_notes(with_velocity(tracks["bass"], 106))},  # locked bass
    ],
}

if __name__ == "__main__":
    # All tracks share one timeline; verify they end at the same beat.
    lens = {name: beats([(n["pitch"], n["duration"]) for n in t["notes"]])
            for name, t in zip(TRACK_ORDER, composition["tracks"])}
    total = max(lens.values())
    assert all(abs(v - total) < 1e-6 for v in lens.values()), f"track length mismatch: {lens}"

    note_count = sum(len(t["notes"]) for t in composition["tracks"])
    rest_count = sum(1 for t in composition["tracks"] for n in t["notes"]
                     if n["pitch"].strip().lower() in ("r", "rest", "-"))
    seconds = total * 60.0 / composition["bpm"]
    print(f"Total: {total:.0f} beats / {total / 4:.0f} bars / ~{seconds:.0f}s "
          f"({int(seconds // 60)}:{int(seconds % 60):02d}) at {composition['bpm']} BPM")
    print(f"Tracks: {len(composition['tracks'])} (chug + chordal slam + harmonics + bass), "
          f"events: {note_count}, of which rests: {rest_count}")
    path = generate_midi_from_dict(composition)
    print(f"MIDI written: {path}")
