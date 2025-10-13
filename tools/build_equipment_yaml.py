"""
Utility script to convert the rank 1 equipment table into structured YAML.

The generated file groups entries by section (weapons, armors, charms) and
captures variant-specific activations, overcharge bonuses, flat bonuses, and
cost data. Attribute symbols are normalised to full words and secondary
effects (e.g., armor damage) are expressed as explicit modifiers with optional
conditions (such as requiring the target to still have armor).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml


FIELD_NAMES = [
    "name",
    "category",
    "type",
    "dice",
    "primary",
    "secondary",
    "tertiary",
    "effect",
    "overcharge",
    "flat_bonus",
    "cost",
]

SECTION_ALIASES = {
    "WEAPONS": "weapon",
    "AMORS": "armor",
    "CHARMS": "charm",
}

ATTR_MAP = {
    "Sq": "square",
    "Tr": "triangle",
    "Cr": "circle",
    "Tri": "triangle",
    "/": None,
}

STAT_MAP = {
    "att": "attack",
    "ar": "armor",
    "ard": "armor_damage",
    "g": "gold",
    "tk": "token",
}

COST_TOKEN_PATTERN = r"\d+\s*[pst]"
EFFECT_PATTERN = re.compile(
    rf"(?P<cost>{COST_TOKEN_PATTERN}(?:\s*\+\s*{COST_TOKEN_PATTERN})*)\s*=\s*\+\s*(?P<value>\d+)\s*(?P<stat>[A-Za-z]+)(?P<extra>[^0-9]*)",
    re.IGNORECASE,
)
BONUS_PATTERN = re.compile(r"\+?\s*(?P<value>\d+)\s*(?P<stat>[A-Za-z]+)(?P<extra>.*)", re.IGNORECASE)
COST_PATTERN = re.compile(r"(?P<value>\d+)\s*(?P<label>[A-Za-z]+)")


@dataclass
class EquipmentRecord:
    raw: Dict[str, str]
    section: str
    index: int


def _parse_equipment_table(path: Path) -> List[EquipmentRecord]:
    """
    Parse the raw equipment table into a list of records, preserving section and
    column ordering.
    """
    records: List[EquipmentRecord] = []
    section: Optional[str] = None
    fields: List[str] = []
    collecting = False
    header_to_skip = 0
    index = 0

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if upper in SECTION_ALIASES:
            section = upper
            collecting = False
            header_to_skip = 0
            continue
        if stripped == "Name":
            collecting = True
            fields = []
            header_to_skip = len(FIELD_NAMES) - 1  # skip the column labels
            continue
        if not collecting:
            continue
        if header_to_skip:
            header_to_skip -= 1
            continue
        if raw_line.startswith("\t"):
            fields.append(stripped)
        else:
            if fields:
                fields[-1] += f" {stripped}"
        if len(fields) == len(FIELD_NAMES):
            record = dict(zip(FIELD_NAMES, fields))
            if section is None:
                raise ValueError("Encountered data row before any section header.")
            records.append(EquipmentRecord(raw=record, section=section, index=index))
            index += 1
            fields = []
    return records


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _normalize_attribute(token: str) -> Optional[str]:
    token = token.strip()
    return ATTR_MAP.get(token, token.lower() if token != "/" else None)


def _normalize_type(section: str, raw_type: str) -> str:
    cleaned = raw_type.strip().lower()
    if SECTION_ALIASES[section] == "weapon":
        return {"1 hand": "one_hand", "2 hand": "two_hand"}.get(cleaned, cleaned.replace(" ", "_"))
    return cleaned.replace(" ", "_")


def _parse_cost_tokens(cost_str: str) -> Dict[str, int]:
    counts = {"primary": 0, "secondary": 0, "tertiary": 0}
    for token in cost_str.split("+"):
        token = token.strip().lower()
        if not token:
            continue
        value = int(re.match(r"\d+", token).group()) if re.match(r"\d+", token) else 0
        value = max(0, value)
        key = token.rstrip("0123456789")
        if token.endswith("p"):
            counts["primary"] += value
        elif token.endswith("s"):
            counts["secondary"] += value
        elif token.endswith("t"):
            counts["tertiary"] += value
    return {k: v for k, v in counts.items() if v}


def _parse_condition(extra: str, stat: str) -> Optional[str]:
    extra_clean = extra.strip().lower()
    if not extra_clean and stat == "armor_damage":
        return "target_armor_intact"
    if "vs" in extra_clean:
        if "monster" in extra_clean:
            return "vs_monsters"
        if "boss" in extra_clean:
            return "vs_bosses"
        if "player" in extra_clean:
            return "vs_players"
    return extra_clean or None


def _parse_activation_entries(text: str) -> List[Dict[str, object]]:
    text = text.strip()
    if not text or text in {"/", "No OC", "No", "No oc"}:
        return []
    entries: List[Dict[str, object]] = []
    for match in EFFECT_PATTERN.finditer(text):
        cost_raw = match.group("cost")
        value = max(0, int(match.group("value")))
        stat_raw = match.group("stat").lower()
        stat = STAT_MAP.get(stat_raw, stat_raw)
        condition = _parse_condition(match.group("extra"), stat)
        cost = _parse_cost_tokens(cost_raw)
        mode = "base" if not cost.get("secondary") and not cost.get("tertiary") else "overcharge"
        entry = {
            "mode": mode,
            "cost": cost or None,
            "effects": {stat: value},
        }
        if condition:
            entry["condition"] = condition
        entries.append(entry)
    return entries


def _parse_bonus_entries(text: str, *, default_condition: Optional[str] = None) -> List[Dict[str, object]]:
    text = text.strip()
    if not text or text in {"/", "No OC", "No"}:
        return []
    entries: List[Dict[str, object]] = []
    for part in text.split("/"):
        piece = part.strip()
        if not piece:
            continue
        match = BONUS_PATTERN.match(piece)
        if not match:
            continue
        value = max(0, int(match.group("value")))
        stat_raw = match.group("stat").lower()
        stat = STAT_MAP.get(stat_raw, stat_raw)
        condition = _parse_condition(match.group("extra"), stat) or default_condition
        entry = {
            "stat": stat,
            "value": value,
        }
        if condition:
            entry["condition"] = condition
        entries.append(entry)
    return entries


def _parse_cost(text: str) -> Dict[str, int]:
    result: Dict[str, int] = {}
    text = text.strip()
    if not text or text == "/":
        return result
    for part in text.split(","):
        piece = part.strip()
        if not piece or piece == "/":
            continue
        match = COST_PATTERN.match(piece)
        if not match:
            continue
        value = max(0, int(match.group("value")))
        label = match.group("label").lower()
        if label.startswith("g"):
            result["gold"] = value
        elif label.startswith("tk"):
            result["tokens"] = value
        else:
            result[label] = value
    return result


def _build_entry(record: EquipmentRecord) -> Dict[str, object]:
    data = record.raw
    section_key = SECTION_ALIASES[record.section]
    base_slug = _slugify(data["name"])
    variant_suffix = _slugify(data["primary"] if data["primary"] != "/" else f"v{record.index}")
    entry_id = f"{section_key}_{base_slug}_{variant_suffix}"

    attributes = {
        "primary": _normalize_attribute(data["primary"]),
        "secondary": _normalize_attribute(data["secondary"]),
        "tertiary": _normalize_attribute(data["tertiary"]),
    }

    activations = _parse_activation_entries(data["effect"])
    overcharge_effects = _parse_bonus_entries(data["overcharge"], default_condition="overcharge_active")
    flat_bonuses = _parse_bonus_entries(data["flat_bonus"])

    entry = {
        "id": entry_id,
        "name": data["name"],
        "category": section_key,
        "item_type": _normalize_type(record.section, data["type"]),
        "dice": None if data["dice"] == "/" else int(data["dice"]),
        "attributes": attributes,
        "activations": activations,
        "overcharge_effects": overcharge_effects,
        "flat_bonuses": flat_bonuses,
        "cost": _parse_cost(data["cost"]),
    }

    # Consolidate flat bonuses into state modifiers for quick reference.
    if flat_bonuses:
        state_modifiers: Dict[str, List[Dict[str, object]]] = {}
        for bonus in flat_bonuses:
            stat = bonus["stat"]
            state_modifiers.setdefault(stat, []).append(
                {"value": bonus["value"], "condition": bonus.get("condition", "always")}
            )
        entry["state_modifiers"] = state_modifiers

    return entry


def generate_yaml(output_path: Path, records: Iterable[EquipmentRecord]) -> None:
    grouped: Dict[str, List[Dict[str, object]]] = {"weapons": [], "armors": [], "charms": []}
    for record in records:
        section_label = SECTION_ALIASES[record.section]
        entry = _build_entry(record)
        if section_label == "weapon":
            grouped["weapons"].append(entry)
        elif section_label == "armor":
            grouped["armors"].append(entry)
        else:
            grouped["charms"].append(entry)

    output = {
        "weapons": grouped["weapons"],
        "armors": grouped["armors"],
        "charms": grouped["charms"],
    }
    output_path.write_text(yaml.safe_dump(output, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    source_path = project_root / "Original files" / "Equipment.txt"
    target_path = project_root / "rules" / "equipment" / "rank1_equipment.yaml"
    records = _parse_equipment_table(source_path)
    generate_yaml(target_path, records)
    print(f"Generated {target_path} with {len(records)} entries.")


if __name__ == "__main__":
    main()
