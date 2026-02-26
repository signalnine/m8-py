"""FX command name tables for M8 tracker.

Maps command byte values to three-letter display names. Version-dependent:
different firmware versions use different command tables.
"""

from m8py.format.constants import InstrumentKind

# --- Sequencer commands (index 0x00+) ---

SEQ_COMMANDS_V2: list[str] = [
    "ARP", "CHA", "DEL", "GRV", "HOP", "KIL", "RAN", "RET",
    "REP", "NTH", "PSL", "PSN", "PVB", "PVX", "SCA", "SCG",
    "SED", "SNG", "TBL", "THO", "TIC", "TPO", "TSP",
]

SEQ_COMMANDS_V3: list[str] = [
    "ARP", "CHA", "DEL", "GRV", "HOP", "KIL", "RND", "RNL",
    "RET", "REP", "RMX", "NTH", "PSL", "PBN", "PVB", "PVX",
    "SCA", "SCG", "SED", "SNG", "TBL", "THO", "TIC", "TBX",
    "TPO", "TSP", "OFF",
]

# --- Mixer/FX commands (appended after sequencer commands) ---

FX_MIXER_V2: list[str] = [
    "VMV", "XCM", "XCF", "XCW", "XCR", "XDT", "XDF", "XDW",
    "XDR", "XRS", "XRD", "XRM", "XRF", "XRW", "XRZ", "VCH",
    "VCD", "VRE", "VT1", "VT2", "VT3", "VT4", "VT5", "VT6",
    "VT7", "VT8", "DJF", "IVO", "ICH", "IDE", "IRE", "IV2",
    "IC2", "ID2", "IR2", "USB",
]

FX_MIXER_V3: list[str] = FX_MIXER_V2  # Same as v2

FX_MIXER_V4: list[str] = [
    "VMV", "XCM", "XCF", "XCW", "XCR", "XDT", "XDF", "XDW",
    "XDR", "XRS", "XRD", "XRM", "XRF", "XRW", "XRZ", "VCH",
    "VDE", "VRE", "VT1", "VT2", "VT3", "VT4", "VT5", "VT6",
    "VT7", "VT8", "DJC", "VIN", "ICH", "IDE", "IRE", "VI2",
    "IC2", "ID2", "IR2", "USB",
    "DJR", "DJT", "EQM", "EQI", "INS", "RTO", "ARC", "GGR", "NXT",
]

FX_MIXER_V6_2: list[str] = [
    "VMV", "XMM", "XMF", "XMW", "XMR", "XDT", "XDF", "XDW",
    "XDR", "XRS", "XRD", "XRM", "XRF", "XRW", "XRZ", "VMX",
    "VDE", "VRE", "VT1", "VT2", "VT3", "VT4", "VT5", "VT6",
    "VT7", "VT8", "DJC", "VIN", "IMX", "IDE", "IRE", "VI2",
    "IM2", "ID2", "IR2", "USB",
    "DJR", "DJT", "EQM", "EQI", "INS", "RTO", "ARC", "GGR", "NXT",
    "XRH", "XMT", "OTT", "OTC", "OTI", "MTT",
]

# Combined tables: seq + mixer
COMMANDS_V2: list[str] = SEQ_COMMANDS_V2 + FX_MIXER_V2
COMMANDS_V3: list[str] = SEQ_COMMANDS_V3 + FX_MIXER_V3
COMMANDS_V4: list[str] = SEQ_COMMANDS_V3 + FX_MIXER_V4
COMMANDS_V6_2: list[str] = SEQ_COMMANDS_V3 + FX_MIXER_V6_2

# --- Send commands (shared across synth instruments) ---

_SEND_COMMANDS: list[str] = ["SCH", "SDL", "SRV"]
_SEND_COMMANDS_V6_2: list[str] = ["SMX", "SDL", "SRV"]

# --- Per-instrument command names (0x80+ range) ---
# Layout: 15 base commands + 3 send commands + extras
# Total slots: BASE_INSTRUMENT_COMMAND_COUNT (18) + extras

