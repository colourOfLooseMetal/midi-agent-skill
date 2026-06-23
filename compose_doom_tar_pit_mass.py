#!/usr/bin/env python3
"""
Compose an ORIGINAL FUNERAL-SLUDGE doom track -- "The Tar Pit Mass" -- and render it
through the midi-generation skill.

This is the deliberate OPPOSITE pole from compose_doom_drowned_cathedral.py. That
driver was mid-tempo, melodic, B-Phrygian stoner-doom with a singing flute and an
anthemic chorus. This one is the FILTH end of the genre as measured in the Electric
Wizard - Dopethrone style card (resources/styles/doom/electric-wizard-dopethrone.md):
crushing, ultra-slow, ultra-down-tuned Bb minor-BLUES sludge -- a monolithic wall,
not a song with verses.

Like every driver here it does NO MIDI work itself: it prepares a Composition *dict*
(defining root lines once, realizing them into voices) and hands it to
skills.generate_midi.generate_midi_from_dict. All channel/program/file work is the
skill's.

What makes this a DIFFERENT doom style from the last one (every choice is a contrast):

  * Scale:  Bb minor BLUES (1 b3 4 b5 5 b7), NOT Phrygian. There is no b2 grind here;
            the whole identity is the b5 "money note" (E natural) -- Dopethrone's
            central colour -- a flatted-fifth tritone tremolo'd and ground against the
            root. (Drowned Cathedral's identity was the Phrygian b2.)
  * Tempo:  ~50 BPM crawling, sagging to 40 then 38 at the climax -- funeral pace.
            Dopethrone is logged at 55 BPM dropping to 48; this goes lower. (The last
            track sat at 68.)
  * Density: dense 16th-note SLUDGE churn -- Dopethrone's dominant duration was the
            16th, logged 1794 times. The main riff is a roiling 16th figure, not the
            eighth-triplet gallop the last track rode.
  * Wall:   THREE guitars locked to the SAME riff (rhythm power-chords + an overdriven
            "bass-effect" guitar doubling the root + bass an octave below), the
            Dopethrone three-amp wall -- everything moving together for mass, instead
            of the last track's chord-vs-gallop counterpoint.
  * Voice:  a low, wordless FUNERAL CHOIR (choir-aahs) chanting whole notes -- buried
            and ominous -- instead of a bright flute lead.
  * Bells:  tubular-bells TOLL the root at phrase heads -- a funeral knell. New colour.
  * Octave: roots at Bb1, the wall doubled down to Bb0 (Dopethrone bottoms at Bb0).
  * Form:   no verse/chorus. Toll -> riff worship -> drone mantra -> a second sludge
            riff -> a crushing breakdown -> a slow single-note crawl -> heavier riff
            return -> the "even slower" tar-pit climax (half speed, feedback wails) ->
            funeral decay. Long and oppressive, the way funeral doom is built.
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
    """MIDI number -> flat-spelled pitch name (genre prefers Bb/Db/E over A#/C#)."""
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
# doubling every note value (a 16th becomes an eighth, an eighth a quarter, ...).
_DOUBLE = {"32": "16", "16": "8", "8": "4", "4": "2", "2": "1", "1": "1",
           "d8": "d4", "d4": "d2", "d2": "1", "T8": "T4", "T4": "T8"}


def halftime(seq):
    """Return the riff at half speed (the doom 'even slower' move)."""
    return [(p, _DOUBLE.get(d, d)) for p, d in seq]


# --------------------------------------------------------------------------- #
# Voicing helpers. A power chord is ONE stacked-pitch event (root+5th+octave),
# never parallel tracks; tension is carried by where the roots move (and the b5
# tritone), not by stacking dissonance.
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


def octave(seq, shift=-12):
    """The root line moved by `shift` semitones (octave doubling for the wall)."""
    return transpose(seq, shift)


# --------------------------------------------------------------------------- #
# Dynamics -- per-note velocity by METRIC position. At funeral pace the wall still
# breathes: the downbeat lands hardest, beat 3 is the half-time snare, the 16th
# subdivisions sit back as churn. The cards note "the source has real accents".
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
    """Stamp one constant velocity (drones / chant / bells -- dynamics stay still)."""
    return [(p, d) if is_rest(p) else (p, d, v) for p, d in seq]


flat = voice


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
    """Pad a phrase out to exactly n_beats with trailing quarter rests."""
    got = beats(seq)
    assert got <= n_beats + EPS, f"phrase is {got} beats, exceeds section {n_beats}"
    rem = n_beats - got
    n = int(round(rem))
    assert abs(rem - n) < 1e-6, f"non-integer pad remainder {rem}"
    return list(seq) + [("R", "4")] * n


def toll(n_beats, pitch="Bb3", period=8, v=92):
    """A tubular-bell knell: a whole-note bell every `period` beats, rest between."""
    unit = [(pitch, "1", v)] + rests(period - 4)   # 4-beat bell + (period-4) rest
    out = []
    while beats(out) + period <= n_beats + EPS:
        out += unit
    return pad_to(out, n_beats)


# =========================================================================== #
# RIFFS -- root lines in Bb minor BLUES, written low (octave 1-2).
# Scale tones:  Bb=1  Db=b3  Eb=4  E=b5(blues money note)  F=5  Ab=b7
# There is NO b2 here (that was the last track's Phrygian colour). The identity is
# the b5 tritone (E) ground against the root, churned in 16ths -- Dopethrone's DNA.
# None of these are transcribed from a card -- built from its measured *grammar*.
# =========================================================================== #

# Riff "Dirge" -- the main sludge churn. Bar 1: pedal-root chug, the b5 grind, a
# blues run up to the tritone, resolve b3->4. Bar 2: a b7 lower-neighbour, a longer
# blues climb (b3 4 b5 5) and land home. Two bars / 8 beats, all 16th/8th churn.
RIFF_DIRGE = [
    # bar 1
    ("Bb1", "8"), ("Bb1", "16"), ("Bb1", "16"),               # 1 1 1
    ("Bb1", "8"), ("E2", "8"),                                # 1  b5 (the grind)
    ("Bb1", "16"), ("Db2", "16"), ("Eb2", "16"), ("E2", "16"),# 1 b3 4 b5 (run up)
    ("Eb2", "8"), ("Db2", "8"),                               # 4 b3 (resolve)
    # bar 2
    ("Bb1", "8"), ("Bb1", "16"), ("Bb1", "16"),               # 1 1 1
    ("Ab1", "8"), ("Bb1", "8"),                               # b7 1 (lower neighbour)
    ("Db2", "16"), ("Eb2", "16"), ("E2", "16"), ("F2", "16"), # b3 4 b5 5 (climb)
    ("F2", "8"), ("Bb1", "8"),                                # 5 1 (land home)
]

# Riff "Mire" -- heavier, the b5/5 tritone tremolo (E<->F) for two beats, then a
# slow blues descent. Two bars / 8 beats.
RIFF_MIRE = [
    # bar 1: 8x 16th tremolo on b5<->5, then descend
    ("E2", "16"), ("F2", "16"), ("E2", "16"), ("F2", "16"),
    ("E2", "16"), ("F2", "16"), ("E2", "16"), ("F2", "16"),
    ("Eb2", "8"), ("Db2", "8"), ("Bb1", "8"), ("Bb1", "8"),  # 4 b3 1 1
    # bar 2: tremolo again, then b7 1 b3 hold
    ("E2", "16"), ("F2", "16"), ("E2", "16"), ("F2", "16"),
    ("E2", "16"), ("F2", "16"), ("E2", "16"), ("F2", "16"),
    ("Ab1", "8"), ("Bb1", "8"), ("Db2", "4"),                # b7 1 b3
]

# Drone "Mantra" -- huge whole-note power chords, root moving 1 -> b3 -> 1 -> b5 so
# slowly it's a meditation. Four bars / 16 beats. (Cursing the One / Audhumbla
# whole-note drone worship, recoloured to minor-blues.)
DRONE = [
    ("Bb1", "1"), ("Db2", "1"), ("Bb1", "1"), ("E2", "1"),   # 1 b3 1 b5
]

# "Crawl" -- a slow single-note dirge LEAD over the drone, high register so it floats
# over the low wall. Blues phrasing, long notes. Eight bars / 32 beats.
CRAWL = [
    ("Bb3", "2"), ("Db4", "2"), ("Eb4", "2"), ("E4", "2"),   # 1 b3 4 b5 (climb)
    ("F4", "1"),                                             # 5 (hold)
    ("Eb4", "2"), ("Db4", "2"),                              # 4 b3
    ("Bb3", "1"),                                            # 1 (land)
    ("R", "2"), ("E4", "2"),                                 # breath .. b5 (hang)
    ("F4", "2"), ("Eb4", "2"),                               # 5 4
    ("Db4", "2"), ("Bb3", "2"),                              # b3 1 (leave open)
]

# Outro cadence -- b5 -> 4 -> b3 -> 1, rung into decaying whole notes. 16 beats.
OUTRO = [
    ("E2", "2"), ("Eb2", "2"), ("Db2", "2"), ("Bb1", "2"),   # b5 4 b3 1
    ("Bb1", "1"), ("Bb1", "1"),                              # home, bloom into feedback
]

# --------------------------------------------------------------------------- #
# FUNERAL CHOIR (choir-aahs) -- low, wordless, slow whole notes on chord tones; the
# "voice" of this track (buried and ominous, the antithesis of the last track's
# bright flute). Range Bb2-Db3. Used in the drone / breakdown / crawl / climax.
# --------------------------------------------------------------------------- #
CHANT = [
    ("Bb2", "1"), ("Ab2", "1"), ("Db3", "1"), ("Bb2", "1"),  # 1 b7 b3 1  (16 beats)
]

# Feedback wails (the lead guitar) -- high sustained b5/5 over the intro and climax,
# amp feedback howling on the tritone.
FEEDBACK_INTRO = rests(8) + [("F4", "1"), ("E4", "1")]       # enters halfway (16 beats)
FEEDBACK_TAR = [                                             # 48 beats of howl
    ("R", "1"), ("E4", "1"), ("F4", "1"), ("E4", "1"),
    ("Bb4", "1"), ("E4", "1"), ("F4", "1"), ("E4", "1"),
    ("E5", "1"), ("F4", "1"), ("E4", "1"), ("Bb4", "1"),
]


# =========================================================================== #
# ARRANGEMENT -- a 7-lane timeline. add() appends EQUAL-length material to every
# lane (silent lanes get exact rests), so the tracks stay sample-aligned no matter
# how the texture thins. The three-guitar WALL = rhythm (power chords) + sub
# (root line, overdriven, same octave) + bass (an octave below).
# =========================================================================== #
LANES = ("rhythm", "lead", "sub", "bass", "chant", "bells", "atmos")
timeline = {lane: [] for lane in LANES}
section_starts = {}
section_log = []


def add(name, n_beats, **parts):
    """Append one section; pad any silent lane with exact rests to keep alignment."""
    section_starts.setdefault(name, beats(timeline["rhythm"]))
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


def wall(root_line, rhythm_kw=None, sub_kw=None, bass_kw=None):
    """Realize a root line into the three locked guitar/bass voices + return them."""
    rhythm_kw = rhythm_kw or {}
    sub_kw = sub_kw or dict(strong=110, back=104, on=82, ghost=64)
    bass_kw = bass_kw or dict(strong=116, back=108, on=98, ghost=82)
    return (
        groove(power_chord(root_line), **rhythm_kw),         # chords at Bb1
        groove(root_line, **sub_kw),                         # overdriven root, same 8ve
        groove(octave(root_line, -12), **bass_kw),           # bass an octave below
    )


def atmos_drone(n_beats, v=44):
    """A quiet synth-FX wash (subterranean atmosphere) under the spacious sections."""
    return fill("Bb1", n_beats, "1", v)


# 1) TOLLING -- the knell: tubular bells toll over a bass drone and a subterranean
#    atmosphere, the lead guitar feeding back. No riff yet. 16 beats / 4 bars.
add("Tolling", 16,
    lead=voice(FEEDBACK_INTRO, 84),
    bass=flat(fill("Bb0", 16, "1"), 88),
    chant=voice(CHANT, 60),
    bells=toll(16, "Bb3", period=8, v=96),
    atmos=atmos_drone(16, v=50))

# 2) FIRST DIRGE -- the main sludge riff, churned and CYCLED (riff worship): x6. The
#    three-guitar wall locks together. 48 beats / 12 bars.
dirge6 = RIFF_DIRGE * 6
r, s, b = wall(dirge6)
add("First Dirge", beats(dirge6), rhythm=r, sub=s, bass=b)

# 3) BLACK MANTRA -- drone worship: whole-note power chords crawl 1->b3->1->b5 while
#    the funeral choir chants and a bell tolls each bar. 16 beats / 4 bars.
mantra = DRONE
mr, ms, mb = wall(mantra,
                  rhythm_kw=dict(strong=118, back=112, on=104, ghost=92),
                  sub_kw=dict(strong=104, back=100, on=92, ghost=84),
                  bass_kw=dict(strong=112, back=106, on=100, ghost=92))
add("Black Mantra", beats(mantra), rhythm=mr, sub=ms, bass=mb,
    chant=voice(CHANT, 78),
    bells=toll(beats(mantra), "Bb3", period=4, v=92))

# 4) THE MIRE -- the second, heavier riff: the b5/5 tritone tremolo ground against a
#    blues descent. x4. 32 beats / 8 bars.
mire4 = RIFF_MIRE * 4
xr, xs, xb = wall(mire4, rhythm_kw=dict(strong=122, back=114, on=100, ghost=78))
add("The Mire", beats(mire4), rhythm=xr, sub=xs, bass=xb,
    chant=voice(CHANT * 2, 64))

# 5) THE PIT -- the crushing breakdown: all guitars drop OUT, only the bass drone,
#    the choir and a slow bell toll hang in the void (negative space = doom's biggest
#    weapon); the sub-guitar churns back in for the last bar. 16 beats / 4 bars.
pit_sub = rests(12) + groove(fill("Bb1", 4, "16"), strong=104, on=80, ghost=64)
add("The Pit", 16,
    sub=pit_sub,
    bass=flat(fill("Bb0", 16, "2"), 94),
    chant=voice(CHANT, 84),
    bells=toll(16, "Bb3", period=8, v=98),
    atmos=atmos_drone(16, v=54))

# 6) CRAWL -- a slow single-note dirge lead over a pedal-root drone that dips to the
#    b5 tritone (E0); the choir beds it. 32 beats / 8 bars.
crawl_bass = flat(fill("Bb0", 24, "2") + fill("E0", 4, "2") + fill("Bb0", 4, "2"), 88)
add("Crawl", beats(CRAWL),
    lead=groove(CRAWL, strong=104, back=100, on=92, ghost=80),
    bass=crawl_bass,
    chant=voice(CHANT * 2, 72),
    bells=toll(beats(CRAWL), "Bb3", period=16, v=84),
    atmos=atmos_drone(beats(CRAWL), v=48))

# 7) SECOND DIRGE -- the main riff returns heavier, hammered harder. x6. 48 / 12 bars.
dirge6b = RIFF_DIRGE * 6
br, bs, bb = wall(dirge6b,
                  rhythm_kw=dict(strong=126, back=118, on=102, ghost=80),
                  sub_kw=dict(strong=114, back=108, on=86, ghost=66),
                  bass_kw=dict(strong=120, back=112, on=100, ghost=84))
add("Second Dirge", beats(dirge6b), rhythm=br, sub=bs, bass=bb)

# 8) THE TAR PIT -- the "even slower" climax: the main riff at HALF speed, the
#    heaviest, most crushing moment, tempo sagging to 40 (see tempo map). The lead
#    guitar howls feedback on the tritone; the choir swells; a deep bell tolls. x3.
#    48 beats / 12 bars.
tar = halftime(RIFF_DIRGE) * 3
tr, ts, tb = wall(tar,
                  rhythm_kw=dict(strong=127, back=122, on=108, ghost=88),
                  sub_kw=dict(strong=118, back=112, on=92, ghost=70),
                  bass_kw=dict(strong=124, back=116, on=104, ghost=88))
add("The Tar Pit", beats(tar), rhythm=tr, sub=ts, bass=tb,
    lead=voice(FEEDBACK_TAR, 96),
    chant=voice(CHANT * 3, 86),
    bells=toll(beats(tar), "Bb2", period=16, v=104),
    atmos=atmos_drone(beats(tar), v=56))

# 9) FUNERAL -- the outro: a final b5 -> b3 -> 1 cadence rung into decaying whole
#    notes; the wall bows out, bass + choir + atmosphere + one last toll let it ring
#    into feedback. 16 beats / 4 bars.
fr, fs, fb = wall(OUTRO, rhythm_kw=dict(strong=120, back=112, on=98, ghost=82))
add("Funeral", beats(OUTRO), rhythm=fr, sub=fs, bass=fb,
    chant=voice(CHANT, 80),
    bells=toll(beats(OUTRO), "Bb2", period=8, v=96),
    atmos=atmos_drone(beats(OUTRO), v=52))


# =========================================================================== #
# PERCUSSION -- a real GM kit on channel 9. The funeral-doom beat is SLOWER and more
# SPACIOUS than the last track: a huge kick on 1, the half-time snare on 3, washing
# crash/ride, sparse fills. It follows the dynamics -- a far-off toll, the groove
# under the dirges, a stripped kick+snare in the Pit, a ride-washed crawl, a heavier
# return, and a colossal slow crush in the Tar Pit decaying into cymbal wash. Each
# bar is on a 16th grid (16 slots), the notation the cards print, so it lines up.
# --------------------------------------------------------------------------- #
DRUM_VEL = {
    "kick": 114, "snare": 122, "crash": 124, "crash2": 118, "splash": 110,
    "ride": 92, "ride-bell": 96, "hihat-open": 84, "hihat-closed": 72, "hihat": 76,
    "tom-high": 108, "tom-mid": 106, "tom-low": 104, "tom-floor": 104,
}


def drum_bar(voices, scale=1.0):
    """One 4/4 bar from a {drum: 16-char grid} dict -> 16 slot events of '16'."""
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
FD = {"kick": "X.......X.......", "snare": "........X.......",            # funeral half-time
      "hihat-open": "X...X...X...X..."}
FDc = {**FD, "crash": "X..............."}                                 # + crash on phrase head
FD2 = {"kick": "X.....X.X.......", "snare": "........X.......",           # busier kick variant
       "hihat-open": "X...X...X...X..."}
FDF = {"kick": "X...............", "tom-high": "....X...........",        # slow tom fill
       "tom-mid": "........X.......", "tom-low": "............X...",
       "snare": ".............X.X", "crash": "...............X"}

TB = {"kick": "X...............", "ride": "X.......X......."}             # sparse toll-time pulse
TB1 = {**TB, "crash": "X..............."}

PB = {"kick": "X...............", "snare": "........X......."}            # the Pit: kick+snare only
PBUILD = {"kick": "X.......X.......", "snare": "........X...X.X.",        # build out of the Pit
          "tom-low": ".............XX."}

JB = {"kick": "X.......X.......", "snare": "........X.......",            # crawl: ride wash
      "ride": "X.X.X.X.X.X.X.X."}
JB1 = {**JB, "crash": "X..............."}

ClA = {"crash": "X...............", "kick": "X.......X.......",           # tar-pit crush, 2-bar unit
       "snare": "........X.......", "ride": "X...X...X...X..."}
ClB = {"kick": "X.......X.......", "snare": "........X.......",
       "ride": "X...X...X...X...", "tom-low": ".............X.X"}

AB = {"crash": "X.......X.......", "kick": "X.......X.......",            # outro cadence hits
      "tom-low": "X.......X......."}
AD = {}                                                                  # cymbal-wash decay

DRUM_PLAN = [
    ("Tolling",      [TB1, TB, TB, TB],                                  0.66),
    ("First Dirge",  [FDc, FD, FD, FDF, FDc, FD, FD2, FDF, FDc, FD, FD2, FDF], 1.00),
    ("Black Mantra", [FDc, FD, FD, FDF],                                 1.00),
    ("The Mire",     [FDc, FD, FD2, FDF, FDc, FD, FD2, FDF],             1.04),
    ("The Pit",      [PB, PB, PB, PBUILD],                               0.92),
    ("Crawl",        [JB1, JB, JB, JB, JB1, JB, JB, FDF],               0.82),
    ("Second Dirge", [FDc, FD, FD2, FDF, FDc, FD, FD2, FDF, FDc, FD, FD2, FDF], 1.08),
    ("The Tar Pit",  [ClA, ClB] * 6,                                     1.10),
    ("Funeral",      [AB, AB, AD, AD],                                   1.00),
]

_sec_beats = dict(section_log)
drum_timeline = []
for _name, _bars, _scale in DRUM_PLAN:
    _part = drum_section(_bars, _scale)
    assert abs(beats(_part) - _sec_beats[_name]) < 1e-6, \
        f"drums/{_name}: {beats(_part)} beats, expected {_sec_beats[_name]}"
    drum_timeline += _part
assert abs(beats(drum_timeline) - beats(timeline["rhythm"])) < 1e-6, "drum lane misaligned"


# --------------------------------------------------------------------------- #
# Tempo map -- ~50 BPM funeral crawl with human DRIFT at section seams and a big rit.
# into the climax (Dopethrone sags to 48; this goes lower, to 40 then 38). Pinned to
# the named section starts captured above.
# --------------------------------------------------------------------------- #
BASE_BPM = 50
_tempo_plan = [
    ("Tolling", 48),          # cold, dragging knell
    ("First Dirge", 52),      # settle into the crawl, a touch of push
    ("Black Mantra", 50),     # drone breathes
    ("The Mire", 51),
    ("The Pit", 46),          # breakdown drags slower
    ("Crawl", 44),            # most funereal
    ("Second Dirge", 54),     # the heaviest push
    ("The Tar Pit", 40),      # the "even slower" climax -- the big rit.
    ("Funeral", 38),          # final decay into silence
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
    "title": "Doom - The Tar Pit Mass",
    "bpm": BASE_BPM,
    "time_signature": "4/4",
    "tempo_map": tempo_map,
    "tracks": [
        # Rhythm guitar: the power-chord riffs (the chord wall, at Bb1).
        {"instrument": "distortion-guitar", "notes": to_notes(timeline["rhythm"])},
        # Lead guitar: feedback wails + the slow Crawl dirge solo.
        {"instrument": "distortion-guitar", "notes": to_notes(timeline["lead"])},
        # Sub guitar: an overdriven "bass-effect" voice doubling the riff root for filth.
        {"instrument": "overdriven-guitar", "notes": to_notes(timeline["sub"])},
        # Bass: an octave below the wall, the Bb0 floor.
        {"instrument": "electric-bass-finger", "notes": to_notes(timeline["bass"])},
        # Funeral choir: low wordless chant -- the "voice" of the mass.
        {"instrument": "choir-aahs", "notes": to_notes(timeline["chant"])},
        # Bells: a tubular-bell knell tolling the root at phrase heads.
        {"instrument": "tubular-bells", "notes": to_notes(timeline["bells"])},
        # Atmosphere: a subterranean synth-FX wash under the spacious sections.
        {"instrument": "fx-4-atmosphere", "notes": to_notes(timeline["atmos"])},
        # Drums: a real GM kit on channel 9 -- the slow funeral-doom groove.
        {"instrument": "drum-kit", "notes": to_notes(drum_timeline)},
    ],
}


if __name__ == "__main__":
    total = beats(timeline["rhythm"])
    for lane in LANES:
        assert abs(beats(timeline[lane]) - total) < 1e-6, f"{lane} misaligned"
    assert abs(beats(drum_timeline) - total) < 1e-6, "drums misaligned"

    print(f"Title : {composition['title']}")
    print(f"Key   : Bb minor blues (b5 = E)   Feel: funeral half-time, {BASE_BPM} BPM base")
    print("Tracks: distortion gtr (chords) + distortion gtr (lead/feedback)\n"
          "        + overdriven gtr (sub) + bass + choir (chant) + tubular bells"
          "\n        + fx atmosphere + GM drum kit (ch.9)\n")

    print(f"{'Section':<16}{'bars':>6}{'beats':>8}{'start@beat':>12}{'bpm':>6}")
    print("-" * 48)
    plan = dict(_tempo_plan)
    for name, n in section_log:
        start = section_starts[name]
        print(f"{name:<16}{n / 4:>6.0f}{n:>8.0f}{start:>12.0f}{plan.get(name, ''):>6}")
    print("-" * 48)

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
          "(~-2 dBFS, non-clipping; the dense 8-voice sludge needs the lower gain)")
