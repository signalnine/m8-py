from m8py.format.constants import (
    HEADER_MAGIC, HEADER_SIZE, EMPTY, INSTRUMENT_SIZE,
    FileType, InstrumentKind, NOTE_OFF_THRESHOLD,
)

def test_magic_bytes():
    assert HEADER_MAGIC == b"M8VERSION\x00"
    assert len(HEADER_MAGIC) == 10

def test_header_size():
    assert HEADER_SIZE == 14

def test_empty_sentinel():
    assert EMPTY == 0xFF

def test_instrument_size():
    assert INSTRUMENT_SIZE == 215

def test_file_types():
    assert FileType.SONG == 0x00
    assert FileType.INSTRUMENT == 0x01
    assert FileType.THEME == 0x02
    assert FileType.SCALE == 0x03

def test_instrument_kinds():
    assert InstrumentKind.WAVSYNTH == 0x00
    assert InstrumentKind.MACROSYNTH == 0x01
    assert InstrumentKind.SAMPLER == 0x02
    assert InstrumentKind.MIDIOUT == 0x03
    assert InstrumentKind.FMSYNTH == 0x04
    assert InstrumentKind.HYPERSYNTH == 0x05
    assert InstrumentKind.EXTERNAL == 0x06
    assert InstrumentKind.NONE == 0xFF

def test_note_off():
    assert NOTE_OFF_THRESHOLD == 0x80
