from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import HEADER_MAGIC, FileType
from m8py.format.errors import M8ParseError


@dataclass
class M8Version:
    major: int
    minor: int
    patch: int

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
    def from_reader(reader: M8FileReader) -> tuple[M8Version, FileType]:
        magic = reader.read_bytes(10)
        if magic != HEADER_MAGIC:
            raise M8ParseError(f"bad magic: expected {HEADER_MAGIC!r}, got {magic!r}")
        lsb = reader.read()
        msb = reader.read()
        major = msb & 0x0F
        minor = (lsb >> 4) & 0x0F
        patch = lsb & 0x0F
        file_type_nibble = (msb >> 4) & 0x0F
        reader.skip(2)
        try:
            file_type = FileType(file_type_nibble)
        except ValueError:
            raise M8ParseError(f"unknown file type nibble: 0x{file_type_nibble:X}")
        return M8Version(major, minor, patch), file_type

    @staticmethod
    def write_header(writer: M8FileWriter, version: M8Version, file_type: FileType) -> None:
        writer.write_bytes(HEADER_MAGIC)
        lsb = (version.minor << 4) | version.patch
        msb = (file_type.value << 4) | version.major
        writer.write(lsb)
        writer.write(msb)
        writer.pad(2)
