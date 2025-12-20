import { Composition } from "../types/music.js";

export function refineComposition(composition: Composition): Composition {
  composition.tracks.forEach(track => {
    if (track.notes.length > 0 && track.notes.length < 16) {
      const base = [...track.notes];
      while (track.notes.length < 16) {
        track.notes.push(...base);
      }
      track.notes.length = 16;
    }
  });
  return composition;
}