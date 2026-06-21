# Style Card — Fu Manchu – Godzilla

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 69 BPM (half-time feel) |
| Tempo changes | 73 BPM @ beat 20.0 |
| Key / scale | F Dorian  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | none |
| Lowest note | Eb1 |
| Lowest open string | None |
| Notes per bar | 16.63 |
| Voicing | power-chord driven |
| Structure | 83 bars, 29 unique (repetition 65%; top bar repeats 11x) |

## Harmony

- **Key / scale:** F Dorian (confidence 100%).
- **Most-used pitch classes:** F, Eb, C, Bb, Ab, D.
- **Voicing:** power-chord driven — 187 power-chord hits vs 0 triads
  across 936 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×444.

## Rhythm & pacing

- **Note density:** 16.63 notes per bar.
- **Tempo:** 69 BPM (half-time feel); changes: 73 BPM @ beat 20.0.
- **Dominant durations:** eighth (830), 16th (325), quarter (217), 16th-triplet (31).

| Duration | Count |
|----------|-------|
| eighth | 830 |
| 16th | 325 |
| quarter | 217 |
| 16th-triplet | 31 |
| half | 16 |
| eighth-triplet | 13 |
| 32nd | 12 |
| dotted-eighth | 12 |
| whole | 11 |
| dotted-quarter | 2 |
| dotted-16th | 2 |
| dotted-half | 1 |

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Distortion Guitar 1 | distortion-guitar | 30 | pitched |
| Distortion Guitar 2 | distortion-guitar | 30 | pitched |
| Electric Bass (pick) | electric-bass-pick | 34 | pitched |
| Drums | acoustic-grand-piano | 0 | pitched |

## How to apply in this skill

- **Set `bpm`: 69** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in F Dorian.** Lean on F, Eb, C, Bb, Ab, D.
- **Octave:** roots around **octave 1** (lowest note here is Eb1).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (65%) — commit to a riff and cycle it; the top bar repeats 11x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
