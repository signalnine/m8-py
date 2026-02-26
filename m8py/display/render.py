"""Pretty-print renderers for M8 tracker structures.

Renders phrases, chains, tables, and song grids in tracker-style text format.
"""

from m8py.display.names import note_name
from m8py.display.formatters import format_fx
from m8py.format.constants import EMPTY, InstrumentKind, N_TRACKS


def render_phrase(phrase, version=None, instrument_kind=None) -> str:
    """Render a phrase as a 16-row tracker grid.

    Format: ROW NOTE VEL INS FX1    FX2    FX3
    """
    ver = (version.major, version.minor) if version is not None else None
    lines = []
    lines.append("ROW NOTE VEL INS FX1    FX2    FX3")
    for i, step in enumerate(phrase.steps):
        note_str = "---" if step.note == EMPTY else note_name(step.note)
        vel_str = "--" if step.velocity == EMPTY else f"{step.velocity:02X}"
        ins_str = "--" if step.instrument == EMPTY else f"{step.instrument:02X}"
        fx1_str = format_fx(step.fx1, version=ver, instrument_kind=instrument_kind)
        fx2_str = format_fx(step.fx2, version=ver, instrument_kind=instrument_kind)
        fx3_str = format_fx(step.fx3, version=ver, instrument_kind=instrument_kind)
        lines.append(f" {i:02X} {note_str} {vel_str}  {ins_str} {fx1_str} {fx2_str} {fx3_str}")
    return "\n".join(lines)


def render_chain(chain) -> str:
    """Render a chain as phrase references with transpose."""
    lines = []
    lines.append("ROW PHR TSP")
    for i, step in enumerate(chain.steps):
        phr_str = "--" if step.phrase == EMPTY else f"{step.phrase:02X}"
        tsp_str = f"{step.transpose:02X}"
        lines.append(f" {i:02X}  {phr_str}  {tsp_str}")
    return "\n".join(lines)


def render_table(table, version=None) -> str:
    """Render a table as a 16-row tracker grid.

    Format: ROW TSP VEL FX1    FX2    FX3
    """
    ver = (version.major, version.minor) if version is not None else None
    lines = []
    lines.append("ROW TSP VEL FX1    FX2    FX3")
    for i, step in enumerate(table.steps):
        tsp_str = f"{step.transpose:02X}"
        vel_str = "--" if step.velocity == EMPTY else f"{step.velocity:02X}"
        fx1_str = format_fx(step.fx1, version=ver)
        fx2_str = format_fx(step.fx2, version=ver)
        fx3_str = format_fx(step.fx3, version=ver)
        lines.append(f" {i:02X}  {tsp_str}  {vel_str} {fx1_str} {fx2_str} {fx3_str}")
    return "\n".join(lines)


def render_song_grid(song, rows=None) -> str:
    """Render the song grid (chain references across 8 tracks).

    Args:
        song: Song object.
        rows: Number of rows to render (default: auto-detect last used row).
    """
    if rows is None:
        rows = _last_used_row(song) + 1
        rows = max(rows, 1)

    lines = []
    header = "ROW " + " ".join(f"T{t+1}" for t in range(N_TRACKS))
    lines.append(header)
    for i in range(min(rows, len(song.song_steps))):
        step = song.song_steps[i]
        cols = []
        for t in range(N_TRACKS):
            val = step.tracks[t]
            cols.append("--" if val == EMPTY else f"{val:02X}")
        lines.append(f" {i:02X} " + " ".join(cols))
    return "\n".join(lines)


def _last_used_row(song) -> int:
    """Find the last song row with any non-empty chain reference."""
    for i in range(len(song.song_steps) - 1, -1, -1):
        if any(t != EMPTY for t in song.song_steps[i].tracks):
            return i
    return 0


def render_instrument_summary(instrument) -> str:
    """Render a one-line instrument summary.

    Format: [NN] KIND  NAME  (key params)
    """
    if instrument.kind == InstrumentKind.NONE:
        return "---"

    kind_names = {
        InstrumentKind.WAVSYNTH: "WAVSYNTH",
        InstrumentKind.MACROSYNTH: "MACROSYN",
        InstrumentKind.SAMPLER: "SAMPLER",
        InstrumentKind.MIDIOUT: "MIDIOUT",
        InstrumentKind.FMSYNTH: "FMSYNTH",
        InstrumentKind.HYPERSYNTH: "HYPRSYTH",
        InstrumentKind.EXTERNAL: "EXTERNAL",
    }
    kind_str = kind_names.get(instrument.kind, f"0x{instrument.kind:02X}")

    if instrument.kind == InstrumentKind.MIDIOUT:
        name = instrument.name
    else:
        name = instrument.common.name

    return f"{kind_str:8s}  {name}"


def render_song_overview(song) -> str:
    """Render a full song overview: metadata, instruments, and grid."""
    lines = []

    # Metadata
    lines.append(f"Song: {song.name}")
    lines.append(f"Version: {song.version.major}.{song.version.minor}.{song.version.patch}")
    lines.append(f"Tempo: {song.tempo:.1f}  Key: {song.key}  Transpose: {song.transpose}")
    lines.append("")

    # Active instruments
    lines.append("Instruments:")
    for i, inst in enumerate(song.instruments):
        if inst.kind != InstrumentKind.NONE:
            lines.append(f"  {i:02X}  {render_instrument_summary(inst)}")
    lines.append("")

    # Song grid
    lines.append(render_song_grid(song))

    return "\n".join(lines)
