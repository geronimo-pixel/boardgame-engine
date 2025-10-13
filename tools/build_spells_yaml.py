"""
Convert the raw spell list into structured YAML.

Each spell entry captures:
    - name
    - number (as integer)
    - effect description
    - target specification
    - phase (string, preserves ranges such as "1-5")
    - cost (integer)

Usage:
    python tools/build_spells_yaml.py

Output:
    rules/spells/spells.yaml
"""
from __future__ import annotations

from pathlib import Path
from typing import List

import yaml


FIELD_NAMES = ["name", "number", "effect", "target", "phase", "cost"]


def parse_spells(path: Path) -> List[dict]:
    records: List[dict] = []
    collecting = False
    buffer: List[str] = []
    header_to_skip = 0

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "Name":
            collecting = True
            buffer = []
            header_to_skip = len(FIELD_NAMES) - 1  # skip column labels that follow
            continue
        if not collecting:
            continue
        if header_to_skip:
            header_to_skip -= 1
            continue

        if raw_line.startswith("\t"):
            buffer.append(line)
        else:
            if buffer:
                buffer[-1] += f" {line}"
            else:
                buffer.append(line)

        if len(buffer) == len(FIELD_NAMES):
            entry = dict(zip(FIELD_NAMES, buffer))
            records.append(entry)
            buffer = []

    return records


def normalise_entry(raw: dict) -> dict:
    entry = {
        "name": raw["name"],
        "number": max(0, int(raw["number"])),
        "effect": raw["effect"],
        "target": raw["target"],
        "phase": raw["phase"],
        "cost": max(0, int(raw["cost"])),
    }
    return entry


def write_yaml(entries: List[dict], output_path: Path) -> None:
    output_path.write_text(yaml.safe_dump(entries, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    source_path = project_root / "Original files" / "Spells.txt"
    output_path = project_root / "rules" / "spells" / "spells.yaml"

    raw_records = parse_spells(source_path)
    normalised = [normalise_entry(record) for record in raw_records]
    write_yaml(normalised, output_path)
    print(f"Wrote {len(normalised)} spells to {output_path}")


if __name__ == "__main__":
    main()
