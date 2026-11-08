# Command field maps

Zero-based offsets; see [framing](../03-frame-format.md) for byte order, length and checksum.

| Kind | Role | Total bytes |
|---|---|---:|
| [01-01](01-01.md) | Thermostat status | 44 |
| [00-01](00-01.md) | Hub status/calendar/setpoint response | 35 |
| [01-05](01-05.md) | Thermostat presence/hourly/recontact | 22 |
| [00-05](00-05.md) | Hub presence response | 16 |
| [00-03](00-03.md) | Hub beacon-like frame | 18 |
| [01-07](01-07.md) | Thermostat weekly-program row | 35 |
| [00-07](00-07.md) | Hub program-row acknowledgement | 17 |
| [01-02](01-02.md) | Thermostat association request candidate | 38 |
| [00-02](00-02.md) | Hub association response candidate | 25 |
| [00-08](00-08-fe-08.md) | Host-to-radio control candidate | 14 |
| [FE-08](00-08-fe-08.md) | Radio-to-host control candidate | 14 |
