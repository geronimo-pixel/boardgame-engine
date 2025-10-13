# Combat Loadouts & Data Pipeline

This document explains how to add new equipment or abilities and how to
use the CLI helper to explore combat outcomes.

## 1. Updating Raw Data

All source-of-truth lists live under `Original files/`. When you add or
change entries there, regenerate the structured YAML so the engine picks
up the new content:

```bash
python tools/build_abilities_yaml.py   # abilities → rules/heroes/abilities.yaml
python tools/build_equipment_yaml.py   # equipment → rules/equipment/rank1_equipment.yaml
python tools/build_spells_yaml.py      # spells → rules/spells/spells.yaml
python tools/build_monsters_yaml.py    # monsters → rules/monsters/monsters.yaml
```

Each script clamps numeric bonuses to zero or higher, so negative stats
can’t slip into the runtime data.

## 2. Defining Equipment & Abilities

The generated YAML files are what the engine reads when building combat
loadouts. A minimal entry needs:

- **Equipment** (`rules/equipment/rank1_equipment.yaml`)
  - `name`, `category`, `item_type` (e.g., `one_hand`, `chest`), cost
  - activation blocks (`activations`, `overcharge_effects`, `flat_bonuses`)
  - the scripts automatically infer slots/hands when building combat loadouts

- **Abilities** (`rules/heroes/abilities.yaml`)
  - `hero`, `type` (`hero` or `class`), `effect`, optional `number`
  - `cooldown` and `phase_limit` (single value or list)

Whenever you add new entries, re-run the builder scripts so the core data
stays in sync.

## 3. CLI Helper (`tools/combat_cli.py`)

Use the CLI to assemble random loadouts, toggle abilities, and run batches
of fights. Key options:

```bash
python tools/combat_cli.py \
    --hero warrior \
    --monster Rat \
    --trials 20 \
    --random-abilities 2 \
    --random-equipment
```

Other useful flags:

| Flag | Description |
|------|-------------|
| `--ability VALUE` | Include ability by number or text match (repeatable). |
| `--random-abilities N` | Add `N` random abilities after manual picks. |
| `--weapon / --armor / --charm` | Force a specific item by name. |
| `--random-equipment` | Fill any empty slots with random gear. |
| `--seed SEED` | Fixed seed for reproducible batches. |
| `--trials N` | Number of combats to simulate. |

The script loads hero ability/equipment YAML and enforces slot rules via
the new loadout builder. Results include win/loss/draw counts and echo the
chosen abilities/gear.

## 4. Extending Heroes

To plug a new hero into the combat framework:

1. Create the raw ability list in `Original files/H&C Abilities.txt` and
   regenerate `abilities.yaml`.
2. Add one or more hero profiles to `LoadoutBuilder` (if non-default health/armor).
3. Implement hero-specific dice logic and equipment activation in
   `engine/combat_sim.py` (see Warrior/Hunter examples).
4. Optionally add integration tests under `tests/` that verify new hero
   loadouts against sample monsters.

With these steps in place, simulations, the CLI, and stage runs will all
recognize the new hero automatically.
