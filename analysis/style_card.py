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


def _riff_block(label: str, r: Dict) -> str:
    notes_py = ",\n".join(
        f'    {{"pitch": "{e["pitch"]}", "duration": "{e["duration"]}"}}'
        for e in r["transcription"]
    )
    degree_line = r["degree_sequence"] or "n/a"
    bars = r.get("bars", 1)
    span = f"{bars} bar{'s' if bars != 1 else ''}, "
    return f"""### {label} — {span}repeats {r['repeats']}x ({r['time_sig']})

```python
[
{notes_py}
]
```

- **Scale-degree sequence:** {degree_line}
- **Onset grid (16th notes, `|` = barline):** `{r['onset_grid']}`"""


def _render_riffs(riffs: List[Dict], pedal: Dict | None, pedal_ratio: float, key_str: str) -> str:
    if not riffs and not pedal:
        return ""
    labels = "ABCDEF"
    blocks = [_riff_block(f"Riff {labels[i]}", r) for i, r in enumerate(riffs)]

    pedal_block = ""
    if pedal:
        pedal_block = "\n\n" + _riff_block("Pedal / root center", pedal) + (
            f"\n- **Coverage:** ~{pedal_ratio:.0%} of bars sit on this drone — it's the "
            f"root the riffs above move against, not a riff itself.")

    body = "\n\n".join(blocks) if blocks else "_No moving riff figure detected (this track is mostly drone)._"
    return f"""
## Riff transcription

The most-repeated **moving** figures on the representative track (multi-bar phrases
preferred over single bars), transcribed verbatim in this skill's note syntax, with
scale degrees relative to {key_str}. Sustained drone bars are pulled out separately as
the **Pedal / root center**. Onset grids share the percussion grid's 16th-note
convention below (with `|` marking each barline).

{body}{pedal_block}
"""


def _render_arrangement(arrangement: List[Dict]) -> str:
    if not arrangement:
        return ""
    rows = "\n".join(
        f"| {i + 1} | {s['label']} | {s['start_bar']}–{s['end_bar']} | {s['bars']} |"
        for i, s in enumerate(arrangement)
    )
    flow = " → ".join(s["label"] for s in arrangement)
    return f"""
## Arrangement

Section markers from the source, as an ordered song map:

| # | Section | Bars | Length |
|---|---------|------|--------|
{rows}

Flow: {flow}.
"""


def _render_vocals(vocals: Dict | None, key_str: str) -> str:
    if not vocals:
        return ""
    v = vocals
    top_deg = ", ".join(f"{d} (×{n})" for d, n in list(v["degree_histogram"].items())[:6]) or "n/a"
    top_dur = ", ".join(f"{lbl} ({n})" for lbl, n in list(v["duration_histogram"].items())[:4]) or "n/a"
    phrase_py = ",\n".join(
        f'    {{"pitch": "{e["pitch"]}", "duration": "{e["duration"]}"}}'
        for e in v["representative_phrase"]
    )
    phrase_block = (f"""Longest unbroken sung phrase, transcribed (a lead-line idea):

```python
[
{phrase_py}
]
```
""" if v["representative_phrase"] else "")
    lyrics_block = f"\n- **Lyrics (sample):** {v['lyrics']}\n" if v.get("lyrics") else ""
    return f"""
## Vocals

Measured from the `{v['track_name']}` track (analyzed separately from the instrumental
riffs, the way drums are).

| Trait | Value |
|-------|-------|
| Range | {v['range_low']}–{v['range_high']} ({v['range_semitones']} semitones) |
| Notes | {v['note_count']} |
| Phrases | {v['phrase_count']} (avg {v['avg_notes_per_phrase']} notes/phrase) |
| Emphasized scale degrees | {top_deg} |
| Note durations | {top_dur} |
{lyrics_block}
{phrase_block}"""


