# Style Card — Electric Wizard – Vinum Sabbathi

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 122 BPM |
| Tempo changes | 100 BPM @ beat 79.0 |
| Key / scale | Bb natural minor (Aeolian)  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | none |
| Lowest note | Bb0 |
| Lowest open string | None |
| Notes per bar | 10.3 |
| Voicing | power-chord driven |
| Structure | 78 bars, 7 unique (repetition 91%; top bar repeats 20x) |

## Harmony

- **Key / scale:** Bb natural minor (Aeolian) (confidence 100%).
- **Most-used pitch classes:** 1 (Bb), b3 (Db), 5 (F), 4 (Eb), b7 (Ab), 2 (C).
- **Voicing:** power-chord driven — 130 power-chord hits vs 0 triads
  across 610 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×276.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to Bb natural minor (Aeolian). Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 20x (4/4)

```python
[
    {"pitch": "Bb1+F2+Bb2", "duration": "d4"},
    {"pitch": "Bb1+F2", "duration": "8"},
    {"pitch": "Bb1+F2+Bb2", "duration": "4"},
    {"pitch": "Bb1+F2", "duration": "8"},
    {"pitch": "Bb1+F2", "duration": "8"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 1 -> 1 -> 1
- **Onset grid (16th notes):** `X.....X.X...X.X.`

### Riff B — repeats 20x (4/4)

```python
[
    {"pitch": "Db2+Ab2+Db3", "duration": "d4"},
    {"pitch": "Db2+Ab2", "duration": "8"},
    {"pitch": "Db2+Ab2", "duration": "8"},
    {"pitch": "Eb2+Bb2", "duration": "4"},
    {"pitch": "Eb2+Bb2", "duration": "8"}
]
```

- **Scale-degree sequence:** b3 -> b3 -> b3 -> 4 -> 4
- **Onset grid (16th notes):** `X.....X.X.X...X.`

### Riff C — repeats 16x (4/4)

```python
[
    {"pitch": "Bb1+F2+Bb2", "duration": "d4"},
    {"pitch": "Bb1+F2", "duration": "8"},
    {"pitch": "C3", "duration": "4"},
    {"pitch": "Ab2", "duration": "8"},
    {"pitch": "Eb2", "duration": "8"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 2 -> b7 -> 4
- **Onset grid (16th notes):** `X.....X.X...X.X.`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 10.3 notes per bar.
- **Tempo:** 122 BPM; changes: 100 BPM @ beat 79.0.
- **Dominant durations:** eighth (400), 32nd (224), dotted-quarter (208), quarter (96).

| Duration | Count |
|----------|-------|
| eighth | 400 |
| 32nd | 224 |
| dotted-quarter | 208 |
| quarter | 96 |
| whole | 12 |
| half | 2 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| kick | 245 | 50.6% |
| snare | 203 | 41.9% |
| tom | 36 | 7.4% |

- **Density:** 5.63 hits/bar.
- **Pattern:** 81 bars, 21 unique
  (repetition 74%; top bar repeats 14x).
- **Fills:** tom hits in 14% of bars.

Dominant bar pattern (16th-note grid, `Mark Greening - Drums 2`):

```
kick: X.....X.........
snare: ........X.X...X.
```

**How to apply in this skill:** this skill has no real GM drum kit (channel 9 is
skipped — see `CLAUDE.md`). Use this pattern as a guide rail: lock chug/palm-mute hits
on the guitar/bass track to where `kick` lands above, place chordal accents where
`snare`/`crash` lands, and let the hi-hat density above suggest your eighth/sixteenth
subdivision choice.

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Jus Oborn - Distortion Guitar | distortion-guitar | 30 | pitched |
| Jus Oborn - Overdriven Guitar | overdriven-guitar | 29 | pitched |
| Tim Bagshaw - Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Mark Greening - Drums 1 | drum kit (ch.10) | — | percussion |
| Mark Greening - Drums 2 | drum kit (ch.10) | — | percussion |

## How to apply in this skill

- **Set `bpm`: 122**. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in Bb natural minor (Aeolian).** Lean on 1 (Bb), b3 (Db), 5 (F), 4 (Eb), b7 (Ab), 2 (C).
- **Octave:** roots around **octave 0** (lowest note here is Bb0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (91%) — commit to a riff and cycle it; the top bar repeats 20x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
