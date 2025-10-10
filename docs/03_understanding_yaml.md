# 📝 Guide 3: Understanding YAML

**Time to read**: 15 minutes
**Prerequisites**: [Guide 2: How to Use Claude Code](02_how_to_use_claude_code.md)

---

## What Is YAML?

YAML (pronounced "YAM-ul") is a way to write structured data that's easy for both humans and computers to read.

**Fun fact**: YAML stands for "YAML Ain't Markup Language" (a recursive acronym, like GNU!)

---

## Why Use YAML for Game Cards?

### Before: Prose Description

> "The Iron Sword is a rank 1 one-handed weapon that costs 5 gold. It requires 1 cube attribute to activate, dealing +3 damage. When overcharged with 2 cubes, it deals +5 damage instead."

**Problems**:
- ❌ Computer can't parse this easily
- ❌ Prone to ambiguity ("deals +5 damage" — does it replace +3 or add to it?)
- ❌ Hard to validate (did I forget to specify the rank?)

### After: YAML

```yaml
name: Iron Sword
rank: 1
category: weapon
hands: 1
cost: 5
cost_type: gold

attributes:
  base:
    cubes: 1
    effect: "+3"
  overcharge:
    cubes: 2
    effect: "+5"
```

**Benefits**:
- ✅ Computer can validate all fields are present
- ✅ Clear structure (no ambiguity)
- ✅ Easy to modify ("Let me change cost from 5 to 6...")

---

## YAML Basics

### Key-Value Pairs

The fundamental building block:

```yaml
name: Iron Sword
cost: 5
```

**Format**: `key: value`
**Rules**:
- Space after the colon is required
- Keys are unique within a level

### Types of Values

**Strings** (text):
```yaml
name: "Iron Sword"    # Quotes optional for simple strings
description: "A sturdy weapon"
```

**Numbers**:
```yaml
cost: 5       # Integer
damage: 3.5   # Decimal (float)
```

**Booleans** (true/false):
```yaml
is_magical: true
is_cursed: false
```

**Null** (empty):
```yaml
special_effect: null   # No effect
```

### Lists (Arrays)

Multiple items:

```yaml
# Inline style
dice: [cube, cube, circle, triangle, skull]

# Block style (preferred for readability)
dice:
  - cube
  - cube
  - circle
  - triangle
  - skull
```

**Important**: Items start with `-` followed by a space

### Nested Objects (Dictionaries)

Grouping related data:

```yaml
attributes:
  base:
    cubes: 1
    effect: "+3"
  overcharge:
    cubes: 2
    effect: "+5"
```

**Key rule**: Indentation shows hierarchy (more on this below!)

---

## The Golden Rule: Indentation

### Why It Matters

In YAML, **indentation defines structure**. This is similar to how paragraphs work in an outline.

### Correct Indentation

```yaml
equipment:
  weapons:
    - Iron Sword
    - Flame Blade
  armors:
    - Leather Armor
```

**Structure**:
- `equipment` has two children: `weapons` and `armors`
- Each child is indented 2 spaces
- List items (`-`) align with their parent

### Incorrect Indentation

```yaml
equipment:
 weapons:       # ❌ Only 1 space (inconsistent)
    - Iron Sword  # ❌ 4 spaces (inconsistent)
  armors:       # ✅ 2 spaces (correct)
    - Leather Armor
```

**Error message**:
```
YAMLError: Inconsistent indentation at line 2
```

### The Rules

1. **Use spaces, not tabs** (tabs will break YAML)
2. **Use 2 spaces per indentation level** (consistent throughout this project)
3. **Be consistent** (always same number of spaces)

---

## Comments

Add notes for yourself or others:

```yaml
name: Flame Blade
cost: 8          # Increased from 6 to balance power
damage: 5
# TODO: Add burn effect implementation
```

**Format**: Anything after `#` is a comment (ignored by computer)

---

## Real Example: Weapon Card

Let's build a weapon card step by step.

### Step 1: Basic Info

```yaml
name: Flame Blade
rank: 1
category: weapon
```

### Step 2: Add Cost

```yaml
name: Flame Blade
rank: 1
category: weapon
cost: 8
cost_type: gold
```

### Step 3: Add Equipment Slots

```yaml
name: Flame Blade
rank: 1
category: weapon
cost: 8
cost_type: gold
hands: 1          # Uses 1 weapon slot (not 2-handed)
```

### Step 4: Add Combat Attributes

```yaml
name: Flame Blade
rank: 1
category: weapon
cost: 8
cost_type: gold
hands: 1

attributes:
  base:
    circles: 1
    effect: "+3"
```

### Step 5: Add Overcharge

```yaml
name: Flame Blade
rank: 1
category: weapon
cost: 8
cost_type: gold
hands: 1

attributes:
  base:
    circles: 1        # Need 1 circle to activate
    effect: "+3"      # Base damage
  overcharge:
    circles: 2        # Need 2 circles for overcharge
    effect: "+5, burn" # Better damage + status effect
```

### Step 6: Add Metadata

```yaml
name: Flame Blade
rank: 1
category: weapon
cost: 8
cost_type: gold
hands: 1

attributes:
  base:
    circles: 1
    effect: "+3"
  overcharge:
    circles: 2
    effect: "+5, burn"

# Design notes (not used by game engine, just for reference)
flavor_text: "Channels the fury of elemental fire."
design_notes: "Intentionally high-risk, high-reward with circle dependency"
balance_concerns: "Monitor win rate—burn might be too strong"
```

**Complete!** This card is ready to validate and test.

---

## Common Mistakes

### Mistake 1: Mixing Tabs and Spaces

