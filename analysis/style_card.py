#!/usr/bin/env python3
"""
Render a feature dict (from analyze.py) into a markdown "style card" and write it
to resources/styles/<slug>.md.

A style card is the reusable artifact of this whole pipeline: measured facts about
a real track plus a "How to apply in this skill" section that maps those facts onto
the skill's own primitives (BPM, tempo_map, time_signature, low-octave roots,
single-track power chords, duration palette, key/scale). The composition step reads
a style card the same way it reads resources/*.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from midi_types.gm_instruments import GM_INSTRUMENTS

_PROGRAM_TO_NAME = {v: k for k, v in GM_INSTRUMENTS.items()}

REPO = Path(__file__).resolve().parent.parent
STYLES_DIR = REPO / "resources" / "styles"


def _slug(artist: str, title: str) -> str:
    raw = f"{artist}-{title}".strip("-") if artist else title
    return re.sub(r"[^a-zA-Z0-9]+", "-", raw).strip("-").lower() or "untitled"


def _gm_name(program: int) -> str:
    return _PROGRAM_TO_NAME.get(program, f"program-{program}")


def _table(rows):
    return "\n".join(f"| {k} | {v} |" for k, v in rows)


def _render_riffs(riffs: List[Dict], key_str: str) -> str:
    if not riffs:
        return ""
    labels = "ABCDEF"
    blocks = []
    for i, r in enumerate(riffs):
        notes_py = ",\n".join(
            f'    {{"pitch": "{e["pitch"]}", "duration": "{e["duration"]}"}}'
            for e in r["transcription"]
        )
        degree_line = r["degree_sequence"] or "n/a"
        blocks.append(f"""### Riff {labels[i]} — repeats {r['repeats']}x ({r['time_sig']})

```python
[
{notes_py}
]
```

- **Scale-degree sequence:** {degree_line}
- **Onset grid (16th notes):** `{r['onset_grid']}`""")
    body = "\n\n".join(blocks)
    return f"""
## Riff transcription

The {len(riffs)} most-repeated distinct bar(s) on the representative track, transcribed
verbatim in this skill's note syntax (paste the list straight into a track's `notes`
array) with scale degrees relative to {key_str}. Onset grids share the percussion
grid's 16th-note convention below, so the two can be lined up by eye.

{body}

**How to apply in this skill:** these are real riffs, not statistics — copy one in,
transpose only the root to change key, and keep the scale-degree sequence intact to
stay in style. Compare each onset grid against the kick/snare grid in **Percussion**
to see where the riff should lock to the beat.
"""


def _render_percussion(perc: Dict | None) -> str:
    if not perc:
        return ""
    voice_rows = "\n".join(
        f"| {cat} | {n} | {perc['voice_percentages'][cat]}% |"
        for cat, n in perc["voice_counts"].items()
    )
    grid = "\n".join(f"{cat}: {pattern}" for cat, pattern in perc["dominant_pattern"].items())
    return f"""
## Percussion

| Voice | Hits | % |
|-------|------|---|
{voice_rows}

- **Density:** {perc['hits_per_bar']} hits/bar.
- **Pattern:** {perc['pattern_bars']} bars, {perc['pattern_unique_bars']} unique
  (repetition {perc['pattern_repetition_ratio']:.0%}; top bar repeats {perc['pattern_top_repeats']}x).
- **Fills:** tom hits in {perc['tom_fill_ratio']:.0%} of bars.

Dominant bar pattern (16th-note grid, `{perc['track_name']}`):

```
{grid}
```

