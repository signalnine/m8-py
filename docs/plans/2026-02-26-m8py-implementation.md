# m8-py Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use conclave:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python library for reading, writing, and composing Dirtywave M8 tracker files with full v4.1 format support.

**Architecture:** Three-layer package (`format/` -> `models/` -> `compose/`) with zero runtime dependencies. Dataclasses with `from_reader()`/`write()` methods. TDD throughout.

**Tech Stack:** Python 3.11+, dataclasses, struct (stdlib). pytest + hypothesis for tests.

**Design doc:** `docs/plans/2026-02-26-m8py-design.md`

**Primary reference:** [m8-files (Rust)](https://github.com/AlexCharlton/m8-files) for byte-level format accuracy.

---

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `m8py/__init__.py`
- Create: `m8py/format/__init__.py`
- Create: `m8py/models/__init__.py`
- Create: `m8py/compose/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/test_format/__init__.py`
- Create: `tests/test_models/__init__.py`
- Create: `tests/test_compose/__init__.py`

**Dependencies:** none

**Step 1: Create pyproject.toml**

```python
# pyproject.toml
[project]
name = "m8py"
version = "0.1.0"
description = "Python library for Dirtywave M8 tracker files"
requires-python = ">=3.11"

[project.optional-dependencies]
dev = ["pytest>=7.0", "hypothesis>=6.0", "ruff"]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
target-version = "py311"
```

**Step 2: Create all `__init__.py` files**

All empty except the top-level:

```python
# m8py/__init__.py
"""m8py - Python library for Dirtywave M8 tracker files."""
```

**Step 3: Verify with a smoke test**

Create `tests/test_smoke.py`:
```python
def test_import():
    import m8py
    assert m8py is not None
```

Run: `python -m pytest tests/test_smoke.py -v`
Expected: PASS

**Step 4: Install dev dependencies and commit**

```bash
pip install -e ".[dev]"
git init && git add -A && git commit -m "feat: project scaffolding"
```

---

## Task 2: Exception Hierarchy

**Files:**
- Create: `m8py/format/errors.py`
- Create: `tests/test_format/test_errors.py`

**Dependencies:** Task 1

**Step 1: Write failing tests**

```python
# tests/test_format/test_errors.py
from m8py.format.errors import (
    M8Error,
    M8ParseError,
    M8VersionError,
    M8ValidationError,
    M8ResourceExhaustedError,
)

def test_hierarchy():
    assert issubclass(M8ParseError, M8Error)
    assert issubclass(M8VersionError, M8Error)
    assert issubclass(M8ValidationError, M8Error)
    assert issubclass(M8ResourceExhaustedError, M8Error)

def test_parse_error_message():
    e = M8ParseError("bad magic at offset 0")
    assert "bad magic" in str(e)

def test_resource_exhausted():
    e = M8ResourceExhaustedError("phrases", 255, 255)
    assert "phrases" in str(e)
    assert "255" in str(e)
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_format/test_errors.py -v`
Expected: FAIL (import errors)

**Step 3: Implement**

```python
# m8py/format/errors.py

class M8Error(Exception):
    """Base exception for all m8py errors."""

class M8ParseError(M8Error):
    """Raised when binary data cannot be parsed."""

class M8VersionError(M8Error):
    """Raised for unsupported or unrecognized version numbers."""

class M8ValidationError(M8Error):
    """Raised when a model violates M8 constraints."""

class M8ResourceExhaustedError(M8Error):
    """Raised when a slot pool is full."""

    def __init__(self, resource: str, used: int, capacity: int):
        self.resource = resource
        self.used = used
        self.capacity = capacity
        super().__init__(
            f"{resource}: {used}/{capacity} slots used, none remaining"
        )
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_format/test_errors.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add m8py/format/errors.py tests/test_format/test_errors.py
git commit -m "feat: exception hierarchy"
```

---

## Task 3: Constants and Enums

**Files:**
- Create: `m8py/format/constants.py`
- Create: `tests/test_format/test_constants.py`

**Dependencies:** Task 1

**Step 1: Write failing tests**

```python
# tests/test_format/test_constants.py
from m8py.format.constants import (
    HEADER_MAGIC,
    HEADER_SIZE,
    EMPTY,
    INSTRUMENT_SIZE,
    FileType,
    InstrumentKind,
    NOTE_OFF_THRESHOLD,
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
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_format/test_constants.py -v`
Expected: FAIL

**Step 3: Implement**

```python
# m8py/format/constants.py
from enum import IntEnum

# File header
HEADER_MAGIC = b"M8VERSION\x00"
HEADER_SIZE = 14

# Universal empty sentinel
EMPTY = 0xFF

# Fixed sizes
INSTRUMENT_SIZE = 215

# Note encoding
NOTE_OFF_THRESHOLD = 0x80  # >= 0x80 means note off

# Song structure counts
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
    TRI = 0
    SIN = 1
    RAMP_DOWN = 2
    RAMP_UP = 3
    EXP_DN = 4
    EXP_UP = 5
    SQR_DN = 6
    SQR_UP = 7
    RANDOM = 8
    DRUNK = 9
    TRI_T = 10
    SIN_T = 11
    RAMPD_T = 12
    RAMPU_T = 13
    EXPD_T = 14
    EXPU_T = 15
    SQ_D_T = 16
    SQ_U_T = 17
    RAND_T = 18
    DRNK_T = 19


class LfoTriggerMode(IntEnum):
    FREE = 0
    RETRIG = 1
    HOLD = 2
    ONCE = 3


class SamplePlayMode(IntEnum):
    FWD = 0
    REV = 1
    FWDLOOP = 2
    REVLOOP = 3
    FWD_PP = 4
    REV_PP = 5
    OSC = 6
    OSC_REV = 7
    OSC_PP = 8


class LimitType(IntEnum):
    CLIP = 0
    SIN = 1
    FOLD = 2
    WRAP = 3
    POST = 4
    POSTAD = 5
    POST_W1 = 6
    POST_W2 = 7
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_format/test_constants.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add m8py/format/constants.py tests/test_format/test_constants.py
git commit -m "feat: constants and enums"
```

---

## Task 4: M8FileReader

**Files:**
- Create: `m8py/format/reader.py`
- Create: `tests/test_format/test_reader.py`

**Dependencies:** Task 2

**Step 1: Write failing tests**

```python
# tests/test_format/test_reader.py
import struct
import pytest
from m8py.format.reader import M8FileReader
from m8py.format.errors import M8ParseError


def test_read_byte():
    r = M8FileReader(bytes([0x42, 0xFF]))
    assert r.read() == 0x42
    assert r.read() == 0xFF


def test_read_bytes():
    r = M8FileReader(b"\x01\x02\x03\x04")
    assert r.read_bytes(2) == b"\x01\x02"
    assert r.read_bytes(2) == b"\x03\x04"


def test_read_past_end_raises():
    r = M8FileReader(b"\x01")
    r.read()
    with pytest.raises(M8ParseError, match="EOF"):
        r.read()


def test_read_bytes_past_end_raises():
    r = M8FileReader(b"\x01\x02")
    with pytest.raises(M8ParseError):
        r.read_bytes(5)


def test_read_str_null_terminated():
    r = M8FileReader(b"HELLO\x00\x00\x00\x00\x00\x00\x00")
    assert r.read_str(12) == "HELLO"
    assert r.position() == 12  # always consumes full length


def test_read_str_ff_terminated():
    r = M8FileReader(b"AB\xFF\xFF\xFF\xFF")
    assert r.read_str(6) == "AB"
    assert r.position() == 6


def test_read_str_empty_ff_fill():
    r = M8FileReader(bytes([0xFF] * 12))
    assert r.read_str(12) == ""


def test_read_float_le():
    data = struct.pack("<f", 120.0)
    r = M8FileReader(data)
    assert r.read_float_le() == pytest.approx(120.0)


def test_read_bool():
    r = M8FileReader(b"\x01\x00")
    assert r.read_bool() is True
    assert r.read_bool() is False


def test_read_u16_le():
    r = M8FileReader(b"\x34\x12")
    assert r.read_u16_le() == 0x1234


def test_position_and_seek():
    r = M8FileReader(b"\x00\x01\x02\x03\x04")
    assert r.position() == 0
    r.seek(3)
    assert r.position() == 3
    assert r.read() == 0x03


def test_seek_out_of_bounds():
    r = M8FileReader(b"\x00\x01")
    with pytest.raises(M8ParseError):
        r.seek(100)


def test_skip():
    r = M8FileReader(b"\x00\x01\x02\x03")
    r.skip(2)
    assert r.read() == 0x02


def test_remaining():
    r = M8FileReader(b"\x00\x01\x02")
    assert r.remaining() == 3
    r.read()
    assert r.remaining() == 2


def test_expect_consumed_pass():
    r = M8FileReader(bytes(215))
    start = r.position()
    r.skip(215)
    r.expect_consumed(215, start)  # should not raise


def test_expect_consumed_fail():
    r = M8FileReader(bytes(215))
    start = r.position()
    r.skip(200)
    with pytest.raises(M8ParseError, match="expected 215.*got 200"):
        r.expect_consumed(215, start)
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_format/test_reader.py -v`
Expected: FAIL

**Step 3: Implement**

```python
# m8py/format/reader.py
import struct
from m8py.format.errors import M8ParseError


class M8FileReader:
    """Cursor-based sequential byte reader for M8 binary files."""

    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0

    def read(self) -> int:
        if self._pos >= len(self._data):
            raise M8ParseError(f"EOF: attempted read at offset {self._pos}")
        val = self._data[self._pos]
        self._pos += 1
        return val

    def read_bytes(self, n: int) -> bytes:
        if self._pos + n > len(self._data):
            raise M8ParseError(
                f"EOF: need {n} bytes at offset {self._pos}, "
                f"only {len(self._data) - self._pos} remaining"
            )
        val = self._data[self._pos : self._pos + n]
        self._pos += n
        return val

    def read_str(self, n: int) -> str:
        raw = self.read_bytes(n)
        result = []
        for b in raw:
            if b == 0x00 or b == 0xFF:
                break
            result.append(chr(b))
        return "".join(result)

    def read_float_le(self) -> float:
        data = self.read_bytes(4)
        return struct.unpack("<f", data)[0]

    def read_bool(self) -> bool:
        return self.read() != 0

    def read_u16_le(self) -> int:
        data = self.read_bytes(2)
        return struct.unpack("<H", data)[0]

    def position(self) -> int:
        return self._pos

    def seek(self, offset: int) -> None:
        if offset < 0 or offset > len(self._data):
            raise M8ParseError(
                f"seek to {offset} out of bounds (size={len(self._data)})"
            )
        self._pos = offset

    def skip(self, n: int) -> None:
        self._pos += n

    def remaining(self) -> int:
        return max(0, len(self._data) - self._pos)

    def expect_consumed(self, n: int, start: int) -> None:
        actual = self._pos - start
        if actual != n:
            raise M8ParseError(
                f"expected {n} bytes consumed from offset {start}, got {actual}"
            )
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_format/test_reader.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add m8py/format/reader.py tests/test_format/test_reader.py
git commit -m "feat: M8FileReader with bounds checking"
```

---

## Task 5: M8FileWriter

**Files:**
- Create: `m8py/format/writer.py`
- Create: `tests/test_format/test_writer.py`

**Dependencies:** Task 2

**Step 1: Write failing tests**

```python
# tests/test_format/test_writer.py
import struct
import pytest
from m8py.format.writer import M8FileWriter
from m8py.format.errors import M8ParseError


def test_write_byte():
    w = M8FileWriter()
    w.write(0x42)
    w.write(0xFF)
    assert w.to_bytes() == bytes([0x42, 0xFF])


def test_write_bytes():
    w = M8FileWriter()
    w.write_bytes(b"\x01\x02\x03")
    assert w.to_bytes() == b"\x01\x02\x03"


def test_write_str_padded():
    w = M8FileWriter()
    w.write_str("HELLO", 12)
    data = w.to_bytes()
    assert len(data) == 12
    assert data[:5] == b"HELLO"
    assert data[5:] == b"\x00" * 7


def test_write_str_truncation():
    w = M8FileWriter()
    w.write_str("A" * 20, 12)
    data = w.to_bytes()
    assert len(data) == 12
    assert data == b"AAAAAAAAAAA\x00"  # 11 chars + null terminator


def test_write_str_empty():
    w = M8FileWriter()
    w.write_str("", 12)
    assert w.to_bytes() == b"\x00" * 12


def test_write_float_le():
    w = M8FileWriter()
    w.write_float_le(120.0)
    assert w.to_bytes() == struct.pack("<f", 120.0)


def test_write_bool():
    w = M8FileWriter()
    w.write_bool(True)
    w.write_bool(False)
    assert w.to_bytes() == b"\x01\x00"


def test_write_u16_le():
    w = M8FileWriter()
    w.write_u16_le(0x1234)
    assert w.to_bytes() == b"\x34\x12"


def test_pad():
    w = M8FileWriter()
    w.pad(5, 0xFF)
    assert w.to_bytes() == bytes([0xFF] * 5)


def test_pad_default_zero():
    w = M8FileWriter()
    w.pad(3)
    assert w.to_bytes() == b"\x00\x00\x00"


def test_position():
    w = M8FileWriter()
    assert w.position() == 0
    w.write(0x42)
    assert w.position() == 1
    w.write_bytes(b"\x01\x02\x03")
    assert w.position() == 4


def test_expect_written_pass():
    w = M8FileWriter()
    start = w.position()
    w.pad(215)
    w.expect_written(215, start)


def test_expect_written_fail():
    w = M8FileWriter()
    start = w.position()
    w.pad(200)
    with pytest.raises(M8ParseError, match="expected 215.*got 200"):
        w.expect_written(215, start)
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_format/test_writer.py -v`
Expected: FAIL

**Step 3: Implement**

```python
# m8py/format/writer.py
import struct
from m8py.format.errors import M8ParseError


class M8FileWriter:
    """Sequential byte writer for M8 binary files."""

    def __init__(self) -> None:
        self._buf = bytearray()

    def write(self, byte: int) -> None:
        self._buf.append(byte & 0xFF)

    def write_bytes(self, data: bytes) -> None:
        self._buf.extend(data)

    def write_str(self, s: str, length: int) -> None:
        encoded = s.encode("ascii")[:length - 1]
        self._buf.extend(encoded)
        self._buf.extend(b"\x00" * (length - len(encoded)))

    def write_float_le(self, value: float) -> None:
        self._buf.extend(struct.pack("<f", value))

    def write_bool(self, value: bool) -> None:
        self._buf.append(1 if value else 0)

    def write_u16_le(self, value: int) -> None:
        self._buf.extend(struct.pack("<H", value))

    def pad(self, n: int, value: int = 0x00) -> None:
        self._buf.extend(bytes([value]) * n)

    def position(self) -> int:
        return len(self._buf)

    def to_bytes(self) -> bytes:
        return bytes(self._buf)

    def expect_written(self, n: int, start: int) -> None:
        actual = len(self._buf) - start
        if actual != n:
            raise M8ParseError(
                f"expected {n} bytes written from offset {start}, got {actual}"
            )
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_format/test_writer.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add m8py/format/writer.py tests/test_format/test_writer.py
git commit -m "feat: M8FileWriter with size tracking"
```

---

## Task 6: M8Version and VersionCapabilities

**Files:**
- Create: `m8py/models/version.py`
- Create: `tests/test_models/test_version.py`

**Dependencies:** Task 4, Task 5

**Step 1: Write failing tests**

```python
# tests/test_models/test_version.py
import pytest
from m8py.models.version import M8Version, VersionCapabilities, M8FileType
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import HEADER_MAGIC, FileType


def test_version_from_reader():
    # Build a v4.1.0 song header
    # LSB = (minor << 4) | patch = (1 << 4) | 0 = 0x10
    # MSB = (file_type << 4) | major = (0x00 << 4) | 4 = 0x04
    data = HEADER_MAGIC + bytes([0x10, 0x04, 0x00, 0x00])
    r = M8FileReader(data)
    version, file_type = M8FileType.from_reader(r)
    assert version.major == 4
    assert version.minor == 1
    assert version.patch == 0
    assert file_type == FileType.SONG


def test_version_2_7_8_instrument():
    # v2.7.8, instrument file
    # LSB = (7 << 4) | 8 = 0x78
    # MSB = (0x01 << 4) | 2 = 0x12
    data = HEADER_MAGIC + bytes([0x78, 0x12, 0x00, 0x00])
    r = M8FileReader(data)
    version, file_type = M8FileType.from_reader(r)
    assert version.major == 2
    assert version.minor == 7
    assert version.patch == 8
    assert file_type == FileType.INSTRUMENT


def test_version_write():
    w = M8FileWriter()
    version = M8Version(4, 1, 0)
    M8FileType.write_header(w, version, FileType.SONG)
    data = w.to_bytes()
    assert len(data) == 14
    assert data[:10] == HEADER_MAGIC
    # Read it back
    r = M8FileReader(data)
    v, ft = M8FileType.from_reader(r)
    assert v.major == 4 and v.minor == 1 and v.patch == 0
    assert ft == FileType.SONG


def test_version_at_least():
    v = M8Version(3, 2, 0)
    assert v.at_least(3, 0)
    assert v.at_least(3, 2)
    assert not v.at_least(3, 3)
    assert not v.at_least(4, 0)
    assert v.at_least(2, 5)


def test_caps_v1():
    v = M8Version(1, 0, 0)
    c = v.caps
    assert not c.has_scales
    assert not c.has_new_modulators
    assert not c.has_hypersynth
    assert not c.has_eq


def test_caps_v25():
    v = M8Version(2, 5, 0)
    c = v.caps
    assert c.has_scales
    assert not c.has_new_modulators
    assert not c.has_hypersynth
    assert not c.has_eq


def test_caps_v3():
    v = M8Version(3, 0, 0)
    c = v.caps
    assert c.has_scales
    assert c.has_new_modulators
    assert c.has_hypersynth
    assert c.has_external
    assert not c.has_eq


def test_caps_v4():
    v = M8Version(4, 0, 0)
    c = v.caps
    assert c.has_eq
    assert not c.has_expanded_eq


def test_caps_v41():
    v = M8Version(4, 1, 0)
    c = v.caps
    assert c.has_eq
    assert c.has_expanded_eq
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_models/test_version.py -v`
Expected: FAIL

**Step 3: Implement**

```python
# m8py/models/version.py
from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import HEADER_MAGIC, FileType
from m8py.format.errors import M8ParseError


@dataclass
class M8Version:
    major: int
    minor: int
    patch: int

    def at_least(self, major: int, minor: int) -> bool:
        return self.major > major or (self.major == major and self.minor >= minor)

    @property
    def caps(self) -> VersionCapabilities:
        return VersionCapabilities.from_version(self)


@dataclass(frozen=True)
class VersionCapabilities:
    has_scales: bool
    has_new_modulators: bool
    has_hypersynth: bool
    has_external: bool
    has_eq: bool
    has_expanded_eq: bool

    @staticmethod
    def from_version(v: M8Version) -> VersionCapabilities:
        return VersionCapabilities(
            has_scales=v.at_least(2, 5),
            has_new_modulators=v.at_least(3, 0),
            has_hypersynth=v.at_least(3, 0),
            has_external=v.at_least(3, 0),
            has_eq=v.at_least(4, 0),
            has_expanded_eq=v.at_least(4, 1),
        )


class M8FileType:
    """Handles reading/writing the 14-byte M8 file header."""

    @staticmethod
    def from_reader(reader: M8FileReader) -> tuple[M8Version, FileType]:
        magic = reader.read_bytes(10)
        if magic != HEADER_MAGIC:
            raise M8ParseError(f"bad magic: expected {HEADER_MAGIC!r}, got {magic!r}")
        lsb = reader.read()
        msb = reader.read()
        major = msb & 0x0F
        minor = (lsb >> 4) & 0x0F
        patch = lsb & 0x0F
        file_type_nibble = (msb >> 4) & 0x0F
        reader.skip(2)  # padding
        try:
            file_type = FileType(file_type_nibble)
        except ValueError:
            raise M8ParseError(f"unknown file type nibble: 0x{file_type_nibble:X}")
        return M8Version(major, minor, patch), file_type

    @staticmethod
    def write_header(writer: M8FileWriter, version: M8Version, file_type: FileType) -> None:
        writer.write_bytes(HEADER_MAGIC)
        lsb = (version.minor << 4) | version.patch
        msb = (file_type.value << 4) | version.major
        writer.write(lsb)
        writer.write(msb)
        writer.pad(2)  # padding
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_models/test_version.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add m8py/models/version.py tests/test_models/test_version.py
git commit -m "feat: M8Version, VersionCapabilities, header parsing"
```

---

## Task 7: Song Offsets

**Files:**
- Create: `m8py/format/offsets.py`
- Create: `tests/test_format/test_offsets.py`

**Dependencies:** Task 6

**Step 1: Write failing tests**

```python
# tests/test_format/test_offsets.py
from m8py.format.offsets import SongOffsets, offsets_for_version, V4_OFFSETS, V4_1_OFFSETS
from m8py.models.version import M8Version


def test_v4_offsets():
    assert V4_OFFSETS.groove == 0xEE
    assert V4_OFFSETS.song == 0x2EE
    assert V4_OFFSETS.phrases == 0xAEE
    assert V4_OFFSETS.chains == 0x9A5E
    assert V4_OFFSETS.table == 0xBA3E
    assert V4_OFFSETS.instruments == 0x13A3E
    assert V4_OFFSETS.effect_settings == 0x1A5C1
    assert V4_OFFSETS.midi_mapping == 0x1A5FE
    assert V4_OFFSETS.scale == 0x1AA7E
    assert V4_OFFSETS.eq == 0x1AD5E
    assert V4_OFFSETS.instrument_eq_count == 32


def test_v41_offsets():
    assert V4_1_OFFSETS.instrument_eq_count == 128
    assert V4_1_OFFSETS.instrument_file_eq_offset == 0x165


def test_offsets_for_v41():
    v = M8Version(4, 1, 0)
    o = offsets_for_version(v)
    assert o.instrument_eq_count == 128


def test_offsets_for_v4():
    v = M8Version(4, 0, 0)
    o = offsets_for_version(v)
    assert o.instrument_eq_count == 32


def test_offsets_for_v3():
    v = M8Version(3, 0, 0)
    o = offsets_for_version(v)
    assert o.scale is not None
    assert o.eq is None
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_format/test_offsets.py -v`
Expected: FAIL

**Step 3: Implement**

```python
# m8py/format/offsets.py
from __future__ import annotations
from dataclasses import dataclass
from m8py.models.version import M8Version


@dataclass(frozen=True)
class SongOffsets:
    groove: int
    song: int
    phrases: int
    chains: int
    table: int
    instruments: int
    effect_settings: int
    midi_mapping: int
    scale: int | None
    eq: int | None
    instrument_eq_count: int
    instrument_file_eq_offset: int | None


# Pre-v2.5: no scales, no EQ
V2_OFFSETS = SongOffsets(
    groove=0xEE, song=0x2EE, phrases=0xAEE,
    chains=0x9A5E, table=0xBA3E, instruments=0x13A3E,
    effect_settings=0x1A5C1, midi_mapping=0x1A5FE,
    scale=None, eq=None,
    instrument_eq_count=0, instrument_file_eq_offset=None,
)

# v2.5+: scales added
V25_OFFSETS = SongOffsets(
    groove=0xEE, song=0x2EE, phrases=0xAEE,
    chains=0x9A5E, table=0xBA3E, instruments=0x13A3E,
    effect_settings=0x1A5C1, midi_mapping=0x1A5FE,
    scale=0x1AA7E, eq=None,
    instrument_eq_count=0, instrument_file_eq_offset=None,
)

# v3: same layout as v2.5 (new modulators/instruments are within instrument slots)
V3_OFFSETS = V25_OFFSETS

# v4.0: EQ added (32 instrument EQs)
V4_OFFSETS = SongOffsets(
    groove=0xEE, song=0x2EE, phrases=0xAEE,
    chains=0x9A5E, table=0xBA3E, instruments=0x13A3E,
    effect_settings=0x1A5C1, midi_mapping=0x1A5FE,
    scale=0x1AA7E, eq=0x1AD5E,
    instrument_eq_count=32, instrument_file_eq_offset=None,
)

# v4.1: expanded EQ (128 instrument EQs)
V4_1_OFFSETS = SongOffsets(
    groove=0xEE, song=0x2EE, phrases=0xAEE,
    chains=0x9A5E, table=0xBA3E, instruments=0x13A3E,
    effect_settings=0x1A5C1, midi_mapping=0x1A5FE,
    scale=0x1AA7E, eq=0x1AD5E,
    instrument_eq_count=128, instrument_file_eq_offset=0x165,
)


def offsets_for_version(version: M8Version) -> SongOffsets:
    if version.at_least(4, 1):
        return V4_1_OFFSETS
    if version.at_least(4, 0):
        return V4_OFFSETS
    if version.at_least(2, 5):
        return V25_OFFSETS
    return V2_OFFSETS
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_format/test_offsets.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add m8py/format/offsets.py tests/test_format/test_offsets.py
git commit -m "feat: version-specific song offset tables"
```

---

## Task 8: Simple Models (FX, RGB, NoteInterval, EQBand, EQ)

**Files:**
- Create: `m8py/models/fx.py`
- Create: `m8py/models/theme.py` (RGB only for now)
- Create: `m8py/models/scale.py` (NoteInterval only for now)
- Create: `m8py/models/eq.py`
- Create: `tests/test_models/test_simple_models.py`

**Dependencies:** Task 4, Task 5

**Step 1: Write failing tests**

```python
# tests/test_models/test_simple_models.py
import pytest
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.fx import FX
from m8py.models.theme import RGB
from m8py.models.scale import NoteInterval
from m8py.models.eq import EQBand, EQ


class TestFX:
    def test_empty(self):
        fx = FX()
        assert fx.command == 0xFF
        assert fx.value == 0x00

    def test_roundtrip(self):
        fx = FX(command=0x03, value=0x42)
        w = M8FileWriter()
        fx.write(w)
        r = M8FileReader(w.to_bytes())
        fx2 = FX.from_reader(r)
        assert fx2.command == 0x03
        assert fx2.value == 0x42

    def test_size(self):
        w = M8FileWriter()
        FX().write(w)
        assert len(w.to_bytes()) == 2


class TestRGB:
    def test_default(self):
        c = RGB()
        assert c.r == 0 and c.g == 0 and c.b == 0

    def test_roundtrip(self):
        c = RGB(r=255, g=128, b=0)
        w = M8FileWriter()
        c.write(w)
        r = M8FileReader(w.to_bytes())
        c2 = RGB.from_reader(r)
        assert c2.r == 255 and c2.g == 128 and c2.b == 0

    def test_size(self):
        w = M8FileWriter()
        RGB().write(w)
        assert len(w.to_bytes()) == 3


class TestNoteInterval:
    def test_default(self):
        n = NoteInterval()
        assert n.semitone == 0 and n.cents == 0

    def test_roundtrip(self):
        n = NoteInterval(semitone=7, cents=50)
        w = M8FileWriter()
        n.write(w)
        r = M8FileReader(w.to_bytes())
        n2 = NoteInterval.from_reader(r)
        assert n2.semitone == 7 and n2.cents == 50

    def test_size(self):
        w = M8FileWriter()
        NoteInterval().write(w)
        assert len(w.to_bytes()) == 2


class TestEQBand:
    def test_default(self):
        b = EQBand()
        assert b.mode_type == 0

    def test_roundtrip(self):
        b = EQBand(mode_type=0x42, freq_fine=10, freq=20, level_fine=30, level=40, q=50)
        w = M8FileWriter()
        b.write(w)
        r = M8FileReader(w.to_bytes())
        b2 = EQBand.from_reader(r)
        assert b2.mode_type == 0x42
        assert b2.freq == 20
        assert b2.q == 50

    def test_size(self):
        w = M8FileWriter()
        EQBand().write(w)
        assert len(w.to_bytes()) == 6


class TestEQ:
    def test_size(self):
        w = M8FileWriter()
        EQ().write(w)
        assert len(w.to_bytes()) == 18  # 3 bands x 6 bytes

    def test_roundtrip(self):
        eq = EQ(
            low=EQBand(mode_type=1),
            mid=EQBand(freq=100),
            high=EQBand(q=80),
        )
        w = M8FileWriter()
        eq.write(w)
        r = M8FileReader(w.to_bytes())
        eq2 = EQ.from_reader(r)
        assert eq2.low.mode_type == 1
        assert eq2.mid.freq == 100
        assert eq2.high.q == 80
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_models/test_simple_models.py -v`
Expected: FAIL

**Step 3: Implement all four files**

```python
# m8py/models/fx.py
from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY


@dataclass
class FX:
    command: int = EMPTY
    value: int = 0x00

    @staticmethod
    def from_reader(reader: M8FileReader) -> FX:
        return FX(command=reader.read(), value=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.command)
        writer.write(self.value)
```

```python
# m8py/models/theme.py
from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter


@dataclass
class RGB:
    r: int = 0
    g: int = 0
    b: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> RGB:
        return RGB(r=reader.read(), g=reader.read(), b=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.r)
        writer.write(self.g)
        writer.write(self.b)
```

```python
# m8py/models/scale.py
from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter


@dataclass
class NoteInterval:
    semitone: int = 0
    cents: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> NoteInterval:
        return NoteInterval(semitone=reader.read(), cents=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.semitone)
        writer.write(self.cents)
```

```python
# m8py/models/eq.py
from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter


@dataclass
class EQBand:
    mode_type: int = 0
    freq_fine: int = 0
    freq: int = 0
    level_fine: int = 0
    level: int = 0
    q: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> EQBand:
        return EQBand(
            mode_type=reader.read(), freq_fine=reader.read(), freq=reader.read(),
            level_fine=reader.read(), level=reader.read(), q=reader.read(),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.mode_type)
        writer.write(self.freq_fine)
        writer.write(self.freq)
        writer.write(self.level_fine)
        writer.write(self.level)
        writer.write(self.q)


@dataclass
class EQ:
    low: EQBand = field(default_factory=EQBand)
    mid: EQBand = field(default_factory=EQBand)
    high: EQBand = field(default_factory=EQBand)

    @staticmethod
    def from_reader(reader: M8FileReader) -> EQ:
        return EQ(
            low=EQBand.from_reader(reader),
            mid=EQBand.from_reader(reader),
            high=EQBand.from_reader(reader),
        )

    def write(self, writer: M8FileWriter) -> None:
        self.low.write(writer)
        self.mid.write(writer)
        self.high.write(writer)
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_models/test_simple_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add m8py/models/fx.py m8py/models/theme.py m8py/models/scale.py m8py/models/eq.py tests/test_models/test_simple_models.py
git commit -m "feat: simple models (FX, RGB, NoteInterval, EQBand, EQ)"
```

---

## Task 9: Song Structure Models (Groove, SongStep, Chain, Phrase, Table)

**Files:**
- Create: `m8py/models/groove.py`
- Create: `m8py/models/chain.py`
- Create: `m8py/models/phrase.py`
- Create: `m8py/models/table.py`
- Create: `m8py/models/song_step.py`
- Create: `tests/test_models/test_song_structures.py`

**Dependencies:** Task 8

**Step 1: Write failing tests**

```python
# tests/test_models/test_song_structures.py
import pytest
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
        g = Groove()
        assert len(g.steps) == 16
        assert all(s == EMPTY for s in g.steps)

    def test_size(self):
        w = M8FileWriter()
        Groove().write(w)
        assert len(w.to_bytes()) == 16

    def test_roundtrip(self):
        g = Groove(steps=[6, 6] + [EMPTY] * 14)
        w = M8FileWriter()
        g.write(w)
        r = M8FileReader(w.to_bytes())
        g2 = Groove.from_reader(r)
        assert g2.steps[0] == 6
        assert g2.steps[2] == EMPTY


class TestChainStep:
    def test_empty(self):
        cs = ChainStep()
        assert cs.phrase == EMPTY
        assert cs.transpose == 0

    def test_size(self):
        w = M8FileWriter()
        ChainStep().write(w)
        assert len(w.to_bytes()) == 2


class TestChain:
    def test_step_count(self):
        c = Chain()
        assert len(c.steps) == 16

    def test_size(self):
        w = M8FileWriter()
        Chain().write(w)
        assert len(w.to_bytes()) == 32  # 16 x 2


class TestPhraseStep:
    def test_empty(self):
        ps = PhraseStep()
        assert ps.note == EMPTY
        assert ps.velocity == EMPTY
        assert ps.instrument == EMPTY

    def test_size(self):
        w = M8FileWriter()
        PhraseStep().write(w)
        assert len(w.to_bytes()) == 9  # 3 + 3*2


class TestPhrase:
    def test_step_count(self):
        p = Phrase()
        assert len(p.steps) == 16

    def test_size(self):
        w = M8FileWriter()
        Phrase().write(w)
        assert len(w.to_bytes()) == 144  # 16 x 9


class TestTableStep:
    def test_empty(self):
        ts = TableStep()
        assert ts.transpose == 0
        assert ts.velocity == EMPTY

    def test_size(self):
        w = M8FileWriter()
        TableStep().write(w)
        assert len(w.to_bytes()) == 8  # 2 + 3*2


class TestTable:
    def test_size(self):
        w = M8FileWriter()
        Table().write(w)
        assert len(w.to_bytes()) == 128  # 16 x 8


class TestSongStep:
    def test_default(self):
        ss = SongStep()
        assert len(ss.tracks) == 8
        assert all(t == EMPTY for t in ss.tracks)

    def test_size(self):
        w = M8FileWriter()
        SongStep().write(w)
        assert len(w.to_bytes()) == 8


class TestRoundtrips:
    def test_phrase_step_roundtrip(self):
        ps = PhraseStep(note=60, velocity=100, instrument=3,
                        fx1=FX(0x00, 0x03), fx2=FX(0x17, 0x80))
        w = M8FileWriter()
        ps.write(w)
        r = M8FileReader(w.to_bytes())
        ps2 = PhraseStep.from_reader(r)
        assert ps2.note == 60
        assert ps2.fx1.command == 0x00
        assert ps2.fx2.value == 0x80

    def test_chain_roundtrip(self):
        c = Chain()
        c.steps[0] = ChainStep(phrase=5, transpose=12)
        w = M8FileWriter()
        c.write(w)
        r = M8FileReader(w.to_bytes())
        c2 = Chain.from_reader(r)
        assert c2.steps[0].phrase == 5
        assert c2.steps[0].transpose == 12
        assert c2.steps[1].phrase == EMPTY
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_models/test_song_structures.py -v`
Expected: FAIL

**Step 3: Implement all five files**

```python
# m8py/models/groove.py
from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY


@dataclass
class Groove:
    steps: list[int] = field(default_factory=lambda: [EMPTY] * 16)

    @staticmethod
    def from_reader(reader: M8FileReader) -> Groove:
        return Groove(steps=[reader.read() for _ in range(16)])

    def write(self, writer: M8FileWriter) -> None:
        for s in self.steps:
            writer.write(s)
```

```python
# m8py/models/chain.py
from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY


@dataclass
class ChainStep:
    phrase: int = EMPTY
    transpose: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> ChainStep:
        return ChainStep(phrase=reader.read(), transpose=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.phrase)
        writer.write(self.transpose)


@dataclass
class Chain:
    steps: list[ChainStep] = field(
        default_factory=lambda: [ChainStep() for _ in range(16)]
    )

    @staticmethod
    def from_reader(reader: M8FileReader) -> Chain:
        return Chain(steps=[ChainStep.from_reader(reader) for _ in range(16)])

    def write(self, writer: M8FileWriter) -> None:
        for s in self.steps:
            s.write(writer)
```

```python
# m8py/models/phrase.py
from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY
from m8py.models.fx import FX


@dataclass
class PhraseStep:
    note: int = EMPTY
    velocity: int = EMPTY
    instrument: int = EMPTY
    fx1: FX = field(default_factory=FX)
    fx2: FX = field(default_factory=FX)
    fx3: FX = field(default_factory=FX)

    @staticmethod
    def from_reader(reader: M8FileReader) -> PhraseStep:
        return PhraseStep(
            note=reader.read(),
            velocity=reader.read(),
            instrument=reader.read(),
            fx1=FX.from_reader(reader),
            fx2=FX.from_reader(reader),
            fx3=FX.from_reader(reader),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.note)
        writer.write(self.velocity)
        writer.write(self.instrument)
        self.fx1.write(writer)
        self.fx2.write(writer)
        self.fx3.write(writer)


@dataclass
class Phrase:
    steps: list[PhraseStep] = field(
        default_factory=lambda: [PhraseStep() for _ in range(16)]
    )

    @staticmethod
    def from_reader(reader: M8FileReader) -> Phrase:
        return Phrase(steps=[PhraseStep.from_reader(reader) for _ in range(16)])

    def write(self, writer: M8FileWriter) -> None:
        for s in self.steps:
            s.write(writer)
```

```python
# m8py/models/table.py
from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY
from m8py.models.fx import FX


@dataclass
class TableStep:
    transpose: int = 0
    velocity: int = EMPTY
    fx1: FX = field(default_factory=FX)
    fx2: FX = field(default_factory=FX)
    fx3: FX = field(default_factory=FX)

    @staticmethod
    def from_reader(reader: M8FileReader) -> TableStep:
        return TableStep(
            transpose=reader.read(),
            velocity=reader.read(),
            fx1=FX.from_reader(reader),
            fx2=FX.from_reader(reader),
            fx3=FX.from_reader(reader),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.transpose)
        writer.write(self.velocity)
        self.fx1.write(writer)
        self.fx2.write(writer)
        self.fx3.write(writer)


@dataclass
class Table:
    steps: list[TableStep] = field(
        default_factory=lambda: [TableStep() for _ in range(16)]
    )

    @staticmethod
    def from_reader(reader: M8FileReader) -> Table:
        return Table(steps=[TableStep.from_reader(reader) for _ in range(16)])

    def write(self, writer: M8FileWriter) -> None:
        for s in self.steps:
            s.write(writer)
```

```python
# m8py/models/song_step.py
from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.constants import EMPTY


@dataclass
class SongStep:
    tracks: list[int] = field(default_factory=lambda: [EMPTY] * 8)

    @staticmethod
    def from_reader(reader: M8FileReader) -> SongStep:
        return SongStep(tracks=[reader.read() for _ in range(8)])

    def write(self, writer: M8FileWriter) -> None:
        for t in self.tracks:
            writer.write(t)
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_models/test_song_structures.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add m8py/models/groove.py m8py/models/chain.py m8py/models/phrase.py m8py/models/table.py m8py/models/song_step.py tests/test_models/test_song_structures.py
git commit -m "feat: song structure models (Groove, Chain, Phrase, Table, SongStep)"
```

---

## Task 10: Scale and Theme (Full File Types)

**Files:**
- Modify: `m8py/models/scale.py`
- Modify: `m8py/models/theme.py`
- Create: `tests/test_models/test_scale_theme.py`

**Dependencies:** Task 8, Task 6

**Step 1: Write failing tests**

```python
# tests/test_models/test_scale_theme.py
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.scale import Scale, NoteInterval
from m8py.models.theme import Theme, RGB


class TestScale:
    def test_default(self):
        s = Scale()
        assert s.name == ""
        assert s.note_enable == 0xFFF
        assert len(s.note_offsets) == 12

    def test_size(self):
        w = M8FileWriter()
        Scale().write(w)
        # 2 (bitmap) + 12*2 (intervals) + 16 (name) = 42
        assert len(w.to_bytes()) == 42

    def test_roundtrip(self):
        s = Scale(
            name="MAJOR",
            note_enable=0b101010110101,
            note_offsets=[NoteInterval(i, i * 10) for i in range(12)],
        )
        w = M8FileWriter()
        s.write(w)
        r = M8FileReader(w.to_bytes())
        s2 = Scale.from_reader(r)
        assert s2.name == "MAJOR"
        assert s2.note_enable == 0b101010110101
        assert s2.note_offsets[5].semitone == 5
        assert s2.note_offsets[5].cents == 50


class TestTheme:
    def test_color_count(self):
        t = Theme()
        # 13 color fields
        w = M8FileWriter()
        t.write(w)
        assert len(w.to_bytes()) == 39  # 13 x 3

    def test_roundtrip(self):
        t = Theme(background=RGB(10, 20, 30), meter_peak=RGB(255, 0, 0))
        w = M8FileWriter()
        t.write(w)
        r = M8FileReader(w.to_bytes())
        t2 = Theme.from_reader(r)
        assert t2.background.r == 10
        assert t2.meter_peak.r == 255
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_models/test_scale_theme.py -v`
Expected: FAIL

**Step 3: Update scale.py with full Scale dataclass**

```python
# m8py/models/scale.py
from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter


@dataclass
class NoteInterval:
    semitone: int = 0
    cents: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> NoteInterval:
        return NoteInterval(semitone=reader.read(), cents=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.semitone)
        writer.write(self.cents)


@dataclass
class Scale:
    name: str = ""
    note_enable: int = 0xFFF  # u16 bitmap, all 12 notes enabled
    note_offsets: list[NoteInterval] = field(
        default_factory=lambda: [NoteInterval() for _ in range(12)]
    )

    @staticmethod
    def from_reader(reader: M8FileReader) -> Scale:
        note_enable = reader.read_u16_le()
        note_offsets = [NoteInterval.from_reader(reader) for _ in range(12)]
        name = reader.read_str(16)
        return Scale(name=name, note_enable=note_enable, note_offsets=note_offsets)

    def write(self, writer: M8FileWriter) -> None:
        writer.write_u16_le(self.note_enable)
        for ni in self.note_offsets:
            ni.write(writer)
        writer.write_str(self.name, 16)
```

**Step 4: Update theme.py with full Theme dataclass**

```python
# m8py/models/theme.py
from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter


@dataclass
class RGB:
    r: int = 0
    g: int = 0
    b: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> RGB:
        return RGB(r=reader.read(), g=reader.read(), b=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.r)
        writer.write(self.g)
        writer.write(self.b)


@dataclass
class Theme:
    background: RGB = field(default_factory=RGB)
    text_empty: RGB = field(default_factory=RGB)
    text_info: RGB = field(default_factory=RGB)
    text_default: RGB = field(default_factory=RGB)
    text_value: RGB = field(default_factory=RGB)
    text_title: RGB = field(default_factory=RGB)
    play_marker: RGB = field(default_factory=RGB)
    cursor: RGB = field(default_factory=RGB)
    selection: RGB = field(default_factory=RGB)
    scope_slider: RGB = field(default_factory=RGB)
    meter_low: RGB = field(default_factory=RGB)
    meter_mid: RGB = field(default_factory=RGB)
    meter_peak: RGB = field(default_factory=RGB)

    @staticmethod
    def from_reader(reader: M8FileReader) -> Theme:
        return Theme(
            background=RGB.from_reader(reader),
            text_empty=RGB.from_reader(reader),
            text_info=RGB.from_reader(reader),
            text_default=RGB.from_reader(reader),
            text_value=RGB.from_reader(reader),
            text_title=RGB.from_reader(reader),
            play_marker=RGB.from_reader(reader),
            cursor=RGB.from_reader(reader),
            selection=RGB.from_reader(reader),
            scope_slider=RGB.from_reader(reader),
            meter_low=RGB.from_reader(reader),
            meter_mid=RGB.from_reader(reader),
            meter_peak=RGB.from_reader(reader),
        )

    def write(self, writer: M8FileWriter) -> None:
        for color in [
            self.background, self.text_empty, self.text_info,
            self.text_default, self.text_value, self.text_title,
            self.play_marker, self.cursor, self.selection,
            self.scope_slider, self.meter_low, self.meter_mid,
            self.meter_peak,
        ]:
            color.write(writer)
```

**Step 5: Run tests**

Run: `python -m pytest tests/test_models/test_scale_theme.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add m8py/models/scale.py m8py/models/theme.py tests/test_models/test_scale_theme.py
git commit -m "feat: Scale and Theme full file type models"
```

---

## Task 11: Settings and MIDI Mapping

**Files:**
- Create: `m8py/models/settings.py`
- Create: `m8py/models/midi.py`
- Create: `tests/test_models/test_settings.py`

**Dependencies:** Task 4, Task 5, Task 6

This task implements `MIDISettings` (28 bytes), `MixerSettings` (~34 bytes), `EffectsSettings` (version-conditional), and `MIDIMapping` (7 bytes). Follow the same TDD pattern as Task 8.

**Key byte layouts from Rust source:**

MIDISettings read order: `receive_sync(bool)`, `receive_transport(u8)`, `send_sync(bool)`, `send_transport(u8)`, `record_note_channel(u8)`, `record_note_velocity(bool)`, `record_note_delay_kill_commands(u8)`, `control_map_channel(u8)`, `song_row_cue_channel(u8)`, `track_input_channel[8]`, `track_input_instrument[8]`, `track_input_program_change(bool)`, `track_input_mode(u8)`.

MixerSettings: `master_volume(u8)`, `master_limit(u8)`, `track_volume[8]`, `chorus_volume(u8)`, `delay_volume(u8)`, `reverb_volume(u8)`, `analog_input_volume[2]`, `usb_input_volume(u8)`, `analog_input_chorus[2]`, `analog_input_delay[2]`, `analog_input_reverb[2]`, `usb_input_chorus(u8)`, `usb_input_delay(u8)`, `usb_input_reverb(u8)`, `dj_filter(u8)`, `dj_peak(u8)`, `dj_filter_type(u8)`, skip 4.

EffectsSettings: chorus (`mod_depth, mod_freq, reverb_send` + 3 unused), delay (`time_l, time_r, feedback, width, reverb_send` + 1 unused; pre-v4 also has `hp, lp` before those), reverb (`size, damping, mod_depth, mod_freq, width`; pre-v4 also has `hp, lp`).

MIDIMapping: 7 bytes (`channel, control_number, value, typ, param_index, min_value, max_value`).

**Test structure:** Write roundtrip tests for each, verify byte sizes match expectations. Use the same `from_reader`/`write` pattern. Tests should verify that `EffectsSettings` handles version-conditional hp/lp fields (pass version to `from_reader`).

**Commit message:** `feat: Settings (MIDI, Mixer, Effects) and MIDIMapping`

---

## Task 12: Modulators

**Files:**
- Create: `m8py/models/modulators.py`
- Create: `tests/test_models/test_modulators.py`

**Dependencies:** Task 4, Task 5, Task 3

**Key byte layout:** Each modulator is 6 bytes. Byte 0 = `(type << 4) | dest`. Bytes 1-5 are type-specific.

**Six modulator types:**
- AHDEnv: amount, attack, hold, decay (byte 5 unused)
- ADSREnv: amount, attack, decay, sustain, release
- DrumEnv: amount, peak, body, decay (byte 5 unused)
- LFO: amount, shape, trigger_mode, freq, retrigger
- TrigEnv: amount, attack, hold, decay, src
- TrackingEnv: amount, src, lval, hval (byte 5 unused)

**Implementation:** Use a `Modulator` base dataclass with `type` and `dest` fields, plus a `from_reader`/`write` that dispatches based on the type nibble. Each concrete type (AHDEnv, ADSREnv, etc.) is a separate dataclass. The `from_reader` always consumes exactly 6 bytes (seek to `start + 6` after reading).

**Tests:** Roundtrip each of the 6 types. Verify 6-byte size. Test unknown type byte raises `M8ParseError`.

**Commit message:** `feat: modulator types (AHD, ADSR, Drum, LFO, Trig, Tracking)`

---

## Task 13: Instruments

**Files:**
- Create: `m8py/models/instrument.py`
- Create: `tests/test_models/test_instruments.py`

**Dependencies:** Task 12, Task 3, Task 4, Task 5, Task 6

This is the most complex task. Each instrument occupies exactly 215 bytes.

**Common layout (all synth instruments after kind byte):**
- name (12), transp_eq (1), table_tick (1), volume (1), pitch (1), fine_tune (1)
- Engine-specific params (varies)
- filter_type (1), filter_cutoff (1), filter_res (1), amp (1), limit (1)
- mixer_pan (1), mixer_dry (1), mixer_chorus (1), mixer_delay (1), mixer_reverb (1)
- Gap/padding to mod_offset
- associated_eq (1, v4.1+ only, at mod_offset-1 from synth params start)
- 4 modulators x 6 bytes = 24 bytes (at mod_offset from synth params start)

**Critical: all instruments place modulators at byte 63 from kind byte.** MOD_OFFSET values differ per type because they're relative to the position after reading filter/mixer.

**Implementation approach:**
1. `EmptyInstrument` — kind=0xFF, skip 214 bytes
2. `SynthParams` dataclass — shared filter/mixer/modulator fields, with `from_reader(reader, version, mod_offset)` and `write(writer, version, mod_offset)`
3. Each instrument type (Wavsynth, Macrosynth, Sampler, FMSynth, MIDIOut, HyperSynth, External) as a dataclass with engine-specific fields + `SynthParams`
4. `BaseInstrument.from_reader()` — reads kind byte, dispatches to subclass, enforces 215-byte consumption via `expect_consumed`
5. `BaseInstrument.write()` — writes kind byte, delegates, pads to 215 bytes via `expect_written`

**Sampler special case:** sample_path (128 bytes) is at offset 0x57 from instrument start (including kind byte). Use `reader.seek(start_pos + 0x57)` to read it.

**MIDIOut special case:** Different layout — no volume/pitch/fine_tune, no filter/mixer. Has port, channel, bank_select, program_change, 3 padding bytes, 10 ControlChange pairs (20 bytes), then modulators only.

**Tests:** Roundtrip each instrument type with known byte sequences. Verify 215-byte invariant. Test EmptyInstrument. Test unknown kind byte raises error.

**Commit message:** `feat: all instrument types with 215-byte enforcement`

---

## Task 14: Song Model

**Files:**
- Create: `m8py/models/song.py`
- Create: `tests/test_models/test_song.py`

**Dependencies:** Task 7, Task 9, Task 10, Task 11, Task 13

The Song model assembles all structures. Reading uses offset tables to seek to each section. Writing writes sections sequentially.

**Read order (from Rust):**
1. Header (14 bytes, already parsed by I/O layer)
2. directory (128 bytes), transpose (1), tempo (f32, 4 bytes), quantize (1), name (12)
3. MIDISettings, key (1), skip 18, MixerSettings
4. Seek to groove offset: 32 Grooves
5. Seek to song offset: 256 SongSteps (2048 bytes flat, row-major)
6. Seek to phrases offset: 255 Phrases
7. Seek to chains offset: 255 Chains
8. Seek to table offset: 256 Tables
9. Seek to instruments offset: 128 Instruments
10. Skip 3 bytes, then EffectsSettings
11. Seek to midi_mapping offset: 128 MIDIMappings
12. If has_scales: seek to scale offset, 16 Scales
13. If has_eq: seek to eq offset, read EQs

**Tests:** Build a minimal song from default empty structures, write to bytes, read back, verify structural equality. Verify total byte count matches expected file size.

**Commit message:** `feat: Song model with offset-based read/write`

---

## Task 15: I/O Layer (load/save)

**Files:**
- Create: `m8py/io.py`
- Create: `tests/test_io.py`

**Dependencies:** Task 14, Task 10, Task 6

**Implementation:**
- `load(path)` — read file bytes, parse header, dispatch to Song/Instrument/Theme/Scale `from_reader`
- `load_song(path)` — load + assert file type is SONG
- `load_instrument(path)`, `load_theme(path)`, `load_scale(path)` — same pattern
- `save(obj, path, validate=True)` — write header + obj to bytes, write to file

**Tests:**
- Create an empty Song, save to temp file, load back, verify equality
- Save a Theme, load back, verify
- Test `load_song` on an instrument file raises `M8ParseError`
- Test loading truncated file raises `M8ParseError`

**Commit message:** `feat: I/O layer (load/save for all file types)`

---

## Task 16: Validation

**Files:**
- Create: `m8py/validate.py`
- Create: `tests/test_validate.py`

**Dependencies:** Task 14

**Implementation:** `validate(obj) -> list[ValidationIssue]` checks:
- Byte field ranges (0-255)
- Tempo range
- Slot reference validity (chain refs point to non-empty phrases, etc.)
- String length limits
- Sample path non-empty for Sampler instruments (warning)

**Tests:** Construct songs with out-of-range values, dangling references, etc. Verify appropriate issues are returned.

**Commit message:** `feat: validation layer`

---

## Task 17: Notation

**Files:**
- Create: `m8py/compose/notation.py`
- Create: `tests/test_compose/test_notation.py`

**Dependencies:** Task 8 (FX, PhraseStep)

**Implementation:**
- `normalize_note(note) -> int` — accepts string ("C4"), int (60), returns MIDI int
- Named constants: `C0` through `B9`, `REST`, `NOTE_OFF`
- `parse_pattern(pattern: str) -> list[PhraseStep]` — parse note strings with velocity

**Tests:** Test all three input formats. Test sharps/flats. Test pattern parsing with `---`, `.`, `OFF`, velocity `@7F`. Test `|` bar separators are ignored. Test invalid note raises ValueError.

**Commit message:** `feat: notation parsing (string, MIDI int, named helpers)`

---

## Task 18: Slot Allocator

**Files:**
- Create: `m8py/compose/allocator.py`
- Create: `tests/test_compose/test_allocator.py`

**Dependencies:** Task 9, Task 13

**Implementation:** `SlotAllocator(deduplicate=False)` with `alloc_phrase`, `alloc_chain`, `alloc_instrument`, `alloc_table`, `alloc_groove`, `pin_*`, introspection methods.

**Tests:**
- Allocate phrases, verify sequential slot assignment
- Pin a specific slot, verify next alloc skips it
- Exhaust all 255 phrase slots, verify `M8ResourceExhaustedError`
- With `deduplicate=True`, allocate identical phrases, verify same slot returned
- With `deduplicate=False`, identical phrases get different slots

**Commit message:** `feat: slot allocator with opt-in deduplication`

---

## Task 19: SongBuilder

**Files:**
- Create: `m8py/compose/builder.py`
- Create: `tests/test_compose/test_builder.py`

**Dependencies:** Task 15, Task 17, Task 18

**Implementation:** `SongBuilder` with fluent API, `last_slot` property, `build()` that returns validated Song.

**Tests:**
- Build a minimal song: 1 instrument, 1 phrase, 1 chain, 1 song step. Save to bytes and verify it's loadable.
- Test `last_slot` returns correct indices
- Test method chaining works
- Test pattern string input to `add_phrase`

**Commit message:** `feat: SongBuilder imperative composition API`

---

## Task 20: Declarative Compose

**Files:**
- Create: `m8py/compose/declarative.py`
- Create: `tests/test_compose/test_declarative.py`

**Dependencies:** Task 19

**Implementation:** `compose()` function and `TrackDef` dataclass. Pattern-to-phrase splitting at 16 steps, auto-chaining, song grid placement.

**Tests:**
- Single track, single pattern (<=16 steps): verify 1 phrase, 1 chain
- Single track, long pattern (>16 steps): verify auto-split into multiple phrases
- Multiple tracks: verify aligned song rows
- Deduplication: two tracks with identical patterns share phrase slots

**Commit message:** `feat: declarative composition API`

---

## Task 21: Sample Export

**Files:**
- Create: `m8py/compose/samples.py`
- Create: `tests/test_compose/test_samples.py`

**Dependencies:** Task 15

**Implementation:** `export_to_sdcard()` with dry_run mode, `ExportResult`.

**Tests:**
- Export a song with no samplers: just the .m8s file
- Export with sampler instruments and sample_sources: verify files copied to correct paths
- Missing sample raises `M8ValidationError`
- Dry run returns manifest without writing

**Commit message:** `feat: SD card sample export`

---

## Task 22: Property and Fuzz Tests

**Files:**
- Create: `tests/test_properties.py`
- Create: `tests/test_fuzz.py`

**Dependencies:** Task 15

**Implementation:**

Property tests (Hypothesis):
- Roundtrip invariant for all model types
- Instrument 215-byte invariant
- Allocator limits

Fuzz tests:
- Random bytes to `load()` — must raise `M8ParseError` or return valid object, never crash

**Commit message:** `feat: property-based and fuzz tests`

---

## Task 23: Package Exports and Final Integration

**Files:**
- Modify: `m8py/__init__.py`
- Modify: `m8py/format/__init__.py`
- Modify: `m8py/models/__init__.py`
- Modify: `m8py/compose/__init__.py`
- Create: `tests/test_integration.py`

**Dependencies:** Task 20, Task 21, Task 22

**Implementation:** Set up clean public API exports. Write an integration test that creates a multi-track song using the declarative API, saves it, loads it back, and verifies structural equality.

**Commit message:** `feat: public API exports and integration test`

---

## Dependency Graph

```
Task 1 (scaffolding)
├── Task 2 (errors)
│   ├── Task 4 (reader)
│   └── Task 5 (writer)
├── Task 3 (constants)
│
├── Task 6 (version) ← Task 4, Task 5
│   └── Task 7 (offsets) ← Task 6
│
├── Task 8 (simple models) ← Task 4, Task 5
│   ├── Task 9 (song structures) ← Task 8
│   └── Task 10 (scale, theme) ← Task 8, Task 6
│
├── Task 11 (settings, midi) ← Task 4, Task 5, Task 6
├── Task 12 (modulators) ← Task 4, Task 5, Task 3
│   └── Task 13 (instruments) ← Task 12, Task 3, Task 6
│
└── Task 14 (song) ← Task 7, Task 9, Task 10, Task 11, Task 13
    ├── Task 15 (I/O) ← Task 14
    │   ├── Task 16 (validation) ← Task 14
    │   ├── Task 17 (notation) ← Task 8
    │   ├── Task 18 (allocator) ← Task 9, Task 13
    │   ├── Task 19 (builder) ← Task 15, Task 17, Task 18
    │   │   └── Task 20 (declarative) ← Task 19
    │   ├── Task 21 (samples) ← Task 15
    │   └── Task 22 (property/fuzz) ← Task 15
    └── Task 23 (integration) ← Task 20, Task 21, Task 22
```

**Maximum parallelism:** Tasks 2, 3 can run in parallel. Tasks 4, 5 can run in parallel. Tasks 8, 11, 12 can run in parallel. Tasks 9, 10 can run in parallel. Tasks 16, 17, 18, 21, 22 can run in parallel.
