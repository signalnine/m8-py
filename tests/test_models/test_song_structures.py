from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY
from m8py.models.groove import Groove
from m8py.models.chain import Chain, ChainStep
from m8py.models.phrase import Phrase, PhraseStep
from m8py.models.table import Table, TableStep
from m8py.models.song_step import SongStep
from m8py.models.fx import FX

class TestGroove:
    def test_default(self):
        assert all(s == EMPTY for s in Groove().steps)
    def test_size(self):
        w = M8FileWriter(); Groove().write(w); assert len(w.to_bytes()) == 16
    def test_roundtrip(self):
        g = Groove(steps=[6, 6] + [EMPTY] * 14)
        w = M8FileWriter(); g.write(w)
        g2 = Groove.from_reader(M8FileReader(w.to_bytes()))
        assert g2.steps[0] == 6 and g2.steps[2] == EMPTY

class TestChain:
    def test_size(self):
        w = M8FileWriter(); Chain().write(w); assert len(w.to_bytes()) == 32
    def test_roundtrip(self):
        c = Chain(); c.steps[0] = ChainStep(phrase=5, transpose=12)
        w = M8FileWriter(); c.write(w)
        c2 = Chain.from_reader(M8FileReader(w.to_bytes()))
        assert c2.steps[0].phrase == 5 and c2.steps[0].transpose == 12

class TestPhrase:
    def test_size(self):
        w = M8FileWriter(); Phrase().write(w); assert len(w.to_bytes()) == 144
    def test_roundtrip(self):
        ps = PhraseStep(note=60, velocity=100, instrument=3, fx1=FX(0x00, 0x03))
        p = Phrase(); p.steps[0] = ps
        w = M8FileWriter(); p.write(w)
        p2 = Phrase.from_reader(M8FileReader(w.to_bytes()))
        assert p2.steps[0].note == 60 and p2.steps[0].fx1.command == 0x00

class TestTable:
    def test_size(self):
        w = M8FileWriter(); Table().write(w); assert len(w.to_bytes()) == 128

class TestSongStep:
    def test_default(self):
        assert all(t == EMPTY for t in SongStep().tracks)
    def test_size(self):
        w = M8FileWriter(); SongStep().write(w); assert len(w.to_bytes()) == 8
