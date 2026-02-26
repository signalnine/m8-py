import pytest
from pathlib import Path

from m8py.compose.samples import export_to_sdcard, ExportResult
from m8py.format.errors import M8ValidationError
from m8py.models.song import Song
from m8py.models.instrument import Sampler, SynthCommon, WavSynth, EmptyInstrument


class TestSampleExport:
    def test_export_no_samplers(self, tmp_path):
        """Song with no samplers exports just the .m8s file."""
        song = Song(name="NoSamples")
        song.instruments[0] = WavSynth(common=SynthCommon(name="Synth"))

        result = export_to_sdcard(song, tmp_path)
        assert result.song_path.exists()
        assert result.song_path.name == "NoSamples.m8s"
        assert len(result.sample_files) == 0

    def test_export_with_samples(self, tmp_path):
        """Song with Sampler instruments copies sample files."""
        # Create a fake source sample
        source_dir = tmp_path / "sources"
        source_dir.mkdir()
        sample_file = source_dir / "kick.wav"
        sample_file.write_bytes(b"RIFF" + b"\x00" * 100)

        song = Song(name="WithSamples")
        song.instruments[0] = Sampler(
            common=SynthCommon(name="Kick"),
            sample_path="/Samples/Drums/kick.wav"
        )

        sdcard = tmp_path / "sdcard"
        result = export_to_sdcard(
            song, sdcard,
            sample_sources={"/Samples/Drums/kick.wav": str(sample_file)}
        )

        assert result.song_path.exists()
        assert len(result.sample_files) == 1
        assert result.sample_files[0].exists()
        assert result.sample_files[0].name == "kick.wav"

    def test_missing_sample_raises(self, tmp_path):
        """Missing sample source raises M8ValidationError."""
        song = Song(name="Missing")
        song.instruments[0] = Sampler(
            common=SynthCommon(name="Samp"),
            sample_path="/Samples/missing.wav"
        )

        with pytest.raises(M8ValidationError, match="missing.wav"):
            export_to_sdcard(song, tmp_path)

    def test_dry_run_no_files_written(self, tmp_path):
        """Dry run returns manifest without creating files."""
        sample_file = tmp_path / "source.wav"
        sample_file.write_bytes(b"RIFF" + b"\x00" * 50)

        song = Song(name="DryRun")
        song.instruments[0] = Sampler(
            common=SynthCommon(name="Hit"),
            sample_path="/Samples/hit.wav"
        )

        sdcard = tmp_path / "sdcard"
        result = export_to_sdcard(
            song, sdcard,
            sample_sources={"/Samples/hit.wav": str(sample_file)},
            dry_run=True
        )

        assert len(result.sample_files) == 1
        assert not result.song_path.exists()
        assert not sdcard.exists()

    def test_dry_run_song_path(self, tmp_path):
        """Dry run still populates the song path in the result."""
        song = Song(name="Preview")
        result = export_to_sdcard(song, tmp_path, dry_run=True)
        assert result.song_path == tmp_path / "Songs" / "Preview.m8s"

    def test_untitled_song_name(self, tmp_path):
        """Song with no name gets 'Untitled' as filename."""
        song = Song()
        result = export_to_sdcard(song, tmp_path, dry_run=True)
        assert "Untitled" in result.song_path.name

    def test_empty_sample_path_skipped(self, tmp_path):
        """Sampler with empty sample_path is skipped (not an error)."""
        song = Song(name="EmptyPath")
        song.instruments[0] = Sampler(common=SynthCommon(name="Empty"))

        result = export_to_sdcard(song, tmp_path)
        assert result.song_path.exists()
        assert len(result.sample_files) == 0
