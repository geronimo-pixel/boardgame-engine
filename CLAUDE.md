# Board Game Engine - Technical Documentation

You are assisting Giovanni, an experienced developer maintaining a board game simulation engine. This is a **dual-user project** where Pietro (game designer, no coding experience) creates cards using Codex, and you help Giovanni maintain the technical infrastructure.

## Project Overview

**Goal:** Enable Pietro to design a dice-based board game through YAML card definitions while Giovanni maintains a robust Python simulation engine.

**Tech Stack:**
- Python 3.10+ (backend engine)
- YAML (card definitions)
- Rich library (CLI visualization)
- Git (version control)
- FastAPI (future API, if needed)

**Key Insight:** Pietro uses OpenAI Codex (VSCode plugin) with `AGENTS.md` guidance. Codex knows Pietro's limitations and shields him from code complexity.

---

## System Architecture

### Code Organization

```
/engine/                      Core simulation engine
  combat_sim.py (512 lines)   Combat resolution logic
  dice_loader.py (221 lines)  Dice mechanics & probabilities
  monster_loader.py (234 lines) YAML parsing for monsters
  stage_sim.py (304 lines)    Multi-combat stage scenarios

/rules/                       YAML card definitions (Pietro's domain)
  monsters/                   Monster cards
  heroes/                     Hero cards
  equipment/                  Weapons, armor
  spells/                     Spell cards
  _examples/                  Templates for Pietro
  _core/                      Core game data (dice)

/docs/                        Documentation
  pietro-guide.md             Non-technical guide for Pietro
  technical/                  Technical specs (this domain)

/tests/                       Test suite
  test_combat_system.py       Comprehensive combat tests
  detailed_sim_tests.py       Edge case testing
  verify_monsters.py          YAML validation

/Original files/              Pietro's source text files
  Monsters.txt                Original monster definitions
  Spells.txt                  Original spell definitions
  H&C Abilities.txt           Hero/class abilities
  Equipment.txt               Equipment definitions
  DICE.txt                    Dice face definitions

play_combat.py                CLI visualizer (Pietro's main tool)
TEST_REPORT.md                Last test results
AGENTS.md                     Codex configuration (Pietro's AI)
CLAUDE.md                     This file (Giovanni's AI)
```

### Data Flow

```
YAML Cards (Pietro)
     ↓
monster_loader.py / dice_loader.py
     ↓
Structured Python objects (Monster, DiceTables)
     ↓
combat_sim.py (simulation logic)
     ↓
CombatResult (bout-by-bout logs)
     ↓
play_combat.py (CLI visualization)
     ↓
Pietro sees visual results
```

---

## Engine Components

### combat_sim.py (Core Combat Logic)

**Key Functions:**
- `simulate_warrior_vs_monster()` - Warrior combat simulation
- `simulate_hunter_triangle_bow_vs_monster()` - Hunter combat simulation
- `choose_best_weapon_configuration()` - Equipment activation logic
- `choose_best_shield_configuration()` - Shield activation logic

**Data Structures:**
```python
@dataclass
class BoutLog:
    bout_number: int
    hero_face: List[str]           # Hero die result
    class_faces: List[List[str]]   # Class dice results
    sword: EquipmentResult          # Sword activation
    shield: EquipmentResult         # Shield activation
    remaining_attributes: Dict[str, int]
    rat_skulls: List[int]           # Monster dice results
    rat_attack: int
    rat_bonus_breakdown: str
    hero_attack: int
    hero_armor: int
    outcome: str                    # "hero wins" / "monster wins"

@dataclass
class CombatResult:
    winner: str
    bouts: List[BoutLog]
    final_hero_health: int
    final_monster_health: int
```

**Combat Flow:**
1. Initialize hero/monster health
2. Loop until one reaches 0 HP or max bouts reached:
   - Roll hero dice (hero die + 2 class dice)
   - Count attributes (square, triangle, circle)
   - Activate equipment (sword, shield based on symbols)
   - Roll monster dice (count skulls)
   - Calculate attacks (base + equipment + skull bonuses)
   - Compare attacks, apply damage to loser
   - Log bout details
3. Return CombatResult with complete history

### monster_loader.py (YAML Parsing)

**Key Functions:**
- `load_monsters()` - Loads all monsters from Original files/Monsters.txt
- `get_monster_by_name()` - Fetches specific monster

**Monster Data Structure:**
```python
@dataclass
class Monster:
    name: str
    rank: int
    health: int
    armor: int
    attack: int
    overkill: int
    dice_code: str  # e.g. "2m", "1c+1m", "1b+1c"
    skull_mapping: Dict[int, int]  # {skulls: attack_bonus}
    overcharge_bonus: int
    loot: str
```

