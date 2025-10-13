"""
Parse hero and class abilities from the original text file and export them as structured YAML.

Each entry captures
    - hero name
    - ability type (hero/class)
    - class ability number (if applicable)
    - effect description (meta markers removed)
    - cooldown values (list when multiple are defined)
    - phase limits (list when multiple are defined)

Usage:
    python tools/build_abilities_yaml.py

Outputs:
    rules/heroes/abilities.yaml
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import yaml


HERO_NAMES = ["Warrior", "Sentinel", "Mage", "Shaman", "Thief", "Hunter", "Mercenary"]

HERO_LINE_RE = re.compile(r"^Hero\s*:?\s*(?P<text>.+)$", re.IGNORECASE)
CLASS_LINE_RE = re.compile(r"^(?P<num>\d+)\.\s*Class\s*:?\s*(?P<text>.+)$", re.IGNORECASE)
PAREN_RE = re.compile(r"\(([^)]*)\)")
CD_RE = re.compile(r"cd\s*(\d+)", re.IGNORECASE)
PHASE_RE = re.compile(r"p\s*([0-9]+(?:\s*-\s*[0-9]+)?)", re.IGNORECASE)
PHASE_DIGIT_RE = re.compile(r"^\s*\d+(?:\s*-\s*\d+)?\s*$")


@dataclass
class AbilityEntry:
    hero: str
    ability_type: str
    effect: str
    cooldown: Optional[List[int]]
    phase_limit: Optional[List[str]]
    number: Optional[int] = None


def _normalize_effect(text: str, removals: Sequence[str]) -> str:
    cleaned = text
    for token in removals:
        cleaned = cleaned.replace(f"({token})", "")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" ;,")


def _parse_meta_tokens(tokens: Sequence[str]) -> Dict[str, List]:
    cooldowns: List[int] = []
    phases: List[str] = []

    for token in tokens:
        lower = token.lower()
        for match in CD_RE.findall(lower):
            try:
                cooldowns.append(max(0, int(match)))
            except ValueError:
                continue

        phase_matches = PHASE_RE.findall(lower)
        if phase_matches:
            for phase in phase_matches:
                phases.append(phase.replace(" ", ""))
        else:
            if PHASE_DIGIT_RE.match(lower):
                phases.append(token.strip())

    return {"cooldowns": cooldowns, "phases": phases}


def _dedupe(seq: Sequence) -> List:
    seen = []
    for item in seq:
        if item not in seen:
            seen.append(item)
    return seen


def parse_abilities(path: Path) -> List[AbilityEntry]:
    entries: List[AbilityEntry] = []
    current_hero: Optional[str] = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        hero_match = next((hero for hero in HERO_NAMES if line.lower().startswith(hero.lower())), None)
        if hero_match:
            current_hero = hero_match.lower()
            continue

        if current_hero is None or line.upper() in {"ABILITIES"}:
            continue

        hero_line = HERO_LINE_RE.match(line)
        if hero_line:
            effect_text = hero_line.group("text").strip()
            parents = PAREN_RE.findall(effect_text)
            meta = _parse_meta_tokens(parents)
            effect_clean = _normalize_effect(effect_text, parents)
            cd_list = _dedupe([max(0, cd) for cd in meta["cooldowns"]])
            phase_list = _dedupe(meta["phases"])
            entries.append(
                AbilityEntry(
                    hero=current_hero,
                    ability_type="hero",
                    effect=effect_clean,
                    cooldown=cd_list or None,
                    phase_limit=phase_list or None,
                )
            )
            continue

        class_line = CLASS_LINE_RE.match(line)
        if class_line:
            number = int(class_line.group("num"))
            effect_text = class_line.group("text").strip()
            parents = PAREN_RE.findall(effect_text)
            meta = _parse_meta_tokens(parents)
            effect_clean = _normalize_effect(effect_text, parents)
            cd_list = _dedupe([max(0, cd) for cd in meta["cooldowns"]])
            phase_list = _dedupe(meta["phases"])
            entries.append(
                AbilityEntry(
                    hero=current_hero,
                    ability_type="class",
                    effect=effect_clean,
                    cooldown=cd_list or None,
                    phase_limit=phase_list or None,
                    number=number,
                )
            )

    return entries


def ability_entry_to_dict(entry: AbilityEntry) -> Dict[str, object]:
    data = {
        "hero": entry.hero,
        "type": entry.ability_type,
        "effect": entry.effect,
    }
    if entry.number is not None:
        data["number"] = entry.number
    if entry.cooldown is not None:
        sanitized = [max(0, value) for value in entry.cooldown]
        data["cooldown"] = sanitized if len(sanitized) > 1 else sanitized[0]
    else:
        data["cooldown"] = None
    if entry.phase_limit is not None:
        data["phase_limit"] = (
            entry.phase_limit if len(entry.phase_limit) > 1 else entry.phase_limit[0]
        )
    else:
        data["phase_limit"] = None
    return data


def write_yaml(entries: List[AbilityEntry], output_path: Path) -> None:
    data = [ability_entry_to_dict(entry) for entry in entries]
    output_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    source_path = project_root / "Original files" / "H&C Abilities.txt"
    target_path = project_root / "rules" / "heroes" / "abilities.yaml"

    parsed = parse_abilities(source_path)
    write_yaml(parsed, target_path)
    print(f"Wrote {len(parsed)} abilities to {target_path}")


if __name__ == "__main__":
    main()
