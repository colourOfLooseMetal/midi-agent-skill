#!/usr/bin/env python3
"""
Compose an ORIGINAL stoner/doom track -- "The Hollow Procession" -- and render it
through the midi-generation skill.

Like compose_stoner_doom.py, this script does NO MIDI work itself. It prepares a
Composition *dict* (defining root lines once and realizing them into voices) and
hands it to skills.generate_midi.generate_midi_from_dict. All channel/program/
file work belongs to the skill.

This is the "improved / more elaborate" sibling of compose_stoner_doom.py. Where
that driver runs ONE chordal guitar over bass + organ, this one is arranged like a
real doom band as measured in resources/styles/*.md (almost every analyzed track is
*two* distortion guitars + bass, several add organ):

  * LEAD/CHORD guitar  (distortion-guitar) -- the ringing power-chord riff, and the
    single-note lead during the psych jam.
  * CHUG guitar        (overdriven-guitar) -- a palm-muted SUB-octave gallop, a
    different instrument AND rhythm from the chords (the only thing CLAUDE.md says
    justifies a parallel track).
  * BASS               (electric-bass-pick) -- locked an octave below, doubling the
    riff's harmonic motion for mass; pedals a drone in the breakdown/jam.
  * ORGAN              (drawbar-organ) -- a quiet root+5th drone, present only in the
    spacious sections (intro / breakdown / jam / climax / outro) as psych colour,
    silent under the dense riffs so it never muddies the wall of fuzz.

Everything below is SYNTHESIZED from the measured style cards, not copied:

  * Key:    C Phrygian with a borrowed blues b5 (Gb). The cards are overwhelmingly
            Phrygian (Monolord, most Electric Wizard) or minor-blues (Dopethrone,
            Cursing the One, Feed the Dream). This blend carries BOTH signature
            colours: the b2 (Db) Phrygian grind and the b5 (Gb) blues "money note".
  * Octave: roots written in octave 2 for the chord stack; chug + bass live an
            octave below (down to C1). Real tracks bottom out at B0/Bb0/C1 -- far
            lower than C2 -- so the whole rig drops an octave vs. the old driver.
  * Voicing: power chords as single stacked pitches (root+5th+octave). All harmonic
            TENSION comes from ROOT MOTION (1 -> b2, 1 -> b5), never stacked
            semitone clusters -- matching the cards' "tritone x0 / minor-2nd x0
            within chords, fifths everywhere" finding and SKILL.md's dissonance rule.
  * Rhythm: the recurring measured signatures -- an eighth-triplet GALLOP
            (Funeralopolis/Dagger Dragger had ~1000+ triplets), a denser 16th CHUG
            for the return (Dopethrone/Satanic Rites), whole-note DRONE for the
            hypnotic sections (Cursing the One/Audhumbla), the Monolord octave-jump
            CALL/RESPONSE, and a Fu-Manchu-style REST inside a riff.
  * Form:   intro drone -> main riff cycled (riff worship) -> octave-lift -> darker
            variation -> subtraction breakdown -> psych jam -> heavier return ->
            "even slower" climax (tempo drops, the heaviest moment) -> decay.
  * Pacing: ~70 BPM half-time with subtle human tempo DRIFT at section seams (every
            card's tempo wanders +/-a few BPM) and a big rit. into the climax
            (Dopethrone famously sags to 48).
"""

import math
import sys
from pathlib import Path

REPO = Path(__file__).parent
sys.path.insert(0, str(REPO))

from skills.generate_midi import generate_midi_from_dict, parse_pitch, parse_duration

# --------------------------------------------------------------------------- #
# Pitch / duration helpers (pure data prep -- the skill does the real MIDI work)
# --------------------------------------------------------------------------- #
FLATS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
REST_TOKENS = ("r", "rest", "-")
EPS = 1e-6


