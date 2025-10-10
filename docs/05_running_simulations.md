# 🧪 Guide 5: Running Simulations

**Time to read**: 20 minutes
**Prerequisites**: [Guide 4: Adding Your First Card](04_adding_your_first_card.md)

---

## What Is Simulation?

A simulation is a **virtual playthrough** of your game. Instead of manually rolling dice and resolving combat, the computer does it thousands of times to find patterns.

### Why Simulate?

**Manual playtesting**:
- Play 5 games manually → Takes 4 hours
- Limited sample size (5 games)
- Hard to isolate specific mechanics

**Simulation**:
- Run 1000 games → Takes 10 seconds
- Large sample size (statistically significant)
- Test isolated scenarios

**Both are valuable!** Simulation finds balance issues; playtesting finds fun issues.

---

## Types of Simulations

### 1. Single Combat

Test one specific fight:
```
/simulate hero=Warrior weapon=Iron_Sword vs monster=Goblin_Berserker
```

**Use when**: Testing a new card or mechanic in isolation

### 2. Monte Carlo (Many Iterations)

Run the same scenario many times:
```
/simulate scenario=basic_combat iterations=100
```

**Use when**: Finding average outcomes and win rates

### 3. Full Game Simulation

Simulate entire games from start to finish:
```
/simulate full-game players=3 strategy=balanced
```

**Use when**: Testing victory point paths and economy flow

### 4. Batch Comparison

Compare multiple options side-by-side:
```
/simulate compare weapons=all vs monster=Goblin_Berserker
```

**Use when**: Balancing a set of cards against each other

---

## Running Your First Simulation

### Step 1: Choose a Scenario

Pre-made scenarios live in `simulations/scenarios/`:
- `01_basic_combat.yaml` → Simple hero vs. monster
- `02_overkill_test.yaml` → Tests overkill mechanic
- `03_armor_break.yaml` → Tests armor mechanics
- `boss_fight_stage1.yaml` → Boss difficulty test

### Step 2: Run It

```
> /simulate 01_basic_combat
```

### Step 3: Read the Output

```
🎲 Loading scenario: 01_basic_combat.yaml

Scenario Description:
  "Basic combat between a level 1 Warrior with starting
   equipment against a rank 1 Goblin Berserker.
   Tests fundamental combat mechanics."

Setup:
  Hero: Warrior (Level 1)
    - HP: 5/5
    - Equipment: Iron Sword (1-handed), Leather Armor
    - Dice: 🔵🔵⚪🔺💀

  Monster: Goblin Berserker (Rank 1)
    - Health: 3 bouts
    - Armor: 2
    - Attack: +4
    - Overkill: 2
    - Dice: 💀💀⚪

Press Enter to start simulation (or Ctrl+C to cancel)...
```

### Step 4: Watch It Unfold

```
──────────────────────────────────────────────────────
Bout 1

Warrior turn:
  Rolls: 🔵 🔵 ⚪
  Equipment activation:
    → Iron Sword (1🔵): +3 damage ✓
    → Leather Armor (1⚪): +1 armor ✓
  Base armor: +2
  Total: 3 + 3 = 6

Goblin turn:
  Rolls: 💀 ⚪
  Ability activation:
    → Reckless Strike (1💀): +2 damage ✓
  Base attack: +4
  Base armor: +2
  Total: 4 + 2 + 2 = 8

Resolution: Goblin wins by 2
  → Warrior armor breaks (2 → 0)
  → No health damage yet

──────────────────────────────────────────────────────
Bout 2

Warrior turn:
  Rolls: 🔺 💀 💀
  Equipment activation:
    → Iron Sword needs 1🔵 ✗ (rolled 0)
    → No weapon activation!
  Armor: 0 (broken)
  Total: 0

Goblin turn:
  Rolls: 💀 💀
  Ability activation:
    → Reckless Strike (1💀): +2 damage ✓
    → OVERCHARGE (2💀): +4 damage ✓✓
  Total: 4 + 4 + 2 = 10

Resolution: Goblin wins by 10
  → Warrior takes 1 damage (5 → 4 HP)
  → Goblin health: 3 → 3

──────────────────────────────────────────────────────
[... more bouts ...]
──────────────────────────────────────────────────────

Final Result: ✅ Warrior wins in 5 bouts

Statistics:
  - Warrior ending HP: 2/5 (took 3 damage)
  - Bouts to victory: 5
  - Warrior activations: Iron Sword 3x, Leather Armor 2x
  - Goblin activations: Reckless Strike 4x (1x overcharged)

Key Moments:
  - Bout 1: Warrior loses armor early
  - Bout 2: Missed activation (no cubes)
  - Bout 4: Overkill damage (dealt 2 health in one bout)

Analysis:
  ✓ Combat took reasonable time (5 bouts)
  ✓ Both sides activated abilities multiple times
  ⚠ Warrior took significant damage (60%)
  💡 Early armor break was decisive
```

---

## Understanding Simulation Output

### Combat Log

