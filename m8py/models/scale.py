from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.version import M8Version

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
    _raw_name: bytes | None = field(default=None, repr=False, compare=False)

    @staticmethod
    def from_reader(reader: M8FileReader, version: M8Version | None = None) -> Scale:
        note_enable = reader.read_u16_le()
        note_offsets = [NoteInterval.from_reader(reader) for _ in range(12)]
        _raw_name = reader.read_bytes(16)
        # Parse name from raw bytes (stop at 0x00 or 0xFF)
        chars = []
        for b in _raw_name:
            if b == 0x00 or b == 0xFF:
                break
            chars.append(chr(b))
        name = "".join(chars)
        tuning = 0.0
        has_tuning = version is not None and version.at_least(4, 0)
        if has_tuning:
            tuning = reader.read_float_le()
        return Scale(name=name, note_enable=note_enable,
                     note_offsets=note_offsets, tuning=tuning,
                     _raw_name=_raw_name)

    def write(self, writer: M8FileWriter, version: M8Version | None = None) -> None:
        writer.write_u16_le(self.note_enable)
        for ni in self.note_offsets:
            ni.write(writer)
        if self._raw_name is not None:
            writer.write_bytes(self._raw_name)
        else:
            writer.write_str(self.name, 16)
        has_tuning = version is None or version.at_least(4, 0)
        if has_tuning:
            writer.write_float_le(self.tuning)
