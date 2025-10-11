"""
Lightweight combat simulation utilities built on top of the structured data
loaders.  This module currently focuses on scenarios that pit the Warrior hero
against a named monster, using the updated rule text from ``Original files``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import random
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .dice_loader import load_all_dice
from .monster_loader import Monster, get_monster_by_name, load_monsters


# --------------------------------------------------------------------------- #
# Dice helpers


@dataclass
class DiceTables:
    hero_faces: Dict[str, List[List[str]]]
    class_faces: Dict[str, List[List[str]]]
    monster_faces: Dict[str, List[int]]

    @classmethod
    def from_loader(cls) -> "DiceTables":
        dice = load_all_dice()
        hero_faces = {die.hero: die.faces for die in dice["hero_dice"]}
        class_faces = {die.hero: die.faces for die in dice["class_dice"]}
        monster_faces = {
            "m": next(die.skull_counts for die in dice["monster_dice"] if die.category == "minion"),
            "c": next(die.skull_counts for die in dice["monster_dice"] if die.category == "chief"),
            "b": next(die.skull_counts for die in dice["monster_dice"] if die.category == "boss"),
        }
        return cls(hero_faces=hero_faces, class_faces=class_faces, monster_faces=monster_faces)


DICE_CODE_PATTERN = re.compile(r"(?P<count>\d+)(?P<kind>[mcb])", re.IGNORECASE)


def parse_monster_dice_code(code: str) -> List[Tuple[int, str]]:
    """Parse strings like ``2m`` or ``1c+1m`` into a list of (count, kind)."""
    groups: List[Tuple[int, str]] = []
    for fragment in code.split("+"):
        fragment = fragment.strip()
        if not fragment:
            continue
        match = DICE_CODE_PATTERN.match(fragment)
        if not match:
            raise ValueError(f"Unable to parse monster dice fragment '{fragment}' from code '{code}'.")
        groups.append((int(match.group("count")), match.group("kind").lower()))
    return groups


# --------------------------------------------------------------------------- #
# Hero equipment resolution (square sword + square shield).


@dataclass
class EquipmentResult:
    attack: int = 0
    armor: int = 0
    used_attributes: Dict[str, int] = field(default_factory=lambda: {"square": 0, "circle": 0})
    description: str = ""


def _compute_square_sword_options(attribute_pool: Dict[str, int]) -> List[EquipmentResult]:
    squares = attribute_pool["square"]
    circles = attribute_pool["circle"]
    options: List[EquipmentResult] = []

    # Flat bonus only.
    options.append(EquipmentResult(attack=1, armor=0, description="sword flat"))

    if squares >= 1:
        options.append(
            EquipmentResult(
                attack=2,
                used_attributes={"square": 1, "circle": 0},
                description="sword base (1p)",
            )
        )

    if squares >= 1 and circles >= 1:
        options.append(
            EquipmentResult(
                attack=3,
                used_attributes={"square": 1, "circle": 1},
                description="sword combo (1p+1s)",
            )
        )
        if squares >= 2:
            options.append(
                EquipmentResult(
                    attack=4,
                    used_attributes={"square": 2, "circle": 1},
                    description="sword combo + overcharge",
                )
            )

    return options


def _compute_square_shield_options(attribute_pool: Dict[str, int]) -> List[EquipmentResult]:
    squares = attribute_pool["square"]
    circles = attribute_pool["circle"]
    options: List[EquipmentResult] = [
        EquipmentResult(attack=0, armor=1, description="shield flat"),
    ]

    if squares >= 1:
        options.append(
            EquipmentResult(
                attack=1,
                armor=1,
                used_attributes={"square": 1, "circle": 0},
                description="shield base (1p)",
            )
        )

    if squares >= 1 and circles >= 1:
        options.append(
            EquipmentResult(
                attack=2,
                armor=3,
                used_attributes={"square": 1, "circle": 1},
                description="shield combo (1p+1s) + overcharge",
            )
        )

    return options


def choose_best_weapon_configuration(attribute_pool: Dict[str, int]) -> Tuple[EquipmentResult, Dict[str, int]]:
    """Return the most damaging sword configuration along with the remaining attributes."""
    best_result: Optional[EquipmentResult] = None
    best_remaining: Dict[str, int] = {}

    for option in _compute_square_sword_options(attribute_pool):
        remaining = attribute_pool.copy()
        for key, amount in option.used_attributes.items():
            remaining[key] -= amount
        if best_result is None or option.attack > best_result.attack:
            best_result = option
            best_remaining = remaining

    assert best_result is not None
    return best_result, best_remaining


def choose_best_shield_configuration(attribute_pool: Dict[str, int]) -> Tuple[EquipmentResult, Dict[str, int]]:
    """
    Select the shield configuration that maximises (attack, armor) lexicographically.
    """
    best_result: Optional[EquipmentResult] = None
    best_remaining: Dict[str, int] = {}

    for option in _compute_square_shield_options(attribute_pool):
        remaining = attribute_pool.copy()
        for key, amount in option.used_attributes.items():
            remaining[key] -= amount
        if best_result is None or (option.attack, option.armor) > (best_result.attack, best_result.armor):
            best_result = option
            best_remaining = remaining

    assert best_result is not None
    return best_result, best_remaining


# --------------------------------------------------------------------------- #
# Combat simulation


@dataclass
class BoutLog:
    bout_number: int
    hero_face: List[str]
    class_faces: List[List[str]]
    sword: EquipmentResult
    shield: EquipmentResult
    remaining_attributes: Dict[str, int]
    rat_skulls: List[int]
    rat_attack: int
    rat_bonus_breakdown: str
    hero_attack: int
    hero_armor: int
    outcome: str


@dataclass
class CombatResult:
    winner: str
    bouts: List[BoutLog]
    final_hero_health: int
    final_monster_health: int


# --------------------------------------------------------------------------- #
# Hunter-specific simulation (triangle bow + CA #1 and CA #11).


@dataclass
class HunterBoutLog:
    bout_number: int
    hero_face: List[str]
    class_faces: List[List[str]]
    rerolls_used: int
    attribute_pool: Dict[str, int]
    attack_components: Dict[str, int]
    rat_skulls: List[int]
    rat_attack: int
    rat_bonus_breakdown: str
    hunter_attack: int
    outcome: str


@dataclass
class HunterCombatResult:
    winner: str
    bouts: List[HunterBoutLog]
    final_hunter_health: int
    final_monster_health: int


def _apply_rerolls_for_hunter(
    dice_tables: DiceTables,
    dice_faces: List[List[str]],
    dice_sources: List[str],
    rng: random.Random,
    rerolls_available: int,
) -> Tuple[List[List[str]], int]:
    """
    Heuristic reroll logic for Hunter CA #11 (reroll up to 2 dice during a hunt).
    - Prioritise obtaining at least one triangle (primary).
    - Then aim for at least one square (secondary).
    """

    faces = [face[:] for face in dice_faces]
    rerolls_used = 0

    def counts_from_faces() -> Dict[str, int]:
        pool = {"square": 0, "triangle": 0, "circle": 0}
        for face in faces:
            for symbol in face:
                pool[symbol] += 1
        return pool

    while rerolls_available > 0:
        pool = counts_from_faces()
        target_symbol: Optional[str] = None
        if pool["triangle"] == 0:
            target_symbol = "triangle"
        elif pool["square"] == 0:
            target_symbol = "square"
        else:
            break

        # Identify a die that does not currently contain the required symbol.
        try:
            idx_to_reroll = next(
                idx
                for idx, face in enumerate(faces)
                if target_symbol not in face
            )
        except StopIteration:
            break

        if dice_sources[idx_to_reroll] == "hero":
            faces[idx_to_reroll] = rng.choice(dice_tables.hero_faces["hunter"])
        else:
            faces[idx_to_reroll] = rng.choice(dice_tables.class_faces["hunter"])

        rerolls_available -= 1
        rerolls_used += 1

    return faces, rerolls_used


def _compute_hunter_attack(
    attribute_pool: Dict[str, int],
    stage: int,
) -> Tuple[int, Dict[str, int]]:
    """
    Calculate Hunter attack when wielding the triangle bow.
    Returns (total_attack, breakdown).
    """
    breakdown: Dict[str, int] = {}

    base_attack = 1 + 1  # flat + versus monsters
    breakdown["flat"] = base_attack

    ability_attack = 0
    if attribute_pool["triangle"] >= 1:
        ability_attack = 2
        if attribute_pool["square"] >= 1:
            ability_attack = 3
    breakdown["bow_effect"] = ability_attack

    ca1_bonus = {1: 1, 2: 2, 3: 3}.get(stage, 1)
    breakdown["CA1"] = ca1_bonus

    total_attack = base_attack + ability_attack + ca1_bonus
    return total_attack, breakdown


def simulate_hunter_triangle_bow_vs_monster(
    monster_name: str,
    *,
    stage: int = 1,
    seed: Optional[int] = None,
    max_bouts: int = 100,
) -> HunterCombatResult:
    rng = random.Random(seed)
    dice_tables = DiceTables.from_loader()
    monsters = load_monsters()
    monster = get_monster_by_name(monster_name, monsters)

    hunter_health = 5
    monster_health = monster.health
    monster_armor = monster.armor
    monster_armor_reinforcement = 0
    bouts: List[HunterBoutLog] = []
    bout_number = 1
    ca11_cooldown = 0

    while hunter_health > 0 and monster_health > 0 and bout_number <= max_bouts:
        # Roll dice
        hero_face = rng.choice(dice_tables.hero_faces["hunter"])
        class_face_a = rng.choice(dice_tables.class_faces["hunter"])
        class_face_b = rng.choice(dice_tables.class_faces["hunter"])
        dice_faces = [hero_face, class_face_a, class_face_b]
        dice_sources = ["hero", "class", "class"]

        rerolls_used = 0
        if ca11_cooldown == 0:
            dice_faces, rerolls_used = _apply_rerolls_for_hunter(
                dice_tables, dice_faces, dice_sources, rng, rerolls_available=2
            )
            if rerolls_used > 0:
                ca11_cooldown = 2

        # Count attributes
        attribute_pool = {"square": 0, "triangle": 0, "circle": 0}
        for face in dice_faces:
            for symbol in face:
                attribute_pool[symbol] += 1

        hunter_attack, breakdown = _compute_hunter_attack(attribute_pool, stage)

        skulls, monster_attack, bonus_text, armor_bonus = _roll_monster_skulls(monster, dice_tables, rng)
        if armor_bonus:
            if monster_armor > 0:
                monster_armor_reinforcement += armor_bonus
                bonus_text += f"; armor reinforcement +{armor_bonus} (total {monster_armor_reinforcement})"
            else:
                bonus_text += "; armor reinforcement failed (armor already broken)"

        # Hunter does NOT have tie-breaker ability (unlike Warrior)
        # Must beat monster to win
        if hunter_attack > monster_attack:
            outcome = "Hunter wins bout"
            if monster_armor > 0:
                if monster_armor_reinforcement > 0:
                    monster_armor_reinforcement -= 1
                    outcome += f" - armor reinforcement absorbs blow ({monster_armor_reinforcement} remaining)"
                else:
                    monster_armor = 0
                    monster_armor_reinforcement = 0
                    outcome += " - monster armor broken"
            else:
                monster_health -= 1
        else:
            outcome = "Monster wins bout"
            if hunter_attack == monster_attack:
                outcome += " (tie)"
            hunter_health -= 1

        bouts.append(
            HunterBoutLog(
                bout_number=bout_number,
                hero_face=dice_faces[0],
                class_faces=dice_faces[1:],
                rerolls_used=rerolls_used,
                attribute_pool=attribute_pool,
                attack_components=breakdown,
                rat_skulls=skulls,
                rat_attack=monster_attack,
                rat_bonus_breakdown=bonus_text,
                hunter_attack=hunter_attack,
                outcome=outcome,
            )
        )

        if ca11_cooldown > 0:
            ca11_cooldown -= 1
        bout_number += 1

    winner = "Hunter" if monster_health <= 0 else ("Monster" if hunter_health <= 0 else "Undecided")
    return HunterCombatResult(
        winner=winner,
        bouts=bouts,
        final_hunter_health=hunter_health,
        final_monster_health=monster_health,
    )


def _roll_hero_attributes(dice_tables: DiceTables, rng: random.Random) -> Tuple[List[str], List[List[str]], Dict[str, int]]:
    hero_face = rng.choice(dice_tables.hero_faces["warrior"])
    class_faces = [rng.choice(dice_tables.class_faces["warrior"]) for _ in range(2)]

    pool = {"square": 0, "triangle": 0, "circle": 0}
    for symbol in hero_face:
        pool[symbol] += 1
    for face in class_faces:
        for symbol in face:
            pool[symbol] += 1

    return hero_face, class_faces, pool


def _roll_monster_skulls(
    monster: Monster, dice_tables: DiceTables, rng: random.Random
) -> Tuple[List[int], int, str, int]:
    skulls: List[int] = []
    bonus_notes: List[str] = []
    for count, kind in parse_monster_dice_code(monster.dice_code):
        die_faces = dice_tables.monster_faces[kind]
        for _ in range(count):
            skulls.append(rng.choice(die_faces))

    total_skulls = sum(skulls)
    bonus = monster.attack_bonus_for_skulls(total_skulls)
    max_defined = max(monster.skull_mapping) if monster.skull_mapping else 0
    exceeded_table = total_skulls > max_defined >= 0
    if total_skulls in monster.skull_mapping:
        bonus_notes.append(f"{total_skulls} skull -> +{monster.skull_mapping[total_skulls]} attack")
    elif total_skulls > 0:
        # Fallback to highest defined bonus if exceeded.
        candidates = [key for key in monster.skull_mapping if key <= total_skulls]
        if candidates:
            key = max(candidates)
            bonus_notes.append(f"{total_skulls} skulls -> using {key}-skull bonus +{monster.skull_mapping[key]} attack")
    if monster.overcharge_attack_bonus and exceeded_table:
        bonus_notes.append(f"overcharge +{monster.overcharge_attack_bonus} attack")

    armor_bonus = 0
    if monster.overcharge_armor_bonus and exceeded_table:
        armor_bonus = monster.overcharge_armor_bonus
        bonus_notes.append(f"overcharge +{armor_bonus} armor (if armor intact)")

    bonus_text = "; ".join(bonus_notes) if bonus_notes else "no ability bonus"
    total_attack = monster.attack + bonus
    return skulls, total_attack, bonus_text, armor_bonus


def simulate_warrior_vs_monster(
    monster_name: str,
    *,
    seed: Optional[int] = None,
    max_bouts: int = 100,
    log_special_effects: bool = True,
    dice_tables: Optional[DiceTables] = None,
    monsters: Optional[Sequence[Monster]] = None,
) -> CombatResult:
    """
    Simulate a combat between the Warrior (equipped with the square sword and square
    shield) and the requested monster.  The warrior automatically wins ties thanks
    to Class Ability #2.
    """
    rng = random.Random(seed)
    dice_tables = dice_tables or DiceTables.from_loader()
    monsters_dataset = monsters or load_monsters()
    monster = get_monster_by_name(monster_name, monsters_dataset)

    warrior_health = 5
    monster_health = monster.health
    monster_armor = monster.armor  # Track monster armor (breaks on first loss)
    monster_armor_reinforcement = 0  # Extra armor layers granted via OC abilities
    hero_armor_broken = False  # Equipment armor can't return once broken
    bouts: List[BoutLog] = []
    bout_number = 1

    while warrior_health > 0 and monster_health > 0 and bout_number <= max_bouts:
        hero_face, class_faces, attribute_pool = _roll_hero_attributes(dice_tables, rng)
        sword_choice, remaining_after_sword = choose_best_weapon_configuration(attribute_pool)
        shield_choice, remaining_after_shield = choose_best_shield_configuration(remaining_after_sword)

        hero_attack = sword_choice.attack + shield_choice.attack
        hero_armor = 0 if hero_armor_broken else shield_choice.armor

        skulls, monster_attack, bonus_text, armor_bonus = _roll_monster_skulls(monster, dice_tables, rng)
        if armor_bonus:
            if monster_armor > 0:
                monster_armor_reinforcement += armor_bonus
                bonus_text += f"; armor reinforcement +{armor_bonus} (total {monster_armor_reinforcement})"
            else:
                bonus_text += "; armor reinforcement failed (armor already broken)"

        # Warrior CA#2: Always wins ties
        if hero_attack >= monster_attack:
            outcome = "Warrior wins bout"
            if hero_attack == monster_attack:
                outcome += " (tie-breaker: CA#2)"
            # Monster loses armor first, then health
            if monster_armor > 0:
                if monster_armor_reinforcement > 0:
                    monster_armor_reinforcement -= 1
                    outcome += f" - armor reinforcement absorbs blow ({monster_armor_reinforcement} remaining)"
                else:
                    monster_armor = 0
                    monster_armor_reinforcement = 0
                    outcome += " - monster armor broken"
            else:
                monster_health -= 1
        else:
            outcome = "Monster wins bout"
            # Hero loses armor first, then health
            if hero_armor > 0:
                hero_armor = 0
                hero_armor_broken = True
                outcome += " - hero armor broken"
            else:
                warrior_health -= 1

        bouts.append(
            BoutLog(
                bout_number=bout_number,
                hero_face=hero_face,
                class_faces=class_faces,
                sword=sword_choice,
                shield=shield_choice,
                remaining_attributes=remaining_after_shield,
                rat_skulls=skulls,
                rat_attack=monster_attack,
                rat_bonus_breakdown=bonus_text,
                hero_attack=hero_attack,
                hero_armor=hero_armor,
                outcome=outcome,
            )
        )

        bout_number += 1

    winner = "Warrior" if monster_health <= 0 else ("Monster" if warrior_health <= 0 else "Undecided")
    return CombatResult(
        winner=winner,
        bouts=bouts,
        final_hero_health=warrior_health,
        final_monster_health=monster_health,
    )
