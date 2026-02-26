from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY

@dataclass
class FX:
    command: int = EMPTY
    value: int = 0x00

    @staticmethod
    def from_reader(reader: M8FileReader) -> FX:
        return FX(command=reader.read(), value=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.command)
        writer.write(self.value)
