"""Tests for all instrument types: roundtrip, size enforcement, and error handling."""
import pytest

from m8py.format.constants import INSTRUMENT_SIZE, InstrumentKind
from m8py.format.errors import M8ParseError
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.instrument import (
    ControlChange,
    EmptyInstrument,
    External,
    FMOperator,
    FMSynth,
    HyperSynth,
    MacroSynth,
    MIDIOut,
    Sampler,
    SynthCommon,
    WavSynth,
    read_instrument,
    write_instrument,
)
from m8py.models.modulators import AHDEnv, LFOMod
from m8py.models.version import M8Version

# A version with no EQ features -- simplest case
_V3 = M8Version(3, 0, 0)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _roundtrip(instrument):
    """Write an instrument, then read it back and return the deserialized copy."""
    w = M8FileWriter()
    write_instrument(instrument, w)
    data = w.to_bytes()
    assert len(data) == INSTRUMENT_SIZE, (
        f"{type(instrument).__name__}: expected {INSTRUMENT_SIZE} bytes, got {len(data)}"
    )
    r = M8FileReader(data)
    return read_instrument(r, _V3)


# ---------------------------------------------------------------------------
# Size enforcement: every instrument type must serialize to exactly 215 bytes
# ---------------------------------------------------------------------------

class TestSizeEnforcement:
    def test_wavsynth_size(self):
        w = M8FileWriter()
        WavSynth().write(w)
        assert len(w.to_bytes()) == INSTRUMENT_SIZE

    def test_macrosynth_size(self):
        w = M8FileWriter()
        MacroSynth().write(w)
        assert len(w.to_bytes()) == INSTRUMENT_SIZE

    def test_sampler_size(self):
        w = M8FileWriter()
        Sampler().write(w)
        assert len(w.to_bytes()) == INSTRUMENT_SIZE

    def test_fmsynth_size(self):
        w = M8FileWriter()
        FMSynth().write(w)
        assert len(w.to_bytes()) == INSTRUMENT_SIZE

    def test_hypersynth_size(self):
        w = M8FileWriter()
        HyperSynth().write(w)
        assert len(w.to_bytes()) == INSTRUMENT_SIZE

    def test_external_size(self):
        w = M8FileWriter()
        External().write(w)
        assert len(w.to_bytes()) == INSTRUMENT_SIZE

    def test_midiout_size(self):
        w = M8FileWriter()
        MIDIOut().write(w)
        assert len(w.to_bytes()) == INSTRUMENT_SIZE

    def test_empty_size(self):
        w = M8FileWriter()
        EmptyInstrument().write(w)
        assert len(w.to_bytes()) == INSTRUMENT_SIZE


# ---------------------------------------------------------------------------
# Roundtrip tests: write -> read -> verify
# ---------------------------------------------------------------------------

class TestWavSynthRoundtrip:
    def test_defaults(self):
        inst = _roundtrip(WavSynth())
        assert isinstance(inst, WavSynth)
        assert inst.kind == InstrumentKind.WAVSYNTH

    def test_fields(self):
        orig = WavSynth(
            common=SynthCommon(
                name="WAVY", transp_eq=0x03, table_tick=4,
                volume=200, pitch=64, fine_tune=0x80,
                filter_type=2, filter_cutoff=100, filter_res=50,
                amp=80, limit=1, mixer_pan=0x80, mixer_dry=0xC0,
                mixer_chorus=10, mixer_delay=20, mixer_reverb=30,
            ),
            shape=5, size=128, mult=3, warp=64, scan=200,
            modulators=[
                AHDEnv(dest=1, amount=100, attack=20, hold=30, decay=40),
                LFOMod(dest=2, amount=60, shape=1, trigger_mode=0, freq=80, retrigger=1),
                AHDEnv(), AHDEnv(),
            ],
        )
        got = _roundtrip(orig)
        assert got.common.name == "WAVY"
        assert got.common.volume == 200
        assert got.common.filter_type == 2
        assert got.common.mixer_reverb == 30
        assert got.shape == 5
        assert got.size == 128
        assert got.mult == 3
        assert got.warp == 64
        assert got.scan == 200
        assert isinstance(got.modulators[0], AHDEnv)
        assert got.modulators[0].amount == 100
        assert isinstance(got.modulators[1], LFOMod)
        assert got.modulators[1].freq == 80


class TestMacroSynthRoundtrip:
    def test_defaults(self):
        inst = _roundtrip(MacroSynth())
        assert isinstance(inst, MacroSynth)
        assert inst.kind == InstrumentKind.MACROSYNTH

    def test_fields(self):
        orig = MacroSynth(
            common=SynthCommon(name="MACRO1"),
            shape=10, timbre=128, color=64, degrade=32, redux=16,
        )
        got = _roundtrip(orig)
        assert got.common.name == "MACRO1"
        assert got.shape == 10
        assert got.timbre == 128
        assert got.color == 64
        assert got.degrade == 32
        assert got.redux == 16


