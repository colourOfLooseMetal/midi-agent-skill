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
- **Most-used pitch classes:** B, Gb, A, C, E, Bb.
- **Voicing:** power-chord driven — 105 power-chord hits vs 0 triads
  across 1418 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×731.

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
- **Write in B Phrygian.** Lean on B, Gb, A, C, E, Bb.
- **Octave:** roots around **octave 0** (lowest note here is B0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (93%) — commit to a riff and cycle it; the top bar repeats 79x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
