"""
One-off test driver: stitches the extracted riffs from two style cards
(resources/styles/doom/monolord-empress-rising.md and electric-wizard-dopethrone.md)
back-to-back into a single MIDI file, each riff played once, so the riff-extraction
output of analyze_song.py can be sanity-checked by ear.

Not part of the packaged skill — just a verification script.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from skills.generate_midi import generate_midi_from_dict, DURATION_MAP


def beats(duration: str) -> float:
    if duration in DURATION_MAP:
        return DURATION_MAP[duration]
    return 4.0 / float(duration)


def total_beats(notes: list) -> float:
    return sum(beats(n["duration"]) for n in notes)


def rest(duration: str) -> dict:
    return {"pitch": "R", "duration": duration}


# --- Monolord - Empress Rising (B Phrygian, 120 BPM) ---

monolord_riff_a = [
    {"pitch": "B1+Gb2", "duration": "2"},
    {"pitch": "B2+Gb3", "duration": "2"},
    {"pitch": "A2+E3", "duration": "8"},
    {"pitch": "B2+Gb3", "duration": "8"},
    {"pitch": "C3+G3", "duration": "4"},
    {"pitch": "A2+E3", "duration": "4"},
    {"pitch": "B2+Gb3", "duration": "4"},
    {"pitch": "B1+Gb2", "duration": "2"},
    {"pitch": "B2+Gb3", "duration": "2"},
    {"pitch": "A2+E3", "duration": "8"},
    {"pitch": "B2+Gb3", "duration": "8"},
    {"pitch": "C3+G3", "duration": "4"},
    {"pitch": "A2+E3", "duration": "4"},
    {"pitch": "B2+Gb3", "duration": "4"},
]

monolord_riff_b = [
    {"pitch": "B1", "duration": "2"},
    {"pitch": "B2", "duration": "2"},
    {"pitch": "A2", "duration": "8"},
    {"pitch": "B2", "duration": "8"},
    {"pitch": "B2", "duration": "4"},
    {"pitch": "B2", "duration": "8"},
    {"pitch": "Bb2", "duration": "8"},
    {"pitch": "Bb2", "duration": "4"},
    {"pitch": "B1", "duration": "2"},
    {"pitch": "B2", "duration": "2"},
    {"pitch": "A2", "duration": "8"},
    {"pitch": "B2", "duration": "8"},
    {"pitch": "B2", "duration": "4"},
    {"pitch": "B2", "duration": "8"},
    {"pitch": "Bb2", "duration": "8"},
    {"pitch": "Bb2", "duration": "4"},
]

monolord_riff_c = [
    {"pitch": "B1+Gb2", "duration": "2"},
    {"pitch": "B2", "duration": "4"},
    {"pitch": "B1+Gb2", "duration": "8"},
    {"pitch": "B1+Gb2", "duration": "8"},
    {"pitch": "C2+G2", "duration": "4"},
    {"pitch": "B1+Gb2", "duration": "4"},
    {"pitch": "F2+C3", "duration": "2"},
    {"pitch": "F2+C3", "duration": "4"},
    {"pitch": "D2+A2", "duration": "8"},
    {"pitch": "D2+A2", "duration": "8"},
    {"pitch": "E2+B2", "duration": "4"},
    {"pitch": "C2+G2", "duration": "4"},
    {"pitch": "B1+Gb2", "duration": "2"},
    {"pitch": "B2", "duration": "4"},
    {"pitch": "B1+Gb2", "duration": "8"},
    {"pitch": "B1+Gb2", "duration": "8"},
    {"pitch": "C2+G2", "duration": "4"},
    {"pitch": "B1+Gb2", "duration": "4"},
    {"pitch": "Bb2+F3", "duration": "2"},
    {"pitch": "Bb2+F3", "duration": "4"},
    {"pitch": "Bb2+F3", "duration": "8"},
    {"pitch": "Bb2+F3", "duration": "8"},
    {"pitch": "A2+E3", "duration": "8"},
    {"pitch": "G2+D3", "duration": "8"},
    {"pitch": "A2+E3", "duration": "4"},
    {"pitch": "Bb2+F3", "duration": "8"},
    {"pitch": "A2+E3", "duration": "d4"},
]

# --- Electric Wizard - Dopethrone (Bb minor blues, 55 BPM) ---

dopethrone_riff_a = [
    {"pitch": "Ab1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb0", "duration": "16"},
    {"pitch": "E2", "duration": "d8"},
    {"pitch": "Bb0", "duration": "16"},
    {"pitch": "Db2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Db2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Ab1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb0", "duration": "16"},
    {"pitch": "E1", "duration": "d8"},
    {"pitch": "Bb0", "duration": "16"},
    {"pitch": "Db1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Db1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Ab1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb0", "duration": "16"},
    {"pitch": "E2", "duration": "d8"},
    {"pitch": "Bb0", "duration": "16"},
    {"pitch": "Db2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Db2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Eb2", "duration": "16"},
    {"pitch": "Ab1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb0", "duration": "16"},
    {"pitch": "E1", "duration": "d8"},
    {"pitch": "Bb0", "duration": "16"},
    {"pitch": "Db1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Db1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
]

dopethrone_riff_b = [
    {"pitch": "Bb1", "duration": "8"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb1", "duration": "8"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "Bb1", "duration": "16"},
    {"pitch": "E2", "duration": "16"},
    {"pitch": "E2", "duration": "16"},
    {"pitch": "E2", "duration": "16"},
    {"pitch": "E2", "duration": "16"},
    {"pitch": "E2", "duration": "16"},
    {"pitch": "E2", "duration": "16"},
    {"pitch": "E2", "duration": "16"},
    {"pitch": "E2", "duration": "16"},
]

dopethrone_riff_c = [
    {"pitch": "Ab1", "duration": "32"},
    {"pitch": "Bb1", "duration": "4"},
    {"pitch": "Bb1", "duration": "d8"},
    {"pitch": "Bb1", "duration": "8"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "8"},
    {"pitch": "Eb1", "duration": "8"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Db1", "duration": "8"},
    {"pitch": "Db2", "duration": "8"},
    {"pitch": "Ab1", "duration": "8"},
    {"pitch": "Ab1", "duration": "32"},
    {"pitch": "Bb1", "duration": "4"},
    {"pitch": "Bb1", "duration": "d8"},
    {"pitch": "Bb1", "duration": "8"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "8"},
    {"pitch": "Eb1", "duration": "8"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Eb1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Gb1", "duration": "16"},
    {"pitch": "F1", "duration": "16"},
    {"pitch": "Db1", "duration": "8"},
    {"pitch": "Db2", "duration": "8"},
    {"pitch": "Ab1", "duration": "8"},
]

SEPARATOR = rest("4")          # 1-beat breather between riffs
SONG_SEPARATOR = rest("2")     # 2-beat breather between songs

monolord_notes = (
    monolord_riff_a + [SEPARATOR]
    + monolord_riff_b + [SEPARATOR]
    + monolord_riff_c
)

dopethrone_notes = (
    dopethrone_riff_a + [SEPARATOR]
    + dopethrone_riff_b + [SEPARATOR]
    + dopethrone_riff_c
)

# Beat at which the Dopethrone half starts (after the Monolord riffs + song separator).
tempo_switch_beat = total_beats(monolord_notes) + beats(SONG_SEPARATOR["duration"])

composition = {
    "title": "Riff Extraction Test",
    "bpm": 120,
    "tempo_map": [
        {"beat": 0, "bpm": 120},
        {"beat": tempo_switch_beat, "bpm": 55},
    ],
    "tracks": [
        {
            "instrument": "distortion-guitar",
            "notes": monolord_notes + [SONG_SEPARATOR] + dopethrone_notes,
        }
    ],
}

if __name__ == "__main__":
    path = generate_midi_from_dict(composition)
    print(f"Wrote {path}")
    print(f"Monolord riffs: {total_beats(monolord_notes):.2f} beats @ 120 BPM")
    print(f"Tempo switch to 55 BPM at beat {tempo_switch_beat:.2f}")
    print(f"Dopethrone riffs: {total_beats(dopethrone_notes):.2f} beats @ 55 BPM")
