"""Round-trip all 281 community instrument presets from impbox.net/matey.

For every .m8i file:
  1. Load raw bytes
  2. Parse through m8py (header + instrument + tail)
  3. Re-serialize to bytes
  4. Assert output == input (byte-exact round-trip)
"""
import pytest
from pathlib import Path

from m8py.io import load, save
from m8py.format.writer import M8FileWriter

FIXTURES = Path(__file__).parent / "fixtures" / "matey"


def m8i_files():
    if not FIXTURES.exists():
        return []
    return sorted(FIXTURES.glob("*.m8i"))


@pytest.mark.parametrize("path", m8i_files(), ids=lambda p: p.name)
def test_roundtrip(path: Path):
    data = path.read_bytes()
    instrument = load(path)

    writer = M8FileWriter()
    from m8py.models.version import M8FileType
    version = getattr(instrument, '_file_version', None)
    assert version is not None, "instrument should have _file_version from load()"
    M8FileType.write_header(writer, version)
    from m8py.models.instrument import write_instrument
    write_instrument(instrument, writer)
    file_tail = getattr(instrument, '_file_tail', None)
    if file_tail is not None:
        writer.write_bytes(file_tail)
    output = writer.to_bytes()

    if data != output:
        # Find first difference for diagnostic
        for i, (a, b) in enumerate(zip(data, output)):
            if a != b:
                ctx_start = max(0, i - 4)
                ctx_end = min(len(data), i + 8)
                pytest.fail(
                    f"{path.name}: first diff at byte {i} "
                    f"(0x{i:04X}): expected 0x{a:02X}, got 0x{b:02X}\n"
                    f"  input  [{ctx_start}:{ctx_end}]: {data[ctx_start:ctx_end].hex(' ')}\n"
                    f"  output [{ctx_start}:{ctx_end}]: {output[ctx_start:ctx_end].hex(' ')}"
                )
        if len(data) != len(output):
            pytest.fail(
                f"{path.name}: size mismatch: expected {len(data)}, got {len(output)}"
            )
