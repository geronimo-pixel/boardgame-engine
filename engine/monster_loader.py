"""
Utility helpers to parse the plain-text monster specification found in
``Original files/Monsters.txt`` and expose a structured representation that can
be consumed by simulators.

The source format lists, for each monster:
    - health, armor, attack, overkill, dice string
    - one or more ability lines describing skull-based bonuses
    - a loot line
    - the monster name on a separate, non-indented line

Example block (tabs omitted):
    1
    0
    1
    2
    2m
    1 sk = + 2Att
    2sk = + 2Att
    OC=+1Att
    2G
    Mush

The parser collects the numeric values, interprets skull-based ability lines,
and preserves any textual special effects so that combat engines can incorporate
them later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MONSTER_PATH = ROOT / "Original files" / "Monsters.txt"


@dataclass
class Monster:
    """Structured representation of a monster entry."""

    name: str
    rank: int
    health: int
    armor: int
    attack: int
    overkill: int
    dice_code: str
    loot: str
    ability_lines: List[str] = field(default_factory=list)
    skull_mapping: Dict[int, int] = field(default_factory=dict)
    overcharge_bonus: Optional[int] = None
    special_effects: List[str] = field(default_factory=list)

    def attack_bonus_for_skulls(self, skull_count: int) -> int:
        """
        Return the attack bonus granted by the ability mapping for the provided
        skull count. The rules define explicit bonuses for exact skull totals;
        if a total exceeds the highest defined key and an overcharge bonus is
        available, that bonus is applied once.
        """
        if skull_count <= 0:
            return 0

        if self.skull_mapping:
            # Prefer an exact match; otherwise fall back to the highest defined
            # key that does not exceed the current skull count.
            if skull_count in self.skull_mapping:
                bonus = self.skull_mapping[skull_count]
            else:
                # Find the highest key that's <= skull_count, then look up its bonus
                candidates = [key for key in self.skull_mapping if key <= skull_count]
                bonus = self.skull_mapping[max(candidates)] if candidates else 0
        else:
            bonus = 0

        max_defined = max(self.skull_mapping) if self.skull_mapping else 0
        if self.overcharge_bonus and skull_count > max_defined >= 0:
            bonus += self.overcharge_bonus

        return bonus

    def total_attack_for_skulls(self, skull_count: int) -> int:
        """Convenience helper returning base attack plus the computed bonus."""
        return self.attack + self.attack_bonus_for_skulls(skull_count)


def _clean_line(raw: str) -> str:
    """Normalise whitespace and strip non-ASCII characters."""
    return raw.strip().replace("\u00a0", " ").replace("\ufeff", "")


LOOT_PATTERN = re.compile(r"^\d+\s*G", re.IGNORECASE)
NAME_PATTERN = re.compile(r"^[A-Za-z\(][A-Za-z\s'\)\-]*$", re.IGNORECASE)
ABILITY_MAPPING_RE = re.compile(r"(?P<count>\d+)\s*sk.*?\+\s*(?P<bonus>\d+)\s*Att", re.IGNORECASE)
OVERCHARGE_RE = re.compile(r"OC.*?\+\s*(?P<bonus>\d+)\s*Att", re.IGNORECASE)


def _parse_ability_lines(lines: Iterable[str]) -> Tuple[Dict[int, int], Optional[int], List[str]]:
    mapping: Dict[int, int] = {}
    overcharge: Optional[int] = None
    specials: List[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        match = ABILITY_MAPPING_RE.match(line)
        if match:
            mapping[int(match.group("count"))] = int(match.group("bonus"))
            continue
        match = OVERCHARGE_RE.match(line)
        if match:
            overcharge = int(match.group("bonus"))
            continue
        specials.append(line)

    return mapping, overcharge, specials


def _finalise_entry(name: str, rank: int, block: List[str]) -> Monster:
    if len(block) < 6:
        raise ValueError(f"Incomplete monster block for '{name}': {block}")

    health, armor, attack, overkill = map(int, block[:4])
    dice_code = block[4]

    ability_lines: List[str] = []
    loot: Optional[str] = None

    for entry in block[5:]:
        if loot is None and ("G" in entry or "HoB" in entry or "Token" in entry or entry.endswith("T")):
            loot = entry
            continue
        if loot is None:
            ability_lines.append(entry)

    if loot is None:
        raise ValueError(f"Missing loot line for monster '{name}'. Block: {block}")

    mapping, overcharge, specials = _parse_ability_lines(ability_lines)

    return Monster(
        name=name,
        rank=rank,
        health=health,
        armor=armor,
        attack=attack,
        overkill=overkill,
        dice_code=dice_code,
        loot=loot,
        ability_lines=ability_lines,
        skull_mapping=mapping,
        overcharge_bonus=overcharge,
        special_effects=specials,
    )


def load_monsters(path: Path = DEFAULT_MONSTER_PATH) -> List[Monster]:
    """
    Parse the monster specification text file into Monster objects.

    Format in source file:
        Health
        Armor
        Attack
        Overkill
        Dice
        Ability lines (optional, multiple)
        Loot
        MonsterName  (name comes LAST)
    """
    if not path.exists():
        raise FileNotFoundError(f"Monster specification not found: {path}")

    raw_lines = [_clean_line(line) for line in path.read_text(encoding="utf-8").splitlines()]
    monsters: List[Monster] = []
    rank: Optional[int] = None
    idx = 0
    headers = {"Name", "Health", "Armor", "Attack", "Overkill", "Dice", "Ability", "Loot"}

    # Accumulator for current monster data block
    current_block: List[str] = []

    while idx < len(raw_lines):
        line = raw_lines[idx]
        idx += 1

        if not line:
            continue
        if line.upper().startswith("RANK"):
            try:
                rank = int(line.split()[1])
            except (IndexError, ValueError) as exc:
                raise ValueError(f"Unable to parse rank from line '{line}'") from exc
            continue
        if line in headers or line.startswith("Att="):
            continue

        if rank is None:
            raise ValueError(f"Encountered monster data '{line}' before any rank declaration.")

        lower_line = line.lower()
        # Check if this line is a monster name
        is_name = (NAME_PATTERN.match(line) and
                   not any(ch.isdigit() for ch in line) and
                   "=" not in line and
                   "+" not in line and
                   not lower_line.startswith("oc"))

        # Check if line looks like OC ability (should be part of data, not a name)
        is_oc_ability = lower_line.startswith("oc")

        if is_name and len(current_block) >= 6:
            # We've accumulated enough data (5 stats + at least 1 loot), this is the name
            monster = _finalise_entry(name=line, rank=rank, block=current_block)
            monsters.append(monster)
            current_block = []
        elif is_oc_ability or not is_name:
            # Continue accumulating data (stats, abilities, loot)
            current_block.append(line)

    return monsters


def get_monster_by_name(name: str, monsters: Optional[List[Monster]] = None) -> Monster:
    """Return the monster with the provided name."""
    entries = monsters or load_monsters()
    for monster in entries:
        if monster.name.lower() == name.lower():
            return monster
    raise KeyError(f"Monster '{name}' not found in specification.")
