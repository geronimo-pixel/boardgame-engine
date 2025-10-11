"""
Detailed simulation tests to capture unusual behaviors and edge cases.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from engine.monster_loader import load_monsters, get_monster_by_name
from engine.combat_sim import simulate_warrior_vs_monster, simulate_hunter_triangle_bow_vs_monster


def print_detailed_bout(bout, bout_type="warrior"):
    """Print detailed bout information."""
    if bout_type == "warrior":
        print(f"  Bout {bout.bout_number}:")
        print(f"    Hero face: {bout.hero_face}")
        print(f"    Class faces: {bout.class_faces}")
        print(f"    Sword: {bout.sword.description} -> Atk+{bout.sword.attack}")
        print(f"    Shield: {bout.shield.description} -> Atk+{bout.shield.attack}, Armor+{bout.shield.armor}")
        print(f"    Remaining attributes: {bout.remaining_attributes}")
        print(f"    Monster skulls: {bout.rat_skulls} (total={sum(bout.rat_skulls)})")
        print(f"    Monster bonus: {bout.rat_bonus_breakdown}")
        print(f"    Total attacks: Hero={bout.hero_attack}, Monster={bout.rat_attack}")
        print(f"    Outcome: {bout.outcome}")
    else:  # hunter
        print(f"  Bout {bout.bout_number}:")
        print(f"    Hero face: {bout.hero_face}")
        print(f"    Class faces: {bout.class_faces}")
        print(f"    Rerolls used: {bout.rerolls_used}")
        print(f"    Attribute pool: {bout.attribute_pool}")
        print(f"    Attack breakdown: {bout.attack_components}")
        print(f"    Monster skulls: {bout.rat_skulls} (total={sum(bout.rat_skulls)})")
        print(f"    Total attacks: Hero={bout.hunter_attack}, Monster={bout.rat_attack}")
        print(f"    Outcome: {bout.outcome}")


def test_zero_attack_monster():
    """Test combat against Mush (0 attack)."""
    print("\n" + "=" * 80)
    print("TEST: Warrior vs Mush (0 Attack Monster)")
    print("=" * 80)

    result = simulate_warrior_vs_monster("Mush", seed=100)
    print(f"\nResult: {result.winner} wins")
    print(f"Bouts: {len(result.bouts)}")
    print(f"Final health: Hero={result.final_hero_health}, Monster={result.final_monster_health}")

    print("\nFirst 3 bouts:")
    for bout in result.bouts[:3]:
        print_detailed_bout(bout)


def test_high_armor_monster():
    """Test combat against high armor monster."""
    print("\n" + "=" * 80)
    print("TEST: Warrior vs Hedge (High Armor Monster)")
    print("=" * 80)

    result = simulate_warrior_vs_monster("Hedge", seed=200)
    print(f"\nResult: {result.winner} wins")
    print(f"Bouts: {len(result.bouts)}")
    print(f"Final health: Hero={result.final_hero_health}, Monster={result.final_monster_health}")

    print("\nFirst 5 bouts:")
    for bout in result.bouts[:5]:
        print_detailed_bout(bout)


def test_long_combat():
    """Test a potentially long combat."""
    print("\n" + "=" * 80)
    print("TEST: Warrior vs Orca (Potentially Long Combat)")
    print("=" * 80)

    result = simulate_warrior_vs_monster("Orca", seed=300, max_bouts=50)
    print(f"\nResult: {result.winner} wins")
    print(f"Bouts: {len(result.bouts)}")
    print(f"Final health: Hero={result.final_hero_health}, Monster={result.final_monster_health}")

    if len(result.bouts) >= 50:
        print("\n⚠️  WARNING: Combat reached max bout limit!")

    print(f"\nFirst 3 bouts:")
    for bout in result.bouts[:3]:
        print_detailed_bout(bout)

    print(f"\nLast 3 bouts:")
    for bout in result.bouts[-3:]:
        print_detailed_bout(bout)


def test_hunter_rerolls():
    """Test hunter reroll mechanics."""
    print("\n" + "=" * 80)
    print("TEST: Hunter vs Skelly (Reroll Mechanics)")
    print("=" * 80)

    result = simulate_hunter_triangle_bow_vs_monster("Skelly", seed=400, stage=1)
    print(f"\nResult: {result.winner} wins")
    print(f"Bouts: {len(result.bouts)}")
    print(f"Final health: Hero={result.final_hunter_health}, Monster={result.final_monster_health}")

    # Count rerolls used
    total_rerolls = sum(bout.rerolls_used for bout in result.bouts)
    bouts_with_rerolls = sum(1 for bout in result.bouts if bout.rerolls_used > 0)

    print(f"\nReroll statistics:")
    print(f"  Total rerolls used: {total_rerolls}")
    print(f"  Bouts with rerolls: {bouts_with_rerolls} / {len(result.bouts)}")

    print("\nBouts with rerolls:")
    for bout in result.bouts:
        if bout.rerolls_used > 0:
            print_detailed_bout(bout, "hunter")


def test_all_skull_counts():
    """Test monster attack calculation with various skull counts."""
    print("\n" + "=" * 80)
    print("TEST: Skull Count Attack Calculations")
    print("=" * 80)

    monsters = load_monsters()
    test_names = ["Rat", "Mush", "Skelly", "Wolf", "Hedge"]

    for name in test_names:
        monster = get_monster_by_name(name, monsters)
        print(f"\n{name} (Base Attack={monster.attack}):")
        print(f"  Skull mapping: {monster.skull_mapping}")
        print(f"  Overcharge bonus: {monster.overcharge_bonus}")

        print("  Skull -> Total Attack:")
        for skull_count in range(0, 8):
            total_attack = monster.total_attack_for_skulls(skull_count)
            bonus = monster.attack_bonus_for_skulls(skull_count)
            print(f"    {skull_count} skulls: {total_attack} (base {monster.attack} + bonus {bonus})")


def test_equipment_configurations():
    """Test different equipment activation patterns."""
    print("\n" + "=" * 80)
    print("TEST: Equipment Configuration Patterns")
    print("=" * 80)

    # Run multiple simulations and track equipment usage
    equipment_patterns = []

    for seed in range(500, 510):
        result = simulate_warrior_vs_monster("Rat", seed=seed)
        for bout in result.bouts:
            pattern = (
                bout.sword.description,
                bout.shield.description,
                sum(bout.hero_face.count(s) for s in ["square", "triangle", "circle"]),
            )
            equipment_patterns.append(pattern)

    print("\nEquipment usage patterns across 10 simulations:")
    from collections import Counter
    pattern_counts = Counter(equipment_patterns)
    for pattern, count in pattern_counts.most_common(10):
        sword, shield, total_symbols = pattern
        print(f"  {count}x: Sword={sword}, Shield={shield} (rolled {total_symbols} symbols)")


def test_tie_breaking():
    """Test tie-breaking behavior."""
    print("\n" + "=" * 80)
    print("TEST: Tie-Breaking Behavior")
    print("=" * 80)

    # Run multiple simulations and find ties
    tie_count = 0
    total_bouts = 0

    for seed in range(600, 650):
        result = simulate_warrior_vs_monster("Skelly", seed=seed)
        for bout in result.bouts:
            total_bouts += 1
            if "tie-breaker" in bout.outcome:
                tie_count += 1
                if tie_count <= 5:
                    print(f"\nTie found (seed={seed}):")
                    print_detailed_bout(bout)

    print(f"\nTie statistics:")
    print(f"  Total bouts: {total_bouts}")
    print(f"  Ties: {tie_count}")
    print(f"  Tie rate: {tie_count / total_bouts * 100:.2f}%")


def main():
    """Run all detailed tests."""
    print("=" * 80)
    print("  DETAILED SIMULATION TESTS")
    print("=" * 80)

    test_zero_attack_monster()
    test_high_armor_monster()
    test_long_combat()
    test_hunter_rerolls()
    test_all_skull_counts()
    test_equipment_configurations()
    test_tie_breaking()

    print("\n" + "=" * 80)
    print("  DETAILED TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
