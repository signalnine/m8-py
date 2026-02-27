import pytest
from m8py.models.version import M8Version, VersionCapabilities, M8FileType
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import HEADER_MAGIC

def test_version_from_reader():
    data = HEADER_MAGIC + bytes([0x10, 0x04, 0x00, 0x10])
    r = M8FileReader(data)
    version = M8FileType.from_reader(r)
    assert version.major == 4
    assert version.minor == 1
    assert version.patch == 0

def test_version_2_7_8():
    data = HEADER_MAGIC + bytes([0x78, 0x02, 0x00, 0x10])
    r = M8FileReader(data)
    version = M8FileType.from_reader(r)
    assert version.major == 2
    assert version.minor == 7
    assert version.patch == 8

def test_version_write_roundtrip():
    w = M8FileWriter()
    version = M8Version(4, 1, 0)
    M8FileType.write_header(w, version)
    data = w.to_bytes()
    assert len(data) == 14
    assert data[12] == 0x00  # header tail byte 1
    assert data[13] == 0x00  # header tail byte 2
    r = M8FileReader(data)
    v = M8FileType.from_reader(r)
    assert v.major == 4 and v.minor == 1 and v.patch == 0

def test_version_at_least():
    v = M8Version(3, 2, 0)
    assert v.at_least(3, 0)
    assert v.at_least(3, 2)
    assert not v.at_least(3, 3)
    assert not v.at_least(4, 0)
    assert v.at_least(2, 5)

def test_caps_v1():
    c = M8Version(1, 0, 0).caps
    assert not c.has_scales
    assert not c.has_new_modulators
    assert not c.has_hypersynth
    assert not c.has_eq

def test_caps_v25():
    c = M8Version(2, 5, 0).caps
    assert c.has_scales
    assert not c.has_new_modulators

def test_caps_v3():
    c = M8Version(3, 0, 0).caps
    assert c.has_scales and c.has_new_modulators and c.has_hypersynth
    assert not c.has_eq

def test_caps_v4():
    c = M8Version(4, 0, 0).caps
    assert c.has_eq and not c.has_expanded_eq

def test_caps_v41():
    c = M8Version(4, 1, 0).caps
    assert c.has_eq and c.has_expanded_eq
