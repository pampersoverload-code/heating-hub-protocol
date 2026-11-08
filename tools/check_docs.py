#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 Heating Hub Protocol contributors.
"""Offline consistency checks for links, field coverage, profiles and examples."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import protocol as p


def check():
    commands = json.loads((ROOT / "protocol/commands.json").read_text(encoding="utf-8"))
    examples = json.loads((ROOT / "examples/frames.json").read_text(encoding="utf-8"))
    frames = {s["name"]: bytes.fromhex(s["hex"]) for s in examples["frames"]}
    assert commands["offset_base"] == 0
    for command in commands["commands"]:
        coverage = []
        for field in command["fields"]:
            assert field["length"] > 0
            coverage.extend(range(field["offset"], field["offset"] + field["length"]))
        assert sorted(coverage) == list(range(command["total_bytes"])), command["kind"]
        frame = frames[command["sample"]]
        kind = int(command["kind"].replace("-", ""), 16)
        p.require(frame, kind)
        assert len(frame) == command["total_bytes"]
    for name, frame in frames.items():
        p.decode(frame)

    profile = json.loads((ROOT / "profiles/cmt2300a-working.json").read_text(encoding="utf-8"))
    registers = profile["base_rx_registers_hex"]
    assert sorted(int(a, 16) for a in registers) == list(range(96))
    assert all(0 <= int(v, 16) <= 255 for v in registers.values())
    assert profile["rf"]["sync_hex"] == "2DD4"
    assert all(len(bytes.fromhex(bank["values_hex"])) == 11 for bank in profile["tx_banks"])

    markdown = list(ROOT.rglob("*.md"))
    links = 0
    for file in markdown:
        text = file.read_text(encoding="utf-8")
        # Inline code examples and fenced code do not contain document links here.
        for target in re.findall(r"\]\(([^\s)]+)\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, anchor = unquote(target).partition("#")
            dest = (file.parent / path).resolve() if path else file
            assert dest.is_relative_to(ROOT), (file, target, "link outside repository")
            assert dest.is_file(), (file, target, "missing linked file")
            if anchor:
                linked = dest.read_text(encoding="utf-8")
                ids = set(re.findall(r'<a id="([^"]+)"', linked))
                for heading in re.findall(r"^#+ (.+)$", linked, re.M):
                    slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
                    ids.add(slug)
                assert anchor in ids, (file, target, "missing anchor")
            links += 1
    # No absolute local paths, device IPs or firmware credentials in public docs.
    for file in ROOT.rglob("*"):
        if not file.is_file() or ".git" in file.parts or "__pycache__" in file.parts:
            continue
        text = file.read_text(encoding="utf-8")
        assert not re.search(r"[A-Za-z]:[\\/]Users[\\/]|192\.168\.2\.\d+|WIFI_PASSWORD\s*=|X-Update-Token\s*:", text), file
    print(f"OK: {len(commands['commands'])} field maps, {len(frames)} examples, "
          f"96 profile registers, {len(markdown)} Markdown files, {links} internal links")


if __name__ == "__main__":
    check()