def _render_bass(bass: Dict | None) -> str:
    if not bass:
        return ""
    b = bass
    struct = b["structure"]
    voicing = ("power-chord/double-stop driven" if b["power_chords"] > b["single_notes"] * 0.1
               else "single-note line")
    riffs = b.get("riffs") or []
    pedal = b.get("pedal")
    pedal_ratio = b.get("pedal_ratio") or 0.0
    labels = "ABCDEF"
    blocks = [_riff_block(f"Bass riff {labels[i]}", r) for i, r in enumerate(riffs)]
    pedal_block = ""
    if pedal:
        pedal_block = "\n\n" + _riff_block("Bass pedal / root center", pedal) + (
            f"\n- **Coverage:** ~{pedal_ratio:.0%} of bars sit on this drone.")
    riff_body = "\n\n".join(blocks) if blocks else "_No moving bass figure detected (mostly drone/root)._"
    return f"""
## Bass

Measured from the `{b['track_name']}` track, analyzed separately from the guitar
riff above so a bass line that diverges from it (different syncopation, a walking
passage, a fill) isn't averaged away into the combined harmony/register stats.

| Trait | Value |
|-------|-------|
| Range | {b['range_low']}–{b['range_high']} |
| Lowest open string | {b['lowest_open_string']}{'  (down-tuned)' if b['down_tuned'] else ''} |
| Voicing | {voicing} — {b['power_chords']} power-chord hits / {b['triads']} triads / {b['single_notes']} single notes |
| Structure | {struct['bars']} bars, {struct['unique_bars']} unique (repetition {struct['repetition_ratio']:.0%}; top bar repeats {struct['top_riff_repeats']}x) |

{riff_body}{pedal_block}
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
    # `confidence` is a heuristic scale-fit score (clamped 0–1), not a calibrated
    # probability — it often reads 100%. Label it as such so it isn't over-trusted.
    conf = f"{key.get('confidence', 0):.0%} scale-fit (heuristic)" if key else "n/a"
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
        ("Key / scale", f"{key_str}  ({conf})"),
        ("Main time signature", main_ts),
        ("Other meters", ", ".join(k for k in features["time_signatures"] if k != main_ts) or "none"),
        ("Lowest note (guitar)", reg["lowest_note"] or "n/a"),
        ("Lowest open string (guitar)", f"{reg['lowest_open_string']}"
                               + ("  (down-tuned)" if reg["down_tuned"] else "")),
        ("Notes per bar", rhythm["notes_per_bar"]),
        ("Voicing", voicing),
        ("Structure", f"{struct['bars']} bars, {struct['unique_bars']} unique "
                      f"(repetition {struct['repetition_ratio']:.0%}; "
                      f"top bar repeats {struct['most_repeated_bar_count']}x)"),
    ])

    def _role(t):
        if t["percussion"]:
            return "percussion"
        if t.get("bass"):
            return "bass"
        return "vocal" if t.get("vocal") else "pitched"

    instruments = "\n".join(
        f"| {t['name']} | {'drum kit (ch.10)' if t['percussion'] else _gm_name(t['gm_program'])} | "
        f"{'—' if t['percussion'] else t['gm_program']} | "
        f"{_role(t)} |"
        for t in features["instrumentation"]
    )

    duration_rows = "\n".join(f"| {lbl} | {n} |" for lbl, n in durs)

    riffs_section = _render_riffs(features.get("riffs") or [], features.get("pedal"),
                                  features.get("pedal_ratio") or 0.0, key_str)
    bass_section = _render_bass(features.get("bass"))
    arrangement_section = _render_arrangement(features.get("arrangement") or [])
    vocals_section = _render_vocals(features.get("vocals"), key_str)
    percussion_section = _render_percussion(features.get("percussion"))

    return f"""# Style Card — {artist} – {title}

*Auto-generated from `{features['format']}` by the Guitar Pro analysis pipeline
(`analysis/`). Measured facts about a real track. See `CLAUDE.md` in this folder for
what each section means and how to apply it in a composition.*

## Snapshot

| Trait | Value |
|-------|-------|
{snapshot}

## Harmony

- **Key / scale:** {key_str} ({conf}).
- **Most-used pitch classes:** {top_pcs}.
- **Voicing:** {voicing} — {h['power_chords']} power-chord hits vs {h['triads']} triads
  across {h['single_notes']} single notes.
- **Interval color (within chords):** tritone ×{h['tritone_hits']}, minor-2nd
  ×{h['minor2_hits']}, fifth ×{h['fifth_hits']}.
{riffs_section}{bass_section}
## Rhythm & pacing

- **Note density:** {rhythm['notes_per_bar']} notes per bar.
- **Tempo:** {tempo['initial_bpm']:.0f} BPM{' (half-time feel)' if tempo['half_time_feel'] else ''}; changes: {tempo_changes}.
- **Dominant durations:** {top_durs}.

| Duration | Count |
|----------|-------|
{duration_rows}
{percussion_section}{vocals_section}{arrangement_section}
## Instrumentation

| Track | GM instrument | Program | Role |
|-------|---------------|---------|------|
{instruments}
"""


GUIDE = """# Style Cards — how to read and use them

Each `.md` file in this folder is a **style card**: measured facts about one real
track, auto-generated by `analysis/` from a Guitar Pro file. This file holds the
explanation once instead of repeating it in every card.

## Headings

