# 🤖 Guide 2: How to Use Claude Code

**Time to read**: 10 minutes
**Prerequisites**: [Guide 1: What Is This Repository](01_what_is_this_repo.md)

---

## What Is Claude Code?

Claude Code is an AI assistant that lives in your terminal (command line). Think of it as a **game design partner** that:
- ✅ Answers questions about your game
- ✅ Creates cards based on your descriptions
- ✅ Runs tests and simulations
- ✅ Explains programming concepts when needed
- ✅ Never judges—always helpful!

---

## Starting Claude Code

### Open Your Terminal

**On Mac**: Press `⌘ + Space`, type "Terminal", press Enter

**On Windows**: Press `Win + R`, type "cmd", press Enter

### Navigate to the Repository

```bash
cd ~/Documents/Projects/boardgame-engine
```

**What this does**: Changes your location to the game folder

### Launch Claude Code

```bash
claude
```

**What you'll see**:
```
Claude Code v1.0
Connected to repository: boardgame-engine
Type your message or /help for assistance

>
```

---

## Three Ways to Interact

### 1. Natural Language Conversations

Just talk naturally:

```
> Explain how the Overkill mechanic works in my game
```

Claude Code will read the rulebook and code, then explain it in plain English.

### 2. Specialized Agents

Call specific assistants using `@agent-name`:

```
> @card-designer I want to create a new sword
```

**Available agents**:
- `@tour-guide` → Repository walkthrough
- `@card-designer` → Create new cards
- `@balance-analyst` → Analyze power levels
- `@simulator` → Run combat scenarios
- `@rules-oracle` → Answer rules questions
- `@code-explainer` → Explain how code works
- `@teach` → Learn technical concepts

### 3. Slash Commands

Quick shortcuts starting with `/`:

```
> /validate
```

**Common commands**:
- `/tour` → Guided walkthrough
- `/model` → Generate game model report
- `/validate` → Check all rules
- `/simulate [scenario]` → Run simulation
- `/balance [type]` → Analyze balance
- `/teach [concept]` → Learn a topic

---

## Example Conversations

### Example 1: Learning About Your Game

```
> What heroes are available in my game?

Claude: I'll check the rules/ folder for hero data...

Currently, your game has 7 heroes defined in the rulebook:
1. Warrior - High HP, consistent damage
2. Mage - Spell-focused, fragile
3. Rogue - High burst, evasion mechanics
4. [... more heroes ...]

Each hero has unique dice, starting equipment, and 12 class abilities.

Would you like to see detailed stats for a specific hero?
```

### Example 2: Creating a Card

```
> @card-designer I want to add a new weapon

@card-designer: Great! Let's create a weapon together. I'll ask a few questions:

1. What's the weapon's name?
> Flame Blade

2. What rank is it? (1, 2, or 3)
> 1

3. How much should it cost in gold?
> 8

4. Which attribute activates it, and how much damage?
> 1 circle for +3 damage, 2 circles for +5 damage plus burn

5. Any special restrictions or effects?
> The burn effect deals 1 damage per turn for 2 turns

Perfect! I'll create the YAML file now...

[Creates rules/equipment/weapons_rank1.yaml with your card]

✅ Created Flame Blade
✅ Validated schema
⚠️ Balance note: 0.63 DPG is 12% above average—might be strong

Would you like to run a simulation to see it in action?
```

### Example 3: Running a Simulation

```
> /simulate 01_basic_combat

🎲 Simulating: Warrior vs. Goblin Berserker

Setting up:
  - Warrior: 5 HP, Iron Sword + Leather Armor
  - Goblin: 3 Health, 2 Armor, 4 Attack

Bout 1:
  Warrior rolls: 🔵🔵⚪
    → Activates Iron Sword (1🔵) = +3 damage
    → Activates Leather Armor (1🔵) = +1 armor
    → Total: 3 + 3 (base armor) = 6

  Goblin rolls: 💀⚪
    → Activates Reckless Strike (1💀) = +2
    → Total: 4 + 2 + 2 (armor) = 8

  Result: Goblin wins! Warrior loses armor

[... more bouts ...]

Final Result: ✅ Warrior wins in 4 bouts

Analysis:
  - Warrior took 1 damage
  - Goblin's armor (2) is significant
  - Warrior's double cube roll was key

Want to run 100 simulations to see the average outcome?
```

### Example 4: Checking Balance

