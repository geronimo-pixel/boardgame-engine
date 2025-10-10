# 📖 Guide 1: What Is This Repository?

**Time to read**: 5 minutes
**Prerequisites**: None—start here!

---

## The Big Picture

You've designed a board game with heroes, monsters, equipment, and complex combat rules. Right now, it exists in your head and on paper. This repository transforms your game into something you can:

✅ **Test automatically** → Run simulations to see if cards are balanced
✅ **Validate instantly** → Check if rules make sense before playtesting
✅ **Visualize easily** → Generate charts showing power curves, win rates
✅ **Iterate quickly** → Change a card's stats and immediately see the impact

---

## How It Works (Simple Version)

### 1. Your Game as Data

Instead of writing rules in paragraphs, we express them as **structured data**:

**Before** (Rulebook):
> "The Iron Sword is a rank 1 weapon that costs 5 gold. It requires 1 cube attribute to activate, dealing +3 damage. If you roll 2 cubes, it overcharges for +5 damage instead."

**After** (YAML):
```yaml
name: Iron Sword
rank: 1
cost: 5
attributes:
  base:
    cubes: 1
    effect: "+3"
  overcharge:
    cubes: 2
    effect: "+5"
```

### Why This Is Better

The computer can now:
- ✅ Read and understand your card
- ✅ Check if it's valid (no missing fields)
- ✅ Simulate combat using it
- ✅ Compare it to other cards for balance

---

## The Repository Structure

Think of this repo as a **game design laboratory** with different rooms:

### 🎯 `rules/` — Your Workshop
**What's here**: YAML files for heroes, equipment, monsters, bosses, spells
**Who uses it**: You! This is where you create and edit cards
**Example**: `rules/equipment/weapons_rank1.yaml`

### 🔧 `engine/` — The Game Brain
**What's here**: Python code that simulates your game
**Who uses it**: Mostly runs in the background. Giovanni maintains this
**Example**: `engine/combat.py` (resolves fights)

### 🧪 `simulations/` — The Testing Lab
**What's here**: Predefined scenarios to test game mechanics
**Who uses it**: You, when you want to test changes
**Example**: `simulations/scenarios/01_basic_combat.yaml`

### 📊 `analysis/` — The Balance Toolkit
**What's here**: Scripts that find overpowered/underpowered cards
**Who uses it**: You, to check if cards need adjusting
**Example**: `analysis/reports/equipment_balance.md`

### 📈 `visualizations/` — The Report Generator
**What's here**: Charts and graphs about your game
**Who uses it**: You, to see patterns and trends
**Example**: `visualizations/outputs/damage_curves.png`

### 📚 `docs/` — The Learning Center
**What's here**: These guides you're reading now!
**Who uses it**: You, whenever you need to learn something

---

## The Workflow Loop

Here's how you'll use this repo day-to-day:

```
1. 💡 Idea: "I want to add a new weapon called Flame Blade"
       ↓
2. 🤖 Create: Talk to @card-designer agent
       ↓
3. ✅ Validate: System checks if the YAML is valid
       ↓
4. 🧪 Test: Run simulations to see it in action
       ↓
5. 📊 Analyze: Check if it's balanced
       ↓
6. 🔄 Iterate: Adjust stats based on results
       ↓
   (Repeat steps 4-6 until satisfied)
       ↓
7. ✓ Commit: Save changes to git history
```

---

## What Makes This Special

### Traditional Game Design Process
1. Design card on paper
2. Play multiple manual games to test
3. Discover it's overpowered
4. Redesign card
5. Play more games to test again
6. (Repeat endlessly)

**Problem**: Each cycle takes hours or days

### With This Repository
1. Design card with `@card-designer`
2. Run 1000 simulated games in 10 seconds
3. See it wins 75% of the time (overpowered!)
4. Adjust stats
5. Re-run simulations instantly
6. (Repeat in minutes, not days)

**Advantage**: Rapid iteration with data-driven decisions

---

## Key Concepts (Don't Worry, You'll Learn These)

### Data-Driven Design
Instead of guessing if a card is balanced, you have **numbers**:
- "Iron Sword has 0.60 damage-per-gold, average is 0.56"
- "Goblin Berserker wins 45% of fights against level 2 heroes"

### Simulation
Running virtual games to test mechanics without manual play.

### Validation
Automatic checking to catch errors before they cause problems.

### Version Control (Git)
A time machine for your work—undo mistakes, try experiments safely.

---

## Common Questions

### "Do I need to learn programming?"

**No!** You'll use natural language to talk to AI agents:
- ❌ "Create a Python function to parse YAML..." ← You never say this
- ✅ "Add a new weapon called Flame Blade" ← You say this

### "What if I break something?"

The system has safety nets:
- Validation catches errors before they're saved
- Git lets you undo any change
- Giovanni can fix anything serious

### "Can I still playtest manually?"

**Absolutely!** Simulations don't replace playtesting—they **supplement** it:
- Simulation → Find obvious balance issues quickly
- Playtesting → Find fun/unfun interactions

---

## What You'll Learn Next

📘 **Guide 2**: How to use Claude Code (your AI assistant)
📘 **Guide 3**: Understanding YAML (the data format)
📘 **Guide 4**: Adding your first card (step-by-step)
📘 **Guide 5**: Running simulations (test your game)
📘 **Guide 6**: Reading balance reports (analyze data)

---

## Ready to Continue?

✅ You understand: This repo is a game design laboratory
✅ You know: `rules/` is where you create cards
✅ You learned: Simulations test balance automatically

**Next**: [Guide 2: How to Use Claude Code →](02_how_to_use_claude_code.md)

Or jump back to the [Getting Started guide](../GETTING_STARTED.md) to take the interactive tour.
