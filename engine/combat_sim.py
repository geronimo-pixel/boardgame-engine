"""
Lightweight combat simulation utilities built on top of the structured data
loaders.  This module currently focuses on scenarios that pit the Warrior hero
against a named monster, using the updated rule text from ``Original files``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter
from pathlib import Path
import random
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .dice_loader import load_all_dice
from .monster_loader import Monster, get_monster_by_name, load_monsters


# --------------------------------------------------------------------------- #
# Dice helpers


@dataclass
class DiceTables:
    hero_faces: Dict[str, List[List[str]]]
    class_faces: Dict[str, List[List[str]]]
    monster_faces: Dict[str, List[int]]
    blank_faces: List[List[str]]

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
        blank_faces = [face[:] for face in dice["blank_die"]]
        return cls(
            hero_faces=hero_faces,
            class_faces=class_faces,
            monster_faces=monster_faces,
            blank_faces=blank_faces,
        )

    def blank_die(self) -> List[List[str]]:
        """Return a copy of the blank die faces."""
        return [face[:] for face in self.blank_faces]


DICE_CODE_PATTERN = re.compile(r"(?P<count>\d+)(?P<kind>[mcb])", re.IGNORECASE)


@dataclass(frozen=True)
class HeroDiceConfig:
    """
    Configuration describing how many hero/class dice a character rolls as their class
    abilities unlock.
    """

    hero_dice: int = 1
    class_dice_progression: Tuple[Tuple[int, int], ...] = ((0, 1), (6, 2))
    default_hero_abilities: int = 1
    default_class_abilities: int = 6


@dataclass
class HeroRollResult:
    hero: str
    hero_faces: List[List[str]]
    class_faces: List[List[str]]
    attribute_pool: Dict[str, int]
    hero_dice_rolled: int
    class_dice_rolled: int
    hero_abilities: int
    class_abilities: int


HERO_DICE_CONFIGS: Dict[str, HeroDiceConfig] = {
    "warrior": HeroDiceConfig(),
    "sentinel": HeroDiceConfig(),
    "mage": HeroDiceConfig(),
    "shaman": HeroDiceConfig(),
    "thief": HeroDiceConfig(),
    "hunter": HeroDiceConfig(),
    "mercenary": HeroDiceConfig(),
}


def _class_dice_for_abilities(config: HeroDiceConfig, ability_count: int) -> int:
    """
    Determine the number of class dice to roll based on unlocked abilities.

    The progression is ordered by the minimum ability count required. We pick the highest
    entry that does not exceed ``ability_count``.
    """

    class_dice = 0
    for threshold, dice in config.class_dice_progression:
        if ability_count >= threshold:
            class_dice = dice
        else:
            break
    return class_dice


def _aggregate_attribute_pool(faces: Iterable[Iterable[str]]) -> Dict[str, int]:
    """
    Convert rolled faces into an attribute counter (square/triangle/circle/blank).
    """

    pool: Dict[str, int] = {"square": 0, "triangle": 0, "circle": 0, "blank": 0}
    for face in faces:
        for symbol in face:
            if symbol == "null":
                continue
            if symbol == "blank":
                pool["blank"] += 1
            else:
                pool.setdefault(symbol, 0)
                pool[symbol] += 1
    return pool


def _roll_generic_hero_dice(
    hero: str,
    dice_tables: DiceTables,
    rng: random.Random,
    *,
    hero_abilities: Optional[int] = None,
    class_abilities: Optional[int] = None,
    hero_dice_override: Optional[int] = None,
    class_dice_override: Optional[int] = None,
) -> HeroRollResult:
    """
    Entry point used by the hero-specific wrappers to generate dice rolls.
    """

    hero_lower = hero.lower()
    if hero_lower not in HERO_DICE_CONFIGS:
        raise KeyError(f"Hero '{hero}' does not have a dice configuration.")

    config = HERO_DICE_CONFIGS[hero_lower]
    hero_ability_count = config.default_hero_abilities if hero_abilities is None else hero_abilities
    class_ability_count = (
        config.default_class_abilities if class_abilities is None else class_abilities
    )

    hero_dice_to_roll = hero_dice_override if hero_dice_override is not None else config.hero_dice
    class_dice_to_roll = (
        class_dice_override
        if class_dice_override is not None
        else _class_dice_for_abilities(config, class_ability_count)
    )

    hero_faces: List[List[str]] = []
    for _ in range(hero_dice_to_roll):
        hero_faces.append(list(rng.choice(dice_tables.hero_faces[hero_lower])))

    class_faces: List[List[str]] = []
    if class_dice_to_roll > 0:
        class_faces = [list(rng.choice(dice_tables.class_faces[hero_lower])) for _ in range(class_dice_to_roll)]

    attribute_pool = _aggregate_attribute_pool([*hero_faces, *class_faces])

    return HeroRollResult(
        hero=hero_lower,
        hero_faces=hero_faces,
        class_faces=class_faces,
        attribute_pool=attribute_pool,
        hero_dice_rolled=hero_dice_to_roll,
        class_dice_rolled=class_dice_to_roll,
        hero_abilities=hero_ability_count,
        class_abilities=class_ability_count,
    )


def roll_warrior_dice(
    dice_tables: DiceTables,
    rng: random.Random,
    *,
    hero_abilities: Optional[int] = None,
    class_abilities: Optional[int] = None,
    hero_dice_override: Optional[int] = None,
    class_dice_override: Optional[int] = None,
) -> HeroRollResult:
    """Roll the warrior hero + class dice."""

    return _roll_generic_hero_dice(
        "warrior",
        dice_tables,
        rng,
        hero_abilities=hero_abilities,
        class_abilities=class_abilities,
        hero_dice_override=hero_dice_override,
        class_dice_override=class_dice_override,
    )


def roll_mage_dice(
    dice_tables: DiceTables,
    rng: random.Random,
    *,
    hero_abilities: Optional[int] = None,
    class_abilities: Optional[int] = None,
    hero_dice_override: Optional[int] = None,
    class_dice_override: Optional[int] = None,
) -> HeroRollResult:
    """Roll the mage hero + class dice."""

    return _roll_generic_hero_dice(
        "mage",
        dice_tables,
        rng,
        hero_abilities=hero_abilities,
        class_abilities=class_abilities,
        hero_dice_override=hero_dice_override,
        class_dice_override=class_dice_override,
    )


def roll_sentinel_dice(
    dice_tables: DiceTables,
    rng: random.Random,
    *,
    hero_abilities: Optional[int] = None,
    class_abilities: Optional[int] = None,
    hero_dice_override: Optional[int] = None,
    class_dice_override: Optional[int] = None,
) -> HeroRollResult:
    """Roll the sentinel hero + class dice."""

    return _roll_generic_hero_dice(
        "sentinel",
        dice_tables,
        rng,
        hero_abilities=hero_abilities,
        class_abilities=class_abilities,
        hero_dice_override=hero_dice_override,
        class_dice_override=class_dice_override,
    )


def roll_shaman_dice(
    dice_tables: DiceTables,
    rng: random.Random,
    *,
    hero_abilities: Optional[int] = None,
    class_abilities: Optional[int] = None,
    hero_dice_override: Optional[int] = None,
    class_dice_override: Optional[int] = None,
) -> HeroRollResult:
    """Roll the shaman hero + class dice."""

    return _roll_generic_hero_dice(
        "shaman",
        dice_tables,
        rng,
        hero_abilities=hero_abilities,
        class_abilities=class_abilities,
        hero_dice_override=hero_dice_override,
        class_dice_override=class_dice_override,
    )


def roll_thief_dice(
    dice_tables: DiceTables,
    rng: random.Random,
    *,
    hero_abilities: Optional[int] = None,
    class_abilities: Optional[int] = None,
    hero_dice_override: Optional[int] = None,
    class_dice_override: Optional[int] = None,
) -> HeroRollResult:
    """Roll the thief hero + class dice."""

    return _roll_generic_hero_dice(
        "thief",
        dice_tables,
        rng,
        hero_abilities=hero_abilities,
        class_abilities=class_abilities,
        hero_dice_override=hero_dice_override,
        class_dice_override=class_dice_override,
    )


def roll_hunter_dice(
    dice_tables: DiceTables,
    rng: random.Random,
    *,
    hero_abilities: Optional[int] = None,
    class_abilities: Optional[int] = None,
    hero_dice_override: Optional[int] = None,
    class_dice_override: Optional[int] = None,
) -> HeroRollResult:
    """Roll the hunter hero + class dice (without rerolls)."""

    return _roll_generic_hero_dice(
        "hunter",
        dice_tables,
        rng,
        hero_abilities=hero_abilities,
        class_abilities=class_abilities,
        hero_dice_override=hero_dice_override,
        class_dice_override=class_dice_override,
    )


def roll_mercenary_dice(
    dice_tables: DiceTables,
    rng: random.Random,
    *,
    hero_abilities: Optional[int] = None,
    class_abilities: Optional[int] = None,
    hero_dice_override: Optional[int] = None,
    class_dice_override: Optional[int] = None,
) -> HeroRollResult:
    """Roll the mercenary hero + class dice."""

    return _roll_generic_hero_dice(
        "mercenary",
        dice_tables,
        rng,
        hero_abilities=hero_abilities,
        class_abilities=class_abilities,
        hero_dice_override=hero_dice_override,
        class_dice_override=class_dice_override,
    )


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
    armor_damage: int = 0
    used_attributes: Dict[str, int] = field(default_factory=lambda: {"square": 0, "triangle": 0, "circle": 0})
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


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


def _deduct_attributes(pool: Dict[str, int], requirements: Dict[str, int]) -> Optional[Dict[str, int]]:
    """
    Return a copy of ``pool`` with the requested attributes consumed. Blank results act as wildcards
    and can satisfy any single attribute requirement. If the requirements cannot be satisfied, return ``None``.
    """
    remaining = pool.copy()
    blanks = remaining.get("blank", 0)

    for attr, needed in requirements.items():
        if needed <= 0:
            continue
        available = remaining.get(attr, 0)
        if available >= needed:
            remaining[attr] = available - needed
        else:
            deficit = needed - available
            if blanks >= deficit:
                remaining[attr] = 0
                blanks -= deficit
            else:
                return None

    remaining["blank"] = blanks
    return remaining


def _can_satisfy(pool: Dict[str, int], requirements: Dict[str, int]) -> bool:
    """Return True if the requirements can be fulfilled using the provided pool (blank counts as a wildcard)."""
    blanks = pool.get("blank", 0)
    for attr, needed in requirements.items():
        if needed <= 0:
            continue
        available = pool.get(attr, 0)
        if available >= needed:
            continue
        blanks -= needed - available
        if blanks < 0:
            return False
    return True


def choose_best_weapon_configuration(attribute_pool: Dict[str, int]) -> Tuple[EquipmentResult, Dict[str, int]]:
    """Return the most damaging sword configuration along with the remaining attributes."""
    best_result: Optional[EquipmentResult] = None
    best_remaining: Dict[str, int] = {}

    for option in _compute_square_sword_options(attribute_pool):
        remaining = _deduct_attributes(attribute_pool, option.used_attributes)
        if remaining is None:
            continue
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
        remaining = _deduct_attributes(attribute_pool, option.used_attributes)
        if remaining is None:
            continue
        if best_result is None or (option.attack, option.armor) > (best_result.attack, best_result.armor):
            best_result = option
            best_remaining = remaining

    assert best_result is not None
    return best_result, best_remaining


# --------------------------------------------------------------------------- #
# Core combat abstractions


@dataclass
class LoadoutAbility:
    """Representation of an equipped ability (hero or class) for a combat loadout."""

    name: str
    description: str = ""


@dataclass
class EquipmentItem:
    """Representation of an equipped item (weapon, armor, charm)."""

    name: str
    category: str
    slot: Optional[str] = None
    hands: int = 0  # 0 -> not a hand slot item; otherwise number of hands required
    provides_armor: int = 0  # Flat armor granted at pre-combat (e.g., chainmail)
    attributes: Dict[str, Optional[str]] = field(default_factory=dict)
    activations: List[Dict[str, Any]] = field(default_factory=list)
    flat_bonuses: List[Dict[str, Any]] = field(default_factory=list)
    overcharge_effects: List[Dict[str, Any]] = field(default_factory=list)
    state_modifiers: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class HeroProfile:
    """Hero baseline statistics used as part of a combat loadout."""

    name: str
    max_health: int = 5
    base_armor: int = 0


@dataclass
class PreCombatState:
    """Initial combat state derived from a loadout (health, armor, cooldowns)."""

    health: int
    armor: int
    cooldowns: Dict[str, int]


@dataclass
class CombatLoadout:
    """Bundle describing the hero, equipped abilities, and gear used in combat."""

    hero_profile: HeroProfile
    abilities: List[LoadoutAbility] = field(default_factory=list)
    equipment: List[EquipmentItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def hero(self) -> str:
        return self.hero_profile.name

    def create_pre_combat_state(self) -> PreCombatState:
        base_armor = self.hero_profile.base_armor
        for item in self.equipment:
            base_armor += max(0, item.provides_armor)

        cooldowns = {
            ability.name: 0
            for ability in self.abilities
            if ability.name
        }
        return PreCombatState(
            health=self.hero_profile.max_health,
            armor=base_armor,
            cooldowns=cooldowns,
        )


@dataclass
class DiceRollContext:
    """Snapshot of a hero's dice results for a single bout."""

    hero_faces: List[List[str]]
    class_faces: List[List[str]]
    attribute_pool: Dict[str, int]
    hero_dice_rolled: int
    class_dice_rolled: int
    hero_abilities_available: int
    class_abilities_available: int
    extras: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EquipmentResolution:
    """Aggregated offensive/defensive output produced by the equipped items."""

    attack: int
    armor: int
    armor_damage: int
    weapon: EquipmentResult
    secondary: EquipmentResult
    remaining_attributes: Dict[str, int]
    metadata: Dict[str, Any] = field(default_factory=dict)


