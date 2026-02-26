import pytest
from m8py.compose.notation import normalize_note, parse_pattern

def test_normalize_string():
    assert normalize_note("C4") == 60
    assert normalize_note("A4") == 69

def test_normalize_sharp():
    assert normalize_note("F#3") == 54

def test_normalize_flat():
    assert normalize_note("Bb4") == 70

def test_normalize_int():
    assert normalize_note(60) == 60
    assert normalize_note(0) == 0

def test_normalize_invalid():
    with pytest.raises(ValueError):
        normalize_note("X4")
    with pytest.raises(ValueError):
        normalize_note(128)

def test_parse_simple():
    steps = parse_pattern("C4 E4 G4")
    assert len(steps) == 3
    assert steps[0].note == 60
    assert steps[1].note == 64
    assert steps[2].note == 67

def test_parse_empty():
    steps = parse_pattern("C4 --- . C4")
    assert len(steps) == 4
    assert steps[1].note == 0xFF
    assert steps[2].note == 0xFF

def test_parse_off():
    steps = parse_pattern("C4 OFF")
    assert steps[1].note == 0x80

def test_parse_bar_separator():
    steps = parse_pattern("C4 E4 | G4 B4")
    assert len(steps) == 4

def test_parse_velocity():
    steps = parse_pattern("C4@7F E4@40")
    assert steps[0].velocity == 0x7F
    assert steps[1].velocity == 0x40

def test_named_constants():
    from m8py.compose.notation import C4, A4, Fs3
    assert C4 == 60
    assert A4 == 69
    assert Fs3 == 54
