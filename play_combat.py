#!/usr/bin/env python3
"""
Combat Visualizer - Pietro's Testing Tool

A simple CLI tool that lets Pietro test game balance by running combat
simulations and seeing visual, bout-by-bout results.

No code shown - only game mechanics in plain language.
"""
import sys
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt
    from rich import box
    from rich.columns import Columns
    from rich.text import Text
except ImportError:
    print("ERROR: 'rich' library not installed.")
    print("Install it with: pip install rich")
    sys.exit(1)

from engine.combat_sim import (
    BoutLog,
    HunterBoutLog,
    EquipmentResult,
    EquipmentResolution,
    LoadoutAbility,
    _compute_square_sword_options,
    _compute_square_shield_options,
    _deduct_attributes,
)
from engine.combat_core import simulate_combat
from engine.loadout_helpers import (
    build_loadout,
    load_ability_dataset,
    load_equipment_dataset,
    get_default_loadout_config,
)
from engine.monster_loader import load_monsters, get_monster_by_name
from engine.dice_loader import load_all_dice

console = Console()


def build_equipment_allocator(console: Console):
    """
    Return a callback that asks the player how to spend their symbols on equipment before combat
    resolution. Currently supports Warrior loadouts (sword + shield).
    """

    ATTRIBUTE_LABELS = {
        "square": "Squares",
        "triangle": "Triangles",
        "circle": "Circles",
        "blank": "Wild",
    }

    def _format_cost(used_attributes: Dict[str, int]) -> str:
        if not used_attributes or all(value == 0 for value in used_attributes.values()):
            return "No attributes needed"
        parts: List[str] = []
        for attr, amount in used_attributes.items():
            if amount <= 0:
                continue
            label = ATTRIBUTE_LABELS.get(attr, attr.title())
            parts.append(f"{label} x{amount}")
        return ", ".join(parts) if parts else "No attributes needed"

    def _format_effects(result: EquipmentResult) -> str:
        effects: List[str] = []
        if result.attack:
            effects.append(f"Attack +{result.attack}")
        if result.armor:
            effects.append(f"Armor +{result.armor}")
        if result.armor_damage:
            effects.append(f"Armor Damage +{result.armor_damage}")
        if not effects:
            effects.append("No effect")
        return ", ".join(effects)

    def _normalize_used_attributes(used: Optional[Dict[str, int]]) -> Dict[str, int]:
        if not used:
            return {}
        return {key: int(value) for key, value in used.items() if value}

    def _allocation_key(used: Optional[Dict[str, int]]) -> Tuple[Tuple[str, int], ...]:
        normalized = _normalize_used_attributes(used)
        return tuple(sorted(normalized.items()))

    def _format_allocation_label(used: Optional[Dict[str, int]]) -> str:
        normalized = _normalize_used_attributes(used)
        if not normalized:
            return "None"
        parts = []
        for attr, amount in normalized.items():
            label = ATTRIBUTE_LABELS.get(attr, attr.title())
            parts.append(f"{label} x{amount}")
        return ", ".join(parts)

    def _parse_allocation_input(text: str) -> Dict[str, int]:
        cleaned = text.strip().lower()
        if not cleaned or cleaned in {"none", "skip", "0"}:
            return {}

        alias_map = {
            "square": "square",
            "squares": "square",
            "triangle": "triangle",
            "triangles": "triangle",
            "circle": "circle",
            "circles": "circle",
            "wild": "blank",
            "blank": "blank",
            "blanks": "blank",
        }

        tokens = cleaned.replace(",", " ").replace(";", " ").split()
        allocation: Dict[str, int] = {}
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            if "=" in token or ":" in token:
                key, value = token.replace(":", "=").split("=", 1)
                idx += 1
            else:
                if idx + 1 >= len(tokens):
                    raise ValueError("Incomplete attribute specification.")
                key = token
                value = tokens[idx + 1]
                idx += 2
            key = key.strip()
            value = value.strip()
            attr = alias_map.get(key)
            if not attr:
                raise ValueError(f"Unknown attribute '{key}'. Use square/triangle/circle/wild.")
            try:
                amount = int(value)
            except ValueError as exc:
                raise ValueError(f"Invalid amount '{value}' for {attr}.") from exc
            if amount < 0:
                raise ValueError("Attribute amounts must be zero or positive.")
            allocation[attr] = allocation.get(attr, 0) + amount
        return {k: v for k, v in allocation.items() if v > 0}

    def _prompt_item_choice(
        item_name: str,
        item_attributes: Dict[str, Optional[str]],
        options: List[EquipmentResult],
        remaining_pool: Dict[str, int],
    ) -> Tuple[EquipmentResult, Dict[str, int], str]:
        console.print(f"\n[bold cyan]{item_name.upper()} OPTIONS[/bold cyan]")
        alignment_parts: List[str] = []
        for slot in ("primary", "secondary", "tertiary"):
            face = item_attributes.get(slot) if item_attributes else None
            face_display = face.title() if isinstance(face, str) and face.lower() != "null" else "None"
            alignment_parts.append(f"{slot.title()}: {face_display}")
        console.print(f"  Attribute alignment: {' | '.join(alignment_parts)}")
        console.print(f"  Available symbols right now: {format_attribute_pool(remaining_pool)}")
        console.print("  Tell me how many symbols you want to spend (e.g., 'square=1 circle=1').")
        console.print("  Type 'none' if you want to keep everything for later.")

        console.print("  Enter attributes to spend (e.g., 'square=1 circle=1'). Type 'none' to skip.")

        allocation_map: Dict[Tuple[Tuple[str, int], ...], EquipmentResult] = {}
        for option in options:
            key = _allocation_key(option.used_attributes)
            if key not in allocation_map:
                allocation_map[key] = option
            else:
                existing = allocation_map[key]
                if option.attack > existing.attack:
                    allocation_map[key] = option

        unique_options = list(allocation_map.values())
        for option in unique_options:
            cost_text = _format_cost(option.used_attributes)
            console.print(
                f"  - Cost {cost_text:>18} -> {option.description or 'Custom'} ({_format_effects(option)})"
            )
        console.print("  - Cost None -> No activation")

        while True:
            user_input = Prompt.ask(
                f"  Spend attributes on {item_name}",
                default="none",
            ).strip()
            try:
                allocation = _parse_allocation_input(user_input)
            except ValueError as exc:
                console.print(f"[yellow]{exc}[/yellow]")
                continue

            if not allocation:
                chosen = EquipmentResult(description=f"{item_name} (no activation)")
                console.print(f"    -> {item_name} stays idle (no symbols spent).")
                return chosen, remaining_pool.copy(), "None"

            key = tuple(sorted(allocation.items()))
            prototype = allocation_map.get(key)
            if not prototype:
                console.print(
                    "[yellow]Those symbols do not match any activation. Use the costs listed above.[/yellow]"
                )
                continue

            chosen = EquipmentResult(
                attack=prototype.attack,
                armor=prototype.armor,
                armor_damage=prototype.armor_damage,
                used_attributes=dict(prototype.used_attributes),
                description=prototype.description,
                metadata=dict(prototype.metadata),
            )
            updated_pool = _deduct_attributes(remaining_pool, allocation)
            if updated_pool is None:
                console.print(
                    "[red]Not enough symbols for that activation.[/red] "
                    f"Needed: {_format_cost(chosen.used_attributes)} | "
                    f"Available: {format_attribute_pool(remaining_pool)}"
                )
                continue
            detail_label = _format_allocation_label(allocation)
            console.print(f"    -> {item_name} uses: {detail_label}")
            return chosen, updated_pool, detail_label

    def allocator(
        *,
        loadout,
        attribute_pool: Dict[str, int],
        dice_context,
        monster,
        monster_roll: Dict[str, Any],
        pipeline,
        context: Dict[str, Any],
    ):
        fight_type_value = (context or {}).get("fight_type") or loadout.metadata.get("fight_type")
        fight_type_key = fight_type_value.lower() if isinstance(fight_type_value, str) else ""
        fight_type_display = fight_type_key.title() if fight_type_key else "this mode"

        def _ability_suffix(ability: LoadoutAbility) -> str:
            statuses: List[str] = []
            modes = getattr(ability, "modes", ())
            if getattr(ability, "passive", False):
                status = "passive"
                if fight_type_key and modes and fight_type_key not in modes:
                    status += f" - inactive in {fight_type_display}"
                statuses.append(status)
            else:
                if modes:
                    modes_display = ", ".join(mode.title() for mode in modes)
                    if fight_type_key and fight_type_key not in modes:
                        statuses.append(f"inactive now (needs {modes_display})")
                    else:
                        statuses.append(f"only {modes_display}")
            if not statuses:
                return ""
            return " [" + "; ".join(statuses) + "]"

        console.print("\n[bold magenta]ABILITY WINDOW[/bold magenta]")
        active_abilities = [ab for ab in loadout.abilities if not getattr(ab, "passive", False)]
        activatable_abilities = [
            ab
            for ab in active_abilities
            if not getattr(ab, "modes", ()) or not fight_type_key or fight_type_key in getattr(ab, "modes", ())
        ]
        locked_active_abilities = [
            ab for ab in active_abilities if ab not in activatable_abilities
        ]
        if loadout.abilities:
            console.print("  Abilities ready this bout:")
            for idx, ability in enumerate(loadout.abilities, start=1):
                ability_name = ability.name or f"Ability {idx}"
                effect_text = ability.description or ability_name
                passive_note = _ability_suffix(ability)
                if effect_text.lower() == ability_name.lower():
                    console.print(f"    {idx}. {ability_name}{passive_note}")
                else:
                    console.print(f"    {idx}. {ability_name}{passive_note}: {effect_text}")
        else:
            console.print("  [dim]No abilities equipped (passive bonuses only).[/dim]")

        if activatable_abilities:
            console.print("\n  You can trigger these abilities now:")
            for index, ability in enumerate(activatable_abilities, start=1):
                effect_text = ability.description or ability.name
                suffix = _ability_suffix(ability)
                console.print(f"    {index}. {ability.name}{suffix}: {effect_text}")
            console.print("  Enter numbers separated by commas to fire multiple abilities, or leave blank to skip.")

            selected_indices: List[int] = []
            while True:
                response = Prompt.ask("  Activate abilities (numbers)", default="").strip()
                if not response:
                    break
                parts = [part.strip() for part in response.replace(";", ",").split(",") if part.strip()]
                invalid = False
                chosen: List[int] = []
                for part in parts:
                    if not part.isdigit():
                        console.print(f"[yellow]'{part}' is not a number. Try again.[/yellow]")
                        invalid = True
                        break
                    value = int(part)
                    if not 1 <= value <= len(activatable_abilities):
                        console.print(f"[yellow]Ability {value} is out of range. Try again.[/yellow]")
                        invalid = True
                        break
                    chosen.append(value)
                if invalid:
                    continue
                selected_indices = sorted(set(chosen))
                break

            if selected_indices:
                activated_labels: List[str] = []
                for idx in selected_indices:
                    ability = activatable_abilities[idx - 1]
                    activated_labels.append(ability.name)
                ability_note = "Activated: " + ", ".join(activated_labels)
            else:
                ability_note = "Activated: (none)"
        else:
            if locked_active_abilities:
                locked_names = ", ".join(ab.name for ab in locked_active_abilities)
                console.print(
                    f"  [dim]Active abilities ({locked_names}) are not available in {fight_type_display}.[/dim]"
                    if fight_type_key
                    else f"  [dim]Active abilities ({locked_names}) are not available right now.[/dim]"
                )
                ability_note = (
                    f"Activated: (none); active inactive ({fight_type_display}): {locked_names}"
                    if fight_type_key
                    else f"Activated: (none); active inactive: {locked_names}"
                )
            else:
                console.print("  [dim]Only passive abilities available; they stay active automatically.[/dim]")
                ability_note = "Passive (auto)"

        inactive_passives = [
            ability.name
            for ability in loadout.abilities
            if getattr(ability, "passive", False)
            and fight_type_key
            and getattr(ability, "modes", ())
            and fight_type_key not in ability.modes
        ]
        if inactive_passives:
            ability_note += (
                f"; passive inactive ({fight_type_display}): {', '.join(inactive_passives)}"
                if fight_type_key
                else f"; passive inactive: {', '.join(inactive_passives)}"
            )

        hero_key = loadout.hero.lower()
        if hero_key != "warrior":
            console.print("[dim]Manual equipment assignment only available for the Warrior. Using defaults.[/dim]")
            fallback = pipeline.resolve(loadout, attribute_pool.copy(), context=context)
            return fallback, {"ability_choice": ability_note, "selected_equipment_label": "Automatic resolution"}

        console.print("\n[bold magenta]EQUIPMENT ASSIGNMENT[/bold magenta]")
        console.print(f"  Rolled symbols: {format_attribute_pool(attribute_pool)}")
        console.print(
            f"  Monster skulls: {monster_roll['skulls']} -> "
            f"{monster_roll['total_attack']} attack ({monster_roll['bonus_text']})"
        )

        weapon_item = next((item for item in loadout.equipment if item.category == "weapon"), None)
        shield_item = next((item for item in loadout.equipment if item.category == "shield"), None)
        if not weapon_item or not shield_item:
            console.print("[yellow]Warrior loadout missing sword or shield. Falling back to automatic resolution.[/yellow]")
            fallback = pipeline.resolve(loadout, attribute_pool.copy(), context=context)
            return fallback, {"ability_choice": ability_note, "selected_equipment_label": "Automatic resolution"}

        weapon_options = _compute_square_sword_options(attribute_pool)
        shield_options = _compute_square_shield_options(attribute_pool)

        remaining_pool = attribute_pool.copy()
        weapon_choice, remaining_pool, weapon_label = _prompt_item_choice(
            weapon_item.name,
            weapon_item.attributes,
            weapon_options,
            remaining_pool,
        )
        console.print(f"    Remaining after weapon: {format_attribute_pool(remaining_pool)}")

        shield_choice, remaining_pool, shield_label = _prompt_item_choice(
            shield_item.name,
            shield_item.attributes,
            shield_options,
            remaining_pool,
        )
        console.print(f"    Remaining after shield: {format_attribute_pool(remaining_pool)}")

        def _display_label(raw: str) -> str:
            if not raw or raw.lower() == "none":
                return "None"
            return raw

        combined_label = f"{_display_label(weapon_label)} + {_display_label(shield_label)}"

        final_resolution = EquipmentResolution(
            attack=weapon_choice.attack + shield_choice.attack,
            armor=shield_choice.armor,
            armor_damage=weapon_choice.armor_damage + shield_choice.armor_damage,
            weapon=weapon_choice,
            secondary=shield_choice,
            remaining_attributes=remaining_pool,
            metadata={
                "weapon_description": weapon_choice.description or weapon_item.name,
                "shield_description": shield_choice.description or shield_item.name,
                "manual_label": combined_label,
            },
        )

        return final_resolution, {
            "ability_choice": ability_note,
            "selected_equipment_label": combined_label,
        }

    return allocator


