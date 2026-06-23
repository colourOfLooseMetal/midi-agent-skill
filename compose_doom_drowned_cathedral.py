#!/usr/bin/env python3
"""
Compose an ORIGINAL stoner/doom epic -- "The Drowned Cathedral" -- and render it
through the midi-generation skill.

This is the BIG, fully-arranged sibling of compose_doom_procession.py. Like every
driver in this repo it does NO MIDI work itself: it prepares a Composition *dict*
(defining root lines once and realizing them into voices) and hands it to
skills.generate_midi.generate_midi_from_dict. All channel/program/file work belongs
to the skill.

Where `compose_doom_procession.py` ran four lanes (chord gtr / chug gtr / bass /
organ + drums), this one is arranged like a full doom band PLUS atmosphere and a
"vocal", as the measured style cards in resources/styles/doom/*.md repeatedly show:

  * LEAD / CHORD guitar (distortion-guitar) -- ringing power-chord riffs + the solo.
  * CHUG guitar         (overdriven-guitar) -- palm-muted SUB-octave gallop, a
    different timbre AND rhythm (the only thing CLAUDE.md says justifies a parallel
    track). Triplet gallop, denser 16th chug on the returns.
  * BASS                (electric-bass-pick) -- an octave below, doubling the riff's
    motion for mass; pedals a drone in the spacious sections.
  * ORGAN               (drawbar-organ)      -- root+5th drone / swell, present in the
    intro, verses, choruses, breakdown, jam, climax & outro (Castle Rat - WIZARD and
    Monolord both layer a Hammond under the fuzz); silent under the densest riffs.
  * FLUTE               (flute)              -- THE VOCAL. The cards' vocal tracks are
    "Voice Oohs" wordless melodies; this skill has no real voice, so the sung line is
    voiced on a flute (CLAUDE.md's note: "voice the line on a clean lead tracking its
    scale degrees"). It sings in the verses/choruses and rests through the riff-worship
    and the breakdown, leaving the wall of fuzz its space -- exactly where the cards
    show vocals entering and dropping out.
  * ATMOSPHERE          (fx-4-atmosphere)    -- a quiet synth-FX wash under the
    spacious sections (intro / breakdown / jam / climax / outro) for psych colour.
  * RISER               (reverse-cymbal)     -- a swell that crescendos INTO the big
    downbeats (out of the intro, into the chorus, into the climax). Placed at section
    ENDS so its build resolves on the next section's first hit.
  * DRUMS               (drum-kit)           -- a real GM kit on channel 9: the genre's
    HALF-TIME doom groove, authored on a 16th grid, following the song's dynamics.

Everything below is SYNTHESIZED from the measured cards, not copied:

  * Key:    B Phrygian with a borrowed blues b5 (F natural). The cards cluster on
            Phrygian (Monolord, most Electric Wizard) and minor-blues (Dopethrone,
            Cursing the One); B is Monolord/Electric-Wizard's actual centre
            (Audhumbla, Empress Rising, Funeralopolis-adjacent). The blues b5 adds
            Dopethrone/Cursing-the-One's "money note" tritone.
            Degrees:  1=B  b2=C  b3=D  4=E  b5=F(blues)  5=Gb  b6=G  b7=A
  * Octave: chord-stack roots in octave 1-2 (guitar bottoms at B1, matching Monolord
            /Audhumbla's "lowest note B1"); chug + bass an octave below to B0 (the
            cards' down-tuned B0 bass floor).
  * Voicing: power chords as single stacked pitches (root+5th+octave). ALL tension is
            ROOT MOTION (1->b2 grind, 1->b5 tritone), never stacked semitone clusters
            -- matching the cards' "tritone ~0 / minor-2nd ~0 within chords, fifths
            everywhere" finding and SKILL.md's dissonance rule.
  * Rhythm: the recurring measured signatures -- the eighth-triplet GALLOP
            (Funeralopolis/Dagger Dragger logged 1000+ triplets), a denser 16th CHUG
            for the returns (Dopethrone), whole-note DRONE for the hypnotic sections
            (Cursing the One/Audhumbla), the Monolord octave-jump CALL/RESPONSE, and a
            Fu-Manchu-style REST inside a riff.
  * Vocal:  flute melody emphasising the cards' measured sung degrees (Castle Rat
            vocals leant on 5, 4, b3, 1, b5) up in octave 4-5, floating over the low
            wall so chord tones stay spread across octaves (no muddy clash).
  * Form:   intro drone -> riff worship -> verse(vox) -> octave-lift -> chorus(hook)
            -> subtraction breakdown -> psych jam(solo) -> dark variation ->
            heavier return -> restated chorus -> "even slower" climax -> decay.
  * Pacing: ~68 BPM half-time with human tempo DRIFT at section seams (every card's
            tempo wanders a few BPM) and a big rit. into the climax (Dopethrone sags
            to 48; this drops to 52 then 47).
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
# Voicing helpers -- turn a single-note ROOT LINE into the low voices. A power
# chord is ONE stacked-pitch event (root+5th+octave), never parallel tracks;
# tension is carried by where the roots move, not by stacking dissonance.
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

    Drives the CHUG gallop as a steady low pulse locked to the riff's harmony,
    independent of the chord guitar's exact rhythm. Rest beats stay rests.
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
    last = "B1"
    for i, r in enumerate(roots):
        if r is None:
            roots[i] = last
        else:
            last = roots[i]
    return roots


def gallop(root_line, sub="T4", octave_shift=-12):
    """Steady sub-octave chug: each beat filled with `sub`-note repeats of its root.

    `sub="T4"` -> 3 hits/beat (the eighth-triplet gallop the cards measure most);
    `sub="16"` -> 4 hits/beat (the denser Dopethrone chug). Rest beats emit silence.
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
# Dynamics -- per-note velocity by METRIC position (kick on 1, the half-time snare
# on 3), so the wall breathes instead of sitting at a flat 100. The style cards
# repeatedly note "the source has real accents MIDI velocity can mimic".
# --------------------------------------------------------------------------- #
def groove(seq, strong=120, back=112, on=96, ghost=74, beats_per_bar=4):
    """Stamp velocity from bar position: downbeat slam, beat-3 backbeat, ghosts."""
    out, pos = [], 0.0
    for p, d in seq:
        dur = parse_duration(d)
        if is_rest(p):
            out.append((p, d))
            pos += dur
            continue
        m = pos % beats_per_bar
        if m < EPS or m > beats_per_bar - EPS:
            v = strong
        elif abs(m - 2.0) < EPS:
            v = back
        elif abs(pos - round(pos)) < EPS:
            v = on
        else:
            v = ghost
        out.append((p, d, v))
        pos += dur
    return out


