"""
Core combat abstractions used by hero-vs-monster simulations.

This module exposes:
    - dataclasses for loadout/ability/equipment definitions
    - helper builders and validators
    - generic combat driver `simulate_combat`

The goal is to keep hero-specific simulations thin wrappers that construct
loadouts and delegate to this API.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple
import random

from .combat_sim import (
    DiceTables,
    LoadoutAbility,
    EquipmentItem,
    CombatLoadout,
    EquipmentResolution,
    DiceRollContext,
    LoadoutBuilder,
    AbilityEngine,
    DiceRoller,
    EquipmentPipeline,
    Monster,
    _roll_monster_skulls,
    BoutLog,
    CombatResult,
)


def simulate_combat(
    loadout: CombatLoadout,
    monster: Monster,
    *,
    seed: Optional[int] = None,
    max_bouts: int = 100,
    dice_tables: Optional[DiceTables] = None,
    options: Optional[Dict[str, Any]] = None,
) -> CombatResult:
    rng = random.Random(seed)
    dice_tables = dice_tables or DiceTables.from_loader()
    options = options or {}

    pre_combat = loadout.create_pre_combat_state()
    dice_roller = DiceRoller()
    equipment_pipeline = EquipmentPipeline()
    ability_engine = AbilityEngine(loadout)

    hero_health = pre_combat.health
    hero_base_armor = pre_combat.armor

    monster_health = monster.health
    monster_armor = monster.armor
    monster_armor_reinforcement = 0

    bouts: List[BoutLog] = []
    bout_number = 1

    hero_armor_broken = False
    hero_base_armor_remaining = hero_base_armor

    extra_context: Dict[str, Any] = loadout.metadata.copy()
    extra_context.update(options)

    while hero_health > 0 and monster_health > 0 and bout_number <= max_bouts:
        dice_context = dice_roller.roll(loadout, dice_tables, rng, context=extra_context)
        attribute_pool = dice_context.attribute_pool.copy()
        equipment_result = equipment_pipeline.resolve(loadout, attribute_pool, context=extra_context)

        hero_face = dice_context.hero_faces[0] if dice_context.hero_faces else []
        class_faces = dice_context.class_faces

        hero_attack = equipment_result.attack
        hero_armor = hero_base_armor_remaining
        if not hero_armor_broken:
            hero_armor += equipment_result.armor

        skulls, monster_attack, bonus_text, armor_bonus = _roll_monster_skulls(monster, dice_tables, rng)
        if armor_bonus:
            if monster_armor > 0:
                monster_armor_reinforcement += armor_bonus
                bonus_text += f"; armor reinforcement +{armor_bonus} (total {monster_armor_reinforcement})"
            else:
                bonus_text += "; armor reinforcement failed (armor already broken)"

        if ability_engine.hero_wins_bout(hero_attack, monster_attack):
            outcome = f"{loadout.hero.capitalize()} wins bout"
            tie_note = ability_engine.tie_note(hero_attack, monster_attack)
            if tie_note:
                outcome += tie_note
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
            if hero_armor > 0:
                if hero_base_armor_remaining > 0:
                    hero_base_armor_remaining = 0
                    outcome += " - base armor broken"
                else:
                    hero_armor_broken = True
                    outcome += " - hero armor broken"
            else:
                hero_health -= 1

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

        bout_number += 1

    winner = loadout.hero.capitalize() if monster_health <= 0 else ("Monster" if hero_health <= 0 else "Undecided")
    return CombatResult(
        winner=winner,
        bouts=bouts,
        final_hero_health=hero_health,
        final_monster_health=monster_health,
    )
