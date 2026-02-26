"""Tests for display name lookup tables and functions."""

import pytest
from m8py.display.names import (
    note_name,
    shape_name,
    filter_name,
    WAVSYNTH_SHAPES,
    MACROSYNTH_SHAPES,
    FM_ALGORITHMS,
    FM_OPERATOR_SHAPES,
    COMMON_FILTER_TYPES,
    WAVSYNTH_FILTER_TYPES,
    LFO_SHAPES,
    LFO_TRIGGER_MODES,
    SAMPLE_PLAY_MODES,
    LIMIT_TYPES,
    MODULATOR_DESTINATIONS,
)
from m8py.format.constants import InstrumentKind


class TestTableCounts:
    def test_wavsynth_shapes(self):
        assert len(WAVSYNTH_SHAPES) == 70

    def test_macrosynth_shapes(self):
        assert len(MACROSYNTH_SHAPES) == 48

    def test_fm_algorithms(self):
        assert len(FM_ALGORITHMS) == 12

    def test_fm_operator_shapes(self):
        assert len(FM_OPERATOR_SHAPES) == 77

    def test_common_filter_types(self):
        assert len(COMMON_FILTER_TYPES) == 8

    def test_wavsynth_filter_types(self):
        assert len(WAVSYNTH_FILTER_TYPES) == 12

    def test_lfo_shapes(self):
        assert len(LFO_SHAPES) == 20

    def test_lfo_trigger_modes(self):
        assert len(LFO_TRIGGER_MODES) == 4

    def test_sample_play_modes(self):
        assert len(SAMPLE_PLAY_MODES) == 15

    def test_limit_types(self):
        assert len(LIMIT_TYPES) == 9

    def test_modulator_destinations_all_kinds(self):
        for kind in (InstrumentKind.WAVSYNTH, InstrumentKind.MACROSYNTH,
                     InstrumentKind.SAMPLER, InstrumentKind.MIDIOUT,
                     InstrumentKind.FMSYNTH, InstrumentKind.HYPERSYNTH,
                     InstrumentKind.EXTERNAL):
            assert kind in MODULATOR_DESTINATIONS


class TestNoteName:
    def test_c0(self):
        assert note_name(0) == "C-0"

    def test_c5_midi60(self):
        assert note_name(60) == "C-5"

    def test_g10_midi127(self):
        assert note_name(127) == "G-10"

    def test_a5_midi69(self):
        assert note_name(69) == "A-5"

    def test_f_sharp_4_midi54(self):
        assert note_name(54) == "F#4"

    def test_out_of_range(self):
        assert note_name(200) == "0xC8"


class TestShapeName:
    def test_wavsynth_first(self):
        assert shape_name(InstrumentKind.WAVSYNTH, 0) == "PULSE12"

    def test_wavsynth_last(self):
        assert shape_name(InstrumentKind.WAVSYNTH, 69) == "WT VOXSYNT"

    def test_macrosynth_first(self):
        assert shape_name(InstrumentKind.MACROSYNTH, 0) == "CSAW"

    def test_macrosynth_last(self):
        assert shape_name(InstrumentKind.MACROSYNTH, 47) == "MORSE"

    def test_fm_algorithm(self):
        assert shape_name(InstrumentKind.FMSYNTH, 0) == "A>B>C>D"
        assert shape_name(InstrumentKind.FMSYNTH, 11) == "A+B+C+D"

    def test_unknown_value(self):
        assert shape_name(InstrumentKind.WAVSYNTH, 200) == "0xC8"

    def test_unknown_kind(self):
        assert shape_name(InstrumentKind.SAMPLER, 5) == "0x05"


class TestFilterName:
    def test_common(self):
        assert filter_name(InstrumentKind.MACROSYNTH, 0) == "OFF"
        assert filter_name(InstrumentKind.MACROSYNTH, 1) == "LOWPASS"

    def test_wavsynth_extra(self):
        assert filter_name(InstrumentKind.WAVSYNTH, 8) == "WAV LP"
        assert filter_name(InstrumentKind.WAVSYNTH, 11) == "WAV BS"

    def test_common_value_on_wavsynth(self):
        assert filter_name(InstrumentKind.WAVSYNTH, 0) == "OFF"

    def test_unknown(self):
        assert filter_name(InstrumentKind.FMSYNTH, 99) == "0x63"