def voice(seq, v):
    """Stamp one constant velocity (drones / sung lines, where dynamics stay still)."""
    return [(p, d) if is_rest(p) else (p, d, v) for p, d in seq]


flat = voice  # alias: same operation, used for drones


def rests(n_beats):
    """Exact silence of n_beats (integer) as quarter rests -- keeps lanes aligned."""
    return [("R", "4")] * int(round(n_beats))


def fill(pitch, n_beats, dur="1", v=None):
    """Tile n_beats with `dur`-length notes of `pitch` (drone/pedal builder)."""
    step = parse_duration(dur)
    n = int(round(n_beats / step))
    note = (pitch, dur) if v is None else (pitch, dur, v)
    return [note] * n


def pad_to(seq, n_beats):
    """Pad a melodic phrase out to exactly n_beats with trailing quarter rests.

    Lets a sung/atmosphere phrase be authored shorter than its section and dropped
    into a lane without hand-counting the remaining silence (the riff lanes are
    bar-exact by construction; the vocal floats inside them).
    """
    got = beats(seq)
    assert got <= n_beats + EPS, f"phrase is {got} beats, exceeds section {n_beats}"
    rem = n_beats - got
    n = int(round(rem))
    assert abs(rem - n) < 1e-6, f"non-integer pad remainder {rem}"
    return list(seq) + [("R", "4")] * n


def riser(n_beats, swell="2", pitch="C5", v=122):
    """A reverse-cymbal swell that crescendos into the NEXT section's downbeat.

    Sits silent for the section then sounds for the final `swell` beats so the wash
    peaks on the following hit. (reverse-cymbal is a one-shot crescendo sample.)
    """
    swell_beats = parse_duration(swell)
    pre = int(round(n_beats - swell_beats))
    assert abs((n_beats - swell_beats) - pre) < 1e-6, "riser swell must land on a beat"
    return rests(pre) + [(pitch, swell, v)]


