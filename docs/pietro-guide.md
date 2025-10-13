# Pietro's Complete Guide to Game Design

Welcome, Pietro! This guide will help you create and test your board game using simple tools. **No programming required!**

---

## What You'll Learn

By the end of this guide, you'll be able to:
- ✅ Create monster, hero, and equipment cards
- ✅ Test combat balance using the simulator
- ✅ Understand why heroes win or lose
- ✅ Make changes and see results immediately
- ✅ Save your work with Git

**Time needed:** 1-2 hours to get started

---

## Quick Start (5 Minutes)

### Step 1: Open Terminal

1. Open VSCode
2. Open Terminal (View → Terminal, or press `` Ctrl+` ``)
3. Make sure you're in the right folder:
   ```bash
   cd ~/Documents/Projects/boardgame-engine-pietro
   ```

### Step 2: Run Your First Combat

Type this command:
```bash
python3 play_combat.py
```

You'll see a menu. Try this:
1. Choose "1" for Warrior
2. Choose "1" for the first monster
3. Choose "n" for no seed
4. Watch the combat play out!

**Congratulations!** You just ran your first simulation. 🎉

---

## Understanding the Combat Simulator

### What You See

When you run a combat, you'll see it broken into **phases**:

```
🎲 DICE ROLL PHASE
  Shows what symbols the hero rolled (■ ▲ ●)

⚔️ EQUIPMENT ACTIVATION PHASE
  Shows how the sword and shield activate

💀 MONSTER ROLL PHASE
  Shows how many skulls the monster rolled

⚡ COMBAT RESOLUTION PHASE
  Shows who wins and why
```

### Reading the Results

**Example:**
```
Hero Die:    ■ ■  (2 squares)
Class Die 1: ▲    (1 triangle)
Class Die 2: ●    (1 circle)
```

This means:
- The hero rolled 2 squares
- Plus 1 triangle from class dice
- Plus 1 circle from class dice

**Then equipment activates:**
```
Sword (combo (1■+1●)):
  → Attack: +3
  → Uses: 1■, 1●
```

This means:
- The sword needs 1 square + 1 circle to activate
- When it does, it gives +3 attack
- Those symbols are "consumed" (used up)

---

## Creating Your First Monster

### Step 1: Look at an Example

Open this file in VSCode:
```
rules/_examples/example_monster.yaml
```

You'll see something like this:
```yaml
name: "Example Beast"
rank: 1
health: 2
armor: 1
attack: 2
```

### Step 2: Copy the Template

In terminal:
```bash
cp rules/_examples/example_monster.yaml rules/monsters/bear.yaml
```

This creates a new file called `bear.yaml`.

### Step 3: Edit Your Monster

Open `rules/monsters/bear.yaml` in VSCode and change the values:

```yaml
name: "Bear"
rank: 1
health: 4      # Bears are tough!
armor: 3       # Thick fur
attack: 3      # Strong claws
```

**What each field means:**
- `name`: What to call it
- `rank`: Difficulty (1=easy, 2=medium, 3=hard)
- `health`: How many hits before it dies
- `armor`: How much damage it blocks
- `attack`: Base damage it deals

### Step 4: Test Your Monster

```bash
python3 play_combat.py
```

1. Choose Warrior
2. Look for "Bear" in the monster list
3. Watch the combat!

### Step 5: Balance Your Monster

Ask yourself:
- Did the hero win too easily? → Increase health or armor
- Was the monster too weak? → Increase attack
- Did combat take too long? → Adjust health

**Then test again!** Keep tweaking until it feels right.

---

## Understanding Dice & Symbols

### Hero Symbols

- **■ (Square)**: Primary attack symbol
  - Needed for sword and shield activation
  - Most common on Warrior dice

- **▲ (Triangle)**: Special ability symbol
  - Primary for Hunter (bow)
  - Used in combos with other symbols

- **● (Circle)**: Combo symbol
  - Used with squares for advanced abilities
  - Unlocks "overcharge" effects

### Monster Symbols

- **💀 (Skull)**: Monster power symbol
  - More skulls = more damage
  - Each monster has different skull bonuses

**Example:** A Rat's skull bonuses:
```
0 skulls → 1 attack
1 skull  → 3 attack
2 skulls → 3 attack
3+ skulls → 4 attack (overcharge!)
```

---

## Advanced: Skull Mapping

When creating a monster, you can control how skulls affect its power.

### In the YAML file:
```yaml
skull_mapping:
  0: 1    # No skulls = 1 attack
  1: 3    # 1 skull = 3 attack (big jump!)
  2: 4    # 2 skulls = 4 attack
```

### What this means in game:
- If the monster rolls **0 skulls**, it attacks with just **1** power
- If it rolls **1 skull**, it gets **3** attack (much scarier!)
- If it rolls **2 skulls**, it gets **4** attack

**Design tip:** Make the jump from 0→1 skull significant to make skull rolls exciting!

---

## Equipment System Explained

### Warrior's Sword

The sword has different activation modes:

1. **Flat** (always works): +1 attack
2. **Base** (needs 1■): +2 attack
3. **Combo** (needs 1■ + 1●): +3 attack
4. **Overcharge** (needs 2■ + 1●): +4 attack

**The game automatically chooses the best option based on what you rolled!**

### Warrior's Shield

1. **Flat** (always works): +1 armor
2. **Base** (needs 1■): +1 attack, +1 armor
3. **Combo** (needs 1■ + 1●): +2 attack, +3 armor

**Both sword AND shield can activate at the same time!**

---

## Reading Combat Results

### Example Combat Output

```
Warrior attack: 5
Monster attack: 3

✓ Warrior wins bout
```

**What happened:**
- Warrior got 5 total attack (base + equipment)
- Monster got 3 attack (base + skull bonuses)
- Warrior's attack was higher, so Warrior wins
- Monster takes damage equal to the difference

### Ties

```
Warrior attack: 5
Monster attack: 5

TIE! → Warrior wins (Class Ability #2)
```

**When attacks are equal:**
- It's a tie
- Warrior's special ability breaks the tie
- Warrior wins the bout

---

## Testing with Seeds

### What is a seed?

A seed is a number that makes the dice rolls **exactly the same** every time.

### Why use seeds?

- **Testing:** "Did my change make the monster better?"
- **Sharing:** "Giovanni, look at seed 42 with Warrior vs Bear"
- **Debugging:** "This monster acts weird with seed 123"

### How to use:

```bash
python3 play_combat.py
# When asked "Use a seed?"
y
# Enter any number (e.g., 42)
42
```

**Now every time you use seed 42, you'll see the exact same combat!**

---

## Common Tasks

### Task 1: Make a Monster Easier

Open the monster's YAML file and:
- **Reduce health** (fewer hits needed to kill it)
- **Reduce armor** (takes more damage per hit)
- **Lower skull bonuses** (less dangerous when it rolls skulls)

### Task 2: Make a Monster Harder

- **Increase health** (takes more hits to kill)
- **Increase armor** (blocks more damage)
- **Higher skull bonuses** (more dangerous rolls)
- **More dice** (change "2m" to "3m" for more skulls)

### Task 3: Create a Monster Variant

```bash
# Copy existing monster
cp rules/monsters/wolf.yaml rules/monsters/dire_wolf.yaml

# Edit dire_wolf.yaml
# Make it bigger and scarier!
```

### Task 4: Test Multiple Combats

Want to see which monster is hardest?

```bash
python3 play_combat.py
# Test Warrior vs Wolf (seed 42)
# Write down: took 5 bouts

# Run again
python3 play_combat.py
# Test Warrior vs Bear (seed 42)
# Write down: took 12 bouts

# Bear is harder! (took more bouts to win)
```

---

## Using Git (Simple Version)

Git helps you save your work and share it with Giovanni.

### Save Your Changes

```bash
# See what you changed
git status

# Save all changes
git add .
git commit -m "Added Bear monster"

# Send to Giovanni
git push
```

### Get Giovanni's Updates

```bash
# Download latest changes
git pull
```

### If Something Goes Wrong

**Don't panic!** Just ask Giovanni. He can fix any Git issues.

---

## YAML Basics (Quick Reference)

YAML is just a form you fill out. Follow these rules:

### Good YAML ✓
```yaml
name: Bear
health: 4
armor: 3
```

### Bad YAML ✗
```yaml
name Bear        ❌ Missing colon (:)
  health: 4      ❌ Wrong indentation (no leading spaces!)
armor: "three"   ❌ Should be number, not text
```

### YAML Rules:
1. **Use colons:** `field: value`
2. **No indentation** for main fields
3. **Numbers are numbers:** Use `4`, not `"4"` or `"four"`
4. **Text in quotes:** Use `"Bear"` for names
5. **Lists use dashes:**
   ```yaml
   abilities:
     - "Roar"
     - "Swipe"
   ```

---

## Troubleshooting

### "Monster not found"

**Problem:** You created a monster but can't select it.

**Solution:**
1. Check the file is in `/rules/monsters/`
2. Check the name in the YAML matches what you're looking for
3. Try restarting the simulator

### "YAML syntax error"

**Problem:** The simulator says your YAML file has an error.

**Solution:**
1. Check for missing colons (`:`)
2. Check for wrong indentation (no spaces before main fields)
3. Check for quotes around text
4. Ask Codex: "What's wrong with this YAML?"

### "Combat never ends"

**Problem:** Combat reaches 100 bouts and no one wins.

**Solution:**
- Your monster is too strong!
- Reduce armor or health
- Check skull bonuses aren't too high

### Something Else Broke?

**Ask Giovanni!** Send him:
1. What you were trying to do
2. What happened instead
3. The monster file you were editing

---

## Best Practices

### Start Simple
- Create one monster at a time
- Test it before making more
- Use example files as templates

### Test Thoroughly
- Test vs Warrior
- Test vs Hunter
- Try with different seeds
- Watch full combats (don't skip)

### Take Notes
- Keep a notebook of balance changes
- Write down which monsters feel too strong/weak
- Note interesting dice roll moments

### Ask Questions
- Ask Codex about game mechanics
- Ask Giovanni about technical issues
- No question is too simple!

---

## Next Steps

### Once You're Comfortable:

1. **Create 5-10 Rank 1 monsters**
   - Vary health (1-4)
   - Vary armor (0-3)
   - Different skull mappings

2. **Test them all vs Warrior**
   - Which ones feel balanced?
   - Which are too easy/hard?

3. **Try Hunter**
   - Different hero, different strategy
   - Monsters that work for Warrior might be different for Hunter

4. **Think about Rank 2 monsters**
   - Stronger versions
   - More interesting mechanics

---

## Quick Command Reference

```bash
# Run combat simulator
python3 play_combat.py

# Validate monsters
python3 verify_monsters.py

# Check YAML syntax
python3 -m yaml rules/monsters/bear.yaml

# Git basics
git status          # See what changed
git add .           # Stage all changes
git commit -m "..."  # Save with message
git push            # Send to Giovanni
git pull            # Get updates
```

---

## Remember

- **You're the game designer** - Giovanni handles the technical stuff
- **Experiment!** - It's easy to undo changes
- **Test frequently** - Run the simulator after every change
- **Have fun!** - This is creative work, enjoy the process

---

## Getting Help

- **Game design questions:** Ask Codex in VSCode
- **Technical issues:** Ask Giovanni
- **"Is this right?"** Use the simulator to test!
- **Git problems:** Always ask Giovanni

---

**Happy game designing! 🎲🎮**

Start with `python3 play_combat.py` and have fun testing your creations!
