from enum import IntEnum

HEADER_MAGIC = b"M8VERSION\x00"
HEADER_SIZE = 14
EMPTY = 0xFF
INSTRUMENT_SIZE = 215
NOTE_OFF_THRESHOLD = 0x80

N_SONG_STEPS = 256
N_TRACKS = 8
N_PHRASES = 255
N_CHAINS = 255
N_INSTRUMENTS = 128
N_TABLES = 256
N_GROOVES = 32
N_SCALES = 16
N_MIDI_MAPPINGS = 128
STEPS_PER_PHRASE = 16
STEPS_PER_CHAIN = 16
STEPS_PER_TABLE = 16
STEPS_PER_GROOVE = 16

class FileType(IntEnum):
    SONG = 0x00
    INSTRUMENT = 0x01
    THEME = 0x02
    SCALE = 0x03

class InstrumentKind(IntEnum):
    WAVSYNTH = 0x00
    MACROSYNTH = 0x01
    SAMPLER = 0x02
    MIDIOUT = 0x03
    FMSYNTH = 0x04
    HYPERSYNTH = 0x05
    EXTERNAL = 0x06
    NONE = 0xFF

class ModulatorType(IntEnum):
    AHD_ENV = 0
    ADSR_ENV = 1
    DRUM_ENV = 2
    LFO = 3
    TRIG_ENV = 4
    TRACKING_ENV = 5

class LfoShape(IntEnum):
    TRI = 0; SIN = 1; RAMP_DOWN = 2; RAMP_UP = 3
    EXP_DN = 4; EXP_UP = 5; SQR_DN = 6; SQR_UP = 7
    RANDOM = 8; DRUNK = 9
    TRI_T = 10; SIN_T = 11; RAMPD_T = 12; RAMPU_T = 13
    EXPD_T = 14; EXPU_T = 15; SQ_D_T = 16; SQ_U_T = 17
    RAND_T = 18; DRNK_T = 19

class LfoTriggerMode(IntEnum):
    FREE = 0; RETRIG = 1; HOLD = 2; ONCE = 3

class SamplePlayMode(IntEnum):
    FWD = 0; REV = 1; FWDLOOP = 2; REVLOOP = 3
    FWD_PP = 4; REV_PP = 5; OSC = 6; OSC_REV = 7; OSC_PP = 8

class LimitType(IntEnum):
    CLIP = 0; SIN = 1; FOLD = 2; WRAP = 3
    POST = 4; POSTAD = 5; POST_W1 = 6; POST_W2 = 7
