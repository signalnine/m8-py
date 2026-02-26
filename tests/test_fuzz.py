import hypothesis
from hypothesis import given, settings
import hypothesis.strategies as st

from m8py.format.reader import M8FileReader
from m8py.format.constants import HEADER_MAGIC, HEADER_SIZE, INSTRUMENT_SIZE
from m8py.format.errors import M8Error, M8ParseError
from m8py.models.version import M8Version, M8FileType


class TestFuzzInstrumentRead:
    """Random bytes to read_instrument -- must not crash."""

    @given(data=st.binary(min_size=INSTRUMENT_SIZE, max_size=INSTRUMENT_SIZE))
    @settings(max_examples=200)
    def test_random_instrument_bytes_no_crash(self, data):
        """Reading random 215-byte blobs must either parse or raise M8Error."""
        from m8py.models.instrument import read_instrument
        reader = M8FileReader(data)
        version = M8Version(4, 1, 0)
        try:
            inst = read_instrument(reader, version)
            # If it succeeds, reader should be at byte 215
            assert reader.position() == INSTRUMENT_SIZE
        except (M8Error, ValueError, KeyError):
            pass  # Expected for malformed data


class TestFuzzHeader:
    """Random bytes to header parser -- must not crash."""

    @given(data=st.binary(min_size=HEADER_SIZE, max_size=HEADER_SIZE))
    @settings(max_examples=200)
    def test_random_header_no_crash(self, data):
        reader = M8FileReader(data)
        try:
            version, ft = M8FileType.from_reader(reader)
        except (M8Error, ValueError):
            pass


class TestFuzzModels:
    """Random bytes fed to model from_reader -- must not crash."""

    @given(data=st.binary(min_size=144, max_size=144))
    @settings(max_examples=100)
    def test_random_phrase_no_crash(self, data):
        from m8py.models.phrase import Phrase
        reader = M8FileReader(data)
        try:
            Phrase.from_reader(reader)
        except M8Error:
            pass

    @given(data=st.binary(min_size=32, max_size=32))
    @settings(max_examples=100)
    def test_random_chain_no_crash(self, data):
        from m8py.models.chain import Chain
        reader = M8FileReader(data)
        try:
            Chain.from_reader(reader)
        except M8Error:
            pass

    @given(data=st.binary(min_size=39, max_size=39))
    @settings(max_examples=100)
    def test_random_theme_no_crash(self, data):
        from m8py.models.theme import Theme
        reader = M8FileReader(data)
        try:
            Theme.from_reader(reader)
        except M8Error:
            pass
