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
- **Most-used pitch classes:** Bb, Db, F, Eb, Ab, C.
- **Voicing:** power-chord driven — 130 power-chord hits vs 0 triads
  across 610 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×276.

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

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Jus Oborn - Distortion Guitar | distortion-guitar | 30 | pitched |
| Jus Oborn - Overdriven Guitar | overdriven-guitar | 29 | pitched |
| Tim Bagshaw - Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Mark Greening - Drums 1 | acoustic-grand-piano | 0 | pitched |
| Mark Greening - Drums 2 | acoustic-grand-piano | 0 | pitched |

## How to apply in this skill

- **Set `bpm`: 122**. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in Bb natural minor (Aeolian).** Lean on Bb, Db, F, Eb, Ab, C.
- **Octave:** roots around **octave 0** (lowest note here is Bb0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (91%) — commit to a riff and cycle it; the top bar repeats 20x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