class TestSamplerRoundtrip:
    def test_defaults(self):
        inst = _roundtrip(Sampler())
        assert isinstance(inst, Sampler)
        assert inst.kind == InstrumentKind.SAMPLER

    def test_fields(self):
        orig = Sampler(
            common=SynthCommon(name="SMPLR"),
            play_mode=2, slice=4, start=10, loop_start=20,
            length=200, degrade=5, sample_path="/Samples/kick.wav",
        )
        got = _roundtrip(orig)
        assert got.common.name == "SMPLR"
        assert got.play_mode == 2
        assert got.slice == 4
        assert got.start == 10
        assert got.loop_start == 20
        assert got.length == 200
        assert got.degrade == 5
        assert got.sample_path == "/Samples/kick.wav"

    def test_long_sample_path_truncated(self):
        long_path = "A" * 200
        orig = Sampler(sample_path=long_path)
        got = _roundtrip(orig)
        # write_str truncates to length = 128 chars
        assert len(got.sample_path) <= 128


class TestFMSynthRoundtrip:
    def test_defaults(self):
        inst = _roundtrip(FMSynth())
        assert isinstance(inst, FMSynth)
        assert inst.kind == InstrumentKind.FMSYNTH

    def test_fields(self):
        ops = [
            FMOperator(shape=1, ratio=2, ratio_fine=10, level=200,
                       feedback=5, mod_a=3, mod_b=7),
            FMOperator(shape=2, ratio=3, ratio_fine=20, level=180,
                       feedback=10, mod_a=1, mod_b=4),
            FMOperator(), FMOperator(),
        ]
        orig = FMSynth(
            common=SynthCommon(name="FM_BASS"),
            algo=7, operators=ops, mod1=11, mod2=22, mod3=33, mod4=44,
        )
        got = _roundtrip(orig)
        assert got.common.name == "FM_BASS"
        assert got.algo == 7
        assert got.operators[0].shape == 1
        assert got.operators[0].ratio == 2
        assert got.operators[0].level == 200
        assert got.operators[1].feedback == 10
        assert got.mod1 == 11
        assert got.mod2 == 22
        assert got.mod3 == 33
        assert got.mod4 == 44


class TestHyperSynthRoundtrip:
    def test_defaults(self):
        inst = _roundtrip(HyperSynth())
        assert isinstance(inst, HyperSynth)
        assert inst.kind == InstrumentKind.HYPERSYNTH

    def test_fields(self):
        chord = bytes([3, 5, 7, 10, 12, 0, 0])
        custom = bytes(range(112))
        orig = HyperSynth(
            common=SynthCommon(name="HYPER"),
            default_chord=chord, scale=5, shift=2,
            swarm=128, width=64, subosc=32,
            custom_chords=custom,
        )
        got = _roundtrip(orig)
        assert got.common.name == "HYPER"
        assert got.default_chord == chord
        assert got.scale == 5
        assert got.shift == 2
        assert got.swarm == 128
        assert got.width == 64
        assert got.subosc == 32
        assert got.custom_chords == custom


class TestExternalRoundtrip:
    def test_defaults(self):
        inst = _roundtrip(External())
        assert isinstance(inst, External)
        assert inst.kind == InstrumentKind.EXTERNAL

    def test_fields(self):
        orig = External(
            common=SynthCommon(name="EXT_SYNTH"),
            input=1, port=2, channel=3, bank=4, program=5,
            cca=bytes([10, 20]), ccb=bytes([30, 40]),
            ccc=bytes([50, 60]), ccd=bytes([70, 80]),
        )
        got = _roundtrip(orig)
        assert got.common.name == "EXT_SYNTH"  # 9 chars fits in 12-byte field
        assert got.input == 1
        assert got.port == 2
        assert got.channel == 3
        assert got.bank == 4
        assert got.program == 5
        assert got.cca == bytes([10, 20])
        assert got.ccb == bytes([30, 40])
        assert got.ccc == bytes([50, 60])
        assert got.ccd == bytes([70, 80])


class TestMIDIOutRoundtrip:
    def test_defaults(self):
        inst = _roundtrip(MIDIOut())
        assert isinstance(inst, MIDIOut)
        assert inst.kind == InstrumentKind.MIDIOUT

    def test_fields(self):
        ccs = [ControlChange(number=i, value=i * 10) for i in range(10)]
        orig = MIDIOut(
            name="MIDI_LEAD", transpose=True, table_tick=8,
            port=1, channel=5, bank_select=3, program_change=42,
            control_changes=ccs,
        )
        got = _roundtrip(orig)
        assert got.name == "MIDI_LEAD"
        assert got.transpose is True
        assert got.table_tick == 8
        assert got.port == 1
        assert got.channel == 5
        assert got.bank_select == 3
        assert got.program_change == 42
        for i in range(10):
            assert got.control_changes[i].number == i
            assert got.control_changes[i].value == i * 10


