# 📚 Example Cards - Learning Templates

**START HERE** when learning how to create cards!

## What's In This Folder

Fully annotated example cards for every type:

- **`example_hero.yaml`** → Complete hero structure
- **`example_weapon.yaml`** → Weapon with extensive comments
- **`example_armor.yaml`** → Armor mechanics explained
- **`example_monster.yaml`** → Monster card breakdown
- **`example_boss.yaml`** → Boss mechanics + stage rules
- **`example_spell.yaml`** → Spell structure + phases

## How to Use These Files

### 1. Read First
Open the relevant example file and read through ALL the comments.
Every field is explained—why it exists, what values are valid, how it affects gameplay.

### 2. Copy As Template
When creating your own cards:
```bash
# Copy the example
cp _examples/example_weapon.yaml equipment/my_new_weapon.yaml

# Modify the values
# (Keep the structure, change the content)

# Validate
/validate my_new_weapon.yaml
```

### 3. Reference While Creating
Keep example files open while using `@card-designer`:
- Check field names
- Verify structure
- Understand options

## Quick Reference

**Creating a weapon?** → Read `example_weapon.yaml`
**Creating a monster?** → Read `example_monster.yaml`
**Creating a spell?** → Read `example_spell.yaml`
**Confused about attributes?** → Check weapon example (best explained there)
**Confused about phase restrictions?** → Check spell example

## Important Notes

⚠️ **DO NOT DELETE THIS FOLDER**
These are reference files, not actual game cards.

⚠️ **DO NOT EDIT THESE FILES**
If you want to experiment, copy them to another location.

✅ **DO REFERENCE THEM OFTEN**
That's what they're here for!

## Learning Path

1. Read `example_weapon.yaml` (simplest structure)
2. Read `example_monster.yaml` (similar to weapons)
3. Read `example_hero.yaml` (more complex)
4. Read `example_spell.yaml` (different mechanics)
5. Read `example_armor.yaml` (passive effects)
6. Read `example_boss.yaml` (most complex)

## See Also

- `../docs/03_understanding_yaml.md` → Learn YAML syntax
- `../docs/04_adding_your_first_card.md` → Step-by-step creation guide
- `_schemas/README.md` → Understanding validation
