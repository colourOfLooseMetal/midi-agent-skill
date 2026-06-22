# Style Card — Electric Wizard – Satanic Rites Of Drugula

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 55 BPM (half-time feel) |
| Tempo changes | 60 BPM @ beat 8.0, 64 BPM @ beat 12.0, 67 BPM @ beat 72.0 |
| Key / scale | Db Phrygian  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | none |
| Lowest note | B0 |
| Lowest open string | None |
| Notes per bar | 26.89 |
| Voicing | power-chord driven |
| Structure | 96 bars, 36 unique (repetition 62%; top bar repeats 12x) |

## Harmony

- **Key / scale:** Db Phrygian (confidence 100%).
- **Most-used pitch classes:** 1 (Db), 5 (Ab), b3 (E), b6 (A), 4 (Gb), b7 (B).
- **Voicing:** power-chord driven — 825 power-chord hits vs 0 triads
  across 1361 single notes.
- **Interval color (within chords):** tritone ×1, minor-2nd
  ×5, fifth ×1212.

## Riff transcription

The 3 most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to Db Phrygian. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

### Riff A — repeats 12x (4/4)

```python
[
    {"pitch": "B2+Gb3", "duration": "16"},
    {"pitch": "Db3+Ab3", "duration": "d8"},
    {"pitch": "Db3+Ab3", "duration": "d8"},
    {"pitch": "Db3+Ab3", "duration": "16"},
    {"pitch": "B2+Gb3", "duration": "16"},
    {"pitch": "Db3+Ab3", "duration": "16"},
    {"pitch": "Db3+Ab3", "duration": "8"},
    {"pitch": "B2+Gb3", "duration": "16"},
    {"pitch": "Db3+Ab3", "duration": "16"},
    {"pitch": "Db3+Ab3", "duration": "8"}
]
```

- **Scale-degree sequence:** b7 -> 1 -> 1 -> 1 -> b7 -> 1 -> 1 -> b7 -> 1 -> 1
- **Onset grid (16th notes):** `XX..X..XXXX.XXX.`

### Riff B — repeats 12x (4/4)

```python
[
    {"pitch": "E3+B3", "duration": "4"},
    {"pitch": "E3+B3", "duration": "d8"},
    {"pitch": "E3+B3", "duration": "16"},
    {"pitch": "E3+B3", "duration": "16"},
    {"pitch": "Eb3+Bb3", "duration": "16"},
    {"pitch": "Eb3+Bb3", "duration": "8"},
    {"pitch": "Eb3+Bb3", "duration": "16"},
    {"pitch": "E3+B3", "duration": "16"},
    {"pitch": "E3+B3", "duration": "8"}
]
```

- **Scale-degree sequence:** b3 -> b3 -> b3 -> b3 -> 2 -> 2 -> 2 -> b3 -> b3
- **Onset grid (16th notes):** `X...X..XXXX.XXX.`

### Riff C — repeats 12x (4/4)

```python
[
    {"pitch": "Db3+Ab3", "duration": "4"},
    {"pitch": "Db3+Ab3", "duration": "8"},
    {"pitch": "C3+G3", "duration": "8"},
    {"pitch": "A2+E3", "duration": "4"},
    {"pitch": "A2+E3", "duration": "8"},
    {"pitch": "C3+G3", "duration": "8"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 7 -> b6 -> b6 -> 7
- **Onset grid (16th notes):** `X...X.X.X...X.X.`

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.

## Rhythm & pacing

- **Note density:** 26.89 notes per bar.
- **Tempo:** 55 BPM (half-time feel); changes: 60 BPM @ beat 8.0, 64 BPM @ beat 12.0, 67 BPM @ beat 72.0.
- **Dominant durations:** 16th (1201), eighth (727), quarter (352), dotted-eighth (251).

| Duration | Count |
|----------|-------|
| 16th | 1201 |
| eighth | 727 |
| quarter | 352 |
| dotted-eighth | 251 |
| 32nd | 131 |
| half | 18 |
| whole | 12 |
| 16th-triplet | 4 |
| eighth-triplet | 4 |
| dotted-half | 1 |

## Percussion

| Voice | Hits | % |
|-------|------|---|
| hihat-closed | 374 | 35.2% |
| crash | 292 | 27.5% |
| snare | 187 | 17.6% |
| kick | 178 | 16.8% |
| tom | 31 | 2.9% |

- **Density:** 11.06 hits/bar.
- **Pattern:** 86 bars, 6 unique
  (repetition 93%; top bar repeats 67x).
- **Fills:** tom hits in 6% of bars.

Dominant bar pattern (16th-note grid, `Percussion - Drums`):

```
crash: X.......X...X...
hihat-closed: ..X.X.X...X...X.
kick: X.......X.......
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
| Vocals - Alto Sax | alto-sax | 65 | pitched |
| Lead - Distortion Guitar | distortion-guitar | 30 | pitched |
| Rhythm  - Distortion Guitar | distortion-guitar | 30 | pitched |
| Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Percussion - Drums | drum kit (ch.10) | — | percussion |

## How to apply in this skill

- **Set `bpm`: 55** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in Db Phrygian.** Lean on 1 (Db), 5 (Ab), b3 (E), b6 (A), 4 (Gb), b7 (B).
- **Octave:** roots around **octave 0** (lowest note here is B0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor 16th as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (62%) — commit to a riff and cycle it; the top bar repeats 12x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
