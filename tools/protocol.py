#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 Heating Hub Protocol contributors.
"""Offline observed-protocol helpers. No networking, radio access or scheduling."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path

SIZES = {0x0101: 44, 0x0001: 35, 0x0105: 22, 0x0005: 16,
         0x0003: 18, 0x0107: 35, 0x0007: 17, 0x0102: 38,
         0x0002: 25, 0x0008: 14, 0xFE08: 14}


def be16(data: bytes) -> int:
    if len(data) != 2:
        raise ValueError("expected two bytes")
    return int.from_bytes(data, "big")


def checksum(data: bytes) -> int:
    """Pass bytes BEFORE the checksum, excluding RF outer framing."""
    return sum(data) & 0xFF


def validate(frame: bytes) -> int:
    """Return the two-byte kind. Unknown kinds are structurally accepted."""
    if len(frame) < 7 or frame[:2] != b"\x7e\x2b":
        raise ValueError("missing application marker or incomplete header")
    if be16(frame[4:6]) + 7 != len(frame):
        raise ValueError("application length mismatch")
    if checksum(frame[:-1]) != frame[-1]:
        raise ValueError("application additive checksum mismatch")
    return be16(frame[2:4])


def require(frame: bytes, kind: int) -> None:
    if validate(frame) != kind or len(frame) != SIZES[kind]:
        raise ValueError("unsupported kind/length combination")


def build_frame(kind: int, payload: bytes) -> bytes:
    if not 0 <= kind <= 65535 or len(payload) > 65535:
        raise ValueError("kind or payload length out of range")
    prefix = b"\x7e\x2b" + kind.to_bytes(2, "big") + len(payload).to_bytes(2, "big") + payload
    return prefix + bytes([checksum(prefix)])


def iter_frames(data: bytes, max_frame_bytes: int = 1024):
    """Recover complete valid frames from a FINISHED byte capture, with offsets.

    This is not a live serial timeout implementation. Truncated/corrupt candidates
    are skipped one byte at a time so later complete frames can still be found.
    """
    pos = 0
    while pos + 6 <= len(data):
        pos = data.find(b"\x7e\x2b", pos)
        if pos < 0 or pos + 6 > len(data):
            return
        size = be16(data[pos + 4:pos + 6]) + 7
        if size <= max_frame_bytes and pos + size <= len(data):
            frame = data[pos:pos + size]
            try:
                validate(frame)
            except ValueError:
                pass
            else:
                yield pos, frame
                pos += size
                continue
        pos += 1


def decode_program(frame: bytes) -> dict:
    require(frame, 0x0107)
    mask, remaining = frame[32], frame[33]
    if not mask or mask > 0x40 or mask & (mask - 1):
        raise ValueError("program day must be one of seven one-hot bits")
    day_index = mask.bit_length() - 1
    if remaining != 6 - day_index:
        raise ValueError("day bit and remaining counter do not match observed form")
    points = []
    for offset in range(16, 32, 4):
        temperature = be16(frame[offset:offset + 2])
        minute = be16(frame[offset + 2:offset + 4])
        if not 50 <= temperature <= 300 or temperature % 5 or minute >= 1440:
            raise ValueError("program point outside observed range")
        points.append({"setpoint_c": temperature / 10,
                       "minute_of_day": minute,
                       "time": f"{minute // 60:02d}:{minute % 60:02d}"})
    return {"day_mask_hex": f"{mask:02X}", "weekday": None,
            "remaining": remaining, "reserved_15_raw": frame[15], "points": points}


def decode(frame: bytes) -> dict:
    kind = validate(frame)
    result = {"kind": f"{kind >> 8:02X}-{kind & 255:02X}",
              "length": len(frame), "checksum_ok": True,
              "raw_hex": frame.hex().upper()}
    if kind not in SIZES or len(frame) != SIZES[kind]:
        result["known_shape"] = False
        return result
    result["known_shape"] = True
    if kind in (0x0101, 0x0105, 0x0107):
        result.update(hub_id=frame[6:10].hex().upper(),
                      thermostat_id=frame[10:14].hex().upper(), slot=frame[14])
    elif kind in (0x0001, 0x0002, 0x0005, 0x0007):
        result.update(thermostat_id=frame[6:10].hex().upper(),
                      hub_id=frame[10:14].hex().upper(), slot=frame[14])
    if kind in (0x0101, 0x0105):
        result.update(setpoint_c=be16(frame[15:17]) / 10,
                      temperature_candidate_c=be16(frame[17:19]) / 10)
    if kind == 0x0101:
        result.update(valve_demand_candidate_raw=frame[21], mode_raw=frame[22],
                      program_signature_candidate_hex=frame[30:32].hex().upper())
    elif kind == 0x0105:
        result.update(status_19_raw=frame[19], hour_candidate_raw=frame[20])
    elif kind == 0x0001:
        target = be16(frame[16:18])
        result["commanded_setpoint_c"] = None if target == 65535 else target / 10
        try:
            result["calendar_wall_time"] = datetime(2000 + frame[20], *frame[21:26]).isoformat()
        except ValueError:
            result["calendar_wall_time"] = None
        result["timezone"] = "not encoded as an identified timezone field"
    elif kind == 0x0107:
        result.update(decode_program(frame))
    elif kind == 0x0007:
        result["remaining"] = frame[15]
    return result


def _association(request: bytes, kind: int) -> bytes:
    require(request, kind)
    if not 1 <= request[14] <= 6:
        raise ValueError("slot outside six observed associations")
    # The caller must check this against its OWN approved system/device registry.
    return request[10:14] + request[6:10] + request[14:15]


def build_status_reply(request: bytes, when: datetime, target_deci_c: int | None = None) -> bytes:
    """Build 00-01 from validated 01-01; use wall time exactly as supplied.

    No timezone conversion, transmitter scheduling or automatic clock lookup.
    None preserves the observed FF FF no-setpoint-change sentinel.
    """
    association = _association(request, 0x0101)
    if not 2000 <= when.year <= 2099:
        raise ValueError("calendar year outside reference implementation range")
    if target_deci_c is not None and (type(target_deci_c) is not int or
            not 50 <= target_deci_c <= 300 or target_deci_c % 5):
        raise ValueError("target must be integer tenths C, 50..300 in steps of 5")
    target = b"\xff\xff" if target_deci_c is None else target_deci_c.to_bytes(2, "big")
    calendar = bytes([when.year - 2000, when.month, when.day, when.hour, when.minute, when.second])
    payload = association + b"\xff" + target + b"\xff\x00" + calendar + b"\x00\x00" + b"\xff" * 6
    return build_frame(0x0001, payload)


def build_presence_reply(request: bytes) -> bytes:
    return build_frame(0x0005, _association(request, 0x0105))


def build_program_ack(request: bytes) -> bytes:
    association = _association(request, 0x0107)
    row = decode_program(request)
    return build_frame(0x0007, association + bytes([row["remaining"]]))


def build_beacon(hub_id: bytes) -> bytes:
    if len(hub_id) != 4:
        raise ValueError("hub ID must be four raw bytes")
    return build_frame(0x0003, bytes(4) + hub_id + b"\x00\xff\x00")


def rf_fifo_payload(frame: bytes) -> bytes:
    """Successful reference envelope only; no preamble/sync/hardware CRC here."""
    validate(frame)
    if len(frame) > 63:
        raise ValueError("reference packet exceeds merged 64-byte FIFO")
    return bytes([len(frame) + 1]) + frame


def nominal_airtime_us(frame: bytes) -> int:
    return (64 + 16 + 8 * len(rf_fifo_payload(frame))) * 20


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--hex", help="one complete application frame")
    group.add_argument("--examples", type=Path, help="validate and summarize example JSON")
    args = parser.parse_args()
    if args.hex:
        print(json.dumps(decode(bytes.fromhex(args.hex)), indent=2))
    else:
        examples = json.loads(args.examples.read_text(encoding="utf-8"))
        for sample in examples["frames"]:
            result = decode(bytes.fromhex(sample["hex"]))
            print(f'{sample["name"]}: {result["kind"]}, {result["length"]} bytes, checksum OK')


if __name__ == "__main__":
    main()
