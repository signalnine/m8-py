import pytest
from m8py.compose.declarative import compose, TrackDef
from m8py.models.instrument import WavSynth, MacroSynth, SynthCommon
from m8py.models.phrase import PhraseStep
from m8py.models.song import Song
from m8py.format.constants import EMPTY, STEPS_PER_PHRASE


class TestDeclarativeCompose:
    def test_single_track_short_pattern(self):
        """Single track with <=16 steps: 1 phrase, 1 chain."""
        song = compose(
            tracks=[TrackDef(
                instrument=WavSynth(common=SynthCommon(name="Lead")),
                pattern="C4 E4 G4 C5",
                track=0,
            )],
            name="Short",
            tempo=120,
        )
        assert isinstance(song, Song)
        assert song.name == "Short"
        # Should have 1 instrument in slot 0
        assert isinstance(song.instruments[0], WavSynth)
        # Should have 1 phrase
        assert song.phrases[0].steps[0].note == 60  # C4
        assert song.phrases[0].steps[1].note == 64  # E4
        assert song.phrases[0].steps[2].note == 67  # G4
        assert song.phrases[0].steps[3].note == 72  # C5
        # Phrase should have instrument stamped
        assert song.phrases[0].steps[0].instrument == 0
        # Chain should reference phrase 0
        assert song.chains[0].steps[0].phrase == 0
        assert song.chains[0].steps[1].phrase == EMPTY  # rest is empty
        # Song grid should have chain 0 on track 0
        assert song.song_steps[0].tracks[0] == 0

    def test_single_track_long_pattern(self):
        """Pattern with >16 steps is auto-split into multiple phrases."""
        # Create a 20-step pattern (will split into 16 + 4)
        notes = " ".join(["C4"] * 20)
        song = compose(
            tracks=[TrackDef(
                instrument=WavSynth(),
                pattern=notes,
                track=0,
            )],
        )
        # Should have 2 phrases
        assert song.phrases[0].steps[0].note == 60  # all C4
        assert song.phrases[1].steps[0].note == 60
        # Second phrase steps 4-15 should be empty (padded)
        assert song.phrases[1].steps[4].note == EMPTY
        # Chain should reference both phrases
        assert song.chains[0].steps[0].phrase == 0
        assert song.chains[0].steps[1].phrase == 1

    def test_multiple_tracks(self):
        """Multiple tracks are placed on different track columns."""
        song = compose(
            tracks=[
                TrackDef(instrument=WavSynth(common=SynthCommon(name="Lead")),
                         pattern="C4 E4 G4", track=0),
                TrackDef(instrument=MacroSynth(common=SynthCommon(name="Bass")),
                         pattern="C2 C2 C2", track=1),
            ],
            name="Multi",
        )
        # Two instruments
        assert isinstance(song.instruments[0], WavSynth)
        assert isinstance(song.instruments[1], MacroSynth)
        # Track 0 and track 1 both have chains
        assert song.song_steps[0].tracks[0] != EMPTY
        assert song.song_steps[0].tracks[1] != EMPTY
        # Remaining tracks are empty
        assert song.song_steps[0].tracks[2] == EMPTY

    def test_deduplication(self):
        """With dedup, identical patterns share phrase slots."""
        song = compose(
            tracks=[
                TrackDef(instrument=WavSynth(), pattern="C4 E4 G4", track=0),
                TrackDef(instrument=WavSynth(), pattern="C4 E4 G4", track=1),
            ],
            deduplicate=True,
        )
        # Both song grid entries should point to a valid chain
        track0_chain = song.song_steps[0].tracks[0]
        track1_chain = song.song_steps[0].tracks[1]
        assert track0_chain != EMPTY
        assert track1_chain != EMPTY
        # With identical content and dedup, both tracks share the same chain
        assert track0_chain == track1_chain
        # That shared chain should reference a valid phrase
        assert song.chains[track0_chain].steps[0].phrase != EMPTY

    def test_instrument_auto_stamped(self):
        """Instrument slot is auto-stamped on notes that lack one."""
        song = compose(
            tracks=[TrackDef(
                instrument=WavSynth(),
                pattern="C4 . E4 OFF",
                track=0,
            )],
        )
        p = song.phrases[0]
        # C4 and E4 should have instrument 0 stamped
        assert p.steps[0].instrument == 0
        assert p.steps[2].instrument == 0
        # Empty step and OFF keep EMPTY instrument
        assert p.steps[1].instrument == EMPTY

    def test_pattern_as_step_list(self):
        """Pattern can be a list of PhraseStep objects."""
        steps = [PhraseStep(note=60, velocity=0x7F), PhraseStep(note=64)]
        song = compose(
            tracks=[TrackDef(
                instrument=WavSynth(),
                pattern=steps,
                track=0,
            )],
        )
        assert song.phrases[0].steps[0].note == 60
        assert song.phrases[0].steps[0].velocity == 0x7F
        assert song.phrases[0].steps[1].note == 64

    def test_empty_pattern(self):
        """Empty pattern still creates one phrase (all empty steps)."""
        song = compose(
            tracks=[TrackDef(
                instrument=WavSynth(),
                pattern="",
                track=0,
            )],
        )
        # Should have at least one phrase
        assert song.chains[0].steps[0].phrase != EMPTY

    def test_compose_returns_song(self):
        song = compose(tracks=[], name="Empty")
        assert isinstance(song, Song)
        assert song.name == "Empty"
