# Style Card — Monolord – Audhumbla

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 114 BPM |
| Tempo changes | none |
| Key / scale | B Phrygian  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | 3/4, 6/4, 2/4 |
| Lowest note | B0 |
| Lowest open string | None |
| Notes per bar | 6.8 |
| Voicing | power-chord driven |
| Structure | 183 bars, 102 unique (repetition 44%; top bar repeats 25x) |

## Harmony

- **Key / scale:** B Phrygian (confidence 100%).
- **Most-used pitch classes:** 1 (B), 5 (Gb), b2 (C), b6 (G), b3 (D), b7 (A).
- **Voicing:** power-chord driven — 128 power-chord hits vs 2 triads
  across 1031 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×389.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to B Phrygian. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 25x (4/4)

```python
[
    {"pitch": "B1+Gb2", "duration": "1"}
]
```

- **Scale-degree sequence:** 1
- **Onset grid (16th notes):** `X...............`

### Riff B — repeats 9x (4/4)

```python
[
    {"pitch": "B1+Gb2", "duration": "4"},
    {"pitch": "C2+G2", "duration": "2"},
    {"pitch": "C2+G2", "duration": "4"}
]
```

- **Scale-degree sequence:** 1 -> b2 -> b2
- **Onset grid (16th notes):** `X...X.......X...`

### Riff C — repeats 8x (4/4)

```python
[
    {"pitch": "B1", "duration": "4"},
    {"pitch": "B1", "duration": "4"},
    {"pitch": "B1", "duration": "4"},
    {"pitch": "B1", "duration": "4"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 1 -> 1
- **Onset grid (16th notes):** `X...X...X...X...`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 6.8 notes per bar.
- **Tempo:** 114 BPM; changes: none.
- **Dominant durations:** quarter (628), eighth (518), half (130), whole (71).

| Duration | Count |
|----------|-------|
| quarter | 628 |
| eighth | 518 |
| half | 130 |
| whole | 71 |
| eighth-triplet | 42 |
| dotted-half | 29 |
| dotted-quarter | 6 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| kick | 338 | 32.5% |
| hihat-open | 264 | 25.4% |
| crash | 158 | 15.2% |
| snare | 141 | 13.6% |
| ride | 79 | 7.6% |
| tom | 59 | 5.7% |

- **Density:** 5.0 hits/bar.
- **Pattern:** 155 bars, 72 unique
  (repetition 54%; top bar repeats 17x).
- **Fills:** tom hits in 6% of bars.

Dominant bar pattern (16th-note grid, `Drums`):

```
crash: X...X...........
kick: X...X...........
```

**How to apply in this skill:** this skill has no real GM drum kit (channel 9 is
skipped — see `CLAUDE.md`). Use this pattern as a guide rail: lock chug/palm-mute hits
on the guitar/bass track to where `kick` lands above, place chordal accents where
`snare`/`crash` lands, and let the hi-hat density above suggest your eighth/sixteenth
subdivision choice.

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Drums | drum kit (ch.10) | — | percussion |
| Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Distortion Guitar 1 | distortion-guitar | 30 | pitched |
| Distortion Guitar 2 | distortion-guitar | 30 | pitched |

## How to apply in this skill

- **Set `bpm`: 114**.
- **`time_signature`: `4/4`** (watch for 3/4, 6/4, 2/4 sections).
- **Write in B Phrygian.** Lean on 1 (B), 5 (Gb), b2 (C), b6 (G), b3 (D), b7 (A).
- **Octave:** roots around **octave 0** (lowest note here is B0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor quarter as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (44%) — commit to a riff and cycle it; the top bar repeats 25x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
