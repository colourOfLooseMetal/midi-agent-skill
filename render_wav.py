#!/usr/bin/env python3
"""
Render the generated MIDI to WAV using the midi-generation skill's converter.

FluidSynth isn't on PATH on this machine, so we locate the locally-extracted
build and prepend its bin dir to PATH for the subprocess the skill spawns.
Reverb is enabled for the genre's psychedelic space; gain is kept moderate to
avoid clipping the dense, chordal power-chord guitar.
"""

import glob
import os
import sys
import wave
from pathlib import Path

REPO = Path(__file__).parent
sys.path.insert(0, str(REPO))

GAIN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.4

# Locate the bundled FluidSynth and expose it on PATH for the skill's subprocess.
hits = glob.glob(os.path.join(os.environ["LOCALAPPDATA"], "fluidsynth", "**", "fluidsynth.exe"),
                 recursive=True)
if not hits:
    sys.exit("fluidsynth.exe not found under %LOCALAPPDATA%\\fluidsynth")
os.environ["PATH"] = os.path.dirname(hits[0]) + os.pathsep + os.environ.get("PATH", "")

from skills.convert_to_wav import convert_to_wav, ConvertOptions, get_conversion_status

status = get_conversion_status()
print("Conversion ready:", status.ready, "-", status.message)

midi = str(REPO / "output" / "Stoner_Doom_-_Riff_Worship.mid")
opts = ConvertOptions(gain=GAIN, reverb=True, chorus=False)
wav = convert_to_wav(midi, opts)
print("WAV written:", wav)

# --- verify: duration + peak level (clipping check) -------------------------
w = wave.open(wav, "rb")
sr, ch, sw, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
dur = n / float(sr)
peak = 0
try:
    import numpy as np
    while True:
        raw = w.readframes(200000)
        if not raw:
            break
        peak = max(peak, int(np.abs(np.frombuffer(raw, dtype="<i2")).max()))
except ImportError:
    import array
    while True:
        raw = w.readframes(200000)
        if not raw:
            break
        a = array.array("h")
        a.frombytes(raw)
        peak = max(peak, max(a), -min(a))
w.close()
full = float(2 ** (8 * sw - 1))
import math
dbfs = 20 * math.log10(peak / full) if peak else -float("inf")
print(f"Audio: {dur:.1f}s, {sr} Hz, {ch}ch, {sw*8}-bit | peak {peak}/{int(full)} "
      f"({dbfs:.2f} dBFS){'  <-- CLIPPING' if peak >= full - 1 else ''}")
