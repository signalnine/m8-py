from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from m8py.format.constants import (
    EMPTY, HEADER_SIZE,
    N_SONG_STEPS, N_PHRASES, N_CHAINS, N_INSTRUMENTS,
    N_TABLES, N_GROOVES, N_SCALES, N_MIDI_MAPPINGS,
)
from m8py.format.offsets import offsets_for_version
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.chain import Chain
from m8py.models.eq import EQ
from m8py.models.groove import Groove
from m8py.models.instrument import Instrument, EmptyInstrument, read_instrument, write_instrument
from m8py.models.midi import MIDIMapping
from m8py.models.phrase import Phrase
from m8py.models.scale import Scale
from m8py.models.settings import MIDISettings, MixerSettings, EffectsSettings
from m8py.models.song_step import SongStep
from m8py.models.table import Table
from m8py.models.version import M8Version, M8FileType


@dataclass
class Song:
    version: M8Version = field(default_factory=lambda: M8Version(4, 1, 0))
    directory: bytes = field(default_factory=lambda: bytes(128))
    transpose: int = 0
    tempo: float = 120.0
    quantize: int = 0
    name: str = ""
    midi_settings: MIDISettings = field(default_factory=MIDISettings)
    key: int = 0
    mixer_settings: MixerSettings = field(default_factory=MixerSettings)
    grooves: List[Groove] = field(default_factory=lambda: [Groove() for _ in range(N_GROOVES)])
    song_steps: List[SongStep] = field(default_factory=lambda: [SongStep() for _ in range(N_SONG_STEPS)])
    phrases: List[Phrase] = field(default_factory=lambda: [Phrase() for _ in range(N_PHRASES)])
    chains: List[Chain] = field(default_factory=lambda: [Chain() for _ in range(N_CHAINS)])
    tables: List[Table] = field(default_factory=lambda: [Table() for _ in range(N_TABLES)])
    instruments: List[Instrument] = field(default_factory=lambda: [EmptyInstrument() for _ in range(N_INSTRUMENTS)])
    effects_settings: EffectsSettings = field(default_factory=EffectsSettings)
    midi_mappings: List[MIDIMapping] = field(default_factory=lambda: [MIDIMapping() for _ in range(N_MIDI_MAPPINGS)])
    scales: List[Scale] = field(default_factory=lambda: [Scale() for _ in range(N_SCALES)])
    eqs: List[EQ] = field(default_factory=list)

    @staticmethod
    def from_reader(reader: M8FileReader, version: M8Version) -> Song:
        offsets = offsets_for_version(version)

        # Header section (after 14-byte file header)
        directory = reader.read_bytes(128)
        transpose = reader.read()
        tempo = reader.read_float_le()
        quantize = reader.read()
        name = reader.read_str(12)
        midi_settings = MIDISettings.from_reader(reader)
        key = reader.read()
        reader.skip(18)  # reserved
        mixer_settings = MixerSettings.from_reader(reader)

        # Seek-based sections
        reader.seek(offsets.groove)
        grooves = [Groove.from_reader(reader) for _ in range(N_GROOVES)]

        reader.seek(offsets.song)
        song_steps = [SongStep.from_reader(reader) for _ in range(N_SONG_STEPS)]

        reader.seek(offsets.phrases)
        phrases = [Phrase.from_reader(reader) for _ in range(N_PHRASES)]

        reader.seek(offsets.chains)
        chains = [Chain.from_reader(reader) for _ in range(N_CHAINS)]

        reader.seek(offsets.table)
        tables = [Table.from_reader(reader) for _ in range(N_TABLES)]

        reader.seek(offsets.instruments)
        instruments = [read_instrument(reader, version) for _ in range(N_INSTRUMENTS)]

        reader.skip(3)  # padding after instruments
        effects_settings = EffectsSettings.from_reader(reader, version)

        reader.seek(offsets.midi_mapping)
        midi_mappings = [MIDIMapping.from_reader(reader) for _ in range(N_MIDI_MAPPINGS)]

        scales: List[Scale]
        if version.caps.has_scales and offsets.scale is not None:
            reader.seek(offsets.scale)
            scales = [Scale.from_reader(reader) for _ in range(N_SCALES)]
        else:
            scales = [Scale() for _ in range(N_SCALES)]

        eqs: List[EQ] = []
        if version.caps.has_eq and offsets.eq is not None:
            reader.seek(offsets.eq)
            eqs = [EQ.from_reader(reader) for _ in range(offsets.instrument_eq_count)]

        return Song(
            version=version,
            directory=directory,
            transpose=transpose,
            tempo=tempo,
            quantize=quantize,
            name=name,
            midi_settings=midi_settings,
            key=key,
            mixer_settings=mixer_settings,
            grooves=grooves,
            song_steps=song_steps,
            phrases=phrases,
            chains=chains,
            tables=tables,
            instruments=instruments,
            effects_settings=effects_settings,
            midi_mappings=midi_mappings,
            scales=scales,
            eqs=eqs,
        )

    def write(self, writer: M8FileWriter) -> None:
        version = self.version
        offsets = offsets_for_version(version)

        # Write header
        M8FileType.write_header(writer, version)

        # Header section
        writer.write_bytes(self.directory[:128])
        if len(self.directory) < 128:
            writer.pad(128 - len(self.directory))
        writer.write(self.transpose)
        writer.write_float_le(self.tempo)
        writer.write(self.quantize)
        writer.write_str(self.name, 12)
        self.midi_settings.write(writer)
        writer.write(self.key)
        writer.pad(18)  # reserved
        self.mixer_settings.write(writer)

        # Pad to groove offset
        _pad_to(writer, offsets.groove)
        for g in self.grooves:
            g.write(writer)

        _pad_to(writer, offsets.song)
        for s in self.song_steps:
            s.write(writer)

        _pad_to(writer, offsets.phrases)
        for p in self.phrases:
            p.write(writer)

        _pad_to(writer, offsets.chains)
        for c in self.chains:
            c.write(writer)

        _pad_to(writer, offsets.table)
        for t in self.tables:
            t.write(writer)

        _pad_to(writer, offsets.instruments)
        for inst in self.instruments:
            write_instrument(inst, writer)

        writer.pad(3)  # padding after instruments
        self.effects_settings.write(writer)

        _pad_to(writer, offsets.midi_mapping)
        for m in self.midi_mappings:
            m.write(writer)

        if version.caps.has_scales and offsets.scale is not None:
            _pad_to(writer, offsets.scale)
            for s in self.scales:
                s.write(writer)

        if version.caps.has_eq and offsets.eq is not None:
            _pad_to(writer, offsets.eq)
            for i in range(offsets.instrument_eq_count):
                if i < len(self.eqs):
                    self.eqs[i].write(writer)
                else:
                    EQ().write(writer)


def _pad_to(writer: M8FileWriter, target: int) -> None:
    """Pad the writer to reach the target offset."""
    current = writer.position()
    if current < target:
        writer.pad(target - current)
