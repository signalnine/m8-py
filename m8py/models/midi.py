from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter


@dataclass
class MIDIMapping:
    channel: int = 0
    control_number: int = 0
    value: int = 0
    typ: int = 0
    param_index: int = 0
    min_value: int = 0
    max_value: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> MIDIMapping:
        return MIDIMapping(
            channel=reader.read(),
            control_number=reader.read(),
            value=reader.read(),
            typ=reader.read(),
            param_index=reader.read(),
            min_value=reader.read(),
            max_value=reader.read(),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.channel)
        writer.write(self.control_number)
        writer.write(self.value)
        writer.write(self.typ)
        writer.write(self.param_index)
        writer.write(self.min_value)
        writer.write(self.max_value)
