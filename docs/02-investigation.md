# Investigation method and useful mistakes

## 1. Observe the original gateway from the inside

Two receive-only UART taps were connected to the gateway's existing controller-
to-radio and radio-to-controller lines, with common signal ground. The working
serial format is 19200, 8N1. Binary logs preserved direction, monotonic ESP
microseconds, sequence numbers, session identity and, once available, UTC.

The historical capture labels W and G are wire labels, not protocol definitions.
In the investigated wiring, W carried host-to-radio output and G carried
radio-to-host input. This direction assignment was checked against time-correlated
RF frames, not inferred from wire colour or frame size. One archive showed hub
00-01 UART starts about 8.603 ms before their RF sync mark, while thermostat
01-01 UART starts followed RF sync by about 22.092 ms. Those offsets are
observations for that setup, not universal transport constants. [E01](08-evidence.md#e01)

Known manual actions, such as changing an absolute setpoint, were compared with
the bytes before and after. Frame length and additive checksums let us reconstruct
messages even in a continuous byte stream. Controlled 18 -> 22 -> 20 -> 22 C
changes established the absolute setpoint in 00-01, rather than a relative step.

## 2. Independently observe the radio

An SDRplay RSP1 recorded IQ, including captures stored at 500 kS/s and attempts
at higher rates. Stored and hardware sample rates are not always identical:
one 500 kS/s run used 2 MS/s hardware sampling followed by x4 decimation.
Raw IQ was frequency-discriminated, filtered and sliced offline. We compared
sync, outer length and the recovered application bytes with UART captures.

The discriminator estimate is proportional to
`arg(IQ[n] * conjugate(IQ[n-1])) * sample_rate / (2*pi)`.
It shows instantaneous frequency, not a direct RF-voltage oscilloscope trace.
Amplitude fades, clipping, sample gaps, filter transients and low-SNR samples
can produce misleading frequency spikes. Preserve those limits when comparing
plots. Identical processing alone does not guarantee identical receiving conditions.

Use the same receive antenna, position, gain/AGC, sample rate and processing
when comparing sources. Align on a declared sync boundary and compare identical
bits where possible. Separate amplitude normalization from calibrated power
measurement; our relative SDR levels were not calibrated transmitter ERP.

## 3. Separate the two experimental directions

**Simulated thermostat -> original hub:** transmit a frozen, valid thermostat
frame while the original hub remains on. Receiving the same bytes on the hub's
radio-to-controller UART proves admission by its radio module. A following
host-to-radio reply shows host processing. The reply's RF capture is a further
independent observation. Six identical transmissions at about ten-second spacing
were useful for identifying our traffic. [E03](08-evidence.md#e03), [E04](08-evidence.md#e04)

**Replacement hub -> real thermostat:** remove the original hub from the exchange,
receive a real thermostat request, then answer that specific request on a fixed
deadline. A later valid status carrying our target temperature establishes
setpoint acceptance. During development a decrement-by-1-C test, wrapping from
5 C back to 21 C, made successes visible. That is a diagnostic policy, not part
of the vendor protocol or the normal local-automation service.

## 4. Findings that changed the implementation

| Issue or experiment | What we learned |
|---|---|
| Wider RX bandwidth | Wider was not automatically better; a CC1101 116 kHz setting improved some archived comparisons over 135/203 kHz. Location and other settings still mattered. |
| 2-FSK, GFSK, 4-FSK and MSK trials | GFSK produced validated gateway reception and later valve operation. Tested MSK configurations did not provide a successful replacement path. This is not an exhaustive proof against every possible MSK setting. |
| 63/65-bit preamble hypothesis | A useful question, but arbitrary-bit TX met GPIO/driver difficulties. Do not report a completed successful 63/65-bit compatibility experiment. Standard 64-bit TX was sufficient for later operation. |
| Capacitors and separate radio supply | Additional local capacitance and later a separate 3.3 V regulator were tried. Qualitative trace changes did not isolate the power supply as the single cause. |
| SPI during a burst | Polling radio registers during TX coincided with problematic traces. All active send paths were changed to preload FIFO, issue TX and leave radio SPI quiet until after the burst. Preserve that working rule; the exact electrical coupling mechanism remains unproven. |
| SD markers before replies | Synchronous flush/fsync in the critical task caused 00-01 starts around 204..241 ms instead of 53 ms. Moving logging after TX/in a queue restored the deadline. This was a software timing fault, not RF evidence. |
| CMT adapter short | GPIO1 was shorted to CSB, creating false IRQs synchronized with our own SPI. Repair restored real IRQ/RF reception. Register communication alone had not proved correct interrupt wiring. |
| CMT missed rising edge | A HIGH arriving while IRQ was masked could strand RX. Recovery drains it without pretending to know the original sync timestamp; a separate heartbeat watchdog handles a stuck worker. |

## 5. Preserve the right evidence

Store the complete frame and checksum status, not just decoded values. Separate
transmission completion from acceptance, RF from UART observations, expected
send slots from actually decoded packets, and raw candidate counts from valid
frame counts. Mark user actions and parameter changes. Do not combine a reboot's
new monotonic timestamps with the previous session without an explicit mapping.

Research trace references are in the [evidence ledger](08-evidence.md). Full
household logs and multi-gigabyte IQ recordings are intentionally not copied
into this public-facing draft.
