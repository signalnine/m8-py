from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY
from m8py.models.fx import FX

@dataclass
class TableStep:
    transpose: int = 0
    velocity: int = EMPTY
    fx1: FX = field(default_factory=FX)
    fx2: FX = field(default_factory=FX)
    fx3: FX = field(default_factory=FX)

    @staticmethod
    def from_reader(reader: M8FileReader) -> TableStep:
        return TableStep(
            transpose=reader.read(), velocity=reader.read(),
            fx1=FX.from_reader(reader), fx2=FX.from_reader(reader), fx3=FX.from_reader(reader),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.transpose); writer.write(self.velocity)
        self.fx1.write(writer); self.fx2.write(writer); self.fx3.write(writer)

@dataclass
class Table:
    steps: list[TableStep] = field(default_factory=lambda: [TableStep() for _ in range(16)])

    @staticmethod
    def from_reader(reader: M8FileReader) -> Table:
        return Table(steps=[TableStep.from_reader(reader) for _ in range(16)])

    def write(self, writer: M8FileWriter) -> None:
        for s in self.steps:
            s.write(writer)
