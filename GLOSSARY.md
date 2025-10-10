# 📚 Glossary: Technical Terms Explained Simply

This glossary explains programming and game design concepts in plain English. Whenever you encounter an unfamiliar term, look it up here—or ask `/teach [term]` for examples from your project.

---

## General Concepts

### Repository (Repo)
**What it is**: A folder that tracks all changes to your files using Git.

**Why it matters**: Lets you:
- See the history of every change
- Undo mistakes safely
- Collaborate with others without conflicts

**Example**: This boardgame-engine folder is a repository.

### Git
**What it is**: Software that tracks changes to files over time.

**Why it matters**: It's like a time machine for your work—you can always go back to any previous version.

**Common commands**:
- `git status` → See what changed
- `git commit` → Save a snapshot
- `git log` → View history

### Branch
**What it is**: A separate timeline for your work.

**Why it matters**: You can experiment without affecting the main version. If it works, merge it in. If not, delete it.

**Example**:
- `main` branch → Stable, tested rules
- `experiments/pietro` branch → Your sandbox

### Commit
**What it is**: A saved snapshot of your work at a point in time.

**Why it matters**: Each commit is a checkpoint you can return to.

**Example**: "Add Fireball Staff weapon card" is a commit message.

### Pull Request (PR)
**What it is**: A proposal to merge your changes into the main branch.

**Why it matters**: Giovanni can review your changes before they become official.

**Workflow**:
1. You work in `experiments/pietro` branch
2. When ready, create a PR
3. Giovanni reviews and suggests changes
4. Once approved, it merges into `main`

---

## File Formats

### YAML (YAM-ul)
**What it is**: A text format for structured data that's easy for humans to read.

**Why it matters**: Your game cards are written in YAML so both you and the computer can understand them.

**Example**:
```yaml
name: Iron Sword
cost: 5
damage: +3
```

**Rules**:
- **Indentation matters!** (2 spaces, not tabs)
- Use `:` to separate keys and values
- Use `-` for lists

### JSON
**What it is**: Another format for structured data, similar to YAML but more strict.

**Why it matters**: Used for schemas (validation rules) and some outputs.

**You rarely need to write it yourself—let the tools generate it.**

### Python
**What it is**: A programming language that runs the game engine.

**Why it matters**: The `engine/` folder contains Python code that simulates your game.

**You don't need to write Python!** Just know it's what makes simulations work.

### Markdown (.md files)
**What it is**: A simple way to format text with headings, lists, and links.

**Why it matters**: All documentation (like this file) is written in Markdown.

**Basic syntax**:
- `# Heading` → Large heading
- `**bold**` → **bold text**
- `- item` → Bullet point
- `` `code` `` → `inline code`

---

## Validation & Testing

### Schema
**What it is**: A set of rules that defines what a valid card looks like.

**Why it matters**: Before you add a card, the schema checks:
- Are all required fields present? (name, cost, etc.)
- Are the values the right type? (cost must be a number)
- Does the structure make sense?

**Example**: The weapon schema requires `name`, `rank`, `cost`, and `attributes`.

**Location**: `rules/_schemas/`

### Validation
**What it is**: The process of checking if your data follows the schema rules.

**Why it matters**: Catches errors before they break simulations:
- ❌ Missing cost field → Validation fails
- ❌ Negative damage → Validation warns
- ✅ All fields correct → Validation passes

**How to use it**:
```
/validate              # Check all files
/validate weapons.yaml # Check specific file
```

### Linting
**What it is**: Checking code/data for style and quality issues.

**Why it matters**: Keeps your files consistent and readable.

**Example**: Lint might warn "Use 2 spaces for indentation, not 3."

### Pre-commit Hook
**What it is**: A script that runs automatically before you save a commit.

**Why it matters**: Blocks commits that would break things:
- ❌ Invalid YAML → Commit blocked, shows error
- ✅ Valid YAML → Commit succeeds

**You don't need to set this up—it's already configured!**

---

## Simulation & Analysis

### Simulation
**What it is**: Running a virtual version of your game to see what happens.

**Why it matters**: Test game balance without playing manually:
- Does this hero beat this monster?
- How many turns to reach level 6?
- Which strategy wins most often?

**Example**:
```
/simulate 01_basic_combat
→ Warrior vs. Goblin, shows bout-by-bout results
```

### Monte Carlo Simulation
**What it is**: Running thousands of simulations with random dice rolls to find patterns.

**Why it matters**: Finds statistical truths:
- "Flame Blade wins 68% of fights against Rank 1 monsters"
- "Average gold at end of Stage 1: 23G"

**Usage**: Advanced tool for deep balance analysis.

### Scenario
**What it is**: A predefined test case for simulation.

