import MidiWriter from "midi-writer-js";
import fs from "fs";
import path from "path";
import { Composition } from "../types/music.js";
import { resolveInstrument } from "../types/gmInstruments.js";

/**
 * Generate a MIDI file from a Composition object
 * Uses General MIDI program changes compatible with A320U.sf2 SoundFont
 *
 * @param composition - The composition to convert to MIDI
 * @returns The path to the generated MIDI file
 */
export function generateMidi(composition: Composition): string {
  const tracks: MidiWriter.Track[] = [];

  composition.tracks.forEach((t, index) => {
    const track = new MidiWriter.Track();

    // Set tempo on first track
    if (index === 0) {
      track.setTempo(composition.bpm);
    }

    // Set instrument via Program Change (GM compatible with A320U.sf2)
    const programNumber = t.instrument
      ? resolveInstrument(t.instrument)
      : 0; // Default to Acoustic Grand Piano

    track.addEvent(new MidiWriter.ProgramChangeEvent({ instrument: programNumber }));

    // Add track name if instrument is specified
    if (t.instrument) {
      track.addTrackName(t.instrument);
    }

    // Add notes
    t.notes.forEach(note => {
      track.addEvent(
        new MidiWriter.NoteEvent({
          pitch: [note.pitch],
          duration: note.duration
        })
      );
    });

    tracks.push(track);
  });

  const writer = new MidiWriter.Writer(tracks);
  const outDir = path.resolve("output");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  const sanitizedTitle = composition.title.replace(/[^a-zA-Z0-9_-]/g, "_");
  const filePath = path.join(outDir, `${sanitizedTitle}.mid`);
  fs.writeFileSync(filePath, writer.buildFile());

  return filePath;
}