# ============================================================================
# Visualization Helpers
# ============================================================================

def symbol_to_icon(symbol: str) -> str:
    """Convert dice symbols to visual icons."""
    symbols = {
        "square": "■",
        "triangle": "▲",
        "circle": "●",
    }
    return symbols.get(symbol, symbol)


def format_dice_faces(faces: list) -> str:
    """Format a list of dice face symbols into a readable string."""
    if not faces:
        return "(empty)"

    icons = []
    for face in faces:
        if isinstance(face, list):
            # Hero/class die (can have multiple symbols per face)
            icons.extend([symbol_to_icon(s) for s in face])
        else:
            # Simple symbol
            icons.append(symbol_to_icon(face))

    return " ".join(icons)


def format_attribute_pool(pool: dict) -> str:
    """Format attribute pools using simple words."""
    labels = [
        ("square", "Squares"),
        ("triangle", "Triangles"),
        ("circle", "Circles"),
        ("blank", "Wild"),
    ]
    segments: List[str] = []
    for key, label in labels:
        amount = pool.get(key, 0)
        if amount > 0:
            segments.append(f"{label} x{amount}")
    return ", ".join(segments) if segments else "(none)"


def health_bar(current: int, maximum: int) -> str:
    """Create a visual health bar using hearts."""
    full_hearts = "❤️ " * current
    empty_hearts = "🖤 " * (maximum - current)
    return full_hearts + empty_hearts


