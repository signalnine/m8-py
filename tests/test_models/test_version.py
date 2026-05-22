import pytest
from m8py.models.version import M8Version, VersionCapabilities, M8FileType
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import HEADER_MAGIC
from m8py.format.errors import M8ParseError

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


@pytest.mark.parametrize(
    "major,minor,patch",
    [
        (16, 0, 0),
        (0, 16, 0),
        (0, 0, 16),
        (255, 0, 0),
        (-1, 0, 0),
    ],
)
def test_write_header_rejects_out_of_range_components(major, minor, patch):
    w = M8FileWriter()
    version = M8Version(major, minor, patch)
    with pytest.raises(M8ParseError, match="out of range"):
        M8FileType.write_header(w, version)


def test_from_reader_rejects_reserved_msb_high_nibble():
    data = HEADER_MAGIC + bytes([0x10, 0x14, 0x00, 0x10])
    r = M8FileReader(data)
    with pytest.raises(M8ParseError, match="reserved high nibble"):
        M8FileType.from_reader(r)


def test_write_header_max_in_range_components_roundtrip():
    w = M8FileWriter()
    version = M8Version(15, 15, 15)
    M8FileType.write_header(w, version)
    r = M8FileReader(w.to_bytes())
    v = M8FileType.from_reader(r)
    assert v.major == 15 and v.minor == 15 and v.patch == 15


def test_version_equality_ignores_header_tail():
    """A loaded version with arbitrary header_tail must equal a constructed
    version with the same (major, minor, patch). _header_tail is an internal
    roundtrip field, not part of the version identity.
    """
    v1 = M8Version(6, 5, 0)
    v2 = M8Version(6, 5, 0, _header_tail=b"\x01\x02")
    assert v1 == v2
