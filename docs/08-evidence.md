# Evidence ledger

These are dated summaries of project experiments, not manufacturer specifications.
Raw household archives remain private. Public examples substitute radio identities
and recompute checksums, so they must not be mistaken for untouched originals.
An external maintainer can reproduce the described checks and submit their own
captures. Statistical claims below apply only to the named observation windows.

<a id="e01"></a>
## E01 - Original UART archive, 11-12 October 2026

7,503 reconstructed frames with valid additive checksums:

| Kind / total bytes | Count | Observed UART direction |
|---|---:|---|
| 01-01 / 44 | 2,973 | Radio -> host |
| 00-01 / 35 | 2,967 | Host -> radio |
| 01-05 / 22 | 101 | Radio -> host |
| 00-05 / 16 | 101 | Host -> radio |
| 00-03 / 18 | 1,200 | Host -> radio |
| 01-02 / 38 | 54 | Radio -> host |
| 00-02 / 25 | 1 | Host -> radio |
| 00-08 / 14 | 53 | Host -> radio |
| FE-08 / 14 | 53 | Radio -> host |

This establishes byte shapes and occurrence in that archive, not RF transmission
of UART control messages. The sole 00-02 followed repeated 01-02 and was followed
about three seconds later by normal status using the assigned slot. Pairing
semantics are therefore strongly suggested, but one reply is insufficient for a
complete implementation. A later paired UART/RF timing analysis established W/G
direction rather than assuming it from labels.

<a id="e02"></a>
## E02 - SDR/radio decoding and RX experiments, 16-26 October

Recovered RF application bytes were compared byte-for-byte with original UART.
An early SDR set showed about 20 us symbols and states near 868.065/868.125 MHz.
CC1101 RX trials included 203, 135 and 116 kHz bandwidths; narrower reception
improved several comparisons, but per-device reception remained unequal.

Matched 2-FSK/GFSK recording conditions on 26 October used 500 kS/s stored IQ,
an 85 kHz analysis filter, identical gain/placement parameters and about 110 s
recording duration without reported gaps/drops. GFSK transitions looked smoother;
the analysis did not prove elimination of every discriminator spike. A periodic
spike pattern is not proof of an extra RF carrier or of its electrical cause.

<a id="e03"></a>
## E03 - CC1101 GFSK positive control, 26 October

Six frozen valid thermostat 01-01 frames, nominal +7 dBm, about ten seconds apart,
with original hub ON. All six were byte-identical and checksum-valid on its
radio-to-host UART, and all six had matching host-to-radio 00-01 replies.
This demonstrates gateway radio admission and host processing of that concrete
GFSK frame. It does not demonstrate acceptance of our hub reply by a thermostat.

<a id="e04"></a>
## E04 - CMT2300A two-direction gateway control, 1 November

After repairing the GPIO1/CSB bridge, automatic CMT IRQ-driven reception of an
original 44-byte status and 35-byte hub reply matched independent UART bytes.
Next, six identical frozen 44-byte status frames were sent at +10 dBm nominal,
GFSK BT0.5, 868.110 MHz, 50 kbit/s, +/-28.56 kHz, 64 preamble bits and sync 2DD4.

- All 6/6 appeared byte-exact and valid on original hub UART input,
  26.762..27.855 ms after the recorded GO_TX write reference.
- All 6/6 had matching valid 35-byte host output, 46.734..47.913 ms after GO_TX.
- All six host replies were also received byte-exact over CMT radio.
- TX completion and RX restoration succeeded in each case.

This validates the specific `[2D] + 44-byte application` envelope with no added
hardware CRC in that control. It is not evidence of thermostat acceptance in
the other direction, and not a calibrated power test.

<a id="e05"></a>
## E05 - Response deadlines and logging interference, 26 October

An impaired run started only 6/16 status replies near 53 ms; the rest were
about 204..232 ms late in absolute offset. Synchronous SD flush/fsync marker
writes blocked the critical task. Deferring the writes produced 29/29 status
GO_TX offsets at 53.001..53.002 ms in two subsequent sections. Yet no setpoint
change was confirmed in those sections. Fixing one timing fault was necessary
but did not by itself prove the entire radio path worked.

<a id="e06"></a>
## E06 - Recovery/hourly exchanges, analysed 2 November

42 own 00-05 replies matched exact RF 01-05 requests: 39 followed by RF 01-01
at 69.075..89.401 ms, two at 259.810/281.101 ms, one at 140.051 s from request
sync. A separate startup had all six known valves perform the 05 -> 01 chain
within 298.09 s after replacement service began.

