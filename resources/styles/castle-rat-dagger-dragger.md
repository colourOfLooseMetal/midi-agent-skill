# Style Card — Castle Rat – Dagger Dragger

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 138 BPM |
| Tempo changes | none |
| Key / scale | C Phrygian  (confidence 94%) |
| Main time signature | 4/4 |
| Other meters | 2/4 |
| Lowest note | C1 |
| Lowest open string | None |
| Notes per bar | 18.65 |
| Voicing | power-chord driven |
| Structure | 128 bars, 35 unique (repetition 73%; top bar repeats 19x) |

## Harmony

- **Key / scale:** C Phrygian (confidence 94%).
- **Most-used pitch classes:** 1 (C), 4 (F), 5 (G), b3 (Eb), b7 (Bb), b5 (Gb).
- **Voicing:** power-chord driven — 340 power-chord hits vs 1 triads
  across 1907 single notes.
- **Interval color (within chords):** tritone ×3, minor-2nd
  ×11, fifth ×507.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to C Phrygian. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 19x (4/4)

```python
[
    {"pitch": "C1", "duration": "4"},
    {"pitch": "Gb1", "duration": "4"},
    {"pitch": "Eb1", "duration": "T4"},
    {"pitch": "F1", "duration": "T8"},
    {"pitch": "Eb1", "duration": "T4"},
    {"pitch": "F1", "duration": "T8"}
]
```

- **Scale-degree sequence:** 1 -> b5 -> b3 -> 4 -> b3 -> 4
- **Onset grid (16th notes):** `X...X...X..XX..X`

### Riff B — repeats 19x (4/4)

```python
[
    {"pitch": "C1", "duration": "4"},
    {"pitch": "Gb1", "duration": "4"},
    {"pitch": "Eb1", "duration": "4"},
    {"pitch": "F1", "duration": "4"}
]
```

- **Scale-degree sequence:** 1 -> b5 -> b3 -> 4
- **Onset grid (16th notes):** `X...X...X...X...`

### Riff C — repeats 10x (4/4)

```python
[
    {"pitch": "Bb1", "duration": "T8"},
    {"pitch": "C2", "duration": "T8"},
    {"pitch": "C2", "duration": "T8"},
    {"pitch": "C2", "duration": "T4"},
    {"pitch": "C2", "duration": "T8"},
    {"pitch": "Bb1", "duration": "T8"},
    {"pitch": "C2", "duration": "T8"},
    {"pitch": "C2", "duration": "T8"},
    {"pitch": "C2", "duration": "T4"},
    {"pitch": "C2", "duration": "T8"}
]
```

- **Scale-degree sequence:** b7 -> 1 -> 1 -> 1 -> 1 -> b7 -> 1 -> 1 -> 1 -> 1
- **Onset grid (16th notes):** `XX.XX..XXX.XX..X`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 18.65 notes per bar.
- **Tempo:** 138 BPM; changes: none.
- **Dominant durations:** eighth-triplet (1084), quarter (654), quarter-triplet (448), half (88).

| Duration | Count |
|----------|-------|
| eighth-triplet | 1084 |
| quarter | 654 |
| quarter-triplet | 448 |
| half | 88 |
| eighth | 88 |
| whole | 43 |
| 16th | 33 |
| 16th-triplet | 23 |
| dotted-half | 11 |
| 32nd | 8 |
| dotted-16th | 7 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| kick | 405 | 30.8% |
| snare | 337 | 25.7% |
| crash | 217 | 16.5% |
| tom | 188 | 14.3% |
| hihat-open | 166 | 12.6% |

- **Density:** 9.95 hits/bar.
- **Pattern:** 126 bars, 66 unique
  (repetition 48%; top bar repeats 9x).
- **Fills:** tom hits in 23% of bars.

Dominant bar pattern (16th-note grid, `The Druid - Drums`):

```
crash: X...X...X...X...
kick: X.......X..X....
snare: ....X.......X..X
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
| The Rat Queen - Guitar - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Plague Doctor - Electric Bass (pick) | electric-bass-pick | 34 | pitched |
| The Druid - Drums | drum kit (ch.10) | — | percussion |

## How to apply in this skill

- **Set `bpm`: 138**.
- **`time_signature`: `4/4`** (watch for 2/4 sections).
- **Write in C Phrygian.** Lean on 1 (C), 4 (F), 5 (G), b3 (Eb), b7 (Bb), b5 (Gb).
- **Octave:** roots around **octave 1** (lowest note here is C1).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth-triplet as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (73%) — commit to a riff and cycle it; the top bar repeats 19x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
