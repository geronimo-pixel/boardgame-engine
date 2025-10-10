# 📊 Guide 6: Reading Balance Reports

**Time to read**: 25 minutes
**Prerequisites**: [Guide 5: Running Simulations](05_running_simulations.md)

---

## What Are Balance Reports?

Balance reports are **data-driven analyses** that reveal:
- Which cards are overpowered or underpowered
- How cards compare to each other
- What adjustments to make
- Whether your intuitions are correct

**Key insight**: Your gut feeling is valuable, but data confirms or challenges it.

---

## Types of Balance Reports

### 1. Card Power Analysis

**What it shows**: Individual card strength metrics
**Command**: `/power-level [card-name]`
**Use when**: Evaluating a single card in detail

### 2. Comparative Balance Report

**What it shows**: All cards of a type side-by-side
**Command**: `/balance [type]`
**Use when**: Balancing a set of cards (e.g., all rank 1 weapons)

### 3. Matchup Matrix

**What it shows**: Win rates between all combinations
**Command**: `/balance matchup-matrix`
**Use when**: Understanding rock-paper-scissors dynamics

### 4. Economy Report

**What it shows**: Gold flow, costs, and leveling pace
**Command**: `/balance economy`
**Use when**: Adjusting costs or rewards

### 5. Victory Path Analysis

**What it shows**: Which VP strategies win most often
**Command**: `/balance victory-paths`
**Use when**: Ensuring all win conditions are viable

---

## Reading a Basic Balance Report

### Generate a Report

```
> /balance weapons rank=1
```

### Understanding the Output

```
📊 Balance Report: Rank 1 Weapons
Generated: 2025-10-10
Sample size: 100 simulations per card
Test opponents: All rank 1 monsters

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary Table:

| Weapon       | Cost | DPG  | Win% | Activation% | Power Rating |
|--------------|------|------|------|-------------|--------------|
| Iron Sword   | 5G   | 0.60 | 68%  | 60%         | ⭐⭐⭐       |
| War Axe      | 6G   | 0.67 | 71%  | 50%         | ⭐⭐⭐⭐     |
| Flame Blade  | 8G   | 0.63 | 65%  | 40%         | ⭐⭐⭐⭐     |
| Frost Hammer | 7G   | 1.00 | 62%  | 35%         | ⭐⭐⭐⭐     |
| Short Bow    | 5G   | 0.50 | 54%  | 70%         | ⭐⭐         |
| Dagger       | 4G   | 0.50 | 58%  | 80%         | ⭐⭐⭐       |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Column Explanations:

Cost: Purchase price in gold
DPG: Damage per gold (efficiency metric)
Win%: Average win rate vs. all rank 1 monsters
Activation%: How often dice meet requirements
Power Rating: Overall strength (⭐-⭐⭐⭐⭐⭐)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Statistical Analysis:

Average cost: 5.8G
Average DPG: 0.65
Average win rate: 63%
Average activation: 56%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Outlier Detection:

🔴 OVERPOWERED:
  War Axe
    - Win rate: 71% (target: 50-65%)
    - 9% above acceptable range
    - Recommendation: Increase cost to 7G OR reduce damage +4 → +3

🟡 POWERFUL (within range but high):
  Frost Hammer
    - DPG: 1.00 (78% above average)
    - Win rate: 62% (acceptable due to low activation)
    - Recommendation: Monitor in playtesting

🔵 UNDERPOWERED:
  Short Bow
    - Win rate: 54% (acceptable but low end)
    - DPG: 0.50 (23% below average)
    - Recommendation: Consider cost reduction to 4G OR damage increase

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Design Insights:

✓ Iron Sword is perfect baseline
  - 68% win rate (slight Warrior advantage is intentional)
  - 0.60 DPG (balanced efficiency)
  - 60% activation (consistent but not guaranteed)

✓ High-risk/high-reward cards working as intended
  - Flame Blade: High cost, high burst, low consistency
  - Frost Hammer: Very high DPG balanced by restrictions

⚠ Efficiency outliers
  - War Axe too efficient (0.67 DPG, 71% win rate)
  - Short Bow too inefficient (0.50 DPG, 54% win rate)

💡 Activation rates inversely correlate with power
  - Dagger: 80% activation → ⭐⭐⭐ power
  - Frost Hammer: 35% activation → ⭐⭐⭐⭐ power
  - This is good design! Consistency vs. power tradeoff

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommended Actions:

1. [HIGH PRIORITY] Nerf War Axe
   - Option A: Cost 6G → 7G
   - Option B: Damage +5 → +4
   - Run simulations to verify

2. [MEDIUM PRIORITY] Buff Short Bow
   - Option A: Cost 5G → 4G
   - Option B: Damage +2 → +3
   - Test player feedback (ranged flavor might compensate)

3. [LOW PRIORITY] Monitor Frost Hammer
   - Currently acceptable
   - Watch for "feels bad" feedback on missed activations

4. [KEEP] Iron Sword, Flame Blade, Dagger
   - Well-balanced as-is
   - Use as reference points for future cards

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
- Run /power-level War_Axe for detailed breakdown
- Apply recommended changes
- Re-run /balance weapons to verify
- Manual playtest to confirm feel
```

