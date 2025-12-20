import MidiWriter from "midi-writer-js";
import fs from "fs";
import path from "path";
import { Composition } from "../types/music.js";

export function generateMidi(composition: Composition): string {
  const tracks: MidiWriter.Track[] = [];

  for (const t of composition.tracks) {
    const track = new MidiWriter.Track();
    track.setTempo(composition.bpm);

    t.notes.forEach(note => {
      track.addEvent(
        new MidiWriter.NoteEvent({
          pitch: [note.pitch],
          duration: note.duration
        })
      );
    });

    tracks.push(track);
  }

  const writer = new MidiWriter.Writer(tracks);
  const outDir = path.resolve("output");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

  const filePath = path.join(outDir, `${composition.title}.mid`);
  fs.writeFileSync(filePath, writer.buildFile());
  return filePath;
}