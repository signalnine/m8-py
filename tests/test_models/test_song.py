import struct
import pytest
from m8py.format.errors import M8ParseError
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import (
    EMPTY, HEADER_SIZE, N_SONG_STEPS, N_PHRASES, N_CHAINS,
    N_INSTRUMENTS, N_TABLES, N_GROOVES, N_SCALES, N_MIDI_MAPPINGS,
    INSTRUMENT_SIZE,
)
from m8py.models.song import Song
from m8py.models.version import M8Version, M8FileType
from m8py.models.groove import Groove
from m8py.models.phrase import Phrase
from m8py.models.chain import Chain
from m8py.models.table import Table
from m8py.models.song_step import SongStep
from m8py.models.instrument import EmptyInstrument, WavSynth, SynthCommon
from m8py.models.settings import MIDISettings, MixerSettings, EffectsSettings
from m8py.models.midi import MIDIMapping
from m8py.models.scale import Scale
from m8py.models.eq import EQ


class TestSong:
    def test_default_song_field_counts(self):
        song = Song()
        assert len(song.grooves) == N_GROOVES
        assert len(song.song_steps) == N_SONG_STEPS
        assert len(song.phrases) == N_PHRASES
        assert len(song.chains) == N_CHAINS
        assert len(song.tables) == N_TABLES
        assert len(song.instruments) == N_INSTRUMENTS
        assert len(song.midi_mappings) == N_MIDI_MAPPINGS
        assert len(song.scales) == N_SCALES

    def test_default_song_values(self):
        song = Song()
        assert song.tempo == 120.0
        assert song.transpose == 0
        assert song.quantize == 0
        assert song.name == ""
        assert song.key == 0
        assert song.version.major == 6
        assert song.version.minor == 5

    def test_write_read_roundtrip_default(self):
        """Default v6.5 song writes to bytes and reads back identically."""
        song = Song()
        writer = M8FileWriter()
        song.write(writer)
        data = writer.to_bytes()

        # Read back -- skip 14-byte header
        reader = M8FileReader(data)
        version = M8FileType.from_reader(reader)
        assert version.major == 6
        assert version.minor == 5

        song2 = Song.from_reader(reader, version)
        assert song2.transpose == song.transpose
        assert song2.quantize == song.quantize
        assert song2.name == song.name
        assert song2.key == song.key
        assert len(song2.grooves) == N_GROOVES
        assert len(song2.phrases) == N_PHRASES
        assert len(song2.instruments) == N_INSTRUMENTS
        # Check tempo with float tolerance
        assert abs(song2.tempo - song.tempo) < 0.01

    def test_write_read_roundtrip_with_data(self):
        """Song with non-default values roundtrips correctly."""
        song = Song()
        song.name = "TestSong"
        song.tempo = 140.0
        song.transpose = 3
        song.quantize = 2
        song.key = 5
        # Set first groove to something non-default
        song.grooves[0] = Groove(steps=[6] + [EMPTY] * 15)

        writer = M8FileWriter()
        song.write(writer)
        data = writer.to_bytes()

        reader = M8FileReader(data)
        version = M8FileType.from_reader(reader)
        song2 = Song.from_reader(reader, version)

        assert song2.name == "TestSong"
        assert abs(song2.tempo - 140.0) < 0.01
        assert song2.transpose == 3
        assert song2.quantize == 2
        assert song2.key == 5
        assert song2.grooves[0].steps[0] == 6

    def test_write_read_with_instrument(self):
        """Song with a WavSynth instrument roundtrips."""
        song = Song()
        ws = WavSynth(common=SynthCommon(name="Lead"))
        ws.shape = 3
        song.instruments[0] = ws

        writer = M8FileWriter()
        song.write(writer)
        data = writer.to_bytes()

        reader = M8FileReader(data)
        version = M8FileType.from_reader(reader)
        song2 = Song.from_reader(reader, version)

        inst = song2.instruments[0]
        assert isinstance(inst, WavSynth)
        assert inst.common.name == "Lead"
        assert inst.shape == 3
        # Remaining instruments should be empty
        assert isinstance(song2.instruments[1], EmptyInstrument)

    def test_default_instruments_are_empty(self):
        song = Song()
        for inst in song.instruments:
            assert isinstance(inst, EmptyInstrument)

    def test_scales_present_v41(self):
        """v4.1 songs include scales."""
        song = Song()
        song.scales[0] = Scale(name="MyScale", note_enable=0x0FFF)

        writer = M8FileWriter()
        song.write(writer)
        data = writer.to_bytes()

        reader = M8FileReader(data)
        version = M8FileType.from_reader(reader)
        song2 = Song.from_reader(reader, version)

        assert song2.scales[0].name == "MyScale"
        assert song2.scales[0].note_enable == 0x0FFF

    def test_eqs_present_v41(self):
        """v4.1 songs include EQs (132: 128 instruments + 3 effects + 1 global)."""
        song = Song()
        song.eqs = [EQ() for _ in range(132)]

        writer = M8FileWriter()
        song.write(writer)
        data = writer.to_bytes()

        reader = M8FileReader(data)
        version = M8FileType.from_reader(reader)
        song2 = Song.from_reader(reader, version)

        assert len(song2.eqs) == 132

    def test_file_size_reasonable(self):
        """Default v4.1 song produces a reasonably-sized output."""
        song = Song()
        song.eqs = [EQ() for _ in range(132)]
        writer = M8FileWriter()
        song.write(writer)
        data = writer.to_bytes()
        # Should be at least the eq offset + eq data
        # V4.1 eq offset is 0x1AD5E, plus 132 * 18 = 2376
        assert len(data) > 0x1AD5E

    def test_header_is_song_type(self):
        """Written song has correct M8 header."""
        song = Song()
        writer = M8FileWriter()
        song.write(writer)
        data = writer.to_bytes()
        assert data[:10] == b"M8VERSION\x00"


class TestPadTo:
    def test_overrun_raises_m8_parse_error(self):
        from m8py.models.song import _pad_to
        writer = M8FileWriter()
        writer.pad(100)
        with pytest.raises(M8ParseError):
            _pad_to(writer, 50)

    def test_overrun_message_includes_position_target_and_overrun(self):
        from m8py.models.song import _pad_to
        writer = M8FileWriter()
        writer.pad(100)
        with pytest.raises(M8ParseError) as exc_info:
            _pad_to(writer, 50)
        msg = str(exc_info.value)
        # Position 100 = 0x64, target 50 = 0x32, overrun = 50
        assert "0x64" in msg or "100" in msg
        assert "0x32" in msg or "50" in msg
        assert "50" in msg  # overrun amount

    def test_at_target_is_noop(self):
        from m8py.models.song import _pad_to
        writer = M8FileWriter()
        writer.pad(100)
        _pad_to(writer, 100)
        assert writer.position() == 100

    def test_below_target_pads_with_zeros(self):
        from m8py.models.song import _pad_to
        writer = M8FileWriter()
        writer.pad(50)
        _pad_to(writer, 100)
        assert writer.position() == 100
        # Last 50 bytes should be zeros
        assert writer.to_bytes()[50:100] == bytes(50)
