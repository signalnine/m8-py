from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY
from m8py.models.fx import FX

@dataclass
class PhraseStep:
    note: int = EMPTY
    velocity: int = EMPTY
    instrument: int = EMPTY
    fx1: FX = field(default_factory=FX)
    fx2: FX = field(default_factory=FX)
    fx3: FX = field(default_factory=FX)

    @staticmethod
    def from_reader(reader: M8FileReader) -> PhraseStep:
        return PhraseStep(
            note=reader.read(), velocity=reader.read(), instrument=reader.read(),
            fx1=FX.from_reader(reader), fx2=FX.from_reader(reader), fx3=FX.from_reader(reader),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.note); writer.write(self.velocity); writer.write(self.instrument)
        self.fx1.write(writer); self.fx2.write(writer); self.fx3.write(writer)

@dataclass
class Phrase:
    steps: list[PhraseStep] = field(default_factory=lambda: [PhraseStep() for _ in range(16)])

    @staticmethod
    def from_reader(reader: M8FileReader) -> Phrase:
        return Phrase(steps=[PhraseStep.from_reader(reader) for _ in range(16)])

    def write(self, writer: M8FileWriter) -> None:
        for s in self.steps:
            s.write(writer)
