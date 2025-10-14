"""Utility helpers for constructing hero loadouts from YAML datasets."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
import copy

import yaml

from .combat_sim import LoadoutAbility, EquipmentItem, HeroProfile, LoadoutBuilder

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_ABILITIES_CACHE: Optional[Dict[str, List[dict]]] = None
_EQUIPMENT_CACHE: Optional[Dict[str, List[dict]]] = None

_DEFAULT_PROFILES: Dict[str, HeroProfile] = {
    "warrior": HeroProfile(name="warrior", max_health=5, base_armor=0),
    "hunter": HeroProfile(name="hunter", max_health=5, base_armor=0),
}

_DEFAULT_LOADOUTS: Dict[str, Dict[str, Any]] = {
    "warrior": {
        "abilities": ["2"],
        "equipment": {"weapon": "Sword", "shield": "Shield"},
    },
    "hunter": {
        "abilities": [1, 11],
        "equipment": {"weapon": "Bow"},
        "metadata": {"stage": 1},
    },
}


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_ability_dataset() -> Dict[str, List[dict]]:
    global _ABILITIES_CACHE
    if _ABILITIES_CACHE is None:
        data = _load_yaml(PROJECT_ROOT / "rules" / "heroes" / "abilities.yaml")
        mapping: Dict[str, List[dict]] = {}
        for entry in data:
            hero = entry.get("hero")
            if hero:
                entry_copy = copy.deepcopy(entry)
                tags_raw = entry_copy.get("tags")
                if tags_raw is None:
                    tags: List[str] = []
                elif isinstance(tags_raw, str):
                    tags = [tags_raw]
                else:
                    tags = list(tags_raw)
                tags_lower = [str(tag).lower() for tag in tags]
                if entry_copy.get("passive"):
                    tags_lower.append("passive")
                entry_copy["tags"] = tags_lower
                entry_copy["passive"] = "passive" in tags_lower
                modes_raw = entry_copy.get("modes")
                if modes_raw is None:
                    modes = []
                elif isinstance(modes_raw, str):
                    modes = [modes_raw]
                else:
                    modes = list(modes_raw)
                entry_copy["modes"] = [str(mode).lower() for mode in modes]
                mapping.setdefault(hero.lower(), []).append(entry_copy)
        _ABILITIES_CACHE = mapping
    return _ABILITIES_CACHE


def load_equipment_dataset() -> Dict[str, List[dict]]:
    global _EQUIPMENT_CACHE
    if _EQUIPMENT_CACHE is None:
        data = _load_yaml(PROJECT_ROOT / "rules" / "equipment" / "rank1_equipment.yaml")
        _EQUIPMENT_CACHE = data
    return _EQUIPMENT_CACHE


def register_hero_profile(profile: HeroProfile) -> None:
    _DEFAULT_PROFILES[profile.name.lower()] = profile


def get_hero_profile(hero: str) -> HeroProfile:
    hero_lower = hero.lower()
    return _DEFAULT_PROFILES.get(hero_lower, HeroProfile(name=hero_lower, max_health=5, base_armor=0))


def get_default_loadout_config(hero: str) -> Dict[str, Any]:
    return _DEFAULT_LOADOUTS.get(hero.lower(), {})


def resolve_abilities(hero: str, tokens: Sequence[object]) -> List[LoadoutAbility]:
    abilities_data = load_ability_dataset().get(hero.lower(), [])
    entries = [entry.copy() for entry in abilities_data]
    chosen: List[dict] = []

    def pick(predicate) -> Optional[dict]:
        for idx, entry in enumerate(entries):
            if predicate(entry):
                return entries.pop(idx)
        return None

    for token in tokens or []:
        value = str(token).strip()
        if not value:
            continue
        ability_entry = None
        if value.isdigit():
            ability_entry = pick(lambda entry: str(entry.get("number")) == value)
        else:
            lower = value.lower()
            ability_entry = pick(lambda entry: lower in entry.get("effect", "").lower())
        if ability_entry:
            chosen.append(ability_entry)

    result: List[LoadoutAbility] = []
    processed_names: set[str] = set()

    def _entry_to_loadout_ability(ability: dict) -> LoadoutAbility:
        effect = ability.get("effect", "")
        number = ability.get("number")
        name = f"#{number} {effect}" if number is not None else effect
        cooldown_raw = ability.get("cooldown")
        if isinstance(cooldown_raw, int):
            cooldown_value = max(0, cooldown_raw)
        elif isinstance(cooldown_raw, str) and cooldown_raw.strip():
            try:
                cooldown_value = max(0, int(cooldown_raw))
            except ValueError:
                cooldown_value = 0
        else:
            cooldown_value = 0

        stage_cooldown_raw = ability.get("stage_cooldown")
        stage_cooldown_value: Optional[int]
        if isinstance(stage_cooldown_raw, int):
            stage_cooldown_value = max(0, stage_cooldown_raw)
        elif isinstance(stage_cooldown_raw, str) and stage_cooldown_raw.strip():
            try:
                stage_cooldown_value = max(0, int(stage_cooldown_raw))
            except ValueError:
                stage_cooldown_value = None
        else:
            stage_cooldown_value = None

        tags_tuple = tuple(ability.get("tags", []))
        modes_tuple = tuple(ability.get("modes", []))
        loadout_ability = LoadoutAbility(
            name=name,
            description=effect,
            cooldown=cooldown_value,
            stage_cooldown=stage_cooldown_value,
            passive=bool(ability.get("passive")),
            tags=tags_tuple,
            modes=modes_tuple,
        )
        processed_names.add(name)
        return loadout_ability

    for ability in chosen:
        result.append(_entry_to_loadout_ability(ability))

    return result


def _find_equipment_entry(data: Dict[str, List[dict]], name: str) -> Optional[dict]:
    name_lower = name.lower()
    for entries in data.values():
        for entry in entries:
            if entry.get("name", "").lower() == name_lower or entry.get("id", "").lower() == name_lower:
                return entry
    return None


def _entry_to_equipment_item(entry: dict) -> EquipmentItem:
    category = entry.get("category", "")
    item_type = entry.get("item_type")
    slot = None
    hands = 0
    provides_armor = 0
    attributes = entry.get("attributes") or {}
    activations = copy.deepcopy(entry.get("activations") or [])
    overcharge_effects = copy.deepcopy(entry.get("overcharge_effects") or [])

    if category == "weapon":
        slot = "hand"
        hands = 2 if item_type == "two_hand" else 1
    elif category == "armor":
        slot = item_type
    elif category == "charm":
        slot = item_type

    for bonus in entry.get("flat_bonuses", []) or []:
        stat = bonus.get("stat")
        value = max(0, bonus.get("value", 0))
        condition = bonus.get("condition")
        if stat == "armor" and (condition in (None, "always")):
            provides_armor += value

    flat_bonuses: List[Dict[str, Any]] = []
    for bonus in entry.get("flat_bonuses", []) or []:
        stat = bonus.get("stat")
        condition = bonus.get("condition")
        if stat == "armor" and (condition in (None, "always")):
            continue
        flat_bonuses.append(copy.deepcopy(bonus))

    state_modifiers_raw = entry.get("state_modifiers") or {}
    state_modifiers: List[Dict[str, Any]] = []
    if isinstance(state_modifiers_raw, dict):
        for stat, modifiers in state_modifiers_raw.items():
            for modifier in modifiers or []:
                entry_copy = copy.deepcopy(modifier)
                entry_copy["stat"] = stat
                state_modifiers.append(entry_copy)

    return EquipmentItem(
        name=entry.get("name", "Unknown"),
        category=category,
        slot=slot,
        hands=hands,
        provides_armor=provides_armor,
        attributes={key: value for key, value in attributes.items() if value},
        activations=activations,
        flat_bonuses=flat_bonuses,
        overcharge_effects=overcharge_effects,
        state_modifiers=state_modifiers,
    )


def resolve_equipment(config: Any) -> List[EquipmentItem]:
    if not config:
        return []
    dataset = load_equipment_dataset()
    names: List[str] = []

    if isinstance(config, list):
        names.extend(str(item) for item in config)
    elif isinstance(config, dict):
        for key in ("items", "weapon", "offhand", "armor", "shield", "charm", "rings", "crowns"):
            value = config.get(key)
            if value is None:
                continue
            if isinstance(value, list):
                names.extend(str(item) for item in value)
            else:
                names.append(str(value))
    else:
        names.append(str(config))

    equipment: List[EquipmentItem] = []
    for name in names:
        entry = _find_equipment_entry(dataset, name)
        if not entry:
            raise ValueError(f"Unknown equipment reference '{name}'.")
        equipment.append(_entry_to_equipment_item(entry))
    return equipment


def build_loadout(
    hero: str,
    *,
    ability_tokens: Optional[Sequence[object]] = None,
    equipment_config: Optional[Any] = None,
    metadata: Optional[Dict[str, Any]] = None,
    builder: Optional[LoadoutBuilder] = None,
):
    hero_lower = hero.lower()
    profile = get_hero_profile(hero_lower)
    builder = builder or LoadoutBuilder({hero_lower: profile})

    ability_tokens = ability_tokens or []
    equipment_config = equipment_config or []

    abilities = resolve_abilities(hero_lower, ability_tokens)
    equipment = resolve_equipment(equipment_config)

    default_config = get_default_loadout_config(hero_lower)
    if not abilities and default_config.get("abilities"):
        abilities = resolve_abilities(hero_lower, default_config["abilities"])
    if not equipment and default_config.get("equipment"):
        equipment = resolve_equipment(default_config["equipment"])

    meta = metadata or default_config.get("metadata", {})
    if not isinstance(meta, dict):
        meta = {}

    return builder.build(
        hero_name=hero_lower,
        abilities=abilities,
        equipment=equipment,
        metadata=meta,
    )
