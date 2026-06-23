# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A packaged **Claude Agent Skill** (`midi-generation`) that turns a structured
composition into a `.mid` file and optionally renders it to `.wav`. `SKILL.md` is
the skill contract; `README.md` is the user-facing doc. The skill is meant to be
**driven from Python**, not reimplemented.

## The golden rule

**Do not hand-write `midiutil`/MIDI code.** Build a composition **dict** and call
`skills.generate_midi.generate_midi_from_dict(dict)`. The script does all MIDI work
(channel assignment, program changes, pitch/duration parsing, file writing).
Composition itself — choosing notes, transposing to build harmony layers,
assembling sections — is just data prep you do *before* the call. `compose_stoner_doom.py`
at the repo root is a complete worked example of this pattern (defines a riff once,
transposes it into power-chord layers, calls the skill).

## Fast path: composition → MIDI → WAV

```bash
pip install -r requirements.txt        # just midiutil==1.2.1

python compose_stoner_doom.py          # build dict + generate -> output/<title>.mid
python render_wav.py 1.1               # render that .mid -> output/<title>.wav (arg = FluidSynth gain)
```

Minimal generate-from-scratch snippet (the only API you usually need):

```python
import sys; sys.path.insert(0, "<repo root>")
from skills.generate_midi import generate_midi_from_dict
path = generate_midi_from_dict({
    "title": "My Song", "bpm": 120,
    "tracks": [{"instrument": "distortion-guitar",
                "notes": [{"pitch": "C2", "duration": "2"}, {"pitch": "Gb2", "duration": "2"}]}],
})
```

Each `skills/*.py` also runs a demo via `python skills/<name>.py`. There is **no
test suite, linter, or build step** in this repo.

## Composition format

- `{"title": str, "bpm": int, "tracks": [{"instrument": <key>, "notes": [{"pitch": "C4", "duration": "4"}]}]}`
- Optional fields (all backward compatible): per-note `"velocity"` (1–127, default 100);
  `"time_signature"` (default `"4/4"`); `"tempo_map": [{"beat": n, "bpm": n}]`.
- **Pitch**: `C4` = middle C = MIDI 60. Sharps/flats: `F#5`, `Bb3`. Octave 2 ≈ low/"down-tuned".
  A pitch may be a **chord** — a `"+"`-joined string (`"C2+G2+C3"`) or a list — sounded as
  one event (see *Hard constraints*). A pitch of `R` (also `rest` / `-`, case-insensitive)
  is a **rest**: it advances time by its `duration` without sounding — true silence.
- **Duration tokens**: `1` whole, `2` half, `4` quarter, `8` eighth, `16`, `32`; dotted `d2`/`d4`/`d8`; triplets `T4`/`T8`. A bare number `N` means a 1/N note.
- **Instruments**: hyphenated GM names (`distortion-guitar`, `electric-bass-pick`,
  `rock-organ`, `acoustic-grand-piano`, ...) plus short aliases (`piano`, `bass`,
  `guitar`). Full table + aliases: `midi_types/gm_instruments.py`. Unknown names
  fuzzy-match, then fall back to piano (program 0).

## Hard constraints (these bite — design around them up front)

- **Real drums need the `drum-kit` track type.** Melodic tracks each get their own
  channel and **skip channel 9** (GM percussion). For a real kit, give a track the
  instrument `drum-kit` (also `percussion`/`kit`/...): the generator pins it to
  channel 9 and reads its note "pitches" as **drum names** — `kick`, `snare`,
  `hihat-open`/`-closed`, `crash`, `ride`, `tom-low`/`-mid`/`-high`, ... — mapped to
  GM kit notes (stack simultaneous hits like a chord, `"kick+crash"`; `R` still
  rests). See `midi_types/gm_percussion.py`. Note the older `drums` *alias* is
  separate and still resolves to the *pitched* `synth-drum` voice (program 118) — use
  `drum-kit`, not `drums`, for an actual kit. `compose_doom_procession.py` is the
  worked example (a half-time groove authored on a 16th grid). You can still build
  rhythm/weight from melodic instruments instead if you prefer.
- **Rests give true silence.** A pitch of `R` (`rest`/`-`) is a rest — it advances time by
  its `duration` without sounding, so you *can* drop an instrument out for a middle section
  and bring it back, or start a track with a rest to stage a late entrance (every track
  still starts its timeline at t=0; a leading rest just delays the first audible note).
  Non-rest notes in a track still play back-to-back with no implicit gaps. **A rest is only
  realized if a note follows it later in the same track** — a *trailing* rest is silently
  dropped (end-of-track lands on the last note, not the advanced cursor), so you can't use
  one to pad a track's length or add measured silence after its final hit.
- **Velocity is per-note now** (default 100 when omitted). Use `"velocity": 1–127` for
  accents/dynamics (ghost ~40, normal ~80, accent ~110, slam ~120) — no longer a flat wall.
