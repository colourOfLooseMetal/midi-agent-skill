# Style Card — Castle Rat – WIZARD

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 73 BPM (half-time feel) |
| Tempo changes | 53 BPM @ beat 7.0, 68 BPM @ beat 7.0, 77 BPM @ beat 9.0, 154 BPM @ beat 37.0, 77 BPM @ beat 61.0, 154 BPM @ beat 98.0 |
| Key / scale | C Phrygian  (confidence 90%) |
| Main time signature | 4/4 |
| Other meters | 2/4, 7/8 |
| Lowest note | C1 |
| Lowest open string | None |
| Notes per bar | 24.32 |
| Voicing | power-chord driven |
| Structure | 117 bars, 49 unique (repetition 58%; top bar repeats 19x) |

## Harmony

- **Key / scale:** C Phrygian (confidence 90%).
- **Most-used pitch classes:** G, C, Bb, Ab, F, Eb.
- **Voicing:** power-chord driven — 215 power-chord hits vs 0 triads
  across 2326 single notes.
- **Interval color (within chords):** tritone ×3, minor-2nd
  ×1, fifth ×532.

## Rhythm & pacing

- **Note density:** 24.32 notes per bar.
- **Tempo:** 73 BPM (half-time feel); changes: 53 BPM @ beat 7.0, 68 BPM @ beat 7.0, 77 BPM @ beat 9.0, 154 BPM @ beat 37.0, 77 BPM @ beat 61.0, 154 BPM @ beat 98.0.
- **Dominant durations:** 16th (917), eighth (747), eighth-triplet (395), quarter (390).

| Duration | Count |
|----------|-------|
| 16th | 917 |
| eighth | 747 |
| eighth-triplet | 395 |
| quarter | 390 |
| 16th-triplet | 159 |
| whole | 158 |
| half | 102 |
| dotted-half | 22 |
| dotted-eighth | 18 |
| dotted-quarter | 17 |
| 32nd | 14 |
| dotted-16th | 7 |
| quarter-triplet | 3 |

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| The Rat Queen - Vocals - Voice Oohs | voice-oohs | 53 | pitched |
| The Rat Queen - Rhythm Guitar - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Rhythm - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Rat Queen - Lead Guitar - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Lead - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Solo Harmony - Distortion Guitar | distortion-guitar | 30 | pitched |
| Drawbar Organ | drawbar-organ | 16 | pitched |
| The Plague Doctor - Electric Bass (pick) | electric-bass-pick | 34 | pitched |
| The Druid - Drums | acoustic-grand-piano | 0 | pitched |

## How to apply in this skill

- **Set `bpm`: 73** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`** (watch for 2/4, 7/8 sections).
- **Write in C Phrygian.** Lean on G, C, Bb, Ab, F, Eb.
- **Octave:** roots around **octave 1** (lowest note here is C1).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor 16th as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (58%) — commit to a riff and cycle it; the top bar repeats 19x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
