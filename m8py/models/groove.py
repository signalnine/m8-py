from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY, STEPS_PER_GROOVE
from m8py.format.errors import M8ParseError

@dataclass
class Groove:
    steps: list[int] = field(default_factory=lambda: [EMPTY] * 16)

    @staticmethod
    def from_reader(reader: M8FileReader) -> Groove:
        return Groove(steps=[reader.read() for _ in range(16)])

    def write(self, writer: M8FileWriter) -> None:
        if len(self.steps) != STEPS_PER_GROOVE:
            raise M8ParseError(
                f"Groove must have {STEPS_PER_GROOVE} steps, got {len(self.steps)}"
            )
        for s in self.steps:
            writer.write(s)
