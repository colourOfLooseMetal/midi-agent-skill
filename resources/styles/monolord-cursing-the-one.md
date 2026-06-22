# Style Card — Monolord – Cursing The One

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 125 BPM |
| Tempo changes | 120 BPM @ beat 32.0, 115 BPM @ beat 153.0 |
| Key / scale | B minor blues  (confidence 88%) |
| Main time signature | 4/4 |
| Other meters | 3/4, 2/4, 7/4, 5/4, 6/4 |
| Lowest note | B0 |
| Lowest open string | None |
| Notes per bar | 6.42 |
| Voicing | power-chord driven |
| Structure | 258 bars, 70 unique (repetition 73%; top bar repeats 35x) |

## Harmony

- **Key / scale:** B minor blues (confidence 88%).
- **Most-used pitch classes:** 1 (B), 5 (Gb), b5 (F), b2 (C), 7 (Bb), 4 (E).
- **Voicing:** power-chord driven — 253 power-chord hits vs 0 triads
  across 1003 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×710.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to B minor blues. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 35x (4/4)

```python
[
    {"pitch": "B0", "duration": "1"}
]
```

- **Scale-degree sequence:** 1
- **Onset grid (16th notes):** `X...............`

### Riff B — repeats 30x (4/4)

```python
[
    {"pitch": "F1", "duration": "1"}
]
```

- **Scale-degree sequence:** b5
- **Onset grid (16th notes):** `X...............`

### Riff C — repeats 12x (4/4)

```python
[
    {"pitch": "Gb1", "duration": "1"}
]
```

- **Scale-degree sequence:** 5
- **Onset grid (16th notes):** `X...............`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 6.42 notes per bar.
- **Tempo:** 125 BPM; changes: 120 BPM @ beat 32.0, 115 BPM @ beat 153.0.
- **Dominant durations:** eighth (888), half (285), quarter (269), whole (184).

| Duration | Count |
|----------|-------|
| eighth | 888 |
| half | 285 |
| quarter | 269 |
| whole | 184 |
| dotted-quarter | 91 |
| dotted-half | 6 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| kick | 530 | 33.2% |
| crash | 376 | 23.6% |
| snare | 270 | 16.9% |
| hihat-open | 233 | 14.6% |
| tom | 183 | 11.5% |
| hihat-closed | 4 | 0.3% |

- **Density:** 5.96 hits/bar.
- **Pattern:** 228 bars, 92 unique
  (repetition 60%; top bar repeats 20x).
- **Fills:** tom hits in 16% of bars.

Dominant bar pattern (16th-note grid, `Drums`):

```
crash: X...............
hihat-open: ....X...X...X...
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
| Distortion Guitar 1 | distortion-guitar | 30 | pitched |
| Distortion Guitar 2 | distortion-guitar | 30 | pitched |
| Electric Bass (pick) | electric-bass-pick | 34 | pitched |
| Drums | drum kit (ch.10) | — | percussion |

## How to apply in this skill

- **Set `bpm`: 125**. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`** (watch for 3/4, 2/4, 7/4, 5/4, 6/4 sections).
- **Write in B minor blues.** Lean on 1 (B), 5 (Gb), b5 (F), b2 (C), 7 (Bb), 4 (E).
- **Octave:** roots around **octave 0** (lowest note here is B0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (73%) — commit to a riff and cycle it; the top bar repeats 35x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