# ============================================================================
# Combat Display Functions
# ============================================================================

def display_warrior_bout(bout: BoutLog, bout_index: int, total_bouts: int):
    """Display a single Warrior combat bout with all phases."""

    # Header
    console.print()
    header = f"[bold cyan]BOUT {bout.bout_number}[/bold cyan] (of {total_bouts})"
    console.print(Panel(header, box=box.DOUBLE, style="cyan"))

    # Phase 1: Dice Roll
    console.print("\n[bold yellow]🎲 DICE ROLL PHASE[/bold yellow]")
    console.print("─" * 60)

    console.print(f"  Hero Die:    {format_dice_faces([bout.hero_face])}")
    console.print(f"  Class Die 1: {format_dice_faces([bout.class_faces[0]])}")
    console.print(f"  Class Die 2: {format_dice_faces([bout.class_faces[1]])}")
    console.print()
    console.print(f"  [dim]Total symbols: {format_attribute_pool(bout.remaining_attributes)}[/dim]")

    # Phase 2: Equipment Activation
    console.print("\n[bold yellow]⚔️  EQUIPMENT ACTIVATION PHASE[/bold yellow]")
    console.print("─" * 60)

    # Sword
    sword_desc = bout.sword.description.replace("sword ", "")
    console.print(f"  Sword ({sword_desc}):")
    console.print(f"    → Attack: [green]+{bout.sword.attack}[/green]")
    if bout.sword.used_attributes.get("square", 0) > 0 or bout.sword.used_attributes.get("circle", 0) > 0:
        used = format_attribute_pool(bout.sword.used_attributes)
        console.print(f"    → Uses: {used}")

    # Shield
    shield_desc = bout.shield.description.replace("shield ", "")
    console.print(f"\n  Shield ({shield_desc}):")
    if bout.shield.attack > 0:
        console.print(f"    → Attack: [green]+{bout.shield.attack}[/green]")
    if bout.shield.armor > 0:
        console.print(f"    → Armor: [blue]+{bout.shield.armor}[/blue]")
    if bout.shield.used_attributes.get("square", 0) > 0 or bout.shield.used_attributes.get("circle", 0) > 0:
        used = format_attribute_pool(bout.shield.used_attributes)
        console.print(f"    → Uses: {used}")

    # Remaining
    console.print(f"\n  [dim]Leftover symbols: {format_attribute_pool(bout.remaining_attributes)}[/dim]")

    # Phase 3: Monster Roll
    console.print("\n[bold yellow]💀 MONSTER ROLL PHASE[/bold yellow]")
    console.print("─" * 60)

    total_skulls = sum(bout.rat_skulls)
    skull_icons = " ".join(["💀" * s for s in bout.rat_skulls if s > 0])
    console.print(f"  Dice results: {bout.rat_skulls}")
    console.print(f"  Total skulls: {total_skulls} {skull_icons}")
    console.print(f"  Bonus: {bout.rat_bonus_breakdown}")

    # Phase 4: Combat Resolution
    console.print("\n[bold yellow]⚡ COMBAT RESOLUTION PHASE[/bold yellow]")
    console.print("─" * 60)

    console.print(f"  Warrior attack: [bold green]{bout.hero_attack}[/bold green]")
    console.print(f"  Monster attack: [bold red]{bout.rat_attack}[/bold red]")

    # Outcome
    console.print()
    if "wins" in bout.outcome.lower():
        if "hero" in bout.outcome.lower() or "warrior" in bout.outcome.lower():
            console.print(f"  [bold green]✓ {bout.outcome}[/bold green]")
        else:
            console.print(f"  [bold red]✗ {bout.outcome}[/bold red]")
    else:
        console.print(f"  [yellow]{bout.outcome}[/yellow]")


