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
        super().__init__(f"{resource}: {used}/{capacity} slots used, none remaining")