# =========================================================================== #
# RIFFS -- root lines in B Phrygian (+ blues b5), written low (octave 1-2).
# Scale tones:  B=1  C=b2  D=b3  E=4  F=b5(blues)  Gb=5  G=b6  A=b7
# Tension = the b2 grind (B->C) and the b5 tritone (B->F); the rest is pedal-root
# and stepwise Phrygian descent. None are transcribed from a card -- they are built
# from the cards' measured *grammar* (degree motion, octave, rhythm).
# =========================================================================== #

# Riff I "Tide" -- pedal root, a b2 neighbour, a leap to the b5 tritone, then a
# stepwise Phrygian fall home (4 -> b3 -> b2 -> 1). Two bars / 8 beats.
RIFF_I = [
    ("B1", "4"), ("B1", "8"), ("C2", "8"), ("B1", "4"), ("F2", "4"),   # 1 1 b2 1 b5
    ("E2", "4"), ("D2", "4"), ("C2", "4"), ("B1", "4"),                # 4 b3 b2 1
]

# Cadence variant -- same opening, ring the home (drop the closing b2). 8 beats.
RIFF_I_RING = [
    ("B1", "4"), ("B1", "8"), ("C2", "8"), ("B1", "4"), ("F2", "4"),   # 1 1 b2 1 b5
    ("E2", "4"), ("D2", "4"), ("B1", "2"),                             # 4 b3 1(ring)
]

# Darker variant -- hang on the b5 tritone, leave a REST gap (Fu-Manchu breath),
# then the b2 and DON'T resolve (end on b2 -- tension is the aesthetic). 8 beats.
RIFF_DARK = [
    ("B1", "4"), ("B1", "8"), ("C2", "8"), ("B1", "4"), ("F2", "4"),   # 1 1 b2 1 b5
    ("F2", "2"), ("R", "4"), ("C2", "4"),                             # b5(hang) _ b2
]

# Riff II "Ascension" -- Monolord-style octave-jump call/response: state the figure
# low, then answer the SAME shape an octave up; the high answer ends on the b2 grind
# (Phrygian dread up top). Four bars / 16 beats. The chord guitar makes the leap;
# bass + chug stay anchored low via ASC_LOW.
RIFF_ASC = [
    ("B1", "2"), ("D2", "2"),     # low : 1  b3
    ("B1", "2"), ("F2", "2"),     # low : 1  b5
    ("B2", "2"), ("D3", "2"),     # high: 1  b3   (octave-up answer)
    ("B2", "2"), ("C3", "2"),     # high: 1  b2   (unresolved up top)
]
ASC_LOW = [
    ("B1", "2"), ("D2", "2"), ("B1", "2"), ("F2", "2"),
    ("B1", "2"), ("D2", "2"), ("B1", "2"), ("F2", "2"),
]

# Chorus "Spire" -- the anthemic hook: a b6 -> b7 lift up to the octave, settle on
# the b7 (the cards' choruses lean on 4/5/b6/b7 motion; Fresh Fur ends on b6->b7).
# Two bars / 8 beats.
CHORUS = [
    ("E2", "4"), ("Gb2", "4"), ("G2", "4"), ("A2", "4"),   # 4 5 b6 b7
    ("B2", "2"), ("A2", "2"),                              # 1(oct) b7 (the lift)
]

# Psych-jam solo -- a single-note bluesy lead over the drone: climb the blues scale,
# a Phrygian sigh home, hang on the b5, breathe. Eight bars / 32 beats. High register
# so it floats over the low drone (chord tones spread across octaves -> no clash).
JAM = [
    ("B3", "4"), ("D4", "4"), ("E4", "4"), ("F4", "4"),    # 1 b3 4 b5 (blues climb)
    ("Gb4", "2"), ("E4", "2"),                             # 5 .. 4 (hold)
    ("D4", "4"), ("C4", "4"), ("B3", "2"),                 # b3 b2 1 (Phrygian land)
    ("R", "2"), ("F4", "2"),                               # breath .. b5 (hang)
    ("F4", "2"), ("E4", "4"), ("D4", "4"),                 # b5 4 b3
    ("C4", "4"), ("B3", "4"), ("A3", "2"),                 # b2 1 b7 (turn)
    ("B3", "4"), ("D4", "4"), ("F4", "4"), ("G4", "4"),    # 1 b3 b5 b6 (climb)
    ("Gb4", "2"), ("B3", "2"),                             # 5 .. 1 (land, leave open)
]