_WAVSYNTH_BASE: list[str] = [
    "VOL", "PIT", "FIN", "OSC", "SIZ", "MUL", "WRP", "MIR",
    "FIL", "CUT", "RES", "AMP", "LIM", "PAN", "DRY",
]
_WAVSYNTH_EXTRA: list[str] = ["SNC", "ERR"]

_MACROSYNTH_BASE: list[str] = [
    "VOL", "PIT", "FIN", "OSC", "TBR", "COL", "DEG", "RED",
    "FIL", "CUT", "RES", "AMP", "LIM", "PAN", "DRY",
]
_MACROSYNTH_EXTRA: list[str] = ["TRG", "ERR"]

_SAMPLER_BASE: list[str] = [
    "VOL", "PIT", "FIN", "PLY", "STA", "LOP", "LEN", "DEG",
    "FIL", "CUT", "RES", "AMP", "LIM", "PAN", "DRY",
]
_SAMPLER_EXTRA: list[str] = ["SLI", "ERR"]

_FMSYNTH_BASE: list[str] = [
    "VOL", "PIT", "FIN", "ALG", "FM1", "FM2", "FM3", "FM4",
    "FLT", "CUT", "RES", "AMP", "LIM", "PAN", "DRY",
]
_FMSYNTH_EXTRA_V5: list[str] = ["FMP"]
_FMSYNTH_EXTRA_V6: list[str] = ["SNC", "ERR"]

_HYPERSYNTH_BASE: list[str] = [
    "VOL", "PIT", "FIN", "CRD", "SHF", "SWM", "WID", "SUB",
    "FLT", "CUT", "RES", "AMP", "LIM", "PAN", "DRY",
]
_HYPERSYNTH_EXTRA: list[str] = ["CVO", "SNC"]

_HYPERSYNTH_BASE_V6: list[str] = [
    "VOL", "PIT", "FIN", "CRD", "CVO", "SWM", "WID", "SUB",
    "FLT", "CUT", "RES", "AMP", "LIM", "PAN", "DRY",
]
_HYPERSYNTH_EXTRA_V6: list[str] = ["SNC", "ERR"]

_EXTERNAL_BASE: list[str] = [
    "VOL", "PIT", "MPB", "MPG", "CCA", "CCB", "CCC", "CCD",
    "FLT", "CUT", "RES", "AMP", "LIM", "PAN", "DRY",
]
_EXTERNAL_EXTRA: list[str] = ["ADD", "CHD"]

_MIDIOUT_COMMANDS: list[str] = [
    "VOL", "PIT", "MPG", "MPB", "ADD", "CHD",
    "CCA", "CCB", "CCC", "CCD", "CCE", "CCF",
    "CCG", "CCH", "CCI", "CCJ",
]


def _build_instr_commands(base: list[str], send: list[str], extra: list[str]) -> list[str]:
    return base + send + extra


# Build version-dependent instrument command tables
INSTRUMENT_COMMANDS: dict[tuple[int, str], list[str]] = {}

# Pre-v6.2 (use SCH/SDL/SRV)
for _kind, _base, _extra in [
    (InstrumentKind.WAVSYNTH, _WAVSYNTH_BASE, _WAVSYNTH_EXTRA),
    (InstrumentKind.MACROSYNTH, _MACROSYNTH_BASE, _MACROSYNTH_EXTRA),
    (InstrumentKind.SAMPLER, _SAMPLER_BASE, _SAMPLER_EXTRA),
    (InstrumentKind.HYPERSYNTH, _HYPERSYNTH_BASE, _HYPERSYNTH_EXTRA),
    (InstrumentKind.EXTERNAL, _EXTERNAL_BASE, _EXTERNAL_EXTRA),
]:
    INSTRUMENT_COMMANDS[(_kind, "v3")] = _build_instr_commands(_base, _SEND_COMMANDS, _extra)

# FMSynth has version-specific extras
INSTRUMENT_COMMANDS[(InstrumentKind.FMSYNTH, "v3")] = _build_instr_commands(
    _FMSYNTH_BASE, _SEND_COMMANDS, _FMSYNTH_EXTRA_V5)