def display_hunter_bout(bout: HunterBoutLog, bout_index: int, total_bouts: int):
    """Display a single Hunter combat bout with all phases."""

    # Header
    console.print()
    header = f"[bold cyan]BOUT {bout.bout_number}[/bold cyan] (of {total_bouts})"
    console.print(Panel(header, box=box.DOUBLE, style="cyan"))

    # Phase 1: Dice Roll
    console.print("\n[bold yellow]🎲 DICE ROLL PHASE[/bold yellow]")
    console.print("─" * 60)

    console.print(f"  Hero Die:    {format_dice_faces([bout.hero_face])}")
    console.print(f"  Class Die 1: {format_dice_faces([bout.class_faces[0]])}")
    console.print(f"  Class Die 2: {format_dice_faces([bout.class_faces[1]])}")

    if bout.rerolls_used > 0:
        console.print(f"\n  [bold magenta]♻️  Rerolled {bout.rerolls_used} dice (Hunter CA #11)[/bold magenta]")

    console.print()
    console.print(f"  [dim]Total symbols: {format_attribute_pool(bout.attribute_pool)}[/dim]")

    # Phase 2: Attack Calculation
    console.print("\n[bold yellow]🏹 ATTACK CALCULATION PHASE[/bold yellow]")
    console.print("─" * 60)

    for component, value in bout.attack_components.items():
        console.print(f"  {component}: +{value}")

    console.print(f"\n  [bold green]Total Hunter Attack: {bout.hunter_attack}[/bold green]")


