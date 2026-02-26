"""Tests for the high-level I/O layer (m8py.io)."""
import pytest

from m8py.io import load, load_song, load_instrument, load_theme, load_scale, save
from m8py.format.errors import M8ParseError
from m8py.models.song import Song
from m8py.models.theme import Theme, RGB
from m8py.models.scale import Scale
from m8py.models.instrument import WavSynth, SynthCommon, EmptyInstrument


class TestIO:
    def test_save_load_song_roundtrip(self, tmp_path):
        song = Song()
        song.name = "IOTest"
        song.tempo = 135.0
        path = tmp_path / "test.m8s"
        save(song, path)

        loaded = load(path)
        assert isinstance(loaded, Song)
        assert loaded.name == "IOTest"
        assert abs(loaded.tempo - 135.0) < 0.01

    def test_save_load_theme_roundtrip(self, tmp_path):
        theme = Theme(background=RGB(10, 20, 30), cursor=RGB(100, 200, 255))
        path = tmp_path / "test.m8t"
        save(theme, path)

        loaded = load(path)
        assert isinstance(loaded, Theme)
        assert loaded.background.r == 10
        assert loaded.background.g == 20
        assert loaded.background.b == 30
        assert loaded.cursor.r == 100
        assert loaded.cursor.g == 200
        assert loaded.cursor.b == 255

    def test_save_load_scale_roundtrip(self, tmp_path):
        scale = Scale(name="TestScale", note_enable=0x0AAA)
        path = tmp_path / "test.m8n"
        save(scale, path)

        loaded = load(path)
        assert isinstance(loaded, Scale)
        assert loaded.name == "TestScale"
        assert loaded.note_enable == 0x0AAA

    def test_save_load_instrument_roundtrip(self, tmp_path):
        ws = WavSynth(common=SynthCommon(name="MySynth"))
        ws.shape = 7
        path = tmp_path / "test.m8i"
        save(ws, path)

        loaded = load(path)
        assert isinstance(loaded, WavSynth)
        assert loaded.common.name == "MySynth"
        assert loaded.shape == 7

    def test_load_song_typed(self, tmp_path):
        song = Song(name="TypedLoad")
        path = tmp_path / "test.m8s"
        save(song, path)
        loaded = load_song(path)
        assert isinstance(loaded, Song)
        assert loaded.name == "TypedLoad"

    def test_load_song_on_theme_raises(self, tmp_path):
        theme = Theme()
        path = tmp_path / "test.m8t"
        save(theme, path)
        with pytest.raises(M8ParseError, match="expected SONG"):
            load_song(path)

    def test_load_theme_typed(self, tmp_path):
        theme = Theme(background=RGB(1, 2, 3))
        path = tmp_path / "test.m8t"
        save(theme, path)
        loaded = load_theme(path)
        assert isinstance(loaded, Theme)

    def test_load_scale_typed(self, tmp_path):
        scale = Scale(name="S")
        path = tmp_path / "test.m8n"
        save(scale, path)
        loaded = load_scale(path)
        assert isinstance(loaded, Scale)

    def test_load_instrument_typed(self, tmp_path):
        ws = WavSynth()
        path = tmp_path / "test.m8i"
        save(ws, path)
        loaded = load_instrument(path)
        assert isinstance(loaded, WavSynth)

    def test_load_truncated_file_raises(self, tmp_path):
        path = tmp_path / "bad.m8s"
        path.write_bytes(b"M8VERSION\x00")  # only 10 bytes, need 14
        with pytest.raises(M8ParseError):
            load(path)

    def test_load_empty_file_raises(self, tmp_path):
        path = tmp_path / "empty.m8s"
        path.write_bytes(b"")
        with pytest.raises(M8ParseError):
            load(path)

    def test_load_instrument_on_song_raises(self, tmp_path):
        song = Song()
        path = tmp_path / "test.m8s"
        save(song, path)
        with pytest.raises(M8ParseError, match="expected INSTRUMENT"):
            load_instrument(path)

    def test_load_theme_on_scale_raises(self, tmp_path):
        scale = Scale()
        path = tmp_path / "test.m8n"
        save(scale, path)
        with pytest.raises(M8ParseError, match="expected THEME"):
            load_theme(path)

    def test_load_scale_on_theme_raises(self, tmp_path):
        theme = Theme()
        path = tmp_path / "test.m8t"
        save(theme, path)
        with pytest.raises(M8ParseError, match="expected SCALE"):
            load_scale(path)