Hourly 01-05 rounds also occurred after ordinary traffic, including preceding
normal status about 120 s earlier. Thus 01-05 is not an exclusive link-loss flag.
An October 29 power-on capture's first valve requests arrived around five to
seven minutes after logging began. Do not infer a precise timeout from these
startup observations or from approximate user recollections.

<a id="e07"></a>
## E07 - Original and replacement beacons, 2 November

Original RF: eleven consecutive beacons yielded ten intervals
59.997822..59.997873 s in one set. Startup showed two RF beacons about 21.3 ms
apart, then another around 13.82 s after the first, overlapping a minute phase
near second 01. UART output multiplicity differed from decoded RF multiplicity.

Replacement implementation: six initially checked beacon sends completed and
restored RX; startup spacing actually 23.017 ms. Longer operation recorded 5,946
beacon sends with no logged TX errors or missed 60-second target slots in the
analysed sections; maximum postponement was about 242 ms for RX priority.
No isolated beacon-to-cold-start synchronization causality has been proved.

<a id="e08"></a>
## E08 - Multi-day local-automation operation, analysed 7 November

Marker window: 3 November 09:14 to 7 November 12:28 local time. In total 18,047
replies: 17,464 status and 583 presence replies. All 130 logged target corrections
matched the next captured valid status for that association. Since the 4 November
restart: 15,105 status replies, 504 presence replies, 105 corrections; 85 matching
reports within one second, 20 later reports from one weak-link valve, maximum
180.187 seconds. These include local-program corrections, not just user requests.

00-01 GO_TX median 53.006 ms, maximum 56.085 ms; 00-05 median 27.203 ms,
maximum 41.691 ms. No logged reply exceeded 60 ms in that window. This is **not
a universal 100% RF delivery rate**: missing requests and missed early status
reports are not fully observable from reply markers.

One location/device had gaps up to 860 s while others kept communicating. One
unhandled-HIGH IRQ recovery was logged, followed by a reply 25.823 s later and
no reset. One FIFO overflow was counted without enough timestamp evidence to
equate it to that event. POWERON resets and a roughly 421 s service-start delay
were observed; delayed clock readiness is plausible, not isolated as the cause.

At all five regular valves, 70 of the 105 corrections matched local 06/18 -> 20 C
and 08/22 -> 16 C program transitions. Original gateway absence and unchanged
external targets support local schedule execution. Exact schedule tables were
not captured from every valve.

<a id="e09"></a>
## E09 - Weekly-program decoding and acknowledgement, 29 October / 7 November

Archived and new 35-byte 01-07 rows exposed four BE16 temperature/minute pairs,
ascending masks 01..40 and a remaining counter 6..0. Seven-row 7 November test:
437.798 ms first-to-last request, gaps 72.927..73.032 ms, all seven rows valid and
seven own ACKs at GO_TX 35.106..35.110 ms. Intermediate next rows demonstrate
progression; no explicit final ACK-of-ACK was identified.

Status offsets 30..31 changed around saved program revisions: 6F39 -> 2EBD in
the old sequence and 2CE1 -> 73D3 later. One old value persisted across 33 normal
statuses and Auto/Manual changes, the next over 302 statuses. This supports a
program signature/version/checksum candidate. Some common CRC16 trials did not
identify a secure algorithm; this is not a decoded CRC16 or request flag.

<a id="e10"></a>
## E10 - Identical times and whole-week selection, 8 November

After selecting the test valve's week-editing option, a complete valid seven-row
upload contained four identical points at **06:00 / 20 C on every day mask**.
The user then recognized the display option 1-7 as **all days**, not "day one
of seven". This explains the changed whole week and establishes that duplicate
times can be stored/transmitted by this firmware. Execution order/count of
coincident points was not measured. The menu's day 1 is described as Monday in
the manual; an independent targeted RF-mask-to-weekday check remains open.

<a id="e11"></a>
## E11 - Auto/Manual and physical setpoint changes, 29 October

On one valve, Auto -> Manual changed status offset 22 from 01 to 00 and kept
the setpoint at 21 C; reversing it restored 01 and the active 16 C program value.
A later physical temperature adjustment to 21.5 C left offset 22 at 01.
Thus the mode interpretation is well supported for that valve, but the same
byte does not uniquely label the cause of every temperature change.

<a id="e12"></a>
## E12 - Software recovery test, 2 November

An intentionally missed IRQ was rescued by the HIGH check, with uncertain
timestamp discarded. A separate deliberate worker stall produced a reset marker
15.267851 s after the test marker; the next boot was observed within 17.844 s.
Radio reception resumed. This tests a worker/IRQ recovery mechanism, not every
possible CPU failure, and does not turn normal RF silence into a reset reason.
