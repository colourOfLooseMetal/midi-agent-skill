"""
Guitar Pro -> style analysis pipeline.

This package is a *process* tool, not part of the packaged runtime skill: it reads
real Guitar Pro tabs, measures their stylistic characteristics, and writes reusable
"style cards" into resources/styles/ that the composition step can read like any
other theory reference. See analyze_song.py at the repo root for the driver.
"""