def midi_to_pitch(m: int) -> str:
    """MIDI number -> flat-spelled pitch name (genre prefers Gb/Db over F#/C#)."""
    return FLATS[m % 12] + str(m // 12 - 1)


def is_rest(p) -> bool:
    return isinstance(p, str) and p.strip().lower() in REST_TOKENS


def beats(seq) -> float:
    """Total beats of a sequence of (pitch, dur) or (pitch, dur, velocity) tuples."""
    return sum(parse_duration(item[1]) for item in seq)


def transpose(seq, semitones):
    """Transpose a [(pitch, dur), ...] root line, preserving rhythm and rests."""
    return [(p, d) if is_rest(p) else (midi_to_pitch(parse_pitch(p) + semitones), d)
            for p, d in seq]


# Duration-doubling map for the "even slower" trick: play a riff at half speed by
# doubling every note value (an eighth becomes a quarter, a quarter a half, ...).
_DOUBLE = {"32": "16", "16": "8", "8": "4", "4": "2", "2": "1", "1": "1",
           "d8": "d4", "d4": "d2", "d2": "1", "T8": "T4", "T4": "T8"}


def halftime(seq):
    """Return the riff at half speed (the doom 'even slower' move)."""
    return [(p, _DOUBLE.get(d, d)) for p, d in seq]


# --------------------------------------------------------------------------- #
# Voicing helpers -- turn a single-note ROOT LINE into the three low voices.
# A power chord is ONE stacked-pitch event (root+5th+octave), never parallel
# tracks; tension is carried by where the roots move, not by stacking dissonance.
# --------------------------------------------------------------------------- #
def power_chord(seq):
    """Root line -> root+5th+octave power chords in a single track."""
    out = []
    for p, d in seq:
        if is_rest(p):
            out.append((p, d))
        else:
            m = parse_pitch(p)
            out.append(("+".join([midi_to_pitch(m), midi_to_pitch(m + 7),
                                   midi_to_pitch(m + 12)]), d))
    return out


def bass_of(seq, octave_shift=-12):
    """Bass line: the root motion, an octave below, single fat notes."""
    return transpose(seq, octave_shift)


def beat_roots(seq):
    """Sample which root is sounding at the start of each integer beat.

    Used to drive the CHUG gallop as a steady low pulse locked to the riff's
    harmony, independent of the chord guitar's exact rhythm (a palm-muted guitar
    pumps the root while the other guitar plays the figure). Rest beats stay rests.
    """
    total = int(round(beats(seq)))
    roots = [None] * total
    pos = 0.0
    for p, d in seq:
        b = parse_duration(d)
        start, end = pos, pos + b
        i = int(math.ceil(start - EPS))
        while i < end - EPS:
            if 0 <= i < total:
                roots[i] = p
            i += 1
        pos = end
    # carry the last known root into any unfilled beat (defensive)
    last = "C2"
    for i, r in enumerate(roots):
        if r is None:
            roots[i] = last
        else:
            last = roots[i]
    return roots


def gallop(root_line, sub="T4", octave_shift=-12):
    """Steady sub-octave chug: each beat filled with `sub`-note repeats of its root.

    `sub="T4"` -> 3 hits/beat (the eighth-triplet gallop the cards measure most);
    `sub="16"` -> 4 hits/beat (the denser Dopethrone/Satanic-Rites chug);
    `sub="8"`  -> 2 hits/beat (a slower creeping chug). Rest beats emit silence.
    """
    per_beat = int(round(1.0 / parse_duration(sub)))
    out = []
    for r in beat_roots(root_line):
        if is_rest(r):
            out += [("R", sub)] * per_beat
        else:
            p = midi_to_pitch(parse_pitch(r) + octave_shift)
            out += [(p, sub)] * per_beat
    return out


# --------------------------------------------------------------------------- #
# Dynamics -- per-note velocity by METRIC position (kick on 1, the big half-time
# snare on 3), so the wall breathes instead of sitting at a flat 100. The style
# cards repeatedly note "the source has real accents MIDI velocity can mimic".
# --------------------------------------------------------------------------- #
def groove(seq, strong=120, back=112, on=96, ghost=74, beats_per_bar=4):
    """Stamp velocity from bar position: downbeat slam, beat-3 backbeat, ghosts."""
    out, pos = [], 0.0
    for p, d in seq:
        dur = parse_duration(d)
        if is_rest(p):
            out.append((p, d))          # rests just advance the cursor
            pos += dur
            continue
        m = pos % beats_per_bar
        if m < EPS or m > beats_per_bar - EPS:
            v = strong                  # bar downbeat -> crash/kick accent
        elif abs(m - 2.0) < EPS:
            v = back                    # beat 3 -> the half-time snare slam
        elif abs(pos - round(pos)) < EPS:
            v = on                      # other on-beats
        else:
            v = ghost                   # off-beat subdivisions (palm-mute ghosts)
        out.append((p, d, v))
        pos += dur
    return out


def flat(seq, v):
    """Stamp one constant velocity (drones, where dynamics should stay still)."""
    return [(p, d) if is_rest(p) else (p, d, v) for p, d in seq]


def rests(n_beats):
    """Exact silence of n_beats (integer) as quarter rests -- keeps lanes aligned."""
    return [("R", "4")] * int(round(n_beats))


def fill(pitch, n_beats, dur="1", v=None):
    """Tile n_beats with `dur`-length notes of `pitch` (drone/pedal builder)."""
    step = parse_duration(dur)
    n = int(round(n_beats / step))
    note = (pitch, dur) if v is None else (pitch, dur, v)
    return [note] * n


# =========================================================================== #
# RIFFS -- root lines in C Phrygian (+ blues b5), written in octave 2.
# Scale tones used:  C=1  Db=b2  Eb=b3  F=4  Gb=b5(blues)  G=5  Ab=b6  Bb=b7
# Tension = the b2 grind and the b5 tritone; the rest is pedal-root and stepwise
# Phrygian descent. None of these are transcribed from a card -- they are built
# from the cards' measured *grammar* (degree motion, octave, rhythm).
# =========================================================================== #

# Riff I "Procession" -- pedal root, a b2 neighbour, a leap to the b5 tritone,
# then a stepwise Phrygian fall home (4 -> b3 -> b2 -> 1). Two bars / 8 beats.
RIFF_I = [
    ("C2", "4"), ("C2", "8"), ("Db2", "8"), ("C2", "4"), ("Gb2", "4"),   # 1 1 b2 1 b5
    ("F2", "4"), ("Eb2", "4"), ("Db2", "4"), ("C2", "4"),                # 4 b3 b2 1
]

# Cadence variant -- same opening, land on a ringing whole-ish home (drop the b2).
RIFF_I_RING = [
    ("C2", "4"), ("C2", "8"), ("Db2", "8"), ("C2", "4"), ("Gb2", "4"),   # 1 1 b2 1 b5
    ("F2", "4"), ("Eb2", "4"), ("C2", "2"),                              # 4 b3 1(ring)
]

# Darker variant -- hang on the b5 tritone, leave a REST gap (Fu-Manchu breath),
# then the b2 and DON'T resolve (end on b2 -- tension is the aesthetic). 8 beats.
RIFF_I_DARK = [
    ("C2", "4"), ("C2", "8"), ("Db2", "8"), ("C2", "4"), ("Gb2", "4"),   # 1 1 b2 1 b5
    ("Gb2", "2"), ("R", "4"), ("Db2", "4"),                              # b5(hang) _ b2
]

# Riff II "Ascension" -- Monolord-style octave-jump call/response: state the figure
# low, then answer the SAME shape an octave up; the high answer ends on the b2 grind
# (Phrygian dread up top). Four bars / 16 beats. (Chord guitar makes the leap; bass
# stays anchored low via RIFF_II_LOW below.)
RIFF_II = [
    ("C2", "2"), ("Eb2", "2"),    # low : 1  b3
    ("C2", "2"), ("Gb2", "2"),    # low : 1  b5
    ("C3", "2"), ("Eb3", "2"),    # high: 1  b3   (octave-up answer)
    ("C3", "2"), ("Db3", "2"),    # high: 1  b2   (unresolved up top)
]
# Anchor line for bass/chug under Ascension -- the low half, repeated, no jump.
RIFF_II_LOW = [
    ("C2", "2"), ("Eb2", "2"), ("C2", "2"), ("Gb2", "2"),
    ("C2", "2"), ("Eb2", "2"), ("C2", "2"), ("Gb2", "2"),
]

# Psych-jam lead -- a single-note bluesy line over the drone: climb the blues scale,
# a Phrygian sigh home, hang on the b5, breathe. Eight bars / 32 beats. Lives in the
# LEAD lane (the chord guitarist takes a solo); high register so it floats over the
# low drone (chord tones spread across octaves -> no muddy clash).
JAM = [
    ("C3", "4"), ("Eb3", "4"), ("F3", "4"), ("Gb3", "4"),      # 1 b3 4 b5 (blues climb)
    ("G3", "2"), ("F3", "2"),                                  # 5 .. 4 (hold)
    ("Eb3", "4"), ("Db3", "4"), ("C3", "2"),                   # b3 b2 1 (Phrygian land)
    ("R", "2"), ("Gb3", "2"),                                  # breath .. b5 (hang)
    ("Gb3", "2"), ("F3", "4"), ("Eb3", "4"),                   # b5 4 b3
    ("Db3", "4"), ("C3", "4"), ("Bb2", "2"),                   # b2 1 b7 (turn)
    ("C3", "4"), ("Eb3", "4"), ("Gb3", "4"), ("Ab3", "4"),     # 1 b3 b5 b6 (climb)
    ("G3", "2"), ("C3", "2"),                                  # 5 .. 1 (land, leave open)
]

# Outro cadence -- b5 -> 4 -> b2 -> 1, then ring the home into "feedback". 16 beats.
OUTRO = [
    ("Gb2", "2"), ("F2", "2"), ("Db2", "2"), ("C2", "2"),      # b5 4 b2 1
    ("C2", "1"), ("C2", "1"),                                  # home, let it bloom
]


# =========================================================================== #
# ARRANGEMENT -- a 4-lane timeline. add() appends EQUAL-length material to every
# lane (inactive lanes get exact rests), so the four tracks stay sample-aligned
# no matter how the texture thins and thickens. Named section starts feed the
# tempo map.
# =========================================================================== #
LANES = ("lead", "chug", "bass", "organ")
timeline = {lane: [] for lane in LANES}
section_starts = {}     # name -> start beat (for the tempo map)
section_log = []        # (name, beats) for the printed breakdown


def add(name, n_beats, lead=None, chug=None, bass=None, organ=None):
    """Append one section; pad any silent lane with exact rests to keep alignment."""
    start = beats(timeline["lead"])
    section_starts.setdefault(name, start)
    parts = {"lead": lead, "chug": chug, "bass": bass, "organ": organ}
    for lane, seq in parts.items():
        if seq is None:
            timeline[lane] += rests(n_beats)
        else:
            got = beats(seq)
            assert abs(got - n_beats) < 1e-6, \
                f"{name}/{lane}: {got} beats, expected {n_beats}"
            timeline[lane] += seq
    section_log.append((name, n_beats))


def organ_drone(n_beats, v=56):
    """Quiet low root+5th drone (Hammond-ish bed) for the spacious sections."""
    return fill("C1+G1", n_beats, "1", v)


# 1) INTRO "Invocation" -- bass + organ drone open cold; the chord guitar enters
#    after two bars with sustained roots, a b2 sigh and a b5 tritone hint. 24 beats.
intro_lead = rests(8) + [
    ("C2", "1"), ("Db2", "2"), ("C2", "2"),       # root .. b2 -> 1
    ("Gb2", "2"), ("C2", "2"), ("C2", "1"),       # b5 hint -> home, ring
]
add("Invocation", 24,
    lead=groove(power_chord(intro_lead), strong=104, back=98, on=88, ghost=70),
    chug=None,
    bass=flat(fill("C1", 24, "1"), 92),
    organ=organ_drone(24))

# 2) PROCESSION -- the main riff, stated and CYCLED (riff worship): 5x + a ringing
#    cadence. Triplet gallop chug underneath. 48 beats.
proc_lead = RIFF_I * 5 + RIFF_I_RING
proc_chug = sum((gallop(RIFF_I, "T4") for _ in range(5)), []) + gallop(RIFF_I_RING, "T4")
proc_bass = bass_of(RIFF_I) * 5 + bass_of(RIFF_I_RING)
add("Procession", beats(proc_lead),
    lead=groove(power_chord(proc_lead)),
    chug=groove(proc_chug, strong=112, back=108, on=84, ghost=66),
    bass=groove(proc_bass, strong=112, back=106, on=98, ghost=82),
    organ=None)

# 3) ASCENSION -- the octave-lift call/response, x2. Bass + chug stay anchored low
#    (RIFF_II_LOW) while the chord guitar makes the leap. 32 beats.
asc_lead = RIFF_II * 2
asc_chug = gallop(RIFF_II_LOW, "T4") * 2
asc_bass = bass_of(RIFF_II_LOW) * 2
add("Ascension", beats(asc_lead),
    lead=groove(power_chord(asc_lead), strong=116, back=110, on=98, ghost=80),
    chug=groove(asc_chug, strong=110, back=106, on=82, ghost=64),
    bass=groove(asc_bass, strong=110, back=104, on=96, ghost=82),
    organ=None)

# 4) DARK PROCESSION -- main riff alternated with the b5/rest variation, x2. The
#    rest-gap lets the wall breathe mid-riff and the b2 ending refuses to resolve.
dark_unit = RIFF_I + RIFF_I_DARK
dark_lead = dark_unit * 2
dark_chug = (gallop(RIFF_I, "T4") + gallop(RIFF_I_DARK, "T4")) * 2
dark_bass = (bass_of(RIFF_I) + bass_of(RIFF_I_DARK)) * 2
add("Dark Procession", beats(dark_lead),
    lead=groove(power_chord(dark_lead)),
    chug=groove(dark_chug, strong=112, back=108, on=84, ghost=66),
    bass=groove(dark_bass, strong=112, back=106, on=98, ghost=82),
    organ=None)

# 5) THE HOLLOW -- subtraction breakdown: guitars drop OUT, bass + organ carry the
#    drone (negative space = doom's biggest weapon), and the chug creeps back in the
#    last bar. 16 beats.
hollow_chug = rests(12) + groove(gallop(fill("C2", 4, "4"), "8"),
                                 strong=104, on=80, ghost=66)
add("The Hollow", 16,
    lead=None,
    chug=hollow_chug,
    bass=flat(fill("C1", 16, "2"), 96),
    organ=organ_drone(16, v=60))

# 6) SPIRAL -- the psych jam: a reverb-friendly single-note lead over a pedal-root
#    drone (bass holds the C, organ beds it). 32 beats.
spiral_bass = flat(fill("C1", 24, "2") + fill("Gb0", 4, "2") + fill("C1", 4, "2"), 90)
add("Spiral", beats(JAM),
    lead=groove(JAM, strong=104, back=100, on=92, ghost=78),
    chug=None,
    bass=spiral_bass,
    organ=organ_drone(beats(JAM), v=54))

# 7) REPRISE -- the return: main riff comes back heavier, now with a DENSER 16th
#    chug (Dopethrone/Satanic-Rites territory) and a low organ swell. 5x. 40 beats.
rep_lead = RIFF_I * 5
rep_chug = sum((gallop(RIFF_I, "16") for _ in range(5)), [])
rep_bass = bass_of(RIFF_I) * 5
add("Reprise", beats(rep_lead),
    lead=groove(power_chord(rep_lead), strong=124, back=116, on=100, ghost=78),
    chug=groove(rep_chug, strong=116, back=110, on=86, ghost=64),
    bass=groove(rep_bass, strong=118, back=110, on=100, ghost=84),
    organ=organ_drone(beats(rep_lead), v=50))

# 8) COLLAPSE -- the "even slower" climax: main riff at HALF speed, the heaviest
#    moment, tempo sagging (see tempo map). Triplet chug crawls; organ swells. 3x.
climax_riff = halftime(RIFF_I)
col_lead = climax_riff * 3
col_chug = sum((gallop(climax_riff, "T4") for _ in range(3)), [])
col_bass = bass_of(climax_riff) * 3
add("Collapse", beats(col_lead),
    lead=groove(power_chord(col_lead), strong=126, back=120, on=104, ghost=84),
    chug=groove(col_chug, strong=118, back=112, on=88, ghost=66),
    bass=groove(col_bass, strong=122, back=114, on=102, ghost=86),
    organ=organ_drone(beats(col_lead), v=58))

# 9) ASHES -- the outro: a final b5 -> b2 -> 1 cadence rung into decaying whole
#    notes; guitars bow out, bass + organ let it ring into "feedback". 16 beats.
add("Ashes", beats(OUTRO),
    lead=groove(power_chord(OUTRO), strong=118, back=110, on=96, ghost=80),
    chug=None,
    bass=flat(bass_of(OUTRO), 96),
    organ=organ_drone(beats(OUTRO), v=54))


# =========================================================================== #
# PERCUSSION -- a real GM kit on channel 9 (the skill now supports a "drum-kit"
# track; see skills/generate_midi.py + midi_types/gm_percussion.py). The groove is
# the genre's HALF-TIME doom beat from the composition guide -- kick on 1 and the
# "&" of 2, the big backbeat SNARE on beat 3, sparse washing crash/ride/open-hat,
# tom fills into sections -- and it FOLLOWS the song's dynamics: a far-off intro,
# the groove under the riffs, a stripped kick+snare breakdown (subtraction), a
# ride-washed jam, a heavier return, and a slow crushing climax that decays into
# cymbal wash. Each bar is authored on a 16th-note grid (16 slots), exactly the
# notation the style cards print, so it lines up with the riffs by eye.
# --------------------------------------------------------------------------- #
DRUM_VEL = {                              # per-voice base velocity (max wins when stacked)
    "kick": 112, "snare": 120, "crash": 122, "crash2": 116, "splash": 110,
    "ride": 92, "ride-bell": 96, "hihat-open": 86, "hihat-closed": 74, "hihat": 78,
    "tom-high": 108, "tom-mid": 106, "tom-low": 104, "tom-floor": 104,
}


def drum_bar(voices, scale=1.0):
    """One 4/4 bar from a {drum: 16-char grid} dict -> 16 slot events of '16'.

    'X' = hit, '.' = empty. Stacked hits in a slot become a "+"-chord; an empty
    slot is a rest. Velocity is the loudest voice in the slot, scaled per section.
    """
    grids = {d: (g + "." * 16)[:16] for d, g in voices.items()}
    out = []
    for i in range(16):
        hits = [d for d, g in grids.items() if g[i] in "Xx"]
        if hits:
            v = max(1, min(127, int(round(max(DRUM_VEL.get(d, 90) for d in hits) * scale))))
            out.append(("+".join(hits), "16", v))
        else:
            out.append(("R", "16"))
    return out


def drum_section(bars, scale=1.0):
    return sum((drum_bar(b, scale) for b in bars), [])


# --- bar templates (16th grid: slots 0-3 = beat1, 4-7 = beat2, 8-11 = 3, 12-15 = 4)
G = {"kick": "X.....X.........", "snare": "........X.......",            # main half-time
     "hihat-open": "X...X...X...X..."}
Gc = {**G, "crash": "X..............."}                                  # + crash on phrase start
G2 = {"kick": "X.....XX..X.....", "snare": "........X.......",           # busier kick variant
      "hihat-open": "X...X...X...X..."}
FILL = {"kick": "X...............", "tom-high": "........X.......",       # tom roll into next phrase
        "tom-mid": "..........X.....", "tom-low": "............X...",
        "snare": ".............XXX", "hihat-open": "X...X..........."}

IB = {"kick": "X...............", "ride": "X.......X......."}             # sparse intro pulse
IB1 = {**IB, "crash": "X..............."}
IF = {"kick": "X...............", "tom-high": "....X.X.........",         # intro roll -> Procession
      "tom-mid": "........X.X.....", "tom-low": "............X.X.",
      "snare": "..............XX"}

HB = {"kick": "X...............", "snare": "........X......."}            # breakdown: kick+snare only
HBUILD = {"kick": "X.....X.........", "snare": "........X...X.X.",        # build out of the breakdown
          "tom-low": ".............XX."}

JB = {"kick": "X.....X.........", "snare": "........X.......",            # jam: ride wash on 8ths
      "ride": "X.X.X.X.X.X.X.X."}
JB1 = {**JB, "crash": "X..............."}

RB = {"kick": "X.....X...X.....", "snare": "........X.......",            # return: busiest, open-hat 8ths
      "hihat-open": "X.X.X.X.X.X.X.X."}
RB1 = {**RB, "crash": "X..............."}

ClA = {"crash": "X...............", "kick": "X.......X.......",           # climax: slow crush, 2-bar unit
       "snare": "........X.......", "ride": "X...X...X...X..."}
ClB = {"kick": "X.......X.......", "snare": "........X.......",
       "ride": "X...X...X...X...", "tom-low": ".............X.X"}

AB = {"crash": "X.......X.......", "kick": "X.......X.......",            # outro cadence hits
      "tom-low": "X.......X......."}
AD = {}                                                                  # cymbal-wash decay (silence)

# --- per-section drum plan (bar lists must total each section's bar count) and a
#     loudness scale per section (intro hushed, jam easy, return/climax pushed).
DRUM_PLAN = [
    ("Invocation",     [IB1, IB, IB, IB, IB, IF],                        0.70),
    ("Procession",     [Gc, G, G, FILL, Gc, G, G, FILL, Gc, G, G2, FILL], 1.00),
    ("Ascension",      [Gc, G, G, FILL, Gc, G, G2, FILL],                1.00),
    ("Dark Procession", [Gc, G, G, FILL, Gc, G, G2, FILL],               1.00),
    ("The Hollow",     [HB, HB, HB, HBUILD],                             0.92),
    ("Spiral",         [JB1, JB, JB, JB, JB1, JB, JB, FILL],             0.82),
    ("Reprise",        [RB1, RB, RB, FILL, RB1, RB, RB, FILL, RB1, FILL], 1.06),
    ("Collapse",       [ClA, ClB] * 6,                                   1.06),
    ("Ashes",          [AB, AB, AD, AD],                                 1.00),
]

_sec_beats = dict(section_log)
drum_timeline = []
for _name, _bars, _scale in DRUM_PLAN:
    _part = drum_section(_bars, _scale)
    assert abs(beats(_part) - _sec_beats[_name]) < 1e-6, \
        f"drums/{_name}: {beats(_part)} beats, expected {_sec_beats[_name]}"
    drum_timeline += _part
assert abs(beats(drum_timeline) - beats(timeline["lead"])) < 1e-6, "drum lane misaligned"


# --------------------------------------------------------------------------- #
# Tempo map -- ~70 BPM half-time with subtle human DRIFT at section seams (every
# analyzed track wanders a few BPM) and a big rit. into the climax (Dopethrone
# sags to 48). Tempos are pinned to the named section starts captured above.
# --------------------------------------------------------------------------- #
BASE_BPM = 70
_tempo_plan = [
    ("Invocation", 66),         # cold, dragging open
    ("Procession", 71),         # settle into the pocket, a touch of push
    ("Ascension", 70),
    ("Dark Procession", 68),    # lean back, heavier
    ("The Hollow", 64),         # breakdown breathes slower
    ("Spiral", 63),             # most spacious
    ("Reprise", 73),            # heaviest push before the drop
    ("Collapse", 52),           # the "even slower" climax -- the big rit.
    ("Ashes", 48),              # final decay
]
tempo_map = [{"beat": 0, "bpm": BASE_BPM}]
tempo_map += [{"beat": section_starts[name], "bpm": bpm} for name, bpm in _tempo_plan]


# --------------------------------------------------------------------------- #
# Build the Composition dict and hand it to the skill.
# --------------------------------------------------------------------------- #
def to_notes(seq):
    """(pitch, dur[, velocity]) tuples -> the skill's note dicts."""
    out = []
    for item in seq:
        note = {"pitch": item[0], "duration": item[1]}
        if len(item) > 2 and item[2] is not None:
            note["velocity"] = item[2]
        out.append(note)
    return out


composition = {
    "title": "Doom - The Hollow Procession",
    "bpm": BASE_BPM,
    "time_signature": "4/4",
    "tempo_map": tempo_map,
    "tracks": [
        # Lead / chord guitar: the ringing power-chord riffs + the jam lead.
        {"instrument": "distortion-guitar", "notes": to_notes(timeline["lead"])},
        # Chug guitar: palm-muted sub-octave gallop (different timbre + rhythm).
        {"instrument": "overdriven-guitar", "notes": to_notes(timeline["chug"])},
        # Bass: an octave below the chords, doubling the riff's motion for mass.
        {"instrument": "electric-bass-pick", "notes": to_notes(timeline["bass"])},
        # Organ: quiet root+5th drone, only in the spacious sections.
        {"instrument": "drawbar-organ", "notes": to_notes(timeline["organ"])},
        # Drums: a real GM kit on channel 9 -- the half-time doom groove.
        {"instrument": "drum-kit", "notes": to_notes(drum_timeline)},
    ],
}


if __name__ == "__main__":
    total = beats(timeline["lead"])
    # sanity: every lane (incl. the drum lane) must span the exact same beats
    for lane in LANES:
        assert abs(beats(timeline[lane]) - total) < 1e-6, f"{lane} misaligned"
    assert abs(beats(drum_timeline) - total) < 1e-6, "drums misaligned"

    print(f"Title : {composition['title']}")
    print(f"Key   : C Phrygian (+ blues b5)   Feel: half-time, {BASE_BPM} BPM base")
    print(f"Tracks: distortion gtr (chords) + overdriven gtr (chug) + bass + "
          f"drawbar organ + GM drum kit (ch.9)\n")

    print(f"{'Section':<18}{'bars':>6}{'beats':>8}{'start@beat':>12}{'bpm':>6}")
    print("-" * 50)
    plan = dict(_tempo_plan)
    for name, n in section_log:
        start = section_starts[name]
        print(f"{name:<18}{n / 4:>6.0f}{n:>8.0f}{start:>12.0f}{plan.get(name, ''):>6}")
    print("-" * 50)

    # approximate runtime across the tempo map
    seconds, prev_beat, prev_bpm = 0.0, 0.0, BASE_BPM
    for change in tempo_map[1:] + [{"beat": total, "bpm": tempo_map[-1]["bpm"]}]:
        seconds += (change["beat"] - prev_beat) * 60.0 / prev_bpm
        prev_beat, prev_bpm = change["beat"], change["bpm"]
    note_count = sum(len(t["notes"]) for t in composition["tracks"])
    print(f"Total : {total:.0f} beats / {total / 4:.0f} bars / "
          f"~{seconds:.0f}s ({int(seconds // 60)}:{int(seconds % 60):02d})")
    print(f"Events: {note_count} notes/chords across {len(composition['tracks'])} tracks\n")

    path = generate_midi_from_dict(composition)
    print(f"MIDI written: {path}")
    stem = Path(path).stem
    print(f"Render to WAV:  python render_wav.py 0.7 \"{stem}\"   "
          "(~-2 dBFS, non-clipping; the 5-voice mix + drum transients need the lower gain)")
