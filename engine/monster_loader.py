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
    overcharge_attack_bonus: Optional[int] = None
    overcharge_armor_bonus: Optional[int] = None
    special_effects: List[str] = field(default_factory=list)

    @property
    def overcharge_bonus(self) -> Optional[int]:
        """Backward-compatible alias for attack overcharge."""
        return self.overcharge_attack_bonus

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
        if self.overcharge_attack_bonus and skull_count > max_defined >= 0:
            bonus += self.overcharge_attack_bonus

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
OVERCHARGE_ATTACK_RE = re.compile(r"OC.*?\+\s*(?P<bonus>\d+)\s*Att", re.IGNORECASE)
OVERCHARGE_ARMOR_RE = re.compile(r"OC.*?\+\s*(?P<bonus>\d+)\s*Ar", re.IGNORECASE)


def _parse_ability_lines(lines: Iterable[str]) -> Tuple[Dict[int, int], Optional[int], Optional[int], List[str]]:
    mapping: Dict[int, int] = {}
    overcharge_attack: Optional[int] = None
    overcharge_armor: Optional[int] = None
    specials: List[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        match = ABILITY_MAPPING_RE.match(line)
        if match:
            mapping[int(match.group("count"))] = int(match.group("bonus"))
            continue
        match = OVERCHARGE_ATTACK_RE.match(line)
        if match:
            overcharge_attack = int(match.group("bonus"))
            continue
        match = OVERCHARGE_ARMOR_RE.match(line)
        if match:
            overcharge_armor = int(match.group("bonus"))
            continue
        specials.append(line)

    return mapping, overcharge_attack, overcharge_armor, specials


def _is_dice_line(entry: str) -> bool:
    candidate = entry.replace(" ", "")
    if not candidate:
        return False
    for segment in candidate.split("+"):
        if not segment:
            return False
        if not segment[:-1].isdigit():
            return False
        if segment[-1].lower() not in {"m", "c", "b"}:
            return False
    return True


def _trim_to_latest_block(block: List[str]) -> List[str]:
    """
    Some source sections accidentally accumulate multiple monster stat blocks
    before a name is encountered (for example, Orca followed by (blue)).  When
    that happens we only want the most recent contiguous block immediately
    preceding the name.  This helper slices the provided block to that suffix.
    """
    if len(block) < 6:
        return block

    dice_index: Optional[int] = None
    for idx in range(len(block) - 1, -1, -1):
        entry = block[idx]
        if _is_dice_line(entry):
            dice_index = idx
            break

    if dice_index is None:
        return block

    digit_indices: List[int] = []
    for idx in range(dice_index - 1, -1, -1):
        entry = block[idx]
        if entry.isdigit():
            digit_indices.append(idx)
            if len(digit_indices) == 4:
                break
        else:
            digit_indices.clear()

    if len(digit_indices) < 4:
        return block

    start_idx = sorted(digit_indices)[0]
    return block[start_idx:]


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

    mapping, overcharge_attack, overcharge_armor, specials = _parse_ability_lines(ability_lines)

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
        overcharge_attack_bonus=overcharge_attack,
        overcharge_armor_bonus=overcharge_armor,
        special_effects=specials,
    )


def load_monsters(path: Path = DEFAULT_MONSTER_PATH) -> List[Monster]:
    """
    Parse the monster specification text file into Monster objects.

    Format in source file:
        MonsterName
        Health
        Armor
        Attack
        Overkill
        Dice
        Ability lines (optional, multiple)
        Loot
    """
    if not path.exists():
        raise FileNotFoundError(f"Monster specification not found: {path}")

    raw_lines = [_clean_line(line) for line in path.read_text(encoding="utf-8").splitlines()]
    monsters: List[Monster] = []
    rank: Optional[int] = None
    idx = 0
    headers = {"Name", "Health", "Armor", "Attack", "Overkill", "Dice", "Ability", "Loot"}

    pending_name: Optional[str] = None
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
        is_name = (
            NAME_PATTERN.match(line)
            and not any(ch.isdigit() for ch in line)
            and "=" not in line
            and "+" not in line
            and not lower_line.startswith("oc")
        )

        if is_name:
            if pending_name is not None and current_block:
                block = _trim_to_latest_block(current_block)
                monster = _finalise_entry(name=pending_name, rank=rank, block=block)
                monsters.append(monster)
                current_block = []
            pending_name = line
            continue

        # Otherwise, accumulate data for the current monster block.
        current_block.append(line)

    if pending_name is not None and current_block:
        block = _trim_to_latest_block(current_block)
        monster = _finalise_entry(name=pending_name, rank=rank, block=block)
        monsters.append(monster)

    return monsters


def get_monster_by_name(name: str, monsters: Optional[List[Monster]] = None) -> Monster:
    """Return the monster with the provided name."""
    entries = monsters or load_monsters()
    for monster in entries:
        if monster.name.lower() == name.lower():
            return monster
    raise KeyError(f"Monster '{name}' not found in specification.")
