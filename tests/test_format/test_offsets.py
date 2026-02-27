from m8py.format.offsets import SongOffsets, offsets_for_version, V4_OFFSETS, V4_1_OFFSETS
from m8py.models.version import M8Version

def test_v4_offsets():
    assert V4_OFFSETS.groove == 0xEE
    assert V4_OFFSETS.instruments == 0x13A3E
    assert V4_OFFSETS.eq == 0x1AD5E
    assert V4_OFFSETS.instrument_eq_count == 36  # 32 instruments + 3 effects + 1 global

def test_v41_offsets():
    assert V4_1_OFFSETS.instrument_eq_count == 132  # 128 instruments + 3 effects + 1 global
    assert V4_1_OFFSETS.instrument_file_eq_offset == 0x165

def test_offsets_for_v41():
    assert offsets_for_version(M8Version(4, 1, 0)).instrument_eq_count == 132

def test_offsets_for_v4():
    assert offsets_for_version(M8Version(4, 0, 0)).instrument_eq_count == 36

def test_offsets_for_v3():
    o = offsets_for_version(M8Version(3, 0, 0))
    assert o.scale is not None and o.eq is None

def test_offsets_for_v2():
    o = offsets_for_version(M8Version(2, 0, 0))
    assert o.scale is None and o.eq is None