# Outro cadence -- b5 -> 4 -> b2 -> 1, then ring the home into "feedback". 16 beats.
OUTRO = [
    ("F2", "2"), ("E2", "2"), ("C2", "2"), ("B1", "2"),    # b5 4 b2 1
    ("B1", "1"), ("B1", "1"),                              # home, let it bloom
]

# --------------------------------------------------------------------------- #
# VOCAL (flute) phrases -- single-note melodies up in octave 3-5, emphasising the
# cards' measured sung degrees (Castle Rat vocals: 5, 4, b3, 1, b5). Authored a
# little short and pad_to'd into each section so the sung line floats inside the
# bar-exact riff. In B:  1=B  b2=C  b3=D  4=E  b5=F  5=Gb  b6=G  b7=A.
# --------------------------------------------------------------------------- #
VERSE_VOX = [                                    # 16 beats; sung over RIFF_I
    ("R", "2"),                                  # let the riff start
    ("Gb4", "4"), ("Gb4", "4"), ("E4", "2"),     # 5 5 4
    ("D4", "4"), ("E4", "4"), ("B3", "2"),       # b3 4 1
    ("R", "4"),                                  # breath
    ("D4", "4"), ("E4", "4"), ("F4", "2"),       # b3 4 b5 (rise to the money note)
    ("E4", "4"),                                 # 4 (settle)
]

CHORUS_VOX = [                                   # 8 beats; the hook
    ("Gb4", "4"), ("A4", "4"),                   # 5 b7
    ("B4", "2"),                                 # 1 (peak)
    ("A4", "2"),                                 # b7
    ("Gb4", "4"), ("E4", "4"),                   # 5 4
]

LAMENT_VOX = [                                   # 16 beats; lone flute in the void
    ("R", "2"), ("B3", "2"),                     # 1
    ("D4", "2"), ("C4", "2"),                    # b3 b2
    ("R", "2"), ("F4", "2"),                     # b5 (money note in the silence)
    ("E4", "2"), ("B3", "2"),                    # 4 1
]

SPIRAL_VOX = [                                   # 16 beats; airy counter-line in the jam
    ("B4", "2"), ("A4", "2"),                    # 1 b7
    ("Gb4", "4"), ("F4", "4"),                   # 5 b5
    ("E4", "2"), ("R", "2"),                     # 4 ..
    ("D4", "2"), ("F4", "2"),                    # b3 b5
    ("Gb4", "2"),                                # 5 (hang)
]

DARK_VOX = [                                     # 16 beats; lower, menacing
    ("R", "4"), ("B3", "2"),                     # 1
    ("C4", "2"), ("B3", "4"),                    # b2 1
    ("R", "2"), ("F4", "2"),                     # b5
    ("D4", "4"), ("C4", "4"), ("B3", "2"),       # b3 b2 1
    ("R", "2"),                                  # breath
]

COLLAPSE_VOX = [                                 # 24 beats; high wail over the crush
    ("R", "1"),                                  # let the slow riff land
    ("F5", "1"),                                 # b5 wail (whole note)
    ("Gb5", "2"), ("F5", "2"),                   # 5 b5
    ("E5", "1"),                                 # 4
    ("D5", "2"), ("F5", "2"),                    # b3 b5
    ("B4", "1"),                                 # 1
]

ASHES_VOX = [                                    # 16 beats; final Phrygian descent
    ("R", "2"), ("B4", "2"),                     # 1
    ("A4", "2"), ("F4", "2"),                    # b7 b5
    ("E4", "2"), ("D4", "2"),                    # 4 b3
    ("C4", "2"), ("B3", "2"),                    # b2 1 (land, fade)
]


