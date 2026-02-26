from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter

# MIDI mapping entry stride is 9 bytes in the firmware (confirmed by
# section math: 0x1AA7E - 0x1A5FE = 1152 = 128 * 9).  Only the first
# 7 bytes carry data; bytes 7-8 are zero padding never accessed by
# any firmware function (verified via Ghidra decompilation of all 7
# callers of thunk_EXT_FUN_0002264a).
MIDI_MAPPING_DATA_SIZE = 7
MIDI_MAPPING_PADDING = 2
MIDI_MAPPING_ENTRY_SIZE = MIDI_MAPPING_DATA_SIZE + MIDI_MAPPING_PADDING


@dataclass
class MIDIMapping:
    channel: int = 0
    control_number: int = 0
    type: int = 0          # mapping type (I/X/M category)
    instr_index: int = 0   # target instrument index (0-127)
    param_index: int = 0   # target parameter within instrument
    min_value: int = 0     # mapping range minimum
    max_value: int = 0     # mapping range maximum

    @staticmethod
    def from_reader(reader: M8FileReader) -> MIDIMapping:
        mapping = MIDIMapping(
            channel=reader.read(),
            control_number=reader.read(),
            type=reader.read(),
            instr_index=reader.read(),
            param_index=reader.read(),
            min_value=reader.read(),
            max_value=reader.read(),
        )
        reader.skip(MIDI_MAPPING_PADDING)  # 2 zero-padding bytes
        return mapping

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.channel)
        writer.write(self.control_number)
        writer.write(self.type)
        writer.write(self.instr_index)
        writer.write(self.param_index)
        writer.write(self.min_value)
        writer.write(self.max_value)
        writer.pad(MIDI_MAPPING_PADDING)  # 2 zero-padding bytes