class LoadoutValidationError(ValueError):
    """Raised when a loadout violates equipment slot rules."""


class LoadoutBuilder:
    """Helper to assemble and validate combat loadouts."""

    SLOT_LIMITS: Dict[str, int] = {
        "hand": 2,
        "chest": 1,
        "legs": 1,
        "arms": 1,
        "ring": 2,
        "crown": 1,
    }

    def __init__(self, hero_profiles: Optional[Dict[str, HeroProfile]] = None) -> None:
        self._hero_profiles: Dict[str, HeroProfile] = hero_profiles or {}

    def register_hero(self, profile: HeroProfile) -> None:
        self._hero_profiles[profile.name.lower()] = profile

    def build(
        self,
        hero_name: str,
        abilities: Optional[List[LoadoutAbility]] = None,
        equipment: Optional[List[EquipmentItem]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CombatLoadout:
        profile = self._hero_profiles.get(hero_name.lower())
        if profile is None:
            raise LoadoutValidationError(f"Unknown hero profile '{hero_name}'.")

        abilities = abilities or []
        equipment = equipment or []
        self._validate_equipment(equipment)

        loadout = CombatLoadout(
            hero_profile=profile,
            abilities=abilities,
            equipment=equipment,
        )
        if metadata:
            loadout.metadata.update(metadata)
        return loadout

    def _validate_equipment(self, equipment: List[EquipmentItem]) -> None:
        hand_usage = 0
        slot_counts: Dict[str, int] = {}

        for item in equipment:
            slot = item.slot or ""
            if slot == "hand":
                hand_usage += max(0, item.hands)
            elif slot:
                slot_counts[slot] = slot_counts.get(slot, 0) + 1
                limit = self.SLOT_LIMITS.get(slot, 1)
                if slot_counts[slot] > limit:
                    raise LoadoutValidationError(
                        f"Too many items equipped in slot '{slot}'. Limit is {limit}."
                    )

        if hand_usage > self.SLOT_LIMITS["hand"]:
            raise LoadoutValidationError(
                f"Equipped items require {hand_usage} hands; limit is {self.SLOT_LIMITS['hand']}."
            )


class DiceRoller:
    """Roll hero + class dice using the configured loadout."""

    def roll(
        self,
        loadout: CombatLoadout,
        dice_tables: DiceTables,
        rng: random.Random,
        context: Optional[Dict[str, Any]] = None,
    ) -> DiceRollContext:
        context = context or {}
        hero_key = loadout.hero.lower()
        if hero_key == "warrior":
            roll = roll_warrior_dice(dice_tables, rng)
            return DiceRollContext(
                hero_faces=roll.hero_faces,
                class_faces=roll.class_faces,
                attribute_pool=roll.attribute_pool,
                hero_dice_rolled=roll.hero_dice_rolled,
                class_dice_rolled=roll.class_dice_rolled,
                hero_abilities_available=roll.hero_abilities,
                class_abilities_available=roll.class_abilities,
            )
        if hero_key == "hunter":
            hero_face = rng.choice(dice_tables.hero_faces["hunter"])
            class_face_a = rng.choice(dice_tables.class_faces["hunter"])
            class_face_b = rng.choice(dice_tables.class_faces["hunter"])
            dice_faces = [hero_face, class_face_a, class_face_b]
            dice_sources = ["hero", "class", "class"]

            rerolls_used = 0
            ca11_enabled = context.get("ca11_enabled", True)
            ca11_cooldown = context.get("ca11_cooldown", 0)
            if ca11_enabled and ca11_cooldown == 0:
                dice_faces, rerolls_used = _apply_rerolls_for_hunter(
                    dice_tables, dice_faces, dice_sources, rng, rerolls_available=2
                )
                if rerolls_used > 0:
                    context["ca11_cooldown"] = context.get("ca11_cooldown_reset", 2)
                else:
                    context["ca11_cooldown"] = 0
            else:
                context["ca11_cooldown"] = max(0, ca11_cooldown - 1)

            attribute_pool = {"square": 0, "triangle": 0, "circle": 0, "blank": 0}
            for face in dice_faces:
                for symbol in face:
                    attribute_pool.setdefault(symbol, 0)
                    attribute_pool[symbol] += 1

            return DiceRollContext(
                hero_faces=[dice_faces[0]],
                class_faces=dice_faces[1:],
                attribute_pool=attribute_pool,
                hero_dice_rolled=1,
                class_dice_rolled=2,
                hero_abilities_available=0,
                class_abilities_available=0,
                extras={"rerolls_used": rerolls_used},
            )
        roll = _roll_generic_hero_dice(
            hero_key,
            dice_tables,
            rng,
            hero_abilities=context.get("hero_abilities"),
            class_abilities=context.get("class_abilities"),
            hero_dice_override=context.get("hero_dice_override"),
            class_dice_override=context.get("class_dice_override"),
        )
        return DiceRollContext(
            hero_faces=roll.hero_faces,
            class_faces=roll.class_faces,
            attribute_pool=roll.attribute_pool,
            hero_dice_rolled=roll.hero_dice_rolled,
            class_dice_rolled=roll.class_dice_rolled,
            hero_abilities_available=roll.hero_abilities,
            class_abilities_available=roll.class_abilities,
        )


class EquipmentPipeline:
    """Convert raw attribute pools into attack/defense values based on equipped gear."""

    def resolve(
        self,
        loadout: CombatLoadout,
        attribute_pool: Dict[str, int],
        context: Optional[Dict[str, Any]] = None,
    ) -> EquipmentResolution:
        context = context or {}
        hero_key = loadout.hero.lower()
        working_pool = attribute_pool.copy()

        if hero_key == "warrior":
            weapon, remaining_after_weapon = choose_best_weapon_configuration(working_pool)
            shield, remaining_after_shield = choose_best_shield_configuration(remaining_after_weapon)
            attack = weapon.attack + shield.attack
            armor = shield.armor
            armor_damage = 0
            return EquipmentResolution(
                attack=attack,
                armor=armor,
                armor_damage=armor_damage,
                weapon=weapon,
                secondary=shield,
                remaining_attributes=remaining_after_shield,
                metadata={"weapon_description": weapon.description, "shield_description": shield.description},
            )

        if hero_key == "hunter":
            stage = context.get("stage", 1)
            attack, breakdown = _compute_hunter_attack(working_pool, stage)
            weapon = EquipmentResult(
                attack=attack,
                armor=0,
                description="triangle bow attack",
            )
            return EquipmentResolution(
                attack=attack,
                armor=0,
                armor_damage=0,
                weapon=weapon,
                secondary=EquipmentResult(),
                remaining_attributes=working_pool,
                metadata={"attack_breakdown": breakdown},
            )

        return _resolve_generic_equipment(loadout, working_pool)


class AbilityEngine:
    """Evaluate loadout abilities and provide combat-time helpers (e.g. tie-breakers)."""

    def __init__(self, loadout: CombatLoadout) -> None:
        tokens: List[str] = []
        for ability in loadout.abilities:
            if ability.name:
                tokens.append(ability.name.lower())
            if ability.description:
                tokens.append(ability.description.lower())

        self.auto_win_ties = any("always wins ties" in token for token in tokens)

    def hero_wins_bout(self, hero_attack: int, monster_attack: int) -> bool:
        if hero_attack > monster_attack:
            return True
        if hero_attack == monster_attack and self.auto_win_ties:
            return True
        return False

    def tie_note(self, hero_attack: int, monster_attack: int) -> Optional[str]:
        if hero_attack == monster_attack and self.auto_win_ties:
            return " (tie-breaker: CA#2)"
        return None


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
    hero_dice_rolled: int = 1
    class_dice_rolled: int = 0
    hero_abilities: int = 0
    class_abilities: int = 0
    hero_faces_all: List[List[str]] = field(default_factory=list)


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
        pool = {"square": 0, "triangle": 0, "circle": 0, "blank": 0}
        for face in faces:
            for symbol in face:
                if symbol == "null":
                    continue
                if symbol == "blank":
                    pool["blank"] += 1
                else:
                    pool.setdefault(symbol, 0)
                    pool[symbol] += 1
        return pool

    while rerolls_available > 0:
        pool = counts_from_faces()
        target_symbol: Optional[str] = None
        if pool["triangle"] == 0 and pool["blank"] == 0:
            target_symbol = "triangle"
        elif pool["square"] == 0 and pool["blank"] == 0:
            target_symbol = "square"
        else:
            break

        # Identify a die that does not currently contain the required symbol.
        try:
            idx_to_reroll = next(
                idx
                for idx, face in enumerate(faces)
                if target_symbol not in face and "blank" not in face
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

    builder = LoadoutBuilder({"hunter": HeroProfile(name="hunter", max_health=5, base_armor=0)})
    loadout = builder.build(
        hero_name="hunter",
        abilities=[
            LoadoutAbility(name="CA #1", description="Stage-based attack bonus"),
            LoadoutAbility(name="CA #11", description="Reroll up to 2 dice during a hunt"),
        ],
        equipment=[
            EquipmentItem(name="Triangle Bow", category="weapon", slot="hand", hands=2),
        ],
        metadata={"stage": stage},
    )
    pre_combat = loadout.create_pre_combat_state()
    dice_roller = DiceRoller()
    equipment_pipeline = EquipmentPipeline()
    ability_engine = AbilityEngine(loadout)

    hunter_health = pre_combat.health
    monster_health = monster.health
    monster_armor = monster.armor
    monster_armor_reinforcement = 0
    bouts: List[HunterBoutLog] = []
    bout_number = 1

    reroll_context: Dict[str, Any] = {
        "ca11_enabled": True,
        "ca11_cooldown": 0,
        "ca11_cooldown_reset": 2,
    }

    while hunter_health > 0 and monster_health > 0 and bout_number <= max_bouts:
        prev_hunter_health = hunter_health
        prev_monster_health = monster_health
        dice_context = dice_roller.roll(loadout, dice_tables, rng, context=reroll_context)
        attribute_pool = dice_context.attribute_pool.copy()
        equipment_result = equipment_pipeline.resolve(
            loadout,
            attribute_pool,
            context={"stage": stage},
        )

        hero_face = dice_context.hero_faces[0] if dice_context.hero_faces else []
        class_faces = dice_context.class_faces
        rerolls_used = dice_context.extras.get("rerolls_used", 0)
        hunter_attack = equipment_result.attack

        skulls, monster_attack, bonus_text, armor_bonus = _roll_monster_skulls(monster, dice_tables, rng)
        if armor_bonus:
            if monster_armor > 0:
                monster_armor_reinforcement += armor_bonus
                bonus_text += f"; armor reinforcement +{armor_bonus} (total {monster_armor_reinforcement})"
            else:
                bonus_text += "; armor reinforcement failed (armor already broken)"

        if hunter_attack > monster_attack:
            outcome = "Hunter wins bout"
            if monster_armor > 0 or monster_armor_reinforcement > 0:
                consumed_reinforcement = monster_armor_reinforcement
                monster_armor = 0
                monster_armor_reinforcement = 0
                note = " - monster armor blocked 1 damage (armor destroyed)"
                if consumed_reinforcement > 0:
                    note = (
                        " - monster armor blocked 1 damage (armor destroyed; "
                        f"reinforcement {consumed_reinforcement} discarded)"
                    )
                outcome += note
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
                hero_face=hero_face,
                class_faces=class_faces,
                rerolls_used=rerolls_used,
                attribute_pool=attribute_pool,
                attack_components=equipment_result.metadata.get("attack_breakdown", {}),
                rat_skulls=skulls,
                rat_attack=monster_attack,
                rat_bonus_breakdown=bonus_text,
                hunter_attack=hunter_attack,
                outcome=outcome,
            )
        )

        if hunter_health < prev_hunter_health or monster_health < prev_monster_health:
            break

        bout_number += 1

    winner = "Hunter" if monster_health <= 0 else ("Monster" if hunter_health <= 0 else "Undecided")
    return HunterCombatResult(
        winner=winner,
        bouts=bouts,
        final_hunter_health=hunter_health,
        final_monster_health=monster_health,
    )


# --------------------------------------------------------------------------- #
# Generic equipment helpers for other heroes
# --------------------------------------------------------------------------- #

BASE_ALLOWED_CONDITIONS = {None, "always", "vs_monsters", "vs_bosses"}
OVERCHARGE_ALLOWED_CONDITIONS = BASE_ALLOWED_CONDITIONS | {"overcharge_active"}
ARMOR_DAMAGE_ALLOWED_CONDITIONS = BASE_ALLOWED_CONDITIONS | {"target_armor_intact"}


def _sum_bonus_entries(entries: Optional[Iterable[Dict[str, Any]]], stat: str, allowed_conditions: set) -> int:
    total = 0
    if not entries:
        return total
    for entry in entries:
        if entry.get("stat") != stat:
            continue
        condition = entry.get("condition")
        if condition not in allowed_conditions:
            continue
        total += entry.get("value", 0) or 0
    return total


def _translate_activation_cost(item: EquipmentItem, cost: Optional[Dict[str, int]]) -> Dict[str, int]:
    if not cost:
        return {}
    requirements: Counter = Counter()
    attribute_map = item.attributes or {}
    for key, amount in cost.items():
        if amount is None or amount <= 0:
            continue
        attr = attribute_map.get(key)
        if attr:
            requirements[attr] += amount
    return {attr: int(value) for attr, value in requirements.items() if value > 0}


def _equipment_result_key(result: EquipmentResult) -> Tuple[int, int, int, int]:
    used_total = sum(result.used_attributes.values())
    return (result.attack, result.armor, result.armor_damage, -used_total)


def _empty_equipment_result(description: str) -> EquipmentResult:
    return EquipmentResult(
        attack=0,
        armor=0,
        armor_damage=0,
        used_attributes={},
        description=description,
        metadata={},
    )


def _evaluate_generic_item(
    item: EquipmentItem,
    attribute_pool: Dict[str, int],
) -> Tuple[EquipmentResult, Dict[str, int]]:
    remaining_best = attribute_pool.copy()

    base_attack = _sum_bonus_entries(item.flat_bonuses, "attack", BASE_ALLOWED_CONDITIONS)
    base_attack += _sum_bonus_entries(item.state_modifiers, "attack", BASE_ALLOWED_CONDITIONS)

    base_armor = item.provides_armor
    base_armor += _sum_bonus_entries(item.flat_bonuses, "armor", BASE_ALLOWED_CONDITIONS)
    base_armor += _sum_bonus_entries(item.state_modifiers, "armor", BASE_ALLOWED_CONDITIONS)

    base_armor_damage = _sum_bonus_entries(item.flat_bonuses, "armor_damage", ARMOR_DAMAGE_ALLOWED_CONDITIONS)
    base_armor_damage += _sum_bonus_entries(item.state_modifiers, "armor_damage", ARMOR_DAMAGE_ALLOWED_CONDITIONS)

    base_description = item.name
    if base_attack or base_armor or base_armor_damage:
        base_description += " (passive)"
    else:
        base_description += " (no activation)"

    best_result = EquipmentResult(
        attack=base_attack,
        armor=base_armor,
        armor_damage=base_armor_damage,
        used_attributes={},
        description=base_description,
        metadata={"item": item.name, "mode": "passive"},
    )

    for activation in item.activations or []:
        condition = activation.get("condition")
        if condition and condition not in BASE_ALLOWED_CONDITIONS:
            continue

        cost_map = _translate_activation_cost(item, activation.get("cost"))
        remaining_after_cost = _deduct_attributes(attribute_pool, cost_map) if cost_map else attribute_pool.copy()
        if remaining_after_cost is None:
            continue

        effects = activation.get("effects") or {}
        attack = base_attack + effects.get("attack", 0)
        armor = base_armor + effects.get("armor", 0)
        armor_damage = base_armor_damage + effects.get("armor_damage", 0)

        if activation.get("mode") == "overcharge":
            attack += _sum_bonus_entries(item.overcharge_effects, "attack", OVERCHARGE_ALLOWED_CONDITIONS)
            armor += _sum_bonus_entries(item.overcharge_effects, "armor", OVERCHARGE_ALLOWED_CONDITIONS)
            armor_damage += _sum_bonus_entries(item.overcharge_effects, "armor_damage", ARMOR_DAMAGE_ALLOWED_CONDITIONS | {"overcharge_active"})

        candidate = EquipmentResult(
            attack=attack,
            armor=armor,
            armor_damage=armor_damage,
            used_attributes={attr: value for attr, value in cost_map.items() if value > 0},
            description=f"{item.name} ({activation.get('mode', 'base')})",
            metadata={
                "item": item.name,
                "mode": activation.get("mode", "base"),
                "effects": effects,
                "cost": cost_map,
            },
        )

        if _equipment_result_key(candidate) > _equipment_result_key(best_result):
            best_result = candidate
            remaining_best = remaining_after_cost

    return best_result, remaining_best


def _accumulate_used_attributes(counter: Counter, used: Dict[str, int]) -> None:
    for attr, value in used.items():
        if value:
            counter[attr] += value


def _resolve_generic_equipment(
    loadout: CombatLoadout,
    attribute_pool: Dict[str, int],
) -> EquipmentResolution:
    remaining = attribute_pool.copy()

    weapon_item = next((item for item in loadout.equipment if item.category == "weapon"), None)
    extra_items = [item for item in loadout.equipment if item is not weapon_item]

    if weapon_item:
        weapon_result, remaining = _evaluate_generic_item(weapon_item, remaining)
    else:
        weapon_result = _empty_equipment_result("No weapon equipped")

    extra_attack = 0
    extra_armor = 0
    extra_armor_damage = 0
    extra_used = Counter()
    extra_descriptions: List[str] = []
    extra_metadata: List[Dict[str, Any]] = []

    for item in extra_items:
        result, remaining = _evaluate_generic_item(item, remaining)
        extra_attack += result.attack
        extra_armor += result.armor
        extra_armor_damage += result.armor_damage
        _accumulate_used_attributes(extra_used, result.used_attributes)
        if result.description:
            extra_descriptions.append(result.description)
        extra_metadata.append(result.metadata)

    secondary_result = EquipmentResult(
        attack=extra_attack,
        armor=extra_armor,
        armor_damage=extra_armor_damage,
        used_attributes={attr: value for attr, value in extra_used.items() if value},
        description="; ".join(extra_descriptions) if extra_descriptions else "No secondary items",
        metadata={"items": extra_metadata},
    )

    total_attack = weapon_result.attack + secondary_result.attack
    total_armor = weapon_result.armor + secondary_result.armor
    total_armor_damage = weapon_result.armor_damage + secondary_result.armor_damage

    return EquipmentResolution(
        attack=total_attack,
        armor=total_armor,
        armor_damage=total_armor_damage,
        weapon=weapon_result,
        secondary=secondary_result,
        remaining_attributes=remaining,
        metadata={
            "weapon": weapon_result.metadata,
            "secondary_items": extra_metadata,
        },
    )


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

    builder = LoadoutBuilder({"warrior": HeroProfile(name="warrior", max_health=5, base_armor=0)})
    loadout = builder.build(
        hero_name="warrior",
        abilities=[LoadoutAbility(name="Always wins ties", description="Class Ability #2")],
        equipment=[
            EquipmentItem(name="Square Sword", category="weapon", slot="hand", hands=1),
            EquipmentItem(name="Square Shield", category="shield", slot="hand", hands=1),
        ],
    )
    pre_combat = loadout.create_pre_combat_state()
    dice_roller = DiceRoller()
    equipment_pipeline = EquipmentPipeline()
    ability_engine = AbilityEngine(loadout)
    dice_roller = DiceRoller()
    equipment_pipeline = EquipmentPipeline()
    ability_engine = AbilityEngine(loadout)

    warrior_health = pre_combat.health
    hero_static_armor_remaining = pre_combat.armor
    monster_health = monster.health
    monster_armor = monster.armor  # Track monster armor (breaks on first loss)
    monster_armor_reinforcement = 0  # Extra armor layers granted via OC abilities
    hero_armor_broken = False  # Equipment armor can't return once broken
    bouts: List[BoutLog] = []
    bout_number = 1

    while warrior_health > 0 and monster_health > 0 and bout_number <= max_bouts:
        prev_warrior_health = warrior_health
        prev_monster_health = monster_health
        dice_context = dice_roller.roll(loadout, dice_tables, rng)
        attribute_pool = dice_context.attribute_pool.copy()
        equipment_result = equipment_pipeline.resolve(loadout, attribute_pool)

        hero_face = dice_context.hero_faces[0] if dice_context.hero_faces else []
        class_faces = dice_context.class_faces

        hero_attack = equipment_result.attack
        hero_armor = hero_static_armor_remaining
        if not hero_armor_broken:
            hero_armor += equipment_result.armor

        skulls, monster_attack, bonus_text, armor_bonus = _roll_monster_skulls(monster, dice_tables, rng)
        if armor_bonus:
            if monster_armor > 0:
                monster_armor_reinforcement += armor_bonus
                bonus_text += f"; armor reinforcement +{armor_bonus} (total {monster_armor_reinforcement})"
            else:
                bonus_text += "; armor reinforcement failed (armor already broken)"

        # Warrior CA#2: Always wins ties
        if ability_engine.hero_wins_bout(hero_attack, monster_attack):
            outcome = "Warrior wins bout"
            tie_note = ability_engine.tie_note(hero_attack, monster_attack)
            if tie_note:
                outcome += tie_note
            # Monster loses armor first, then health
            if monster_armor > 0 or monster_armor_reinforcement > 0:
                consumed_reinforcement = monster_armor_reinforcement
                monster_armor = 0
                monster_armor_reinforcement = 0
                note = " - monster armor blocked 1 damage (armor destroyed)"
                if consumed_reinforcement > 0:
                    note = (
                        " - monster armor blocked 1 damage (armor destroyed; "
                        f"reinforcement {consumed_reinforcement} discarded)"
                    )
                outcome += note
            else:
                monster_health -= 1
        else:
            outcome = "Monster wins bout"
            # Hero loses armor first, then health
            if hero_armor > 0:
                if hero_static_armor_remaining > 0:
                    hero_static_armor_remaining = 0
                    outcome += " - base armor broken"
                else:
                    hero_armor_broken = True
                    outcome += " - hero armor broken"
            else:
                warrior_health -= 1

        bouts.append(
            BoutLog(
                bout_number=bout_number,
                hero_face=hero_face,
                class_faces=class_faces,
                sword=equipment_result.weapon,
                shield=equipment_result.secondary,
                remaining_attributes=equipment_result.remaining_attributes,
                rat_skulls=skulls,
                rat_attack=monster_attack,
                rat_bonus_breakdown=bonus_text,
                hero_attack=hero_attack,
                hero_armor=hero_armor,
                outcome=outcome,
                hero_dice_rolled=dice_context.hero_dice_rolled,
                class_dice_rolled=dice_context.class_dice_rolled,
                hero_abilities=dice_context.hero_abilities_available,
                class_abilities=dice_context.class_abilities_available,
                hero_faces_all=dice_context.hero_faces,
            )
        )

        if warrior_health < prev_warrior_health or monster_health < prev_monster_health:
            break

        bout_number += 1

    winner = "Warrior" if monster_health <= 0 else ("Monster" if warrior_health <= 0 else "Undecided")
    return CombatResult(
        winner=winner,
        bouts=bouts,
        final_hero_health=warrior_health,
        final_monster_health=monster_health,
    )
