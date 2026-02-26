from __future__ import annotations
from dataclasses import dataclass, field
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter

@dataclass
class RGB:
    r: int = 0
    g: int = 0
    b: int = 0

    @staticmethod
    def from_reader(reader: M8FileReader) -> RGB:
        return RGB(r=reader.read(), g=reader.read(), b=reader.read())

    def write(self, writer: M8FileWriter) -> None:
        writer.write(self.r)
        writer.write(self.g)
        writer.write(self.b)


@dataclass
class Theme:
    background: RGB = field(default_factory=RGB)
    text_empty: RGB = field(default_factory=RGB)
    text_info: RGB = field(default_factory=RGB)
    text_default: RGB = field(default_factory=RGB)
    text_value: RGB = field(default_factory=RGB)
    text_title: RGB = field(default_factory=RGB)
    play_marker: RGB = field(default_factory=RGB)
    cursor: RGB = field(default_factory=RGB)
    selection: RGB = field(default_factory=RGB)
    scope_slider: RGB = field(default_factory=RGB)
    meter_low: RGB = field(default_factory=RGB)
    meter_mid: RGB = field(default_factory=RGB)
    meter_peak: RGB = field(default_factory=RGB)

    @staticmethod
    def from_reader(reader: M8FileReader) -> Theme:
        return Theme(
            background=RGB.from_reader(reader), text_empty=RGB.from_reader(reader),
            text_info=RGB.from_reader(reader), text_default=RGB.from_reader(reader),
            text_value=RGB.from_reader(reader), text_title=RGB.from_reader(reader),
            play_marker=RGB.from_reader(reader), cursor=RGB.from_reader(reader),
            selection=RGB.from_reader(reader), scope_slider=RGB.from_reader(reader),
            meter_low=RGB.from_reader(reader), meter_mid=RGB.from_reader(reader),
            meter_peak=RGB.from_reader(reader),
        )

    def write(self, writer: M8FileWriter) -> None:
        for color in [
            self.background, self.text_empty, self.text_info,
            self.text_default, self.text_value, self.text_title,
            self.play_marker, self.cursor, self.selection,
            self.scope_slider, self.meter_low, self.meter_mid,
            self.meter_peak,
        ]:
            color.write(writer)
