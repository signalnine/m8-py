"""Formatting helpers for M8 FX and other display values."""

from m8py.display.commands import fx_command_name


def format_fx(
    fx,
    version: tuple[int, int] | None = None,
    instrument_kind: int | None = None,
) -> str:
    """Format an FX object as a display string like 'ARP 03' or '--- --'.

    Args:
        fx: An FX dataclass with .command and .value attributes.
        version: (major, minor) file format version tuple.
        instrument_kind: InstrumentKind value for instrument-specific commands.
    """
    if fx.command == 0xFF:
        return "--- --"
    name = fx_command_name(fx.command, version=version, instrument_kind=instrument_kind)
    return f"{name} {fx.value:02X}"
