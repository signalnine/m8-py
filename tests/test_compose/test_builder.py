import pytest
from m8py.compose.builder import SongBuilder
from m8py.models.instrument import WavSynth, SynthCommon
from m8py.models.phrase import Phrase, PhraseStep
from m8py.models.chain import Chain, ChainStep
from m8py.models.song import Song
from m8py.format.writer import M8FileWriter
from m8py.format.reader import M8FileReader
from m8py.models.version import M8FileType
from m8py.format.constants import EMPTY


class TestSongBuilder:
    def test_build_minimal_song(self):
        """Build a minimal song with 1 instrument, 1 phrase, 1 chain, 1 song step."""
        synth = WavSynth(common=SynthCommon(name="Lead"))
        song = (SongBuilder(name="Mini", tempo=120)
            .add_instrument(synth)
            .add_phrase("C4 E4 G4 C5")
            .add_chain([0])
            .set_song_step(0, track=0, chain=0)
            .build())

        assert isinstance(song, Song)
        assert song.name == "Mini"
        assert song.tempo == 120.0
        assert isinstance(song.instruments[0], WavSynth)
        assert song.phrases[0].steps[0].note == 60  # C4
        assert song.chains[0].steps[0].phrase == 0
        assert song.song_steps[0].tracks[0] == 0

    def test_minimal_song_is_writable(self):
        """Built song can be serialized to bytes."""
        song = (SongBuilder(name="Test")
            .add_instrument(WavSynth())
            .add_phrase("C4 E4 G4")
            .add_chain([0])
            .set_song_step(0, track=0, chain=0)
            .build())

        writer = M8FileWriter()
        song.write(writer)
        data = writer.to_bytes()
        assert len(data) > 0
        # Verify it starts with M8 header
        assert data[:10] == b"M8VERSION\x00"

    def test_last_slot_properties(self):
        builder = SongBuilder()
        assert builder.last_phrase is None
        assert builder.last_chain is None
        assert builder.last_instrument is None

        builder.add_instrument(WavSynth())
        assert builder.last_instrument == 0

        builder.add_phrase(Phrase())
        assert builder.last_phrase == 0

        builder.add_chain([0])
        assert builder.last_chain == 0

    def test_sequential_slot_assignment(self):
        builder = SongBuilder()
        builder.add_instrument(WavSynth())
        assert builder.last_instrument == 0
        builder.add_instrument(WavSynth())
        assert builder.last_instrument == 1

        builder.add_phrase(Phrase())
        assert builder.last_phrase == 0
        builder.add_phrase(Phrase())
        assert builder.last_phrase == 1

    def test_method_chaining(self):
        """All builder methods return self for chaining."""
        builder = SongBuilder()
        result = builder.add_instrument(WavSynth())
        assert result is builder
        result = builder.add_phrase(Phrase())
        assert result is builder
        result = builder.add_chain([0])
        assert result is builder
        result = builder.set_song_step(0, 0, 0)
        assert result is builder
        result = builder.set_tempo(140)
        assert result is builder
        result = builder.set_name("Test")
        assert result is builder

    def test_pattern_string_input(self):
        """add_phrase accepts pattern strings."""
        song = SongBuilder().add_phrase("C4 E4 G4 . OFF").build()
        p = song.phrases[0]
        assert p.steps[0].note == 60   # C4
        assert p.steps[1].note == 64   # E4
        assert p.steps[2].note == 67   # G4
        assert p.steps[3].note == EMPTY  # empty step
        assert p.steps[4].note == 0x80   # note off

    def test_chain_with_multiple_phrases(self):
        builder = SongBuilder()
        builder.add_phrase("C4 E4")
        builder.add_phrase("G4 B4")
        builder.add_chain([0, 1])
        song = builder.build()
        assert song.chains[0].steps[0].phrase == 0
        assert song.chains[0].steps[1].phrase == 1
        assert song.chains[0].steps[2].phrase == EMPTY  # padded

    def test_build_with_roundtrip(self):
        """Built song survives write/read roundtrip."""
        song = (SongBuilder(name="Round", tempo=135)
            .add_instrument(WavSynth(common=SynthCommon(name="Pad")))
            .add_phrase("C4 E4 G4 C5")
            .add_chain([0])
            .set_song_step(0, track=0, chain=0)
            .build())

        writer = M8FileWriter()
        song.write(writer)
        data = writer.to_bytes()

        reader = M8FileReader(data)
        version, ft = M8FileType.from_reader(reader)
        song2 = Song.from_reader(reader, version)

        assert song2.name == "Round"
        assert abs(song2.tempo - 135.0) < 0.01
        assert song2.instruments[0].common.name == "Pad"
        assert song2.phrases[0].steps[0].note == 60

    def test_set_transpose(self):
        song = SongBuilder().set_transpose(5).build()
        assert song.transpose == 5

    def test_default_values(self):
        song = SongBuilder().build()
        assert song.name == ""
        assert song.tempo == 120.0
