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
    equipment_allocator = options.get("equipment_allocator")
    context_overrides = {
        key: value for key, value in options.items() if key not in {"equipment_allocator"}
    }

    pre_combat = loadout.create_pre_combat_state()
    extra_context: Dict[str, Any] = loadout.metadata.copy()
    extra_context.update(context_overrides)

    dice_roller = DiceRoller()
    equipment_pipeline = EquipmentPipeline()
    ability_engine = AbilityEngine(
        loadout,
        stage=extra_context.get("stage"),
        pre_combat_state=pre_combat,
    )

    hero_health = pre_combat.health
    hero_base_armor = pre_combat.armor

    monster_health = monster.health
    monster_armor = monster.armor
    monster_armor_reinforcement = 0

    bouts: List[BoutLog] = []
    bout_number = 1

    hero_armor_broken = False
    hero_base_armor_remaining = hero_base_armor

    while hero_health > 0 and monster_health > 0 and bout_number <= max_bouts:
        prev_hero_health = hero_health
        prev_monster_health = monster_health
        dice_context = dice_roller.roll(loadout, dice_tables, rng, context=extra_context)
        attribute_pool = dice_context.attribute_pool.copy()

        skulls, monster_attack, bonus_text, armor_bonus = _roll_monster_skulls(monster, dice_tables, rng)
        if armor_bonus:
            if monster_armor > 0:
                monster_armor_reinforcement += armor_bonus
                bonus_text += f"; armor reinforcement +{armor_bonus} (total {monster_armor_reinforcement})"
            else:
                bonus_text += "; armor reinforcement failed (armor already broken)"

        extra_bout_info: Dict[str, Any] = {}
        if equipment_allocator:
            allocation_result = equipment_allocator(
                loadout=loadout,
                attribute_pool=attribute_pool.copy(),
                dice_context=dice_context,
                monster=monster,
                monster_roll={
                    "skulls": skulls,
                    "total_attack": monster_attack,
                    "bonus_text": bonus_text,
                },
                pipeline=equipment_pipeline,
                context=extra_context,
            )
            if allocation_result:
                if isinstance(allocation_result, tuple) and len(allocation_result) == 2:
                    equipment_result, extra_payload = allocation_result
                    extra_bout_info = extra_payload or {}
                else:
                    equipment_result = allocation_result
            else:
                equipment_result = equipment_pipeline.resolve(loadout, attribute_pool, context=extra_context)
        else:
            equipment_result = equipment_pipeline.resolve(loadout, attribute_pool, context=extra_context)

        hero_face = dice_context.hero_faces[0] if dice_context.hero_faces else []
        class_faces = dice_context.class_faces

        hero_attack_breakdown: List[Tuple[str, int]] = []
        hero_attack = equipment_result.attack
        ability_attack_bonus, ability_breakdown = ability_engine.attack_bonus_after_roll()
        if ability_attack_bonus:
            hero_attack += ability_attack_bonus
            hero_attack_breakdown.extend(ability_breakdown)

        hero_armor = hero_base_armor_remaining
        if not hero_armor_broken:
            hero_armor += equipment_result.armor

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

        label_override = extra_bout_info.get("selected_equipment_label")
        if not label_override:
            weapon_desc = equipment_result.metadata.get("weapon_description")
            shield_desc = equipment_result.metadata.get("shield_description")
            pieces = [part for part in (weapon_desc, shield_desc) if part]
            label_override = " + ".join(pieces) if pieces else None

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
                monster_base_attack=monster.attack,
                monster_bonus_attack=monster_attack - monster.attack,
                hero_attack=hero_attack,
                hero_attack_breakdown=hero_attack_breakdown,
                ability_choice=extra_bout_info.get("ability_choice"),
                selected_equipment_label=label_override,
                hero_armor=hero_armor,
                outcome=outcome,
                hero_attribute_pool=dice_context.attribute_pool,
                hero_dice_rolled=dice_context.hero_dice_rolled,
                class_dice_rolled=dice_context.class_dice_rolled,
                hero_abilities=dice_context.hero_abilities_available,
                class_abilities=dice_context.class_abilities_available,
                hero_faces_all=dice_context.hero_faces,
            )
        )

        if hero_health < prev_hero_health or monster_health < prev_monster_health:
            break

        bout_number += 1

    winner = loadout.hero.capitalize() if monster_health <= 0 else ("Monster" if hero_health <= 0 else "Undecided")
    return CombatResult(
        winner=winner,
        bouts=bouts,
        final_hero_health=hero_health,
        final_monster_health=monster_health,
    )
