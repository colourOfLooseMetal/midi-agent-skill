---
name: midi-generation
description: Generate MIDI files with GM instruments and music theory. Use when creating music, composing melodies, or generating MIDI files.
license: MIT
---

# MIDI Generation Skill

Generate MIDI files with proper music theory. **Use the provided Python scripts in `skills/`. Do NOT write custom code.**

## Important Rules

1. **Use provided scripts** in `skills/` directory (Python)
2. **Never write custom Python/JS** for MIDI generation
3. **Install dependencies first**: `pip install midiutil`
4. **Consult music theory resources** when needed (see below)

## Quick Dissonance Rules

**Always follow these to avoid harsh sounds:**

1. **Never play notes 1 semitone apart** (C+C#, E+F, B+C)
2. **Bass plays root or fifth** of the chord
3. **Spread voices across octaves** (don't cluster)
4. **Each track uses different MIDI channel** (automatic)

---

## Music Theory Resources (Read When Needed)

**Only read the resource that matches your current task:**

| When you need... | Read this file |
|------------------|----------------|
| Scales, chords, intervals, cadences | [resources/music-theory.md](resources/music-theory.md) |
| Chord progressions by genre | [resources/chord-progressions.md](resources/chord-progressions.md) |
| Avoiding dissonance, voice spacing | [resources/voice-leading.md](resources/voice-leading.md) |
| **Classical/Baroque counterpoint** | [resources/counterpoint.md](resources/counterpoint.md) |
| Modes (Dorian, Phrygian, etc.) | [resources/modes-scales.md](resources/modes-scales.md) |
| Rhythm, time signatures, syncopation | [resources/rhythm-patterns.md](resources/rhythm-patterns.md) |
| Instrument ranges, combinations | [resources/orchestration.md](resources/orchestration.md) |
| **Real-song style cards** (measured from Guitar Pro tabs) | [resources/styles/](resources/styles/) |

### When to Read Each Resource

- **Pop/Rock song** → chord-progressions.md + voice-leading.md
- **Classical piece** → counterpoint.md + orchestration.md
- **Jazz composition** → modes-scales.md + chord-progressions.md
- **Film score** → orchestration.md + modes-scales.md
- **In a specific artist's/song's style** → read or generate a card in `resources/styles/`
  (see *Style cards from real songs* below)
- **Any composition** → Always check voice-leading.md for dissonance

---

## Workflow

1. **Install dependencies**: `pip install midiutil`
2. **Identify genre/style** → Select appropriate resources
3. **Read relevant theory** → Only the files you need
4. **Choose instruments** → See [midi_types/gm_instruments.py](midi_types/gm_instruments.py)
5. **Create composition JSON**
6. **Use scripts** to generate MIDI

## Python Scripts

| Script | Purpose |
|--------|---------|
| `skills/generate_midi.py` | Generate MIDI (auto-assigns channels per track) |
| `skills/normalize_composition.py` | Validate and normalize input |
| `skills/refine_composition.py` | Adjust length, extend tracks |
| `skills/convert_to_wav.py` | MIDI → WAV (requires FluidSynth) |

## Usage Example

```python
import sys
sys.path.insert(0, '/path/to/midi-skill')

from skills.generate_midi import generate_midi_from_dict

composition = {
    "title": "My Song",
    "bpm": 120,
    "tracks": [
        {
            "instrument": "acoustic-grand-piano",
            "notes": [
                {"pitch": "C4", "duration": "4"},
                {"pitch": "E4", "duration": "4"},
                {"pitch": "G4", "duration": "4"},
                {"pitch": "C5", "duration": "2"}
            ]
        },
        {
            "instrument": "acoustic-bass",
            "notes": [
                {"pitch": "C2", "duration": "2"},
                {"pitch": "G2", "duration": "2"}
            ]
        }
    ]
}

midi_path = generate_midi_from_dict(composition)
print(f"Generated: {midi_path}")
```

## Composition Format

```json
{
  "title": "My Song",
  "bpm": 120,
  "tracks": [
    {
      "instrument": "acoustic-grand-piano",
      "notes": [
        { "pitch": "C4", "duration": "4" },
        { "pitch": "E4", "duration": "4" }
      ]
    },
    {
      "instrument": "acoustic-bass",
      "notes": [
        { "pitch": "C2", "duration": "2" }
      ]
    }
  ]
}
```

## Chords, Dynamics, Tempo & Meter

These optional fields make output less mechanical. All are backward compatible —
omit them and you get the old behavior (mono notes, velocity 100, single tempo, 4/4).

- **Chords in ONE track.** A note's `pitch` may be a chord: a `"+"`-joined string
  (`"C2+G2+C3"`) or a list (`["C2","G2","C3"]`). All tones share one start and
  duration. **This is the right way to write power chords and triads** — *not*
  parallel tracks. Only use separate tracks when voices differ in *instrument or
  rhythm*. (A power chord = root, +7 fifth, +12 octave: `"C2+G2+C3"`.)
- **Per-note `velocity`** (1–127, default 100): `{"pitch":"C2","duration":"4","velocity":110}`.
  Use it for accents and dynamics — ghost ~40, normal ~80, accent ~110, slam ~120.
- **`tempo_map`**: a list of `{"beat": <offset>, "bpm": <n>}` for half-time feel,
  accel/rit, or per-section tempo shifts. `bpm` stays the initial tempo.
- **`time_signature`** (default `"4/4"`): written into the MIDI so the file carries
  bar structure. Supports odd meters (`"7/8"`, `"6/8"`).

```json
{
  "title": "Heavy Riff", "bpm": 70, "time_signature": "4/4",
  "tempo_map": [{"beat": 0, "bpm": 70}, {"beat": 32, "bpm": 58}],
  "tracks": [
    { "instrument": "distortion-guitar", "notes": [
      { "pitch": "C2+G2+C3", "duration": "2", "velocity": 115 },
      { "pitch": "R", "duration": "4" },
      { "pitch": "Gb2+Db3+Gb3", "duration": "2", "velocity": 100 }
    ]}
  ]
}
```

## Style cards from real songs

To compose in a real artist's or song's style, ground it in measured facts instead
of a generic template. Point the analysis pipeline at a **Guitar Pro** file (a far
richer source than MIDI — it has bars, a tempo map, exact durations, and tab
voicings):

```bash
pip install PyGuitarPro            # only for .gp3/.gp4/.gp5; modern .gp uses stdlib
python analyze_song.py "path/to/song.gp4"
```

This writes a **style card** to `resources/styles/<artist-title>.md` — tempo, key/
scale, meter, voicing, duration palette, repetition, and a "How to apply in this
skill" section. Read that card, then compose from its numbers. Supported inputs:
`.gp3/.gp4/.gp5/.gtp` (PyGuitarPro) and `.gp` (GP7/8, stdlib). `.gpx` (GP6) is not.

## Duration Notation

| Value | Note |
|-------|------|
| `1` | Whole note (4 beats) |
| `2` | Half note (2 beats) |
| `d2` | Dotted half (3 beats) |
| `4` | Quarter note (1 beat) |
| `d4` | Dotted quarter (1.5 beats) |
| `8` | Eighth note (0.5 beats) |
| `16` | Sixteenth note (0.25 beats) |

**Rests:** set a note's `"pitch"` to `"R"` (also `"rest"` or `"-"`) to produce a
**rest** — silence for the given `duration`. Use it to leave gaps, stage a late
entrance (a leading rest), or drop an instrument out mid-track and bring it back.
A rest is only realized if a note follows it later in the same track; a *trailing*
rest (none after it) is dropped, so it won't pad a track's length or add silence
after the last note.

## Instrument Aliases

| Alias | GM Instrument |
|-------|---------------|
| `piano` | acoustic-grand-piano |
| `guitar` | acoustic-guitar-nylon |
| `bass` | acoustic-bass |
| `strings` | string-ensemble-1 |
| `brass` | brass-section |
| `sax` | alto-sax |

Full list: [midi_types/gm_instruments.py](midi_types/gm_instruments.py)

## Notes

- Max 15 melodic tracks (MIDI channels 0-8, 10-15; ch.9 = drums)
- Output: `output/` directory
- WAV requires: FluidSynth + A320U.sf2 in `soundfonts/`
