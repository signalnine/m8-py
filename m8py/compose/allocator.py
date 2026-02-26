from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from m8py.format.constants import (
    N_PHRASES, N_CHAINS, N_INSTRUMENTS, N_TABLES, N_GROOVES,
)
from m8py.format.errors import M8ResourceExhaustedError


@dataclass
class _SlotPool:
    """Manages allocation for a single resource type."""
    name: str
    capacity: int
    _next: int = 0
    _pinned: set[int] = field(default_factory=set)
    _allocated: dict[int, Any] = field(default_factory=dict)
    _dedup_index: dict[int, int] | None = None  # hash -> slot

    def enable_dedup(self) -> None:
        self._dedup_index = {}

    def pin(self, slot: int, obj: Any) -> None:
        """Reserve a specific slot."""
        if slot < 0 or slot >= self.capacity:
            raise ValueError(f"{self.name} slot {slot} out of range [0, {self.capacity})")
        self._pinned.add(slot)
        self._allocated[slot] = obj
        if self._dedup_index is not None:
            h = _obj_hash(obj)
            self._dedup_index[h] = slot

    def alloc(self, obj: Any) -> int:
        """Allocate the next available slot. Returns slot index."""
        # Check dedup first
        if self._dedup_index is not None:
            h = _obj_hash(obj)
            if h in self._dedup_index:
                return self._dedup_index[h]

        # Find next free slot
        while self._next < self.capacity and self._next in self._pinned:
            self._next += 1

        if self._next >= self.capacity:
            raise M8ResourceExhaustedError(
                self.name, len(self._allocated), self.capacity
            )

        slot = self._next
        self._next += 1
        self._allocated[slot] = obj

        if self._dedup_index is not None:
            h = _obj_hash(obj)
            self._dedup_index[h] = slot

        return slot

    @property
    def used(self) -> int:
        return len(self._allocated)

    @property
    def remaining(self) -> int:
        return self.capacity - self.used


def _obj_hash(obj: Any) -> int:
    """Hash an object for deduplication. Uses repr for general-purpose hashing."""
    return hash(repr(obj))


class SlotAllocator:
    """Manages slot allocation for all M8 song resource types.

    Args:
        deduplicate: If True, identical objects reuse the same slot.
    """

    def __init__(self, deduplicate: bool = False):
        self._deduplicate = deduplicate
        self._phrases = _SlotPool("phrase", N_PHRASES)
        self._chains = _SlotPool("chain", N_CHAINS)
        self._instruments = _SlotPool("instrument", N_INSTRUMENTS)
        self._tables = _SlotPool("table", N_TABLES)
        self._grooves = _SlotPool("groove", N_GROOVES)
        if deduplicate:
            self._phrases.enable_dedup()
            self._chains.enable_dedup()
            self._instruments.enable_dedup()
            self._tables.enable_dedup()
            self._grooves.enable_dedup()

    def alloc_phrase(self, phrase: Any) -> int:
        return self._phrases.alloc(phrase)

    def alloc_chain(self, chain: Any) -> int:
        return self._chains.alloc(chain)

    def alloc_instrument(self, instrument: Any) -> int:
        return self._instruments.alloc(instrument)

    def alloc_table(self, table: Any) -> int:
        return self._tables.alloc(table)

    def alloc_groove(self, groove: Any) -> int:
        return self._grooves.alloc(groove)

    def pin_phrase(self, slot: int, phrase: Any) -> None:
        self._phrases.pin(slot, phrase)

    def pin_chain(self, slot: int, chain: Any) -> None:
        self._chains.pin(slot, chain)

    def pin_instrument(self, slot: int, instrument: Any) -> None:
        self._instruments.pin(slot, instrument)

    def pin_table(self, slot: int, table: Any) -> None:
        self._tables.pin(slot, table)

    def pin_groove(self, slot: int, groove: Any) -> None:
        self._grooves.pin(slot, groove)

    @property
    def phrases_used(self) -> int:
        return self._phrases.used

    @property
    def chains_used(self) -> int:
        return self._chains.used

    @property
    def instruments_used(self) -> int:
        return self._instruments.used

    @property
    def tables_used(self) -> int:
        return self._tables.used

    @property
    def grooves_used(self) -> int:
        return self._grooves.used

    @property
    def phrases_remaining(self) -> int:
        return self._phrases.remaining

    @property
    def chains_remaining(self) -> int:
        return self._chains.remaining

    @property
    def instruments_remaining(self) -> int:
        return self._instruments.remaining

    @property
    def tables_remaining(self) -> int:
        return self._tables.remaining

    @property
    def grooves_remaining(self) -> int:
        return self._grooves.remaining