---

## Key Metrics Explained

### 1. DPG (Damage Per Gold)

**Formula**: Average damage ÷ Cost

**What it measures**: Efficiency (value for money)

**Interpretation**:
- **0.40-0.60**: Standard efficiency
- **0.60-0.80**: Good efficiency
- **0.80+**: Very efficient (potential OP)
- **<0.40**: Inefficient (potential UP)

**Example**:
```
Iron Sword: 3.5 avg damage / 5G = 0.70 DPG (efficient)
Frost Hammer: 7 avg damage / 7G = 1.00 DPG (very efficient!)
```

**Important**: DPG doesn't account for:
- Activation difficulty
- Special effects (armor shred, status effects)
- Opportunity costs (two-handed weapons)

### 2. Win Rate

**What it measures**: Likelihood of victory

**Target ranges**:
- **50-55%**: Balanced, slight advantage
- **55-65%**: Acceptable range
- **65-75%**: Strong, possibly intentional
- **75%+**: Overpowered

**Context matters**:
- Hero vs. "easy" monster: 60-70% is fine
- Hero vs. "hard" monster: 40-50% is fine
- Hero vs. boss: 30-40% is fine

### 3. Activation Rate

**What it measures**: % of bouts where card can be used

**Interpretation**:
- **70%+**: Very consistent
- **50-70%**: Moderate consistency
- **30-50%**: Inconsistent (needs good rolls)
- **<30%**: Rarely activates

**Balance principle**: High activation = lower power, Low activation = higher power

**Example**:
```
Dagger (1 cube needed):
  - Activation: 80%
  - Effect: +2 damage (modest)

Frost Hammer (2 triangles needed):
  - Activation: 35%
  - Effect: +7 damage + armor shred (powerful!)
```

### 4. Power Rating (⭐)

**What it measures**: Holistic strength assessment

**Scale**:
- ⭐ → Very weak
- ⭐⭐ → Below average
- ⭐⭐⭐ → Balanced
- ⭐⭐⭐⭐ → Strong
- ⭐⭐⭐⭐⭐ → Very strong / OP

**Calculation**: Combines DPG, win rate, activation rate, special effects

---

## Deep Dive: Card Power Report

### Generate Detailed Analysis

```
> /power-level War_Axe
```

### Reading the Output

```
🔍 Power Level Analysis: War Axe (Rank 1 Weapon)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Card Definition:
```yaml
name: War Axe
rank: 1
cost: 6
hands: 1
attributes:
  base:
    cubes: 1
    effect: "+4"
  overcharge:
    cubes: 2
    effect: "+6"
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Metrics:

Cost: 6G (rank 1 avg: 5.8G)
Base damage: +4 (rank 1 avg: +3.2)
OC damage: +6 (rank 1 avg: +5.1)
DPG: 0.67 (rank 1 avg: 0.65, +3% above)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Activation Analysis:

Requirement: 1 cube
Expected probability:
  - Warrior (2 cubes / 5 dice): 40%
  - Actual from 100 simulations: 42%

Overcharge requirement: 2 cubes
Expected probability: 16%
Actual from simulations: 14%

Consistency rating: HIGH (activates in 42% of bouts)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Combat Performance:

Tested against: All rank 1 monsters (100 games each)

Goblin Berserker:
  - Win rate: 72% (vs. Iron Sword: 68%)
  - Avg bouts: 3.6 (vs. Iron Sword: 4.2)
  - Avg damage taken: 2.3 HP (vs. Iron Sword: 2.8 HP)

Orc Raider:
  - Win rate: 74% (vs. Iron Sword: 63%)
  - Avg bouts: 4.1 (vs. Iron Sword: 5.0)
  - Avg damage taken: 2.7 HP (vs. Iron Sword: 3.2 HP)

Dark Cultist:
  - Win rate: 67% (vs. Iron Sword: 64%)
  - Avg bouts: 4.8 (vs. Iron Sword: 5.3)
  - Avg damage taken: 1.9 HP (vs. Iron Sword: 2.1 HP)

Overall win rate: 71% (vs. baseline 65%)
Performance edge: +6% over Iron Sword

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Value Analysis:

Cost comparison:
  - War Axe: 6G for 71% win rate = 11.8% per gold
  - Iron Sword: 5G for 68% win rate = 13.6% per gold

