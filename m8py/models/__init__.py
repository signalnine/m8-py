"""M8 data models for songs, instruments, and related structures."""

from m8py.models.song import Song
from m8py.models.version import M8Version, VersionCapabilities
from m8py.models.instrument import (
    WavSynth, MacroSynth, Sampler, FMSynth, HyperSynth,
    External, MIDIOut, EmptyInstrument, SynthCommon, Instrument,
)
from m8py.models.phrase import Phrase, PhraseStep
from m8py.models.chain import Chain, ChainStep
from m8py.models.table import Table, TableStep
from m8py.models.groove import Groove
from m8py.models.song_step import SongStep
from m8py.models.theme import Theme, RGB
from m8py.models.scale import Scale, NoteInterval
from m8py.models.eq import EQ, EQBand
from m8py.models.fx import FX
from m8py.models.settings import MIDISettings, MixerSettings, EffectsSettings
from m8py.models.midi import MIDIMapping

__all__ = [
    "Song", "M8Version", "VersionCapabilities",
    "WavSynth", "MacroSynth", "Sampler", "FMSynth", "HyperSynth",
    "External", "MIDIOut", "EmptyInstrument", "SynthCommon", "Instrument",
    "Phrase", "PhraseStep", "Chain", "ChainStep", "Table", "TableStep",
    "Groove", "SongStep", "Theme", "RGB", "Scale", "NoteInterval",
    "EQ", "EQBand", "FX", "MIDISettings", "MixerSettings", "EffectsSettings",
    "MIDIMapping",
]
