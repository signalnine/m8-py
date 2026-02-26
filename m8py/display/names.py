"""Display name tables for M8 enum values.

Pure-data module mapping raw byte values to human-readable display strings.
All tables are dict[int, str]. Unknown values fall back to hex representation.
"""

from m8py.format.constants import InstrumentKind

# --- Note names ---

_NOTE_NAMES = ("C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-")


def note_name(midi: int) -> str:
    """Convert MIDI note number to display string like 'C-4' or 'G#9'."""
    if not 0 <= midi <= 127:
        return f"0x{midi:02X}"
    octave = midi // 12
    note = midi % 12
    return f"{_NOTE_NAMES[note]}{octave}"


# --- WavSynth shapes (70 entries, 0-69) ---

WAVSYNTH_SHAPES: dict[int, str] = {
    0: "PULSE12", 1: "PULSE25", 2: "PULSE50", 3: "PULSE75",
    4: "SAW", 5: "TRIANGLE", 6: "SINE",
    7: "NOISE:P", 8: "NOISE",
    9: "WT CRUSH", 10: "WT FOLDING", 11: "WT FREQ", 12: "WT FUZZY",
    13: "WT GHOST", 14: "WT GRAPHIC", 15: "WT LFOPLAY", 16: "WT LIQUID",
    17: "WT MORPHNG", 18: "WT MYSTIC", 19: "WT STICKY", 20: "WT TIDAL",
    21: "WT TIDY", 22: "WT TUBE", 23: "WT UMBRELL", 24: "WT UNWIND",
    25: "WT VIRAL", 26: "WT WAVES", 27: "WT DRIP", 28: "WT FROGGY",
    29: "WT INSONIC", 30: "WT RADIUS", 31: "WT SCRATCH", 32: "WT SMOOTH",
    33: "WT WOBBLE", 34: "WT ASIMMTR", 35: "WT BLEEN", 36: "WT FRACTAL",
    37: "WT GENTLE", 38: "WT HARMNIC", 39: "WT HYPNOTC", 40: "WT ITERATV",
    41: "WT MICROWV", 42: "WT PLAIT01", 43: "WT PLAIT02", 44: "WT RISEFL",
    45: "WT TONAL", 46: "WT TWINE", 47: "WT ALIEN", 48: "WT CYBRNRT",
    49: "WT DISORDR", 50: "WT FORMANT", 51: "WT HYPER", 52: "WT JAGGED",
    53: "WT MIXED", 54: "WT MULTPLY", 55: "WT NOWHERE", 56: "WT PINBALL",
    57: "WT RINGS", 58: "WT SHIMMER", 59: "WT SPECTRL", 60: "WT SPOOKY",
    61: "WT TRANSFRM", 62: "WT TWISTED", 63: "WT VOCAL", 64: "WT WASHED",
    65: "WT WONDER", 66: "WT WOWEE", 67: "WT ZAP", 68: "WT BRAIDS",
    69: "WT VOXSYNT",
}

# --- MacroSynth shapes (48 entries, 0-47) ---

MACROSYNTH_SHAPES: dict[int, str] = {
    0: "CSAW", 1: "MORPH", 2: "SAW SQU", 3: "SIN TRI",
    4: "BUZZ", 5: "SQU SUB", 6: "SAW SUB", 7: "SQU SYN",
    8: "SAW SYN", 9: "TRI SAW", 10: "TRI SQU", 11: "TRI TRI",
    12: "TRI SIN", 13: "TRI RNG", 14: "SAW SWM", 15: "SAW CMB",
    16: "TOY*", 17: "DGTL LP", 18: "DGTL PK", 19: "DGTL BP",
    20: "DGTL HP", 21: "VOSIM", 22: "VOWEL", 23: "VOW FOF",
    24: "HARMNCS", 25: "FM", 26: "FDBK FM", 27: "CHAOFBFM",
    28: "PLUCKED", 29: "BOWED", 30: "BLOWN", 31: "FLUTED",
    32: "STR BELL", 33: "STR DRUM", 34: "KICK", 35: "CYMBAL",
    36: "SNARE", 37: "WAVETBL", 38: "WAV MAP", 39: "WAV LIN",
    40: "WAV PAR", 41: "FLT NOIS", 42: "TW PEAKS", 43: "CLK NOIS",
    44: "GRANULR", 45: "PARTCLE", 46: "DGTL MOD", 47: "MORSE",
}