**Parser Quirks:**
- Reads tab-delimited text files (not YAML yet for monsters)
- Skull mappings parsed from multi-line text
- Overcharge (OC) = bonus when skulls exceed defined mapping
- **KNOWN ISSUE:** Duplicate "Rat" entries (lines 13-31) - only second one loads

### dice_loader.py (Dice Mechanics)

**Key Functions:**
- `load_all_dice()` - Loads hero, class, and monster dice from rules/_core/dice.yaml

**Dice Structure:**
```python
@dataclass
class HeroDie:
    hero: str  # "warrior", "hunter", etc.
    faces: List[List[str]]  # Each face can have multiple symbols

@dataclass
class MonsterDie:
    category: str  # "minion", "chief", "boss"
    skull_counts: List[int]  # Number of skulls on each face
```

**Probabilities:**
- Each die has exactly 6 faces
- Hero/class dice: symbols are "square", "triangle", "circle"
- Monster dice: integers representing skull counts (0-3)

---

## Testing Infrastructure

### Current Test Coverage

**test_combat_system.py** (450 lines)
- Monster loading validation (28 monsters)
- Dice loading validation (7 heroes × 2 dice)
- Combat simulations (5+ scenarios)
- Edge cases (0 attack, high armor, long combats)
- Data integrity checks

**Test Results:** 26/28 checks passing (92.9% success rate)

**Known Failures:**
1. Duplicate Rat monster (only 1 of 2 loads)
2. Loot parsing for Imp/Jaguar (special abilities mixed in)

### Running Tests

```bash
# Full test suite
python test_combat_system.py

# Edge case testing
python detailed_sim_tests.py

# Monster validation
python verify_monsters.py

# Stage simulations
python -m engine.stage_sim simulations/scenarios/stage1_baseline.yaml
```

---

## Critical Issues

### Issue #1: Duplicate Rat Monster (PRIORITY: HIGH)

**Location:** `Original files/Monsters.txt` lines 13-31

**Problem:**
```
Rat #1 (lines 13-22):
  Health=1, Armor=1, Attack=2, Loot=4G

Rat #2 (lines 23-31):
  Health=1, Armor=0, Attack=1, Loot=2G
```

**Current Behavior:** Parser loads only Rat #2, ignores #1

**Impact:**
- Missing monster variant
- Tests use weaker version
- Pietro may be confused by discrepancy

**Fix Required:**
1. Ask Pietro which is correct OR
2. Rename to "Rat" and "Giant Rat" OR
3. Remove outdated entry

### Issue #2: Special Ability Loot Parsing (PRIORITY: MEDIUM)

**Problem:** Some monsters have special abilities in loot field:
- Imp: `Loot="3 sk = escapes drop half G"` (should be "4G")
- Jaguar: `Loot="OC attacker loses 1 G,"` (should be numeric)

**Impact:** Loot not parseable as gold amounts

**Fix:** Update monster_loader.py to separate special effects from loot values

---

## Development Workflow

### Git Strategy

**Pietro's Workflow:**
- Works directly on `main` branch (simple)
- Commits with basic messages
- Pushes after testing
- Codex helps with Git basics

**Giovanni's Workflow:**
- Pull latest before starting work
- Create feature branches for new features
- Test locally before pushing
- Create PR for complex changes
- Merge to main after review
- **Help Pietro resolve conflicts if they occur**

**Branch Naming:**
```
feat/hunter-reroll-mechanics
fix/duplicate-rat-monster
refactor/equipment-activation
docs/pietro-yaml-guide
```

### Code Standards

**Required:**
- Type hints for all function signatures
- Docstrings with examples
- Dataclasses for structured data
- Comprehensive error messages (Pietro-friendly)
- Unit tests for new features

**Example:**
```python
def simulate_warrior_vs_monster(
    monster_name: str,
    *,
    seed: Optional[int] = None,
    max_bouts: int = 100,
) -> CombatResult:
    """
    Simulate combat between Warrior and a named monster.

    Args:
        monster_name: Name of monster from loaded monster pool
        seed: Random seed for reproducible results
        max_bouts: Maximum combat rounds before forcing tie

    Returns:
        CombatResult with complete bout-by-bout history

    Example:
        >>> result = simulate_warrior_vs_monster("Rat", seed=42)
        >>> result.winner
        'warrior'
    """
```

### Adding New Hero Classes

When Pietro wants to add a new hero:

