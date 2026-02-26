from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union

from m8py.compose.builder import SongBuilder
from m8py.compose.notation import parse_pattern
from m8py.format.constants import STEPS_PER_PHRASE
from m8py.models.instrument import Instrument
from m8py.models.phrase import Phrase, PhraseStep
from m8py.models.song import Song


@dataclass
class TrackDef:
    """Defines a single track's content for declarative composition.

    Args:
        instrument: The instrument to use for this track.
        pattern: Notes as a pattern string or list of PhraseSteps.
            Can be longer than 16 steps — will be auto-split into
            multiple phrases and chained.
        track: Which M8 track (0-7) to place this on.
    """
    instrument: Instrument
    pattern: Union[str, list[PhraseStep]]
    track: int = 0


def compose(
    tracks: list[TrackDef],
    name: str = "",
    tempo: float = 120.0,
    deduplicate: bool = False,
) -> Song:
    """Build a Song from high-level track definitions.

    Handles:
    - Converting patterns to PhraseSteps
    - Splitting patterns longer than 16 steps into multiple phrases
    - Creating chains from phrase sequences
    - Placing chains on the song grid (one row per chain)
    - Auto-allocating instrument, phrase, and chain slots

    Args:
        tracks: List of TrackDef describing each track.
        name: Song name.
        tempo: Song tempo in BPM.
        deduplicate: If True, identical phrases share slots.

    Returns:
        A fully assembled Song.
    """
    builder = SongBuilder(name=name, tempo=tempo, deduplicate=deduplicate)

    for tdef in tracks:
        # Allocate instrument
        builder.add_instrument(tdef.instrument)
        inst_slot = builder.last_instrument

        # Parse pattern to steps
        if isinstance(tdef.pattern, str):
            steps = parse_pattern(tdef.pattern)
        else:
            steps = list(tdef.pattern)

        # Stamp instrument on each step that has a note
        for step in steps:
            if step.note != 0xFF and step.instrument == 0xFF:
                step.instrument = inst_slot

        # Split into phrase-sized chunks
        phrase_slots = []
        for i in range(0, max(len(steps), 1), STEPS_PER_PHRASE):
            chunk = steps[i:i + STEPS_PER_PHRASE]
            # Pad to 16 steps
            while len(chunk) < STEPS_PER_PHRASE:
                chunk.append(PhraseStep())
            phrase = Phrase(steps=chunk)
            builder.add_phrase(phrase)
            phrase_slots.append(builder.last_phrase)

        # Create chain from phrase slots
        builder.add_chain(phrase_slots)
        chain_slot = builder.last_chain

        # Place on song grid
        builder.set_song_step(0, tdef.track, chain_slot)

    return builder.build()
