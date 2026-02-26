from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter

@dataclass
class EQBand:
    mode_type: int = 0
    freq_fine: int = 0
    freq: int = 0
    level_fine: int = 0
    level: int = 0
    q: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> EQBand:
        return EQBand(
            mode_type=reader.read(), freq_fine=reader.read(), freq=reader.read(),
            level_fine=reader.read(), level=reader.read(), q=reader.read(),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.mode_type)
        writer.write(self.freq_fine)
        writer.write(self.freq)
        writer.write(self.level_fine)
        writer.write(self.level)
        writer.write(self.q)


@dataclass
class EQ:
    low: EQBand = field(default_factory=EQBand)
    mid: EQBand = field(default_factory=EQBand)
    high: EQBand = field(default_factory=EQBand)

    @staticmethod
    def from_reader(reader: M8FileReader) -> EQ:
        return EQ(low=EQBand.from_reader(reader), mid=EQBand.from_reader(reader), high=EQBand.from_reader(reader))

    def write(self, writer: M8FileWriter) -> None:
        self.low.write(writer)
        self.mid.write(writer)
        self.high.write(writer)
