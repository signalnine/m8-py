from __future__ import annotations
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Union

from m8py.format.errors import M8ValidationError
from m8py.io import save
from m8py.models.instrument import Sampler
from m8py.models.song import Song


def _safe_join(base: Path, untrusted: str) -> Path:
    """Join an untrusted relative path under base, rejecting traversal.

    Rejects absolute paths, drive letters, backslash separators, and any
    component equal to '..' or containing a NUL byte. The result is
    guaranteed (post-resolve) to live under base.resolve().
    """
    if not untrusted:
        raise M8ValidationError("path is empty")
    if "\x00" in untrusted:
        raise M8ValidationError(f"path contains NUL byte: {untrusted!r}")
    cleaned = untrusted.lstrip("/")
    if PurePosixPath(cleaned).is_absolute() or os.path.isabs(cleaned) or "\\" in cleaned:
        raise M8ValidationError(f"path is not relative or contains backslash: {untrusted!r}")
    parts = PurePosixPath(cleaned).parts
    if any(p == ".." for p in parts):
        raise M8ValidationError(f"path contains parent reference: {untrusted!r}")
    base_resolved = base.resolve()
    candidate = (base_resolved / cleaned).resolve()
    try:
        candidate.relative_to(base_resolved)
    except ValueError:
        raise M8ValidationError(
            f"path escapes export root: {untrusted!r}"
        ) from None
    return candidate


@dataclass
class ExportResult:
    """Result of an export operation."""
    song_path: Path
    sample_files: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def export_to_sdcard(
    song: Song,
    sdcard_root: Union[str, Path],
    sample_sources: dict[str, Union[str, Path]] | None = None,
    dry_run: bool = False,
) -> ExportResult:
    """Export a song and its samples to an SD card directory structure.

    Args:
        song: The Song to export.
        sdcard_root: Root directory of the SD card (or target export dir).
        sample_sources: Mapping from M8 sample paths (as stored in Sampler
            instruments) to local source file paths. Required for any
            Sampler instruments that reference samples.
        dry_run: If True, compute the manifest without writing any files.

    Returns:
        ExportResult with paths of files that were (or would be) written.

    Raises:
        M8ValidationError: If a Sampler references a sample not found in
            sample_sources.
    """
    sdcard = Path(sdcard_root)
    sample_sources = sample_sources or {}
    raw_name = song.name or "Untitled"
    if any(sep in raw_name for sep in ("/", "\\", "\x00")) or raw_name in ("..", "."):
        raise M8ValidationError(
            f"song.name contains path separator or is reserved: {raw_name!r}"
        )
    song_filename = f"{raw_name}.m8s"
    songs_dir = _safe_join(sdcard, "Songs")
    song_path = _safe_join(songs_dir, song_filename)
    result = ExportResult(song_path=song_path)

    sample_dests: list[tuple[Sampler, Path]] = []
    for i, inst in enumerate(song.instruments):
        if not isinstance(inst, Sampler):
            continue
        if not inst.sample_path:
            continue

        m8_path = inst.sample_path
        if m8_path not in sample_sources:
            raise M8ValidationError(
                f"instrument[{i}]: Sampler references '{m8_path}' "
                f"but no source provided in sample_sources"
            )

        try:
            dest = _safe_join(sdcard, m8_path)
        except M8ValidationError as e:
            raise M8ValidationError(
                f"instrument[{i}]: unsafe sample_path: {e}"
            ) from None
        sample_dests.append((inst, dest))
        result.sample_files.append(dest)

    if dry_run:
        return result

    result.song_path.parent.mkdir(parents=True, exist_ok=True)
    save(song, result.song_path)

    for inst, dest in sample_dests:
        source = Path(sample_sources[inst.sample_path])
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

    return result
