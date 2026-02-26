from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY

@dataclass
class SongStep:
    tracks: list[int] = field(default_factory=lambda: [EMPTY] * 8)

    @staticmethod
    def from_reader(reader: M8FileReader) -> SongStep:
        return SongStep(tracks=[reader.read() for _ in range(8)])

    def write(self, writer: M8FileWriter) -> None:
        for t in self.tracks:
            writer.write(t)
