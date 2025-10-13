#!/usr/bin/env python3
"""
Combat Visualizer - Pietro's Testing Tool

A simple CLI tool that lets Pietro test game balance by running combat
simulations and seeing visual, bout-by-bout results.

No code shown - only game mechanics in plain language.
"""
import sys
from pathlib import Path
from typing import Optional

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
    simulate_warrior_vs_monster,
    simulate_hunter_triangle_bow_vs_monster,
    BoutLog,
    CombatResult,
    HunterBoutLog,
    HunterCombatResult,
)
from engine.monster_loader import load_monsters
from engine.dice_loader import load_all_dice

console = Console()


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
    """Format attribute pool (square/triangle/circle counts)."""
    parts = []
    if pool.get("square", 0) > 0:
        parts.append(f"■ x{pool['square']}")
    if pool.get("triangle", 0) > 0:
        parts.append(f"▲ x{pool['triangle']}")
    if pool.get("circle", 0) > 0:
        parts.append(f"● x{pool['circle']}")

    return ", ".join(parts) if parts else "(none)"


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

    # Phase 3: Monster Roll
    console.print("\n[bold yellow]💀 MONSTER ROLL PHASE[/bold yellow]")
    console.print("─" * 60)

    total_skulls = sum(bout.rat_skulls)
    skull_icons = " ".join(["💀" * s for s in bout.rat_skulls if s > 0])
    console.print(f"  Dice results: {bout.rat_skulls}")
    console.print(f"  Total skulls: {total_skulls} {skull_icons}")
    console.print(f"  Bonus: {bout.rat_bonus_breakdown}")
    console.print(f"\n  [bold red]Total Monster Attack: {bout.rat_attack}[/bold red]")

    # Phase 4: Combat Resolution
    console.print("\n[bold yellow]⚡ COMBAT RESOLUTION PHASE[/bold yellow]")
    console.print("─" * 60)

    # Outcome
    if "wins" in bout.outcome.lower():
        if "hero" in bout.outcome.lower() or "hunter" in bout.outcome.lower():
            console.print(f"  [bold green]✓ {bout.outcome}[/bold green]")
        else:
            console.print(f"  [bold red]✗ {bout.outcome}[/bold red]")
    else:
        console.print(f"  [yellow]{bout.outcome}[/yellow]")


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

def show_hero_menu() -> str:
    """Show hero selection menu."""
    console.print("\n[bold cyan]SELECT HERO:[/bold cyan]")
    console.print("  1. Warrior (sword & shield)")
    console.print("  2. Hunter (bow & reroll ability)")
    console.print("  [dim]More heroes coming soon...[/dim]")

    choice = Prompt.ask("Choose hero", choices=["1", "2"], default="1")
    return "warrior" if choice == "1" else "hunter"


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


def get_seed_choice() -> Optional[int]:
    """Ask if user wants to use a seed."""
    console.print("\n[bold cyan]RANDOM SEED:[/bold cyan]")
    console.print("  Using a seed lets you replay the exact same combat.")

    use_seed = Prompt.ask("Use a seed?", choices=["y", "n"], default="n")

    if use_seed.lower() == "y":
        seed = IntPrompt.ask("Enter seed number", default=42)
        return seed

    return None


def run_combat(hero: str, monster: str, seed: Optional[int]):
    """Run the combat simulation and display results."""
    console.clear()

    # Header
    console.print()
    title = f"[bold white on blue] {hero.upper()} vs {monster.upper()} [/bold white on blue]"
    if seed is not None:
        title += f" [dim](seed: {seed})[/dim]"
    console.print(Panel(title, box=box.DOUBLE))

    # Run simulation
    console.print("\n[dim]Running combat simulation...[/dim]")

    if hero == "warrior":
        result = simulate_warrior_vs_monster(monster, seed=seed, max_bouts=100)
    elif hero == "hunter":
        result = simulate_hunter_triangle_bow_vs_monster(monster, seed=seed, stage=1, max_bouts=100)
    else:
        console.print(f"[red]Hero '{hero}' not yet implemented![/red]")
        return

    console.clear()

    # Show combat header again
    console.print()
    console.print(Panel(title, box=box.DOUBLE))

    # Display bouts
    for i, bout in enumerate(result.bouts):
        if hero == "warrior":
            display_warrior_bout(bout, i, len(result.bouts))
        elif hero == "hunter":
            display_hunter_bout(bout, i, len(result.bouts))

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
    display_combat_summary(result, hero, monster, seed)


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
    except Exception as e:
        console.print(f"[red]Error loading dice: {e}[/red]")
        return

    # Main loop
    while True:
        try:
            # Select hero
            hero = show_hero_menu()

            # Select monster
            monster = show_monster_menu(monsters)

            # Get seed
            seed = get_seed_choice()

            # Run combat
            run_combat(hero, monster, seed)

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
