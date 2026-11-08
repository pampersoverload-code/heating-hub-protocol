# External references and source boundaries

Protocol field meanings and timing in this repository come from our experiment
ledger, not an official vendor radio specification. The documents below explain
products or component interfaces. No third-party PDF is redistributed here.

<a id="manufacturer-manuals"></a>
## Manufacturer manuals

- [Saswell SEA801-DF1 + SASWG-04-WIFI(TY), combined instructions](https://www.saswell.com/storage/file/20251018/1760771404174643.pdf).
  Useful for physical controls, local-program operation and association UI.
  PDF page 8: AUTO/MANU + Plus association; PDF pages 9-10: four program
  periods and saving with AUTO/MANU. Its frequency specifications conflict
  between valve and gateway, so it is not authoritative evidence of our RF layer.
- [Saswell instruction index](https://www.saswell.com/Smart-radiator-thermostats-TRV-Instructions.html).
  Separate SEA801-DF1 and SEA801-Z01 entries illustrate why model/variant matters.
- [Older SEA801-APP manufacturer guide hosted by a distributor](https://amativeikals.lv/content/SEA801_APP_EN_.pdf).
  Specifies 868 MHz and AUTO/MANU + Plus; describes local schedules. Its defaults
  differ from the later combined guide. Do not mix revisions into one supposed
  universal device specification.

<a id="radio-components"></a>
## Radio components

- [TI CC1101 datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf).
  Modem/FIFO/register definitions for the research CC1101 module. It does not
  identify the original hub's chip or prove the original protocol's settings.
- [EBYTE E49-900M20S module manual](https://www.cdebyte.com/Uploadfiles/Files/2022-1-11/202211110463836.pdf).
  Module-pad references and electrical/module information. Module pad numbers
  differ from CMT2300A bare-chip pin numbers.
- CMOSTEK CMT2300A datasheet Rev0.7, AN142 quick-start material, AN192 register
  material, and **RFPDK 1.68** exports were used locally to implement the driver.
  The actual numerical working snapshot is in [profiles](../profiles/cmt2300a-working.json).
  Generated generic TX exports were not blindly copied over the working RX
  sync/baseband profile. SDK/installers are not included.

<a id="controller"></a>
## Controller

- [Espressif ESP32 GPIO documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gpio.html).
  Reference for GPIO capabilities, particularly input-only pins without internal
  pull resistors. ESP32-Sx/Cx variants must not inherit the classic ESP32 pin
  assumptions without checking their own documentation.

## Citation and capture policy

The evidence IDs E01..E12 refer to first-hand project observations summarized
in [the ledger](08-evidence.md). Full private UART/RF/SDR archives are not part
of this draft. Example identities, dates in illustrative new builder outputs,
and checksum updates must not be treated as untouched original measurements.
Hardware/API code from the operating project is not implicitly included here.
