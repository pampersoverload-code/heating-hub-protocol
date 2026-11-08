# Application framing and command catalogue

All offsets in this repository are **zero based**. Multi-byte temperature,
length and program-time values below are **big endian**. Do not confuse a
human's "byte 23" with offset 23: that phrase refers to offset 22.

## Application frame

```text
offset      0  1   2  3   4  5   6 ... N-2      N-1
            7E 2B  kind   length  payload        sum8
                         BE16
total N = BE16(frame[4:6]) + 7
sum8 = sum(frame[0:N-1]) & 0xFF
```

The length counts bytes from offset 6 to the last payload byte, excluding the
checksum. A 44-byte status has `00 25` (37), a 35-byte reply has `00 1C` (28).
The checksum is an additive byte, **not a CRC**. It does not include RF preamble,
sync or the outer length byte. Changing identifiers, setpoint, time or payload
requires recomputing it. An additive sum can miss compensating corruptions;
also validate command shape, identity and field plausibility.

`7E 2B` is an application marker, not the RF sync word `2D D4`. No UART-style
start/stop bits are inserted around the RF bytes. No byte escaping has been
identified in the captured normal frames. Parse by binary length, not by newline
or the next marker alone.

## Identity layout in regular addressed messages

| Direction/type | 6..9 | 10..13 | 14 |
|---|---|---|---|
| Thermostat `01-01`, `01-05`, `01-07` | Hub/network ID | Thermostat ID | Association slot |
| Hub `00-01`, `00-02`, `00-05`, `00-07` | Thermostat ID | Hub/network ID | Association slot |
| Hub `00-03` | `00 00 00 00` | Hub/network ID | `00` observed |

Do not generalize that layout to the shorter `00-08` / `FE-08` messages. Pairing
`01-02` also differs: its first identity field was `FF FF FF FF`, and its slot-like
field did not yet equal the eventual assigned slot. IDs should be treated as
opaque byte strings in their transmitted order, not converted by endianness.

## Command catalogue

| Kind | Bytes | Documented role | Evidence level / limitations |
|---|---:|---|---|
| [01-01](commands/01-01.md) | 44 | Thermostat status | Setpoint confirmed; other fields carry separate confidence labels |
| [00-01](commands/00-01.md) | 35 | Hub reply, calendar and optional absolute setpoint | Accepted setpoint changes demonstrated; rare 31-byte form not decoded |
| [01-05](commands/01-05.md) | 22 | Thermostat presence/hourly/recontact exchange | Not a universal loss-of-link flag |
| [00-05](commands/00-05.md) | 16 | Matching short hub response | Operating handshake demonstrated |
| [00-03](commands/00-03.md) | 18 | Periodic hub beacon-like message | Fixed bytes and timing observed; exact purpose unknown |
| [01-07](commands/01-07.md) | 35 | One row of a seven-day local program | Four temperature/time pairs, day bit and remaining count decoded |
| [00-07](commands/00-07.md) | 17 | Program-row acknowledgement | IDs/slot and remaining count mirrored; live transfers successful |
| [01-02](commands/01-02.md) | 38 | Thermostat association request candidate | Observed during pairing; payload mostly unknown |
| [00-02](commands/00-02.md) | 25 | Hub association response candidate | One archived example; complete pairing state machine not implemented |
| [00-08 / FE-08](commands/00-08-fe-08.md) | 14 each | Host/radio control exchange candidate | Observed on internal UART; RF transmission not established |

The early UART archive contains 7,503 reconstructed valid frames. Its counts
and sample selection are recorded in [E01](08-evidence.md#e01). Counts of one
kind/length in one archive are not an exhaustive vendor command specification.

## Stream decoder requirements

1. Find `7E 2B`; wait for the complete six-byte header.
2. Read BE16 length, add seven, enforce a sensible buffer limit.
3. Wait until that many bytes arrive; compare additive checksum.
4. On failure advance by one byte and search again, rather than accepting a
   guessed fixed-size message or discarding an entire subsequent good frame.
5. Classify by both kind and total size, then apply per-command checks.

At 19200 8N1 each UART byte takes about 520.83 us. A 44-byte UART frame therefore
takes about 22.92 ms to serialize. At 50 kbit/s those 44 RF data bytes take 7.04 ms.
This difference matters when comparing timestamps taken at the two interfaces.

The [offline helper](../tools/protocol.py) implements strict frame checking and
byte-stream reconstruction. It also exposes unknown payload bytes rather than
silently assigning them a meaning.
