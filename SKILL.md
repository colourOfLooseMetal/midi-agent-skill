---
name: midi-generation
description: Generate MIDI files with GM instruments and convert to WAV using A320U SoundFont
license: MIT
---

# MIDI Generation Skill

This skill provides pre-built TypeScript functions to generate MIDI files. **You MUST use the provided scripts in `skills/` directory. Do NOT write your own MIDI generation code.**

## Important Rules

1. **ALWAYS use the provided scripts** in `skills/` directory
2. **NEVER write custom Python or JavaScript code** for MIDI generation
3. **Read the script files first** to understand the API before using them
4. **Use the exact function signatures** defined in the scripts

## Available Scripts

### 1. `skills/generateMidi.ts` - Generate MIDI file

When the user wants to create a MIDI file, read `skills/generateMidi.ts` and use the `generateMidi` function.

```typescript
import { generateMidi } from "./skills/generateMidi.js";

const composition = {
  title: "My Song",
  bpm: 120,
  tracks: [
    {
      instrument: "acoustic-grand-piano",
      notes: [
        { pitch: "C4", duration: "4" },
        { pitch: "E4", duration: "4" }
      ]
    }
  ]
};

const midiPath = generateMidi(composition);
```

### 2. `skills/normalizeComposition.ts` - Validate input

Before generating MIDI, read `skills/normalizeComposition.ts` and use `normalizeComposition` to validate user input.

### 3. `skills/refineComposition.ts` - Adjust length

Read `skills/refineComposition.ts` and use `refineComposition` to ensure the composition has enough notes.

### 4. `skills/convertToWav.ts` - Convert to audio

When the user wants audio output, read `skills/convertToWav.ts` and use `convertToWav` with FluidSynth.

### 5. `types/gmInstruments.ts` - Instrument list

When selecting instruments, read `types/gmInstruments.ts` to see all 128 GM instruments compatible with A320U.sf2.

## Workflow

When the user requests music generation:

1. **Read `types/gmInstruments.ts`** to select appropriate instruments
2. **Read `skills/normalizeComposition.ts`** and call `normalizeComposition(input)`
3. **Read `skills/refineComposition.ts`** and call `refineComposition(composition)`
4. **Read `skills/generateMidi.ts`** and call `generateMidi(composition)`
5. If audio is requested, **read `skills/convertToWav.ts`** and call `convertToWav(midiPath)`

## Supported Instruments

Read `types/gmInstruments.ts` for the full list. Common aliases:

- `piano` → acoustic-grand-piano
- `guitar` → acoustic-guitar-nylon
- `bass` → acoustic-bass
- `strings` → string-ensemble-1
- `brass` → brass-section
- `sax` → alto-sax

## Prerequisites

- Node.js with TypeScript support
- For WAV: FluidSynth (`brew install fluidsynth`) + A320U.sf2 in `soundfonts/`

## Notes

- Output files are saved to `output/` directory
- All 128 GM instruments are supported
- Instrument names are case-insensitive
