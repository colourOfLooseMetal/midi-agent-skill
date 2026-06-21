# Style Card — Electric Wizard – Funeralopolis

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 84 BPM (half-time feel) |
| Tempo changes | 86 BPM @ beat 8.0, 87 BPM @ beat 12.0, 88 BPM @ beat 24.0, 84 BPM @ beat 28.0, 85 BPM @ beat 32.0, 83 BPM @ beat 39.0, 85 BPM @ beat 50.0, 86 BPM @ beat 56.0, 87 BPM @ beat 60.0, 84 BPM @ beat 64.0, 91 BPM @ beat 66.0, 88 BPM @ beat 80.0, 89 BPM @ beat 84.0, 90 BPM @ beat 96.0, 82 BPM @ beat 103.0, 121 BPM @ beat 104.0, 122 BPM @ beat 112.0, 124 BPM @ beat 115.0, 126 BPM @ beat 123.0, 125 BPM @ beat 128.0, 124 BPM @ beat 136.0, 123 BPM @ beat 168.0, 125 BPM @ beat 175.0, 127 BPM @ beat 183.0, 128 BPM @ beat 208.0, 105 BPM @ beat 215.0 |
| Key / scale | Bb Phrygian  (confidence 100%) |
| Main time signature | 4/4 |
| Other meters | none |
| Lowest note | Bb0 |
| Lowest open string | None |
| Notes per bar | 18.4 |
| Voicing | power-chord driven |
| Structure | 223 bars, 47 unique (repetition 79%; top bar repeats 30x) |

## Harmony

- **Key / scale:** Bb Phrygian (confidence 100%).
- **Most-used pitch classes:** Bb, Eb, F, Gb, Db, E.
- **Voicing:** power-chord driven — 756 power-chord hits vs 0 triads
  across 2484 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×0, fifth ×1575.

## Rhythm & pacing

- **Note density:** 18.4 notes per bar.
- **Tempo:** 84 BPM (half-time feel); changes: 86 BPM @ beat 8.0, 87 BPM @ beat 12.0, 88 BPM @ beat 24.0, 84 BPM @ beat 28.0, 85 BPM @ beat 32.0, 83 BPM @ beat 39.0, 85 BPM @ beat 50.0, 86 BPM @ beat 56.0, 87 BPM @ beat 60.0, 84 BPM @ beat 64.0, 91 BPM @ beat 66.0, 88 BPM @ beat 80.0, 89 BPM @ beat 84.0, 90 BPM @ beat 96.0, 82 BPM @ beat 103.0, 121 BPM @ beat 104.0, 122 BPM @ beat 112.0, 124 BPM @ beat 115.0, 126 BPM @ beat 123.0, 125 BPM @ beat 128.0, 124 BPM @ beat 136.0, 123 BPM @ beat 168.0, 125 BPM @ beat 175.0, 127 BPM @ beat 183.0, 128 BPM @ beat 208.0, 105 BPM @ beat 215.0.
- **Dominant durations:** eighth-triplet (1774), quarter (669), quarter-triplet (633), eighth (577).

| Duration | Count |
|----------|-------|
| eighth-triplet | 1774 |
| quarter | 669 |
| quarter-triplet | 633 |
| eighth | 577 |
| dotted-quarter | 219 |
| half | 123 |
| whole | 68 |
| 16th-triplet | 28 |
| 32nd | 12 |
| dotted-half | 4 |

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| Jus Oborn - Electric Guitar (jazz) | electric-guitar-jazz | 26 | pitched |
| Jus Oborn (left) - Distortion Guitar | distortion-guitar | 30 | pitched |
| Jus Oborn (Overdriven intro) - Overdriven Guitar | overdriven-guitar | 29 | pitched |
| Jus Oborn (right) - Distortion Guitar | distortion-guitar | 30 | pitched |
| Tim Bagshaw - Electric Bass (finger) | electric-bass-finger | 33 | pitched |
| Mark Greening - Drums | acoustic-grand-piano | 0 | pitched |

## How to apply in this skill

- **Set `bpm`: 84** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`**.
- **Write in Bb Phrygian.** Lean on Bb, Eb, F, Gb, Db, E.
- **Octave:** roots around **octave 0** (lowest note here is Bb0).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth-triplet as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (79%) — commit to a riff and cycle it; the top bar repeats 30x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