# =========================================================================== #
# ARRANGEMENT -- a 7-lane timeline. add() appends EQUAL-length material to every
# lane (inactive lanes get exact rests), so the tracks stay sample-aligned no
# matter how the texture thins and thickens. Named section starts feed the tempo
# map. The drum kit is built separately below and checked against these lengths.
# =========================================================================== #
LANES = ("lead", "chug", "bass", "organ", "flute", "atmos", "riser")
timeline = {lane: [] for lane in LANES}
section_starts = {}     # name -> start beat (for the tempo map)
section_log = []        # (name, beats) for the printed breakdown


def add(name, n_beats, **parts):
    """Append one section; pad any silent lane with exact rests to keep alignment."""
    start = beats(timeline["lead"])
    section_starts.setdefault(name, start)
    for lane in LANES:
        seq = parts.get(lane)
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
    return fill("B0+Gb1", n_beats, "1", v)


def atmos_drone(n_beats, v=46):
    """Quiet synth-FX wash (psych atmosphere) under the spacious sections."""
    return fill("B1", n_beats, "1", v)


# 1) INVOCATION -- bass + organ drone open cold under an atmosphere wash; the chord
#    guitar enters after two bars with sustained roots, a b2 sigh and a b5 hint. A
#    reverse-cymbal swells out of the last bar into the Procession. 24 beats.
intro_lead = rests(8) + [
    ("B1", "1"), ("C2", "2"), ("B1", "2"),        # root .. b2 -> 1
    ("F2", "2"), ("B1", "2"), ("B1", "1"),        # b5 hint -> home, ring
]
add("Invocation", 24,
    lead=groove(power_chord(intro_lead), strong=104, back=98, on=88, ghost=70),
    bass=flat(fill("B0", 24, "1"), 92),
    organ=organ_drone(24),
    atmos=atmos_drone(24, v=50),
    riser=riser(24, swell="2", v=118))

# 2) PROCESSION -- the main riff, stated and CYCLED (riff worship): 5x + a ringing
#    cadence. Triplet gallop chug underneath. Instrumental -- no vocal yet. 48 beats.
proc_lead = RIFF_I * 5 + RIFF_I_RING
proc_chug = sum((gallop(RIFF_I, "T4") for _ in range(5)), []) + gallop(RIFF_I_RING, "T4")
proc_bass = bass_of(RIFF_I) * 5 + bass_of(RIFF_I_RING)
add("Procession", beats(proc_lead),
    lead=groove(power_chord(proc_lead)),
    chug=groove(proc_chug, strong=112, back=108, on=84, ghost=66),
    bass=groove(proc_bass, strong=112, back=106, on=98, ghost=82))

# 3) VERSE -- the riff continues but the FLUTE "vocal" enters, organ lightly under.
#    Main riff x4, flute sings VERSE_VOX x2. 32 beats.
verse_lead = RIFF_I * 4
verse_chug = sum((gallop(RIFF_I, "T4") for _ in range(4)), [])
verse_bass = bass_of(RIFF_I) * 4
add("Verse", beats(verse_lead),
    lead=groove(power_chord(verse_lead), strong=112, back=106, on=92, ghost=70),
    chug=groove(verse_chug, strong=104, back=100, on=80, ghost=62),
    bass=groove(verse_bass, strong=110, back=104, on=96, ghost=80),
    organ=organ_drone(beats(verse_lead), v=48),
    flute=voice(VERSE_VOX * 2, 100))

# 4) ASCENSION -- the octave-lift call/response, x2. Bass + chug stay anchored low
#    (ASC_LOW) while the chord guitar makes the leap. Instrumental lift -- a
#    reverse-cymbal swells out of it into the Chorus. 32 beats.
asc_lead = RIFF_ASC * 2
asc_chug = gallop(ASC_LOW, "T4") * 2
asc_bass = bass_of(ASC_LOW) * 2
add("Ascension", beats(asc_lead),
    lead=groove(power_chord(asc_lead), strong=116, back=110, on=98, ghost=80),
    chug=groove(asc_chug, strong=110, back=106, on=82, ghost=64),
    bass=groove(asc_bass, strong=110, back=104, on=96, ghost=82),
    riser=riser(beats(asc_lead), swell="2", v=122))

