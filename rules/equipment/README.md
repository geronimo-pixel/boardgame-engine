# ⚔️ Equipment

Weapons, armors, and charms organized by rank.

## File Structure

```
weapons_rank1.yaml    # Stage 1 weapons (4-10G)
weapons_rank2.yaml    # Stage 2 weapons (10-20G)
weapons_rank3.yaml    # Stage 3 weapons (20-35G)
armors_rank1.yaml     # Stage 1 armors
armors_rank2.yaml     # Stage 2 armors
armors_rank3.yaml     # Stage 3 armors
charms_rank1.yaml     # Stage 1 charms
...
```

## Equipment Rules

**Weapons**: Max 2 (or 1 if 2-handed)
**Armors**: Max 2 (must be different types: light/heavy/magical)
**Charms**: Max 2 (must be different types)

## Balance Guidelines

### Weapons
- **Rank 1**: 3-4 base damage, 5-10G cost, DPG ~0.60
- **Rank 2**: 5-7 base damage, 10-20G cost, DPG ~0.55
- **Rank 3**: 8-12 base damage, 20-35G cost, DPG ~0.50

### Armors
- **Rank 1**: +1-2 armor, 4-8G
- **Rank 2**: +2-3 armor, 8-15G
- **Rank 3**: +3-5 armor, 15-25G

### Charms
- Utility effects (not direct damage/armor)
- Situational power spikes
- Lower cost than weapons

## Creating Equipment

```bash
# Quick creation
@card-designer Create rank 2 weapon

# Balance check
/balance weapons rank=2

# Test specific card
/simulate weapon=[name] vs monsters=rank2
```

## See Also

- `_examples/example_weapon.yaml`
- `_examples/example_armor.yaml`
- `docs/06_reading_balance_reports.md`
