from m8py.format.errors import (
    M8Error, M8ParseError, M8VersionError,
    M8ValidationError, M8ResourceExhaustedError,
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
