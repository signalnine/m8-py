from __future__ import annotations
from dataclasses import dataclass
from m8py.format.reader import M8FileReader
from m8py.format.writer import M8FileWriter
from m8py.format.errors import M8ParseError
from m8py.format.constants import ModulatorType

MOD_SIZE = 6


@dataclass
class AHDEnv:
    dest: int = 0
    amount: int = 0
    attack: int = 0
    hold: int = 0
    decay: int = 0


@dataclass
class ADSREnv:
    dest: int = 0
    amount: int = 0
    attack: int = 0
    decay: int = 0
    sustain: int = 0
    release: int = 0


@dataclass
class DrumEnv:
    dest: int = 0
    amount: int = 0
    peak: int = 0
    body: int = 0
    decay: int = 0


@dataclass
class LFOMod:
    dest: int = 0
    amount: int = 0
    shape: int = 0
    trigger_mode: int = 0
    freq: int = 0
    retrigger: int = 0


@dataclass
class TrigEnv:
    dest: int = 0
    amount: int = 0
    attack: int = 0
    hold: int = 0
    decay: int = 0
    src: int = 0


@dataclass
class TrackingEnv:
    dest: int = 0
    amount: int = 0
    src: int = 0
    lval: int = 0
    hval: int = 0


Modulator = AHDEnv | ADSREnv | DrumEnv | LFOMod | TrigEnv | TrackingEnv


def empty_modulator() -> AHDEnv:
    return AHDEnv()


def mod_from_reader(reader: M8FileReader) -> Modulator:
    start = reader.position()
    first_byte = reader.read()
    ty = (first_byte >> 4) & 0x0F
    dest = first_byte & 0x0F

    if ty == ModulatorType.AHD_ENV:
        mod = AHDEnv(dest=dest, amount=reader.read(), attack=reader.read(),
                     hold=reader.read(), decay=reader.read())
    elif ty == ModulatorType.ADSR_ENV:
        mod = ADSREnv(dest=dest, amount=reader.read(), attack=reader.read(),
                      decay=reader.read(), sustain=reader.read(), release=reader.read())
    elif ty == ModulatorType.DRUM_ENV:
        mod = DrumEnv(dest=dest, amount=reader.read(), peak=reader.read(),
                      body=reader.read(), decay=reader.read())
    elif ty == ModulatorType.LFO:
        mod = LFOMod(dest=dest, amount=reader.read(), shape=reader.read(),
                     trigger_mode=reader.read(), freq=reader.read(), retrigger=reader.read())
    elif ty == ModulatorType.TRIG_ENV:
        mod = TrigEnv(dest=dest, amount=reader.read(), attack=reader.read(),
                      hold=reader.read(), decay=reader.read(), src=reader.read())
    elif ty == ModulatorType.TRACKING_ENV:
        mod = TrackingEnv(dest=dest, amount=reader.read(), src=reader.read(),
                          lval=reader.read(), hval=reader.read())
    else:
        raise M8ParseError(f"unknown modulator type {ty} at offset {start}")

    reader.seek(start + MOD_SIZE)
    return mod


def mod_write(mod: Modulator, writer: M8FileWriter) -> None:
    start = writer.position()
    if isinstance(mod, AHDEnv):
        writer.write((ModulatorType.AHD_ENV << 4) | mod.dest)
        writer.write(mod.amount); writer.write(mod.attack)
        writer.write(mod.hold); writer.write(mod.decay)
    elif isinstance(mod, ADSREnv):
        writer.write((ModulatorType.ADSR_ENV << 4) | mod.dest)
        writer.write(mod.amount); writer.write(mod.attack)
        writer.write(mod.decay); writer.write(mod.sustain); writer.write(mod.release)
    elif isinstance(mod, DrumEnv):
        writer.write((ModulatorType.DRUM_ENV << 4) | mod.dest)
        writer.write(mod.amount); writer.write(mod.peak)
        writer.write(mod.body); writer.write(mod.decay)
    elif isinstance(mod, LFOMod):
        writer.write((ModulatorType.LFO << 4) | mod.dest)
        writer.write(mod.amount); writer.write(mod.shape)
        writer.write(mod.trigger_mode); writer.write(mod.freq); writer.write(mod.retrigger)
    elif isinstance(mod, TrigEnv):
        writer.write((ModulatorType.TRIG_ENV << 4) | mod.dest)
        writer.write(mod.amount); writer.write(mod.attack)
        writer.write(mod.hold); writer.write(mod.decay); writer.write(mod.src)
    elif isinstance(mod, TrackingEnv):
        writer.write((ModulatorType.TRACKING_ENV << 4) | mod.dest)
        writer.write(mod.amount); writer.write(mod.src)
        writer.write(mod.lval); writer.write(mod.hval)

    # Pad to exactly 6 bytes
    written = writer.position() - start
    if written < MOD_SIZE:
        writer.pad(MOD_SIZE - written)
