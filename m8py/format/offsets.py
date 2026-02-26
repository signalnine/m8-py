from __future__ import annotations
from dataclasses import dataclass
from m8py.models.version import M8Version


@dataclass(frozen=True)
class SongOffsets:
    groove: int
    song: int
    phrases: int
    chains: int
    table: int
    instruments: int
    effect_settings: int
    midi_mapping: int
    scale: int | None
    eq: int | None
    instrument_eq_count: int
    instrument_file_eq_offset: int | None


V2_OFFSETS = SongOffsets(
    groove=0xEE, song=0x2EE, phrases=0xAEE,
    chains=0x9A5E, table=0xBA3E, instruments=0x13A3E,
    effect_settings=0x1A5C1, midi_mapping=0x1A5FE,
    scale=None, eq=None,
    instrument_eq_count=0, instrument_file_eq_offset=None,
)

V25_OFFSETS = SongOffsets(
    groove=0xEE, song=0x2EE, phrases=0xAEE,
    chains=0x9A5E, table=0xBA3E, instruments=0x13A3E,
    effect_settings=0x1A5C1, midi_mapping=0x1A5FE,
    scale=0x1AA7E, eq=None,
    instrument_eq_count=0, instrument_file_eq_offset=None,
)

V3_OFFSETS = V25_OFFSETS

V4_OFFSETS = SongOffsets(
    groove=0xEE, song=0x2EE, phrases=0xAEE,
    chains=0x9A5E, table=0xBA3E, instruments=0x13A3E,
    effect_settings=0x1A5C1, midi_mapping=0x1A5FE,
    scale=0x1AA7E, eq=0x1AD5E,
    instrument_eq_count=32, instrument_file_eq_offset=None,
)

V4_1_OFFSETS = SongOffsets(
    groove=0xEE, song=0x2EE, phrases=0xAEE,
    chains=0x9A5E, table=0xBA3E, instruments=0x13A3E,
    effect_settings=0x1A5C1, midi_mapping=0x1A5FE,
    scale=0x1AA7E, eq=0x1AD5E,
    instrument_eq_count=128, instrument_file_eq_offset=0x165,
)


def offsets_for_version(version: M8Version) -> SongOffsets:
    if version.at_least(4, 1):
        return V4_1_OFFSETS
    if version.at_least(4, 0):
        return V4_OFFSETS
    if version.at_least(2, 5):
        return V25_OFFSETS
    return V2_OFFSETS