**Shows**: Bout-by-bout breakdown
**Look for**:
- Activation rates (how often dice match requirements)
- Key turning points (armor breaks, overcharges)
- Total bout count (too long = boring, too short = swingy)

### Statistics Summary

**Shows**: Aggregate numbers
**Look for**:
- Ending HP (how much damage taken)
- Activation counts (consistency)
- Victory condition (how did someone win?)

### Analysis Section

**Shows**: Computer's interpretation
**Look for**:
- Balance flags (too easy/hard)
- Mechanic validation (did features work as intended?)
- Recommendations (what to test next)

---

## Monte Carlo Simulations

### Running Multiple Iterations

```
> /simulate 01_basic_combat iterations=100
```

### Statistical Output

```
🎲 Monte Carlo Simulation: 01_basic_combat (100 iterations)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Outcome Distribution:
  ✅ Warrior wins: 68 (68%)
  ❌ Warrior loses: 32 (32%)

Win Rate Analysis:
  Target: 50-65% (balanced matchup)
  Actual: 68%
  Assessment: ⚠️ Slightly favors Warrior

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Warrior Performance (when winning):
  - Avg ending HP: 2.8/5 (56% health)
  - Avg bouts: 4.2
  - Avg damage taken: 2.2

Warrior Performance (when losing):
  - Avg ending HP: 0
  - Avg bouts: 6.8
  - Insight: Losses take longer (attrition)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Activation Rates:
  Iron Sword (1🔵):
    - Expected probability: 40% (2 cubes on 5-sided die)
    - Actual activation: 38% (within variance)

  Reckless Strike (1💀):
    - Expected probability: 40% (2 skulls on 3-sided monster die)
    - Actual activation: 42% (within variance)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Insights:

💡 Warrior's starting equipment is slightly strong
   - Win rate 68% vs. target 55%
   - Recommend: Test against other rank 1 monsters

💡 Armor break timing matters
   - Losing armor in bout 1-2: 42% win rate
   - Keeping armor 3+ bouts: 81% win rate

💡 Overkill mechanic works as designed
   - Triggered in 23% of games
   - Reduced bout count by avg 1.4 bouts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommendations:
1. Test Warrior vs. other rank 1 monsters for comparison
2. Consider nerfing Leather Armor (+1 → +0 armor?) to reduce win rate
3. Current matchup acceptable for "easy" rank 1 monster
```

---

## Advanced: Custom Scenarios

### Create Your Own Test

Create `simulations/scenarios/my_test.yaml`:

```yaml
name: Frost Hammer vs. Armored Foes
description: Tests if Frost Hammer's armor shred is valuable

hero:
  class: Warrior
  level: 1
  equipment:
    - Frost Hammer
  health: 5

monsters:
  - name: Goblin Berserker
    rank: 1
  - name: Iron Guard
    rank: 1
    note: "High armor target"

iterations: 50

expected_outcome:
  win_rate_min: 50
  win_rate_max: 70
  note: "Armor shred should give advantage vs. Iron Guard"

analyze:
  - armor_shred_impact
  - activation_consistency
```

### Run Your Scenario

```
> /simulate my_test
```

---

## Batch Comparisons

### Compare All Weapons

```
> /simulate compare type=weapons rank=1 vs monster=Goblin_Berserker
```

### Output

```
📊 Batch Comparison: Rank 1 Weapons vs. Goblin Berserker (50 iterations each)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Weapon       | Win Rate | Avg HP Left | Avg Bouts | DPG  |
|--------------|----------|-------------|-----------|------|
| Iron Sword   | 68%      | 2.8/5       | 4.2       | 0.60 |
| War Axe      | 71%      | 2.5/5       | 3.8       | 0.67 |
| Frost Hammer | 62%      | 2.1/5       | 5.4       | 1.00 |
| Short Bow    | 54%      | 3.2/5       | 6.1       | 0.50 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analysis:

Strongest: War Axe
  - Highest win rate (71%)
  - Fast combat (3.8 bouts)
  - Good DPG (0.67)

Weakest: Short Bow
  - Lowest win rate (54%)
  - Slow combat (6.1 bouts)
  - Low DPG (0.50)

Outlier: Frost Hammer
  - Moderate win rate (62%)
  - High variance (48%-76% across matchups)
  - Highest DPG (1.00) but inconsistent activation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommendations:
- War Axe: Consider cost increase (6G → 7G)
- Short Bow: Needs buff (+2 → +3 damage or 5G → 4G cost)
- Frost Hammer: Acceptable given high-risk design
- Iron Sword: Perfect baseline
```

---

## Full Game Simulations

### Simulate Entire Games

```
> /simulate full-game players=3 stages=all
```

### What It Tests

- **Economy**: Gold accumulation over stages
- **Leveling**: When players hit 6 class abilities
- **Victory points**: Which path wins most often (HoB/Gold/CA)
- **Stage length**: How many turns per stage
- **PvP frequency**: How often players clash

### Sample Output

