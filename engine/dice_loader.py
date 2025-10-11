"""
Utility functions to load and validate the dice definitions stored in rules/_core/dice.yaml.

The loader expands the primary/secondary/tertiary shortcuts into raw symbols so other
engine components can work with consistent data structures.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

try:
    import yaml  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    raise ModuleNotFoundError(
        "Missing dependency 'pyyaml'. Install it with 'pip install pyyaml' before using the loader."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
DICE_PATH = ROOT / "rules" / "_core" / "dice.yaml"

HERO_SYMBOLS = {"square", "triangle", "circle"}
MONSTER_SYMBOL = "skull"
FACES_PER_DIE = 6


@dataclass(frozen=True)
class HeroDie:
    hero: str
    faces: List[List[str]]


@dataclass(frozen=True)
class ClassDie:
    hero: str
    faces: List[List[str]]


@dataclass(frozen=True)
class MonsterDie:
    category: str
    skull_counts: List[int]


class DiceConfigError(ValueError):
    """Raised when the dice configuration file contains invalid data."""


def _expand_faces(face_def: Iterable[str], attributes: Mapping[str, str]) -> List[str]:
    result: List[str] = []
    for token in face_def:
        if token in attributes:
            result.append(attributes[token])
        else:
            # Accept literals such as "square" for mercenary entries.
            result.append(token)
    return result


def _validate_symbols(hero: str, faces: Iterable[Iterable[str]]) -> None:
    for idx, face in enumerate(faces, start=1):
        for symbol in face:
            if symbol not in HERO_SYMBOLS:
                raise DiceConfigError(
                    f"Hero '{hero}' has an invalid symbol '{symbol}' on face {idx}. "
                    f"Allowed symbols: {sorted(HERO_SYMBOLS)}."
                )


def _validate_face_count(name: str, faces: Sequence[Iterable[str]]) -> None:
    count = len(faces)
    if count != FACES_PER_DIE:
        raise DiceConfigError(
            f"Die '{name}' defines {count} faces; expected {FACES_PER_DIE}."
        )


def load_raw_config(path: Optional[Path] = None) -> Mapping[str, object]:
    """Load the YAML file without additional processing."""
    target = path or DICE_PATH
    if not target.exists():
        raise FileNotFoundError(f"Dice configuration file missing: {target}")
    with target.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_hero_dice(config: Optional[Mapping[str, object]] = None) -> List[HeroDie]:
    data = config or load_raw_config()
    hero_section = data.get("hero_dice")
    if not isinstance(hero_section, Mapping):
        raise DiceConfigError("Missing 'hero_dice' section.")

    heroes = hero_section.get("heroes")
    if not isinstance(heroes, Mapping):
        raise DiceConfigError("Missing 'hero_dice.heroes' definitions.")

    result: List[HeroDie] = []
    for hero_name, hero_data in heroes.items():
        if not isinstance(hero_data, Mapping):
            raise DiceConfigError(f"Hero '{hero_name}' entry must be a mapping.")

        attributes = hero_data.get("attributes")
        if not isinstance(attributes, Mapping):
            raise DiceConfigError(f"Hero '{hero_name}' is missing attribute mappings.")

        faces_def = hero_data.get("faces")
        if not isinstance(faces_def, Iterable):
            raise DiceConfigError(f"Hero '{hero_name}' is missing face definitions.")

        expanded_faces: List[List[str]] = []
        for face in faces_def:
            if isinstance(face, (str, bytes)) or not isinstance(face, Iterable):
                raise DiceConfigError(
                    f"Hero '{hero_name}' has a face entry that is not a list."
                )
                # continue loop even though exception raised
            expanded_faces.append(_expand_faces(face, attributes))

        _validate_face_count(f"hero:{hero_name}", expanded_faces)
        _validate_symbols(hero_name, expanded_faces)
        result.append(HeroDie(hero=hero_name, faces=expanded_faces))

    return result


def load_class_dice(config: Optional[Mapping[str, object]] = None) -> List[ClassDie]:
    data = config or load_raw_config()
    class_section = data.get("class_dice")
    if not isinstance(class_section, Mapping):
        raise DiceConfigError("Missing 'class_dice' section.")

    heroes = class_section.get("heroes")
    if not isinstance(heroes, Mapping):
        raise DiceConfigError("Missing 'class_dice.heroes' definitions.")

    result: List[ClassDie] = []
    for hero_name, hero_data in heroes.items():
        if not isinstance(hero_data, Mapping):
            raise DiceConfigError(f"Class entry '{hero_name}' must be a mapping.")

        attributes = hero_data.get("attributes")
        if not isinstance(attributes, Mapping):
            raise DiceConfigError(
                f"Class die '{hero_name}' is missing attribute mappings."
            )

        faces_def = hero_data.get("faces")
        if not isinstance(faces_def, Iterable):
            raise DiceConfigError(f"Class die '{hero_name}' is missing face definitions.")

        expanded_faces: List[List[str]] = []
        for face in faces_def:
            if isinstance(face, (str, bytes)) or not isinstance(face, Iterable):
                raise DiceConfigError(
                    f"Class die '{hero_name}' has a face entry that is not a list."
                )
            expanded_faces.append(_expand_faces(face, attributes))

        _validate_face_count(f"class:{hero_name}", expanded_faces)
        _validate_symbols(hero_name, expanded_faces)
        result.append(ClassDie(hero=hero_name, faces=expanded_faces))

    return result


def load_monster_dice(config: Optional[Mapping[str, object]] = None) -> List[MonsterDie]:
    data = config or load_raw_config()
    monster_section = data.get("monster_dice")
    if not isinstance(monster_section, Mapping):
        raise DiceConfigError("Missing 'monster_dice' section.")

    result: List[MonsterDie] = []
    for category, faces_def in monster_section.items():
        if not isinstance(faces_def, Iterable):
            raise DiceConfigError(
                f"Monster category '{category}' must define a list of skull counts."
            )

        skull_counts: List[int] = []
        for position, value in enumerate(faces_def, start=1):
            if not isinstance(value, int):
                raise DiceConfigError(
                    f"Monster die '{category}' has non-integer value '{value}' on face {position}."
                )
            if value < 0:
                raise DiceConfigError(
                    f"Monster die '{category}' has negative skull count on face {position}."
                )
            skull_counts.append(value)

        if len(skull_counts) != FACES_PER_DIE:
            raise DiceConfigError(
                f"Monster die '{category}' defines {len(skull_counts)} faces; expected {FACES_PER_DIE}."
            )
        result.append(MonsterDie(category=category, skull_counts=skull_counts))

    return result


def load_all_dice(path: Optional[Path] = None) -> Dict[str, object]:
    """Convenience helper that loads and validates every die definition."""
    config = load_raw_config(path)
    return {
        "hero_dice": load_hero_dice(config),
        "class_dice": load_class_dice(config),
        "monster_dice": load_monster_dice(config),
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke test helper
    dice = load_all_dice()
    print("Hero dice:")
    for die in dice["hero_dice"]:
        print(f"  {die.hero:10s} -> {die.faces}")
    print("\nClass dice:")
    for die in dice["class_dice"]:
        print(f"  {die.hero:10s} -> {die.faces}")
    print("\nMonster dice:")
    for die in dice["monster_dice"]:
        print(f"  {die.category:6s} -> {die.skull_counts}")
