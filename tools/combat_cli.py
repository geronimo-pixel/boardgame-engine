#!/usr/bin/env python
"""
Quick CLI for assembling hero loadouts and running combat batches against monsters.

Examples:
    python tools/combat_cli.py --hero warrior --monster Rat --trials 20 --random-abilities 2 --random-equipment
    python tools/combat_cli.py --hero hunter --monster Rat --trials 10 --ability 1 --ability 11 --weapon "Triangle Bow"
"""
from __future__ import annotations

import argparse
import random
from typing import Dict, List, Optional, Sequence

from engine.combat_core import simulate_combat
from engine.combat_sim import DiceTables
from engine.loadout_helpers import (
    build_loadout,
    get_default_loadout_config,
    load_ability_dataset,
    load_equipment_dataset,
    resolve_abilities,
    resolve_equipment,
)
from engine.monster_loader import get_monster_by_name, load_monsters

ABILITY_DATA = load_ability_dataset()
EQUIPMENT_DATA = load_equipment_dataset()


def _ability_token_for_entry(entry: dict) -> str:
    number = entry.get("number")
    if number is not None:
        return str(number)
    return entry.get("effect", "")


def choose_ability_tokens(hero: str, requested: Sequence[str], random_count: int) -> List[str]:
    entries = [entry.copy() for entry in ABILITY_DATA.get(hero, [])]
    tokens: List[str] = []

    def pick(predicate) -> Optional[dict]:
        for idx, entry in enumerate(entries):
            if predicate(entry):
                return entries.pop(idx)
        return None

    for token in requested:
        token_lower = token.lower()
        ability_entry = None
        if token_lower.isdigit():
            ability_entry = pick(lambda entry: str(entry.get("number")) == token_lower)
        else:
            ability_entry = pick(lambda entry: token_lower in entry.get("effect", "").lower())
        if ability_entry:
            tokens.append(_ability_token_for_entry(ability_entry))

    if random_count > 0 and entries:
        random.shuffle(entries)
        for entry in entries[:random_count]:
            tokens.append(_ability_token_for_entry(entry))

    return tokens


def choose_equipment_config(
    *,
    weapon: Optional[str],
    armor: Optional[str],
    charm: Optional[str],
    randomize: bool,
) -> Dict[str, str]:
    config: Dict[str, str] = {}

    def pick(category: str, requested_name: Optional[str]) -> None:
        if requested_name:
            config[category] = requested_name
        elif randomize:
            pool = EQUIPMENT_DATA.get({"weapon": "weapons", "armor": "armors", "charm": "charms"}[category], [])
            if pool:
                config[category] = random.choice(pool)["name"]

    pick("weapon", weapon)
    pick("armor", armor)
    pick("charm", charm)

    return config


def simulate_batch(loadout, monster, trials: int, seed: Optional[int]) -> Dict[str, int]:
    dice_tables = DiceTables.from_loader()
    wins = losses = draws = 0

    for index in range(trials):
        trial_seed = None if seed is None else seed + index
        result = simulate_combat(loadout, monster, seed=trial_seed, dice_tables=dice_tables)
        winner = result.winner.lower()
        if winner == loadout.hero:
            wins += 1
        elif winner == "monster":
            losses += 1
        else:
            draws += 1

    return {"wins": wins, "losses": losses, "draws": draws}


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble combat loadouts and run simulations.")
    parser.add_argument("--hero", default="warrior", help="Hero to use (default: warrior).")
    parser.add_argument("--monster", required=True, help="Monster name to fight.")
    parser.add_argument("--trials", type=int, default=10, help="Number of simulations to run.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed baseline.")

    parser.add_argument("--ability", action="append", default=[], help="Include ability by number or text (repeatable).")
    parser.add_argument("--random-abilities", type=int, default=0, help="Number of additional random abilities to add.")

    parser.add_argument("--weapon", help="Specific weapon to equip.")
    parser.add_argument("--armor", help="Specific armor to equip.")
    parser.add_argument("--charm", help="Specific charm to equip.")
    parser.add_argument("--random-equipment", action="store_true", help="Randomly select equipment for missing slots.")

    args = parser.parse_args()

    hero_key = args.hero.lower()
    ability_tokens = choose_ability_tokens(hero_key, args.ability, args.random_abilities)
    equipment_config = choose_equipment_config(
        weapon=args.weapon,
        armor=args.armor,
        charm=args.charm,
        randomize=args.random_equipment,
    )

    loadout = build_loadout(hero_key, ability_tokens=ability_tokens, equipment_config=equipment_config)

    default_config = get_default_loadout_config(hero_key)
    display_abilities = resolve_abilities(hero_key, ability_tokens or default_config.get("abilities", []))
    display_equipment = resolve_equipment(equipment_config or default_config.get("equipment", {}))

    monsters = load_monsters()
    monster = get_monster_by_name(args.monster, monsters)

    summary = simulate_batch(loadout, monster, args.trials, args.seed)

    print(f"Hero: {args.hero.capitalize()} vs Monster: {monster.name}")
    print(f"Trials: {args.trials}")
    print(f"Wins: {summary['wins']}  Losses: {summary['losses']}  Draws: {summary['draws']}")
    if display_abilities:
        print("Abilities:")
        for ability in display_abilities:
            print(f"  - {ability.name}")
    if display_equipment:
        print("Equipment:")
        for item in display_equipment:
            print(f"  - {item.name}")


if __name__ == "__main__":
    main()
