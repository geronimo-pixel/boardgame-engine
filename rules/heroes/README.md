# 🦸 Heroes

This folder contains the 7 playable character cards.

## What's Defined Here

Each hero has:
- **Unique dice** (attribute distribution)
- **Starting equipment**
- **12 class abilities** (drawn 3 at a time when leveling)
- **Final equipment** (special gear for level 6)

## Current Heroes

1. **Warrior** → Balanced, beginner-friendly
2. **Mage** → Spell-focused, circle-heavy dice
3. **Rogue** → High-burst, skull-heavy dice
4. **Paladin** → Tank, cube + triangle focus
5. **Ranger** → Versatile, ranged attacks
6. **Cleric** → Support, healing abilities
7. **Barbarian** → High-risk, high-reward

(Populate as you design them!)

## Design Considerations

**Dice balance**: Each hero should have a unique attribute distribution
- Warrior: 🔵🔵⚪🔺💀 (balanced)
- Mage: ⚪⚪⚪🔺💀 (circle-focused)
- Rogue: 💀💀💀🔵⚪ (skull-focused)

**Power level**: All heroes should have similar win rates (~50-55%)
- Use `/balance heroes` to check
- Test against all rank 1 monsters

**Playstyle**: Each hero should feel distinct
- Don't just change numbers—change mechanics!

## Commands

```bash
# Create new hero
@card-designer I want to create a new hero called [name]

# Test hero performance
/simulate hero=[name] vs monsters=all_rank1

# Compare all heroes
/balance heroes
```

## See Also

- `_examples/example_hero.yaml` → Full hero template
- `docs/01_what_is_this_repo.md` → Understanding the system
