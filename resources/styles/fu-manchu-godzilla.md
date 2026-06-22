# Style Card — Fu Manchu – Godzilla

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 69 BPM (half-time feel) |
| Tempo changes | 73 BPM @ beat 20.0 |
| Key / scale | F Dorian  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | none |
| Lowest note | Eb1 |
| Lowest open string | None |
| Notes per bar | 16.63 |
| Voicing | power-chord driven |
| Structure | 83 bars, 29 unique (repetition 65%; top bar repeats 11x) |

## Harmony

- **Key / scale:** F Dorian (confidence 100%).
- **Most-used pitch classes:** 1 (F), b7 (Eb), 5 (C), 4 (Bb), b3 (Ab), 6 (D).
- **Voicing:** power-chord driven — 187 power-chord hits vs 0 triads
  across 936 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×444.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to F Dorian. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 11x (4/4)

```python
[
    {"pitch": "Eb2", "duration": "8"},
    {"pitch": "Eb2", "duration": "8"},
    {"pitch": "Db2", "duration": "8"},
    {"pitch": "Db2", "duration": "8"},
    {"pitch": "C2", "duration": "8"},
    {"pitch": "C2", "duration": "8"},
    {"pitch": "Bb1", "duration": "8"},
    {"pitch": "Bb1", "duration": "8"}
]
```

- **Scale-degree sequence:** b7 -> b7 -> b6 -> b6 -> 5 -> 5 -> 4 -> 4
- **Onset grid (16th notes):** `X.X.X.X.X.X.X.X.`

### Riff B — repeats 9x (4/4)

```python
[
    {"pitch": "Ab1", "duration": "4"},
    {"pitch": "Ab1", "duration": "4"},
    {"pitch": "R", "duration": "8"},
    {"pitch": "D2", "duration": "8"},
    {"pitch": "Eb2", "duration": "8"},
    {"pitch": "Bb1", "duration": "8"}
]
```

- **Scale-degree sequence:** b3 -> b3 -> 6 -> b7 -> 4
- **Onset grid (16th notes):** `X...X.....X.X.X.`

### Riff C — repeats 8x (4/4)

```python
[
    {"pitch": "F1", "duration": "4"},
    {"pitch": "F1", "duration": "4"},
    {"pitch": "R", "duration": "8"},
    {"pitch": "Bb1", "duration": "8"},
    {"pitch": "C2", "duration": "8"},
    {"pitch": "G1", "duration": "8"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 4 -> 5 -> 2
- **Onset grid (16th notes):** `X...X.....X.X.X.`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 16.63 notes per bar.
- **Tempo:** 69 BPM (half-time feel); changes: 73 BPM @ beat 20.0.
- **Dominant durations:** eighth (830), 16th (325), quarter (217), 16th-triplet (31).

| Duration | Count |
|----------|-------|
| eighth | 830 |
| 16th | 325 |
| quarter | 217 |
| 16th-triplet | 31 |
| half | 16 |
| eighth-triplet | 13 |
| 32nd | 12 |
| dotted-eighth | 12 |
| whole | 11 |
| dotted-quarter | 2 |
| dotted-16th | 2 |
| dotted-half | 1 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| kick | 309 | 26.0% |
| snare | 244 | 20.5% |
| ride | 238 | 20.0% |
| hihat-open | 164 | 13.8% |
| crash | 130 | 10.9% |
| hihat-closed | 83 | 7.0% |
| tom | 20 | 1.7% |

- **Density:** 14.31 hits/bar.
- **Pattern:** 83 bars, 40 unique
  (repetition 52%; top bar repeats 10x).
- **Fills:** tom hits in 12% of bars.

Dominant bar pattern (16th-note grid, `Drums`):

```
hihat-open: X.X.X.X.X.X.X.X.
kick: X.......X.X.....
snare: ....X.......X...
```

**How to apply in this skill:** this skill has no real GM drum kit (channel 9 is
skipped — see `CLAUDE.md`). Use this pattern as a guide rail: lock chug/palm-mute hits
on the guitar/bass track to where `kick` lands above, place chordal accents where
`snare`/`crash` lands, and let the hi-hat density above suggest your eighth/sixteenth
subdivision choice.

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Distortion Guitar 1 | distortion-guitar | 30 | pitched |
| Distortion Guitar 2 | distortion-guitar | 30 | pitched |
| Electric Bass (pick) | electric-bass-pick | 34 | pitched |
| Drums | drum kit (ch.10) | — | percussion |

## How to apply in this skill

- **Set `bpm`: 69** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in F Dorian.** Lean on 1 (F), b7 (Eb), 5 (C), 4 (Bb), b3 (Ab), 6 (D).
- **Octave:** roots around **octave 1** (lowest note here is Eb1).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (65%) — commit to a riff and cycle it; the top bar repeats 11x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