# --- FM algorithms (12 entries, 0-11) ---

FM_ALGORITHMS: dict[int, str] = {
    0: "A>B>C>D",
    1: "[A+B]>C>D",
    2: "[A>B+C]>D",
    3: "[A>B+A>C]>D",
    4: "[A+B+C]>D",
    5: "[A>B>C]+D",
    6: "[A>B>C]+[A>B>D]",
    7: "[A>B]+[C>D]",
    8: "[A>B]+[A>C]+[A>D]",
    9: "[A>B]+[A>C]+D",
    10: "[A>B]+C+D",
    11: "A+B+C+D",
}

# --- FM operator shapes (77 entries, 0-76) ---

FM_OPERATOR_SHAPES: dict[int, str] = {
    0: "SIN", 1: "SW2", 2: "SW3", 3: "SW4", 4: "SW5", 5: "SW6",
    6: "TRI", 7: "SAW", 8: "SQR", 9: "PUL", 10: "IMP",
    11: "NOI", 12: "NLP", 13: "NHP", 14: "NBP", 15: "CLK",
}
# Entries 16-76 are v4.1+ waveforms (W09..W45)
for _i in range(16, 77):
    FM_OPERATOR_SHAPES[_i] = f"W{_i - 16 + 9:02X}"

# --- Filter types ---

COMMON_FILTER_TYPES: dict[int, str] = {
    0: "OFF", 1: "LOWPASS", 2: "HIGHPAS", 3: "BANDPAS",
    4: "BANDSTP", 5: "LP > HP", 6: "ZDF LP", 7: "ZDF HP",
}

WAVSYNTH_FILTER_TYPES: dict[int, str] = {
    **COMMON_FILTER_TYPES,
    8: "WAV LP", 9: "WAV HP", 10: "WAV BP", 11: "WAV BS",
}

# --- LFO shapes (20 entries, 0-19) ---

LFO_SHAPES: dict[int, str] = {
    0: "TRI", 1: "SIN", 2: "RAMP DN", 3: "RAMP UP",
    4: "EXP DN", 5: "EXP UP", 6: "SQR DN", 7: "SQR UP",
    8: "RANDOM", 9: "DRUNK",
    10: "TRI T", 11: "SIN T", 12: "RMPD T", 13: "RMPU T",
    14: "EXPD T", 15: "EXPU T", 16: "SQ D T", 17: "SQ U T",
    18: "RAND T", 19: "DRNK T",
}

# --- LFO trigger modes (4 entries, 0-3) ---

LFO_TRIGGER_MODES: dict[int, str] = {
    0: "FREE", 1: "RETRIG", 2: "HOLD", 3: "ONCE",
}

# --- Sample play modes (15 entries, 0-14) ---

SAMPLE_PLAY_MODES: dict[int, str] = {
    0: "FWD", 1: "REV", 2: "FWD LOP", 3: "REV LOP",
    4: "FWD PP", 5: "REV PP", 6: "OSC", 7: "OSC REV", 8: "OSC PP",
    9: "REPITCH", 10: "REP REV", 11: "REP PP",
    12: "REP BPM", 13: "BPM REV", 14: "BPM PP",
}

# --- Limit types (9 entries, 0-8) ---

LIMIT_TYPES: dict[int, str] = {
    0: "CLIP", 1: "SIN", 2: "FOLD", 3: "WRAP",
    4: "POST", 5: "POSTAD", 6: "POST:W1", 7: "POST:W2", 8: "POST:W3",
}

# --- Modulator destinations per instrument kind ---
# dict[InstrumentKind, dict[int, str]]

