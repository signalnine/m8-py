"""High-level I/O for loading and saving M8 files.

Supports all four M8 file types: Song (.m8s), Instrument (.m8i),
Theme (.m8t), and Scale (.m8n).
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from m8py.format.constants import FileType, HEADER_SIZE
from m8py.format.errors import M8ParseError
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.instrument import Instrument, read_instrument, write_instrument
from m8py.models.scale import Scale
from m8py.models.song import Song
from m8py.models.theme import Theme
from m8py.models.version import M8FileType, M8Version

_EXT_TO_FILE_TYPE = {
    ".m8s": FileType.SONG,
    ".m8i": FileType.INSTRUMENT,
    ".m8t": FileType.THEME,
    ".m8n": FileType.SCALE,
}


def load(path: Union[str, Path]) -> Song | Instrument | Theme | Scale:
    """Load an M8 file, detecting file type from extension."""
    path = Path(path)
    data = path.read_bytes()
    if len(data) < HEADER_SIZE:
        raise M8ParseError(
            f"file too small: {len(data)} bytes, need at least {HEADER_SIZE}"
        )
    ext = path.suffix.lower()
    file_type = _EXT_TO_FILE_TYPE.get(ext)
    if file_type is None:
        raise M8ParseError(f"unknown M8 file extension: {ext!r}")
    reader = M8FileReader(data)
    version = M8FileType.from_reader(reader)
    return _dispatch_read(reader, version, file_type)


def load_song(path: Union[str, Path]) -> Song:
    """Load an M8 song file (.m8s)."""
    obj = load(path)
    if not isinstance(obj, Song):
        raise M8ParseError(f"expected SONG file, got {type(obj).__name__}")
    return obj


def load_instrument(path: Union[str, Path]) -> Instrument:
    """Load an M8 instrument file (.m8i)."""
    obj = load(path)
    if isinstance(obj, (Song, Theme, Scale)):
        raise M8ParseError(f"expected INSTRUMENT file, got {type(obj).__name__}")
    return obj  # It's an Instrument


def load_theme(path: Union[str, Path]) -> Theme:
    """Load an M8 theme file (.m8t)."""
    obj = load(path)
    if not isinstance(obj, Theme):
        raise M8ParseError(f"expected THEME file, got {type(obj).__name__}")
    return obj


def load_scale(path: Union[str, Path]) -> Scale:
    """Load an M8 scale file (.m8n)."""
    obj = load(path)
    if not isinstance(obj, Scale):
        raise M8ParseError(f"expected SCALE file, got {type(obj).__name__}")
    return obj


def save(obj: Song | Instrument | Theme | Scale, path: Union[str, Path]) -> None:
    """Save an M8 object to a file."""
    writer = M8FileWriter()
    version = M8Version(4, 1, 0)  # default version

    if isinstance(obj, Song):
        # Song.write() handles header internally
        obj.write(writer)
    elif isinstance(obj, Theme):
        M8FileType.write_header(writer, version)
        obj.write(writer)
    elif isinstance(obj, Scale):
        M8FileType.write_header(writer, version)
        obj.write(writer)
    else:
        # Instrument types
        M8FileType.write_header(writer, version)
        write_instrument(obj, writer)

    Path(path).write_bytes(writer.to_bytes())


def _dispatch_read(
    reader: M8FileReader, version: M8Version, file_type: FileType
) -> Song | Instrument | Theme | Scale:
    """Dispatch reading based on file type."""
    if file_type == FileType.SONG:
        return Song.from_reader(reader, version)
    elif file_type == FileType.INSTRUMENT:
        return read_instrument(reader, version)
    elif file_type == FileType.THEME:
        return Theme.from_reader(reader)
    elif file_type == FileType.SCALE:
        return Scale.from_reader(reader)
    else:
        raise M8ParseError(f"unsupported file type: {file_type}")
