# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install for development
pip install -e ".[dev]"

# Run all tests (628 tests)
python3 -m pytest

# Run a single test
python3 -m pytest tests/test_models/test_settings.py::TestMixerSettings::test_roundtrip -v

# Run a test file
python3 -m pytest tests/test_display/test_commands.py -v

# Byte-exact roundtrip tests against 281 community presets
python3 -m pytest tests/test_matey_roundtrip.py

# Lint
python3 -m ruff check m8py/ tests/

# Format
python3 -m ruff format m8py/ tests/
```

Zero runtime dependencies. Python 3.11+.

## Architecture

### Layer structure

```
m8py/format/    → Binary I/O: M8FileReader (cursor-based), M8FileWriter, version-aware offsets
m8py/models/    → Dataclasses: Song, 8 instrument types, Phrase, Chain, Table, settings, etc.
m8py/compose/   → Song building: declarative compose(), imperative SongBuilder, pattern parser
m8py/display/   → Name lookups, FX command tables, tracker-style text rendering
m8py/io.py      → File load/save facade
m8py/validate.py → Constraint checking
```

### Read/write flow

Every model has `from_reader(M8FileReader)` and `write(M8FileWriter)`. Song reading: parse header → seek to version-aware offsets (`offsets_for_version()`) → read each section sequentially. Writing mirrors this with `_pad_to()` calls between sections to maintain exact byte positions.

### Instruments: polymorphic 215-byte model

All 8 instrument types serialize to exactly 215 bytes. Reading dispatches on the kind byte at offset 0. Each type has a shared `SynthCommon` (name, filter, mixer fields), kind-specific engine params, 4 modulator slots (offset 63), and a 128-byte tail (sample path, chords, or padding). Writing enforces `expect_written(215)`.

### Version-conditional logic

`M8Version.caps` returns `VersionCapabilities` with boolean flags (e.g., `has_scales`, `has_eq`, `has_limiter_settings`). Models wrap version-dependent reads/writes in capability checks. Song section offsets vary by version — always use `offsets_for_version()`.

Key version gates: v2.5 (scales), v3.0 (HyperSynth/External, new modulators), v4.0 (EQ), v4.1 (expanded EQ), v6.0 (limiter), v6.1 (OTT, shimmer, mfx_kind).

### Compose subsystem

Three levels: `compose()` with `TrackDef` (pattern strings auto-split into phrases/chains), `SongBuilder` (fluent imperative), `SlotAllocator` (low-level index management with optional deduplication). Pattern notation: `C4 E4 G4 . OFF C5@7F | Bb3`.

### Display subsystem

`display/names.py`: pure dict tables mapping enum values to display strings. `display/commands.py`: version-dependent FX command tables (V2/V3/V4/V6.2, 78 commands total), per-instrument command tables, modulator commands — all verified against v6.5.1G firmware binary. `display/render.py`: tracker-style text rendering.

## Key constraints

- **Byte-exact round-trip fidelity is the core invariant.** Load a file, save it, get identical bytes. The 281-preset roundtrip test suite (`test_matey_roundtrip.py`) enforces this. Never change read/write logic without running it.
- Mixer analog input sends are grouped by **channel** (L then R), not by effect type. Confirmed by firmware RE.
- File format section offsets are identical from v4 through v6 — new fields fit in existing padding bytes.
- Effects section is always 61 bytes; mixer section is always 32 bytes within the 96-byte metadata block.
- `EMPTY = 0xFF` is the sentinel for unused slots throughout the format.

## Firmware RE

Reverse engineering notes and scripts are in `re/`. Two firmware binaries analyzed: v4.0.2 and v6.5.1G (flash base `0x60000000`, ARM Cortex-M7). Findings documented in `re/FINDINGS.md`. Rust reference implementation at `/tmp/m8-file-parser/src/` when available.
