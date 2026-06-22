# Style Card — Monolord – Empress Rising

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 120 BPM |
| Tempo changes | 110 BPM @ beat 230.0, 120 BPM @ beat 265.0 |
| Key / scale | B Phrygian  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | 6/4, 8/4, 2/4 |
| Lowest note | B0 |
| Lowest open string | None |
| Notes per bar | 6.59 |
| Voicing | power-chord driven |
| Structure | 250 bars, 18 unique (repetition 93%; top bar repeats 79x) |

## Harmony

- **Key / scale:** B Phrygian (confidence 100%).
- **Most-used pitch classes:** 1 (B), 5 (Gb), b7 (A), b2 (C), 4 (E), 7 (Bb).
- **Voicing:** power-chord driven — 105 power-chord hits vs 0 triads
  across 1418 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×731.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to B Phrygian. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 79x (4/4)

```python
[
    {"pitch": "B1+Gb2", "duration": "2"},
    {"pitch": "B2+Gb3", "duration": "2"}
]
```

- **Scale-degree sequence:** 1 -> 1
- **Onset grid (16th notes):** `X.......X.......`

### Riff B — repeats 74x (4/4)

```python
[
    {"pitch": "A2+E3", "duration": "8"},
    {"pitch": "B2+Gb3", "duration": "8"},
    {"pitch": "C3+G3", "duration": "4"},
    {"pitch": "A2+E3", "duration": "4"},
    {"pitch": "B2+Gb3", "duration": "4"}
]
```

- **Scale-degree sequence:** b7 -> 1 -> b2 -> b7 -> 1
- **Onset grid (16th notes):** `X.X.X...X...X...`

### Riff C — repeats 21x (4/4)

```python
[
    {"pitch": "B1", "duration": "2"},
    {"pitch": "B2", "duration": "2"}
]
```

- **Scale-degree sequence:** 1 -> 1
- **Onset grid (16th notes):** `X.......X.......`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 6.59 notes per bar.
- **Tempo:** 120 BPM; changes: 110 BPM @ beat 230.0, 120 BPM @ beat 265.0.
- **Dominant durations:** eighth (791), quarter (783), half (481), dotted-quarter (63).

| Duration | Count |
|----------|-------|
| eighth | 791 |
| quarter | 783 |
| half | 481 |
| dotted-quarter | 63 |
| whole | 35 |
| dotted-half | 4 |
| 16th | 1 |
| dotted-eighth | 1 |

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Distortion Guitar - Thomas V. Jäger - Distortion Guitar | distortion-guitar | 30 | pitched |
| Electric Bass - Mika Häkki - Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Jazz Guitar - Thomas V. Jäger - Electric Guitar (jazz) | electric-guitar-jazz | 26 | pitched |

## How to apply in this skill

- **Set `bpm`: 120**. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`** (watch for 6/4, 8/4, 2/4 sections).
- **Write in B Phrygian.** Lean on 1 (B), 5 (Gb), b7 (A), b2 (C), 4 (E), 7 (Bb).
- **Octave:** roots around **octave 0** (lowest note here is B0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (93%) — commit to a riff and cycle it; the top bar repeats 79x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
