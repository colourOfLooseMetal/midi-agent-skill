# MIDI Generation Skill

**MIDI Generation Skill** is a custom **Agent Skill for Claude.ai** that enables AI agents to generate MIDI files from natural language music descriptions, with full **General MIDI instrument support** optimized for the **A320U.sf2 SoundFont**.

---

## Features

- Generate MIDI from text prompts
- 128 GM instruments - Full General MIDI support (A320U.sf2 compatible)
- Chords in one track, per-note velocity, tempo maps, and time signatures
- WAV export - Convert MIDI to audio using FluidSynth
- Guitar Pro → style cards - analyze real `.gp3/.gp4/.gp5/.gp` tabs into reusable style guides
- Claude Skills compatible - Automatic skill invocation
- Python implementation using midiutil

---

## Repository Structure

```
/
├─ skills/                   # Skill implementation (Python)
│   ├─ generate_midi.py          # MIDI file generation
│   ├─ convert_to_wav.py         # MIDI to WAV conversion (FluidSynth)
│   ├─ normalize_composition.py  # Input validation
│   └─ refine_composition.py     # Adjust composition length
├─ midi_types/
│   ├─ music.py                  # Composition types
│   └─ gm_instruments.py         # 128 GM instruments list
├─ analysis/                 # Guitar Pro → style card pipeline
│   ├─ parse_guitarpro.py        # GP file → normalized IR
│   ├─ analyze.py                # IR → style features
│   └─ style_card.py             # features → resources/styles/*.md
├─ resources/                # Music theory references
│   ├─ music-theory.md
│   ├─ chord-progressions.md
│   ├─ voice-leading.md
│   ├─ counterpoint.md
│   ├─ modes-scales.md
│   ├─ rhythm-patterns.md
│   ├─ orchestration.md
│   └─ styles/                   # Auto-generated style cards from real songs
├─ soundfonts/               # Place A320U.sf2 here
├─ output/                   # Generated MIDI/WAV files
├─ analyze_song.py           # Driver: GP file → style card
├─ SKILL.md                  # Claude Skill definition
├─ requirements.txt          # Python dependencies
└─ README.md
```

---

## Supported Instruments

All 128 General MIDI instruments are supported. Common examples:

| Category | Instruments |
|----------|-------------|
| Piano | `acoustic-grand-piano`, `electric-piano-1`, `harpsichord` |
| Guitar | `acoustic-guitar-nylon`, `electric-guitar-clean`, `distortion-guitar` |
| Bass | `acoustic-bass`, `electric-bass-finger`, `synth-bass-1` |
| Strings | `violin`, `cello`, `string-ensemble-1`, `orchestral-harp` |
| Brass | `trumpet`, `trombone`, `french-horn`, `brass-section` |
| Woodwind | `flute`, `clarinet`, `oboe`, `alto-sax` |
| Synth | `lead-1-square`, `pad-1-new-age`, `synth-strings-1` |

Simple aliases like `piano`, `guitar`, `bass`, `strings`, `brass`, `sax` are also supported.

See `midi_types/gm_instruments.py` for the full list.

---

## Installation

### 1. Install Python dependencies

```bash
pip install midiutil
```

Or using requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Download SoundFont (for WAV conversion)

