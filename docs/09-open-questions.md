# Open questions and useful next experiments

| Topic | Current limit | Useful evidence |
|---|---|---|
| Printed serial -> radio ID | No conversion known | Multiple labelled devices and independently captured binary IDs; do not derive from one example |
| Pairing without the vendor hub | Only partial 01-02/00-02 history | Full synchronized RF/UART capture from before association through first stable status, across more than one association |
| 00-08 / FE-08 | Internal UART exchange observed; RF role unproved | Time-correlated IQ plus both UART directions; do not transmit it just because it appears on UART |
| Exact RX listening window | Reply targets work; window edge not measured | Controlled delay sweep at fixed payload/radio settings with later setpoint reports; account for lost reports |
| Original modem identity/shaping | Unmarked hardware; binary states and working GFSK profile | Board/chip identification or calibrated phase/frequency comparison under equal capture conditions |
| Outer packet/trailer universality | Specific length+application envelope works; no universal outer CRC established | Complete original RF bursts of multiple lengths with exact raw bit boundaries |
| Exact preamble start | Alternating bits easy to see, absolute start less certain | Stable high-SNR IQ including burst onset; distinguish PA settling from bit boundaries |
| Status offsets 19,20,23,24..29,32..42 | Raw patterns known; meanings mostly unresolved | One controlled state change at a time: battery, window, local mode, valve behaviour |
| Valve demand vs physical position | Offset21 plausibly 0..100 demand/opening | Independent position or motor measurement, not just setpoint-temperature correlation |
| Program signature at 30..31 | Stable pairs change with program revisions | Precisely labelled complete before/after tables, inspect original hub's response; search checksum algorithms without declaring the first coincidence a match |
| Program request/download | No proven active request command or hub-to-valve schedule writer | Original-hub traffic around a deliberate app request or remotely edited schedule |
| RF weekday mapping | Seven one-hot masks; names intentionally unset | Change just one specifically named day and one unique point; compare all seven rows |
| Coincident program points | Four identical times can be stored | Observe the time boundary with external target null and a distinct prior setpoint; don't infer execution count from four equal table entries |
| Local hand change vs schedule change | Auto remains set after some hand changes | Controlled physical change versus a program event at the same mode, comparing all raw bytes; mode bit alone is insufficient |
| Beacon necessity | Vendor cadence and successful replacement TX known | Long-powered-off valve reintroduced while original hub is physically absent, with and without correctly scheduled beacons |
| Different batches/channels | One radio system deeply studied | Passive, long-enough captures from independently identified variants; do not silently auto-select a nearby household's system |

When comparing an experiment, state what is held fixed and which single change
is being tested. In a non-controlled historical sequence, report correlation
instead of assigning all improvement to the latest hardware or power change.
Exact target acceptance is stronger than an aesthetically smoother SDR plot.

No active probing of guessed command bits is required to read this repository.
See [the contribution guide](../CONTRIBUTING.md) for a minimal useful capture.
