from __future__ import annotations
from typing import Union

from m8py.compose.allocator import SlotAllocator
from m8py.compose.notation import parse_pattern
from m8py.format.constants import STEPS_PER_PHRASE
from m8py.models.chain import Chain, ChainStep
from m8py.models.groove import Groove
from m8py.models.instrument import Instrument
from m8py.models.phrase import Phrase, PhraseStep
from m8py.models.song import Song
from m8py.models.table import Table


class SongBuilder:
    """Fluent imperative API for building M8 songs.

    Example:
        song = (SongBuilder(name="MyTrack", tempo=120)
            .add_instrument(synth)
            .add_phrase("C4 E4 G4 C5")
            .add_chain([0])  # chain referencing phrase 0
            .set_song_step(0, track=0, chain=0)
            .build())
    """

    def __init__(self, name: str = "", tempo: float = 120.0,
                 deduplicate: bool = False):
        self._song = Song()
        self._song.name = name
        self._song.tempo = tempo
        self._alloc = SlotAllocator(deduplicate=deduplicate)
        self._last_phrase: int | None = None
        self._last_chain: int | None = None
        self._last_instrument: int | None = None
        self._last_table: int | None = None
        self._last_groove: int | None = None

    @property
    def last_phrase(self) -> int | None:
        return self._last_phrase

    @property
    def last_chain(self) -> int | None:
        return self._last_chain

    @property
    def last_instrument(self) -> int | None:
        return self._last_instrument

    @property
    def last_table(self) -> int | None:
        return self._last_table

    @property
    def last_groove(self) -> int | None:
        return self._last_groove

    def add_instrument(self, instrument: Instrument) -> SongBuilder:
        """Add an instrument and allocate a slot."""
        slot = self._alloc.alloc_instrument(instrument)
        self._song.instruments[slot] = instrument
        self._last_instrument = slot
        return self

    def add_phrase(self, phrase: Union[Phrase, str]) -> SongBuilder:
        """Add a phrase (Phrase object or pattern string)."""
        if isinstance(phrase, str):
            steps = parse_pattern(phrase)
            # Pad or truncate to 16 steps
            if len(steps) < STEPS_PER_PHRASE:
                steps.extend([PhraseStep() for _ in range(STEPS_PER_PHRASE - len(steps))])
            phrase = Phrase(steps=steps[:STEPS_PER_PHRASE])
        slot = self._alloc.alloc_phrase(phrase)
        self._song.phrases[slot] = phrase
        self._last_phrase = slot
        return self

    def add_chain(self, phrase_slots: list[int], transpose: int = 0) -> SongBuilder:
        """Add a chain referencing the given phrase slot indices."""
        steps = []
        for ps in phrase_slots:
            steps.append(ChainStep(phrase=ps, transpose=transpose))
        # Pad with empty steps
        while len(steps) < 16:
            steps.append(ChainStep())
        chain = Chain(steps=steps[:16])
        slot = self._alloc.alloc_chain(chain)
        self._song.chains[slot] = chain
        self._last_chain = slot
        return self

    def add_table(self, table: Table) -> SongBuilder:
        """Add a table and allocate a slot."""
        slot = self._alloc.alloc_table(table)
        self._song.tables[slot] = table
        self._last_table = slot
        return self

    def add_groove(self, groove: Groove) -> SongBuilder:
        """Add a groove and allocate a slot."""
        slot = self._alloc.alloc_groove(groove)
        self._song.grooves[slot] = groove
        self._last_groove = slot
        return self

    def set_song_step(self, row: int, track: int, chain: int) -> SongBuilder:
        """Place a chain reference in the song grid."""
        self._song.song_steps[row].tracks[track] = chain
        return self

    def set_tempo(self, tempo: float) -> SongBuilder:
        self._song.tempo = tempo
        return self

    def set_name(self, name: str) -> SongBuilder:
        self._song.name = name
        return self

    def set_transpose(self, transpose: int) -> SongBuilder:
        self._song.transpose = transpose
        return self

    def build(self) -> Song:
        """Return the constructed Song."""
        return self._song
