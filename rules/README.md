# 🎯 Rules Folder - Your Game Data

This folder contains all your game's content as structured YAML files.

## What's Here?

**`heroes/`** → The 7 playable characters
**`equipment/`** → Weapons, armors, and charms (by rank)
**`monsters/`** → Enemies to fight (by rank)
**`bosses/`** → Stage-ending bosses (4 per rank)
**`spells/`** → One-time use spell cards (no rank)
**`_examples/`** → Fully annotated reference cards
**`_schemas/`** → Validation rules (ensures cards are correct)

## How to Use This Folder

### Reading Cards

Look at **`_examples/`** first to understand card structure:
- `example_hero.yaml` → Hero card format
- `example_weapon.yaml` → Equipment format
- `example_monster.yaml` → Monster format
- `example_spell.yaml` → Spell format

### Creating Cards

**Option 1: Use the agent (recommended)**
```
@card-designer I want to create a new rank 1 weapon
```

**Option 2: Copy and modify**
```
1. Copy example_weapon.yaml
2. Modify the values
3. Run /validate to check
```

### Validation

Always validate after editing:
```
/validate                    # Check all files
/validate weapons_rank1.yaml # Check specific file
```

## File Organization

### Equipment Folder
```
equipment/
├── weapons_rank1.yaml    # All rank 1 weapons
├── weapons_rank2.yaml    # All rank 2 weapons
├── weapons_rank3.yaml    # All rank 3 weapons
├── armors_rank1.yaml
└── ...
```

### Why group by rank?
- Easy to balance within a rank
- Clear stage progression
- Simpler file management

## Important Rules

1. **Never delete _examples/ or _schemas/**
   - These are reference/validation files

2. **Always use 2-space indentation**
   - YAML is sensitive to indentation

3. **Validate before committing**
   - Catch errors early

4. **Add design notes**
   - Future you will thank you!

## Quick Commands

```bash
# Create new card
@card-designer

# Validate all rules
/validate

# Check balance
/balance weapons rank=1

# Test a card
/simulate hero=Warrior weapon=[your-card] vs monster=Goblin
```

## Need Help?

- **See example cards**: `_examples/` folder
- **Learn YAML syntax**: `../docs/03_understanding_yaml.md`
- **Creating cards guide**: `../docs/04_adding_your_first_card.md`
- **Ask for help**: `@rules-oracle [your question]`
