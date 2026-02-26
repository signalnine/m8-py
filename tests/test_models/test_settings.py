from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.version import M8Version
from m8py.models.settings import MIDISettings, MixerSettings, EffectsSettings
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
        es.delay.feedback = 100
        es.reverb.width = 200
        w = M8FileWriter()
        es.write(w)
        es2 = EffectsSettings.from_reader(M8FileReader(w.to_bytes()), V41)
        assert es2.chorus.mod_depth == 42
        assert es2.delay.feedback == 100
        assert es2.reverb.width == 200

    def test_write_size_v4(self):
        w = M8FileWriter()
        EffectsSettings().write(w)
        # chorus: 6, delay: 6, reverb: 5 = 17
        assert len(w.to_bytes()) == 17


class TestMIDIMapping:
    def test_size(self):
        w = M8FileWriter()
        MIDIMapping().write(w)
        assert len(w.to_bytes()) == 7

    def test_roundtrip(self):
        m = MIDIMapping(channel=3, control_number=64, max_value=127)
        w = M8FileWriter()
        m.write(w)
        m2 = MIDIMapping.from_reader(M8FileReader(w.to_bytes()))
        assert m2.channel == 3
        assert m2.max_value == 127
