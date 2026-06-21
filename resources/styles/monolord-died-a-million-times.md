# Style Card — Monolord – Died A Million Times

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 110 BPM |
| Tempo changes | 107 BPM @ beat 13.0, 105 BPM @ beat 17.0 |
| Key / scale | B Phrygian  (confidence 100%) |
| Main time signature | 2/1 |
| Other meters | 4/4, 1/1, 3/1 |
| Lowest note | B0 |
| Lowest open string | None |
| Notes per bar | 2.12 |
| Voicing | power-chord driven |
| Structure | 54 bars, 24 unique (repetition 56%; top bar repeats 12x) |

## Harmony

- **Key / scale:** B Phrygian (confidence 100%).
- **Most-used pitch classes:** B, Gb, C, D, Db, G.
- **Voicing:** power-chord driven — 108 power-chord hits vs 0 triads
  across 253 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×339.

## Rhythm & pacing

- **Note density:** 2.12 notes per bar.
- **Tempo:** 110 BPM; changes: 107 BPM @ beat 13.0, 105 BPM @ beat 17.0.
- **Dominant durations:** eighth (321), quarter (87), whole (86), half (53).

| Duration | Count |
|----------|-------|
| eighth | 321 |
| quarter | 87 |
| whole | 86 |
| half | 53 |
| dotted-eighth | 28 |
| 16th | 18 |
| dotted-quarter | 18 |
| 32nd | 2 |
| dotted-half | 1 |

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Thomas V Jäger - Distortion Guitar | distortion-guitar | 30 | pitched |
| Thomas V Jäger - Electric Guitar (clean) | electric-guitar-clean | 27 | pitched |
| Mika Häkki - Electric Bass (finger) | electric-bass-finger | 33 | pitched |

## How to apply in this skill

- **Set `bpm`: 110**. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `2/1`** (watch for 4/4, 1/1, 3/1 sections).
- **Write in B Phrygian.** Lean on B, Gb, C, D, Db, G.
- **Octave:** roots around **octave 0** (lowest note here is B0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (56%) — commit to a riff and cycle it; the top bar repeats 12x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
