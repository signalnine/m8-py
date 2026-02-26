"""End-to-end integration test: create a multi-track song, save, load, verify."""
import pytest
from pathlib import Path

import m8py
from m8py import (
    Song, SongBuilder, compose, TrackDef,
    WavSynth, MacroSynth, Sampler, FMSynth, SynthCommon,
    save, load_song, validate, export_to_sdcard,
    M8Version, Theme, Scale, load, load_theme, load_scale,
)
from m8py.models.phrase import PhraseStep
from m8py.format.constants import EMPTY


class TestIntegration:
    def test_declarative_multi_track_roundtrip(self, tmp_path):
        """Create a multi-track song declaratively, save, load, verify."""
        song = compose(
            tracks=[
                TrackDef(
                    instrument=WavSynth(common=SynthCommon(name="Lead")),
                    pattern="C4 E4 G4 C5 B4 G4 E4 C4",
                    track=0,
                ),
                TrackDef(
                    instrument=MacroSynth(common=SynthCommon(name="Bass")),
                    pattern="C2 . . . C2 . . . E2 . . . E2 . . .",
                    track=1,
                ),
                TrackDef(
                    instrument=FMSynth(common=SynthCommon(name="Pad")),
                    pattern="C4 . . . . . . . G3 . . . . . . .",
                    track=2,
                ),
            ],
            name="IntTest",
            tempo=128.0,
        )

        # Validate
        issues = validate(song)
        errors = [i for i in issues if i.severity.value == "error"]
        assert len(errors) == 0, f"Validation errors: {errors}"

        # Save and load
        path = tmp_path / "integration.m8s"
        save(song, path)
        loaded = load_song(path)

        # Verify structural equality
        assert loaded.name == "IntTest"
        assert abs(loaded.tempo - 128.0) < 0.01
        assert isinstance(loaded.instruments[0], WavSynth)
        assert loaded.instruments[0].common.name == "Lead"
        assert isinstance(loaded.instruments[1], MacroSynth)
        assert loaded.instruments[1].common.name == "Bass"
        assert isinstance(loaded.instruments[2], FMSynth)
        assert loaded.instruments[2].common.name == "Pad"

        # Verify song grid has chains on tracks 0, 1, 2
        assert loaded.song_steps[0].tracks[0] != EMPTY
        assert loaded.song_steps[0].tracks[1] != EMPTY
        assert loaded.song_steps[0].tracks[2] != EMPTY
        assert loaded.song_steps[0].tracks[3] == EMPTY

        # Verify notes survived roundtrip
        lead_phrase_idx = loaded.chains[0].steps[0].phrase
        assert loaded.phrases[lead_phrase_idx].steps[0].note == 60  # C4

    def test_builder_api_roundtrip(self, tmp_path):
        """Build a song imperatively, save, load, verify."""
        song = (SongBuilder(name="Builder", tempo=140)
            .add_instrument(WavSynth(common=SynthCommon(name="Synth")))
            .add_phrase("C4 E4 G4 C5 . . . . C4 E4 G4 C5 . . . .")
            .add_chain([0])
            .set_song_step(0, track=0, chain=0)
            .build())

        path = tmp_path / "builder.m8s"
        save(song, path)
        loaded = load_song(path)

        assert loaded.name == "Builder"
        assert abs(loaded.tempo - 140.0) < 0.01
        assert isinstance(loaded.instruments[0], WavSynth)

    def test_theme_roundtrip(self, tmp_path):
        """Theme save/load roundtrip through top-level API."""
        from m8py.models.theme import RGB
        theme = Theme(
            background=RGB(10, 20, 30),
            cursor=RGB(200, 100, 50),
        )
        path = tmp_path / "test.m8t"
        save(theme, path)
        loaded = load_theme(path)
        assert loaded.background.r == 10
        assert loaded.cursor.g == 100

    def test_scale_roundtrip(self, tmp_path):
        """Scale save/load roundtrip through top-level API."""
        scale = Scale(name="Custom", note_enable=0x0FFF)
        path = tmp_path / "test.m8n"
        save(scale, path)
        loaded = load_scale(path)
        assert loaded.name == "Custom"
        assert loaded.note_enable == 0x0FFF

    def test_sample_export_integration(self, tmp_path):
        """Export a song with samples to SD card structure."""
        source = tmp_path / "source_kick.wav"
        source.write_bytes(b"RIFF" + b"\x00" * 100)

        song = compose(
            tracks=[
                TrackDef(
                    instrument=Sampler(
                        common=SynthCommon(name="Kick"),
                        sample_path="/Samples/kick.wav",
                    ),
                    pattern="C4 . . . C4 . . .",
                    track=0,
                ),
            ],
            name="SampTest",
        )

        sdcard = tmp_path / "sdcard"
        result = export_to_sdcard(
            song, sdcard,
            sample_sources={"/Samples/kick.wav": str(source)}
        )

        assert result.song_path.exists()
        assert len(result.sample_files) == 1
        assert result.sample_files[0].exists()

    def test_top_level_imports(self):
        """Verify key symbols are importable from m8py."""
        assert hasattr(m8py, 'load')
        assert hasattr(m8py, 'save')
        assert hasattr(m8py, 'Song')
        assert hasattr(m8py, 'WavSynth')
        assert hasattr(m8py, 'SongBuilder')
        assert hasattr(m8py, 'compose')
        assert hasattr(m8py, 'TrackDef')
        assert hasattr(m8py, 'validate')

    def test_subpackage_imports(self):
        """Verify subpackage exports work."""
        from m8py.format import M8FileReader, M8FileWriter, EMPTY, M8Error
        from m8py.models import Song, Phrase, Chain, WavSynth, M8Version
        from m8py.compose import SongBuilder, compose, SlotAllocator, normalize_note
        assert M8FileReader is not None
        assert Song is not None
        assert SongBuilder is not None
