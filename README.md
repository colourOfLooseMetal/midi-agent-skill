# 🎹 MIDI Generation Skill

**MIDI Generation Skill** is a custom **Agent Skill for Claude.ai** that enables AI agents to generate MIDI files from natural language music descriptions, with full **General MIDI instrument support** optimized for the **A320U.sf2 SoundFont**.

---

## 🚀 Features

- 🎼 **Generate MIDI from text prompts**
- 🎹 **128 GM instruments** - Full General MIDI support (A320U.sf2 compatible)
- 🔊 **WAV export** - Convert MIDI to audio using FluidSynth
- 🤖 **Claude Skills compatible** - Automatic skill invocation
- 🟦 **TypeScript implementation**

---

## 📦 Repository Structure

```
/
├─ skills/               # Skill implementation
│   ├─ generateMidi.ts       # MIDI file generation
│   ├─ convertToWav.ts       # MIDI to WAV conversion (FluidSynth)
│   ├─ normalizeComposition.ts
│   └─ refineComposition.ts
├─ types/
│   ├─ music.ts              # Composition types
│   └─ gmInstruments.ts      # 128 GM instruments list
├─ soundfonts/           # Place A320U.sf2 here
├─ output/               # Generated MIDI/WAV files
├─ SKILL.md              # Claude Skill definition
├─ package.json
└─ README.md
```

---

## 🎹 Supported Instruments

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

See `types/gmInstruments.ts` for the full list.

---

## 📘 Installation

### 1. Install dependencies

```bash
npm install
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

## 🚀 Usage with Claude.ai

### 1. Enable Skills in Claude

1. Open **Claude Settings**
2. Enable **Skills**
3. Upload this repository as a **ZIP file**
4. Turn the skill **ON**

### 2. Use the Skill

Simply ask Claude something related to music:

```text
Create a baroque-style piece with harpsichord and strings
```

```text
Generate a jazz composition with piano, bass, and saxophone
```

Claude will automatically:
1. Detect that the request matches this skill
2. Use the provided scripts in `skills/` directory
3. Generate MIDI with proper GM instruments
4. Optionally convert to WAV

---

## 📄 Composition Format

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
| `"1"` | Whole note |
| `"2"` | Half note |
| `"4"` | Quarter note |
| `"8"` | Eighth note |
| `"16"` | Sixteenth note |

---

## 🔧 API Reference

### `generateMidi(composition: Composition): string`

Generate a MIDI file from a Composition object.

- **Input**: Composition JSON with title, bpm, and tracks
- **Output**: Path to the generated `.mid` file

### `convertToWav(midiPath: string, options?: ConvertOptions): string`

Convert a MIDI file to WAV using FluidSynth and A320U.sf2.

- **Input**: Path to MIDI file
- **Output**: Path to the generated `.wav` file

### `normalizeComposition(input: any): Composition`

Validate and normalize user input into a proper Composition object.

### `refineComposition(composition: Composition): Composition`

Adjust composition length (ensures minimum 16 notes per track).

### `resolveInstrument(name: string): number`

Convert instrument name to GM program number (0-127).

---

## 📌 Example Prompts

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

## 🛠️ Development Notes

- `SKILL.md` defines **when and how Claude should use this skill**
- The `skills/` directory contains **pre-built scripts that Claude must use**
- Claude should **NOT write custom code** - it should use the provided functions
- All instruments are GM-compatible for A320U.sf2 playback

---

## 📜 License

MIT License

---

## 🔗 References

- [A320U SoundFont](https://musical-artifacts.com/artifacts/5906)
- [General MIDI Specification](https://www.midi.org/specifications/midi1-specifications/general-midi-specifications)
- [Claude Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [FluidSynth](https://www.fluidsynth.org/)