# 5) CHORUS -- the big hook: full band, the flute sings CHORUS_VOX, organ swells,
#    drums open up. Chorus riff x4, vocal x4. 32 beats.
chorus_lead = CHORUS * 4
chorus_chug = sum((gallop(CHORUS, "T4") for _ in range(4)), [])
chorus_bass = bass_of(CHORUS) * 4
add("Chorus", beats(chorus_lead),
    lead=groove(power_chord(chorus_lead), strong=122, back=116, on=102, ghost=82),
    chug=groove(chorus_chug, strong=114, back=110, on=86, ghost=66),
    bass=groove(chorus_bass, strong=118, back=110, on=100, ghost=84),
    organ=organ_drone(beats(chorus_lead), v=62),
    flute=voice(CHORUS_VOX * 4, 112))

# 6) THE HOLLOW -- subtraction breakdown: guitars drop OUT, bass + organ + atmosphere
#    carry the drone (negative space = doom's biggest weapon), a lone flute LAMENT
#    sings in the void, and the chug creeps back in the last bar. 16 beats.
hollow_chug = rests(12) + groove(gallop(fill("B1", 4, "4"), "8"),
                                 strong=104, on=80, ghost=66)
add("The Hollow", 16,
    chug=hollow_chug,
    bass=flat(fill("B0", 16, "2"), 96),
    organ=organ_drone(16, v=60),
    flute=voice(LAMENT_VOX, 96),
    atmos=atmos_drone(16, v=52))

# 7) SPIRAL -- the psych jam: a reverb-friendly single-note lead SOLO over a
#    pedal-root drone (bass holds B, organ + atmosphere bed it), the flute weaving an
#    airy counter-line above. 32 beats.
spiral_bass = flat(fill("B0", 24, "2") + fill("F0", 4, "2") + fill("B0", 4, "2"), 90)
add("Spiral", beats(JAM),
    lead=groove(JAM, strong=104, back=100, on=92, ghost=78),
    bass=spiral_bass,
    organ=organ_drone(beats(JAM), v=54),
    flute=voice(SPIRAL_VOX * 2, 92),
    atmos=atmos_drone(beats(JAM), v=48))

# 8) DARK PROCESSION -- main riff alternated with the b5/rest variation, x2. The
#    rest-gap lets the wall breathe mid-riff; the flute returns lower and menacing.
#    A reverse-cymbal swells out into the Reprise. 32 beats.
dark_unit = RIFF_I + RIFF_DARK
dark_lead = dark_unit * 2
dark_chug = (gallop(RIFF_I, "T4") + gallop(RIFF_DARK, "T4")) * 2
dark_bass = (bass_of(RIFF_I) + bass_of(RIFF_DARK)) * 2
add("Dark Procession", beats(dark_lead),
    lead=groove(power_chord(dark_lead)),
    chug=groove(dark_chug, strong=112, back=108, on=84, ghost=66),
    bass=groove(dark_bass, strong=112, back=106, on=98, ghost=82),
    flute=voice(DARK_VOX * 2, 96),
    riser=riser(beats(dark_lead), swell="2", v=120))

# 9) REPRISE -- the return: main riff heavier, now with a DENSER 16th chug
#    (Dopethrone territory), a low organ swell and the chorus hook in the flute. 5x.
#    40 beats.
rep_lead = RIFF_I * 5
rep_chug = sum((gallop(RIFF_I, "16") for _ in range(5)), [])
rep_bass = bass_of(RIFF_I) * 5
add("Reprise", beats(rep_lead),
    lead=groove(power_chord(rep_lead), strong=124, back=116, on=100, ghost=78),
    chug=groove(rep_chug, strong=116, back=110, on=86, ghost=64),
    bass=groove(rep_bass, strong=118, back=110, on=100, ghost=84),
    organ=organ_drone(beats(rep_lead), v=52),
    flute=voice(CHORUS_VOX * 5, 110))

# 10) CHORUS II -- the hook restated, biggest yet, then a reverse-cymbal swells into
#     the climax. Chorus riff x2, vocal x2. 16 beats.
chorus2_lead = CHORUS * 2
chorus2_chug = sum((gallop(CHORUS, "16") for _ in range(2)), [])
chorus2_bass = bass_of(CHORUS) * 2
add("Chorus II", beats(chorus2_lead),
    lead=groove(power_chord(chorus2_lead), strong=126, back=118, on=104, ghost=84),
    chug=groove(chorus2_chug, strong=116, back=112, on=88, ghost=66),
    bass=groove(chorus2_bass, strong=120, back=112, on=102, ghost=86),
    organ=organ_drone(beats(chorus2_lead), v=64),
    flute=voice(CHORUS_VOX * 2, 116),
    riser=riser(beats(chorus2_lead), swell="2", v=124))