1. **Pietro's Part (with Codex):**
   - Create hero YAML in `/rules/heroes/`
   - Add dice definitions to `/rules/_core/dice.yaml`

2. **Your Part (Giovanni):**
   - Implement combat simulation function in `combat_sim.py`
   - Add equipment activation logic (if custom equipment)
   - Write unit tests
   - Update CLI visualizer to support new hero

### Adding New Monster Types

**Pietro does:** Create YAML in `/rules/monsters/`

**Codex helps:** Guide through YAML structure, validate format

**You ensure:** Parser handles edge cases, simulations work

---

## Pietro Integration

### What Pietro Sees

**Pietro's View:**
1. Opens VSCode
2. Asks Codex: "Create a new monster called Bear"
3. Codex creates `/rules/monsters/bear.yaml` with guided questions
4. Pietro runs `python play_combat.py`
5. Selects "Warrior vs Bear"
6. Sees visual combat play out in CLI
7. Adjusts stats based on results

**What Pietro DOESN'T See:**
- Python code internals
- Stack traces (Codex shields him)
- Git merge conflicts (asks you)
- Engine errors (reports to you)

### When Pietro Needs You

**Pietro will ping you when:**
- CLI crashes with Python errors
- YAML validation fails mysteriously
- Git operations fail (merge conflicts)
- He wants to add completely new card types
- He wants the simulator to show different information
- Something that worked before suddenly breaks

**Your Response:**
1. Pull latest changes
2. Reproduce issue locally
3. Fix in feature branch
4. Test thoroughly
5. Push and tell Pietro to pull

---

## CLI Visualizer (play_combat.py)

### Purpose

- Pietro's primary testing tool
- Visual, game-terms-only interface
- No code visible
- Auto-reflects Pietro's card changes (zero maintenance)
- Codex can extend easily

### Implementation Requirements

**Must Use:**
- `rich` library for visual formatting
- Existing combat_sim.py functions (no engine changes)
- Clear phase separation (dice → equipment → combat)
- Game symbols: ■ (square), ▲ (triangle), ● (circle), 💀 (skull)

**Must Show:**
1. Hero/Monster health bars
2. Dice roll results (visual)
3. Equipment activation (which rules triggered)
4. Attack calculations (step-by-step)
5. Damage resolution (who wins, why)
6. Final result summary

**Must Support:**
- All current heroes (Warrior, Hunter, +5 more eventually)
- All monsters (28 currently, growing)
- Seed control (reproducible tests)
- Bout-by-bout playback (pause/advance)

### Extension Points for Codex

Make it easy for Codex to extend when Pietro asks:

```python
# Clear, documented functions Codex can modify

def display_bout(bout: BoutLog, hero_name: str):
    """Display a single combat bout visually."""
    # Codex can modify this to show more/less info
    pass

def format_dice_roll(faces: List[List[str]]) -> str:
    """Convert dice faces to visual symbols."""
    # Codex can add new symbols here
    pass

def show_equipment_activation(sword: EquipmentResult, shield: EquipmentResult):
    """Display which equipment rules fired."""
    # Codex can extend for new equipment
    pass
```

---

## Future Enhancements

### Short-term (Next 2-4 weeks)

- [ ] Fix duplicate Rat issue
- [ ] Implement all 7 hero simulations
- [ ] Add equipment system for other heroes
- [ ] Stage-level simulations (multi-combat runs)
- [ ] Balance reports (win rates, average bouts)

### Medium-term (1-3 months)

- [ ] Spell system implementation
- [ ] Boss battles
- [ ] Multi-player simulation (PvP)
- [ ] Statistical analysis tools
- [ ] Automated balance suggestions

### Long-term (3+ months)

- [ ] Web UI (if Pietro requests)
- [ ] API for external tools
- [ ] AI game balance assistant
- [ ] Replay system with branching (what-if scenarios)

---

## Common Tasks

### Task: Review Pietro's New Card

```bash
# Pull his changes
git pull origin main

# Validate YAML
python verify_monsters.py

# Test in simulator
python play_combat.py
# Select new monster, test vs all heroes

# Check balance
python -m engine.stage_sim simulations/scenarios/stage1_baseline.yaml

# If issues found, fix and push
git checkout -b fix/pietro-card-balance
# Make fixes
git commit -m "fix: Balance Pietro's new Bear monster"
git push origin fix/pietro-card-balance
# Then tell Pietro to pull
```

### Task: Add New Equipment Type