```
> /balance weapons

📊 Weapon Balance Report (Rank 1)

| Weapon       | Cost | Avg Damage | DPG  | Activation % | Power Rating |
|--------------|------|------------|------|--------------|--------------|
| Iron Sword   | 5G   | 3.5        | 0.70 | 60%          | ⭐⭐⭐         |
| Flame Blade  | 8G   | 4.8        | 0.60 | 40%          | ⭐⭐⭐⭐       |
| War Hammer   | 6G   | 4.0        | 0.67 | 50%          | ⭐⭐⭐         |

Outliers:
  ⚠️ Flame Blade: 37% higher average damage than cost suggests

Recommendation: Consider reducing Flame Blade damage to +2/+4 or increasing cost to 10G

Run /power-level Flame Blade for detailed analysis.
```

---

## Understanding Responses

### Format of Responses

Claude Code uses structured outputs:

**Headers**: `##` for sections
**Code blocks**: `` ```yaml `` for showing code
**Lists**: `- item` or `1. item` for steps
**Emphasis**: `**bold**` for important points
**Emojis**: ✅ ❌ ⚠️ for quick status

### Types of Information

**Explanations**: Plain English descriptions
**Code examples**: Annotated YAML/Python
**Analysis**: Data tables and charts
**Suggestions**: Actionable recommendations
**Warnings**: Potential issues to address

---

## Advanced Features

### Multi-Step Workflows

Claude Code can handle complex tasks:

```
> I want to balance all rank 1 weapons. First analyze them,
  then suggest adjustments, then apply changes, and finally
  run simulations to verify.

Claude: I'll break this into steps:
1. Analyzing current weapon balance...
2. Identifying outliers...
3. Suggesting specific stat changes...
4. Would you like me to apply these changes? [Y/N]
> Y
5. Applying changes...
6. Running validation...
7. Simulating 100 games per weapon...
8. Generating comparison report...

[Shows before/after data]
```

### Context Awareness

Claude Code remembers your conversation:

```
> What's the Warrior's starting equipment?
Claude: Iron Sword and Leather Armor

> How much damage can that setup deal?
Claude: [Remembers we're talking about Warrior]
With Iron Sword (1 cube = +3), if Warrior rolls 2 cubes...
```

### File Operations

Claude Code can read/write files for you:

```
> Show me the Flame Blade card

Claude: [Reads rules/equipment/weapons_rank1.yaml]
Here's the Flame Blade definition:
[... shows YAML ...]

> Change the cost to 10G

Claude: [Edits the file]
✅ Updated Flame Blade cost: 8G → 10G
Running validation... ✅ Valid
```

---

## Best Practices

### 1. Be Specific

❌ "Make this card better"
✅ "Increase Flame Blade's damage from +3 to +4"

### 2. Ask for Explanations

If you don't understand something:
```
> Explain what "validation" means
> Why did this simulation fail?
> What does DPG measure?
```

### 3. Use Agents for Specialized Tasks

Instead of:
```
> Create a YAML file for a new weapon called...
```

Do this:
```
> @card-designer Create a new weapon called...
```

### 4. Save Checkpoints

Before major changes:
```
> /checkpoint before-balance-changes
```

If things go wrong:
```
> /rollback before-balance-changes
```

### 5. Iterate Incrementally

Don't change 10 cards at once. Instead:
1. Change one card
2. Test it
3. Verify balance
4. Move to next card

---

## Getting Help

### Built-In Help

```
/help                # General help
/help validate       # Help on specific command
@teach validation    # Learn a concept
```

### When Stuck

```
> I don't understand why this YAML is invalid

Claude: Let me explain validation errors in simple terms...
[Shows specific issue + how to fix]
```

### Ask for Tutorials

```
> Show me how to add a new monster step-by-step

Claude: Great! Let's walk through this together:
Step 1: Choose monster stats...
[Interactive tutorial]
```

---

## Common Mistakes (and How to Fix Them)

### Mistake 1: Assuming Context

❌ "Change the cost"
✅ "Change Flame Blade's cost to 10G"

**Why**: Claude Code needs to know *what* to change.

### Mistake 2: Not Validating

❌ Edit file → commit immediately
✅ Edit file → `/validate` → commit

**Why**: Catches errors before they break simulations.

### Mistake 3: Ignoring Warnings

Claude Code says:
```
⚠️ Warning: This card is 50% stronger than average
```

Don't ignore it! Ask:
```
> Is that a problem? How should I fix it?
```

---

## What You've Learned

✅ How to start Claude Code
✅ Three ways to interact (natural language, agents, commands)
✅ How to have effective conversations
✅ Best practices for vibecoding

---

## Next Steps

**Practice Exercise**:
1. Launch Claude Code
2. Run `/tour` to explore the repository
3. Ask `@rules-oracle How does combat work?`
4. Try `/validate` to check current rules

**Ready to continue?**
📘 [Guide 3: Understanding YAML →](03_understanding_yaml.md)
