# 🎮 Getting Started: Your First Session

Welcome, Pietro! This repository is where your board game comes to life through code. Don't worry if you've never programmed before—this entire system is designed to teach you as you go.

---

## What You'll Learn Today

By the end of this session, you'll understand:
- ✅ How your game is represented as **data** (YAML files)
- ✅ How to talk to Claude Code using **natural language**
- ✅ How to **validate** your game rules automatically
- ✅ How to **simulate** combat to test balance

**Time needed**: 30-45 minutes

---

## Before You Start

### What is This Repository?

Think of this repository (or "repo") as a **living rulebook** that can:
- ✅ Check if your rules make sense
- ✅ Run simulations to test game balance
- ✅ Generate visual reports of your game
- ✅ Help you design new cards with AI assistance

### What is Claude Code?

Claude Code is an AI assistant that lives in your command line (terminal). You can talk to it in plain English, and it will:
- ✅ Answer questions about your game
- ✅ Create new cards based on your descriptions
- ✅ Run tests and simulations
- ✅ Explain programming concepts when you need them

---

## Your First 5 Minutes

### Step 1: Open the Repository

```bash
cd ~/Documents/Projects/boardgame-engine
```

**What this does**: Changes your location to the game repository folder.

### Step 2: Start Claude Code

```bash
claude
```

**What this does**: Launches Claude Code in interactive mode. You'll see a prompt where you can type commands.

### Step 3: Take a Tour

Type this command:

```
/tour
```

**What this does**: The `@tour-guide` agent will walk you through the entire repository, explaining each folder and showing you example files. Just sit back and read!

---

## Understanding Your Game as Code

### The Big Idea

Your game has different **entities**:
- **Heroes** → Characters players control
- **Equipment** → Weapons, armors, charms
- **Monsters** → Enemies to fight
- **Bosses** → Stage-ending challenges
- **Spells** → Special one-time effects

In this repo, each entity is described in a **YAML file** (pronounced "YAM-ul"). YAML is just a way to write structured information that both humans and computers can read.

### Example: A Weapon Card

Here's what a weapon looks like in YAML:

```yaml
# Human-readable fields
name: "Iron Sword"
rank: 1
cost: 5
cost_type: gold

# How it works in combat
attributes:
  base:
    cubes: 1              # Need 1 cube on dice to activate
    effect: "+3"          # Adds 3 to your attack roll
  overcharge:
    cubes: 2              # Need 2 cubes for overcharge
    effect: "+5"          # Better effect when overcharged
```

**Don't worry about writing this yourself yet!** The `@card-designer` agent will create these files for you through a conversation.

---

## Your First Real Task

### Let's Look at the Game Model

Type this command:

```
/model
```

**What this does**: Generates `GAME_MODEL.md`, a comprehensive report showing how the computer understands your entire game:
- All heroes with stats
- Combat mechanics explained
- Sample cards visualized
- Economy model
- Victory point calculations

**Open the file** (`GAME_MODEL.md`) and read through it. This is your **source of truth**. If something looks wrong, we'll fix it together.

---

## Next Steps (Choose Your Own Adventure)

### Path 1: Explore Existing Cards

```
Read the file: rules/_examples/example_weapon.yaml
```

This shows you a fully annotated weapon card with explanations for every field.

### Path 2: Ask Questions

```
@rules-oracle How does the Overkill mechanic work?
```

The oracle will explain any game concept by referencing the rulebook and code.

### Path 3: Learn a Technical Concept

```
/teach validation
```

Explains what "validation" means and why it's useful for game design.

### Path 4: Create Your First Card

```
@card-designer I want to create a new weapon
```

The designer will ask you questions and generate the YAML file automatically.

### Path 5: Run a Simulation

```
/simulate 01_basic_combat
```

Watch a predefined combat scenario play out with step-by-step narration.

---

## Common Questions

### "What if I break something?"

**Don't worry!** This system has guardrails:
- ✅ **Validation** checks your changes before they're saved
- ✅ **/rollback** command undoes your last change
- ✅ **/checkpoint** saves a restore point you can return to

### "How do I know if my card is balanced?"

Use these commands:
```
/balance weapons           # Shows all weapons with power analysis
/power-level [card name]   # Deep dive on a specific card
```

### "What does [technical term] mean?"

```
/teach [concept]
```

Examples:
- `/teach YAML`
- `/teach schema`
- `/teach validation`
- `/teach simulation`

### "I want to understand the code"

```
/explain-code engine/combat.py
```

The `@code-explainer` agent will walk you through any file in plain English.

---

## Quick Reference Card

### Exploration
- `/tour` → Guided walkthrough
- `/model` → Regenerate game model report
- `/help [command]` → Get help on any command

### Learning
- `/teach [concept]` → Explain technical terms
- `/explain-code [file]` → Annotated code walkthrough
- `@rules-oracle [question]` → Ask about game rules

### Creating
- `@card-designer` → Guided card creation wizard
- `/new-card` → Quick card creation
- `/copy-card [name]` → Duplicate and modify

### Testing
- `/validate` → Check all rules for errors
- `/simulate [scenario]` → Run combat simulations
- `/balance [type]` → Analyze card balance

### Visualizing
- `/visualize [metric]` → Generate charts
- `/diagram [system]` → Flow diagrams

### Safety
- `/checkpoint` → Save restore point
- `/rollback` → Undo last change

---

## You're Ready!

Take a deep breath. You don't need to memorize any of this—you can always return to this guide.

**Suggested first steps:**
1. Run `/tour` to see the repository
2. Run `/model` to see the game model
3. Read `GAME_MODEL.md` to verify the computer understands your game
4. Try `@card-designer` to create your first card

**Remember**: Claude Code is here to help. If you're ever stuck, just ask in plain English: "I don't understand X" or "How do I do Y?"

---

## Need Help?

- **Giovanni** → Your technical partner, can fix anything broken
- **GLOSSARY.md** → Definitions of all technical terms
- **docs/** folder → Step-by-step learning guides
- **Claude Code** → Your AI assistant, always available

**Let's build something amazing!** 🚀
