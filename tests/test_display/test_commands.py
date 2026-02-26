"""Tests for FX command name lookup."""

import pytest
from m8py.display.commands import (
    fx_command_name,
    COMMANDS_V2, COMMANDS_V3, COMMANDS_V4, COMMANDS_V6_2,
    SEQ_COMMANDS_V3, FX_MIXER_V4, FX_MIXER_V6_2,
    INSTRUMENT_COMMANDS,
    AHD_ENV_COMMANDS, ADSR_ENV_COMMANDS, DRUM_ENV_COMMANDS,
    LFO_COMMANDS, TRIG_ENV_COMMANDS, TRACKING_ENV_COMMANDS,
)
from m8py.display.formatters import format_fx
from m8py.format.constants import InstrumentKind


class TestCommandTableSizes:
    def test_v2_table(self):
        assert len(COMMANDS_V2) == 23 + 36  # 59

    def test_v3_table(self):
        assert len(COMMANDS_V3) == 27 + 36  # 63

    def test_v4_table(self):
        assert len(COMMANDS_V4) == 27 + 45  # 72

    def test_v6_2_table(self):
        assert len(COMMANDS_V6_2) == 27 + 51  # 78

    def test_seq_v3_count(self):
        assert len(SEQ_COMMANDS_V3) == 27


class TestSequencerCommands:
    def test_arp_is_first(self):
        assert fx_command_name(0x00) == "ARP"

    def test_v3_new_commands(self):
        # v3 added RND(6), RNL(7) at indexes 6-7
        assert fx_command_name(0x06, version=(3, 0)) == "RND"
        assert fx_command_name(0x07, version=(3, 0)) == "RNL"

    def test_v3_off_command(self):
        # OFF is last seq command in v3 (index 26)
        assert fx_command_name(0x1A, version=(3, 0)) == "OFF"


class TestMixerCommands:
    def test_vmv_after_seq(self):
        # VMV is first mixer command, at index 27 in v4
        assert fx_command_name(0x1B, version=(4, 0)) == "VMV"

    def test_v4_new_commands(self):
        # v4 added DJR..NXT at end of mixer (indexes 0x3F-0x47)
        assert fx_command_name(0x3F, version=(4, 0)) == "DJR"
        assert fx_command_name(0x47, version=(4, 0)) == "NXT"

    def test_v6_2_renamed_commands(self):
        # v6.2 renamed XCM->XMM, XCF->XMF, etc.
        assert fx_command_name(0x1C, version=(6, 1)) == "XMM"  # was XCM in v4
        assert fx_command_name(0x1D, version=(6, 1)) == "XMF"

    def test_v6_2_new_commands(self):
        # v6.2 added XRH, XMT, OTT, OTC, OTI, MTT
        assert fx_command_name(0x48, version=(6, 1)) == "XRH"
        assert fx_command_name(0x4A, version=(6, 1)) == "OTT"
        assert fx_command_name(0x4D, version=(6, 1)) == "MTT"


class TestVersionDependentNames:
    def test_same_index_different_name(self):
        # Index 0x1C: XCM in v4, XMM in v6.2
        assert fx_command_name(0x1C, version=(4, 0)) == "XCM"
        assert fx_command_name(0x1C, version=(6, 1)) == "XMM"

    def test_v2_vs_v3_at_index_6(self):
        # v2 has RAN at index 6, v3 has RND
        assert fx_command_name(0x06, version=(2, 0)) == "RAN"
        assert fx_command_name(0x06, version=(3, 0)) == "RND"


class TestEmptyAndUnknown:
    def test_empty_command(self):
        assert fx_command_name(0xFF) == "---"

    def test_unknown_command(self):
        # Command between seq+mixer range and 0x80 should be unknown
        result = fx_command_name(0x70)
        assert result.startswith("?")


class TestInstrumentCommands:
    def test_wavsynth_vol(self):
        assert fx_command_name(0x80, instrument_kind=InstrumentKind.WAVSYNTH) == "VOL"

    def test_wavsynth_osc(self):
        assert fx_command_name(0x83, instrument_kind=InstrumentKind.WAVSYNTH) == "OSC"

    def test_sampler_ply(self):
        assert fx_command_name(0x83, instrument_kind=InstrumentKind.SAMPLER) == "PLY"

    def test_fmsynth_alg(self):
        assert fx_command_name(0x83, instrument_kind=InstrumentKind.FMSYNTH) == "ALG"

    def test_midiout_mpg(self):
        assert fx_command_name(0x82, instrument_kind=InstrumentKind.MIDIOUT) == "MPG"


class TestModulatorCommands:
    def test_ahd_env_commands(self):
        assert AHD_ENV_COMMANDS[0] == ["EA1", "AT1", "HO1", "DE1", "ET1"]
        assert AHD_ENV_COMMANDS[3] == ["EA4", "AT4", "HO4", "DE4", "ET4"]

    def test_adsr_env_commands(self):
        assert ADSR_ENV_COMMANDS[0] == ["EA1", "AT1", "DE1", "SU1", "ET1"]

    def test_drum_env_commands(self):
        assert DRUM_ENV_COMMANDS[0] == ["EA1", "PK1", "BO1", "DE1", "ET1"]

    def test_lfo_commands(self):
        assert LFO_COMMANDS[0] == ["LA1", "LO1", "LS1", "LF1", "LT1"]

    def test_tracking_env_commands(self):
        assert TRACKING_ENV_COMMANDS[0] == ["TA1", "TS1", "TL1", "TH1", "TX1"]


class TestFormatFx:
    def test_empty(self):
        class FakeFX:
            command = 0xFF
            value = 0x00
        assert format_fx(FakeFX()) == "--- --"

    def test_arp(self):
        class FakeFX:
            command = 0x00
            value = 0x03
        assert format_fx(FakeFX()) == "ARP 03"

    def test_with_version(self):
        class FakeFX:
            command = 0x1C
            value = 0x80
        assert format_fx(FakeFX(), version=(6, 1)) == "XMM 80"
