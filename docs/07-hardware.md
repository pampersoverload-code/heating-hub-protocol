# Reference hardware and capture connections

The current research build uses an ESP32 DevKit-class controller and an EBYTE
E49-900M20S module based on CMT2300A, with an external antenna. The earlier
CC1101 module was useful for protocol discovery and remains a separate driver
option. Pin numbers below are a **reference wiring**, not a protocol requirement.

## CMT adapter

| Signal | ESP32 GPIO / supply | E49-900M20S module pad | Notes |
|---|---|---:|---|
| VCC | Separate regulated 3.3 V | 8 | Actual research supply; not powered by a GPIO |
| GND | Common signal ground | e.g. 9 | Ground reference for controller/module |
| SCLK | 18 | 11 | Clock |
| SDIO | 23 | 12 | Bidirectional data, formerly CC1101 MOSI contact |
| CSB | 17 | 13 | Register select, active LOW |
| FCSB | 19 | 14 | FIFO select, active LOW; formerly CC1101 MISO contact |
| GPIO1 / INT1 | 27, ESP input | 5 | Configured SYNC_OK output |
| Unused old GDO2 | 26, ESP input | not connected | Do not assume the CMT IRQ is on this old CC pin |

These are **module pad numbers**, not bare CMT2300A chip pin numbers. Consult
the [module manual](10-references.md#radio-components). CMT three-wire SPI is not
a drop-in four-wire MOSI/MISO interface: the old MISO contact is now a driven
FIFO-select signal. Never join CSB and FCSB or assume an old CC1101 image can
drive the new adapter correctly.

A real GPIO1-to-CSB solder bridge initially generated false interrupts exactly
when software selected the radio. Confirmed repair led to valid automatic RF
reception. Keep such electrical checks separate from register-readback checks.
Normal reference SPI half-period is 2 us after startup verification; bit-banged
GPIO overhead makes that a timing parameter, not a precise measured 250 kHz rate.

Local ceramic decoupling was already present on the module. Extra 2.2 uF, then
47 uF capacitance and later a separate 3.3 V linear supply were tried. The
separate regulator was rated for 1 A; this is supply headroom, **not a measured
radio current requirement**. Improvements were not isolated enough to claim the
regulator alone solved the link. Keep wiring and antenna geometry fixed during
comparisons and measure supply behaviour at the module when investigating it.

## Optional UART taps on the original gateway

| Captured original link | Reference ESP input | Historical label |
|---|---:|---|
| Host/controller -> original radio | 34 | W |
| Original radio -> host/controller | 35 | G |

The capture format is 19200 8N1. These connections observe existing logic signals;
they are not RS-232 voltage-level connections. Check actual signal levels and use
appropriate interfacing. Connect only receive inputs and a common reference;
do not tie two transmit outputs together. UART0/USB debug logging is separate.

Classic ESP32 GPIO34..39 have no internal pulls. With the original gateway
removed, floating tap inputs produced byte noise and misleading activity. The
operating firmware therefore disables unused UART drivers persistently and
blinks activity only for validated frames. It does not need a live UART for RF
hub operation. [ESP32 reference](10-references.md#controller)

## Optional research peripherals

| Function | Reference GPIOs |
|---|---|
| SD-card SPI, separate host | SCK25, MOSI32, MISO33, CS13 |
| Monochrome I2C display | SDA21, SCL22 |
| Board activity LED | GPIO2; polarity depends on board |
| Original-hub supply switch control | GPIO4 through the actual interface circuit |

The original-hub power pin drives an external transistor interface; it must not
be wired as a 12 V output from the ESP32. A software power-state flag is not
proof that an unplugged gateway has power. None of the display, SD or gateway
switch components is inherently necessary for implementing the radio protocol.

Radio placement and antenna polarization changed per-device reception in the
apartment. Relative SDR levels from one antenna/location cannot establish the
original gateway's absolute transmit power or guarantee the same ranking at
every thermostat. A receiver gap is not fixed by increasing our TX power alone.
