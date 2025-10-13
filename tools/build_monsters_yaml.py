"""
Export the parsed monster data into a concise YAML reference.

Each monster entry includes:
    - sequential number (1-based ordering, matching the source iteration)
    - name, health, armor, attack, overkill
    - dice code
    - ability text lines
    - loot description

Usage:
    python tools/build_monsters_yaml.py

Output:
    rules/monsters/monsters.yaml
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

import yaml

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.monster_loader import load_monsters


def _monster_entry(monster, number: int) -> dict:
    return {
        "number": number,
        "name": monster.name,
        "health": max(0, monster.health),
        "armor": max(0, monster.armor),
        "attack": max(0, monster.attack),
        "overkill": max(0, monster.overkill),
        "dice": monster.dice_code,
        "abilities": monster.ability_lines or [],
        "loot": monster.loot,
    }


def build_entries(monsters: Sequence) -> List[dict]:
    return [_monster_entry(monster, idx) for idx, monster in enumerate(monsters, start=1)]


def write_yaml(entries: List[dict], output_path: Path) -> None:
    output_path.write_text(yaml.safe_dump(entries, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> None:
    output_path = PROJECT_ROOT / "rules" / "monsters" / "monsters.yaml"
    monsters = load_monsters()
    entries = build_entries(monsters)
    write_yaml(entries, output_path)
    print(f"Wrote {len(entries)} monsters to {output_path}")


if __name__ == "__main__":
    main()
