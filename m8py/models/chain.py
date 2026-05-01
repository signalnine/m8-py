from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY, STEPS_PER_CHAIN
from m8py.format.errors import M8ParseError

@dataclass
class ChainStep:
    phrase: int = EMPTY
    transpose: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> ChainStep:
        return ChainStep(phrase=reader.read(), transpose=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.phrase)
        writer.write(self.transpose)

@dataclass
class Chain:
    steps: list[ChainStep] = field(default_factory=lambda: [ChainStep() for _ in range(16)])

    @staticmethod
    def from_reader(reader: M8FileReader) -> Chain:
        return Chain(steps=[ChainStep.from_reader(reader) for _ in range(16)])

    def write(self, writer: M8FileWriter) -> None:
        if len(self.steps) != STEPS_PER_CHAIN:
            raise M8ParseError(
                f"Chain must have {STEPS_PER_CHAIN} steps, got {len(self.steps)}"
            )
        for s in self.steps:
            s.write(writer)
