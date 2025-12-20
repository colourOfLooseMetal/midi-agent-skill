---
name: midi-generation
description: Generate MIDI files locally from structured music descriptions
license: MIT
---

# MIDI Generation Skill

This skill enables Claude to generate MIDI files locally from structured music descriptions.

## Capabilities

- Normalize a Composition JSON
- Refine musical length automatically
- Generate `.mid` files without external APIs

## Intended Usage

Claude should:
1. Interpret the user's musical request
2. Construct a Composition JSON
3. Call normalizeComposition
4. Call refineComposition
5. Call generateMidi

## Notes

- All execution is local
- No external API or billing required