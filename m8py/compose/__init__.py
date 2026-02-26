"""Composition tools for building M8 songs programmatically."""

from m8py.compose.builder import SongBuilder
from m8py.compose.declarative import compose, TrackDef
from m8py.compose.allocator import SlotAllocator
from m8py.compose.notation import normalize_note, parse_pattern, NOTE_OFF
from m8py.compose.samples import export_to_sdcard, ExportResult

__all__ = [
    "SongBuilder", "compose", "TrackDef", "SlotAllocator",
    "normalize_note", "parse_pattern", "NOTE_OFF",
    "export_to_sdcard", "ExportResult",
]