def display_generic_bout(hero: str, bout: BoutLog, bout_index: int, total_bouts: int):
    """Display a combat bout for heroes that use the generic simulator."""

    console.print()
    header = f"[bold cyan]BOUT {bout.bout_number}[/bold cyan] (of {total_bouts})"
    console.print(Panel(header, box=box.DOUBLE, style="cyan"))

    # Phase 1: Dice roll
    console.print("\n[bold yellow]DICE ROLL PHASE[/bold yellow]")
    console.print("-" * 60)
    if bout.hero_faces_all:
        hero_faces = bout.hero_faces_all
    else:
        hero_faces = [bout.hero_face] if bout.hero_face else []

    hero_face_text = format_dice_faces(hero_faces[:1])
    console.print(f"  Hero Die:    {hero_face_text}")
    if bout.class_faces:
        for idx, class_face in enumerate(bout.class_faces, start=1):
            console.print(f"  Class Die {idx}: {format_dice_faces([class_face])}")

    console.print()
    console.print(f"  Rolled symbols: {format_attribute_pool(bout.hero_attribute_pool)}")
    spent_pool: Dict[str, int] = {}
    for key, value in bout.hero_attribute_pool.items():
        remaining = bout.remaining_attributes.get(key, 0)
        spent = max(0, value - remaining)
        if spent > 0:
            spent_pool[key] = spent
    if spent_pool:
        console.print(f"  Spent this bout: {format_attribute_pool(spent_pool)}")
    console.print(f"  Remaining symbols: {format_attribute_pool(bout.remaining_attributes)}")

    # Phase 2: Equipment / abilities
    console.print("\n[bold yellow]HERO ACTION PHASE[/bold yellow]")
    console.print("-" * 60)

    primary_desc = bout.sword.description or "Primary action"
    console.print(f"  Primary: {primary_desc}")
    console.print(f"    Attack: [green]+{bout.sword.attack}[/green]")
    if bout.sword.armor > 0:
        console.print(f"    Armor: [blue]+{bout.sword.armor}[/blue]")
    if bout.sword.armor_damage > 0:
        console.print(f"    Armor Damage: [red]+{bout.sword.armor_damage}[/red]")
    if bout.sword.used_attributes:
        used = format_attribute_pool(bout.sword.used_attributes)
        console.print(f"    Uses: {used}")

    secondary_desc = bout.shield.description or "Secondary items"
    console.print(f"\n  Secondary: {secondary_desc}")
    if bout.shield.attack > 0:
        console.print(f"    Attack: [green]+{bout.shield.attack}[/green]")
    if bout.shield.armor > 0:
        console.print(f"    Armor: [blue]+{bout.shield.armor}[/blue]")
    if bout.shield.armor_damage > 0:
        console.print(f"    Armor Damage: [red]+{bout.shield.armor_damage}[/red]")
    if bout.shield.used_attributes:
        used = format_attribute_pool(bout.shield.used_attributes)
        console.print(f"    Uses: {used}")

    if bout.hero_attack_breakdown:
        console.print("\n  Ability bonuses triggered automatically:")
        for source, amount in bout.hero_attack_breakdown:
            console.print(f"    [green]+{amount} attack from {source}[/green]")
    else:
        console.print("\n  [dim]No hero abilities added attack this bout.[/dim]")

    # Phase 3: Monster roll
    console.print("\n[bold yellow]MONSTER ROLL PHASE[/bold yellow]")
    console.print("-" * 60)
    total_skulls = sum(bout.rat_skulls)
    console.print(f"  Dice results: {bout.rat_skulls}")
    console.print(f"  Total skulls: {total_skulls}")
    console.print(f"  Bonus: {bout.rat_bonus_breakdown}")
    console.print(f"  Base attack: {bout.monster_base_attack}  |  Bonus attack: {bout.monster_bonus_attack}")

    # Phase 4: Resolution
    console.print("\n[bold yellow]COMBAT RESOLUTION[/bold yellow]")
    console.print("-" * 60)
    if bout.selected_equipment_label:
        console.print(f"  Selected combo: {bout.selected_equipment_label}")
    if bout.ability_choice:
        console.print(f"  Ability choice: {bout.ability_choice} abilities")
    console.print(f"  {_format_hero_name(hero)} attack: [bold green]{bout.hero_attack}[/bold green]")
    hero_components: List[str] = []
    if bout.sword.attack:
        hero_components.append(f"{bout.sword.description or 'Weapon'} +{bout.sword.attack}")
    if bout.shield.attack:
        hero_components.append(f"{bout.shield.description or 'Secondary'} +{bout.shield.attack}")
    for source, amount in bout.hero_attack_breakdown:
        hero_components.append(f"{source} +{amount}")
    if not hero_components:
        hero_components.append("Base roll only")
    console.print(f"    Breakdown: {', '.join(hero_components)}")

    console.print(f"  Monster attack: [bold red]{bout.rat_attack}[/bold red]")
    monster_components = [
        f"Base {bout.monster_base_attack}",
        f"Bonus +{bout.monster_bonus_attack}",
    ]
    console.print(f"    Breakdown: {', '.join(monster_components)}")
    console.print()
    console.print(f"  Outcome: [bold]{bout.outcome}[/bold]")


