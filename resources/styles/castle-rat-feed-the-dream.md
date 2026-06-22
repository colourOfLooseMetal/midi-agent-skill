# Style Card — Castle Rat – Feed the Dream

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 85 BPM (half-time feel) |
| Tempo changes | 67 BPM @ beat 9.0, 73 BPM @ beat 10.0, 80 BPM @ beat 13.0, 174 BPM @ beat 14.0, 85 BPM @ beat 39.0, 177 BPM @ beat 49.0, 85 BPM @ beat 74.0, 88 BPM @ beat 84.0, 84 BPM @ beat 90.0, 117 BPM @ beat 93.0, 85 BPM @ beat 107.0, 78 BPM @ beat 120.0, 108 BPM @ beat 122.0 |
| Key / scale | C minor blues  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | 2/4, 3/4, 7/8, 9/8, 9/16 |
| Lowest note | C1 |
| Lowest open string | None |
| Notes per bar | 16.75 |
| Voicing | power-chord driven |
| Structure | 126 bars, 45 unique (repetition 64%; top bar repeats 20x) |

## Harmony

- **Key / scale:** C minor blues (confidence 100%).
- **Most-used pitch classes:** 1 (C), 4 (F), b7 (Bb), 5 (G), b3 (Eb), b5 (Gb).
- **Voicing:** power-chord driven — 234 power-chord hits vs 0 triads
  across 1744 single notes.
- **Interval color (within chords):** tritone ×1, minor-2nd
  ×0, fifth ×361.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to C minor blues. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 20x (4/4)

```python
[
    {"pitch": "C2", "duration": "4"},
    {"pitch": "C2", "duration": "8"},
    {"pitch": "C3+G3", "duration": "8"},
    {"pitch": "Bb2+F3", "duration": "8"},
    {"pitch": "C3+G3", "duration": "8"},
    {"pitch": "C3+G3", "duration": "4"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 1 -> b7 -> 1 -> 1
- **Onset grid (16th notes):** `X...X.X.X.X.X...`

### Riff B — repeats 11x (4/4)

```python
[
    {"pitch": "C2+G2", "duration": "2"},
    {"pitch": "Bb2+F3", "duration": "2"}
]
```

- **Scale-degree sequence:** 1 -> b7
- **Onset grid (16th notes):** `X.......X.......`

### Riff C — repeats 10x (4/4)

```python
[
    {"pitch": "C2", "duration": "4"},
    {"pitch": "C2", "duration": "8"},
    {"pitch": "C3+G3", "duration": "8"},
    {"pitch": "Bb2+F3", "duration": "8"},
    {"pitch": "Db3+Ab3", "duration": "8"},
    {"pitch": "C3+G3", "duration": "4"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 1 -> b7 -> b2 -> 1
- **Onset grid (16th notes):** `X...X.X.X.X.X...`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 16.75 notes per bar.
- **Tempo:** 85 BPM (half-time feel); changes: 67 BPM @ beat 9.0, 73 BPM @ beat 10.0, 80 BPM @ beat 13.0, 174 BPM @ beat 14.0, 85 BPM @ beat 39.0, 177 BPM @ beat 49.0, 85 BPM @ beat 74.0, 88 BPM @ beat 84.0, 84 BPM @ beat 90.0, 117 BPM @ beat 93.0, 85 BPM @ beat 107.0, 78 BPM @ beat 120.0, 108 BPM @ beat 122.0.
- **Dominant durations:** eighth (865), 16th (453), quarter (403), half (171).

| Duration | Count |
|----------|-------|
| eighth | 865 |
| 16th | 453 |
| quarter | 403 |
| half | 171 |
| dotted-quarter | 88 |
| dotted-eighth | 58 |
| 16th-triplet | 51 |
| whole | 35 |
| dotted-half | 10 |
| 32nd | 1 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| kick | 313 | 27.5% |
| crash | 267 | 23.5% |
| snare | 244 | 21.4% |
| hihat-open | 163 | 14.3% |
| tom | 151 | 13.3% |

- **Density:** 9.03 hits/bar.
- **Pattern:** 119 bars, 62 unique
  (repetition 48%; top bar repeats 15x).
- **Fills:** tom hits in 30% of bars.

Dominant bar pattern (16th-note grid, `The Druid - Drums`):

```
hihat-open: X...X...X...X...
kick: X...X.X.........
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
| The Rat Queen - Vocals - Voice Oohs | voice-oohs | 53 | pitched |
| The Rat Queen - Guitar - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Plague Doctor - Electric Bass (pick) | electric-bass-pick | 34 | pitched |
| The Druid - Drums | drum kit (ch.10) | — | percussion |

## How to apply in this skill

- **Set `bpm`: 85** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`** (watch for 2/4, 3/4, 7/8, 9/8, 9/16 sections).
- **Write in C minor blues.** Lean on 1 (C), 4 (F), b7 (Bb), 5 (G), b3 (Eb), b5 (Gb).
- **Octave:** roots around **octave 1** (lowest note here is C1).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (64%) — commit to a riff and cycle it; the top bar repeats 20x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
