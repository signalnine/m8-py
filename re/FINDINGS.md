# M8 Firmware Reverse Engineering Findings

## Overview

Analysis of two firmware versions:
- **v4.0.2**: `M8_Headless_Firmware_4_0_2.hex` — initial structural RE
- **v6.5.1G**: `M8_V6_5_1G_HEADLESS.hex` — verification and v6 delta analysis

Platform: ARM Cortex-M7, Teensy 4.1 / NXP i.MX RT1062, flash base `0x60000000`.
Tools: Ghidra 11.3.1, radare2 5.9.8, custom Python scripts.

## Key Discovery: RAM-Mapped Strings

The firmware copies its `.data` section from flash to DTCM RAM (`0x20000000`)
at startup. All strings (M8VERSION, SONG SAVED, file extensions, etc.) are accessed at their
RAM addresses, NOT flash addresses. This is why initial Ghidra xref analysis found zero
references — the binary never contains direct pointers to the flash-resident string addresses.

**v4.0.2**: flash `.data` at `0x601988DC` → RAM `0x20000000`
**v6.5.1G**: flash `.data` shifted (larger binary), same RAM target

## File Layout — Firmware-Confirmed Structure

### Song File (.m8s) Overall Layout

Identical across v4.0.2 and v6.5.1G — all section offsets and element sizes unchanged.

| Section          | File Offset | Size (bytes) | Element Size | Count | v4 ✅ | v6 ✅ |
|------------------|-------------|-------------- |-------------|-------|-------|-------|
| M8VERSION header | `0x0000`    | 14           | 14          | 1     | ✅    | ✅    |
| Directory path   | `0x000E`    | 128          | 128         | 1     | ✅    | ✅    |
| Song metadata    | `0x008E`    | 96           | —           | —     | ✅    | ✅    |
| Groove           | `0x00EE`    | 512          | 16          | 32    | ✅    | ✅    |
| Song steps       | `0x02EE`    | 2048         | 8           | 256   | ✅    | ✅    |
| Phrases          | `0x0AEE`    | 36720        | 144         | 255   | ✅    | ✅    |
| Chains           | `0x9A5E`    | 8160         | 32          | 255   | ✅    | ✅    |
| Tables           | `0xBA3E`    | 32768        | 128         | 256   | ✅    | ✅    |
| Instruments      | `0x13A3E`   | 27520        | 215         | 128   | ✅    | ✅    |
| Padding          | `0x1A5BE`   | 3            | —           | —     | ✅    | ✅    |
| Effects settings | `0x1A5C1`   | 61           | 61          | 1     | ✅    | ✅    |
| MIDI mappings    | `0x1A5FE`   | 1152         | 9           | 128   | ✅    | ✅    |
| Scales           | `0x1AA7E`   | 736          | 46          | 16    | ✅    | ✅    |
| EQ (v4.0+)       | `0x1AD5E`   | varies       | 18          | 32/128| ✅    | ✅    |

### Firmware Bulk Read Strategy

Both v4 and v6 read the file identically:
1. Read 14-byte M8VERSION header and validate magic string
2. Parse 4-byte version number (`major<<24 | minor<<16 | patch<<8 | 0`)
3. Read 128-byte directory path
4. Bulk read `0x139B0` bytes (from file offset `0x8E` to `0x13A3E`) — metadata through tables
5. Read instruments individually (128 × 215 bytes)
6. Read remaining sections (effects, MIDI, scales, EQ)

| Property | v4.0.2 | v6.5.1G |
|----------|--------|---------|
| Song load function | `0x60034598` | `0x6004C8E0` |
| Bulk read size | `0x139B0` | `0x139B0` (unchanged) |
| Instrument seek base | `0x139B0 + (0xD7 * index)` | same |
| Header validator | `0x600348B4` | `0x6005B3A4` |

### Element Size Getter Functions

Vtable-style size getters, each a 4-byte `MOVS R0, #imm; BX LR`:

