import pytest
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.errors import M8ParseError
from m8py.models.modulators import (
    AHDEnv, ADSREnv, DrumEnv, LFOMod, TrigEnv, TrackingEnv,
    mod_from_reader, mod_write, MOD_SIZE, empty_modulator,
)

def _roundtrip(mod):
    w = M8FileWriter()
    mod_write(mod, w)
    data = w.to_bytes()
    assert len(data) == MOD_SIZE, f"expected {MOD_SIZE} bytes, got {len(data)}"
    return mod_from_reader(M8FileReader(data))

def test_ahd_roundtrip():
    m = AHDEnv(dest=1, amount=100, attack=20, hold=30, decay=40)
    m2 = _roundtrip(m)
    assert isinstance(m2, AHDEnv)
    assert m2.dest == 1 and m2.amount == 100 and m2.decay == 40

def test_adsr_roundtrip():
    m = ADSREnv(dest=2, amount=80, attack=10, decay=20, sustain=200, release=30)
    m2 = _roundtrip(m)
    assert isinstance(m2, ADSREnv)
    assert m2.sustain == 200 and m2.release == 30

def test_drum_roundtrip():
    m = DrumEnv(dest=3, amount=50, peak=100, body=150, decay=200)
    m2 = _roundtrip(m)
    assert isinstance(m2, DrumEnv)
    assert m2.peak == 100 and m2.body == 150

def test_lfo_roundtrip():
    m = LFOMod(dest=4, amount=60, shape=1, trigger_mode=2, freq=100, retrigger=5)
    m2 = _roundtrip(m)
    assert isinstance(m2, LFOMod)
    assert m2.shape == 1 and m2.freq == 100

def test_trig_roundtrip():
    m = TrigEnv(dest=5, amount=70, attack=10, hold=20, decay=30, src=2)
    m2 = _roundtrip(m)
    assert isinstance(m2, TrigEnv)
    assert m2.src == 2

def test_tracking_roundtrip():
    m = TrackingEnv(dest=6, amount=90, src=1, lval=0, hval=255)
    m2 = _roundtrip(m)
    assert isinstance(m2, TrackingEnv)
    assert m2.hval == 255

def test_empty_modulator():
    m = empty_modulator()
    assert isinstance(m, AHDEnv)
    w = M8FileWriter()
    mod_write(m, w)
    assert len(w.to_bytes()) == 6

def test_unknown_type_raises():
    data = bytes([0xF0, 0, 0, 0, 0, 0])  # type=15 is unknown
    with pytest.raises(M8ParseError, match="unknown modulator type"):
        mod_from_reader(M8FileReader(data))
