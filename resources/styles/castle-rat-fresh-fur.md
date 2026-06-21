# Style Card — Castle Rat – Fresh Fur

*Auto-generated from `gp` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
| Tempo | 81 BPM (half-time feel) |
| Tempo changes | 124 BPM @ beat 7.0, 77 BPM @ beat 15.0, 124 BPM @ beat 35.0, 76 BPM @ beat 51.0, 124 BPM @ beat 71.0, 74 BPM @ beat 87.0, 64 BPM @ beat 94.0, 74 BPM @ beat 95.0, 125 BPM @ beat 97.0, 120 BPM @ beat 106.0 |
| Key / scale | C Phrygian  (confidence 99%) |
| Main time signature | 4/4 |
| Other meters | 6/8, 2/4, 1/4, 3/4 |
| Lowest note | C1 |
| Lowest open string | None |
| Notes per bar | 11.97 |
| Voicing | power-chord driven |
| Structure | 106 bars, 37 unique (repetition 65%; top bar repeats 10x) |

## Harmony

- **Key / scale:** C Phrygian (confidence 99%).
- **Most-used pitch classes:** C, G, Db, F, Eb, Ab.
- **Voicing:** power-chord driven — 281 power-chord hits vs 0 triads
  across 877 single notes.
- **Interval color (within chords):** tritone ×0, minor-2nd
  ×2, fifth ×406.

## Rhythm & pacing

- **Note density:** 11.97 notes per bar.
- **Tempo:** 81 BPM (half-time feel); changes: 124 BPM @ beat 7.0, 77 BPM @ beat 15.0, 124 BPM @ beat 35.0, 76 BPM @ beat 51.0, 124 BPM @ beat 71.0, 74 BPM @ beat 87.0, 64 BPM @ beat 94.0, 74 BPM @ beat 95.0, 125 BPM @ beat 97.0, 120 BPM @ beat 106.0.
- **Dominant durations:** eighth (374), quarter (267), dotted-quarter (235), quarter-triplet (219).

| Duration | Count |
|----------|-------|
| eighth | 374 |
| quarter | 267 |
| dotted-quarter | 235 |
| quarter-triplet | 219 |
| eighth-triplet | 99 |
| half | 55 |
| 16th | 45 |
| 32nd | 21 |
| 16th-triplet | 12 |
| dotted-half | 9 |
| whole | 5 |
| dotted-eighth | 4 |

## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
| The Rat Queen - Vocals - Voice Oohs | voice-oohs | 53 | pitched |
| The Rat Queen - Guitar - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Count - Lead - Distortion Guitar | distortion-guitar | 30 | pitched |
| The Plague Doctor - Electric Bass (pick) | electric-bass-pick | 34 | pitched |
| The Druid - Drums | acoustic-grand-piano | 0 | pitched |

## How to apply in this skill

- **Set `bpm`: 81** and feel it in half-time. Use a `tempo_map` to reproduce the tempo moves listed above.
- **`time_signature`: `4/4`** (watch for 6/8, 2/4, 1/4, 3/4 sections).
- **Write in C Phrygian.** Lean on C, G, Db, F, Eb, Ab.
- **Octave:** roots around **octave 1** (lowest note here is C1).
- **Voicing:** this is power-chord driven. Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.
- **Duration palette:** favor eighth as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive (65%) — commit to a riff and cycle it; the top bar repeats 10x here.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