| v4.0.2 Address | v6.5.1G Address | Returns | Section |
|----------------|-----------------|---------|---------|
| `0x601798A8`   | `0x601A3ED8`    | 16      | Groove  |
| `0x601798AC`   | `0x601A3EDC`    | 32      | Chain   |
| `0x601798B0`   | `0x601A3EE0`    | 144     | Phrase  |
| `0x601798B4`   | `0x601A3EE4`    | 128     | Table   |
| `0x601798B8`   | `0x601A3EE8`    | 215     | Instrument |
| `0x601798BC`   | `0x601A3EEC`    | 46      | Scale   |
| —              | `0x601A3EF0`    | **18**  | **EQ**  |

The 7th getter (EQ, 18 bytes) is new in v6. Confirmed: 3 EQ bands × 6 bytes = 18.
Matches the Rust crate's `Equ::V4_SIZE = 3 * EqBand::V4_SIZE = 3 * 6 = 18`.

## Song Metadata (96 bytes at 0x008E)

### MixerSettings Layout (32 bytes at file offset 0x00CE)

Verified against v6.5.1G firmware UI strings and real `.m8s` files.

```
+0x00: master_volume        (u8)
+0x01: master_limit         (u8, limiter level)
+0x02: track_volume[0..7]   (8 × u8)
+0x0A: chorus_volume        (u8, MFX send level in v6+)
+0x0B: delay_volume         (u8)
+0x0C: reverb_volume        (u8)
+0x0D: analog_input_volume_l (u8)
+0x0E: analog_input_volume_r (u8, 0xFF = stereo mode)
+0x0F: usb_input_volume     (u8)
+0x10: analog_input_l_mfx   (u8)  ← grouped by CHANNEL, not effect
+0x11: analog_input_l_delay (u8)
+0x12: analog_input_l_reverb (u8)
+0x13: analog_input_r_mfx   (u8)
+0x14: analog_input_r_delay (u8)
+0x15: analog_input_r_reverb (u8)
+0x16: usb_input_mfx        (u8)
+0x17: usb_input_delay      (u8)
+0x18: usb_input_reverb     (u8)
+0x19: dj_filter            (u8)
+0x1A: dj_peak              (u8, DJ filter resonance)
+0x1B: dj_filter_type       (u8)
+0x1C: limiter_attack       (u8, v6.0+)
+0x1D: limiter_release      (u8, v6.0+)
+0x1E: limiter_soft_clip    (u8, v6.0+)
+0x1F: ott_level            (u8, v6.1+)
```

Pre-v6.0 files: bytes 0x1C-0x1F are padding (zeroes).
Ends exactly at 0x00EE where grooves begin.

**Critical note on byte grouping**: Analog input sends are grouped by **channel** (L then R),
not by effect type. The Rust crate reads `InputMixerSettings::from_reader()` per-channel.
An earlier m8py bug grouped by effect type (chorus[L,R], delay[L,R], reverb[L,R]) which
crossed channel boundaries — fixed.

### DJ Filter Type Values (from firmware strings)

```
0: LOWPASS:HIGHPASS
1: LOWPASS:BANDSTOP
2: BANDSTOP:HIGHPASS
```

### Limiter Format Strings (from firmware)

```
"LIM ATTACK:%3.1F MS"
"LIM RELEASE:%4.1F MS"
"LIM RELEASE:AUTO"
```

## Effects Settings (61 bytes at 0x1A5C1)

### Byte Layout (26 data + 35 padding)

