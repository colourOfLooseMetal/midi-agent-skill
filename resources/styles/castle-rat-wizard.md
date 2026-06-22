# Style Card — Castle Rat – WIZARD

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 73 BPM (half-time feel) |
| Tempo changes | 53 BPM @ beat 7.0, 68 BPM @ beat 7.0, 77 BPM @ beat 9.0, 154 BPM @ beat 37.0, 77 BPM @ beat 61.0, 154 BPM @ beat 98.0 |
| Key / scale | C Phrygian  (confidence 90%) |
| Main time signature | 4/4 |
| Other meters | 2/4, 7/8 |
| Lowest note | C1 |
| Lowest open string | None |
| Notes per bar | 24.32 |
| Voicing | power-chord driven |
| Structure | 117 bars, 49 unique (repetition 58%; top bar repeats 19x) |

## Harmony

- **Key / scale:** C Phrygian (confidence 90%).
- **Most-used pitch classes:** 5 (G), 1 (C), b7 (Bb), b6 (Ab), 4 (F), b3 (Eb).
- **Voicing:** power-chord driven — 215 power-chord hits vs 0 triads
  across 2326 single notes.
- **Interval color (within chords):** tritone ×3, minor-2nd
  ×1, fifth ×532.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to C Phrygian. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 19x (4/4)

```python
[
    {"pitch": "C2", "duration": "4"},
    {"pitch": "C2", "duration": "4"},
    {"pitch": "Bb1", "duration": "8"},
    {"pitch": "G1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "G1", "duration": "16"},
    {"pitch": "Bb1", "duration": "8"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> b7 -> 5 -> b7 -> b7 -> 5 -> b7
- **Onset grid (16th notes):** `X...X...X.XXXXX.`

### Riff B — repeats 8x (4/4)

```python
[
    {"pitch": "G1", "duration": "T8"},
    {"pitch": "G1", "duration": "T8"},
    {"pitch": "G1", "duration": "T8"},
    {"pitch": "G2", "duration": "T8"},
    {"pitch": "G2", "duration": "T8"},
    {"pitch": "G1", "duration": "T8"},
    {"pitch": "G1", "duration": "T8"},
    {"pitch": "G1", "duration": "T8"},
    {"pitch": "G1", "duration": "T8"},
    {"pitch": "G2", "duration": "T8"},
    {"pitch": "G2", "duration": "T8"},
    {"pitch": "G1", "duration": "T8"}
]
```

- **Scale-degree sequence:** 5 -> 5 -> 5 -> 5 -> 5 -> 5 -> 5 -> 5 -> 5 -> 5 -> 5 -> 5
- **Onset grid (16th notes):** `XX.XXX.XXX.XXX.X`

### Riff C — repeats 6x (4/4)

```python
[
    {"pitch": "Bb1", "duration": "d8"},
    {"pitch": "F2", "duration": "16"},
    {"pitch": "Bb2", "duration": "16"},
    {"pitch": "Bb2", "duration": "16"},
    {"pitch": "F2", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Ab1", "duration": "8"},
    {"pitch": "Ab1", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Ab2", "duration": "16"},
    {"pitch": "Ab2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Ab1", "duration": "16"}
]
```

- **Scale-degree sequence:** b7 -> 4 -> b7 -> b7 -> 4 -> b7 -> b6 -> b6 -> b3 -> b6 -> b6 -> b3 -> b6
- **Onset grid (16th notes):** `X..XXXXXX.XXXXXX`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 24.32 notes per bar.
- **Tempo:** 73 BPM (half-time feel); changes: 53 BPM @ beat 7.0, 68 BPM @ beat 7.0, 77 BPM @ beat 9.0, 154 BPM @ beat 37.0, 77 BPM @ beat 61.0, 154 BPM @ beat 98.0.
- **Dominant durations:** 16th (917), eighth (747), eighth-triplet (395), quarter (390).

| Duration | Count |
|----------|-------|
| 16th | 917 |
| eighth | 747 |
| eighth-triplet | 395 |
| quarter | 390 |
| 16th-triplet | 159 |
| whole | 158 |
| half | 102 |
| dotted-half | 22 |
| dotted-eighth | 18 |
| dotted-quarter | 17 |
| 32nd | 14 |
| dotted-16th | 7 |
| quarter-triplet | 3 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| kick | 581 | 31.9% |
| hihat-open | 419 | 23.0% |
| tom | 239 | 13.1% |
| ride | 236 | 12.9% |
| snare | 232 | 12.7% |
| crash | 70 | 3.8% |
| other | 46 | 2.5% |

- **Density:** 15.45 hits/bar.
- **Pattern:** 116 bars, 48 unique
  (repetition 59%; top bar repeats 9x).
- **Fills:** tom hits in 29% of bars.

Dominant bar pattern (16th-note grid, `The Druid - Drums`):

```
hihat-open: X.X.X.X.X.XX..X.
kick: X.......X..X.X..
snare: ....X.........X.
```

**How to apply in this skill:** this skill has no real GM drum kit (channel 9 is
skipped — see `CLAUDE.md`). Use this pattern as a guide rail: lock chug/palm-mute hits
on the guitar/bass track to where `kick` lands above, place chordal accents where
`snare`/`crash` lands, and let the hi-hat density above suggest your eighth/sixteenth
subdivision choice.

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| The Rat Queen - Vocals - Voice Oohs | voice-oohs | 53 | pitched |
| The Rat Queen - Rhythm Guitar - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Rhythm - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Rat Queen - Lead Guitar - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Lead - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Solo Harmony - Distortion Guitar | distortion-guitar | 30 | pitched |
| Drawbar Organ | drawbar-organ | 16 | pitched |
| The Plague Doctor - Electric Bass (pick) | electric-bass-pick | 34 | pitched |
| The Druid - Drums | drum kit (ch.10) | — | percussion |

## How to apply in this skill

- **Set `bpm`: 73** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`** (watch for 2/4, 7/8 sections).
- **Write in C Phrygian.** Lean on 5 (G), 1 (C), b7 (Bb), b6 (Ab), 4 (F), b3 (Eb).
- **Octave:** roots around **octave 1** (lowest note here is C1).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor 16th as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (58%) — commit to a riff and cycle it; the top bar repeats 19x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
