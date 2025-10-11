"""
Verify monster data against source file to find discrepancies.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from engine.monster_loader import load_monsters, get_monster_by_name


def main():
    """Compare loaded monsters with manual checks from source."""
    monsters = load_monsters()

    print("=" * 80)
    print("MONSTER DATA VERIFICATION")
    print("=" * 80)

    # Check for duplicate names
    names = [m.name for m in monsters]
    duplicates = set([name for name in names if names.count(name) > 1])

    if duplicates:
        print(f"\n❌ FOUND DUPLICATE MONSTER NAMES: {duplicates}")
        for dup_name in duplicates:
            print(f"\n{dup_name} appears {names.count(dup_name)} times:")
            for i, m in enumerate(monsters):
                if m.name == dup_name:
                    print(f"  Instance {i+1}:")
                    print(f"    Health: {m.health}, Armor: {m.armor}, Attack: {m.attack}")
                    print(f"    Dice: {m.dice_code}")
                    print(f"    Skull mapping: {m.skull_mapping}")
                    print(f"    Overcharge: {m.overcharge_bonus}")
                    print(f"    Loot: {m.loot}")
    else:
        print("\n✓ No duplicate monster names found")

    # Manual verification of expected monsters based on source file
    print("\n" + "=" * 80)
    print("MANUAL VERIFICATION OF KEY MONSTERS")
    print("=" * 80)

    # Expected data from source file (lines 13-22, first entry)
    print("\nFirst Rat entry (from lines 13-22):")
    print("  Expected: Health=1, Armor=1, Attack=2, Overkill=2")
    print("  Expected: Dice=2m")
    print("  Expected: 1sk=+2Att, 2sk=+3Att, OC=+2Att")
    print("  Expected: Loot=4G")

    # Check if this version exists
    rat_instances = [m for m in monsters if m.name == "Rat"]
    if len(rat_instances) == 1:
        rat = rat_instances[0]
        print(f"\n  Loaded (only one Rat found):")
        print(f"    Health={rat.health}, Armor={rat.armor}, Attack={rat.attack}, Overkill={rat.overkill}")
        print(f"    Dice={rat.dice_code}")
        print(f"    Skull mapping={rat.skull_mapping}")
        print(f"    Overcharge={rat.overcharge_bonus}")
        print(f"    Loot={rat.loot}")

        # Check which version was loaded
        if rat.armor == 1 and rat.attack == 2 and rat.loot == "4G":
            print("\n  ✓ Loaded the FIRST Rat entry (lines 13-22)")
        elif rat.armor == 0 and rat.attack == 1 and rat.loot == "2G":
            print("\n  ⚠️  Loaded the SECOND Rat entry (lines 23-31)")
        else:
            print("\n  ❌ Loaded data doesn't match either entry!")
    elif len(rat_instances) == 2:
        print(f"\n  Found {len(rat_instances)} Rat entries - checking both:")
        for i, rat in enumerate(rat_instances, 1):
            print(f"\n  Rat #{i}:")
            print(f"    Health={rat.health}, Armor={rat.armor}, Attack={rat.attack}, Overkill={rat.overkill}")
            print(f"    Dice={rat.dice_code}")
            print(f"    Skull mapping={rat.skull_mapping}")
            print(f"    Overcharge={rat.overcharge_bonus}")
            print(f"    Loot={rat.loot}")

    # Expected data from source file (lines 23-31, second entry)
    print("\n" + "-" * 80)
    print("Second Rat entry (from lines 23-31):")
    print("  Expected: Health=1, Armor=0, Attack=1, Overkill=2")
    print("  Expected: Dice=2m")
    print("  Expected: 1sk=+2Att, 2sk=+2Att, OC=+1Att")
    print("  Expected: Loot=2G")

    # Verify other key monsters
    print("\n" + "=" * 80)
    print("VERIFICATION OF OTHER KEY MONSTERS")
    print("=" * 80)

    test_cases = {
        "Mush": {
            "health": 1, "armor": 3, "attack": 0, "overkill": 2,
            "dice": "2m", "loot": "2G"
        },
        "Skelly": {
            "health": 2, "armor": 0, "attack": 3, "overkill": 3,
            "dice": "2m", "loot": "3G"
        },
    }

    for name, expected in test_cases.items():
        print(f"\n{name}:")
        try:
            monster = get_monster_by_name(name, monsters)
            matches = []
            mismatches = []

            for key, expected_value in expected.items():
                actual_value = getattr(monster, key if key != "dice" else "dice_code")
                if actual_value == expected_value:
                    matches.append(f"{key}={actual_value}")
                else:
                    mismatches.append(f"{key}: expected {expected_value}, got {actual_value}")

            if mismatches:
                print(f"  ❌ Mismatches: {', '.join(mismatches)}")
                print(f"  ✓ Matches: {', '.join(matches)}")
            else:
                print(f"  ✓ All fields match: {', '.join(matches)}")

        except KeyError:
            print(f"  ❌ Monster not found!")

    # List all monsters
    print("\n" + "=" * 80)
    print(f"ALL {len(monsters)} LOADED MONSTERS")
    print("=" * 80)

    for i, m in enumerate(monsters, 1):
        print(f"{i:2d}. {m.name:15s} (Rank {m.rank}) - HP:{m.health} Armor:{m.armor} Atk:{m.attack} Dice:{m.dice_code} Loot:{m.loot}")


if __name__ == "__main__":
    main()