**How to apply in this skill:** this skill has no real GM drum kit (channel 9 is
skipped — see `CLAUDE.md`). Use this pattern as a guide rail: lock chug/palm-mute hits
on the guitar/bass track to where `kick` lands above, place chordal accents where
`snare`/`crash` lands, and let the hi-hat density above suggest your eighth/sixteenth
subdivision choice.
"""


def render(features: Dict) -> str:
    h = features["harmony"]
    key = h.get("key_estimate") or {}
    tempo = features["tempo"]
    rhythm = features["rhythm"]
    reg = features["register"]
    struct = features["structure"]

    artist = features.get("artist") or "Unknown"
    title = features.get("title") or "Untitled"

    key_str = f"{key.get('tonic', '?')} {key.get('scale', '?')}" if key else "unknown"
    conf = f"{key.get('confidence', 0):.0%}" if key else "n/a"
    main_ts = next(iter(features["time_signatures"]), "4/4")

    # top durations and pitch classes for the prose
    durs = list(rhythm["duration_histogram"].items())
    top_durs = ", ".join(f"{lbl} ({n})" for lbl, n in durs[:4])
    pcs = list(h["pitch_class_weights"].items())
    degrees = h.get("pitch_class_degrees") or {}
    top_pcs = ", ".join(f"{degrees[pc]} ({pc})" if pc in degrees else pc for pc, _ in pcs[:6])

    chord_total = h["power_chords"] + h["triads"]
    voicing = ("power-chord driven" if h["power_chords"] > h["triads"]
               else "triad/extended-chord driven" if chord_total else "mostly single-note lines")

    tempo_changes = ("none" if not tempo["changes"]
                     else ", ".join(f"{bpm:.0f} BPM @ beat {beat}" for beat, bpm in tempo["changes"]))

    snapshot = _table([
        ("Tempo", f"{tempo['initial_bpm']:.0f} BPM"
                  + (" (half-time feel)" if tempo["half_time_feel"] else "")),
        ("Tempo changes", tempo_changes),
        ("Key / scale", f"{key_str}  (confidence {conf})"),
        ("Main time signature", main_ts),
        ("Other meters", ", ".join(k for k in features["time_signatures"] if k != main_ts) or "none"),
        ("Lowest note", reg["lowest_note"] or "n/a"),
        ("Lowest open string", f"{reg['lowest_open_string']}"
                               + ("  (down-tuned)" if reg["down_tuned"] else "")),
        ("Notes per bar", rhythm["notes_per_bar"]),
        ("Voicing", voicing),
        ("Structure", f"{struct['bars']} bars, {struct['unique_bars']} unique "
                      f"(repetition {struct['repetition_ratio']:.0%}; "
                      f"top bar repeats {struct['most_repeated_bar_count']}x)"),
    ])

    instruments = "\n".join(
        f"| {t['name']} | {'drum kit (ch.10)' if t['percussion'] else _gm_name(t['gm_program'])} | "
        f"{'—' if t['percussion'] else t['gm_program']} | "
        f"{'percussion' if t['percussion'] else 'pitched'} |"
        for t in features["instrumentation"]
    )

    duration_rows = "\n".join(f"| {lbl} | {n} |" for lbl, n in durs)

    riffs_section = _render_riffs(features.get("riffs") or [], key_str)
    percussion_section = _render_percussion(features.get("percussion"))

    # Suggested octave for roots from the lowest note
    low = reg["lowest_note"] or "C2"
    low_oct = re.sub(r"[^0-9-]", "", low) or "2"

    apply_bpm = int(round(tempo["initial_bpm"]))

    return f"""# Style Card — {artist} – {title}

*Auto-generated from `{features['format']}` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track, plus how to reproduce the style
with this skill's primitives. Treat the numbers as a starting point, not a cage.*

## Snapshot

| Trait | Value |
|-------|-------|
{snapshot}

## Harmony

- **Key / scale:** {key_str} (confidence {conf}).
- **Most-used pitch classes:** {top_pcs}.
- **Voicing:** {voicing} — {h['power_chords']} power-chord hits vs {h['triads']} triads
  across {h['single_notes']} single notes.
- **Interval color (within chords):** tritone ×{h['tritone_hits']}, minor-2nd
  ×{h['minor2_hits']}, fifth ×{h['fifth_hits']}.
{riffs_section}
## Rhythm & pacing

- **Note density:** {rhythm['notes_per_bar']} notes per bar.
- **Tempo:** {tempo['initial_bpm']:.0f} BPM{' (half-time feel)' if tempo['half_time_feel'] else ''}; changes: {tempo_changes}.
- **Dominant durations:** {top_durs}.

| Duration | Count |
|----------|-------|
{duration_rows}
{percussion_section}
## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
{instruments}

## How to apply in this skill

- **Set `bpm`: {apply_bpm}**{' and feel it in half-time.' if tempo['half_time_feel'] else '.'}{' Use a `tempo_map` to reproduce the tempo moves listed above.' if tempo['changes'] else ''}
- **`time_signature`: `{main_ts}`**{(' (watch for ' + ', '.join(k for k in features['time_signatures'] if k != main_ts) + ' sections)') if len(features['time_signatures']) > 1 else ''}.
- **Write in {key_str}.** Lean on {top_pcs}.
- **Octave:** roots around **octave {low_oct}** (lowest note here is {low}{'; this is down-tuned territory' if reg['down_tuned'] else ''}).
- **Voicing:** this is {voicing}. {'Write each chord as a SINGLE-track stacked pitch — `root+5th+octave` (e.g. `C2+G2+C3`) — not parallel layer tracks.' if h['power_chords'] >= h['triads'] and chord_total else 'Use stacked single-track chords rather than parallel layer tracks.'}
- **Duration palette:** favor {top_durs.split(',')[0].split('(')[0].strip()} as the rhythmic unit; mix in the rest of the histogram above.
- **Structure:** highly repetitive ({struct['repetition_ratio']:.0%}) — commit to a riff and cycle it; the top bar repeats {struct['most_repeated_bar_count']}x here. See **Riff transcription** above for the actual notes, not just the count.
- **Dynamics:** the source has real accents Guitar Pro encodes that MIDI velocity can mimic — use per-note `velocity` (ghost ~40, normal ~80, accent ~110+) instead of a flat wall.
"""


def write_card(features: Dict, out_dir: Path = STYLES_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(features.get("artist", ""), features.get("title", ""))
    path = out_dir / f"{slug}.md"
    path.write_text(render(features), encoding="utf-8")
    return path