```
+0x00: chorus_mod_depth   (u8, default 0x40)
+0x01: chorus_mod_freq    (u8, default 0x80)
+0x02: chorus_width       (u8, default 0xFF)
+0x03: chorus_reverb_send (u8)
+0x04: unused[3]          (3 bytes padding)
+0x07: delay_filter_hp    (u8, vestigial in v4+, replaced by EQ)
+0x08: delay_filter_lp    (u8, vestigial in v4+)
+0x09: delay_time_l       (u8, default 0x30)
+0x0A: delay_time_r       (u8, default 0x30)
+0x0B: delay_feedback     (u8, default 0x80)
+0x0C: delay_width        (u8, default 0xFF)
+0x0D: delay_reverb_send  (u8)
+0x0E: unused[1]          (1 byte padding)
+0x0F: reverb_filter_hp   (u8, vestigial, default 0x10)
+0x10: reverb_filter_lp   (u8, vestigial, default 0xE0)
+0x11: reverb_size        (u8, default 0xFF)
+0x12: reverb_damping     (u8, default 0xC0, UI: "DECAY")
+0x13: reverb_mod_depth   (u8, default 0x10)
+0x14: reverb_mod_freq    (u8, default 0xFF)
+0x15: reverb_width       (u8, default 0xFF)
+0x16: reverb_shimmer     (u8, v6.1+ only)
+0x17: ott_time           (u8, v6.1+ only, default 0x80)
+0x18: ott_color          (u8, v6.1+ only, default 0x80)
+0x19: mfx_kind           (u8, v6.1+ only: 0=Chorus, 1=Phaser, 2=Flanger)
+0x1A: padding[35]        (uninitialized junk, never written by firmware)
```

Pre-v6.1 files: bytes 0x16-0x19 are part of the padding (zero or junk).
Section size is always 61 bytes regardless of version.

### Fields NOT in the file format

- **Microtime** (`MTT`): appears in firmware UI strings but is NOT stored in the effects
  section. Likely stored in the song header's 18-byte area at offset 0xBC-0xCE, or runtime-only.
- **Reverb Freeze** (`XRZ`): appears in MIDI CC mapping name table but is runtime-only.

## Version Encoding and Migration

### Version format: `0xMMSS`

The 4-byte version field encodes as `major<<8 | sub`, stored as a 32-bit word.

| File Format Version | Hex Code | Firmware Version |
|---------------------|----------|-----------------|
| 1.4                 | `0x0140` | 1.x             |
| 2.5                 | `0x0250` | 2.x             |
| 2.6                 | `0x0260` | 2.x             |
| 3.0                 | `0x0300` | 3.x             |
| 3.1                 | `0x0310` | 3.x             |
| 4.0                 | `0x0400` | 4.x / 5.x       |
| 4.2                 | `0x0420` | 5.x             |
| 6.0                 | `0x0600` | 6.0.x           |
| 6.1                 | `0x0610` | 6.2.x+          |
| 6.5                 | `0x0650` | 6.5.x           |

### v6.5.1G Migration Chain (at 0x6005A3AC)

The v6 firmware applies sequential upgrades for any historical format:

```
0x0140 → 0x0250 → 0x0260 → 0x0300 → 0x0310 → 0x0400 → 0x0420 → 0x0600 → 0x0610 → 0x0650
```

Each step has a dedicated upgrade function (addresses `0x6005915A` through `0x6005A38C`).
If `version == 0x0650`, the native read path runs directly (no migration needed).
If `version > 0x0650`, the file is rejected.

### v6 Song Load Function (0x6004C8E0)

The v6 load function at `0x6004C9F4` routes by version:
- `version == 0x0650`: native bulk read path at `0x6004CAE8`
- `version < 0x0650`: compatibility path via migration chain at `0x6005A3AC`
- `version > 0x0650`: rejected

Single-instrument loader at `0x6004C554`: seeks to `0x139B0 + (0xD7 * index)`, reads 215 bytes.

## Identified Functions

### v4.0.2

#### Save Pipeline

| Address        | Size | Function                      |
|----------------|------|-------------------------------|
| `0x60027688`   | 96   | `song_save_to_file()` entry   |
| `0x600272FC`   | 890  | `song_serialize_write()` core |
| `0x600357B0`   | 2038 | `save_song_with_samples()`    |
| `0x600349DC`   | 520  | `file_copy_with_progress()`   |

#### Load Pipeline

| Address        | Size | Function                          |
|----------------|------|-----------------------------------|
| `0x60034598`   | —    | Song load main (version dispatch) |
| `0x600348B4`   | —    | Song load alternate entry         |
| `0x60034C18`   | —    | Song save-with-verify             |
| `0x60034D48`   | —    | Incremental verify/re-save        |
| `0x60034ED8`   | 878  | Version migration dispatcher      |

