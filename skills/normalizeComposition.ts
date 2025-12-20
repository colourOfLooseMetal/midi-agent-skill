import { Composition } from "../types/music.js";

export function normalizeComposition(input: any): Composition {
  return {
    title: typeof input.title === "string" ? input.title : "untitled",
    bpm: typeof input.bpm === "number" ? input.bpm : 90,
    tracks: Array.isArray(input.tracks)
      ? input.tracks.map((t: any) => ({
          instrument: typeof t.instrument === "string" ? t.instrument : undefined,
          notes: Array.isArray(t.notes)
            ? t.notes
                .filter((n: any) => n.pitch && n.duration)
                .map((n: any) => ({
                  pitch: String(n.pitch),
                  duration: String(n.duration)
                }))
            : []
        }))
      : []
  };
}