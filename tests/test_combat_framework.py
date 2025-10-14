import unittest
import random

from engine.combat_core import simulate_combat
from engine.combat_sim import (
    AbilityEngine,
    DiceRoller,
    DiceTables,
    EquipmentPipeline,
    EquipmentItem,
    HeroProfile,
    LoadoutAbility,
    LoadoutBuilder,
)
from engine.loadout_helpers import build_loadout, resolve_abilities, resolve_equipment
from engine.monster_loader import Monster, get_monster_by_name, load_monsters


class EquipmentPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = LoadoutBuilder(
            {"warrior": HeroProfile(name="warrior", max_health=5, base_armor=0)}
        )
        self.loadout = self.builder.build(
            hero_name="warrior",
            abilities=[],
            equipment=[
                EquipmentItem(name="Sword", category="weapon", slot="hand", hands=1),
                EquipmentItem(name="Shield", category="shield", slot="hand", hands=1),
            ],
        )
        self.pipeline = EquipmentPipeline()

    def test_warrior_sword_shield_activation(self) -> None:
        attribute_pool = {"square": 2, "triangle": 0, "circle": 1, "blank": 0}

        result = self.pipeline.resolve(self.loadout, attribute_pool)

        self.assertEqual(result.attack, 4, "Expected overcharged sword attack total.")
        self.assertEqual(result.armor, 1, "Shield should grant base armor when no attributes remain.")
        self.assertEqual(result.weapon.description, "sword combo + overcharge")
        self.assertEqual(result.secondary.description, "shield flat")


class DiceRollerFallbackTests(unittest.TestCase):
    def test_roll_generic_hero(self) -> None:
        builder = LoadoutBuilder({"mage": HeroProfile(name="mage", max_health=4, base_armor=0)})
        loadout = builder.build(hero_name="mage", abilities=[], equipment=[])

        dice_tables = DiceTables.from_loader()
        roller = DiceRoller()
        rng = random.Random(42)

        context = {"hero_abilities": 1, "class_abilities": 6}
        roll = roller.roll(loadout, dice_tables, rng, context=context)

        self.assertGreaterEqual(roll.hero_dice_rolled, 1)
        self.assertGreaterEqual(roll.class_dice_rolled, 1)
        self.assertIn("square", roll.attribute_pool)
        self.assertIsInstance(roll.hero_faces, list)
        self.assertTrue(roll.hero_faces)


class GenericEquipmentPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = LoadoutBuilder({"mage": HeroProfile(name="mage", max_health=4, base_armor=0)})
        self.pipeline = EquipmentPipeline()

    def test_generic_equipment_resolution(self) -> None:
        equipment = resolve_equipment({"weapon": "Spear", "armor": "Chainmail"})
        loadout = self.builder.build(hero_name="mage", abilities=[], equipment=equipment)
        attribute_pool = {"square": 2, "triangle": 1, "circle": 1, "blank": 0}

        result = self.pipeline.resolve(loadout, attribute_pool)

        self.assertGreaterEqual(result.attack, 0)
        self.assertGreaterEqual(result.armor, 0)
        self.assertIn("Spear", result.weapon.description)
        self.assertIsInstance(result.remaining_attributes, dict)


class AbilityEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        builder = LoadoutBuilder({"warrior": HeroProfile(name="warrior", max_health=5, base_armor=0)})
        self.loadout_with_tie = builder.build(
            hero_name="warrior",
            abilities=[LoadoutAbility(name="Always wins ties", passive=True)],
            equipment=[],
        )
        self.loadout_without_tie = builder.build(
            hero_name="warrior",
            abilities=[],
            equipment=[],
        )

    def test_tie_breaker_enabled(self) -> None:
        engine = AbilityEngine(self.loadout_with_tie)
        self.assertTrue(engine.hero_wins_bout(3, 3))
        self.assertEqual(engine.tie_note(3, 3), " (tie-breaker: CA#2)")

    def test_tie_breaker_disabled(self) -> None:
        engine = AbilityEngine(self.loadout_without_tie)
        self.assertFalse(engine.hero_wins_bout(3, 3))
        self.assertIsNone(engine.tie_note(3, 3))


class CombatIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.monsters = load_monsters()
        cls.rat = get_monster_by_name("Rat", cls.monsters)

    def test_simulate_combat_warrior_vs_rat(self) -> None:
        loadout = build_loadout(
            "warrior",
            ability_tokens=["Always wins ties"],
            equipment_config={"weapon": "Sword", "shield": "Shield"},
        )

        result = simulate_combat(loadout, self.rat, seed=1, max_bouts=10)

        self.assertEqual(result.winner, "Warrior")
        self.assertEqual(result.final_hero_health, 5)
        self.assertEqual(result.final_monster_health, 0)
        self.assertEqual(len(result.bouts), 2)

    def test_simulate_combat_hunter_vs_rat(self) -> None:
        loadout = build_loadout(
            "hunter",
            ability_tokens=[1, 11],
            equipment_config={"weapon": "Bow"},
            metadata={"stage": 1},
        )

        result = simulate_combat(loadout, self.rat, seed=1, max_bouts=10)

        self.assertEqual(result.winner, "Hunter")
        self.assertEqual(result.final_hero_health, 5)
        self.assertEqual(result.final_monster_health, 0)
        self.assertEqual(len(result.bouts), 1)

    def test_simulation_stops_after_health_loss(self) -> None:
        builder = LoadoutBuilder({"mage": HeroProfile(name="mage", max_health=4, base_armor=0)})
        loadout = builder.build(hero_name="mage", abilities=[], equipment=[])

        brute = Monster(
            name="Test Brute",
            rank=1,
            health=3,
            armor=0,
            attack=5,
            overkill=0,
            dice_code="0m",
            loot="",
        )

        result = simulate_combat(loadout, brute, seed=1, max_bouts=5)

        self.assertEqual(result.winner, "Undecided")
        self.assertEqual(result.final_hero_health, 3)
        self.assertEqual(result.final_monster_health, 3)
        self.assertEqual(len(result.bouts), 1)

class LoadoutHelperTests(unittest.TestCase):
    def test_resolve_ability_by_number(self) -> None:
        abilities = resolve_abilities("warrior", ["2"])
        self.assertTrue(any("Always wins ties" in ability.name for ability in abilities))

    def test_resolve_equipment_by_name(self) -> None:
        items = resolve_equipment({"weapon": "Sword"})
        self.assertTrue(any("Sword" in item.name for item in items))

    def test_build_loadout_defaults(self) -> None:
        loadout = build_loadout("warrior")
        ability_names = [ability.name for ability in loadout.abilities]
        self.assertTrue(any("Always wins ties" in name for name in ability_names))
        equipment_names = [item.name for item in loadout.equipment]
        self.assertTrue(any("Sword" in name for name in equipment_names))


if __name__ == "__main__":
    unittest.main()
