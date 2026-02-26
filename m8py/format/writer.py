import struct
from m8py.format.errors import M8ParseError


class M8FileWriter:
    """Sequential byte writer for M8 binary files."""

    def __init__(self) -> None:
        self._buf = bytearray()

    def write(self, byte: int) -> None:
        self._buf.append(byte & 0xFF)

    def write_bytes(self, data: bytes) -> None:
        self._buf.extend(data)

    def write_str(self, s: str, length: int) -> None:
        encoded = s.encode("ascii")[:length]
        self._buf.extend(encoded)
        self._buf.extend(b"\x00" * (length - len(encoded)))

    def write_float_le(self, value: float) -> None:
        self._buf.extend(struct.pack("<f", value))

    def write_bool(self, value: bool) -> None:
        self._buf.append(1 if value else 0)

    def write_u16_le(self, value: int) -> None:
        self._buf.extend(struct.pack("<H", value))

    def pad(self, n: int, value: int = 0x00) -> None:
        self._buf.extend(bytes([value]) * n)

    def position(self) -> int:
        return len(self._buf)

    def to_bytes(self) -> bytes:
        return bytes(self._buf)

    def expect_written(self, n: int, start: int) -> None:
        actual = len(self._buf) - start
        if actual != n:
            raise M8ParseError(
                f"expected {n} bytes written from offset {start}, got {actual}"
            )