1. Download **A320U.sf2** from [Musical Artifacts](https://musical-artifacts.com/artifacts/5906)
2. Place it in `soundfonts/A320U.sf2`

### 3. Install FluidSynth (for WAV conversion)

```bash
# macOS
brew install fluidsynth

# Linux
apt-get install fluidsynth
```

---

## Usage with Claude.ai

### 1. Enable Skills in Claude

1. Open **Claude Settings**
2. Enable **Skills**
3. Upload this repository as a **ZIP file**
4. Turn the skill **ON**

### 2. Use the Skill

Simply ask Claude something related to music:

```text
Added the “midi-generation” skill. Use it to create grand classical music. I look forward to bright, grand, and beautiful melodies layered together. Once you have the MIDI, please convert it to WAV.
```

Claude will automatically:
1. Detect that the request matches this skill
2. Use the provided Python scripts in `skills/` directory
3. Generate MIDI with proper GM instruments (each track on different channel)
4. Optionally convert to WAV

### Demo



https://github.com/user-attachments/assets/34f018e5-6354-40a9-9426-15d2ccc7c39a



---

## Composition Format

The skill uses a structured JSON format:

```json
{
  "title": "My Song",
  "bpm": 120,
  "tracks": [
    {
      "instrument": "acoustic-grand-piano",
      "notes": [
        { "pitch": "C4", "duration": "4" },
        { "pitch": "E4", "duration": "4" },
        { "pitch": "G4", "duration": "2" }
      ]
    },
    {
      "instrument": "acoustic-bass",
      "notes": [
        { "pitch": "C2", "duration": "1" }
      ]
    }
  ]
}
```

### Note Duration Values

| Value | Duration |
|-------|----------|
| `"1"` | Whole note (4 beats) |
| `"2"` | Half note (2 beats) |
| `"d2"` | Dotted half (3 beats) |
| `"4"` | Quarter note (1 beat) |
| `"d4"` | Dotted quarter (1.5 beats) |
| `"8"` | Eighth note (0.5 beats) |
| `"16"` | Sixteenth note (0.25 beats) |

**Rests:** a note with `"pitch": "R"` (also `"rest"` or `"-"`) is a **rest** — silence
for its `duration`. Use it to leave gaps, delay a track's entrance, or drop an
instrument out and bring it back.

### Chords, dynamics, tempo & meter (optional)

All optional and backward compatible — omit them for the classic behavior.

| Field | Where | Example | Effect |
|-------|-------|---------|--------|
| Chord `pitch` | per note | `{ "pitch": "C2+G2+C3", "duration": "4" }` | stacked notes sounded together in one track (power chords/triads) |
| `velocity` | per note | `{ "pitch": "C2", "duration": "4", "velocity": 110 }` | accents/dynamics (1–127, default 100) |
| `tempo_map` | composition | `"tempo_map": [{ "beat": 0, "bpm": 120 }, { "beat": 32, "bpm": 96 }]` | tempo changes (half-time, accel/rit) |
| `time_signature` | composition | `"time_signature": "7/8"` | written into the MIDI as bar structure |

### Style cards from real songs

Analyze a Guitar Pro tab into a reusable style card under `resources/styles/`:

```bash
pip install PyGuitarPro                    # for .gp3/.gp4/.gp5; modern .gp uses stdlib
python analyze_song.py "path/to/song.gp4"  # -> resources/styles/<artist-title>.md
```

The card reports measured tempo, key/scale, meter, voicing, duration palette, and
repetition, with a "How to apply in this skill" section. `.gpx` (GP6) is not supported.

---

## API Reference

### `generate_midi(composition: Composition) -> str`

Generate a MIDI file from a Composition object.

- **Input**: Composition object with title, bpm, and tracks
- **Output**: Path to the generated `.mid` file

### `generate_midi_from_dict(data: dict) -> str`

Generate a MIDI file from a dictionary.

- **Input**: Dictionary with title, bpm, and tracks
- **Output**: Path to the generated `.mid` file

### `convert_to_wav(midi_path: str, options: ConvertOptions) -> str`

Convert a MIDI file to WAV using FluidSynth and A320U.sf2.

- **Input**: Path to MIDI file
- **Output**: Path to the generated `.wav` file

### `normalize_composition(data: Any) -> Composition`

Validate and normalize user input into a proper Composition object.

### `refine_composition(composition: Composition, min_notes: int) -> Composition`

Adjust composition length (ensures minimum notes per track).

### `resolve_instrument(name: str) -> int`

Convert instrument name to GM program number (0-127).

---

## Example Prompts

```text
Create a calm ambient piece with pad synths and strings
```

```text
Generate a rock song with distortion guitar and drums at 140 BPM
```

```text
Compose a classical piece with violin, cello, and harpsichord
```

---

## Development Notes

- `SKILL.md` defines **when and how Claude should use this skill**
- The `skills/` directory contains **pre-built Python scripts that Claude must use**
- Claude should **NOT write custom code** - it should use the provided functions
- All instruments are GM-compatible for A320U.sf2 playback
- **Each track is assigned to a different MIDI channel** for proper multi-instrument playback

---

## License

MIT License

See LICENSE.txt for details including third-party licenses.

---

## References

- [A320U SoundFont](https://musical-artifacts.com/artifacts/5906)
- [General MIDI Specification](https://www.midi.org/specifications/midi1-specifications/general-midi-specifications)
- [Claude Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [FluidSynth](https://www.fluidsynth.org/)
- [MIDIUtil](https://github.com/MarkCWirt/MIDIUtil)
