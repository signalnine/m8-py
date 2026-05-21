from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.fx import FX
from m8py.models.theme import RGB, Theme
from m8py.models.scale import NoteInterval, Scale
from m8py.models.eq import EQBand, EQ
from m8py.models.version import M8Version

V41 = M8Version(4, 1, 0)
V30 = M8Version(3, 0, 0)

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
    def test_size_v4(self):
        w = M8FileWriter(); Scale().write(w, V41); assert len(w.to_bytes()) == 46
    def test_size_v3(self):
        w = M8FileWriter(); Scale().write(w, V30); assert len(w.to_bytes()) == 42
    def test_roundtrip_v4(self):
        s = Scale(name="MAJOR", note_enable=0b101010110101,
                  note_offsets=[NoteInterval(i, i*10) for i in range(12)])
        w = M8FileWriter(); s.write(w, V41)
        s2 = Scale.from_reader(M8FileReader(w.to_bytes()), V41)
        assert s2.name == "MAJOR" and s2.note_enable == 0b101010110101
        assert s2.note_offsets[5].semitone == 5
    def test_roundtrip_v3(self):
        s = Scale(name="MAJOR", note_enable=0b101010110101,
                  note_offsets=[NoteInterval(i, i*10) for i in range(12)])
        w = M8FileWriter(); s.write(w, V30)
        s2 = Scale.from_reader(M8FileReader(w.to_bytes()), V30)
        assert s2.name == "MAJOR" and s2.note_enable == 0b101010110101
        assert s2.tuning == 0.0  # no tuning in v3
    def test_tuning_roundtrip(self):
        s = Scale(name="CUSTOM", tuning=440.0)
        w = M8FileWriter(); s.write(w, V41)
        s2 = Scale.from_reader(M8FileReader(w.to_bytes()), V41)
        assert abs(s2.tuning - 440.0) < 0.01
    def test_tuning_default_zero(self):
        s = Scale()
        assert s.tuning == 0.0
    def test_roundtrip_version_none(self):
        s = Scale(name="CUSTOM", tuning=440.0)
        w = M8FileWriter(); s.write(w)
        s2 = Scale.from_reader(M8FileReader(w.to_bytes()))
        assert s2.name == "CUSTOM"
        assert abs(s2.tuning - 440.0) < 0.01

    def test_name_mutation_after_load_persists(self):
        """m8-py-blk: mutating .name after load must reflect on write."""
        s = Scale(name="ORIG")
        w = M8FileWriter(); s.write(w, V41)
        data1 = w.to_bytes()
        s2 = Scale.from_reader(M8FileReader(data1), V41)
        s2.name = "NEW_NAME"
        w2 = M8FileWriter(); s2.write(w2, V41)
        s3 = Scale.from_reader(M8FileReader(w2.to_bytes()), V41)
        assert s3.name == "NEW_NAME"

    def test_unchanged_name_byte_exact_roundtrip(self):
        """m8-py-blk: writing back without mutation preserves exact bytes."""
        s = Scale(name="MAJOR")
        w = M8FileWriter(); s.write(w, V41)
        data1 = w.to_bytes()
        s2 = Scale.from_reader(M8FileReader(data1), V41)
        # don't mutate
        w2 = M8FileWriter(); s2.write(w2, V41)
        assert w2.to_bytes() == data1

    def test_from_reader_stops_at_high_bit(self):
        """m8-py-l2j: high-bit bytes (>=0x80) terminate name parse like 0x00/0xFF."""
        # 26-byte scale: note_enable(2) + 12 NoteIntervals(24) + name(16) + tuning(4) = 46
        payload = bytearray()
        payload.extend(b"\xff\x0f")  # note_enable
        payload.extend(b"\x00" * 24)  # 12 NoteIntervals (each 2 bytes)
        payload.extend(b"AB\xe9CD" + b"\x00" * 11)  # name: stops at 0xE9 -> "AB"
        payload.extend(b"\x00" * 4)  # tuning
        s = Scale.from_reader(M8FileReader(bytes(payload)), V41)
        assert s.name == "AB"

    def test_from_reader_cursor_advances_full_length_with_high_bit(self):
        """m8-py-l2j: cursor still advances full 16 bytes even when name truncates early."""
        payload = bytearray()
        payload.extend(b"\xff\x0f")
        payload.extend(b"\x00" * 24)
        payload.extend(b"X\xe9" + b"\x00" * 14)
        payload.extend(b"\x00\x00\x80\x3f")  # tuning = 1.0 float32 LE
        s = Scale.from_reader(M8FileReader(bytes(payload)), V41)
        assert s.name == "X"
        assert abs(s.tuning - 1.0) < 0.001

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