Wait, Iron Sword is MORE efficient per gold spent!
But War Axe has higher absolute performance.

Interpretation: War Axe is a luxury purchase—better performance
but diminishing returns (you pay 20% more for only 3% better win rate).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Special Features:

✓ Overcharge effect analyzed:
  - Triggers in 14% of bouts
  - When it triggers: Avg +2.4 damage over base
  - Impact: Reduces combat length by ~0.8 bouts

✗ No special effects (armor break, status, etc.)
✗ No restrictions

Complexity: LOW (straightforward damage increase)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Power Level Summary:

Overall rating: ⭐⭐⭐⭐ (Strong)

Strengths:
  + Higher base damage than most rank 1 weapons
  + Consistent activation (42%)
  + Only 1-handed (can pair with shield/second weapon)
  + Solid overcharge potential

Weaknesses:
  - Slightly expensive (6G)
  - No special effects (just raw damage)
  - Diminishing returns vs. cheaper options

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balance Verdict:

Status: 🟡 SLIGHTLY OVERPOWERED

Issue: 71% win rate exceeds 65% target ceiling by 6%

Severity: MODERATE (not game-breaking, but noticeable edge)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommended Adjustments:

Option 1: Increase cost
  Current: 6G
  Suggested: 7G
  Predicted impact: Win rate unchanged, but DPG drops from 0.67 → 0.57
  Rationale: Makes it a true luxury item

Option 2: Reduce base damage
  Current: +4 base, +6 OC
  Suggested: +3 base, +5 OC
  Predicted impact: Win rate drops to ~65%
  Rationale: Brings it in line with other weapons

Option 3: Add activation requirement
  Current: 1 cube
  Suggested: 1 cube + 1 circle
  Predicted impact: Activation drops to ~20%, win rate to ~62%
  Rationale: Turns it into a high-skill weapon

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommendation: Option 1 (cost increase)

Reasoning:
  - Maintains fun factor (no gameplay change)
  - Creates meaningful choice (Iron Sword for value vs. War Axe for power)
  - Players who save gold get rewarded

Apply change?
  > Yes → I'll update the YAML and re-validate
  > No → I'll log this report for later review
  > Test first → I'll run simulations with proposed changes
```

---

## Comparing Changes: Before & After

### After Applying a Fix

```
> Apply Option 1 (cost 6G → 7G) and re-run analysis

@balance-analyst: Updating War Axe cost...
✅ Changed cost: 6G → 7G
🧪 Running validation... ✅ VALID
📊 Re-running balance analysis...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before vs. After Comparison:

|Metric       | Before (6G) | After (7G) | Change    |
|-------------|-------------|------------|-----------|
| DPG         | 0.67        | 0.57       | -15%      |
| Win rate    | 71%         | 71%        | No change |
| Value/gold  | 11.8%       | 10.1%      | -14%      |
| Power rating| ⭐⭐⭐⭐     | ⭐⭐⭐     | Normalized |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analysis:

✅ DPG now within acceptable range (0.57 vs. avg 0.65)
✅ Still performs well (71% win rate)
✅ Creates strategic choice:
   - Iron Sword: 5G, 68% win rate (value option)
   - War Axe: 7G, 71% win rate (premium option)
✅ Economic balance: Worth saving for, not mandatory

Verdict: ✅ BALANCED

Save changes?
```

---

## Economy Balance Report

### Generate Economy Analysis

```
> /balance economy
```

### Reading the Output

```
💰 Economy Balance Report

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Gold Income Sources (per stage):

Stage 1:
  - Monster loot: 4-6G per monster
  - Avg monsters per player: 4
  - Total income: ~20G

Stage 2:
  - Monster loot: 8-12G per monster
  - Avg monsters per player: 5
  - Total income: ~50G
  - Cumulative: ~70G

Stage 3:
  - Monster loot: 15-20G per monster
  - Avg monsters per player: 4
  - Total income: ~68G
  - Cumulative: ~138G

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Gold Expenditures:

Equipment purchases:
  - Stage 1: Avg 12G (2 items)
  - Stage 2: Avg 28G (3-4 items)
  - Stage 3: Avg 40G (4-5 items)
  - Total: ~80G

Leveling:
  - 10G per level
  - Avg 5 levels per player
  - Total: 50G

Shop refreshes: ~3G

Total expenses: ~133G

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

End-game Gold:

Income: ~138G
Expenses: ~133G
Remaining: ~5G

Distribution:
  - Richest player: ~15G (spent less on equipment)
  - Average player: ~5G
  - Poorest player: ~0G (spent on final equipment)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balance Assessment:

⚠️ Issue: Gold VP path undervalued

Richest player advantage: 15G over poorest
Current VP: +1 VP total for being richest