def display_combat_summary(result, hero_name: str, monster_name: str, seed: Optional[int]):
    """Display final combat summary."""
    console.print()
    console.print("═" * 60)

    # Winner announcement
    if result.winner == "undecided":
        winner_text = "[yellow]UNDECIDED (max bouts reached)[/yellow]"
    elif "hero" in result.winner.lower() or hero_name.lower() in result.winner.lower():
        winner_text = f"[bold green]{hero_name.upper()} WINS![/bold green]"
    else:
        winner_text = f"[bold red]{monster_name.upper()} WINS![/bold red]"

    console.print(Panel(winner_text, box=box.DOUBLE))

    # Stats
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Stat", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Total Bouts", str(len(result.bouts)))
    table.add_row("Final Hero Health", str(result.final_hero_health if hasattr(result, 'final_hero_health') else result.final_hunter_health))
    table.add_row("Final Monster Health", str(result.final_monster_health))
    if seed is not None:
        table.add_row("Seed Used", str(seed))

    console.print(table)
    console.print("═" * 60)


# ============================================================================
# Main Menu & Interaction
# ============================================================================

def _format_hero_name(hero_key: str) -> str:
    """Human-friendly hero name for menu display."""
    return hero_key.replace("_", " ").title()


def prompt_for_ability_tokens(hero: str, ability_dataset: dict, fight_type: Optional[str] = None) -> List[str]:
    """Prompt user to select abilities for the chosen hero."""
    hero_key = hero.lower()
    all_entries = ability_dataset.get(hero_key, [])
    if not all_entries:
        console.print("[dim]No ability list found for this hero (using defaults).[/dim]")
        return []

    fight_type_key = (fight_type or "").lower()
    console.print("\n[bold cyan]SELECT ABILITIES[/bold cyan]")
    console.print(
        "[dim]Pick the abilities you want to bring. Passive cards must be selected to stay active. "
        "Enter numbers separated by commas; leave blank to use defaults.[/dim]"
    )

    for idx, entry in enumerate(all_entries, start=1):
        number = entry.get("number")
        number_text = f"#{number} " if number is not None else ""
        labels: List[str] = []
        if entry.get("passive"):
            labels.append("passive")
        modes = entry.get("modes") or []
        if modes:
            modes_display = ", ".join(mode.title() for mode in modes)
            if fight_type_key and fight_type_key not in modes:
                labels.append(f"only {modes_display} (inactive now)")
            else:
                labels.append(f"only {modes_display}")
        suffix = f" [{' ; '.join(labels)}]" if labels else ""
        console.print(f"  {idx}. {number_text}{entry.get('effect', '')}{suffix}")

    response = Prompt.ask("Abilities", default="")
    if not response.strip():
        return []

    tokens: List[str] = []
    for part in response.split(","):
        selection = part.strip()
        if not selection:
            continue
        try:
            index = int(selection)
        except ValueError:
            console.print(f"[yellow]Ignoring invalid ability selection '{selection}'.[/yellow]")
            continue
        if not 1 <= index <= len(entries):
            console.print(f"[yellow]Ability index {index} out of range.[/yellow]")
            continue
        entry = entries[index - 1]
        if entry.get("number") is not None:
            tokens.append(str(entry["number"]))
        else:
            tokens.append(entry.get("effect", ""))
    return tokens


