from __future__ import annotations
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

    # Tempo range
    if song.tempo < 1.0 or song.tempo > 800.0:
        issues.append(ValidationIssue(
            Severity.ERROR, "song.tempo",
            f"tempo {song.tempo} out of range [1.0, 800.0]",
        ))

    # Byte field ranges
    if song.transpose > 255:
        issues.append(ValidationIssue(
            Severity.ERROR, "song.transpose",
            f"transpose {song.transpose} exceeds byte range",
        ))

    if song.quantize > 255:
        issues.append(ValidationIssue(
            Severity.ERROR, "song.quantize",
            f"quantize {song.quantize} exceeds byte range",
        ))

    if song.key > 255:
        issues.append(ValidationIssue(
            Severity.ERROR, "song.key",
            f"key {song.key} exceeds byte range",
        ))

    # Song name length
    if len(song.name) > 11:
        issues.append(ValidationIssue(
            Severity.WARNING, "song.name",
            f"name '{song.name}' will be truncated to 11 characters",
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

    return issues
