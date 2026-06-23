# Style Card — Monolord – Cursing The One

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track. See `CLAUDE.md` in this folder for
what each section means and how to apply it in a composition.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 125 BPM |
| Tempo changes | 120 BPM @ beat 32.0, 115 BPM @ beat 153.0 |
| Key / scale | B minor blues  (83% scale-fit (heuristic)) |
| Main time signature | 4/4 |
| Other meters | 3/4, 2/4, 7/4, 5/4, 6/4 |
| Lowest note (guitar) | B1 |
| Lowest open string (guitar) | B1  (down-tuned) |
| Notes per bar | 5.91 |
| Voicing | power-chord driven |
| Structure | 258 bars, 81 unique (repetition 69%; top bar repeats 22x) |

## Harmony

- **Key / scale:** B minor blues (83% scale-fit (heuristic)).
- **Most-used pitch classes:** 1 (B), 5 (Gb), b5 (F), b2 (C), 7 (Bb), 4 (E).
- **Voicing:** power-chord driven — 253 power-chord hits vs 0 triads
  across 150 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×660.

## Riff transcription

The most-repeated **moving** figures on the representative track (multi-bar phrases
preferred over single bars), transcribed verbatim in this skill's note syntax, with
scale degrees relative to B minor blues. Sustained drone bars are pulled out separately as
the **Pedal / root center**. Onset grids share the percussion grid's 16th-note
convention below (with `|` marking each barline).

### Riff A — 4 bars, repeats 8x (4/4)

```python
[
    {"pitch": "Gb2", "duration": "1"},
    {"pitch": "F2", "duration": "1"},
    {"pitch": "R", "duration": "1"},
    {"pitch": "B1", "duration": "1"}
]
```

- **Scale-degree sequence:** 5 -> b5 -> 1
- **Onset grid (16th notes, `|` = barline):** `X............... | X............... | ................ | X...............`

### Riff B — 4 bars, repeats 6x (4/4)

```python
[
    {"pitch": "B1+Gb2", "duration": "1"},
    {"pitch": "R", "duration": "2"},
    {"pitch": "F2+C3", "duration": "4"},
    {"pitch": "B1+Gb2", "duration": "4"},
    {"pitch": "R", "duration": "4"},
    {"pitch": "F2+C3", "duration": "4"},
    {"pitch": "B1+Gb2", "duration": "2"},
    {"pitch": "R", "duration": "2"},
    {"pitch": "C2+G2", "duration": "4"},
    {"pitch": "C2+G2", "duration": "8"},
    {"pitch": "Eb2+Bb2", "duration": "8"}
]
```

- **Scale-degree sequence:** 1 -> b5 -> 1 -> b5 -> 1 -> b2 -> b2 -> 3
- **Onset grid (16th notes, `|` = barline):** `X............... | ........X...X... | ....X...X....... | ........X...X.X.`

### Riff C — 2 bars, repeats 6x (4/4)

```python
[
    {"pitch": "B1+Gb2", "duration": "2"},
    {"pitch": "B2+Gb3", "duration": "d4"},
    {"pitch": "B2+Gb3", "duration": "8"},
    {"pitch": "Bb2+F3", "duration": "8"},
    {"pitch": "B2+Gb3", "duration": "8"},
    {"pitch": "C3+G3", "duration": "8"},
    {"pitch": "B2+Gb3", "duration": "8"},
    {"pitch": "F2+C3", "duration": "4"},
    {"pitch": "B2+Gb3", "duration": "4"}
]
```

- **Scale-degree sequence:** 1 -> 1 -> 1 -> 7 -> 1 -> b2 -> 1 -> b5 -> 1
- **Onset grid (16th notes, `|` = barline):** `X.......X.....X. | X.X.X.X.X...X...`

### Pedal / root center — 1 bar, repeats 16x (4/4)

```python
[
    {"pitch": "B1+Gb2", "duration": "1"}
]
```

- **Scale-degree sequence:** 1
- **Onset grid (16th notes, `|` = barline):** `X...............`
- **Coverage:** ~44% of bars sit on this drone — it's the root the riffs above move against, not a riff itself.

## Bass

Measured from the `Electric Bass (pick)` track, analyzed separately from the guitar
riff above so a bass line that diverges from it (different syncopation, a walking
passage, a fill) isn't averaged away into the combined harmony/register stats.

| Trait | Value |
|-------|-------|
| Range | B0–Db2 |
| Lowest open string | B0  (down-tuned) |
| Voicing | single-note line — 0 power-chord hits / 0 triads / 767 single notes |
| Structure | 258 bars, 72 unique (repetition 72%; top bar repeats 26x) |

### Bass riff A — 4 bars, repeats 11x (4/4)

```python
[
    {"pitch": "B0", "duration": "1"},
    {"pitch": "Gb1", "duration": "1"},
    {"pitch": "F1", "duration": "1"},
    {"pitch": "R", "duration": "1"}
]
```

- **Scale-degree sequence:** 1 -> 5 -> b5
- **Onset grid (16th notes, `|` = barline):** `X............... | X............... | X............... | ................`

### Bass riff B — 4 bars, repeats 5x (4/4)

```python
[
    {"pitch": "B0", "duration": "1"},
    {"pitch": "R", "duration": "2"},
    {"pitch": "F1", "duration": "4"},
    {"pitch": "B0", "duration": "4"},
    {"pitch": "R", "duration": "4"},
    {"pitch": "F1", "duration": "4"},
    {"pitch": "B0", "duration": "2"},
    {"pitch": "R", "duration": "2"},
    {"pitch": "C1", "duration": "4"},
    {"pitch": "C1", "duration": "8"},
    {"pitch": "Eb1", "duration": "8"}
]
```

- **Scale-degree sequence:** 1 -> b5 -> 1 -> b5 -> 1 -> b2 -> b2 -> 3
- **Onset grid (16th notes, `|` = barline):** `X............... | ........X...X... | ....X...X....... | ........X...X.X.`

### Bass pedal / root center — 1 bar, repeats 26x (4/4)

```python
[
    {"pitch": "B0", "duration": "1"}
]
```

- **Scale-degree sequence:** 1
- **Onset grid (16th notes, `|` = barline):** `X...............`
- **Coverage:** ~43% of bars sit on this drone.

## Rhythm & pacing

- **Note density:** 5.91 notes per bar.
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

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Distortion Guitar 1 | distortion-guitar | 30 | pitched |
| Distortion Guitar 2 | distortion-guitar | 30 | pitched |
| Electric Bass (pick) | electric-bass-pick | 34 | bass |
| Drums | drum kit (ch.10) | — | percussion |
