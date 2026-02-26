from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import HEADER_MAGIC
from m8py.format.errors import M8ParseError

HEADER_MAGIC_BYTE = 0x10


@dataclass
class M8Version:
    major: int
    minor: int
    patch: int
    _header_tail: bytes = b"\x00\x10"

    def at_least(self, major: int, minor: int) -> bool:
        return self.major > major or (self.major == major and self.minor >= minor)

    @property
    def caps(self) -> VersionCapabilities:
        return VersionCapabilities.from_version(self)


@dataclass(frozen=True)
class VersionCapabilities:
    has_scales: bool
    has_new_modulators: bool
    has_hypersynth: bool
    has_external: bool
    has_eq: bool
    has_expanded_eq: bool

    @staticmethod
    def from_version(v: M8Version) -> VersionCapabilities:
        return VersionCapabilities(
            has_scales=v.at_least(2, 5),
            has_new_modulators=v.at_least(3, 0),
            has_hypersynth=v.at_least(3, 0),
            has_external=v.at_least(3, 0),
            has_eq=v.at_least(4, 0),
            has_expanded_eq=v.at_least(4, 1),
        )


class M8FileType:
    @staticmethod
    def from_reader(reader: M8FileReader) -> M8Version:
        magic = reader.read_bytes(10)
        if magic != HEADER_MAGIC:
            raise M8ParseError(f"bad magic: expected {HEADER_MAGIC!r}, got {magic!r}")
        lsb = reader.read()
        msb = reader.read()
        major = msb & 0x0F
        minor = (lsb >> 4) & 0x0F
        patch = lsb & 0x0F
        header_tail = reader.read_bytes(2)
        return M8Version(major, minor, patch, _header_tail=header_tail)

    @staticmethod
    def write_header(writer: M8FileWriter, version: M8Version) -> None:
        writer.write_bytes(HEADER_MAGIC)
        lsb = (version.minor << 4) | version.patch
        writer.write(lsb)
        writer.write(version.major)
        writer.write_bytes(version._header_tail)
