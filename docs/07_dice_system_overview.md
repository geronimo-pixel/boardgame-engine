# Dice System Overview

This guide explains how the new dice specification fits into the engine and how to extend it as we add more game logic.

## File Layout

- `rules/_core/dice.yaml` stores every die in the game:
  - Hero dice map the primary/secondary/tertiary attribute priorities per hero.
  - Class dice mirror each hero but with weaker face patterns.
  - Monster dice list the skull counts for minion, chief, and boss categories.
- `engine/dice_loader.py` reads that YAML file, expands the shorthand tokens, and validates the results.

## Loading Pipeline

1. `dice_loader.load_raw_config()` loads the YAML file (requires `pyyaml`).
2. `load_hero_dice()` and `load_class_dice()` expand the `primary/secondary/tertiary` placeholders into raw symbols (`square`, `triangle`, `circle`).
3. `load_monster_dice()` verifies that each monster die defines six non-negative skull counts.
4. `load_all_dice()` returns every die in one dictionary so future systems can request everything at once.

If the YAML is malformed the loader raises `DiceConfigError` with a human-friendly message that pinpoints the issue.

## Integration Roadmap

1. **Symbol semantics** — Define what each symbol contributes during combat (attack strength, armor, resource gain). Store that mapping alongside the dice for easy lookup.
2. **Roll mechanics** — Add utilities that roll a die, return the selected face, and translate symbols into mechanical effects using the mapping from step 1.
3. **Ability hooks** — Extend the loader so hero/class abilities can modify dice pools (add extra dice, reroll, convert blanks).
4. **Simulation bridge** — Plug the roll utilities into combat simulations once the engine modules exist. Start with a single scenario that exercises one hero die and one monster die.
5. **Validation tooling** — Incorporate dice checks into `/validate` so rule changes that reference unknown dice or symbols are caught early.

Follow this sequence to grow the engine without rewriting early work. As soon as step 1 is complete we can start wiring combat resolution logic on top of the dice loader.
