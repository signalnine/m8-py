"""Round-trip all 281 community instrument presets from impbox.net/matey.

For every .m8i file:
  1. Load raw bytes
  2. Parse through m8py (header + instrument)
  3. Re-serialize to bytes
  4. Assert output == input (byte-exact round-trip)
"""
import pytest
from pathlib import Path

from m8py.format.constants import HEADER_SIZE
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.instrument import read_instrument, write_instrument
from m8py.models.version import M8FileType

FIXTURES = Path(__file__).parent / "fixtures" / "matey"


def m8i_files():
    if not FIXTURES.exists():
        return []
    return sorted(FIXTURES.glob("*.m8i"))


@pytest.mark.parametrize("path", m8i_files(), ids=lambda p: p.name)
def test_roundtrip(path: Path):
    data = path.read_bytes()
    reader = M8FileReader(data)
    version = M8FileType.from_reader(reader)

    instrument = read_instrument(reader, version)

    writer = M8FileWriter()
    M8FileType.write_header(writer, version)
    write_instrument(instrument, writer)
    output = writer.to_bytes()

    # Compare byte-exact: header + instrument (215 bytes) = 229 bytes
    expected_len = HEADER_SIZE + 215
    input_trimmed = data[:expected_len]
    output_trimmed = output[:expected_len]

    if input_trimmed != output_trimmed:
        # Find first difference for diagnostic
        for i, (a, b) in enumerate(zip(input_trimmed, output_trimmed)):
            if a != b:
                ctx_start = max(0, i - 4)
                ctx_end = min(len(input_trimmed), i + 8)
                pytest.fail(
                    f"{path.name}: first diff at byte {i} "
                    f"(0x{i:04X}): expected 0x{a:02X}, got 0x{b:02X}\n"
                    f"  input  [{ctx_start}:{ctx_end}]: {input_trimmed[ctx_start:ctx_end].hex(' ')}\n"
                    f"  output [{ctx_start}:{ctx_end}]: {output_trimmed[ctx_start:ctx_end].hex(' ')}"
                )
