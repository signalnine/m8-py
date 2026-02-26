import struct
import hypothesis
from hypothesis import given, settings, assume
import hypothesis.strategies as st

from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import INSTRUMENT_SIZE, EMPTY
from m8py.models.version import M8Version
from m8py.models.fx import FX
from m8py.models.phrase import PhraseStep, Phrase
from m8py.models.chain import ChainStep, Chain
from m8py.models.groove import Groove
from m8py.models.table import TableStep, Table
from m8py.models.theme import RGB, Theme
from m8py.models.scale import NoteInterval, Scale
from m8py.models.eq import EQBand, EQ
from m8py.models.midi import MIDIMapping
from m8py.models.instrument import (
    WavSynth, MacroSynth, Sampler, FMSynth, HyperSynth,
    External, MIDIOut, EmptyInstrument, SynthCommon,
    FMOperator, ControlChange, write_instrument, read_instrument,
)
from m8py.models.modulators import AHDEnv, mod_write, mod_from_reader


# -- Strategies --

u8 = st.integers(min_value=0, max_value=255)


@st.composite
def fx_strategy(draw):
    return FX(command=draw(u8), value=draw(u8))


@st.composite
def phrase_step_strategy(draw):
    return PhraseStep(
        note=draw(u8), velocity=draw(u8), instrument=draw(u8),
        fx1=draw(fx_strategy()), fx2=draw(fx_strategy()), fx3=draw(fx_strategy()),
    )


@st.composite
def phrase_strategy(draw):
    return Phrase(steps=[draw(phrase_step_strategy()) for _ in range(16)])


@st.composite
def chain_step_strategy(draw):
    return ChainStep(phrase=draw(u8), transpose=draw(u8))


@st.composite
def chain_strategy(draw):
    return Chain(steps=[draw(chain_step_strategy()) for _ in range(16)])


@st.composite
def groove_strategy(draw):
    return Groove(steps=[draw(u8) for _ in range(16)])


@st.composite
def table_step_strategy(draw):
    return TableStep(
        transpose=draw(u8), velocity=draw(u8),
        fx1=draw(fx_strategy()), fx2=draw(fx_strategy()), fx3=draw(fx_strategy()),
    )


@st.composite
def table_strategy(draw):
    return Table(steps=[draw(table_step_strategy()) for _ in range(16)])


@st.composite
def rgb_strategy(draw):
    return RGB(r=draw(u8), g=draw(u8), b=draw(u8))


@st.composite
def theme_strategy(draw):
    return Theme(**{f.name: draw(rgb_strategy()) for f in Theme.__dataclass_fields__.values()})


@st.composite
def note_interval_strategy(draw):
    return NoteInterval(semitone=draw(u8), cents=draw(u8))


@st.composite
def scale_strategy(draw):
    # Name: ascii printable, 0-15 chars (write_str truncates to length-1)
    name = draw(st.text(
        st.characters(whitelist_categories=('L', 'N'), min_codepoint=32, max_codepoint=126),
        min_size=0, max_size=15,
    ))
    # Tuning: finite float32 values (avoid NaN/inf which don't roundtrip via ==)
    tuning = draw(st.floats(
        min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False,
        width=32,
    ))
    return Scale(
        name=name,
        note_enable=draw(st.integers(min_value=0, max_value=0xFFFF)),
        note_offsets=[draw(note_interval_strategy()) for _ in range(12)],
        tuning=tuning,
    )


@st.composite
def eq_band_strategy(draw):
    return EQBand(**{f.name: draw(u8) for f in EQBand.__dataclass_fields__.values()})


@st.composite
def eq_strategy(draw):
    return EQ(low=draw(eq_band_strategy()), mid=draw(eq_band_strategy()), high=draw(eq_band_strategy()))


@st.composite
def midi_mapping_strategy(draw):
    return MIDIMapping(
        channel=draw(u8), control_number=draw(u8),
        type=draw(u8), instr_index=draw(u8),
        param_index=draw(u8), min_value=draw(u8), max_value=draw(u8),
    )


# -- Roundtrip tests --