def prompt_for_equipment_choices(equipment_dataset: dict) -> List[str]:
    """Prompt user to select equipment items."""
    selections: List[str] = []
    console.print("\n[bold cyan]SELECT EQUIPMENT[/bold cyan]")
    console.print("[dim]Pick item indices by category. Leave blank to keep defaults.[/dim]")

    category_labels = {
        "weapons": "Weapons",
        "armors": "Armors",
        "charms": "Charms",
    }
    attribute_titles = {"primary": "Primary", "secondary": "Secondary", "tertiary": "Tertiary"}

    for key, label in category_labels.items():
        entries = equipment_dataset.get(key, [])
        if not entries:
            continue

        console.print(f"\n{label}:")
        for idx, entry in enumerate(entries, start=1):
            base_name = entry.get("name", "Unknown")
            attributes = entry.get("attributes") or {}
            parts: List[str] = []
            for attr_key in ("primary", "secondary", "tertiary"):
                face = attributes.get(attr_key)
                face_display = face.title() if isinstance(face, str) and face.lower() != "null" else "None"
                parts.append(f"{attribute_titles[attr_key]}: {face_display}")
            attribute_summary = " | ".join(parts)
            console.print(f"  {idx}. {base_name} ({attribute_summary})")

        response = Prompt.ask(f"{label} (comma separated indices)", default="")
        if not response.strip():
            continue

        for part in response.split(","):
            selection = part.strip()
            if not selection:
                continue
            try:
                index = int(selection)
            except ValueError:
                console.print(f"[yellow]Ignoring invalid selection '{selection}'.[/yellow]")
                continue
            if not 1 <= index <= len(entries):
                console.print(f"[yellow]Equipment index {index} out of range.[/yellow]")
                continue
            chosen_entry = entries[index - 1]
            token = chosen_entry.get("id") or chosen_entry.get("name", "Unknown")
            selections.append(token)

    return selections


def derive_seed_for_loadout(loadout, monster_name: str) -> int:
    """Derive a deterministic seed from the selected hero, abilities, equipment, and monster."""
    ability_names = sorted(ability.name for ability in loadout.abilities)
    equipment_names = sorted(item.name for item in loadout.equipment)
    stage_value = str(loadout.metadata.get("stage", "")) if hasattr(loadout, "metadata") else ""
    base = "|".join(
        [
            loadout.hero.lower(),
            ",".join(ability_names),
            ",".join(equipment_names),
            monster_name.lower(),
            stage_value,
        ]
    )
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def choose_fight_type() -> str:
    """Prompt the user for the fight type they want to simulate."""
    console.print("\n[bold cyan]SELECT FIGHT TYPE:[/bold cyan]")
    options = [
        ("hunt", "Hunt (hero vs monster)"),
        ("duel", "Duel (1 player vs 1 player)"),
        ("coop", "Co-op (2 players vs 1 monster)"),
        ("clash", "Clash (party vs party)"),
    ]

    for index, (_, label) in enumerate(options, start=1):
        console.print(f"  {index}. {label}")

    choices = [str(index) for index in range(1, len(options) + 1)]
    selection = Prompt.ask("Choose fight type", choices=choices, default="1")
    fight_key = options[int(selection) - 1][0]

    if fight_key != "hunt":
        console.print(
            "[yellow]That fight mode is not implemented yet. "
            "Available modes: Hunt (hero vs monster).[/yellow]"
        )
        return "hunt"

    return fight_key


def choose_stage() -> int:
    """Ask the player which stage to simulate (currently only stage 1 is supported)."""
    console.print("\n[bold cyan]SELECT STAGE:[/bold cyan]")
    stage = IntPrompt.ask("Stage", default=1)
    if stage != 1:
        console.print("[yellow]Only stage 1 is implemented right now. Defaulting to stage 1.[/yellow]")
        stage = 1
    return stage


def show_hero_menu(hero_names: list[str]) -> str:
    """Show hero selection menu."""
    console.print("\n[bold cyan]SELECT HERO:[/bold cyan]")
    numbered_choices = []
    for index, hero in enumerate(hero_names, start=1):
        console.print(f"  {index}. {_format_hero_name(hero)}")
        numbered_choices.append(str(index))

    choice = Prompt.ask("Choose hero", choices=numbered_choices, default="1")
    selected_index = max(1, min(int(choice), len(hero_names)))
    return hero_names[selected_index - 1]


def show_monster_menu(monsters: list) -> str:
    """Show monster selection menu."""
    console.print("\n[bold cyan]SELECT MONSTER:[/bold cyan]")

    # Group by rank
    by_rank = {}
    for m in monsters:
        if m.rank not in by_rank:
            by_rank[m.rank] = []
        by_rank[m.rank].append(m.name)

    # Show monsters
    index = 1
    monster_list = []
    for rank in sorted(by_rank.keys()):
        console.print(f"\n[yellow]Rank {rank}:[/yellow]")
        for name in sorted(by_rank[rank]):
            console.print(f"  {index}. {name}")
            monster_list.append(name)
            index += 1
            if index > 20:  # Limit display
                console.print("  [dim]... and more[/dim]")
                break
        if index > 20:
            break

    # Get choice
    if len(monster_list) == 0:
        console.print("[red]No monsters found![/red]")
        sys.exit(1)

    choice_num = IntPrompt.ask("Choose monster number", default=1)
    choice_num = max(1, min(choice_num, len(monster_list)))

    return monster_list[choice_num - 1]