class TestEmptyInstrument:
    def test_roundtrip(self):
        inst = _roundtrip(EmptyInstrument())
        assert isinstance(inst, EmptyInstrument)
        assert inst.kind == InstrumentKind.NONE

    def test_bytes_content(self):
        w = M8FileWriter()
        EmptyInstrument().write(w)
        data = w.to_bytes()
        assert data[0] == 0xFF
        assert all(b == 0x00 for b in data[1:])


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_unknown_kind_raises(self):
        data = bytes([0xFE]) + bytes(INSTRUMENT_SIZE - 1)
        with pytest.raises(M8ParseError, match="unknown instrument kind 0xFE"):
            read_instrument(M8FileReader(data), _V3)

    def test_another_unknown_kind(self):
        data = bytes([0x07]) + bytes(INSTRUMENT_SIZE - 1)
        with pytest.raises(M8ParseError, match="unknown instrument kind 0x07"):
            read_instrument(M8FileReader(data), _V3)


# ---------------------------------------------------------------------------
# Dispatcher: read_instrument identifies correct types
# ---------------------------------------------------------------------------

class TestReadInstrumentDispatch:
    def _write_kind(self, kind_byte: int) -> bytes:
        """Create a minimal 215-byte buffer with the given kind byte."""
        w = M8FileWriter()
        w.write(kind_byte)
        w.pad(INSTRUMENT_SIZE - 1)
        return w.to_bytes()

    def test_wavsynth(self):
        data = self._write_kind(InstrumentKind.WAVSYNTH)
        inst = read_instrument(M8FileReader(data), _V3)
        assert isinstance(inst, WavSynth)

    def test_macrosynth(self):
        data = self._write_kind(InstrumentKind.MACROSYNTH)
        inst = read_instrument(M8FileReader(data), _V3)
        assert isinstance(inst, MacroSynth)

    def test_sampler(self):
        data = self._write_kind(InstrumentKind.SAMPLER)
        inst = read_instrument(M8FileReader(data), _V3)
        assert isinstance(inst, Sampler)

    def test_midiout(self):
        data = self._write_kind(InstrumentKind.MIDIOUT)
        inst = read_instrument(M8FileReader(data), _V3)
        assert isinstance(inst, MIDIOut)

    def test_fmsynth(self):
        data = self._write_kind(InstrumentKind.FMSYNTH)
        inst = read_instrument(M8FileReader(data), _V3)
        assert isinstance(inst, FMSynth)

    def test_hypersynth(self):
        data = self._write_kind(InstrumentKind.HYPERSYNTH)
        inst = read_instrument(M8FileReader(data), _V3)
        assert isinstance(inst, HyperSynth)

    def test_external(self):
        data = self._write_kind(InstrumentKind.EXTERNAL)
        inst = read_instrument(M8FileReader(data), _V3)
        assert isinstance(inst, External)

    def test_empty(self):
        data = self._write_kind(InstrumentKind.NONE)
        inst = read_instrument(M8FileReader(data), _V3)
        assert isinstance(inst, EmptyInstrument)


# ---------------------------------------------------------------------------
# Multiple instruments back-to-back (simulates reading from a song file)
# ---------------------------------------------------------------------------

class TestMultipleInstruments:
    def test_three_instruments_back_to_back(self):
        """Write three different instruments, read them back sequentially."""
        w = M8FileWriter()
        write_instrument(WavSynth(common=SynthCommon(name="W1"), shape=42), w)
        write_instrument(FMSynth(common=SynthCommon(name="FM1"), algo=3), w)
        write_instrument(EmptyInstrument(), w)
        data = w.to_bytes()
        assert len(data) == INSTRUMENT_SIZE * 3

        r = M8FileReader(data)
        i1 = read_instrument(r, _V3)
        i2 = read_instrument(r, _V3)
        i3 = read_instrument(r, _V3)

        assert isinstance(i1, WavSynth)
        assert i1.common.name == "W1"
        assert i1.shape == 42

        assert isinstance(i2, FMSynth)
        assert i2.common.name == "FM1"
        assert i2.algo == 3

        assert isinstance(i3, EmptyInstrument)


# ---------------------------------------------------------------------------
# Modulator preservation
# ---------------------------------------------------------------------------

class TestModulatorPreservation:
    def test_modulators_survive_roundtrip(self):
        mods = [
            LFOMod(dest=1, amount=80, shape=2, trigger_mode=1, freq=60, retrigger=3),
            AHDEnv(dest=2, amount=100, attack=10, hold=20, decay=30),
            AHDEnv(),
            AHDEnv(),
        ]
        orig = MacroSynth(
            common=SynthCommon(name="MODS"),
            shape=1, timbre=2, color=3, degrade=4, redux=5,
            modulators=mods,
        )
        got = _roundtrip(orig)
        m0 = got.modulators[0]
        assert isinstance(m0, LFOMod)
        assert m0.dest == 1
        assert m0.amount == 80
        assert m0.freq == 60
        m1 = got.modulators[1]
        assert isinstance(m1, AHDEnv)
        assert m1.amount == 100