**Why it matters**: Reusable tests you can run anytime:
- `01_basic_combat.yaml` → Simple hero vs. monster
- `02_overkill_test.yaml` → Tests overkill mechanic
- `boss_fight_stage1.yaml` → Tests boss difficulty

**Location**: `simulations/scenarios/`

### Win Rate
**What it is**: Percentage of simulations where a specific outcome occurs.

**Why it matters**: Measures card/hero strength:
- 50% win rate → Balanced
- 75% win rate → Probably overpowered
- 25% win rate → Probably underpowered

---

## Balance & Analysis

### DPG (Damage Per Gold)
**What it is**: A metric for weapon efficiency—damage divided by cost.

**Why it matters**: Compares card value:
- Iron Sword: 3 damage / 5 gold = **0.60 DPG**
- Flame Blade: 5 damage / 8 gold = **0.63 DPG**

**Higher DPG = better value** (but might be overpowered)

### Activation Probability
**What it is**: Chance of rolling the dice you need to use a card.

**Why it matters**: A powerful card is useless if you can never activate it.

**Example**:
- Needs 1 cube → 40% chance (easy)
- Needs 3 cubes → 8% chance (rare)

### Overcharge (OC)
**What it is**: Activating a card multiple times for bonus effects.

**Why it matters**: Rewards lucky dice rolls with extra power.

**Example**:
- Base: 1 circle → +3 damage
- OC: 2 circles → +5 damage + burn

### Outlier
**What it is**: A card that's significantly different from others (too strong/weak).

**Why it matters**: Balance reports flag outliers for review.

**Example**: "Flame Blade has 0.89 DPG while others average 0.56—58% stronger!"

### Cost Curve
**What it is**: How card power scales with cost.

**Why it matters**: Ensures expensive cards are worth their price.

**Example**: Rank 1 weapons cost 5-10G, Rank 3 weapons cost 15-25G.

---

## Claude Code Concepts

### Agent
**What it is**: A specialized AI assistant for specific tasks.

**Why it matters**: Different agents have different expertise:
- `@card-designer` → Creates new cards
- `@balance-analyst` → Analyzes power levels
- `@simulator` → Runs combat scenarios
- `@rules-oracle` → Answers game rules questions

**Usage**: `@agent-name your request here`

### Slash Command
**What it is**: A shortcut that starts with `/` to trigger actions.

**Why it matters**: Quick access to common tasks without typing full requests.

**Examples**:
- `/validate` → Check all rules
- `/simulate [scenario]` → Run simulation
- `/balance [type]` → Analyze card balance
- `/teach [concept]` → Learn a technical term

### Vibecoding
**What it is**: Programming by describing what you want in natural language, letting AI handle the technical details.

**Why it matters**: You don't need to know Python or YAML syntax—just explain your intent.

**Example**:
```
You: "I want a sword that deals 4 damage and costs 6 gold"
@card-designer: "I'll create that YAML file for you..."
```

### Context
**What it is**: The information Claude Code uses to understand your requests.

**Why it matters**: The more context it has, the better its responses.

**How it works**: When you open a file or run a command, Claude Code remembers that information for the conversation.

---

## Common Abbreviations

- **CA** → Class Ability
- **G** → Gold (in-game currency)
- **HoB** → Heart of the Boss (victory point tokens)
- **OK** → Overkill
- **OC** → Overcharge
- **VP** → Victory Point
- **DPG** → Damage Per Gold
- **PR** → Pull Request
- **CLI** → Command Line Interface (the terminal)
- **AI** → Artificial Intelligence

---

## Game-Specific Terms

These are terms from your board game that are important for modeling:

### Bout
**What it is**: A single exchange of attacks in combat.

**Why it matters**: Determines combat resolution:
- Duels → 1 bout
- Hunts → Multiple bouts until victory/defeat

### Armor Break
**What it is**: When armor is destroyed after losing a bout.

**Why it matters**: Losing armor makes you vulnerable—no more armor bonus until you get new armor.

### Overkill (OK)
**What it is**: Dealing extra damage by exceeding the opponent's total by a threshold.

**Why it matters**: Speeds up fights—kill monsters in fewer bouts.

**Example**: Monster has OK 2. If you beat them by 3+, deal 2 damage instead of 1.

### Attributes (Cube, Circle, Triangle, Skull)
**What it is**: Symbols on dice that activate equipment/abilities.

**Why it matters**: Core resource system for combat—matching symbols to card requirements.

---

## Need More Help?

- **`/teach [concept]`** → Get examples from your project
- **GETTING_STARTED.md** → Step-by-step first session guide
- **docs/** → Progressive learning guides
- **Ask Giovanni** → Your technical partner

---

**Tip**: You don't need to memorize this! Just know it exists so you can look things up when needed.