#### Version Migration Chain (v4)

| Function       | Size | Purpose                                           |
|----------------|------|---------------------------------------------------|
| `0x6003384E`   | 76   | Remap FX command bytes (insert new enum values)   |
| `0x600337D8`   | 30   | WAVSYNTH filter type bump (offset 0x17, >4 → +1) |
| `0x6003375E`   | 96   | MACROSYNTH shape remap (offset 0x12, >30 → +1)   |
| `0x60033A90`   | 300  | SAMPLER new fields init + field shift migration   |
| `0x60033D58`   | 108  | SAMPLER memmove(+0x14, +0x12, 0x18)              |
| `0x60033F28`   | 180  | WAVSYNTH filter +2, flag byte at 0x0D, FX mods   |

### v6.5.1G

| Address        | Function                              |
|----------------|---------------------------------------|
| `0x6004C8E0`   | Song load main (version dispatch)     |
| `0x6004C554`   | Single-instrument loader              |
| `0x6005A3AC`   | Version migration dispatcher          |
| `0x6005915A`   | Oldest-format deserializer (<0x0140)  |
| `0x6005B3A4`   | M8VERSION header validator            |
| `0x6017C7E0`   | FX command name string table (78 entries) |

### Library / System Functions (v4.0.2)

| Veneer Address | Function    |
|----------------|-------------|
| `0x6003B770`   | `f_write`   |
| `0x6003BE20`   | `f_read`    |
| `0x6003B678`   | `f_open`    |
| `0x6003BEE8`   | `f_close`   |
| `0x6003C238`   | `f_lseek`   |
| `0x6003BA10`   | `memcpy`    |
| `0x6003B650`   | `memset`    |