```yaml
name: Iron Sword
	cost: 5      # ❌ Tab used instead of spaces
```

**Fix**: Use only spaces (configure your editor to convert tabs to spaces)

### Mistake 2: Missing Space After Colon

```yaml
name:Iron Sword   # ❌ No space after :
```

**Fix**:
```yaml
name: Iron Sword  # ✅ Space after :
```

### Mistake 3: Inconsistent Indentation

```yaml
attributes:
  base:
    cubes: 1
   effect: "+3"   # ❌ 3 spaces instead of 4
```

**Fix**:
```yaml
attributes:
  base:
    cubes: 1
    effect: "+3"  # ✅ 4 spaces (2 levels deep)
```

### Mistake 4: Forgetting Dash for List Items

```yaml
dice:
  cube           # ❌ Missing dash
  circle
```

**Fix**:
```yaml
dice:
  - cube         # ✅ Dash for list items
  - circle
```

### Mistake 5: Quotes Around Numbers

```yaml
cost: "5"        # ❌ String, not number
```

**Fix**:
```yaml
cost: 5          # ✅ Number (no quotes)
```

---

## Validation to the Rescue

### What Is Validation?

Validation checks your YAML against a **schema** (set of rules):
- ✅ Are required fields present?
- ✅ Are values the right type? (numbers vs. strings)
- ✅ Is the structure correct?

### Running Validation

```bash
/validate rules/equipment/weapons_rank1.yaml
```

**Example output**:

```
✅ Validating: weapons_rank1.yaml

Checking schema compliance...
  ✅ All required fields present
  ✅ Data types correct
  ✅ Structure valid

Balance checks...
  ⚠️ Flame Blade: DPG 0.63 is 12% above average

Overall: ✅ VALID (1 warning)
```

### Common Validation Errors

#### Error: Missing Required Field

```
❌ Error at line 8: Missing required field 'cost'

Every equipment card must specify a cost in gold or tokens.

Example:
  cost: 5
  cost_type: gold
```

#### Error: Wrong Data Type

```
❌ Error at line 10: Expected number, got string for 'cost'

Found: cost: "five"
Expected: cost: 5

Tip: Remove quotes around numbers.
```

#### Error: Invalid Value

```
❌ Error at line 12: Invalid value for 'rank'

Found: rank: 4
Expected: rank must be 1, 2, or 3 (matching game stages)
```

---

## Advanced YAML Features

### Anchors & Aliases (Reusing Data)

Avoid repeating yourself:

```yaml
# Define anchor with &
base_sword: &sword_template
  category: weapon
  hands: 1
  cost_type: gold

# Reuse with *
iron_sword:
  <<: *sword_template    # Inherits category, hands, cost_type
  name: Iron Sword
  cost: 5

flame_blade:
  <<: *sword_template
  name: Flame Blade
  cost: 8
```

**You probably won't need this**, but it's useful for reducing duplication.

### Multi-Line Strings

For long text:

```yaml
# Preserves line breaks
description: |
  This legendary sword was forged in dragon fire.
  It glows with an eerie red light.
  Wielders report hearing whispers in ancient tongues.

# Folds into single line
summary: >
  This legendary sword was forged in dragon fire.
  It glows with an eerie red light.
  Wielders report hearing whispers in ancient tongues.
```

---

## Practical Exercise

### Your Turn: Create a Monster

Try writing YAML for a monster with these properties:
- Name: Shadow Wolf
- Rank: 2
- Health: 4 bouts
- Armor: 3
- Attack: +6
- Overkill: 3
- Dice: 2 minion dice, 1 chief dice
- Ability: "Dark Pounce" (1 skull = +3, overcharge 2 skulls = +6 + player loses 1 HP even if they win)
- Loot: 8 gold

**Solution** (don't peek until you try!):

<details>
<summary>Click to reveal solution</summary>

```yaml
name: Shadow Wolf
rank: 2
health: 4
armor: 3
attack: 6
overkill: 3

dice:
  - minion
  - minion
  - chief

abilities:
  - name: Dark Pounce
    attribute: skull
    skulls_needed: 1
    effect: "+3"
    overcharge:
      skulls_needed: 2
      effect: "+6, player loses 1 HP even on win"

loot:
  gold: 8
  tokens: 0
```

</details>

---

## Tips for Working with YAML

### 1. Use a Good Editor

**VS Code** (recommended):
- Install "YAML" extension
- Auto-indentation
- Syntax highlighting
- Error detection

### 2. Validate Often

After any change:
```
/validate
```

Don't wait until you've edited 10 files—catch errors early.

### 3. Check Examples

When unsure, look at:
```
rules/_examples/example_weapon.yaml
```

Fully annotated reference cards show correct format.

### 4. Use Comments Liberally

```yaml
cost: 8    # Increased from 6 after simulation showed 68% win rate
```

Future you (and Giovanni) will thank you.

### 5. Ask for Help

```
@teach YAML indentation
```

Claude Code can explain any YAML concept with examples from your project.

---

## What You've Learned

✅ What YAML is and why we use it
✅ Basic syntax (key-value pairs, lists, nested objects)
✅ The golden rule: indentation matters!
✅ How to write a complete card in YAML
✅ Common mistakes and how to avoid them
✅ How validation catches errors

---

## Next Steps

**Practice Exercise**:
1. Open `rules/_examples/example_weapon.yaml`
2. Read through it and understand each field
3. Try modifying one value (e.g., change cost)
4. Run `/validate` to check your change
5. Ask Claude Code to explain any field you don't understand

**Ready to create your first card?**
📘 [Guide 4: Adding Your First Card →](04_adding_your_first_card.md)