def run_combat(loadout, monster, seed: Optional[int], fight_type: Optional[str] = None):
    """Run the combat simulation and display results."""
    hero = loadout.hero
    monster_name = monster.name
    console.clear()

    # Header
    console.print()
    title = f"[bold white on blue] {hero.upper()} vs {monster_name.upper()} [/bold white on blue]"
    if seed is not None:
        title += f" [dim](seed: {seed})[/dim]"
    console.print(Panel(title, box=box.DOUBLE))

    # Run simulation
    ability_list = ", ".join(ability.name for ability in loadout.abilities) or "(none)"
    equipment_list = ", ".join(item.name for item in loadout.equipment) or "(none)"
    console.print(f"[dim]Abilities: {ability_list}[/dim]")
    console.print(f"[dim]Equipment: {equipment_list}[/dim]")
    stage_value = loadout.metadata.get("stage") if hasattr(loadout, "metadata") else None
    console.print(f"[dim]Stage: {stage_value or 1}[/dim]")
    console.print("\n[dim]Running combat simulation...[/dim]")
    console.print(f"[dim]Auto seed derived from selection: {seed}[/dim]")

    equipment_allocator = build_equipment_allocator(console)
    sim_options = {
        "equipment_allocator": equipment_allocator,
    }
    if fight_type:
        sim_options["fight_type"] = fight_type.lower()
    else:
        sim_options["fight_type"] = loadout.metadata.get("fight_type")

    result = simulate_combat(
        loadout,
        monster,
        seed=seed,
        max_bouts=100,
        options=sim_options,
    )

    # Show combat header again
    console.print()
    console.print(Panel(title, box=box.DOUBLE))

    # Display bouts
    for i, bout in enumerate(result.bouts):
        display_generic_bout(hero, bout, i, len(result.bouts))

        # Pause after each bout (except last)
        if i < len(result.bouts) - 1:
            should_continue = Prompt.ask(
                "\n[cyan]Continue to next bout?[/cyan]",
                choices=["y", "n", "skip"],
                default="y"
            )
            if should_continue == "n":
                console.print("[yellow]Combat display paused.[/yellow]")
                break
            elif should_continue == "skip":
                console.print("[dim]Skipping to final result...[/dim]")
                break

    # Final summary
    display_combat_summary(result, hero, monster_name, seed)


def main():
    """Main entry point."""
    console.clear()

    # Welcome
    console.print()
    console.print(Panel(
        "[bold cyan]COMBAT SIMULATOR[/bold cyan]\n\n"
        "Test your game balance by watching heroes fight monsters.\n"
        "See exactly how dice rolls, equipment, and abilities work!",
        box=box.DOUBLE,
        border_style="cyan"
    ))

    # Load game data
    console.print("\n[dim]Loading monsters...[/dim]")
    try:
        monsters = load_monsters()
        console.print(f"[green]✓ Loaded {len(monsters)} monsters[/green]")
    except Exception as e:
        console.print(f"[red]Error loading monsters: {e}[/red]")
        return

    console.print("[dim]Loading dice...[/dim]")
    try:
        dice = load_all_dice()
        console.print(f"[green]✓ Loaded {len(dice['hero_dice'])} hero dice[/green]")
        hero_names = list(dict.fromkeys(die.hero for die in dice["hero_dice"]))
    except Exception as e:
        console.print(f"[red]Error loading dice: {e}[/red]")
        return

    try:
        ability_dataset = load_ability_dataset()
        equipment_dataset = load_equipment_dataset()
    except Exception as e:
        console.print(f"[red]Error loading ability or equipment data: {e}[/red]")
        return

    # Main loop
    while True:
        try:
            fight_type = choose_fight_type()
            if fight_type != "hunt":
                continue

            stage = choose_stage()

            # Select hero
            hero = show_hero_menu(hero_names)

            # Select abilities and equipment
            ability_tokens = prompt_for_ability_tokens(hero, ability_dataset, fight_type=fight_type)
            equipment_choices = prompt_for_equipment_choices(equipment_dataset)
            equipment_config = equipment_choices if equipment_choices else None

            try:
                default_config = get_default_loadout_config(hero)
                metadata = dict(default_config.get("metadata", {}))
                metadata["stage"] = stage
                metadata["fight_type"] = fight_type
                loadout = build_loadout(
                    hero,
                    ability_tokens=ability_tokens,
                    equipment_config=equipment_config,
                    metadata=metadata,
                )
            except Exception as exc:
                console.print(f"[red]Unable to build loadout: {exc}[/red]")
                continue

            # Select monster
            monster_name = show_monster_menu(monsters)
            try:
                monster_obj = get_monster_by_name(monster_name, monsters)
            except Exception as exc:
                console.print(f"[red]Error selecting monster: {exc}[/red]")
                continue

            # Derive seed and run combat
            seed = derive_seed_for_loadout(loadout, monster_obj.name)
            run_combat(loadout, monster_obj, seed, fight_type=fight_type)

            # Play again?
            console.print()
            again = Prompt.ask(
                "[cyan]Run another combat?[/cyan]",
                choices=["y", "n"],
                default="y"
            )

            if again.lower() != "y":
                console.print("\n[green]Thanks for testing! Happy game designing! 🎲[/green]\n")
                break

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Exiting...[/yellow]\n")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print("[yellow]Please report this to Giovanni[/yellow]\n")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            break


if __name__ == "__main__":
    main()