Note: Firmware uses **SdFat** (Bill Greiman's C++ SD library), not stock FatFS.
File open flags use `0x4202` (SdFat's `O_WRITE | O_CREAT | O_TRUNC`).

## FX Command Names — Firmware Verified

The FX command name string table at flash `0x6017C7E0` (v6.5.1G) contains 78 null-terminated
3-character entries. All 78 match the `COMMANDS_V6_2` table in `m8py/display/commands.py` exactly.

## Resolved Discrepancies

### 1. MIDI Mapping Size: 9 bytes (7 data + 2 padding)

**Firmware**: Section spans `0x1A5FE` to `0x1AA7E` = 1152 bytes / 128 entries = **9 bytes each**.
**Root cause**: Entry stride is 9 bytes but only 7 bytes carry data. Bytes 7-8 are always zero.

**Evidence chain:**
1. `FUN_60038c44` (MIDI mapping creation) writes exactly 7 bytes at offsets 0-6
2. All 7 callers of `thunk_EXT_FUN_0002264a` only access offsets 0-6
3. Empirical analysis of `.m8s` files confirms clean 7-byte data with trailing zeros
4. All community libraries (m8-js, m8-files, m8-file-parser) read only 7 bytes
5. No firmware size getter exists for MIDI mapping

**Confirmed entry layout (9 bytes):**
```
Byte 0: channel        (0 = empty/inactive)
Byte 1: control_number (MIDI CC number)
Byte 2: type           (mapping type: 0x04-0x07=I, 0x08-0x0B=X, 0x0C-0x0F=M)
Byte 3: instr_index    (target instrument index, 0-127)
Byte 4: param_index    (target parameter index within instrument)
Byte 5: min_value      (mapping range minimum)
Byte 6: max_value      (mapping range maximum)
Byte 7: padding        (always 0)
Byte 8: padding        (always 0)
```

**Status**: m8py fixed — reads 7 data + skips 2 padding, writes 7 data + 2 zero bytes.

### 2. Scale Entry Size: 46 bytes (not 42)

**Firmware**: Size getter returns 46 (both v4 and v6). Section: 736 bytes / 16 = 46.
**Root cause**: Missing `float32` tuning field at offset +0x2A (4 bytes).

**Confirmed layout (46 bytes):**
```
+0x00: note_enable    (u16 LE, default 0xFFFF)
+0x02: note_offsets   (12 × {semitone: u8, cents: u8} = 24 bytes)
+0x1A: name           (16-byte string, 0xFF-filled when empty)
+0x2A: tuning         (float32 LE, reference pitch offset, default 0.0)
```

**Status**: m8py fixed — Scale reads/writes 46 bytes with `tuning: float` field.

### 3. Effects Settings: 22 bytes of data (v4), 26 bytes (v6.1+)

See Effects Settings section above for full byte map.

**Status**: m8py fixed — chorus has `width`, delay/reverb always read filter bytes,
v6.1+ reads shimmer/ott/mfx_kind.

### 4. Analog Input Sends: Channel-Grouped, Not Effect-Grouped

**Firmware**: Reads analog sends as L.mfx, L.delay, L.reverb, R.mfx, R.delay, R.reverb.
**Old m8py**: Read as chorus[L,R], delay[L,R], reverb[L,R] — crossed channel boundaries.
**Evidence**: Verified against Rust m8-file-parser `InputMixerSettings::from_reader()` and
real `.m8s` files with sequential test values (DGLTMX.m8s).

**Status**: m8py fixed — uses `analog_input_l_chorus/delay/reverb` and
`analog_input_r_chorus/delay/reverb` fields, grouped by channel.

### 5. Instrument Kind Numbering

**Firmware migration code** refers to instrument types by index:
- 0 = WAVSYNTH, 1 = MACROSYNTH, 2 = SAMPLER, 3 = MIDIOUT, 4 = FMSYNTH

**m8py constants**: identical. ✅

Note: The v4 migration function at `0x60033A90` checks `uVar9 == 3` and initializes
sample-path-like fields, which appears to conflict (type 3 = MIDIOUT). This is likely a
format-version migration edge case, not a current-format issue.

## Key RAM Structures

| Property | v4.0.2 | v6.5.1G |
|----------|--------|---------|
| Song data buffer | `0x2025AE2C` (OCRAM2) | `0x200013A4` |
| Mixer in RAM | — | `0x200013E4` (+0x40 from song base) |
| Song struct size | `0x1AF58` | `0x1B638` (+1760 bytes) |
| FatFS file handle | `0x20016458` | — |
| M8VERSION string | `0x2000130C` (DTCM) | `0x6017F6E0` (flash ref) |
| Instruments base | `0x200127B8` | — |

The song struct grew 1760 bytes in RAM to accommodate runtime state for new features
(OTT, DJ filter, limiter parameters), but this does not affect the file format size.

## Confirmed m8py Values

All values confirmed correct by both v4.0.2 and v6.5.1G firmware analysis:

- `HEADER_MAGIC = b"M8VERSION\x00"` ✅
- `HEADER_SIZE = 14` ✅
- `INSTRUMENT_SIZE = 215` ✅
- `N_INSTRUMENTS = 128` ✅
- `N_PHRASES = 255` ✅
- `N_CHAINS = 255` ✅
- `N_TABLES = 256` ✅
- `N_GROOVES = 32` ✅
- `N_SCALES = 16` ✅
- `N_MIDI_MAPPINGS = 128` ✅
- `STEPS_PER_PHRASE = 16` ✅
- `STEPS_PER_CHAIN = 16` ✅
- `STEPS_PER_TABLE = 16` ✅
- `STEPS_PER_GROOVE = 16` ✅
- All section offsets (identical v4 through v6) ✅
- PhraseStep = 9 bytes (note + velocity + instrument + 3×FX) ✅
- ChainStep = 2 bytes (phrase + transpose) ✅
- TableStep = 8 bytes (transpose + velocity + 3×FX) ✅
- FX = 2 bytes (command + value) ✅
- SongStep = 8 bytes (8 track chain references) ✅
- Groove = 16 bytes (16 step ticks) ✅
- EQ entry = 18 bytes (3 bands × 6 bytes) ✅
- Modulator position at instrument offset 63 ✅
- 4 modulators per instrument ✅
- Sample path at instrument tail (offset 87, 128 bytes) ✅
- Bulk read size `0x139B0` (80,304 bytes) ✅
