# Style Card — Electric Wizard – We Hate You

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 74 BPM (half-time feel) |
| Tempo changes | 50 BPM @ beat 79.0 |
| Key / scale | Eb Phrygian  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | none |
| Lowest note | Bb0 |
| Lowest open string | None |
| Notes per bar | 23.05 |
| Voicing | power-chord driven |
| Structure | 84 bars, 7 unique (repetition 92%; top bar repeats 22x) |

## Harmony

- **Key / scale:** Eb Phrygian (confidence 100%).
- **Most-used pitch classes:** 1 (Eb), 5 (Bb), b6 (B), 4 (Ab), b3 (Gb), b2 (E).
- **Voicing:** power-chord driven — 256 power-chord hits vs 0 triads
  across 1261 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×675.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to Eb Phrygian. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 22x (4/4)

```python
[
    {"pitch": "Eb1", "duration": "4"},
    {"pitch": "Eb1", "duration": "8"},
    {"pitch": "Eb1", "duration": "4"},
    {"pitch": "Eb1", "duration": "8"},
    {"pitch": "Eb1", "duration": "8"},
    {"pitch": "Eb1", "duration": "8"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 1 -> 1 -> 1 -> 1
- **Onset grid (16th notes):** `X...X.X...X.X.X.`

### Riff B — repeats 22x (4/4)

```python
[
    {"pitch": "B0", "duration": "4"},
    {"pitch": "B0", "duration": "8"},
    {"pitch": "B0", "duration": "8"},
    {"pitch": "Ab1", "duration": "16"},
    {"pitch": "Ab1", "duration": "16"},
    {"pitch": "Ab1", "duration": "16"},
    {"pitch": "Ab1", "duration": "16"},
    {"pitch": "Ab1", "duration": "8"},
    {"pitch": "Ab1", "duration": "8"}
]
```

- **Scale-degree sequence:** b6 -> b6 -> b6 -> 4 -> 4 -> 4 -> 4 -> 4 -> 4
- **Onset grid (16th notes):** `X...X.X.XXXXX.X.`

### Riff C — repeats 10x (4/4)

```python
[
    {"pitch": "Bb0", "duration": "4"},
    {"pitch": "D1", "duration": "8"},
    {"pitch": "B1", "duration": "4"},
    {"pitch": "D1", "duration": "8"},
    {"pitch": "Db1", "duration": "8"},
    {"pitch": "Ab1", "duration": "8"}
]
```

- **Scale-degree sequence:** 5 -> 7 -> b6 -> 7 -> b7 -> 4
- **Onset grid (16th notes):** `X...X.X...X.X.X.`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 23.05 notes per bar.
- **Tempo:** 74 BPM (half-time feel); changes: 50 BPM @ beat 79.0.
- **Dominant durations:** eighth (1020), quarter (506), 16th (312), half (66).

| Duration | Count |
|----------|-------|
| eighth | 1020 |
| quarter | 506 |
| 16th | 312 |
| half | 66 |
| dotted-quarter | 20 |
| whole | 16 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| kick | 595 | 41.2% |
| crash | 295 | 20.4% |
| snare | 254 | 17.6% |
| hihat-open | 199 | 13.8% |
| tom | 97 | 6.7% |
| other | 4 | 0.3% |

- **Density:** 17.19 hits/bar.
- **Pattern:** 79 bars, 59 unique
  (repetition 25%; top bar repeats 6x).
- **Fills:** tom hits in 49% of bars.

Dominant bar pattern (16th-note grid, `Mark Greening - Drums`):

```
crash: X.X.....X.X.....
hihat-open: ....X.X.....X.X.
kick: XXX.....XXX.....
snare: ....X..X....X..X
```

**How to apply in this skill:** this skill has no real GM drum kit (channel 9 is
skipped — see `CLAUDE.md`). Use this pattern as a guide rail: lock chug/palm-mute hits
on the guitar/bass track to where `kick` lands above, place chordal accents where
`snare`/`crash` lands, and let the hi-hat density above suggest your eighth/sixteenth
subdivision choice.

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Jus Oborn - Distortion Guitar 1 | distortion-guitar | 30 | pitched |
| Jus Oborn - Distortion Guitar 2 | distortion-guitar | 30 | pitched |
| Tim Bagshaw-bass effect - Overdriven Guitar | overdriven-guitar | 29 | pitched |
| Tim Bagshaw - Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Mark Greening - Drums | drum kit (ch.10) | — | percussion |

## How to apply in this skill

- **Set `bpm`: 74** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in Eb Phrygian.** Lean on 1 (Eb), 5 (Bb), b6 (B), 4 (Ab), b3 (Gb), b2 (E).
- **Octave:** roots around **octave 0** (lowest note here is Bb0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (92%) — commit to a riff and cycle it; the top bar repeats 22x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
