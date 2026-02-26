from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.version import M8Version
from m8py.models.settings import (
    MIDISettings, MixerSettings, EffectsSettings,
    ChorusSettings, DelaySettings, ReverbSettings,
)
from m8py.models.midi import MIDIMapping

V41 = M8Version(4, 1, 0)


class TestMIDISettings:
    def test_roundtrip(self):
        ms = MIDISettings(receive_sync=True, record_note_channel=5)
        w = M8FileWriter()
        ms.write(w)
        ms2 = MIDISettings.from_reader(M8FileReader(w.to_bytes()))
        assert ms2.receive_sync is True
        assert ms2.record_note_channel == 5

    def test_default_size(self):
        w = M8FileWriter()
        MIDISettings().write(w)
        # 9 scalar fields + 8 track_input_channel + 8 track_input_instrument + 2 = 27
        assert len(w.to_bytes()) == 27

    def test_all_fields_roundtrip(self):
        ms = MIDISettings(
            receive_sync=True, receive_transport=2,
            send_sync=True, send_transport=3,
            record_note_channel=10, record_note_velocity=True,
            record_note_delay_kill_commands=1, control_map_channel=5,
            song_row_cue_channel=7,
            track_input_channel=[1, 2, 3, 4, 5, 6, 7, 8],
            track_input_instrument=[10, 20, 30, 40, 50, 60, 70, 80],
            track_input_program_change=True, track_input_mode=2,
        )
        w = M8FileWriter()
        ms.write(w)
        ms2 = MIDISettings.from_reader(M8FileReader(w.to_bytes()))
        assert ms2 == ms


class TestMixerSettings:
    def test_roundtrip(self):
        ms = MixerSettings(master_volume=200, dj_filter=100)
        w = M8FileWriter()
        ms.write(w)
        ms2 = MixerSettings.from_reader(M8FileReader(w.to_bytes()))
        assert ms2.master_volume == 200
        assert ms2.dj_filter == 100

    def test_default_size(self):
        w = M8FileWriter()
        MixerSettings().write(w)
        # 2 + 8 + 3 + 2 + 1 + 2 + 2 + 2 + 3 + 3 + 4 = 32
        assert len(w.to_bytes()) == 32


class TestEffectsSettings:
    def test_roundtrip_v41(self):
        es = EffectsSettings()
        es.chorus.mod_depth = 42
        es.chorus.width = 180
        es.delay.filter_hp = 64
        es.delay.filter_lp = 200
        es.delay.feedback = 100
        es.reverb.filter_hp = 32
        es.reverb.filter_lp = 240
        es.reverb.width = 200
        w = M8FileWriter()
        es.write(w)
        es2 = EffectsSettings.from_reader(M8FileReader(w.to_bytes()), V41)
        assert es2.chorus.mod_depth == 42
        assert es2.chorus.width == 180
        assert es2.delay.filter_hp == 64
        assert es2.delay.filter_lp == 200
        assert es2.delay.feedback == 100
        assert es2.reverb.filter_hp == 32
        assert es2.reverb.filter_lp == 240
        assert es2.reverb.width == 200

    def test_write_size(self):
        w = M8FileWriter()
        EffectsSettings().write(w)
        # chorus: 7, delay: 8, reverb: 7 = 22
        assert len(w.to_bytes()) == 22

    def test_chorus_has_width(self):
        cs = ChorusSettings(mod_depth=10, mod_freq=20, width=0xFF, reverb_send=30)
        w = M8FileWriter()
        cs.write(w)
        cs2 = ChorusSettings.from_reader(M8FileReader(w.to_bytes()))
        assert cs2.width == 0xFF
        assert cs2.reverb_send == 30

    def test_delay_filter_always_present(self):
        ds = DelaySettings(filter_hp=0x40, filter_lp=0xC0, time_l=30, feedback=80)
        w = M8FileWriter()
        ds.write(w)
        ds2 = DelaySettings.from_reader(M8FileReader(w.to_bytes()))
        assert ds2.filter_hp == 0x40
        assert ds2.filter_lp == 0xC0
        assert ds2.time_l == 30
        assert ds2.feedback == 80

    def test_reverb_filter_always_present(self):
        rs = ReverbSettings(filter_hp=0x10, filter_lp=0xE0, size=0xFF, damping=0xC0)
        w = M8FileWriter()
        rs.write(w)
        rs2 = ReverbSettings.from_reader(M8FileReader(w.to_bytes()))
        assert rs2.filter_hp == 0x10
        assert rs2.filter_lp == 0xE0
        assert rs2.size == 0xFF
        assert rs2.damping == 0xC0


class TestMIDIMapping:
    def test_size(self):
        w = M8FileWriter()
        MIDIMapping().write(w)
        assert len(w.to_bytes()) == 9  # 7 data + 2 padding

    def test_roundtrip(self):
        m = MIDIMapping(channel=3, control_number=64, type=5, instr_index=2, max_value=127)
        w = M8FileWriter()
        m.write(w)
        m2 = MIDIMapping.from_reader(M8FileReader(w.to_bytes()))
        assert m2.channel == 3
        assert m2.control_number == 64
        assert m2.type == 5
        assert m2.instr_index == 2
        assert m2.max_value == 127

    def test_field_names(self):
        """Verify firmware-confirmed field names (not the old value/typ names)."""
        m = MIDIMapping()
        assert hasattr(m, "type")
        assert hasattr(m, "instr_index")
        assert not hasattr(m, "value")  # old name, was wrong
        assert not hasattr(m, "typ")    # old name, was wrong
