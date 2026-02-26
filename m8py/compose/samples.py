from __future__ import annotations
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

from m8py.format.errors import M8ValidationError
from m8py.io import save
from m8py.models.instrument import Sampler
from m8py.models.song import Song


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
    result = ExportResult(song_path=sdcard / "Songs" / f"{song.name or 'Untitled'}.m8s")

    # Collect sample paths from Sampler instruments
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

        dest = sdcard / m8_path.lstrip("/")
        result.sample_files.append(dest)

    if dry_run:
        return result

    # Create directories and write files
    result.song_path.parent.mkdir(parents=True, exist_ok=True)
    save(song, result.song_path)

    for inst in song.instruments:
        if not isinstance(inst, Sampler) or not inst.sample_path:
            continue
        m8_path = inst.sample_path
        source = Path(sample_sources[m8_path])
        dest = sdcard / m8_path.lstrip("/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

    return result
