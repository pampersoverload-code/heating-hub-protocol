# Radio layer and reproducible working profile

## Separate measurements from settings

| Parameter | Original-traffic evidence | Tested replacement setting |
|---|---|---|
| Band | Proprietary traffic near 868.1 MHz | 868.110 MHz on CMT |
| Centre | One SDR set placed the two states near 868.065 and 868.125 MHz, midpoint about 868.095 MHz | CC1101 centre 868.095154 MHz in a historical RX profile; CMT 868.110 MHz worked in both directions |
| Data rate | About 49,987.79 bit/s; bit interval about 20.0049 us in a measured set | Nominal 50 kbit/s |
| Frequency states | Two principal discriminator levels, around +/-28.5..30 kHz | GFSK, +/-28.56 kHz deviation, BT 0.5 |
| Bit representation | Binary frequency states in successful decoding | 0 = low frequency, 1 = high frequency; bytes MSB first |
| Preamble | Alternating bits before sync; absolute start boundary can be uncertain | 64 TX bits, eight bytes `AA`, nominal 1.28 ms |
| Sync | `2D D4` observed before application marker | 16 bits, no extra application sync bytes |
| Manchester / whitening / FEC | Not needed by validated working path | Disabled |
| Packet hardware CRC | A separate universal RF CRC algorithm has not been established | Disabled in successful TX profile; inner additive checksum retained |

GFSK is the working setting, not proof of the original chip's exact internal
Gaussian filter or a manufacturer-verified modulation register. Two-state FSK
demodulation by itself cannot distinguish unshaped 2-FSK from GFSK conclusively.
We found no convincing evidence for an additional pilot tone or hidden 4-FSK
symbols. Do not convert that into an exhaustive proof that every conceivable
extra signal was ruled out. [E02](08-evidence.md#e02), [E03](08-evidence.md#e03)

## Successful transmitted envelope

```mermaid
flowchart LR
    P[64 alternating preamble bits] --> S[16-bit sync 2D D4]
    S --> L[Outer byte = N + 1]
    L --> A[N-byte application frame: 7E 2B ... sum8]
```

| Application | N | Outer byte |
|---|---:|---|
| 01-01 status | 44 | `2D` |
| 00-01 reply / 01-07 program row | 35 | `24` |
| 01-05 presence | 22 | `17` |
| 00-05 reply | 16 | `11` |
| 00-07 program ACK | 17 | `12` |
| 00-03 beacon | 18 | `13` |

The entire FIFO payload is `[N+1] + application`, with no additional software
CRC bytes appended by this successful transmitter. It reproduces the established
CC1101 path and was accepted through the original hub radio six out of six
controlled CMT trials. That is positive evidence for this concrete envelope;
it is **not** a completed reverse engineering of every possible trailer, packet
length convention or original radio's private CRC mechanism. Do not add a guessed
CRC16 merely because a radio chip normally supports one. [E04](08-evidence.md#e04)

The RX decoder searches FIFO bytes for a validated application frame. A sync
flag or full FIFO alone is not a frame acceptance test. The longest regular
application here is 44 bytes; with the outer byte it fits in 45 FIFO bytes.

## CMT2300A / E49-900M20S

The reference module uses a 26 MHz crystal assumption and CMOSTEK RFPDK 1.68
profiles. The [machine-readable snapshot](../profiles/cmt2300a-working.json)
contains the 96-byte base RX profile, runtime register settings and the grouped
TX-bank values. It is a profile record, not a complete portable radio driver.

Important conventions used by the working driver:

- Module register CSB and FIFO FCSB are different selects. SDIO is bidirectional.
- GPIO1 is configured as active-HIGH INT1/SYNC_OK and wired to ESP32 GPIO27.
- RX uses a merged FIFO, with a latched sync timestamp and an 8.5 ms post-sync
  quiet interval for the known short packets before reading FIFO.
- TX uses fixed-length packet mode and writes exactly N+1 FIFO bytes. The CMT
  fixed-length register `0x46` is set to **FIFO-byte-count minus one**, hence N.
- Before TX, set STBY, load TX settings and all FIFO bytes, then enter TFS/PLL
  preparation. Issue one GO_TX at the absolute target time.
- Leave SPI untouched during the burst. The conservative reference wait is
  `2 * ((64 + 16 + 8*(N+1)) * 20 us) + 5 ms`, rounded up to RTOS ticks.
  For N=44, nominal airtime is 8.8 ms and this wait is 22.6 ms before rounding.
- Afterward inspect TX_DONE/end state once, restore RX registers/FIFO direction,
  clear flags and rearm RX. Only then dispatch deferred log writes.

RFPDK's generic TX export had **different default sync/baseband settings**.
We copied only its TX bank `0x55..0x5F`; blindly loading the whole TX export
would destroy the known working packet configuration.

The operating profile used +13 dBm **nominal**. Its TX bank is
`70 FF 08 00 02 30 00 5D 0B 3F 7F`. The successful initial +10 dBm bank was
`70 FF 08 00 02 30 00 3F 07 3F 7F`. These values apply to the RFPDK **20 dBm
matching-network selection** for this module. The separate nominal-dBm label is
not a power register and changing that label alone changes no RF output.
Neither setting is a calibrated radiated-power measurement or a regulatory
approval for any antenna/region.

## CC1101 context

CC1101 established useful RX, gateway-admission and some valve-control evidence.
It was not shown to be fundamentally incompatible. An older tested RX centre
was `FREQ2/1/0 = 21 63 66` with a 26 MHz crystal, rate `MDMCFG3 = F8` and
`MDMCFG4 = BA` for about 49,987.79 bit/s and 116,071 Hz RX bandwidth. Sync was
`2D D4`; `DEVIATN = 41` corresponds to about +/-28,564 Hz. These few values are
**not a complete CC1101 initialization recipe**: analogue, AFC/AGC, FIFO and
mode settings also matter. See the chip's [datasheet](10-references.md#radio-components).

CC1101 receive bandwidth is an RX filter parameter, not a knob that directly
narrows the transmitted signal. TX deviation and Gaussian shaping are different
controls. Widening RX or increasing TX power did not automatically improve all
thermostat links; timing, SPI activity, placement and antenna orientation were
confounding factors. The original gateway's output power was not calibrated.
