import struct
import pytest
from m8py.format.writer import M8FileWriter
from m8py.format.errors import M8ParseError

def test_write_byte():
    w = M8FileWriter()
    w.write(0x42)
    w.write(0xFF)
    assert w.to_bytes() == bytes([0x42, 0xFF])

def test_write_bytes():
    w = M8FileWriter()
    w.write_bytes(b"\x01\x02\x03")
    assert w.to_bytes() == b"\x01\x02\x03"

def test_write_str_padded():
    w = M8FileWriter()
    w.write_str("HELLO", 12)
    data = w.to_bytes()
    assert len(data) == 12
    assert data[:5] == b"HELLO"
    assert data[5:] == b"\x00" * 7

def test_write_str_truncation():
    w = M8FileWriter()
    w.write_str("A" * 20, 12)
    data = w.to_bytes()
    assert len(data) == 12
    assert data == b"AAAAAAAAAAA\x00"

def test_write_str_empty():
    w = M8FileWriter()
    w.write_str("", 12)
    assert w.to_bytes() == b"\x00" * 12

def test_write_float_le():
    w = M8FileWriter()
    w.write_float_le(120.0)
    assert w.to_bytes() == struct.pack("<f", 120.0)

def test_write_bool():
    w = M8FileWriter()
    w.write_bool(True)
    w.write_bool(False)
    assert w.to_bytes() == b"\x01\x00"

def test_write_u16_le():
    w = M8FileWriter()
    w.write_u16_le(0x1234)
    assert w.to_bytes() == b"\x34\x12"

def test_pad():
    w = M8FileWriter()
    w.pad(5, 0xFF)
    assert w.to_bytes() == bytes([0xFF] * 5)

def test_pad_default_zero():
    w = M8FileWriter()
    w.pad(3)
    assert w.to_bytes() == b"\x00\x00\x00"

def test_position():
    w = M8FileWriter()
    assert w.position() == 0
    w.write(0x42)
    assert w.position() == 1
    w.write_bytes(b"\x01\x02\x03")
    assert w.position() == 4

def test_expect_written_pass():
    w = M8FileWriter()
    start = w.position()
    w.pad(215)
    w.expect_written(215, start)

def test_expect_written_fail():
    w = M8FileWriter()
    start = w.position()
    w.pad(200)
    with pytest.raises(M8ParseError, match="expected 215.*got 200"):
        w.expect_written(215, start)
