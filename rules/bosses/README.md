# 🐉 Bosses

Stage-ending bosses with Hearts of the Boss (HoB) and stage rules.

## Structure

Each stage has 4 bosses (drawn randomly at stage start):
- `rank1_bosses.yaml` → 4 stage 1 bosses
- `rank2_bosses.yaml` → 4 stage 2 bosses
- `rank3_bosses.yaml` → 4 stage 3 bosses

## Boss Mechanics

**Hearts of the Boss**: Must defeat boss multiple times (4-8 HoB)
**Stage Rule**: Special rule active until boss defeated
**One fight per turn**: Players can only fight boss once per turn (abilities unlimited)

## Design Guidelines

### Stage 1 Bosses
- 4-5 HoB (8-12 total VP)
- Health: 4-6 bouts
- Win rate: 40-50%
- Stage rule: Light impact

### Stage 2 Bosses
- 5-6 HoB (12-18 total VP)
- Health: 6-8 bouts
- Win rate: 30-40%
- Stage rule: Moderate impact

### Stage 3 Bosses
- 6-8 HoB (18-28 total VP)
- Health: 8-10 bouts
- Win rate: 25-35%
- Stage rule: Major impact (can cause loss condition)

## Stage Rule Examples

- **Economic**: "All equipment costs +2G"
- **Combat**: "Armor only protects for 1 bout"
- **Strategic**: "Players cannot cooperate on monsters"
- **VP**: "HoB worth double VP"

## Commands

```bash
# Create boss
@card-designer Create rank 1 boss

# Test boss difficulty
/simulate heroes=all_level3 vs boss=[name] iterations=100

# Analyze boss balance
/power-level [boss-name]
```

## See Also

- `_examples/example_boss.yaml`
- Rulebook section on bosses (page X)