```
🎮 Full Game Simulation (3 players, all 3 stages)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Players:
  1. Warrior (Player 1)
  2. Mage (Player 2)
  3. Rogue (Player 3)

Stage 1 (Turns 1-6):
  - Boss defeated: Turn 6
  - Avg gold: 18G
  - Levels gained: 1-2 per player
  - PvP incidents: 2 duels

Stage 2 (Turns 7-13):
  - Boss defeated: Turn 13
  - Avg gold: 42G
  - Levels gained: 2-3 per player
  - PvP incidents: 4 duels, 1 clash

Stage 3 (Turns 14-22):
  - Boss defeated: Turn 22
  - Avg gold: 31G (spent on final equipment)
  - Levels gained: 1-2 per player
  - PvP incidents: 6 duels, 3 clashes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Final Standings:

1st Place: Warrior (12 VP)
  - HoB: 4 hearts (8 VP)
  - Gold: 45G, richest by 12G (+1 VP per G = +12 VP... wait, no)
  - [Correcting: +1 VP total for being richest, then +1 per G difference]
  - Gold advantage: +1 VP (richest)
  - Class abilities: 5 (not in top 2)
  - Total: 8 + 1 + 0 = 9 VP

2nd Place: Rogue (8 VP)
  - HoB: 2 hearts (4 VP)
  - Gold: 33G (second richest)
  - Class abilities: 6 (first to 6 CA: +3 VP)
  - Total: 4 + 0 + 3 = 7 VP

3rd Place: Mage (7 VP)
  - HoB: 3 hearts (6 VP)
  - Gold: 28G
  - Class abilities: 6 (second to 6 CA: +1 VP)
  - Total: 6 + 0 + 1 = 7 VP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Victory Path Analysis:

Most VP from: HoB collection (63% of total VP)
Second: Class abilities (21% of total VP)
Least: Wealth (16% of total VP)

⚠️ Balance concern: HoB path dominates
  - Aggressive players get more VP
  - Gold path undervalued

Recommendation: Increase gold VP or reduce HoB VP values
```

---

## Interpreting Results

### What to Look For

#### Win Rates
- **50-65%**: Balanced
- **65-75%**: Favors one side (intentional?)
- **75%+**: Imbalanced (needs adjustment)

#### Variance
- **Low (± 5%)**: Consistent outcomes
- **Medium (± 10%)**: Some RNG, acceptable
- **High (± 20%)**: Very swingy, "luck-based"

#### Bout Count
- **2-4 bouts**: Fast, decisive
- **5-7 bouts**: Standard combat length
- **8+ bouts**: Slow, potentially tedious

#### Activation Rates
- **Expected = Actual**: Working as designed
- **Expected > Actual**: Dice pool might be wrong
- **Expected < Actual**: Possible bug in code

---

## Common Simulation Mistakes

### Mistake 1: Too Small Sample

```
❌ iterations=5  (not statistically significant)
✅ iterations=100 (reliable patterns)
```

### Mistake 2: Testing in Isolation

```
❌ Only test new card vs. one monster
✅ Test vs. all rank-appropriate monsters
```

### Mistake 3: Ignoring Context

```
❌ "This weapon has 68% win rate, must be OP!"
✅ "68% vs. Goblin (easy), 52% vs. Orc (medium), 41% vs. Drake (hard)"
```

### Mistake 4: Simulation ≠ Fun

```
A card can be perfectly balanced (50% win rate)
but still be unfun to play (e.g., pure luck, no decisions)

Simulation finds balance issues.
Playtesting finds fun issues.
```

---

## Advanced Techniques

### Sensitivity Analysis

Test how changes affect outcomes:

```
> /simulate sensitivity variable=Iron_Sword_damage values=2,3,4,5
```

**Output**: Shows how win rate changes with each damage value

### Matchup Matrix

Test all heroes vs. all monsters:

```
> /simulate matchup-matrix heroes=all monsters=rank1
```

**Output**: Heat map showing which heroes counter which monsters

### Strategic AI Simulation

Test different player strategies:

```
> /simulate full-game players=4 strategies=aggressive,balanced,economic,CA-rush
```

**Output**: Which strategy wins most often

---

## What You've Learned

✅ What simulations are and why they're valuable
✅ How to run single combats and Monte Carlo simulations
✅ How to interpret statistical output
✅ How to create custom scenarios
✅ How to compare cards in batch
✅ When simulation is useful vs. manual playtesting

---

## Practice Exercises

### Exercise 1: Compare Two Cards

Pick two weapons you've created and run:
```
/simulate compare weapons=[card1,card2] vs monster=[monster]
```

### Exercise 2: Find Balance Point

If a card wins 75% of games, adjust its stats and re-simulate until you hit 55-60%.

### Exercise 3: Create Test Scenario

Write a YAML scenario that tests a specific mechanic (e.g., overkill, armor break, spell usage).

---

## Next Steps

**You now know how to**:
- Test balance quantitatively
- Compare cards objectively
- Iterate based on data

**Final learning guide**:
📘 [Guide 6: Reading Balance Reports →](06_reading_balance_reports.md)

Or start experimenting:
```
> /simulate --help
```
