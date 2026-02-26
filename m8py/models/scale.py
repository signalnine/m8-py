from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter

@dataclass
class NoteInterval:
    semitone: int = 0
    cents: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> NoteInterval:
        return NoteInterval(semitone=reader.read(), cents=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.semitone)
        writer.write(self.cents)


@dataclass
class Scale:
    name: str = ""
    note_enable: int = 0xFFF
    note_offsets: list[NoteInterval] = field(
        default_factory=lambda: [NoteInterval() for _ in range(12)]
    )
    tuning: float = 0.0  # float32 at +0x2A, reference pitch offset (v4+)

    @staticmethod
    def from_reader(reader: M8FileReader) -> Scale:
        note_enable = reader.read_u16_le()
        note_offsets = [NoteInterval.from_reader(reader) for _ in range(12)]
        name = reader.read_str(16)
        tuning = reader.read_float_le()
        return Scale(name=name, note_enable=note_enable,
                     note_offsets=note_offsets, tuning=tuning)

    def write(self, writer: M8FileWriter) -> None:
        writer.write_u16_le(self.note_enable)
        for ni in self.note_offsets:
            ni.write(writer)
        writer.write_str(self.name, 16)
        writer.write_float_le(self.tuning)
