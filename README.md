# m8py

A Python library for reading, writing, and composing [Dirtywave M8](https://dirtywave.com/) tracker files.

m8py parses every M8 binary format -- songs (`.m8s`), instruments (`.m8i`), themes (`.m8t`), and scales (`.m8n`) -- across firmware versions 1.x through 4.1. Load a file, save it, and get the same bytes back. Zero runtime dependencies.

## Install

```bash
pip install m8py
```

Requires Python 3.11+.

## Quick Start

### Load and inspect a file

```python
import m8py

song = m8py.load_song("my_track.m8s")
print(song.name, song.tempo)

for i, inst in enumerate(song.instruments):
    if not isinstance(inst, m8py.EmptyInstrument):
        print(f"  [{i}] {type(inst).__name__}: {inst.common.name}")
```

### Load and modify an instrument

```python
inst = m8py.load_instrument("lead.m8i")
inst.common.filter_cutoff = 200
inst.common.mixer_reverb = 40
m8py.save(inst, "lead_modified.m8i")
```

### Compose a song from scratch

The declarative API builds a song from track definitions:

```python
from m8py import compose, TrackDef, WavSynth, MacroSynth, SynthCommon, save

bass = MacroSynth(common=SynthCommon(name="BASS", volume=200), shape=10)
lead = WavSynth(common=SynthCommon(name="LEAD", volume=180), shape=3)

song = compose(
    tracks=[
        TrackDef(instrument=bass, pattern="C3 C3 . . E3 E3 . . G3 G3 . . C4 . . .", track=0),
        TrackDef(instrument=lead, pattern="C5 E5 G5 C6", track=1),
    ],
    name="DEMO",
    tempo=140.0,
)

save(song, "DEMO.m8s")
```

### Build with finer control

`SongBuilder` gives direct access to phrases, chains, and the song grid:

```python
from m8py import SongBuilder, FMSynth, SynthCommon

synth = FMSynth(common=SynthCommon(name="FM_PAD"), algo=7)

song = (
    SongBuilder(name="PADTRACK", tempo=100)
    .add_instrument(synth)
    .add_phrase("C4 E4 G4 B4 | C5 . . . | G4 E4 C4 . | . . . OFF")
    .add_chain([0])
    .set_song_step(0, track=0, chain=0)
    .build()
)
```

### Export to SD card

```python
from m8py import export_to_sdcard

result = export_to_sdcard(
    song,
    sdcard_root="/media/M8",
    sample_sources={
        "/Samples/kick.wav": "./samples/kick.wav",
        "/Samples/snare.wav": "./samples/snare.wav",
    },
)
print(f"Wrote {result.song_path}")
print(f"Copied {len(result.sample_files)} samples")
```

## API Reference

### I/O

| Function | Description |
|---|---|
| `load(path)` | Load any M8 file; detects type by extension |
| `load_song(path)` | Load a `.m8s` song file |
| `load_instrument(path)` | Load a `.m8i` instrument file |
| `load_theme(path)` | Load a `.m8t` theme file |
| `load_scale(path)` | Load a `.m8n` scale file |
| `save(obj, path)` | Save any M8 object to a file |
| `validate(obj)` | Check an M8 object and return a list of issues |

### Instruments

Every instrument serializes to exactly 215 bytes. Each carries four modulator slots and shared mixer/filter controls through `SynthCommon`.

| Type | Kind | Engine Parameters |
|---|---|---|
| `WavSynth` | 0x00 | shape, size, mult, warp, scan |
| `MacroSynth` | 0x01 | shape, timbre, color, degrade, redux |
| `Sampler` | 0x02 | play_mode, slice, start, loop_start, length, degrade, sample_path |
| `MIDIOut` | 0x03 | port, channel, bank_select, program_change, 10 control changes |
| `FMSynth` | 0x04 | algo, 4 operators (shape/ratio/level/feedback/mod), mod1-mod4 |
| `HyperSynth` | 0x05 | default_chord, scale, shift, swarm, width, subosc, 16 custom chords |
| `External` | 0x06 | input, port, channel, bank, program, 4 CC pairs |
| `EmptyInstrument` | 0xFF | placeholder for an unused slot |

**SynthCommon fields** (shared by all except MIDIOut): name, transp_eq, table_tick, volume, pitch, fine_tune, filter_type, filter_cutoff, filter_res, amp, limit, mixer_pan, mixer_dry, mixer_chorus, mixer_delay, mixer_reverb.

### Modulators

Each instrument holds four modulator slots. m8py supports six types:

| Type | Parameters |
|---|---|
| `AHDEnv` | dest, amount, attack, hold, decay |
| `ADSREnv` | dest, amount, attack, decay, sustain, release |
| `DrumEnv` | dest, amount, peak, body, decay |
| `LFOMod` | dest, amount, shape, trigger_mode, freq, retrigger |
| `TrigEnv` | dest, amount, attack, hold, decay, src |
| `TrackingEnv` | dest, amount, src, lval, hval |

### Song Structure

A Song contains:

- **256 song rows**, each with 8 track slots pointing to chains
- **255 chains**, each a sequence of up to 16 phrase references with transpose
- **255 phrases**, each a sequence of 16 steps (note, velocity, instrument, 3 FX columns)
- **128 instruments**
- **256 tables** (16 steps of transpose, velocity, and FX)
- **32 grooves** (16-step timing patterns)
- **16 scales** (custom tunings with per-note cent offsets)

### Pattern Notation

`compose()` and `SongBuilder.add_phrase()` accept pattern strings:

| Syntax | Meaning |
|---|---|
| `C4`, `F#3`, `Bb5` | Note with octave |
| `---` or `.` | Empty step |
| `OFF` | Note off |
| `C4@7F` | Note with velocity (hex) |
| `\|` | Bar separator (cosmetic only) |

Patterns longer than 16 steps split across multiple phrases and chain together automatically.

### Version Handling

m8py reads files from every firmware version (1.x through 4.1). The `M8Version` object exposes capability flags:

```python
song = m8py.load_song("old_track.m8s")
print(song.version)           # M8Version(3, 0, 0)
print(song.version.caps)      # VersionCapabilities(has_eq=False, ...)
print(song.version.at_least(3, 0))  # True
```

## Testing

```bash
pip install -e ".[dev]"
pytest
```

The test suite includes 540 tests:

- Round-trip tests for every model type
- Byte-exact fidelity tests against 281 community instrument presets
- Property-based tests (Hypothesis)
- Fuzz tests with random binary data

## License

MIT