# 11) COLLAPSE -- the "even slower" climax: main riff at HALF speed, the heaviest
#     moment, tempo sagging (see tempo map). Triplet chug crawls; organ + atmosphere
#     swell; the flute WAILS the b5 money note up top. 3x. 48 beats.
climax_riff = halftime(RIFF_I)
col_lead = climax_riff * 3
col_chug = sum((gallop(climax_riff, "T4") for _ in range(3)), [])
col_bass = bass_of(climax_riff) * 3
add("Collapse", beats(col_lead),
    lead=groove(power_chord(col_lead), strong=126, back=120, on=104, ghost=84),
    chug=groove(col_chug, strong=118, back=112, on=88, ghost=66),
    bass=groove(col_bass, strong=122, back=114, on=102, ghost=86),
    organ=organ_drone(beats(col_lead), v=60),
    flute=voice(COLLAPSE_VOX * 2, 114),
    atmos=atmos_drone(beats(col_lead), v=54))

# 12) ASHES -- the outro: a final b5 -> b2 -> 1 cadence rung into decaying whole
#     notes; guitars bow out, bass + organ + atmosphere let it ring into "feedback",
#     the flute traces one last Phrygian descent. 16 beats.
add("Ashes", beats(OUTRO),
    lead=groove(power_chord(OUTRO), strong=118, back=110, on=96, ghost=80),
    bass=flat(bass_of(OUTRO), 96),
    organ=organ_drone(beats(OUTRO), v=54),
    flute=voice(ASHES_VOX, 100),
    atmos=atmos_drone(beats(OUTRO), v=50))


# =========================================================================== #
# PERCUSSION -- a real GM kit on channel 9 (the skill's "drum-kit" track type; see
# skills/generate_midi.py + midi_types/gm_percussion.py). The groove is the genre's
# HALF-TIME doom beat -- kick on 1 and the "&" of 2, the big backbeat SNARE on beat
# 3, washing crash/ride/open-hat, tom fills into sections -- and it FOLLOWS the
# song's dynamics: a far-off intro, the groove under the riffs, anthemic open-hat
# choruses, a stripped kick+snare breakdown, a ride-washed jam, a heavier return,
# and a slow crushing climax that decays into cymbal wash. Each bar is on a 16th
# grid (16 slots), the same notation the style cards print, so it lines up by eye.
# --------------------------------------------------------------------------- #
DRUM_VEL = {
    "kick": 112, "snare": 120, "crash": 122, "crash2": 116, "splash": 110,
    "ride": 92, "ride-bell": 96, "hihat-open": 86, "hihat-closed": 74, "hihat": 78,
    "tom-high": 108, "tom-mid": 106, "tom-low": 104, "tom-floor": 104,
}


