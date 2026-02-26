"""All M8 instrument types with 215-byte binary enforcement.

Binary layout (all instruments, 215 bytes total):

    Offset 0:     kind byte (1 byte)
    Offsets 1-62: instrument-specific header + engine params + gap
    Offset 63:    4 modulators (24 bytes)
    Offset 87:    tail data (128 bytes) -- sample_path, chords, or padding
    Offset 215:   end

Synth instruments share a common prefix (offsets 1-27):
    name(12), transp_eq(1), table_tick(1), volume(1), pitch(1), fine_tune(1),
    filter_type(1), filter_cutoff(1), filter_res(1), amp(1), limit(1),
    mixer_pan(1), mixer_dry(1), mixer_chorus(1), mixer_delay(1), mixer_reverb(1)

Engine-specific params follow at offset 28.  A gap (with optional EQ data
for firmware >= 4.0) fills from end-of-engine to offset 63.

MIDIOut has a different prefix but still places modulators at offset 63.
EmptyInstrument (kind 0xFF) is 1 + 214 zero bytes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from m8py.format.constants import INSTRUMENT_SIZE, InstrumentKind
from m8py.format.errors import M8ParseError
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.modulators import (
    Modulator, empty_modulator, mod_from_reader, mod_write, MOD_SIZE,
)
from m8py.models.version import M8Version

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_NUM_MODS = 4
_MOD_ABS_OFFSET = 63          # modulators always begin at byte 63 from kind
_TAIL_OFFSET = _MOD_ABS_OFFSET + _NUM_MODS * MOD_SIZE  # = 87
_TAIL_SIZE = INSTRUMENT_SIZE - _TAIL_OFFSET              # = 128
_COMMON_PREFIX_SIZE = 28       # kind(1) + name(12) + 5 common + 10 filter/mixer
_SAMPLE_PATH_LEN = 128
_HYPERSYNTH_CHORDS_SIZE = 112  # 16 chords × 7 bytes each


def _default_mods() -> List[Modulator]:
    return [empty_modulator() for _ in range(_NUM_MODS)]


# ---------------------------------------------------------------------------
# Shared synth-instrument common fields
# ---------------------------------------------------------------------------

@dataclass
class SynthCommon:
    """Fields shared by WavSynth, MacroSynth, Sampler, FMSynth,
    HyperSynth, and External instruments (offsets 1-27 after kind byte)."""

    name: str = ""
    transp_eq: int = 0
    table_tick: int = 0
    volume: int = 0
    pitch: int = 0
    fine_tune: int = 0x80
    filter_type: int = 0
    filter_cutoff: int = 0xFF
    filter_res: int = 0
    amp: int = 0
    limit: int = 0
    mixer_pan: int = 0x80
    mixer_dry: int = 0xC0
    mixer_chorus: int = 0
    mixer_delay: int = 0
    mixer_reverb: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> SynthCommon:
        return SynthCommon(
            name=reader.read_str(12),
            transp_eq=reader.read(),
            table_tick=reader.read(),
            volume=reader.read(),
            pitch=reader.read(),
            fine_tune=reader.read(),
            filter_type=reader.read(),
            filter_cutoff=reader.read(),
            filter_res=reader.read(),
            amp=reader.read(),
            limit=reader.read(),
            mixer_pan=reader.read(),
            mixer_dry=reader.read(),
            mixer_chorus=reader.read(),
            mixer_delay=reader.read(),
            mixer_reverb=reader.read(),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write_str(self.name, 12)
        writer.write(self.transp_eq)
        writer.write(self.table_tick)
        writer.write(self.volume)
        writer.write(self.pitch)
        writer.write(self.fine_tune)
        writer.write(self.filter_type)
        writer.write(self.filter_cutoff)
        writer.write(self.filter_res)
        writer.write(self.amp)
        writer.write(self.limit)
        writer.write(self.mixer_pan)
        writer.write(self.mixer_dry)
        writer.write(self.mixer_chorus)
        writer.write(self.mixer_delay)
        writer.write(self.mixer_reverb)


# ---------------------------------------------------------------------------
# Helper: read/write modulators at absolute offset 63 and enforce tail
# ---------------------------------------------------------------------------

def _read_gap_and_mods(reader: M8FileReader, inst_start: int) -> tuple[bytes, List[Modulator]]:
    """Read gap bytes from current position to offset 63, then read 4 modulators."""
    current = reader.position()
    gap_start = current - inst_start
    gap_size = _MOD_ABS_OFFSET - gap_start
    gap = reader.read_bytes(gap_size) if gap_size > 0 else b""
    mods = [mod_from_reader(reader) for _ in range(_NUM_MODS)]
    return gap, mods


def _write_gap_and_mods(writer: M8FileWriter, gap: bytes, mods: List[Modulator],
                        inst_start: int) -> None:
    """Write gap bytes then 4 modulators at offset 63 from inst_start."""
    current = writer.position()
    target = inst_start + _MOD_ABS_OFFSET
    gap_needed = target - current
    if gap_needed < 0:
        raise M8ParseError(
            f"overflowed into modulator region: wrote {current - inst_start} "
            f"bytes, expected <= {_MOD_ABS_OFFSET}"
        )
    if gap and len(gap) == gap_needed:
        writer.write_bytes(gap)
    elif gap_needed > 0:
        writer.pad(gap_needed)
    for m in mods:
        mod_write(m, writer)


def _write_tail(writer: M8FileWriter, tail: bytes, inst_start: int) -> None:
    """Write tail bytes (128 bytes at offset 87), preserving raw data."""
    if tail and len(tail) == _TAIL_SIZE:
        writer.write_bytes(tail)
    else:
        _pad_to_end(writer, inst_start)


def _pad_to_end(writer: M8FileWriter, inst_start: int) -> None:
    """Pad from current position to exactly inst_start + INSTRUMENT_SIZE."""
    current = writer.position()
    remaining = (inst_start + INSTRUMENT_SIZE) - current
    if remaining < 0:
        raise M8ParseError(
            f"instrument overflow: wrote {current - inst_start} bytes, "
            f"max {INSTRUMENT_SIZE}"
        )
    if remaining > 0:
        writer.pad(remaining)


# ---------------------------------------------------------------------------
# Instrument types
# ---------------------------------------------------------------------------

@dataclass
class WavSynth:
    """WavSynth instrument (kind 0x00).

    Engine params (5 bytes at offset 28): shape, size, mult, warp, scan.
    MOD_OFFSET = 30 (gap of 30 between end-of-engine at offset 33 and mods at 63).
    """
    kind: int = InstrumentKind.WAVSYNTH
    common: SynthCommon = field(default_factory=SynthCommon)
    shape: int = 0
    size: int = 0
    mult: int = 0
    warp: int = 0
    scan: int = 0
    modulators: List[Modulator] = field(default_factory=_default_mods)
    _gap: bytes = b""
    _tail: bytes = b""

    @staticmethod
    def from_reader(reader: M8FileReader, inst_start: int, version: M8Version) -> WavSynth:
        common = SynthCommon.from_reader(reader)
        shape = reader.read()
        size = reader.read()
        mult = reader.read()
        warp = reader.read()
        scan = reader.read()
        gap, mods = _read_gap_and_mods(reader, inst_start)
        tail = reader.read_bytes(_TAIL_SIZE)
        return WavSynth(common=common, shape=shape, size=size,
                        mult=mult, warp=warp, scan=scan, modulators=mods,
                        _gap=gap, _tail=tail)

    def write(self, writer: M8FileWriter) -> None:
        inst_start = writer.position()
        writer.write(self.kind)
        self.common.write(writer)
        writer.write(self.shape)
        writer.write(self.size)
        writer.write(self.mult)
        writer.write(self.warp)
        writer.write(self.scan)
        _write_gap_and_mods(writer, self._gap, self.modulators, inst_start)
        _write_tail(writer, self._tail, inst_start)
        writer.expect_written(INSTRUMENT_SIZE, inst_start)


@dataclass
class MacroSynth:
    """MacroSynth instrument (kind 0x01).

    Engine params (5 bytes at offset 28): shape, timbre, color, degrade, redux.
    MOD_OFFSET = 30.
    """
    kind: int = InstrumentKind.MACROSYNTH
    common: SynthCommon = field(default_factory=SynthCommon)
    shape: int = 0
    timbre: int = 0
    color: int = 0
    degrade: int = 0
    redux: int = 0
    modulators: List[Modulator] = field(default_factory=_default_mods)
    _gap: bytes = b""
    _tail: bytes = b""

    @staticmethod
    def from_reader(reader: M8FileReader, inst_start: int, version: M8Version) -> MacroSynth:
        common = SynthCommon.from_reader(reader)
        shape = reader.read()
        timbre = reader.read()
        color = reader.read()
        degrade = reader.read()
        redux = reader.read()
        gap, mods = _read_gap_and_mods(reader, inst_start)
        tail = reader.read_bytes(_TAIL_SIZE)
        return MacroSynth(common=common, shape=shape, timbre=timbre,
                          color=color, degrade=degrade, redux=redux,
                          modulators=mods, _gap=gap, _tail=tail)

    def write(self, writer: M8FileWriter) -> None:
        inst_start = writer.position()
        writer.write(self.kind)
        self.common.write(writer)
        writer.write(self.shape)
        writer.write(self.timbre)
        writer.write(self.color)
        writer.write(self.degrade)
        writer.write(self.redux)
        _write_gap_and_mods(writer, self._gap, self.modulators, inst_start)
        _write_tail(writer, self._tail, inst_start)
        writer.expect_written(INSTRUMENT_SIZE, inst_start)


@dataclass
class Sampler:
    """Sampler instrument (kind 0x02).

    Engine params (6 bytes at offset 28): play_mode, slice, start,
    loop_start, length, degrade.  MOD_OFFSET = 29.
    Sample path (128 bytes) at offset 87 (in the tail region).
    """
    kind: int = InstrumentKind.SAMPLER
    common: SynthCommon = field(default_factory=SynthCommon)
    play_mode: int = 0
    slice: int = 0
    start: int = 0
    loop_start: int = 0
    length: int = 0xFF
    degrade: int = 0
    sample_path: str = ""
    modulators: List[Modulator] = field(default_factory=_default_mods)
    _gap: bytes = b""

    @staticmethod
    def from_reader(reader: M8FileReader, inst_start: int, version: M8Version) -> Sampler:
        common = SynthCommon.from_reader(reader)
        play_mode = reader.read()
        slice_ = reader.read()
        start = reader.read()
        loop_start = reader.read()
        length = reader.read()
        degrade = reader.read()
        gap, mods = _read_gap_and_mods(reader, inst_start)
        sample_path = reader.read_str(_SAMPLE_PATH_LEN)
        return Sampler(common=common, play_mode=play_mode, slice=slice_,
                       start=start, loop_start=loop_start, length=length,
                       degrade=degrade, sample_path=sample_path, modulators=mods,
                       _gap=gap)

    def write(self, writer: M8FileWriter) -> None:
        inst_start = writer.position()
        writer.write(self.kind)
        self.common.write(writer)
        writer.write(self.play_mode)
        writer.write(self.slice)
        writer.write(self.start)
        writer.write(self.loop_start)
        writer.write(self.length)
        writer.write(self.degrade)
        _write_gap_and_mods(writer, self._gap, self.modulators, inst_start)
        # Write sample path in tail region (offset 87)
        writer.write_str(self.sample_path, _SAMPLE_PATH_LEN)
        writer.expect_written(INSTRUMENT_SIZE, inst_start)


@dataclass
class FMOperator:
    """Single FM operator (7 bytes): shape, ratio, ratio_fine, level,
    feedback, mod_a, mod_b."""
    shape: int = 0
    ratio: int = 0x01
    ratio_fine: int = 0
    level: int = 0x80
    feedback: int = 0
    mod_a: int = 0
    mod_b: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> FMOperator:
        return FMOperator(
            shape=reader.read(), ratio=reader.read(),
            ratio_fine=reader.read(), level=reader.read(),
            feedback=reader.read(), mod_a=reader.read(), mod_b=reader.read(),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.shape)
        writer.write(self.ratio)
        writer.write(self.ratio_fine)
        writer.write(self.level)
        writer.write(self.feedback)
        writer.write(self.mod_a)
        writer.write(self.mod_b)


@dataclass
class FMSynth:
    """FMSynth instrument (kind 0x04).

    Engine params (33 bytes at offset 28): algo(1), operators(4 * 7 = 28),
    mod1-mod4(4).  MOD_OFFSET = 2.
    """
    kind: int = InstrumentKind.FMSYNTH
    common: SynthCommon = field(default_factory=SynthCommon)
    algo: int = 0
    operators: List[FMOperator] = field(
        default_factory=lambda: [FMOperator() for _ in range(4)]
    )
    mod1: int = 0
    mod2: int = 0
    mod3: int = 0
    mod4: int = 0
    modulators: List[Modulator] = field(default_factory=_default_mods)
    _gap: bytes = b""
    _tail: bytes = b""

    @staticmethod
    def from_reader(reader: M8FileReader, inst_start: int, version: M8Version) -> FMSynth:
        common = SynthCommon.from_reader(reader)
        algo = reader.read()
        operators = [FMOperator.from_reader(reader) for _ in range(4)]
        mod1 = reader.read()
        mod2 = reader.read()
        mod3 = reader.read()
        mod4 = reader.read()
        gap, mods = _read_gap_and_mods(reader, inst_start)
        tail = reader.read_bytes(_TAIL_SIZE)
        return FMSynth(common=common, algo=algo, operators=operators,
                       mod1=mod1, mod2=mod2, mod3=mod3, mod4=mod4,
                       modulators=mods, _gap=gap, _tail=tail)

    def write(self, writer: M8FileWriter) -> None:
        inst_start = writer.position()
        writer.write(self.kind)
        self.common.write(writer)
        writer.write(self.algo)
        for op in self.operators:
            op.write(writer)
        writer.write(self.mod1)
        writer.write(self.mod2)
        writer.write(self.mod3)
        writer.write(self.mod4)
        _write_gap_and_mods(writer, self._gap, self.modulators, inst_start)
        _write_tail(writer, self._tail, inst_start)
        writer.expect_written(INSTRUMENT_SIZE, inst_start)


@dataclass
class HyperSynth:
    """HyperSynth instrument (kind 0x05).

    Engine params (12 bytes at offset 28): default_chord(7), scale(1),
    shift(1), swarm(1), width(1), subosc(1).  MOD_OFFSET = 23.
    After modulators: 16 custom chords (16 bytes) in the tail region.
    """
    kind: int = InstrumentKind.HYPERSYNTH
    common: SynthCommon = field(default_factory=SynthCommon)
    default_chord: bytes = field(default_factory=lambda: bytes(7))
    scale: int = 0
    shift: int = 0
    swarm: int = 0
    width: int = 0
    subosc: int = 0
    custom_chords: bytes = field(default_factory=lambda: bytes(_HYPERSYNTH_CHORDS_SIZE))
    modulators: List[Modulator] = field(default_factory=_default_mods)
    _gap: bytes = b""
    _tail: bytes = b""

    @staticmethod
    def from_reader(reader: M8FileReader, inst_start: int, version: M8Version) -> HyperSynth:
        common = SynthCommon.from_reader(reader)
        default_chord = reader.read_bytes(7)
        scale = reader.read()
        shift = reader.read()
        swarm = reader.read()
        width = reader.read()
        subosc = reader.read()
        gap, mods = _read_gap_and_mods(reader, inst_start)
        custom_chords = reader.read_bytes(_HYPERSYNTH_CHORDS_SIZE)
        tail = reader.read_bytes(_TAIL_SIZE - _HYPERSYNTH_CHORDS_SIZE)
        return HyperSynth(common=common, default_chord=default_chord,
                          scale=scale, shift=shift, swarm=swarm,
                          width=width, subosc=subosc,
                          custom_chords=custom_chords, modulators=mods,
                          _gap=gap, _tail=tail)

    def write(self, writer: M8FileWriter) -> None:
        inst_start = writer.position()
        writer.write(self.kind)
        self.common.write(writer)
        writer.write_bytes(self.default_chord[:7])
        if len(self.default_chord) < 7:
            writer.pad(7 - len(self.default_chord))
        writer.write(self.scale)
        writer.write(self.shift)
        writer.write(self.swarm)
        writer.write(self.width)
        writer.write(self.subosc)
        _write_gap_and_mods(writer, self._gap, self.modulators, inst_start)
        writer.write_bytes(self.custom_chords[:_HYPERSYNTH_CHORDS_SIZE])
        if len(self.custom_chords) < _HYPERSYNTH_CHORDS_SIZE:
            writer.pad(_HYPERSYNTH_CHORDS_SIZE - len(self.custom_chords))
        _write_tail(writer, self._tail, inst_start)
        writer.expect_written(INSTRUMENT_SIZE, inst_start)


@dataclass
class External:
    """External instrument (kind 0x06).

    Engine params (13 bytes at offset 28): input(1), port(1), channel(1),
    bank(1), program(1), cca(2), ccb(2), ccc(2), ccd(2).  MOD_OFFSET = 22.
    """
    kind: int = InstrumentKind.EXTERNAL
    common: SynthCommon = field(default_factory=SynthCommon)
    input: int = 0
    port: int = 0
    channel: int = 0
    bank: int = 0
    program: int = 0
    cca: bytes = field(default_factory=lambda: bytes(2))
    ccb: bytes = field(default_factory=lambda: bytes(2))
    ccc: bytes = field(default_factory=lambda: bytes(2))
    ccd: bytes = field(default_factory=lambda: bytes(2))
    modulators: List[Modulator] = field(default_factory=_default_mods)
    _gap: bytes = b""
    _tail: bytes = b""

    @staticmethod
    def from_reader(reader: M8FileReader, inst_start: int, version: M8Version) -> External:
        common = SynthCommon.from_reader(reader)
        inp = reader.read()
        port = reader.read()
        channel = reader.read()
        bank = reader.read()
        program = reader.read()
        cca = reader.read_bytes(2)
        ccb = reader.read_bytes(2)
        ccc = reader.read_bytes(2)
        ccd = reader.read_bytes(2)
        gap, mods = _read_gap_and_mods(reader, inst_start)
        tail = reader.read_bytes(_TAIL_SIZE)
        return External(common=common, input=inp, port=port, channel=channel,
                        bank=bank, program=program, cca=cca, ccb=ccb,
                        ccc=ccc, ccd=ccd, modulators=mods, _gap=gap, _tail=tail)

    def write(self, writer: M8FileWriter) -> None:
        inst_start = writer.position()
        writer.write(self.kind)
        self.common.write(writer)
        writer.write(self.input)
        writer.write(self.port)
        writer.write(self.channel)
        writer.write(self.bank)
        writer.write(self.program)
        writer.write_bytes(self.cca[:2])
        if len(self.cca) < 2:
            writer.pad(2 - len(self.cca))
        writer.write_bytes(self.ccb[:2])
        if len(self.ccb) < 2:
            writer.pad(2 - len(self.ccb))
        writer.write_bytes(self.ccc[:2])
        if len(self.ccc) < 2:
            writer.pad(2 - len(self.ccc))
        writer.write_bytes(self.ccd[:2])
        if len(self.ccd) < 2:
            writer.pad(2 - len(self.ccd))
        _write_gap_and_mods(writer, self._gap, self.modulators, inst_start)
        _write_tail(writer, self._tail, inst_start)
        writer.expect_written(INSTRUMENT_SIZE, inst_start)


# ---------------------------------------------------------------------------
# MIDIOut -- completely different layout
# ---------------------------------------------------------------------------

@dataclass
class ControlChange:
    """A single MIDI CC entry (2 bytes): number and value."""
    number: int = 0xFF
    value: int = 0xFF

    @staticmethod
    def from_reader(reader: M8FileReader) -> ControlChange:
        return ControlChange(number=reader.read(), value=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.number)
        writer.write(self.value)


_NUM_CCS = 10


def _default_ccs() -> List[ControlChange]:
    return [ControlChange() for _ in range(_NUM_CCS)]


@dataclass
class MIDIOut:
    """MIDIOut instrument (kind 0x03).

    Layout (after kind byte):
      name(12), transpose(1), table_tick(1), port(1), channel(1),
      bank_select(1), program_change(1), skip(3), 10 ControlChanges(20),
      gap(21 bytes padding), modulators(24), tail(128).
    Total = 215 bytes.
    """
    kind: int = InstrumentKind.MIDIOUT
    name: str = ""
    transpose: bool = False
    table_tick: int = 0
    port: int = 0
    channel: int = 0
    bank_select: int = 0
    program_change: int = 0
    control_changes: List[ControlChange] = field(default_factory=_default_ccs)
    modulators: List[Modulator] = field(default_factory=_default_mods)
    _gap: bytes = b""
    _tail: bytes = b""

    @staticmethod
    def from_reader(reader: M8FileReader, inst_start: int, version: M8Version) -> MIDIOut:
        name = reader.read_str(12)
        transpose = reader.read_bool()
        table_tick = reader.read()
        port = reader.read()
        channel = reader.read()
        bank_select = reader.read()
        program_change = reader.read()
        reader.skip(3)  # reserved
        ccs = [ControlChange.from_reader(reader) for _ in range(_NUM_CCS)]
        gap, mods = _read_gap_and_mods(reader, inst_start)
        tail = reader.read_bytes(_TAIL_SIZE)
        return MIDIOut(name=name, transpose=transpose, table_tick=table_tick,
                       port=port, channel=channel, bank_select=bank_select,
                       program_change=program_change, control_changes=ccs,
                       modulators=mods, _gap=gap, _tail=tail)

    def write(self, writer: M8FileWriter) -> None:
        inst_start = writer.position()
        writer.write(self.kind)
        writer.write_str(self.name, 12)
        writer.write_bool(self.transpose)
        writer.write(self.table_tick)
        writer.write(self.port)
        writer.write(self.channel)
        writer.write(self.bank_select)
        writer.write(self.program_change)
        writer.pad(3)  # reserved
        for cc in self.control_changes:
            cc.write(writer)
        _write_gap_and_mods(writer, self._gap, self.modulators, inst_start)
        _write_tail(writer, self._tail, inst_start)
        writer.expect_written(INSTRUMENT_SIZE, inst_start)


# ---------------------------------------------------------------------------
# EmptyInstrument
# ---------------------------------------------------------------------------

@dataclass
class EmptyInstrument:
    """Empty/unused instrument slot (kind 0xFF)."""
    kind: int = InstrumentKind.NONE

    @staticmethod
    def from_reader(reader: M8FileReader, inst_start: int, version: M8Version) -> EmptyInstrument:
        reader.seek(inst_start + INSTRUMENT_SIZE)
        return EmptyInstrument()

    def write(self, writer: M8FileWriter) -> None:
        inst_start = writer.position()
        writer.write(0xFF)
        writer.pad(INSTRUMENT_SIZE - 1)
        writer.expect_written(INSTRUMENT_SIZE, inst_start)


# ---------------------------------------------------------------------------
# Union type
# ---------------------------------------------------------------------------

Instrument = (
    WavSynth | MacroSynth | Sampler | MIDIOut |
    FMSynth | HyperSynth | External | EmptyInstrument
)


# ---------------------------------------------------------------------------
# Top-level read / write dispatchers
# ---------------------------------------------------------------------------

_KIND_MAP = {
    InstrumentKind.WAVSYNTH: WavSynth,
    InstrumentKind.MACROSYNTH: MacroSynth,
    InstrumentKind.SAMPLER: Sampler,
    InstrumentKind.MIDIOUT: MIDIOut,
    InstrumentKind.FMSYNTH: FMSynth,
    InstrumentKind.HYPERSYNTH: HyperSynth,
    InstrumentKind.EXTERNAL: External,
    InstrumentKind.NONE: EmptyInstrument,
}


def read_instrument(reader: M8FileReader, version: M8Version) -> Instrument:
    """Read one instrument (215 bytes) from the current reader position.

    Reads the kind byte, dispatches to the appropriate type's from_reader,
    and guarantees the reader ends at exactly start + 215.
    """
    inst_start = reader.position()
    kind_byte = reader.read()

    try:
        kind = InstrumentKind(kind_byte)
    except ValueError:
        raise M8ParseError(
            f"unknown instrument kind 0x{kind_byte:02X} at offset {inst_start}"
        )

    cls = _KIND_MAP[kind]
    instrument = cls.from_reader(reader, inst_start, version)
    reader.expect_consumed(INSTRUMENT_SIZE, inst_start)
    return instrument


def write_instrument(instrument: Instrument, writer: M8FileWriter) -> None:
    """Write one instrument (215 bytes) to the writer.

    Delegates to the instrument's write() method, which is responsible
    for enforcing the 215-byte size.
    """
    instrument.write(writer)
