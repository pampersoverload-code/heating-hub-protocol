# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 Heating Hub Protocol contributors.
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import protocol as p


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples = json.loads((ROOT / "examples/frames.json").read_text(encoding="utf-8"))
        cls.frames = {x["name"]: bytes.fromhex(x["hex"]) for x in cls.examples["frames"]}

    def test_all_documented_examples(self):
        for x in self.examples["frames"]:
            with self.subTest(x["name"]):
                b = bytes.fromhex(x["hex"])
                self.assertEqual(len(b), x["length"])
                self.assertEqual(p.decode(b)["kind"], x["kind"])

    def test_every_single_bit_fault_in_status_is_rejected(self):
        original = self.frames["01_01"]
        for index in range(len(original)):
            for bit in range(8):
                b = bytearray(original); b[index] ^= 1 << bit
                with self.assertRaises(ValueError):
                    p.validate(b)

    def test_additive_checksum_does_not_detect_all_compensating_faults(self):
        b = bytearray(self.frames["01_01"])
        before = bytes(b)
        b[20] -= 1; b[21] += 1
        self.assertNotEqual(b, before)
        self.assertEqual(p.validate(b), 0x0101)

    def test_no_change_status_reply_matches_observed_shape(self):
        request = self.frames["01_01"]
        actual = p.build_status_reply(request, datetime(2026, 1, 2, 3, 4, 5))
        self.assertEqual(actual, self.frames["00_01"])
        self.assertIsNone(p.decode(actual)["commanded_setpoint_c"])

    def test_absolute_half_degree_target_and_binary_calendar(self):
        b = p.build_status_reply(self.frames["01_01"], datetime(2026, 11, 8, 17, 42, 59), 215)
        self.assertEqual(b[16:18], bytes.fromhex("00D7"))
        self.assertEqual(b[20:26], bytes([26, 11, 8, 17, 42, 59]))
        self.assertEqual(p.decode(b)["commanded_setpoint_c"], 21.5)
        self.assertEqual(b[6:10], self.frames["01_01"][10:14])
        self.assertEqual(b[10:14], self.frames["01_01"][6:10])

    def test_no_hidden_timezone_conversion(self):
        when = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        b = p.build_status_reply(self.frames["01_01"], when)
        self.assertEqual(b[23:26], bytes([3, 4, 5]))

    def test_invalid_target_ranges_types_and_request_shapes(self):
        for target in (49, 301, 211, 215.0, True):
            with self.subTest(target=target), self.assertRaises(ValueError):
                p.build_status_reply(self.frames["01_01"], datetime(2026, 1, 1), target)
        with self.assertRaises(ValueError):
            p.build_status_reply(self.frames["01_05"], datetime(2026, 1, 1), 200)
        with self.assertRaises(ValueError):
            p.build_status_reply(self.frames["01_01"], datetime(1999, 1, 1), 200)

    def test_presence_reply_matches_original_shape(self):
        self.assertEqual(p.build_presence_reply(self.frames["01_05"]), self.frames["00_05"])

    def test_beacon_matches_original_shape(self):
        hub = bytes.fromhex(self.examples["hub_id"])
        self.assertEqual(p.build_beacon(hub), self.frames["00_03"])

    def test_all_program_masks_counts_and_acks(self):
        for index in range(7):
            mask = f"{1 << index:02x}"
            request = self.frames["program_day_" + mask]
            row = p.decode_program(request)
            ack = p.build_program_ack(request)
            self.assertEqual(row["remaining"], 6 - index)
            self.assertIsNone(row["weekday"])
            self.assertEqual(ack[15], request[33])
            self.assertEqual(ack[6:10], request[10:14])
            self.assertEqual(ack[10:14], request[6:10])
            self.assertEqual(p.validate(ack), 0x0007)
            self.assertEqual(len(ack), 17)
            self.assertTrue(all(x["time"] == "06:00" and x["setpoint_c"] == 20 for x in row["points"]))

    def test_varied_program_is_not_forced_to_default_times(self):
        row = p.decode_program(self.frames["program_varied"])
        self.assertEqual([x["time"] for x in row["points"]], ["06:00", "08:00", "16:00", "22:00"])

    def test_program_plausibility_after_recomputing_checksum(self):
        for offset, value in ((32, 3), (33, 0), (18, 6), (16, 2)):
            b = bytearray(self.frames["program_day_01"])
            b[offset] = value; b[-1] = p.checksum(b[:-1])
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                p.decode_program(b)

    def test_envelope_lengths_and_airtime(self):
        for name, outer in (("01_01", 0x2D), ("00_01", 0x24), ("00_05", 0x11),
                            ("program_ack_01", 0x12), ("00_03", 0x13)):
            frame = self.frames[name]
            self.assertEqual(p.rf_fifo_payload(frame), bytes([outer]) + frame)
        self.assertEqual(p.nominal_airtime_us(self.frames["01_01"]), 8800)
        oversized = p.build_frame(0x1234, bytes(57))
        with self.assertRaises(ValueError):
            p.rf_fifo_payload(oversized)

    def test_no_uart_control_rf_claim(self):
        for name in ("00_08", "fe_08"):
            b = self.frames[name]
            self.assertEqual(len(b), 14)
            self.assertNotIn("setpoint_c", p.decode(b))

    def test_offline_stream_resynchronization(self):
        good = self.frames["01_01"]; reply = self.frames["00_01"]
        bad = bytearray(good); bad[-1] ^= 1
        data = b"noise\x7e\x2b\xff\xff\xff\xff" + bytes(bad) + good + reply + b"\x7e"
        found = list(p.iter_frames(data))
        self.assertEqual([b for _, b in found], [good, reply])

    def test_unknown_valid_kind_retained_as_raw(self):
        frame = p.build_frame(0x1234, b"unknown")
        self.assertFalse(p.decode(frame)["known_shape"])
        self.assertEqual(p.decode(frame)["raw_hex"], frame.hex().upper())


if __name__ == "__main__":
    unittest.main()