def drum_bar(voices, scale=1.0):
    """One 4/4 bar from a {drum: 16-char grid} dict -> 16 slot events of '16'.

    'X' = hit, '.' = empty. Stacked hits in a slot become a "+"-chord; an empty slot
    is a rest. Velocity is the loudest voice in the slot, scaled per section.
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

CB = {"kick": "X.....X...X.....", "snare": "........X.......",            # chorus: open-hat 8ths
      "hihat-open": "X.X.X.X.X.X.X.X.", "crash": "X..............."}
CB2 = {"kick": "X.....X...X.....", "snare": "........X.......",
       "hihat-open": "X.X.X.X.X.X.X.X."}

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

# --- per-section drum plan (bar lists total each section's bar count) + a loudness
#     scale per section (intro hushed, jam easy, chorus/return/climax pushed).
DRUM_PLAN = [
    ("Invocation",      [IB1, IB, IB, IB, IB, IF],                         0.70),
    ("Procession",      [Gc, G, G, FILL, Gc, G, G, FILL, Gc, G, G2, FILL], 1.00),
    ("Verse",           [Gc, G, G, FILL, Gc, G, G2, FILL],                 0.94),
    ("Ascension",       [Gc, G, G, FILL, Gc, G, G2, FILL],                 1.00),
    ("Chorus",          [CB, CB2, CB2, FILL, CB, CB2, CB2, FILL],          1.06),
    ("The Hollow",      [HB, HB, HB, HBUILD],                              0.92),
    ("Spiral",          [JB1, JB, JB, JB, JB1, JB, JB, FILL],              0.82),
    ("Dark Procession", [Gc, G, G, FILL, Gc, G, G2, FILL],                 1.00),
    ("Reprise",         [RB1, RB, RB, FILL, RB1, RB, RB, FILL, RB1, FILL], 1.08),
    ("Chorus II",       [CB, CB2, CB2, FILL],                              1.10),
    ("Collapse",        [ClA, ClB] * 6,                                    1.08),
    ("Ashes",           [AB, AB, AD, AD],                                  1.00),
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
# Tempo map -- ~68 BPM half-time with subtle human DRIFT at section seams (every
# analyzed track wanders a few BPM) and a big rit. into the climax (Dopethrone sags
# to 48). Tempos are pinned to the named section starts captured above.
# --------------------------------------------------------------------------- #
BASE_BPM = 68
_tempo_plan = [
    ("Invocation", 64),         # cold, dragging open
    ("Procession", 70),         # settle into the pocket, a touch of push
    ("Verse", 71),
    ("Ascension", 70),
    ("Chorus", 72),             # the hook lifts
    ("The Hollow", 65),         # breakdown breathes slower
    ("Spiral", 63),             # most spacious
    ("Dark Procession", 68),    # lean back, heavier
    ("Reprise", 74),            # heaviest push
    ("Chorus II", 75),          # peak before the drop
    ("Collapse", 52),           # the "even slower" climax -- the big rit.
    ("Ashes", 47),              # final decay
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
    "title": "Doom - The Drowned Cathedral",
    "bpm": BASE_BPM,
    "time_signature": "4/4",
    "tempo_map": tempo_map,
    "tracks": [
        # Lead / chord guitar: the ringing power-chord riffs + the jam solo.
        {"instrument": "distortion-guitar", "notes": to_notes(timeline["lead"])},
        # Chug guitar: palm-muted sub-octave gallop (different timbre + rhythm).
        {"instrument": "overdriven-guitar", "notes": to_notes(timeline["chug"])},
        # Bass: an octave below the chords, doubling the riff's motion for mass.
        {"instrument": "electric-bass-pick", "notes": to_notes(timeline["bass"])},
        # Organ: quiet root+5th drone/swell, only in the spacious & anthemic sections.
        {"instrument": "drawbar-organ", "notes": to_notes(timeline["organ"])},
        # Flute: THE VOCAL -- the sung melody, voiced on a flute (verses/choruses).
        {"instrument": "flute", "notes": to_notes(timeline["flute"])},
        # Atmosphere: a quiet synth-FX wash for psych colour in the spacious sections.
        {"instrument": "fx-4-atmosphere", "notes": to_notes(timeline["atmos"])},
        # Riser: reverse-cymbal swells that crescendo into the big downbeats.
        {"instrument": "reverse-cymbal", "notes": to_notes(timeline["riser"])},
        # Drums: a real GM kit on channel 9 -- the half-time doom groove.
        {"instrument": "drum-kit", "notes": to_notes(drum_timeline)},
    ],
}


if __name__ == "__main__":
    total = beats(timeline["lead"])
    for lane in LANES:
        assert abs(beats(timeline[lane]) - total) < 1e-6, f"{lane} misaligned"
    assert abs(beats(drum_timeline) - total) < 1e-6, "drums misaligned"

    print(f"Title : {composition['title']}")
    print(f"Key   : B Phrygian (+ blues b5)   Feel: half-time, {BASE_BPM} BPM base")
    print("Tracks: distortion gtr (chords) + overdriven gtr (chug) + bass + "
          "drawbar organ\n        + flute (vocal) + fx atmosphere + reverse-cymbal "
          "riser + GM drum kit (ch.9)\n")

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
          "(~-2 dBFS, non-clipping; the 8-voice mix + drum transients need the lower gain)")
