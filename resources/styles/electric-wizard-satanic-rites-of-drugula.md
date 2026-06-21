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
- **Most-used pitch classes:** Db, Ab, E, A, Gb, B.
- **Voicing:** power-chord driven — 825 power-chord hits vs 0 triads
  across 1361 single notes.
- **Interval color (within chords):** tritone ×1, minor-2nd
  ×5, fifth ×1212.

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

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Vocals - Alto Sax | alto-sax | 65 | pitched |
| Lead - Distortion Guitar | distortion-guitar | 30 | pitched |
| Rhythm  - Distortion Guitar | distortion-guitar | 30 | pitched |
| Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Percussion - Drums | acoustic-grand-piano | 0 | pitched |

## How to apply in this skill

- **Set `bpm`: 55** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in Db Phrygian.** Lean on Db, Ab, E, A, Gb, B.
- **Octave:** roots around **octave 0** (lowest note here is B0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor 16th as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (62%) — commit to a riff and cycle it; the top bar repeats 12x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
