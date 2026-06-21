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
- **Most-used pitch classes:** Eb, Bb, B, Ab, Gb, E.
- **Voicing:** power-chord driven — 256 power-chord hits vs 0 triads
  across 1261 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×675.

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

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Jus Oborn - Distortion Guitar 1 | distortion-guitar | 30 | pitched |
| Jus Oborn - Distortion Guitar 2 | distortion-guitar | 30 | pitched |
| Tim Bagshaw-bass effect - Overdriven Guitar | overdriven-guitar | 29 | pitched |
| Tim Bagshaw - Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Mark Greening - Drums | acoustic-grand-piano | 0 | pitched |

## How to apply in this skill

- **Set `bpm`: 74** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in Eb Phrygian.** Lean on Eb, Bb, B, Ab, Gb, E.
- **Octave:** roots around **octave 0** (lowest note here is Bb0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (92%) — commit to a riff and cycle it; the top bar repeats 22x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
