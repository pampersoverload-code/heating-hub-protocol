# Publication state

This is the first documentation-only stage of Heating Hub. The owner authorized
publication and confirmed an open-sharing approach on 8 November 2026. The
selected licenses are CC BY-SA 4.0 for documentation/data and GPLv3 for software;
see [LICENSE.md](LICENSE.md). No firmware deployment or change to the operating
heating system is part of publishing this repository.

Included:

- English system/protocol/radio/timing/investigation documentation.
- Field maps with explicit evidence labels and unresolved bytes.
- Sanitized byte examples, machine-readable command/profile records.
- Standalone Python decoder/builders and offline consistency tests.

Publication preparation:

- Licenses and their scopes are recorded, with full license texts included.
- Examples, local-path/privacy exclusions, byte-level tests and internal links
  have been checked. Model/variant and evidence limits remain explicit.
- GitHub destination: [pampersoverload-code/heating-hub-protocol](https://github.com/pampersoverload-code/heating-hub-protocol).
- Additional captures or measured plots can be contributed separately; raw
  household archives and third-party PDFs are intentionally absent.

The working ESP32 application and configurable community firmware remain separate
checkouts. Do not upload a firmware image merely to publish these notes. This
repository can explain a protocol independently of that software's eventual UI,
network setup, SD/display options and application-specific setpoint policy.