INSTRUMENT_COMMANDS[(InstrumentKind.FMSYNTH, "v6")] = _build_instr_commands(
    _FMSYNTH_BASE, _SEND_COMMANDS, _FMSYNTH_EXTRA_V6)
INSTRUMENT_COMMANDS[(InstrumentKind.FMSYNTH, "v6.2")] = _build_instr_commands(
    _FMSYNTH_BASE, _SEND_COMMANDS_V6_2, _FMSYNTH_EXTRA_V6)

# HyperSynth v6.0 changes base layout
INSTRUMENT_COMMANDS[(InstrumentKind.HYPERSYNTH, "v6")] = _build_instr_commands(
    _HYPERSYNTH_BASE_V6, _SEND_COMMANDS, _HYPERSYNTH_EXTRA_V6)
INSTRUMENT_COMMANDS[(InstrumentKind.HYPERSYNTH, "v6.2")] = _build_instr_commands(
    _HYPERSYNTH_BASE_V6, _SEND_COMMANDS_V6_2, _HYPERSYNTH_EXTRA_V6)

# v6.2 send changes (SMX replaces SCH)
for _kind, _base, _extra in [
    (InstrumentKind.WAVSYNTH, _WAVSYNTH_BASE, _WAVSYNTH_EXTRA),
    (InstrumentKind.MACROSYNTH, _MACROSYNTH_BASE, _MACROSYNTH_EXTRA),
    (InstrumentKind.SAMPLER, _SAMPLER_BASE, _SAMPLER_EXTRA),
    (InstrumentKind.EXTERNAL, _EXTERNAL_BASE, _EXTERNAL_EXTRA),
]:
    INSTRUMENT_COMMANDS[(_kind, "v6.2")] = _build_instr_commands(_base, _SEND_COMMANDS_V6_2, _extra)

# MIDIOut doesn't change across versions
INSTRUMENT_COMMANDS[(InstrumentKind.MIDIOUT, "v3")] = _MIDIOUT_COMMANDS
INSTRUMENT_COMMANDS[(InstrumentKind.MIDIOUT, "v6")] = _MIDIOUT_COMMANDS
INSTRUMENT_COMMANDS[(InstrumentKind.MIDIOUT, "v6.2")] = _MIDIOUT_COMMANDS

# --- Modulator command names ---
# 5 commands per modulator slot, indexed by modulator type and slot number (0-3)

AHD_ENV_COMMANDS: list[list[str]] = [
    ["EA1", "AT1", "HO1", "DE1", "ET1"],
    ["EA2", "AT2", "HO2", "DE2", "ET2"],
    ["EA3", "AT3", "HO3", "DE3", "ET3"],
    ["EA4", "AT4", "HO4", "DE4", "ET4"],
]

ADSR_ENV_COMMANDS: list[list[str]] = [
    ["EA1", "AT1", "DE1", "SU1", "ET1"],
    ["EA2", "AT2", "DE2", "SU2", "ET2"],
    ["EA3", "AT3", "DE3", "SU3", "ET3"],
    ["EA4", "AT4", "DE4", "SU4", "ET4"],
]

DRUM_ENV_COMMANDS: list[list[str]] = [
    ["EA1", "PK1", "BO1", "DE1", "ET1"],
    ["EA2", "PK2", "BO2", "DE2", "ET2"],
    ["EA3", "PK3", "BO3", "DE3", "ET3"],
    ["EA4", "PK4", "BO4", "DE4", "ET4"],
]

LFO_COMMANDS: list[list[str]] = [
    ["LA1", "LO1", "LS1", "LF1", "LT1"],
    ["LA2", "LO2", "LS2", "LF2", "LT2"],
    ["LA3", "LO3", "LS3", "LF3", "LT3"],
    ["LA4", "LO4", "LS4", "LF4", "LT4"],
]

TRIG_ENV_COMMANDS: list[list[str]] = [
    ["EA1", "AT1", "HO1", "SU1", "ET1"],
    ["EA2", "AT2", "HO2", "SU2", "ET2"],
    ["EA3", "AT3", "HO3", "SU3", "ET3"],
    ["EA4", "AT4", "HO4", "SU4", "ET4"],
]

