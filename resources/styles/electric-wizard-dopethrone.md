# Style Card — Electric Wizard – Dopethrone

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 55 BPM (half-time feel) |
| Tempo changes | 57 BPM @ beat 5.0, 56 BPM @ beat 9.0, 55 BPM @ beat 11.0, 56 BPM @ beat 13.0, 57 BPM @ beat 14.0, 58 BPM @ beat 15.0, 59 BPM @ beat 16.0, 60 BPM @ beat 17.0, 59 BPM @ beat 21.0, 60 BPM @ beat 41.0, 48 BPM @ beat 99.0 |
| Key / scale | Bb minor blues  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | none |
| Lowest note | Bb0 |
| Lowest open string | None |
| Notes per bar | 17.36 |
| Voicing | power-chord driven |
| Structure | 129 bars, 12 unique (repetition 91%; top bar repeats 24x) |

## Harmony

- **Key / scale:** Bb minor blues (confidence 100%).
- **Most-used pitch classes:** Bb, Eb, E, Db, F, Ab.
- **Voicing:** power-chord driven — 204 power-chord hits vs 0 triads
  across 2200 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×236.

## Rhythm & pacing

- **Note density:** 17.36 notes per bar.
- **Tempo:** 55 BPM (half-time feel); changes: 57 BPM @ beat 5.0, 56 BPM @ beat 9.0, 55 BPM @ beat 11.0, 56 BPM @ beat 13.0, 57 BPM @ beat 14.0, 58 BPM @ beat 15.0, 59 BPM @ beat 16.0, 60 BPM @ beat 17.0, 59 BPM @ beat 21.0, 60 BPM @ beat 41.0, 48 BPM @ beat 99.0.
- **Dominant durations:** 16th (1815), eighth (335), 32nd (194), dotted-eighth (129).

| Duration | Count |
|----------|-------|
| 16th | 1815 |
| eighth | 335 |
| 32nd | 194 |
| dotted-eighth | 129 |
| quarter | 95 |
| whole | 12 |
| 16th-triplet | 7 |
| dotted-16th | 2 |
| dotted-quarter | 1 |
| eighth-triplet | 1 |

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Jus Oborn | Epipiphone SG G-400 (Lead) - Distortion Guitar | distortion-guitar | 30 | pitched |
| Jus Oborn | Epipiphone SG G-400 (Rhythm) - Distortion Guitar | distortion-guitar | 30 | pitched |
| Overdriven Bass Effect - Overdriven Guitar | overdriven-guitar | 29 | pitched |
| Tim Bagshaw | Rickenbacker 4001  - Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Mark Greening | Yamaha Stage Custom (Kit) - Drums | acoustic-grand-piano | 0 | pitched |

## How to apply in this skill

- **Set `bpm`: 55** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in Bb minor blues.** Lean on Bb, Eb, E, Db, F, Ab.
- **Octave:** roots around **octave 0** (lowest note here is Bb0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor 16th as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (91%) — commit to a riff and cycle it; the top bar repeats 24x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
