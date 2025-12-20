export type Note = {
  pitch: string;
  duration: string;
};

export type Track = {
  instrument?: string;
  notes: Note[];
};

export type Composition = {
  title: string;
  bpm: number;
  tracks: Track[];
};