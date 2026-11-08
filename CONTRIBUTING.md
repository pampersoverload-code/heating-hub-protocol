# Contributing protocol evidence

Contributions to documentation/data use CC BY-SA 4.0; software changes use GPLv3
as scoped in [LICENSE.md](LICENSE.md). Identify any differently licensed source
material before submitting it. Commercial reuse is allowed under these licenses.

A useful report contains a raw frame and a controlled observation, not only a
decoded screenshot. Please state:

1. Valve and gateway labels, radio/firmware variant if known; what makes you
   believe this is the same protocol family.
2. Capture interface: RF, radio FIFO, or which original UART direction. Include
   modem settings, stored/hardware sample rate and timestamp reference.
3. Complete hexadecimal bytes, total length and checksum result. Keep unknown
   fields intact. For RF include outer bytes and preamble/sync boundary if available.
4. Several frames before and after the action, with monotonic time and session
   boundaries. Say whether the original hub was actually powered/connected.
5. One precise user action, such as a 20 -> 21.5 C physical adjustment or a named
   weekday's unique program change. Identify other simultaneous changes.
6. What was independently confirmed: UART admission, RF reply, next reported
   setpoint, or just local TX completion.

Remove credentials, account identifiers, Wi-Fi data, personal room names and
unnecessary location/occupancy history before submitting logs. If replacing
radio IDs, replace them consistently in both directions, recompute checksums,
and label the data **sanitized**. Keep the untouched originals privately so the
transformation can be audited. Do not claim a modified checksum is measured RF.

Unknowns belong in the documentation as unknowns. A packet counter is not a
delivery rate without a denominator, and a timestamp association is not proof
of causation. New field meanings should identify an experiment/evidence ID and
show conflicting or exceptional cases too.

For offline changes run:

```sh
python -m unittest discover -s tests -v
python tools/check_docs.py
python tools/protocol.py --examples examples/frames.json
```

These commands use only local files and never transmit radio or contact a hub.
