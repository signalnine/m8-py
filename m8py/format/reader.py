import struct
from m8py.format.errors import M8ParseError


class M8FileReader:
    """Cursor-based sequential byte reader for M8 binary files."""

    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0

    def read(self) -> int:
        if self._pos >= len(self._data):
            raise M8ParseError(f"EOF: attempted read at offset {self._pos}")
        val = self._data[self._pos]
        self._pos += 1
        return val

    def read_bytes(self, n: int) -> bytes:
        if self._pos + n > len(self._data):
            raise M8ParseError(
                f"EOF: need {n} bytes at offset {self._pos}, "
                f"only {len(self._data) - self._pos} remaining"
            )
        val = self._data[self._pos : self._pos + n]
        self._pos += n
        return val

    def read_str(self, n: int) -> str:
        raw = self.read_bytes(n)
        result = []
        for b in raw:
            if b == 0x00 or b == 0xFF:
                break
            result.append(chr(b))
        return "".join(result)

    def read_float_le(self) -> float:
        data = self.read_bytes(4)
        return struct.unpack("<f", data)[0]

    def read_bool(self) -> bool:
        return self.read() != 0

    def read_u16_le(self) -> int:
        data = self.read_bytes(2)
        return struct.unpack("<H", data)[0]

    def position(self) -> int:
        return self._pos

    def seek(self, offset: int) -> None:
        if offset < 0 or offset > len(self._data):
            raise M8ParseError(
                f"seek to {offset} out of bounds (size={len(self._data)})"
            )
        self._pos = offset

    def skip(self, n: int) -> None:
        self._pos += n

    def remaining(self) -> int:
        return max(0, len(self._data) - self._pos)

    def expect_consumed(self, n: int, start: int) -> None:
        actual = self._pos - start
        if actual != n:
            raise M8ParseError(
                f"expected {n} bytes consumed from offset {start}, got {actual}"
            )
