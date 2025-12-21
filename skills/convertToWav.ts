import { execSync } from "child_process";
import fs from "fs";
import path from "path";

/**
 * Configuration for MIDI to WAV conversion
 */
export interface ConvertOptions {
  /** Path to the SoundFont file (defaults to A320U.sf2 in soundfonts directory) */
  soundfontPath?: string;
  /** Sample rate in Hz (default: 44100) */
  sampleRate?: number;
  /** Audio gain (default: 0.5) */
  gain?: number;
  /** Enable reverb (default: false for cleaner output) */
  reverb?: boolean;
  /** Enable chorus (default: false for cleaner output) */
  chorus?: boolean;
}

/**
 * Convert a MIDI file to WAV using FluidSynth and A320U.sf2 SoundFont
 *
 * Prerequisites:
 * - FluidSynth must be installed (brew install fluidsynth on macOS)
 * - A320U.sf2 must be placed in the soundfonts directory
 *
 * @param midiPath - Path to the input MIDI file
 * @param options - Conversion options
 * @returns Path to the generated WAV file
 */
export function convertToWav(midiPath: string, options: ConvertOptions = {}): string {
  // Validate MIDI file exists
  if (!fs.existsSync(midiPath)) {
    throw new Error(`MIDI file not found: ${midiPath}`);
  }

  // Resolve soundfont path
  const soundfontPath = options.soundfontPath
    ?? path.resolve("soundfonts", "A320U.sf2");

  if (!fs.existsSync(soundfontPath)) {
    throw new Error(
      `SoundFont not found: ${soundfontPath}\n` +
      `Please download A320U.sf2 from https://musical-artifacts.com/artifacts/5906 ` +
      `and place it in the soundfonts directory.`
    );
  }

  // Set up output path
  const outDir = path.resolve("output");
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const baseName = path.basename(midiPath, path.extname(midiPath));
  const wavPath = path.join(outDir, `${baseName}.wav`);

  // Build FluidSynth command
  const sampleRate = options.sampleRate ?? 44100;
  const gain = options.gain ?? 0.5;
  const reverb = options.reverb ?? false;
  const chorus = options.chorus ?? false;

  const args = [
    "fluidsynth",
    "-ni",                         // Non-interactive, no shell
    `--sample-rate=${sampleRate}`, // Sample rate
    `--gain=${gain}`,              // Audio gain
    reverb ? "--reverb=yes" : "--reverb=no",
    chorus ? "--chorus=yes" : "--chorus=no",
    "-F", wavPath,                 // Output file
    soundfontPath,                 // SoundFont
    midiPath                       // Input MIDI
  ];

  const command = args.join(" ");

  try {
    execSync(command, { stdio: "pipe" });
  } catch (error: any) {
    // Check if FluidSynth is installed
    try {
      execSync("which fluidsynth", { stdio: "pipe" });
    } catch {
      throw new Error(
        "FluidSynth is not installed.\n" +
        "Install it with: brew install fluidsynth (macOS) or apt-get install fluidsynth (Linux)"
      );
    }
    throw new Error(`FluidSynth conversion failed: ${error.message}`);
  }

  return wavPath;
}

/**
 * Check if FluidSynth is available on the system
 */
export function isFluidSynthAvailable(): boolean {
  try {
    execSync("which fluidsynth", { stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if the default SoundFont (A320U.sf2) is available
 */
export function isSoundFontAvailable(): boolean {
  const soundfontPath = path.resolve("soundfonts", "A320U.sf2");
  return fs.existsSync(soundfontPath);
}

/**
 * Get system status for MIDI to WAV conversion
 */
export function getConversionStatus(): {
  fluidSynthInstalled: boolean;
  soundFontAvailable: boolean;
  ready: boolean;
  message: string;
} {
  const fluidSynthInstalled = isFluidSynthAvailable();
  const soundFontAvailable = isSoundFontAvailable();
  const ready = fluidSynthInstalled && soundFontAvailable;

  let message = "";
  if (!fluidSynthInstalled) {
    message += "FluidSynth is not installed. Install with: brew install fluidsynth\n";
  }
  if (!soundFontAvailable) {
    message += "A320U.sf2 SoundFont not found. Download from: https://musical-artifacts.com/artifacts/5906\n";
    message += "Place the file in: soundfonts/A320U.sf2";
  }
  if (ready) {
    message = "Ready for MIDI to WAV conversion using A320U.sf2 SoundFont.";
  }

  return { fluidSynthInstalled, soundFontAvailable, ready, message };
}
