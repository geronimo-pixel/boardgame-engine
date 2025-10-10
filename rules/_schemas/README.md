# 🔍 Schemas - Validation Rules

This folder contains JSON schemas that define what makes a valid card.

## What Are Schemas?

Think of schemas as **blueprints** for cards:
- ✅ "A weapon MUST have a name, rank, cost, and attributes"
- ✅ "Rank must be 1, 2, or 3 (not 0 or 4)"
- ✅ "Cost must be a positive number (not negative or text)"

When you run `/validate`, your cards are checked against these schemas.

## Files In This Folder

- `hero_schema.json` → Hero card rules
- `weapon_schema.json` → Weapon validation
- `armor_schema.json` → Armor validation
- `charm_schema.json` → Charm validation
- `monster_schema.json` → Monster validation
- `boss_schema.json` → Boss validation
- `spell_schema.json` → Spell validation

## How Validation Works

```
1. You edit a YAML card file
2. You run /validate
3. System loads the appropriate schema
4. System checks your card against schema rules
5. Reports any errors or warnings
```

## Example Validation

### Your YAML card:
```yaml
name: Iron Sword
cost: "five"  # ❌ Should be a number!
rank: 1
```

### Validation error:
```
❌ Error at line 2: Expected number, got string for 'cost'

Found: cost: "five"
Expected: cost: 5

Tip: Remove quotes around numbers.
```

## Understanding Schema Files

Schemas are written in JSON (not YAML). You probably won't need to edit them, but here's how to read one:

```json
{
  "type": "object",
  "required": ["name", "rank", "cost"],  // These fields are mandatory
  "properties": {
    "name": { "type": "string" },        // name must be text
    "rank": { "type": "integer", "minimum": 1, "maximum": 3 },  // 1-3 only
    "cost": { "type": "number", "minimum": 0 }  // Positive numbers only
  }
}
```

## When To Edit Schemas

**Rarely!** Only if you're:
- Adding a new card type
- Adding a new field to all cards
- Changing fundamental rules

**Most design work happens in YAML files, not schemas.**

## Important Notes

⚠️ **DO NOT DELETE THIS FOLDER**
Without schemas, validation can't work.

⚠️ **ASK BEFORE EDITING**
Schema changes affect ALL cards. Discuss with Giovanni first.

✅ **USE VALIDATION OFTEN**
`/validate` after every card edit—catch errors early!

## Common Validation Errors

### 1. Missing Required Field
```
❌ Error: Missing required field 'cost'
Fix: Add cost: 5 to your card
```

### 2. Wrong Data Type
```
❌ Error: Expected number, got string for 'rank'
Fix: Change rank: "1" to rank: 1 (remove quotes)
```

### 3. Invalid Value
```
❌ Error: 'rank' must be 1, 2, or 3
Fix: rank: 4 is not valid (game only has 3 stages)
```

### 4. Indentation Error
```
❌ Error: Invalid YAML structure at line 8
Fix: Check your spacing (use 2 spaces consistently)
```

## Commands

```bash
# Validate all rules
/validate

# Validate specific file
/validate weapons_rank1.yaml

# Validate and get detailed report
/validate --verbose
```

## See Also

- `../docs/03_understanding_yaml.md` → YAML syntax
- `_examples/` → Valid card examples
- `../GLOSSARY.md` → Define "validation", "schema"