```python
# 1. Add to combat_sim.py
def _compute_new_weapon_options(attribute_pool: Dict[str, int]) -> List[EquipmentResult]:
    """Compute activation options for new weapon."""
    # Implementation here
    pass

# 2. Update choose_best_weapon_configuration
def choose_best_weapon_configuration(attribute_pool, weapon_type: str = "sword"):
    if weapon_type == "new_weapon":
        return _compute_new_weapon_options(attribute_pool)
    # ... existing logic

# 3. Add tests
def test_new_weapon_activation():
    # Test cases here
    pass

# 4. Update CLI visualizer
def show_equipment_activation(weapon, shield):
    if weapon.description.startswith("new_weapon"):
        # Special visualization
        pass
```

### Task: Debug Combat Logic Error

```bash
# 1. Get reproduction info from Pietro
#    - Which hero/monster?
#    - What seed?
#    - What seemed wrong?

# 2. Run with detailed logging
python detailed_sim_tests.py

# 3. Add targeted test
def test_pietro_reported_bug():
    result = simulate_warrior_vs_monster("Bear", seed=42)
    # Assert expected behavior
    assert result.bouts[0].hero_attack == 5

# 4. Fix, test, deploy
```

---

## Performance Considerations

### Current Performance

- Single combat: <10ms
- 100 combats: ~500ms
- 10,000 combat Monte Carlo: ~30-50 seconds

**Bottlenecks:**
- Random number generation (acceptable)
- Equipment activation logic (could optimize)
- Result logging (acceptable for debugging)

**Optimization Opportunities (if needed):**
- Cache dice probability calculations
- Vectorize Monte Carlo simulations
- Profile slow functions

---

## Debugging Tips

### When Pietro Reports "It's Broken"

1. **Reproduce locally:**
   ```bash
   git pull
   python play_combat.py
   # Try to see the issue
   ```

2. **Check recent changes:**
   ```bash
   git log --oneline -5
   git diff HEAD~1
   ```

3. **Validate data:**
   ```bash
   python verify_monsters.py
   python test_combat_system.py
   ```

4. **Check Pietro's last edit:**
   ```bash
   git log --all --full-history -- "rules/**"
   ```

### When Tests Fail

1. Read test output carefully
2. Check if it's a data issue (Pietro's YAML) or code issue
3. Fix data → tell Pietro
4. Fix code → test, push, tell Pietro to pull

---

## Security & Best Practices

### Git

- Never force push to main (Pietro might be working)
- Always pull before starting work
- Use descriptive commit messages
- Keep commits atomic (one logical change)

### Code

- Never commit secrets (.env, API keys)
- Validate all user inputs (Pietro's YAML)
- Handle errors gracefully (Pietro-friendly messages)
- Log important operations for debugging

### Data

- Backup Original files/ before major changes
- Version control everything
- Keep test data separate from production

---

## Documentation Maintenance

### When to Update This File

- New hero/equipment systems added
- Architecture changes
- New testing procedures
- Critical issues discovered
- Pietro's workflow changes

### When to Update AGENTS.md

- Pietro struggles with a concept
- New commands Pietro needs to know
- Codex gives bad advice (adjust guidelines)
- New game mechanics added

---

## Quick Reference

### File Locations
- Engine code: `/engine/*.py`
- Pietro's cards: `/rules/*/`
- Tests: `test_*.py`, `verify_*.py`
- CLI tool: `play_combat.py`
- Docs: `/docs/`

### Key Commands
```bash
# Testing
python test_combat_system.py
python verify_monsters.py
python play_combat.py

# Git
git pull origin main
git add .
git commit -m "..."
git push origin main

# Python
python -m pytest tests/
python -m engine.stage_sim <scenario>
```

### Contact Points
- Pietro issues with YAML → Codex first, then you if stuck
- Pietro issues with Git → You
- Pietro issues with CLI → You (unless Codex can fix easily)
- Game design questions → Pietro + Codex
- Technical decisions → You

---

## Philosophy

**Your Role:** Build robust systems that let Pietro be creative without technical barriers.

**Success Criteria:**
- Pietro can design and test cards independently
- Changes to game logic automatically reflected in CLI
- Minimal maintenance overhead for you
- Both AIs (Codex + Claude) work harmoniously via clear configuration

**Remember:**
- Pietro is the game designer - respect his domain
- You're the technical enabler - make tools that empower him
- Keep complexity hidden from Pietro, but documented here
- When in doubt, prioritize Pietro's ability to work independently

---

**Last Updated:** 2025-10-12
**Maintained by:** Giovanni (you) with Claude Code assistance
**Related Files:** AGENTS.md (Pietro's Codex guide), README.md (project overview)
