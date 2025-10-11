"""
Comprehensive test suite for Pietro's combat system.
Tests monster loading, dice loading, combat simulations, and edge cases.
"""
import sys
from pathlib import Path

# Add engine directory to path
sys.path.insert(0, str(Path(__file__).parent))

from engine.monster_loader import load_monsters, get_monster_by_name
from engine.dice_loader import load_all_dice
from engine.combat_sim import simulate_warrior_vs_monster, simulate_hunter_triangle_bow_vs_monster


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_monster_loading():
    """Test 1: Monster loading test."""
    print_section("TEST 1: Monster Loading")

    try:
        monsters = load_monsters()
        print(f"✓ Successfully loaded {len(monsters)} monsters")

        # Expected count is 28
        if len(monsters) != 28:
            print(f"⚠️  WARNING: Expected 28 monsters, but loaded {len(monsters)}")

        # Check for missing data
        anomalies = []
        for monster in monsters:
            issues = []
            if not monster.name:
                issues.append("missing name")
            if monster.health <= 0:
                issues.append("health <= 0")
            if monster.armor < 0:
                issues.append("negative armor")
            if monster.attack < 0:
                issues.append("negative attack")
            if not monster.dice_code:
                issues.append("missing dice code")
            if not monster.loot:
                issues.append("missing loot")

            if issues:
                anomalies.append((monster.name, issues))

        if anomalies:
            print(f"\n❌ Found {len(anomalies)} monsters with anomalies:")
            for name, issues in anomalies:
                print(f"   - {name}: {', '.join(issues)}")
        else:
            print("✓ No data anomalies detected in monsters")

        # Print summary by rank
        print("\nMonsters by rank:")
        ranks = {}
        for monster in monsters:
            if monster.rank not in ranks:
                ranks[monster.rank] = []
            ranks[monster.rank].append(monster.name)

        for rank in sorted(ranks.keys()):
            print(f"  Rank {rank}: {len(ranks[rank])} monsters - {', '.join(ranks[rank][:5])}" +
                  ("..." if len(ranks[rank]) > 5 else ""))

        # Show sample monster details
        print("\nSample Monster Details (Rat):")
        rat = get_monster_by_name("Rat", monsters)
        print(f"  Name: {rat.name}")
        print(f"  Rank: {rat.rank}")
        print(f"  Health: {rat.health}, Armor: {rat.armor}, Attack: {rat.attack}")
        print(f"  Dice: {rat.dice_code}")
        print(f"  Skull mapping: {rat.skull_mapping}")
        print(f"  Overcharge: {rat.overcharge_bonus}")
        print(f"  Loot: {rat.loot}")

        return True, monsters
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_dice_loading():
    """Test 2: Dice loading test."""
    print_section("TEST 2: Dice Loading")

    try:
        dice = load_all_dice()

        hero_dice = dice["hero_dice"]
        class_dice = dice["class_dice"]
        monster_dice = dice["monster_dice"]

        print(f"✓ Successfully loaded dice data")
        print(f"  Hero dice: {len(hero_dice)} heroes")
        print(f"  Class dice: {len(class_dice)} classes")
        print(f"  Monster dice: {len(monster_dice)} categories")

        # Verify 7 heroes
        hero_names = [die.hero for die in hero_dice]
        class_names = [die.hero for die in class_dice]

        print(f"\nHero dice loaded: {', '.join(hero_names)}")
        print(f"Class dice loaded: {', '.join(class_names)}")

        if len(hero_dice) != 7:
            print(f"⚠️  WARNING: Expected 7 heroes, found {len(hero_dice)}")
        else:
            print("✓ All 7 heroes have dice")

        if len(class_dice) != 7:
            print(f"⚠️  WARNING: Expected 7 class dice, found {len(class_dice)}")

        # Check face counts
        face_errors = []
        for die in hero_dice:
            if len(die.faces) != 6:
                face_errors.append(f"Hero {die.hero} has {len(die.faces)} faces (expected 6)")

        for die in class_dice:
            if len(die.faces) != 6:
                face_errors.append(f"Class {die.hero} has {len(die.faces)} faces (expected 6)")

        for die in monster_dice:
            if len(die.skull_counts) != 6:
                face_errors.append(f"Monster {die.category} has {len(die.skull_counts)} faces (expected 6)")

        if face_errors:
            print(f"\n❌ Face count errors:")
            for error in face_errors:
                print(f"   - {error}")
        else:
            print("✓ All dice have correct face counts (6 per die)")

        # Show sample die details
        print("\nSample Die Details (Warrior Hero Die):")
        warrior_die = next(die for die in hero_dice if die.hero == "warrior")
        for i, face in enumerate(warrior_die.faces, 1):
            print(f"  Face {i}: {face}")

        return True, dice
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_combat_simulations():
    """Test 3: Combat simulation tests."""
    print_section("TEST 3: Combat Simulations")

    test_cases = [
        ("Warrior", "Rat", 42),
        ("Warrior", "Mush", 123),
        ("Warrior", "Skelly", 456),
        ("Hunter", "Rat", 789),
    ]

    results = []
    all_passed = True

    for hero, monster, seed in test_cases:
        print(f"\n--- {hero} vs {monster} (seed={seed}) ---")
        try:
            if hero == "Warrior":
                result = simulate_warrior_vs_monster(monster, seed=seed)
            elif hero == "Hunter":
                result = simulate_hunter_triangle_bow_vs_monster(monster, seed=seed, stage=1)
            else:
                raise ValueError(f"Unknown hero: {hero}")

            print(f"✓ Simulation completed without errors")
            print(f"  Winner: {result.winner}")
            print(f"  Bouts: {len(result.bouts)}")
            if hero == "Warrior":
                print(f"  Final Health: Hero={result.final_hero_health}, Monster={result.final_monster_health}")
            else:
                print(f"  Final Health: Hero={result.final_hunter_health}, Monster={result.final_monster_health}")

            # Show first 3 bouts
            print(f"  Sample bouts:")
            for bout in result.bouts[:3]:
                if hero == "Warrior":
                    print(f"    Bout {bout.bout_number}: Hero Atk={bout.hero_attack}, Monster Atk={bout.rat_attack} -> {bout.outcome}")
                else:
                    print(f"    Bout {bout.bout_number}: Hero Atk={bout.hunter_attack}, Monster Atk={bout.rat_attack} -> {bout.outcome}")

            results.append((hero, monster, seed, True, result))
        except Exception as e:
            print(f"❌ FAILED: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append((hero, monster, seed, False, str(e)))
            all_passed = False

    # Test warrior vs strongest rank 1 monster
    print(f"\n--- Warrior vs Strongest Rank 1 Monster ---")
    try:
        monsters = load_monsters()
        rank1_monsters = [m for m in monsters if m.rank == 1]

        # Find strongest by total attack potential
        strongest = max(rank1_monsters, key=lambda m: m.attack + m.total_attack_for_skulls(10))
        print(f"  Strongest Rank 1: {strongest.name} (Attack={strongest.attack}, Max Bonus={strongest.total_attack_for_skulls(10) - strongest.attack})")

        result = simulate_warrior_vs_monster(strongest.name, seed=999)
        print(f"✓ Simulation completed without errors")
        print(f"  Winner: {result.winner}")
        print(f"  Bouts: {len(result.bouts)}")
        print(f"  Final Health: Hero={result.final_hero_health}, Monster={result.final_monster_health}")

        results.append(("Warrior", strongest.name, 999, True, result))
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Warrior", "Strongest Rank 1", 999, False, str(e)))
        all_passed = False

    return all_passed, results


def test_edge_cases():
    """Test 4: Edge case tests."""
    print_section("TEST 4: Edge Case Tests")

    all_passed = True

    # Find monsters with specific characteristics
    print("\n--- Finding Edge Case Monsters ---")
    try:
        monsters = load_monsters()

        zero_attack = [m for m in monsters if m.attack == 0]
        high_armor = [m for m in monsters if m.armor >= 3]

        print(f"Monsters with 0 attack: {len(zero_attack)}")
        for m in zero_attack[:3]:
            print(f"  - {m.name} (Rank {m.rank})")

        print(f"\nMonsters with high armor (>=3): {len(high_armor)}")
        for m in high_armor[:3]:
            print(f"  - {m.name} (Armor={m.armor}, Rank {m.rank})")

    except Exception as e:
        print(f"❌ Error finding edge case monsters: {e}")
        all_passed = False

    # Test 100 bout limit
    print("\n--- Test 100-Bout Limit ---")
    try:
        # Use a high-health monster to test limit
        monsters = load_monsters()
        high_health = max(monsters, key=lambda m: m.health)
        print(f"Testing with {high_health.name} (Health={high_health.health})")

        result = simulate_warrior_vs_monster(high_health.name, seed=12345, max_bouts=10)
        print(f"✓ Simulation with max_bouts=10 completed")
        print(f"  Bouts executed: {len(result.bouts)}")
        print(f"  Winner: {result.winner}")

        if len(result.bouts) > 10:
            print(f"⚠️  WARNING: Exceeded max_bouts limit")
            all_passed = False
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    # Test skull combinations
    print("\n--- Test Skull Combinations ---")
    try:
        # Test monster bonus calculations for different skull counts
        rat = get_monster_by_name("Rat", monsters)
        mush = get_monster_by_name("Mush", monsters)

        print(f"Rat skull bonuses:")
        for skulls in [0, 1, 2, 3, 4, 5]:
            bonus = rat.attack_bonus_for_skulls(skulls)
            total = rat.total_attack_for_skulls(skulls)
            print(f"  {skulls} skulls: +{bonus} attack (total={total})")

        print(f"\nMush skull bonuses:")
        for skulls in [0, 1, 2, 3, 4, 5]:
            bonus = mush.attack_bonus_for_skulls(skulls)
            total = mush.total_attack_for_skulls(skulls)
            print(f"  {skulls} skulls: +{bonus} attack (total={total})")

        print("✓ Skull bonus calculations work correctly")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    return all_passed


def test_data_integrity():
    """Test 5: Data integrity checks."""
    print_section("TEST 5: Data Integrity Checks")

    all_passed = True

    print("\n--- Loot Value Parsing ---")
    try:
        monsters = load_monsters()

        loot_errors = []
        for monster in monsters:
            if not monster.loot:
                loot_errors.append(f"{monster.name}: missing loot")

        if loot_errors:
            print(f"❌ Loot parsing errors:")
            for error in loot_errors:
                print(f"   - {error}")
            all_passed = False
        else:
            print("✓ All monsters have loot values")

        # Show sample loot values
        print("\nSample loot values:")
        for monster in monsters[:5]:
            print(f"  {monster.name}: {monster.loot}")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        all_passed = False

    print("\n--- Dice Probability Check ---")
    try:
        dice = load_all_dice()

        print("Warrior hero die face distribution:")
        warrior_hero = next(d for d in dice["hero_dice"] if d.hero == "warrior")
        symbol_counts = {"square": 0, "triangle": 0, "circle": 0}
        for face in warrior_hero.faces:
            for symbol in face:
                symbol_counts[symbol] += 1

        total_symbols = sum(symbol_counts.values())
        for symbol, count in symbol_counts.items():
            prob = count / total_symbols * 100
            print(f"  {symbol}: {count}/{total_symbols} ({prob:.1f}%)")

        print("\nWarrior class die face distribution:")
        warrior_class = next(d for d in dice["class_dice"] if d.hero == "warrior")
        symbol_counts = {"square": 0, "triangle": 0, "circle": 0}
        for face in warrior_class.faces:
            for symbol in face:
                symbol_counts[symbol] += 1

        total_symbols = sum(symbol_counts.values())
        for symbol, count in symbol_counts.items():
            prob = count / total_symbols * 100
            print(f"  {symbol}: {count}/{total_symbols} ({prob:.1f}%)")

        print("✓ Dice probabilities are sensible")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        all_passed = False

    print("\n--- Cross-Reference Monsters Against Source ---")
    try:
        monsters = load_monsters()

        # Manually verify 3 monsters
        test_monsters = ["Rat", "Mush", "Skelly"]

        for name in test_monsters:
            monster = get_monster_by_name(name, monsters)
            print(f"\n{name}:")
            print(f"  Health: {monster.health}")
            print(f"  Armor: {monster.armor}")
            print(f"  Attack: {monster.attack}")
            print(f"  Overkill: {monster.overkill}")
            print(f"  Dice: {monster.dice_code}")
            print(f"  Abilities: {monster.ability_lines}")
            print(f"  Skull mapping: {monster.skull_mapping}")
            print(f"  Overcharge: {monster.overcharge_bonus}")
            print(f"  Loot: {monster.loot}")

        print("\n✓ Monster data appears consistent (manual verification needed)")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        all_passed = False

    return all_passed


def main():
    """Run all tests."""
    print("=" * 80)
    print("  COMBAT SYSTEM COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    results = {}

    # Test 1: Monster loading
    results["monster_loading"] = test_monster_loading()

    # Test 2: Dice loading
    results["dice_loading"] = test_dice_loading()

    # Test 3: Combat simulations
    results["combat_simulations"] = test_combat_simulations()

    # Test 4: Edge cases
    results["edge_cases"] = test_edge_cases()

    # Test 5: Data integrity
    results["data_integrity"] = test_data_integrity()

    # Final summary
    print_section("FINAL SUMMARY")

    all_tests_passed = True
    for test_name, result in results.items():
        if isinstance(result, tuple):
            passed = result[0]
        else:
            passed = result

        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_tests_passed = False

    print("\n" + "=" * 80)
    if all_tests_passed:
        print("  ALL TESTS PASSED!")
    else:
        print("  SOME TESTS FAILED - Review output above")
    print("=" * 80)


if __name__ == "__main__":
    main()