_SYNTH_COMMON_TAIL: dict[int, str] = {
    7: "CUTOFF", 8: "RES", 9: "AMP", 10: "PAN",
    11: "MOD AMT", 12: "MOD RATE", 13: "MOD BOTH", 14: "MOD BINV",
}

MODULATOR_DESTINATIONS: dict[int, dict[int, str]] = {
    InstrumentKind.WAVSYNTH: {
        0: "OFF", 1: "VOLUME", 2: "PITCH",
        3: "SIZE", 4: "MULT", 5: "WARP", 6: "SCAN",
        **_SYNTH_COMMON_TAIL,
    },
    InstrumentKind.MACROSYNTH: {
        0: "OFF", 1: "VOLUME", 2: "PITCH",
        3: "TIMBRE", 4: "COLOR", 5: "DEGRADE", 6: "REDUX",
        **_SYNTH_COMMON_TAIL,
    },
    InstrumentKind.SAMPLER: {
        0: "OFF", 1: "VOLUME", 2: "PITCH",
        3: "LOOP ST", 4: "LENGTH", 5: "DEGRADE",
        6: "CUTOFF", 7: "RES", 8: "AMP", 9: "PAN",
        10: "MOD AMT", 11: "MOD RATE", 12: "MOD BOTH", 13: "MOD BINV",
    },
    InstrumentKind.MIDIOUT: {
        0: "OFF", 1: "CCA", 2: "CCB", 3: "CCC", 4: "CCD",
        5: "CCE", 6: "CCF", 7: "CCG", 8: "CCH", 9: "CCI", 10: "CCJ",
        11: "MOD AMT", 12: "MOD RATE", 13: "MOD BOTH", 14: "MOD BINV",
    },
    InstrumentKind.FMSYNTH: {
        0: "OFF", 1: "VOLUME", 2: "PITCH",
        3: "MOD1", 4: "MOD2", 5: "MOD3", 6: "MOD4",
        **_SYNTH_COMMON_TAIL,
    },
    InstrumentKind.HYPERSYNTH: {
        0: "OFF", 1: "VOLUME", 2: "PITCH",
        3: "SHIFT", 4: "SWARM", 5: "WIDTH", 6: "SUBOSC",
        **_SYNTH_COMMON_TAIL,
    },
    InstrumentKind.EXTERNAL: {
        0: "OFF", 1: "VOLUME",
        2: "CUTOFF", 3: "RES", 4: "AMP", 5: "PAN",
        6: "CCA", 7: "CCB", 8: "CCC", 9: "CCD",
        10: "MOD AMT", 11: "MOD RATE", 12: "MOD BOTH", 13: "MOD BINV",
    },
}


# --- Lookup helpers ---

def _hex_fallback(value: int) -> str:
    return f"0x{value:02X}"


def shape_name(kind: int, value: int) -> str:
    """Look up display name for an instrument shape value.

    Args:
        kind: InstrumentKind value (0=WAVSYNTH, 1=MACROSYNTH, etc.)
        value: Raw shape byte value.
    """
    table: dict[int, str] | None = None
    if kind == InstrumentKind.WAVSYNTH:
        table = WAVSYNTH_SHAPES
    elif kind == InstrumentKind.MACROSYNTH:
        table = MACROSYNTH_SHAPES
    elif kind == InstrumentKind.FMSYNTH:
        table = FM_ALGORITHMS  # "shape" for FM is the algorithm
    if table is None:
        return _hex_fallback(value)
    return table.get(value, _hex_fallback(value))


def filter_name(kind: int, value: int) -> str:
    """Look up display name for a filter type value.

    Args:
        kind: InstrumentKind value.
        value: Raw filter_type byte value.
    """
    if kind == InstrumentKind.WAVSYNTH:
        return WAVSYNTH_FILTER_TYPES.get(value, _hex_fallback(value))
    return COMMON_FILTER_TYPES.get(value, _hex_fallback(value))
