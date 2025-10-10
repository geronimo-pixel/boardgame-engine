# ✨ Spells

One-time use spell cards (no rank, single deck for all stages).

## Spell Mechanics

**No rank**: All spells in one deck throughout the game
**One-time use**: Discarded after activation
**Phase restrictions**: Can only be used in specific phases

## Spell Categories

### Damage Spells
- Direct damage to monsters/players
- Typically ignore armor
- Example: Fireball (5 damage, 6G)

### Utility Spells
- Card draw, gold generation, shop refresh
- Example: Merchant's Favor (draw 2 equipment cards)

### Combat Tricks
- Modify dice, reroll, change activations
- Example: Lucky Charm (reroll all dice)

### Strategic Spells
- Affect game state, steal HoB, prevent actions
- Example: Time Stop (skip opponent's turn)

## Phase Restrictions

Spells specify when they can be used:
- **Phase 1 (Starting)**: Rarely used
- **Phase 2 (Planning)**: Information/setup spells
- **Phase 3 (Hunting)**: Combat spells
- **Phase 4 (Shopping)**: Economic spells
- **Phase 5 (Ending)**: Cleanup effects

## Balance Guidelines

**Cost**: 3-10G (based on impact)
**Damage spells**: ~0.8-1.0 damage-per-gold (higher than weapons, but one-time)
**Utility spells**: Hard to quantify—playtest!

**Rule of thumb**: "Would I pay this cost for this effect once?"

## Commands

```bash
# Create spell
@card-designer Create a new spell

# Test spell impact
/simulate spell=[name] scenario=[test]

# Check spell balance
/balance spells
```

## See Also

- `_examples/example_spell.yaml`
- Rulebook spell rules (page X)
