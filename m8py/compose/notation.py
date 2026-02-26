"""Note parsing: string notation, MIDI integers, and named helpers."""
from __future__ import annotations
from m8py.models.phrase import PhraseStep
from m8py.format.constants import EMPTY

# Note name to pitch class (semitone within octave)
_NOTE_NAMES = {
    "C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11,
}
_ACCIDENTALS = {"#": 1, "b": -1}


def normalize_note(note) -> int:
    """Convert any note representation to MIDI int (0-127).

    Accepts:
        - str: "C4", "F#3", "Bb5"
        - int: 0-127 (pass-through)
    """
    if isinstance(note, int):
        if not (0 <= note <= 127):
            raise ValueError(f"MIDI note {note} out of range 0-127")
        return note

    if not isinstance(note, str) or len(note) < 2:
        raise ValueError(f"invalid note: {note!r}")

    s = note.strip()
    name = s[0].upper()
    if name not in _NOTE_NAMES:
        raise ValueError(f"invalid note name: {name!r} in {note!r}")

    pitch_class = _NOTE_NAMES[name]
    rest = s[1:]

    # Check for accidental
    if rest and rest[0] in _ACCIDENTALS:
        pitch_class += _ACCIDENTALS[rest[0]]
        rest = rest[1:]

    # Rest should be the octave number
    try:
        octave = int(rest)
    except ValueError:
        raise ValueError(f"invalid octave in note: {note!r}")

    midi = (octave + 1) * 12 + pitch_class
    if not (0 <= midi <= 127):
        raise ValueError(f"note {note!r} maps to MIDI {midi}, out of range")
    return midi


def parse_pattern(pattern: str) -> list[PhraseStep]:
    """Parse a tracker-style pattern string into PhraseStep objects.

    Syntax:
        Notes: "C4", "F#3", "Bb5"
        Empty: "---" or "."
        Note off: "OFF"
        Velocity: "C4@7F" (hex)
        Bar separator: "|" (cosmetic, ignored)
    """
    tokens = pattern.split()
    steps = []
    for token in tokens:
        if token == "|":
            continue

        if token in ("---", "."):
            steps.append(PhraseStep())
            continue

        if token.upper() == "OFF":
            steps.append(PhraseStep(note=0x80))
            continue

        # Check for velocity suffix
        velocity = EMPTY
        if "@" in token:
            note_part, vel_hex = token.split("@", 1)
            velocity = int(vel_hex, 16)
        else:
            note_part = token

        midi = normalize_note(note_part)
        steps.append(PhraseStep(note=midi, velocity=velocity))

    return steps


# Named note constants: C0 through B9
def _generate_note_constants():
    names = ["C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs", "A", "As", "B"]
    constants = {}
    for midi in range(128):
        octave = (midi // 12) - 1
        name_idx = midi % 12
        if octave >= 0:
            const_name = f"{names[name_idx]}{octave}"
            constants[const_name] = midi
    return constants

_NOTES = _generate_note_constants()
globals().update(_NOTES)

REST = None
NOTE_OFF = 0x80

# Make names available for: from m8py.compose.notation import C4, E4, ...
__all__ = list(_NOTES.keys()) + ["REST", "NOTE_OFF", "normalize_note", "parse_pattern"]