- **Snapshot** — at-a-glance table: tempo, key/scale, time signature, lowest
  note/string, note density, voicing, structural repetition. The lowest-note rows
  are scoped to guitar specifically (see **Bass** below for the bass's own range).
- **Harmony** — key/scale with a `confidence` (a heuristic scale-fit score, not a
  calibrated probability — it often reads 100%, so don't over-trust it), most-used
  pitch classes (across all pitched instruments), and power-chord/triad/single-note
  counts + interval color scoped to the **guitar** tracks (bass has its own voicing
  breakdown below so its mostly-single-note line doesn't dilute the guitar's).
- **Riff transcription** — the most-repeated *moving* figures on the guitar,
  transcribed verbatim in this skill's note syntax (`{"pitch": ..., "duration": ...}`),
  each with a scale-degree sequence and a 16th-note onset grid (`|` = barline).
  Sustained drone bars are split out as **Pedal / root center** rather than counted
  as a riff.
- **Bass** *(if present)* — the bass's own range, voicing, structure, and riff/pedal
  transcription, measured the same way as the guitar's but kept separate so a bass
  line that diverges from the guitar (different syncopation, a walking passage, a
  fill) isn't averaged into the guitar's numbers or lost entirely.
- **Rhythm & pacing** — note density, tempo (+ any tempo changes), duration
  histogram (across all pitched instruments).
- **Percussion** *(if present)* — per-voice hit counts, hits/bar, pattern
  repetition, fill density, and the dominant bar pattern on the same 16th-note
  grid as the riffs (so the two can be lined up by eye).
- **Vocals** *(if present)* — range, phrase count/length, emphasized scale
  degrees, duration histogram, and (if the phrase was short enough) a
  representative transcribed phrase.
- **Arrangement** *(if present)* — section markers from the source as an ordered
  song map (bars per section, overall flow).
- **Instrumentation** — each track's GM instrument/program and role
  (pitched/percussion/vocal/bass).

## Applying a card to a composition

- **Tempo/meter:** set `bpm` from Snapshot; if the card lists tempo changes, use a
  `tempo_map` to reproduce them; set `time_signature` from the main meter.
- **Key:** write in the listed key/scale, leaning on the most-used pitch classes.
- **Octave:** root the guitar around the octave of the card's lowest note — that's
  down-tuned territory if flagged as such. Root the bass an octave below using its
  own **Bass** range/lowest-string numbers, not the guitar's.
- **Bass line:** if the card has a Bass section, give the bass its own track and copy
  its riff/pedal transcription in like the guitar's — don't just double the guitar
  line an octave down, the bass's own riffs may diverge (different rhythm, walking
  passages, fills under a guitar pedal).
- **Voicing:** if power-chord driven, write each chord as a single-track stacked
  pitch (`root+5th+octave`, e.g. `C2+G2+C3`), not parallel layer tracks — see
  CLAUDE.md's *Hard constraints* at the repo root.
- **Riffs:** copy a transcribed riff in verbatim and transpose only the root to
  change key; keep its scale-degree sequence intact to stay in style. Lay the
  Pedal/root center under it as a low sustained chord.
- **Percussion:** this skill has no real GM drum kit (channel 9 is skipped — see
  the repo-root `CLAUDE.md`). Use a card's percussion pattern as a guide rail: lock
  chug/palm-mute hits to where `kick` lands, chordal accents to `snare`/`crash`, and
  let hi-hat density suggest the eighth/sixteenth subdivision.
- **Vocals:** not in this skill's instrument set, but the contour shows where
  melodic weight sits and the phrasing shows where to leave space in the riff under
  sung phrases. Voice the line on a clean lead (e.g. `rock-organ` or clean guitar)
  tracking its scale degrees.
- **Arrangement:** build section by section in the listed order, swapping
  riff/pedal/voicing per section (e.g. drop to the pedal in an intro/interlude,
  bring the moving riff back for verses, thicken voicing for a chorus); bar counts
  say how long to hold each.
- **Structure:** a high repetition ratio means commit to a riff and cycle it — use
  the actual transcribed notes in **Riff transcription**, not just the repeat count.
- **Dynamics:** Guitar Pro encodes real accents that aren't yet extracted into these
  cards; until they are, use per-note `velocity` (ghost ~40, normal ~80, accent
  ~110+) by ear instead of a flat wall.

*Regenerated each time `analyze_song.py` writes a card into this folder — edits here
will be overwritten.*
"""


def write_guide(out_dir: Path = STYLES_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "CLAUDE.md"
    path.write_text(GUIDE, encoding="utf-8")
    return path


def write_card(features: Dict, out_dir: Path = STYLES_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(features.get("artist", ""), features.get("title", ""))
    path = out_dir / f"{slug}.md"
    path.write_text(render(features), encoding="utf-8")
    return path
