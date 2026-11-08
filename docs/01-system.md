# System, objective and compatibility boundary

## Target installation

The research installation contains five regularly used battery radiator valves
and one convenient test valve. The product family is described in Saswell's
SEA801-DF1 / SEA801-APP and gateway documentation. The gateway-style designation
in the located combined manual is SASWG-04-WIFI(TY). Traffic in this installation
is proprietary 868 MHz radio, not Zigbee. Exact original radio-chip identification
was not established: the original module was unmarked or could not be identified.
It must not be described as a CC1101 merely because a CC1101 can receive it.

The located combined manufacturer manual itself contains conflicting frequency
entries, listing 2.400 GHz for the valve and 868 MHz for its gateway. We therefore
use captured RF and actual protocol behaviour to establish compatibility. The
manual also describes AUTO/MANU + Plus for radio association, and Plus for valve
stroke adaptation: those are distinct operations. [Manufacturer source](10-references.md#manufacturer-manuals)

## Original operation

The commercial arrangement provides app/voice control through an Internet-facing
gateway. That gateway exchanges framed binary messages over an internal UART
with its radio module, which communicates with the valves. Battery valves send
periodic status and listen for a hub response; the gateway is mains powered.
The timing and duration of the valve's actual RX window were not measured
directly. A brief window is plausible, not a decoded specification.

Local schedules continue to operate in the valves. Offline operation with the
original gateway absent still produced changes matching the programmed times.
Those schedules may originally have been configured through the vendor system;
the logs establish local execution behaviour, not their original provenance.

## Objective and achieved scope

The objective was to retain the existing valves but control them directly from
local automation, independently of the original gateway and its vendor cloud.
The resulting research hub can:

- Receive and validate the known normal status and presence frames.
- Reply with the relevant device/network identifiers and current calendar bytes.
- Set an absolute target temperature and repeat it until subsequently reported.
- Send the observed beacon pattern.
- Receive seven local-program rows and acknowledge the program transfer.
- Log radio/optional UART events and expose local HTTP status/setpoint interfaces.

A particular multi-day operational run is documented in [E08](08-evidence.md#e08).
It demonstrates useful real operation, not perfect packet reception or guaranteed
coverage. Some locations/devices had substantial receive gaps.

## Identity and pairing

Each operating association has a four-byte thermostat radio ID, four-byte hub
or network ID, and a slot observed as 1..6. These are binary fields, not ASCII
serial numbers. Conversion from a printed serial number has not been decoded.
The slot can be assigned during association and must not be inferred from a
thermostat's factory identity.

The practical commissioning method is passive observation of the original
working system, recording both sides of valid exchanges, followed by deliberate
takeover. UART access helped the investigation but is not required for a future
user to learn identities over the air. Fresh pairing without any original hub
is not yet a documented, complete implementation.

## Outside this repository's scope

This is not Tuya cloud API documentation, Zigbee cluster documentation, or a
dump of the original gateway firmware. It does not include the complete running
ESP32 application or promise the same behaviour across every SEA801 revision.
SD logging, a small status display, remote access and the unrelated 433 MHz
socket-transmitter addon are application choices, not this 868 MHz protocol.
