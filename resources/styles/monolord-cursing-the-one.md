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
- **Most-used pitch classes:** B, Gb, F, C, Bb, E.
- **Voicing:** power-chord driven — 253 power-chord hits vs 0 triads
  across 1003 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×710.

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

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Distortion Guitar 1 | distortion-guitar | 30 | pitched |
| Distortion Guitar 2 | distortion-guitar | 30 | pitched |
| Electric Bass (pick) | electric-bass-pick | 34 | pitched |
| Drums | acoustic-grand-piano | 0 | pitched |

## How to apply in this skill

- **Set `bpm`: 125**. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`** (watch for 3/4, 2/4, 7/4, 5/4, 6/4 sections).
- **Write in B minor blues.** Lean on B, Gb, F, C, Bb, E.
- **Octave:** roots around **octave 0** (lowest note here is B0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (73%) — commit to a riff and cycle it; the top bar repeats 35x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