- **Power chords go in ONE track** as a stacked-pitch chord (`"C2+G2+C3"` = root, +7 fifth,
  +12 octave; bass an octave below in its own track). A single track is no longer
  monophonic. Only use *parallel* tracks when voices differ in **instrument or rhythm**
  (e.g. a palm-muted chug vs. ringing slam chords). Keep chord tones spread across octaves
  so intervals never collapse to a same-octave semitone cluster (SKILL.md's dissonance rule).
  `compose_*.py` model this: each builds a root line and maps it to single-track power chords.
- **Output**: always `output/<sanitized-title>.mid`; the title is sanitized to
  `[A-Za-z0-9_-]` (spaces/punct → `_`), so two compositions with similar titles
  overwrite each other.

## WAV rendering / FluidSynth (machine-specific)

`skills/convert_to_wav.py` shells out to the **`fluidsynth` CLI** + `soundfonts/A320U.sf2`.

- **FluidSynth is not installed system-wide here** and is not in winget. A standalone
  build lives at `%LOCALAPPDATA%\fluidsynth\...\bin\fluidsynth.exe`. The skill calls
  the bare command `fluidsynth`, so that `bin` dir must be on `PATH` for the
  subprocess. `render_wav.py` auto-discovers it and prepends it to `PATH` — prefer
  that driver over calling `convert_to_wav` directly.
- **`convert_to_wav` defaults to `gain=0.5`, `reverb=False`, `chorus=False`.** For a
  dense multi-voice mix that default renders quiet (~−11 dBFS). Pass `gain≈1.1` for a
  hot, non-clipping ~−2 dBFS master (peak scales roughly linearly with gain).
- `A320U.sf2` is already present in `soundfonts/`.

## Architecture

Three layers, read in this order to get productive:

- `skills/` — the callable functions (the skill's behavior): `generate_midi.py`
  (dict → `.mid`), `convert_to_wav.py` (`.mid` → `.wav`), `normalize_composition.py`
  (coerce/clean messy input), `refine_composition.py` (pad/extend short tracks),
  `export_guitarpro.py` (dict → `.gp3`/`.gp4`/`.gp5`, viewable/playable in TuxGuitar
  or Guitar Pro — `export_guitarpro_from_dict(data, fmt="gp5")`; the reverse
  direction of the analysis pipeline below, sharing its optional PyGuitarPro
  dependency). It's not a real-tab fingering generator — it synthesizes a
  per-track tuning wide enough to place every pitch/chord used, so frets won't
  look idiomatic; only pitch and rhythm are guaranteed correct. Measures cut at
  the nominal time-signature length wherever that lands on a note boundary shared
  by every track (true by construction for this repo's bar-aligned `compose_*.py`
  drivers); a note that would straddle the boundary just makes that one bar
  longer instead of being split, so the file is always structurally valid.
- `midi_types/` — the data model: `music.py` (`Composition`/`Track`/`Note` dataclasses
  + dict round-tripping) and `gm_instruments.py` (the 128 GM name→program map +
  `resolve_instrument`).
- `resources/` — Markdown **music-theory references the skill reads on demand**, not
  code. SKILL.md maps task → file; read only the one you need. `resources/stoner-doom-composition.md`
  and `resources/groove-metal-composition.md` are worked genre guides that map theory
  directly onto this skill's primitives. `resources/styles/` holds **style cards** —
  measured profiles of real songs auto-generated by the analysis pipeline (below).
  Each style-card output folder also gets a single auto-generated `CLAUDE.md` (e.g.
  `resources/styles/doom/CLAUDE.md`) explaining what the cards' headings mean and how
  to apply them — that explanatory text lives there once instead of repeating in every
  card; the cards themselves hold only measured facts.
- `analysis/` — the **Guitar Pro → style card** pipeline (a process tool, not part of the
  packaged skill): `parse_guitarpro.py` (GP file → format-agnostic IR; PyGuitarPro for
  `.gp3/.gp4/.gp5`, stdlib zip+XML for modern `.gp`), `analyze.py` (IR → tempo/rhythm/
  harmony/voicing/structure/percussion features), `style_card.py` (features →
  `resources/styles/*.md` plus the per-folder `CLAUDE.md` guide via `write_guide`).
  Driven by `analyze_song.py` at the repo root. **PyGuitarPro** is an optional dependency
  (lazy-imported; only needed for `.gp3/.gp4/.gp5`). `.gpx` (GP6) is unsupported.

Composition data flow: `dict` → `Composition.from_dict` → `generate_midi` (midiutil) →
`output/*.mid` → `convert_to_wav` (FluidSynth + A320U) → `output/*.wav`.
Analysis data flow: `*.gp*` → `parse_guitarpro.load` (IR) → `analyze` (features) →
`style_card.write_card` → `resources/styles/*.md`.

## Repo-root drivers

`compose_stoner_doom.py`, `compose_groove_metal.py`, `render_wav.py`, and `analyze_song.py`
are working end-to-end examples — the canonical reference for "how do I actually drive this."
`compose_stoner_doom.py` shows the transpose-one-root-line pattern mapped to **single-track
power chords**, downbeat-accent velocities, and a `tempo_map` that drops into the "even
slower" climax (drone-heavy doom). `compose_groove_metal.py` shows the per-track-timeline
pattern and is the worked example for **rests** (cold open, a chordal slam that rests through
the chug and blooms on the release, a subtraction breakdown) plus **velocity contrast**
between the gated chug and the exploding slam chords. `analyze_song.py` drives the Guitar Pro
→ style card pipeline. None are part of the packaged skill itself.
