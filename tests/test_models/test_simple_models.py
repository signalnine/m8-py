from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.fx import FX
from m8py.models.theme import RGB, Theme
from m8py.models.scale import NoteInterval, Scale
from m8py.models.eq import EQBand, EQ

class TestFX:
    def test_empty(self):
        fx = FX()
        assert fx.command == 0xFF and fx.value == 0x00
    def test_roundtrip(self):
        w = M8FileWriter()
        FX(command=0x03, value=0x42).write(w)
        fx2 = FX.from_reader(M8FileReader(w.to_bytes()))
        assert fx2.command == 0x03 and fx2.value == 0x42
    def test_size(self):
        w = M8FileWriter(); FX().write(w); assert len(w.to_bytes()) == 2

class TestRGB:
    def test_default(self):
        assert RGB().r == 0
    def test_roundtrip(self):
        w = M8FileWriter(); RGB(255, 128, 0).write(w)
        c = RGB.from_reader(M8FileReader(w.to_bytes()))
        assert c.r == 255 and c.g == 128 and c.b == 0
    def test_size(self):
        w = M8FileWriter(); RGB().write(w); assert len(w.to_bytes()) == 3

class TestTheme:
    def test_size(self):
        w = M8FileWriter(); Theme().write(w); assert len(w.to_bytes()) == 39
    def test_roundtrip(self):
        t = Theme(background=RGB(10, 20, 30), meter_peak=RGB(255, 0, 0))
        w = M8FileWriter(); t.write(w)
        t2 = Theme.from_reader(M8FileReader(w.to_bytes()))
        assert t2.background.r == 10 and t2.meter_peak.r == 255

class TestNoteInterval:
    def test_roundtrip(self):
        w = M8FileWriter(); NoteInterval(7, 50).write(w)
        n = NoteInterval.from_reader(M8FileReader(w.to_bytes()))
        assert n.semitone == 7 and n.cents == 50
    def test_size(self):
        w = M8FileWriter(); NoteInterval().write(w); assert len(w.to_bytes()) == 2

class TestScale:
    def test_size(self):
        w = M8FileWriter(); Scale().write(w); assert len(w.to_bytes()) == 46
    def test_roundtrip(self):
        s = Scale(name="MAJOR", note_enable=0b101010110101,
                  note_offsets=[NoteInterval(i, i*10) for i in range(12)])
        w = M8FileWriter(); s.write(w)
        s2 = Scale.from_reader(M8FileReader(w.to_bytes()))
        assert s2.name == "MAJOR" and s2.note_enable == 0b101010110101
        assert s2.note_offsets[5].semitone == 5
    def test_tuning_roundtrip(self):
        s = Scale(name="CUSTOM", tuning=440.0)
        w = M8FileWriter(); s.write(w)
        s2 = Scale.from_reader(M8FileReader(w.to_bytes()))
        assert abs(s2.tuning - 440.0) < 0.01
    def test_tuning_default_zero(self):
        s = Scale()
        assert s.tuning == 0.0

class TestEQBand:
    def test_size(self):
        w = M8FileWriter(); EQBand().write(w); assert len(w.to_bytes()) == 6
    def test_roundtrip(self):
        w = M8FileWriter(); EQBand(mode_type=0x42, q=50).write(w)
        b = EQBand.from_reader(M8FileReader(w.to_bytes()))
        assert b.mode_type == 0x42 and b.q == 50

class TestEQ:
    def test_size(self):
        w = M8FileWriter(); EQ().write(w); assert len(w.to_bytes()) == 18
    def test_roundtrip(self):
        eq = EQ(low=EQBand(mode_type=1), mid=EQBand(freq=100), high=EQBand(q=80))
        w = M8FileWriter(); eq.write(w)
        eq2 = EQ.from_reader(M8FileReader(w.to_bytes()))
        assert eq2.low.mode_type == 1 and eq2.mid.freq == 100 and eq2.high.q == 80
