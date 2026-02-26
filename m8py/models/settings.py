from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.models.version import M8Version


@dataclass
class MIDISettings:
    receive_sync: bool = False
    receive_transport: int = 0
    send_sync: bool = False
    send_transport: int = 0
    record_note_channel: int = 0
    record_note_velocity: bool = False
    record_note_delay_kill_commands: int = 0
    control_map_channel: int = 0
    song_row_cue_channel: int = 0
    track_input_channel: list[int] = field(default_factory=lambda: [0] * 8)
    track_input_instrument: list[int] = field(default_factory=lambda: [0] * 8)
    track_input_program_change: bool = False
    track_input_mode: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> MIDISettings:
        return MIDISettings(
            receive_sync=reader.read_bool(),
            receive_transport=reader.read(),
            send_sync=reader.read_bool(),
            send_transport=reader.read(),
            record_note_channel=reader.read(),
            record_note_velocity=reader.read_bool(),
            record_note_delay_kill_commands=reader.read(),
            control_map_channel=reader.read(),
            song_row_cue_channel=reader.read(),
            track_input_channel=[reader.read() for _ in range(8)],
            track_input_instrument=[reader.read() for _ in range(8)],
            track_input_program_change=reader.read_bool(),
            track_input_mode=reader.read(),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write_bool(self.receive_sync)
        writer.write(self.receive_transport)
        writer.write_bool(self.send_sync)
        writer.write(self.send_transport)
        writer.write(self.record_note_channel)
        writer.write_bool(self.record_note_velocity)
        writer.write(self.record_note_delay_kill_commands)
        writer.write(self.control_map_channel)
        writer.write(self.song_row_cue_channel)
        for ch in self.track_input_channel:
            writer.write(ch)
        for inst in self.track_input_instrument:
            writer.write(inst)
        writer.write_bool(self.track_input_program_change)
        writer.write(self.track_input_mode)


@dataclass
class MixerSettings:
    master_volume: int = 0
    master_limit: int = 0
    track_volume: list[int] = field(default_factory=lambda: [0] * 8)
    chorus_volume: int = 0
    delay_volume: int = 0
    reverb_volume: int = 0
    analog_input_volume: list[int] = field(default_factory=lambda: [0, 0])
    usb_input_volume: int = 0
    analog_input_chorus: list[int] = field(default_factory=lambda: [0, 0])
    analog_input_delay: list[int] = field(default_factory=lambda: [0, 0])
    analog_input_reverb: list[int] = field(default_factory=lambda: [0, 0])
    usb_input_chorus: int = 0
    usb_input_delay: int = 0
    usb_input_reverb: int = 0
    dj_filter: int = 0
    dj_peak: int = 0
    dj_filter_type: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> MixerSettings:
        ms = MixerSettings(
            master_volume=reader.read(),
            master_limit=reader.read(),
            track_volume=[reader.read() for _ in range(8)],
            chorus_volume=reader.read(),
            delay_volume=reader.read(),
            reverb_volume=reader.read(),
            analog_input_volume=[reader.read(), reader.read()],
            usb_input_volume=reader.read(),
            analog_input_chorus=[reader.read(), reader.read()],
            analog_input_delay=[reader.read(), reader.read()],
            analog_input_reverb=[reader.read(), reader.read()],
            usb_input_chorus=reader.read(),
            usb_input_delay=reader.read(),
            usb_input_reverb=reader.read(),
            dj_filter=reader.read(),
            dj_peak=reader.read(),
            dj_filter_type=reader.read(),
        )
        reader.skip(4)  # padding
        return ms

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.master_volume)
        writer.write(self.master_limit)
        for v in self.track_volume:
            writer.write(v)
        writer.write(self.chorus_volume)
        writer.write(self.delay_volume)
        writer.write(self.reverb_volume)
        for v in self.analog_input_volume:
            writer.write(v)
        writer.write(self.usb_input_volume)
        for v in self.analog_input_chorus:
            writer.write(v)
        for v in self.analog_input_delay:
            writer.write(v)
        for v in self.analog_input_reverb:
            writer.write(v)
        writer.write(self.usb_input_chorus)
        writer.write(self.usb_input_delay)
        writer.write(self.usb_input_reverb)
        writer.write(self.dj_filter)
        writer.write(self.dj_peak)
        writer.write(self.dj_filter_type)
        writer.pad(4)


@dataclass
class ChorusSettings:
    mod_depth: int = 0
    mod_freq: int = 0
    width: int = 0xFF
    reverb_send: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> ChorusSettings:
        cs = ChorusSettings(
            mod_depth=reader.read(),
            mod_freq=reader.read(),
            width=reader.read(),
            reverb_send=reader.read(),
        )
        reader.skip(3)  # unused
        return cs

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.mod_depth)
        writer.write(self.mod_freq)
        writer.write(self.width)
        writer.write(self.reverb_send)
        writer.pad(3)


@dataclass
class DelaySettings:
    filter_hp: int = 0x80
    filter_lp: int = 0x80
    time_l: int = 0
    time_r: int = 0
    feedback: int = 0
    width: int = 0
    reverb_send: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> DelaySettings:
        ds = DelaySettings(
            filter_hp=reader.read(),
            filter_lp=reader.read(),
            time_l=reader.read(),
            time_r=reader.read(),
            feedback=reader.read(),
            width=reader.read(),
            reverb_send=reader.read(),
        )
        reader.skip(1)  # unused
        return ds

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.filter_hp)
        writer.write(self.filter_lp)
        writer.write(self.time_l)
        writer.write(self.time_r)
        writer.write(self.feedback)
        writer.write(self.width)
        writer.write(self.reverb_send)
        writer.pad(1)


@dataclass
class ReverbSettings:
    filter_hp: int = 0x80
    filter_lp: int = 0x80
    size: int = 0
    damping: int = 0
    mod_depth: int = 0
    mod_freq: int = 0
    width: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> ReverbSettings:
        return ReverbSettings(
            filter_hp=reader.read(),
            filter_lp=reader.read(),
            size=reader.read(),
            damping=reader.read(),
            mod_depth=reader.read(),
            mod_freq=reader.read(),
            width=reader.read(),
        )

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.filter_hp)
        writer.write(self.filter_lp)
        writer.write(self.size)
        writer.write(self.damping)
        writer.write(self.mod_depth)
        writer.write(self.mod_freq)
        writer.write(self.width)


@dataclass
class EffectsSettings:
    chorus: ChorusSettings = field(default_factory=ChorusSettings)
    delay: DelaySettings = field(default_factory=DelaySettings)
    reverb: ReverbSettings = field(default_factory=ReverbSettings)

    @staticmethod
    def from_reader(reader: M8FileReader, version: M8Version | None = None) -> EffectsSettings:
        return EffectsSettings(
            chorus=ChorusSettings.from_reader(reader),
            delay=DelaySettings.from_reader(reader),
            reverb=ReverbSettings.from_reader(reader),
        )

    def write(self, writer: M8FileWriter) -> None:
        self.chorus.write(writer)
        self.delay.write(writer)
        self.reverb.write(writer)
