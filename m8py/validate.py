from __future__ import annotations
import math
from dataclasses import dataclass
from enum import Enum
from typing import List

from m8py.format.constants import EMPTY, N_PHRASES, N_CHAINS, N_INSTRUMENTS
from m8py.models.song import Song


class Severity(Enum):
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    severity: Severity
    path: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.path}: {self.message}"


def validate(song: Song) -> List[ValidationIssue]:
    """Validate a Song and return a list of issues found."""
    issues: List[ValidationIssue] = []

    # Tempo range. NaN compares False against any bound, so check it explicitly
    # before the range test or float('nan') silently passes validation.
    if math.isnan(song.tempo) or not (1.0 <= song.tempo <= 800.0):
        issues.append(ValidationIssue(
            Severity.ERROR, "song.tempo",
            f"tempo {song.tempo} out of range [1.0, 800.0]",
        ))

    # Byte field ranges (both bounds: write() truncated negatives to low byte
    # and accepted >255, so validate must catch both before save).
    for field_name in ("transpose", "quantize", "key"):
        value = getattr(song, field_name)
        _check_byte(issues, f"song.{field_name}", field_name, value)

    # PhraseStep byte fields - bypass writer's per-byte check by surfacing
    # errors at validate time on a fully populated path.
    for i, phrase in enumerate(song.phrases):
        for j, ps in enumerate(phrase.steps):
            _check_byte(issues, f"phrases[{i}].steps[{j}].note", "note", ps.note)
            _check_byte(issues, f"phrases[{i}].steps[{j}].velocity", "velocity", ps.velocity)
            _check_byte(
                issues, f"phrases[{i}].steps[{j}].instrument", "instrument", ps.instrument
            )

    # ChainStep.transpose - phrase index is range-checked below as a reference.
    for i, chain in enumerate(song.chains):
        for j, cs in enumerate(chain.steps):
            _check_byte(
                issues, f"chains[{i}].steps[{j}].transpose", "transpose", cs.transpose
            )

    # Song name length (12-byte field, no null terminator required)
    if len(song.name) > 12:
        issues.append(ValidationIssue(
            Severity.WARNING, "song.name",
            f"name '{song.name}' will be truncated to 12 characters",
        ))

    # Song name must encode cleanly as ASCII; writer is strict, validate fails fast.
    if not _is_ascii(song.name):
        issues.append(ValidationIssue(
            Severity.ERROR, "song.name",
            f"name {song.name!r} contains non-ASCII characters and will fail to save",
        ))

    # Song step chain references
    for i, step in enumerate(song.song_steps):
        for t, chain_idx in enumerate(step.tracks):
            if chain_idx != EMPTY and chain_idx >= N_CHAINS:
                issues.append(ValidationIssue(
                    Severity.ERROR, f"song_steps[{i}].tracks[{t}]",
                    f"chain reference {chain_idx} >= {N_CHAINS}",
                ))

    # Chain phrase references
    for i, chain in enumerate(song.chains):
        for j, cs in enumerate(chain.steps):
            if cs.phrase != EMPTY and cs.phrase >= N_PHRASES:
                issues.append(ValidationIssue(
                    Severity.ERROR, f"chains[{i}].steps[{j}].phrase",
                    f"phrase reference {cs.phrase} >= {N_PHRASES}",
                ))

    # Phrase instrument references
    for i, phrase in enumerate(song.phrases):
        for j, ps in enumerate(phrase.steps):
            if ps.instrument != EMPTY and ps.instrument >= N_INSTRUMENTS:
                issues.append(ValidationIssue(
                    Severity.ERROR, f"phrases[{i}].steps[{j}].instrument",
                    f"instrument reference {ps.instrument} >= {N_INSTRUMENTS}",
                ))

    # Sampler instruments without sample paths (warning)
    from m8py.models.instrument import Sampler, EmptyInstrument
    for i, inst in enumerate(song.instruments):
        if isinstance(inst, Sampler) and not inst.sample_path:
            issues.append(ValidationIssue(
                Severity.WARNING, f"instruments[{i}]",
                "Sampler instrument has empty sample_path",
            ))

        # Instrument names must encode as ASCII or save() crashes.
        inst_name = _instrument_name(inst)
        if inst_name is not None and not _is_ascii(inst_name):
            issues.append(ValidationIssue(
                Severity.ERROR, f"instruments[{i}].name",
                f"name {inst_name!r} contains non-ASCII characters and will fail to save",
            ))

        # Sample paths must also be ASCII.
        if isinstance(inst, Sampler) and inst.sample_path and not _is_ascii(inst.sample_path):
            issues.append(ValidationIssue(
                Severity.ERROR, f"instruments[{i}].sample_path",
                f"sample_path {inst.sample_path!r} contains non-ASCII characters and will fail to save",
            ))

    return issues


def _check_byte(issues: List[ValidationIssue], path: str, name: str, value: int) -> None:
    if not (0 <= value <= 255):
        issues.append(ValidationIssue(
            Severity.ERROR, path,
            f"{name} {value} out of byte range [0, 255]",
        ))


def _is_ascii(s: str) -> bool:
    return all(ord(c) < 128 for c in s)


def _instrument_name(inst) -> str | None:
    """Return the displayable name of an instrument, or None for EmptyInstrument."""
    common = getattr(inst, "common", None)
    if common is not None:
        return getattr(common, "name", None)
    return getattr(inst, "name", None)
