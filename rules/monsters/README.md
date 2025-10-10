# 👾 Monsters

Enemies players fight, organized by rank.

## Files

- `rank1.yaml` → Early game (4-6G loot, 2-4 health)
- `rank2.yaml` → Mid game (8-15G loot, 4-6 health)
- `rank3.yaml` → Late game (15-25G loot, 6-10 health)

## Monster Composition

Each rank should have ~30 monsters with variety:
- **Easy** (30%): High win rate (~70%), low rewards
- **Medium** (50%): Balanced (~55% win rate)
- **Hard** (20%): Challenging (~40%), high rewards

## Design Balance

**Target win rates** (level-appropriate hero):
- Rank 1 vs. Level 1-2 hero: 60-70%
- Rank 2 vs. Level 3-4 hero: 50-60%
- Rank 3 vs. Level 5-6 hero: 40-50%

## Key Stats

**Health**: Bouts to defeat
**Armor**: Added to monster's roll
**Attack**: Base damage value
**Overkill**: Threshold for extra damage

## Commands

```bash
# Create new monster
@card-designer Create rank 2 monster

# Test difficulty
/simulate heroes=all vs monster=[name]

# Balance check
/balance monsters rank=2
```

## See Also

- `_examples/example_monster.yaml`
- `bosses/README.md` (for boss design)
