import pytest
from m8py.compose.allocator import SlotAllocator
from m8py.format.constants import N_PHRASES, N_CHAINS, N_INSTRUMENTS, N_TABLES, N_GROOVES
from m8py.format.errors import M8ResourceExhaustedError
from m8py.models.phrase import Phrase, PhraseStep
from m8py.models.chain import Chain
from m8py.models.instrument import WavSynth
from m8py.models.table import Table
from m8py.models.groove import Groove


class TestSlotAllocator:
    def test_sequential_phrase_allocation(self):
        alloc = SlotAllocator()
        p1 = Phrase()
        p2 = Phrase()
        assert alloc.alloc_phrase(p1) == 0
        assert alloc.alloc_phrase(p2) == 1

    def test_sequential_chain_allocation(self):
        alloc = SlotAllocator()
        assert alloc.alloc_chain(Chain()) == 0
        assert alloc.alloc_chain(Chain()) == 1

    def test_sequential_instrument_allocation(self):
        alloc = SlotAllocator()
        assert alloc.alloc_instrument(WavSynth()) == 0
        assert alloc.alloc_instrument(WavSynth()) == 1

    def test_pin_then_alloc_skips_pinned(self):
        alloc = SlotAllocator()
        alloc.pin_phrase(0, Phrase())
        slot = alloc.alloc_phrase(Phrase())
        assert slot == 1

    def test_pin_middle_slot(self):
        alloc = SlotAllocator()
        alloc.pin_phrase(5, Phrase())
        # First alloc still gets 0
        assert alloc.alloc_phrase(Phrase()) == 0

    def test_exhaust_phrases_raises(self):
        alloc = SlotAllocator()
        for i in range(N_PHRASES):
            alloc.alloc_phrase(Phrase())
        with pytest.raises(M8ResourceExhaustedError) as exc_info:
            alloc.alloc_phrase(Phrase())
        assert "phrase" in str(exc_info.value)

    def test_exhaust_instruments_raises(self):
        alloc = SlotAllocator()
        for i in range(N_INSTRUMENTS):
            alloc.alloc_instrument(WavSynth())
        with pytest.raises(M8ResourceExhaustedError):
            alloc.alloc_instrument(WavSynth())

    def test_dedup_identical_phrases_same_slot(self):
        alloc = SlotAllocator(deduplicate=True)
        p1 = Phrase()
        p2 = Phrase()
        slot1 = alloc.alloc_phrase(p1)
        slot2 = alloc.alloc_phrase(p2)
        assert slot1 == slot2
        assert alloc.phrases_used == 1

    def test_dedup_different_phrases_different_slots(self):
        alloc = SlotAllocator(deduplicate=True)
        p1 = Phrase()
        p2 = Phrase(steps=[PhraseStep(note=60)] + [PhraseStep() for _ in range(15)])
        slot1 = alloc.alloc_phrase(p1)
        slot2 = alloc.alloc_phrase(p2)
        assert slot1 != slot2

    def test_no_dedup_identical_phrases_different_slots(self):
        alloc = SlotAllocator(deduplicate=False)
        p1 = Phrase()
        p2 = Phrase()
        slot1 = alloc.alloc_phrase(p1)
        slot2 = alloc.alloc_phrase(p2)
        assert slot1 != slot2

    def test_used_and_remaining_counts(self):
        alloc = SlotAllocator()
        assert alloc.phrases_used == 0
        assert alloc.phrases_remaining == N_PHRASES
        alloc.alloc_phrase(Phrase())
        assert alloc.phrases_used == 1
        assert alloc.phrases_remaining == N_PHRASES - 1

    def test_pin_invalid_slot_raises(self):
        alloc = SlotAllocator()
        with pytest.raises(ValueError):
            alloc.pin_phrase(-1, Phrase())
        with pytest.raises(ValueError):
            alloc.pin_phrase(N_PHRASES, Phrase())

    def test_groove_allocation(self):
        alloc = SlotAllocator()
        assert alloc.alloc_groove(Groove()) == 0
        assert alloc.grooves_used == 1
        assert alloc.grooves_remaining == N_GROOVES - 1

    def test_table_allocation(self):
        alloc = SlotAllocator()
        assert alloc.alloc_table(Table()) == 0
        assert alloc.tables_used == 1

    def test_all_resource_types_independent(self):
        """Each resource type has its own slot space."""
        alloc = SlotAllocator()
        assert alloc.alloc_phrase(Phrase()) == 0
        assert alloc.alloc_chain(Chain()) == 0
        assert alloc.alloc_instrument(WavSynth()) == 0
        assert alloc.alloc_table(Table()) == 0
        assert alloc.alloc_groove(Groove()) == 0
