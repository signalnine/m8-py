"""Tests for pretty-print rendering functions."""

import pytest
from m8py.display.render import (
    render_phrase, render_chain, render_table,
    render_song_grid, render_instrument_summary, render_song_overview,
)
from m8py.models.phrase import Phrase, PhraseStep
from m8py.models.chain import Chain, ChainStep
from m8py.models.table import Table, TableStep
from m8py.models.fx import FX
from m8py.models.song import Song
from m8py.models.instrument import WavSynth, MacroSynth, EmptyInstrument, SynthCommon
from m8py.format.constants import EMPTY


class TestRenderPhrase:
    def test_empty_phrase(self):
        p = Phrase()
        result = render_phrase(p)
        assert "ROW NOTE VEL INS FX1" in result
        # All rows should have "---" for note
        lines = result.split("\n")
        assert len(lines) == 17  # header + 16 rows
        assert "---" in lines[1]

    def test_phrase_with_notes(self):
        p = Phrase()
        p.steps[0].note = 60  # C-5
        p.steps[0].velocity = 0x80
        p.steps[0].instrument = 0x00
        result = render_phrase(p)
        lines = result.split("\n")
        assert "C-5" in lines[1]
        assert "80" in lines[1]
        assert "00" in lines[1]

    def test_phrase_with_fx(self):
        p = Phrase()
        p.steps[0].fx1 = FX(command=0x00, value=0x03)  # ARP 03
        result = render_phrase(p)
        assert "ARP 03" in result

    def test_empty_fx_shows_dashes(self):
        p = Phrase()
        result = render_phrase(p)
        assert "--- --" in result


class TestRenderChain:
    def test_empty_chain(self):
        c = Chain()
        result = render_chain(c)
        assert "ROW PHR TSP" in result
        lines = result.split("\n")
        assert len(lines) == 17

    def test_chain_with_phrases(self):
        c = Chain()
        c.steps[0].phrase = 0x10
        c.steps[0].transpose = 0x0C
        result = render_chain(c)
        lines = result.split("\n")
        assert "10" in lines[1]
        assert "0C" in lines[1]


class TestRenderTable:
    def test_empty_table(self):
        t = Table()
        result = render_table(t)
        assert "ROW TSP VEL FX1" in result
        lines = result.split("\n")
        assert len(lines) == 17

    def test_table_with_fx(self):
        t = Table()
        t.steps[0].fx1 = FX(command=0x00, value=0x07)
        result = render_table(t)
        assert "ARP 07" in result


class TestRenderSongGrid:
    def test_empty_song(self):
        s = Song()
        result = render_song_grid(s)
        assert "ROW T1 T2 T3 T4 T5 T6 T7 T8" in result
        lines = result.split("\n")
        assert len(lines) >= 2  # header + at least 1 row

    def test_song_with_chains(self):
        s = Song()
        s.song_steps[0].tracks[0] = 0x00
        s.song_steps[0].tracks[1] = 0x01
        result = render_song_grid(s)
        lines = result.split("\n")
        assert "00 01" in lines[1]

    def test_explicit_rows(self):
        s = Song()
        result = render_song_grid(s, rows=4)
        lines = result.split("\n")
        assert len(lines) == 5  # header + 4 rows


class TestRenderInstrumentSummary:
    def test_wavsynth(self):
        ws = WavSynth(common=SynthCommon(name="Lead"))
        result = render_instrument_summary(ws)
        assert "WAVSYNTH" in result
        assert "Lead" in result

    def test_macrosynth(self):
        ms = MacroSynth(common=SynthCommon(name="Bass"))
        result = render_instrument_summary(ms)
        assert "MACROSYN" in result
        assert "Bass" in result

    def test_empty_instrument(self):
        e = EmptyInstrument()
        assert render_instrument_summary(e) == "---"


class TestRenderSongOverview:
    def test_basic_overview(self):
        s = Song(name="TestSong")
        s.instruments[0] = WavSynth(common=SynthCommon(name="Synth"))
        result = render_song_overview(s)
        assert "Song: TestSong" in result
        assert "Instruments:" in result
        assert "WAVSYNTH" in result
        assert "Synth" in result

    def test_empty_song_overview(self):
        s = Song(name="Empty")
        result = render_song_overview(s)
        assert "Song: Empty" in result
        assert "Instruments:" in result