class TestRoundtrip:
    @given(phrase=phrase_strategy())
    @settings(max_examples=50)
    def test_phrase_roundtrip(self, phrase):
        writer = M8FileWriter()
        phrase.write(writer)
        data = writer.to_bytes()
        assert len(data) == 144  # 16 * 9
        reader = M8FileReader(data)
        phrase2 = Phrase.from_reader(reader)
        assert phrase == phrase2

    @given(chain=chain_strategy())
    @settings(max_examples=50)
    def test_chain_roundtrip(self, chain):
        writer = M8FileWriter()
        chain.write(writer)
        data = writer.to_bytes()
        assert len(data) == 32  # 16 * 2
        reader = M8FileReader(data)
        chain2 = Chain.from_reader(reader)
        assert chain == chain2

    @given(groove=groove_strategy())
    @settings(max_examples=50)
    def test_groove_roundtrip(self, groove):
        writer = M8FileWriter()
        groove.write(writer)
        data = writer.to_bytes()
        assert len(data) == 16
        reader = M8FileReader(data)
        groove2 = Groove.from_reader(reader)
        assert groove == groove2

    @given(table=table_strategy())
    @settings(max_examples=50)
    def test_table_roundtrip(self, table):
        writer = M8FileWriter()
        table.write(writer)
        data = writer.to_bytes()
        assert len(data) == 128  # 16 * 8
        reader = M8FileReader(data)
        table2 = Table.from_reader(reader)
        assert table == table2

    @given(theme=theme_strategy())
    @settings(max_examples=50)
    def test_theme_roundtrip(self, theme):
        writer = M8FileWriter()
        theme.write(writer)
        data = writer.to_bytes()
        assert len(data) == 39  # 13 * 3
        reader = M8FileReader(data)
        theme2 = Theme.from_reader(reader)
        assert theme == theme2

    @given(scale=scale_strategy())
    @settings(max_examples=50)
    def test_scale_roundtrip(self, scale):
        writer = M8FileWriter()
        scale.write(writer)
        data = writer.to_bytes()
        assert len(data) == 46  # 2 + 24 + 16 + 4 (float32 tuning)
        reader = M8FileReader(data)
        scale2 = Scale.from_reader(reader)
        assert scale == scale2

    @given(eq=eq_strategy())
    @settings(max_examples=50)
    def test_eq_roundtrip(self, eq):
        writer = M8FileWriter()
        eq.write(writer)
        data = writer.to_bytes()
        assert len(data) == 18  # 3 * 6
        reader = M8FileReader(data)
        eq2 = EQ.from_reader(reader)
        assert eq == eq2

    @given(mapping=midi_mapping_strategy())
    @settings(max_examples=50)
    def test_midi_mapping_roundtrip(self, mapping):
        writer = M8FileWriter()
        mapping.write(writer)
        data = writer.to_bytes()
        assert len(data) == 9  # 7 data + 2 padding
        reader = M8FileReader(data)
        mapping2 = MIDIMapping.from_reader(reader)
        assert mapping == mapping2


class TestInstrumentInvariants:
    """All instrument types must produce exactly 215 bytes."""

    def test_wavsynth_size(self):
        writer = M8FileWriter()
        write_instrument(WavSynth(), writer)
        assert len(writer.to_bytes()) == INSTRUMENT_SIZE

    def test_macrosynth_size(self):
        writer = M8FileWriter()
        write_instrument(MacroSynth(), writer)
        assert len(writer.to_bytes()) == INSTRUMENT_SIZE

    def test_sampler_size(self):
        writer = M8FileWriter()
        write_instrument(Sampler(), writer)
        assert len(writer.to_bytes()) == INSTRUMENT_SIZE

    def test_fmsynth_size(self):
        writer = M8FileWriter()
        write_instrument(FMSynth(), writer)
        assert len(writer.to_bytes()) == INSTRUMENT_SIZE

    def test_hypersynth_size(self):
        writer = M8FileWriter()
        write_instrument(HyperSynth(), writer)
        assert len(writer.to_bytes()) == INSTRUMENT_SIZE

    def test_external_size(self):
        writer = M8FileWriter()
        write_instrument(External(), writer)
        assert len(writer.to_bytes()) == INSTRUMENT_SIZE

    def test_midiout_size(self):
        writer = M8FileWriter()
        write_instrument(MIDIOut(), writer)
        assert len(writer.to_bytes()) == INSTRUMENT_SIZE

    def test_empty_size(self):
        writer = M8FileWriter()
        write_instrument(EmptyInstrument(), writer)
        assert len(writer.to_bytes()) == INSTRUMENT_SIZE

    def test_wavsynth_roundtrip(self):
        inst = WavSynth(common=SynthCommon(name="Test"), shape=5, size=3)
        writer = M8FileWriter()
        write_instrument(inst, writer)
        reader = M8FileReader(writer.to_bytes())
        inst2 = read_instrument(reader, M8Version(4, 1, 0))
        assert isinstance(inst2, WavSynth)
        assert inst2.common.name == "Test"
        assert inst2.shape == 5

    def test_empty_roundtrip(self):
        inst = EmptyInstrument()
        writer = M8FileWriter()
        write_instrument(inst, writer)
        reader = M8FileReader(writer.to_bytes())
        inst2 = read_instrument(reader, M8Version(4, 1, 0))
        assert isinstance(inst2, EmptyInstrument)
