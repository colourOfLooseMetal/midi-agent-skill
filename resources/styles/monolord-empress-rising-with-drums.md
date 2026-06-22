# Style Card — Monolord – Empress Rising (With Drums)

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 120 BPM |
| Tempo changes | none |
| Key / scale | B Phrygian  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | none |
| Lowest note | B0 |
| Lowest open string | None |
| Notes per bar | 16.0 |
| Voicing | power-chord driven |
| Structure | 16 bars, 2 unique (repetition 88%; top bar repeats 8x) |

## Harmony

- **Key / scale:** B Phrygian (confidence 100%).
- **Most-used pitch classes:** 1 (B), 5 (Gb), b7 (A), b2 (C), 4 (E), b6 (G).
- **Voicing:** power-chord driven — 16 power-chord hits vs 0 triads
  across 128 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×128.

## Riff transcription

The 2 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to B Phrygian. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 8x (4/4)

```python
[
    {"pitch": "B0", "duration": "8"},
    {"pitch": "B0", "duration": "8"},
    {"pitch": "B0", "duration": "8"},
    {"pitch": "B0", "duration": "8"},
    {"pitch": "B1", "duration": "8"},
    {"pitch": "B1", "duration": "8"},
    {"pitch": "B1", "duration": "8"},
    {"pitch": "B1", "duration": "8"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 1 -> 1 -> 1 -> 1 -> 1 -> 1
- **Onset grid (16th notes):** `X.X.X.X.X.X.X.X.`

### Riff B — repeats 8x (4/4)

```python
[
    {"pitch": "A1", "duration": "8"},
    {"pitch": "B1", "duration": "8"},
    {"pitch": "C2", "duration": "8"},
    {"pitch": "C2", "duration": "8"},
    {"pitch": "A1", "duration": "8"},
    {"pitch": "A1", "duration": "8"},
    {"pitch": "B1", "duration": "8"},
    {"pitch": "B1", "duration": "8"}
]
```

- **Scale-degree sequence:** b7 -> 1 -> b2 -> b2 -> b7 -> b7 -> 1 -> 1
- **Onset grid (16th notes):** `X.X.X.X.X.X.X.X.`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 16.0 notes per bar.
- **Tempo:** 120 BPM; changes: none.
- **Dominant durations:** eighth (256).

| Duration | Count |
|----------|-------|
| eighth | 256 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| hihat-open | 57 | 50.9% |
| kick | 28 | 25.0% |
| snare | 19 | 17.0% |
| tom | 7 | 6.2% |
| crash | 1 | 0.9% |

- **Density:** 7.0 hits/bar.
- **Pattern:** 16 bars, 7 unique
  (repetition 56%; top bar repeats 8x).
- **Fills:** tom hits in 12% of bars.

Dominant bar pattern (16th-note grid, `Drums`):

```
hihat-open: X...X...X...X...
kick: X...............
snare: ........X.......
```

**How to apply in this skill:** this skill has no real GM drum kit (channel 9 is
skipped — see `CLAUDE.md`). Use this pattern as a guide rail: lock chug/palm-mute hits
on the guitar/bass track to where `kick` lands above, place chordal accents where
`snare`/`crash` lands, and let the hi-hat density above suggest your eighth/sixteenth
subdivision choice.

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Drums | drum kit (ch.10) | — | percussion |
| Distortion Guitar | distortion-guitar | 30 | pitched |

## How to apply in this skill

- **Set `bpm`: 120**.
- **`time_signature`: `4/4`**.
- **Write in B Phrygian.** Lean on 1 (B), 5 (Gb), b7 (A), b2 (C), 4 (E), b6 (G).
- **Octave:** roots around **octave 0** (lowest note here is B0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (88%) — commit to a riff and cycle it; the top bar repeats 8x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