TRACKING_ENV_COMMANDS: list[list[str]] = [
    ["TA1", "TS1", "TL1", "TH1", "TX1"],
    ["TA2", "TS2", "TL2", "TH2", "TX2"],
    ["TA3", "TS3", "TL3", "TH3", "TX3"],
    ["TA4", "TS4", "TL4", "TH4", "TX4"],
]

# Indexed by ModulatorType enum value
MODULATOR_COMMANDS: list[list[list[str]]] = [
    AHD_ENV_COMMANDS,     # 0: AHD_ENV
    ADSR_ENV_COMMANDS,    # 1: ADSR_ENV
    DRUM_ENV_COMMANDS,    # 2: DRUM_ENV
    LFO_COMMANDS,         # 3: LFO
    TRIG_ENV_COMMANDS,    # 4: TRIG_ENV
    TRACKING_ENV_COMMANDS,  # 5: TRACKING_ENV
]

# --- Command layout constants ---
INSTRUMENT_COMMAND_OFFSET = 0x80
BASE_INSTRUMENT_COMMAND_COUNT = 18
COMMANDS_PER_MODULATOR = 5
MODULATOR_COUNT = 4


def _version_key(major: int, minor: int) -> str:
    """Map file format version to command table key."""
    if major >= 6 and minor >= 1:
        return "v6.2"
    if major >= 6:
        return "v6"
    return "v3"


def _get_command_table(major: int, minor: int) -> list[str]:
    """Get the combined seq+mixer command table for a version."""
    if major >= 6 and minor >= 1:
        return COMMANDS_V6_2
    if major >= 4:
        return COMMANDS_V4
    if major >= 3:
        return COMMANDS_V3
    return COMMANDS_V2


def fx_command_name(
    command: int,
    version: tuple[int, int] | None = None,
    instrument_kind: int | None = None,
) -> str:
    """Look up the 3-letter display name for an FX command byte.

    Args:
        command: The raw command byte (0x00-0xFF).
        version: (major, minor) file format version tuple. Defaults to v4.
        instrument_kind: InstrumentKind value for 0x80+ instrument commands.

    Returns:
        3-letter command name, or "---" for empty (0xFF), or hex fallback.
    """
    if command == 0xFF:
        return "---"

    major, minor = version if version is not None else (4, 0)
    table = _get_command_table(major, minor)

    # Sequencer + mixer range
    if command < len(table):
        return table[command]

    # Instrument-specific range (0x80+)
    if command >= INSTRUMENT_COMMAND_OFFSET and instrument_kind is not None:
        cmd_offset = command - INSTRUMENT_COMMAND_OFFSET

        # Get instrument command table
        vkey = _version_key(major, minor)
        instr_table = INSTRUMENT_COMMANDS.get((instrument_kind, vkey))
        if instr_table is None:
            # Fall back to v3
            instr_table = INSTRUMENT_COMMANDS.get((instrument_kind, "v3"))

        if instr_table is not None:
            # Base instrument commands (first 18 slots)
            if cmd_offset < BASE_INSTRUMENT_COMMAND_COUNT:
                if cmd_offset < len(instr_table):
                    return instr_table[cmd_offset]

            # Modulator commands (slots 18-37, 5 per modulator × 4 modulators)
            mod_offset = cmd_offset - BASE_INSTRUMENT_COMMAND_COUNT
            if 0 <= mod_offset < COMMANDS_PER_MODULATOR * MODULATOR_COUNT:
                # We don't know the modulator type here, so return generic
                mod_idx = mod_offset // COMMANDS_PER_MODULATOR
                cmd_in_mod = mod_offset % COMMANDS_PER_MODULATOR
                # Use AHD as default since we can't determine type from command alone
                return AHD_ENV_COMMANDS[mod_idx][cmd_in_mod]

            # Extra commands after modulators
            extra_offset = cmd_offset - (COMMANDS_PER_MODULATOR * MODULATOR_COUNT)
            if 0 <= extra_offset < len(instr_table):
                return instr_table[extra_offset]

    return f"?{command:02X}"