If VP was +1 per gold difference:
  Richest: +15 VP (breaks game!)

Current rule is intentional but may feel unrewarding.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommended Adjustments:

Option 1: Increase wealth VP
  Current: Richest gets +1 VP total
  Suggested: Richest gets +1 VP per 5G difference
  Example: 15G lead = +3 VP

Option 2: Add wealth milestones
  - 30G: +1 VP
  - 50G: +2 VP (cumulative: +3 VP)
  - 80G: +3 VP (cumulative: +6 VP)

Option 3: Keep as-is
  Rationale: Gold is for buying power, not VP directly
```

---

## Victory Path Analysis

```
> /balance victory-paths
```

```
🏆 Victory Path Analysis (based on 50 full-game simulations)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VP Sources (average per player):

HoB Collection:
  - Avg HoB collected: 3.2 hearts
  - Avg VP value: 6.4 VP
  - % of total VP: 64%

Wealth:
  - Richest player: +1 VP (only 1 player)
  - Avg across all players: +0.25 VP
  - % of total VP: 2.5%

Class Abilities:
  - First to 6 CA: +3 VP
  - Second to 6 CA: +1 VP
  - Avg across all players: +1.0 VP
  - % of total VP: 10%

Total avg VP per player: 10 VP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Winning Strategy Distribution:

HoB-focused (aggressive): 68% of wins
CA-focused (leveling): 24% of wins
Gold-focused (economic): 8% of wins

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balance Assessment:

🔴 IMBALANCED: HoB path dominates

Issue: Fighting bosses/monsters gives both:
  - Equipment/gold (instrumental value)
  - HoB (victory points)

Meanwhile:
  - Gold path: Gives power but little VP
  - CA path: Costs gold (10G/level) for moderate VP

Result: Optimal strategy is "fight everything" (which may be intentional?)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommendations:

If you want diverse strategies:
1. Increase gold VP (wealth milestones)
2. Increase CA VP (+5/+2 instead of +3/+1)
3. Reduce HoB VP values

If aggressive play is intentional theme:
✓ Keep as-is
✓ Game design coherent: combat-focused game rewards combat
```

---

## Acting on Balance Reports

### Workflow

1. **Generate report**
```
/balance [type]
```

2. **Identify issues**
- Read outlier section
- Check recommendations

3. **Propose changes**
```
@balance-analyst Suggest fixes for [card-name]
```

4. **Test changes**
```
> Test with Option 1 (cost increase)

@balance-analyst: Running simulations with proposed change...
[Shows predicted outcomes]
```

5. **Apply if satisfied**
```
> Apply changes

✅ Updated [card-name]
✅ Re-validated
📊 New balance report generated
```

6. **Iterate if needed**

Repeat until happy with results

7. **Commit**
```
> /checkpoint balanced-weapons-rank1
```

---

## What You've Learned

✅ How to generate and read balance reports
✅ What key metrics mean (DPG, win rate, activation rate)
✅ How to identify overpowered and underpowered cards
✅ How to interpret recommendations
✅ How to test and apply balance changes
✅ How economy and victory path analysis works

---

## Final Thoughts

### Balance Is Iterative

You won't get it perfect on the first try. That's okay!

Design → Test → Analyze → Adjust → Repeat

### Data + Intuition

**Data tells you WHAT is imbalanced**
**Intuition tells you WHY and HOW to fix it**

Use both!

### Playtest Still Matters

Simulation finds:
- Statistical imbalances
- Mathematical outliers
- Efficiency problems

Playtesting finds:
- Fun/unfun interactions
- Confusing rules
- Emergent strategies

**You need both!**

---

## Practice Exercise

### Challenge: Balance a Full Set

1. Generate balance report for all rank 1 weapons
2. Identify the strongest and weakest
3. Propose changes to bring them in line
4. Test your changes in simulation
5. Apply and commit if satisfied

```
> /balance weapons rank=1
> @balance-analyst Suggest fixes for [outliers]
> Test proposed changes
> Apply and commit
```

---

## You're Ready!

You now have all the tools to:
- ✅ Design cards through conversation
- ✅ Validate automatically
- ✅ Test in simulation
- ✅ Analyze balance quantitatively
- ✅ Iterate based on data
- ✅ Commit safely with version control

**Start creating!** 🎨

---

## Quick Reference

```bash
# Balance commands
/balance [type]                    # Compare all cards of type
/power-level [card]                # Deep dive on specific card
/balance matchup-matrix            # Win rates between all cards
/balance economy                   # Gold flow analysis
/balance victory-paths             # VP strategy viability

# Workflow
/balance → identify issues → /simulate with changes → apply → /checkpoint
```

**Need help?** Ask `@balance-analyst [your question]`
