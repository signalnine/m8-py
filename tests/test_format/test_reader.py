import struct
import pytest
from m8py.format.reader import M8FileReader
from m8py.format.errors import M8ParseError

def test_read_byte():
    r = M8FileReader(bytes([0x42, 0xFF]))
    assert r.read() == 0x42
    assert r.read() == 0xFF

def test_read_bytes():
    r = M8FileReader(b"\x01\x02\x03\x04")
    assert r.read_bytes(2) == b"\x01\x02"
    assert r.read_bytes(2) == b"\x03\x04"

def test_read_past_end_raises():
    r = M8FileReader(b"\x01")
    r.read()
    with pytest.raises(M8ParseError, match="EOF"):
        r.read()

def test_read_bytes_past_end_raises():
    r = M8FileReader(b"\x01\x02")
    with pytest.raises(M8ParseError):
        r.read_bytes(5)

def test_read_str_null_terminated():
    r = M8FileReader(b"HELLO\x00\x00\x00\x00\x00\x00\x00")
    assert r.read_str(12) == "HELLO"
    assert r.position() == 12

def test_read_str_ff_terminated():
    r = M8FileReader(b"AB\xFF\xFF\xFF\xFF")
    assert r.read_str(6) == "AB"
    assert r.position() == 6

def test_read_str_empty_ff_fill():
    r = M8FileReader(bytes([0xFF] * 12))
    assert r.read_str(12) == ""

def test_read_float_le():
    data = struct.pack("<f", 120.0)
    r = M8FileReader(data)
    assert r.read_float_le() == pytest.approx(120.0)

def test_read_bool():
    r = M8FileReader(b"\x01\x00")
    assert r.read_bool() is True
    assert r.read_bool() is False

def test_read_u16_le():
    r = M8FileReader(b"\x34\x12")
    assert r.read_u16_le() == 0x1234

def test_position_and_seek():
    r = M8FileReader(b"\x00\x01\x02\x03\x04")
    assert r.position() == 0
    r.seek(3)
    assert r.position() == 3
    assert r.read() == 0x03

def test_seek_out_of_bounds():
    r = M8FileReader(b"\x00\x01")
    with pytest.raises(M8ParseError):
        r.seek(100)

def test_skip():
    r = M8FileReader(b"\x00\x01\x02\x03")
    r.skip(2)
    assert r.read() == 0x02

def test_remaining():
    r = M8FileReader(b"\x00\x01\x02")
    assert r.remaining() == 3
    r.read()
    assert r.remaining() == 2

def test_expect_consumed_pass():
    r = M8FileReader(bytes(215))
    start = r.position()
    r.skip(215)
    r.expect_consumed(215, start)

def test_expect_consumed_fail():
    r = M8FileReader(bytes(215))
    start = r.position()
    r.skip(200)
    with pytest.raises(M8ParseError, match="expected 215.*got 200"):
        r.expect_consumed(215, start)
