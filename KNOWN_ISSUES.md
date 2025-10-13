# Known Issues & Fixes

## Issue #1: Phantom Monster Data (CRITICAL)

**Status:** Identified, fix available
**Impact:** All monsters after Rat are loading with wrong stats
**Priority:** HIGH - Fix before Pietro continues designing

### Problem

Lines 23-31 in `Original files/Monsters.txt` contain phantom/duplicate data that shouldn't exist. This causes all subsequent monsters to load with incorrect stats.

### Current Behavior (WRONG)

| Monster | Loaded Stats | Expected Stats |
|---------|--------------|----------------|
| Rat | HP=1 AR=1 ATK=2 ✓ | HP=1 AR=1 ATK=2 |
| Mush | HP=1 AR=0 ATK=1 ✗ | HP=1 AR=3 ATK=0 |
| Wolf | HP=1 AR=3 ATK=0 ✗ | HP=1 AR=2 ATK=2 |
| Hedge | HP=1 AR=2 ATK=2 ✗ | HP=1 AR=4 ATK=1 |

**The phantom data causes a cascading shift**: each monster loads the stats of the NEXT monster!

### Root Cause

`Original files/Monsters.txt` has duplicate data between Rat and Mush:

```
Line 21:    [tab]4G         ← Rat's loot
Line 22:    [tab]Rat        ← Rat's name
Lines 23-31: PHANTOM DATA   ← Should NOT exist!
Line 32:    [tab]Mush       ← Mush's name
Line 33:    [tab]1          ← ACTUAL Mush data starts here
```

The parser reads lines 23-31 as Mush's data (incorrect), then reads lines 33+ as Wolf's data (also incorrect), cascading the error.

### Fix

**Option A: Delete Phantom Lines** (Recommended)

Remove lines 23-31 from `Original files/Monsters.txt`:

```bash
# Make backup first
cp "Original files/Monsters.txt" "Original files/Monsters.txt.backup"

# Edit file and remove lines 23-31:
# [tab]1
# [tab]0
# [tab]1
# [tab]2
# [tab]2m
# [tab]1 sk = + 2Att
# 2sk = + 2Att
# OC=+1Att
# [tab]2G
```

After fix, structure should be:
```
Line 21:    [tab]4G         ← Rat's loot
Line 22:    [tab]Rat        ← Rat's name
Line 23:    [tab]Mush       ← Mush's name (formerly line 32)
Line 24:    [tab]1          ← Mush data starts (formerly line 33)
...
```

**Option B: Ask Pietro**

If Pietro intentionally added this data for a different monster variant:
1. Ask him what this monster should be named
2. Add the name at line 32 (between phantom data and "Mush")
3. Verify this creates the intended monster

### Verification

After applying fix, run:

```bash
python3 verify_monsters.py
```

Expected output:
```
✓ Mush: armor=3, attack=0 (was armor=0, attack=1)
✓ Wolf: armor=2, attack=2 (was armor=3, attack=0)
✓ All monsters loading with correct stats
```

### Git Workflow Note

- **If Pietro hasn't pushed yet:** Fix locally, commit, push
- **If Pietro has pushed:** Pull first, check if issue exists, then fix
- **After fix:** Both of you should `git pull` to get corrected file

---

## Issue #2: Special Abilities in Loot Field (MINOR)

**Status:** Documented, low priority
**Impact:** Loot values for 2 monsters are text instead of gold amounts
**Priority:** MEDIUM

### Affected Monsters

- **Imp**: Loot = "3 sk = escapes drop half G" (should be "4G" or similar)
- **Jaguar**: Loot = "OC attacker loses 1 G," (should be numeric)

### Impact

- CLI simulator shows text instead of loot amount
- Not breaking gameplay, just confusing display

### Fix

Update `engine/monster_loader.py` to:
1. Parse special effects from loot field
2. Extract numeric gold value
3. Store special effects separately in `Monster.special_effects`

### Workaround

For now, Pietro can ignore this - these monsters still work in simulations.

---

## Testing After Fixes

Run complete test suite:

```bash
# Validate all monsters
python3 verify_monsters.py

# Run combat tests
python3 test_combat_system.py

# Test in CLI simulator
python3 play_combat.py
# Select Warrior vs Mush
# Verify Mush has high armor (3) and low attack (0)
```

---

**Last Updated:** 2025-10-12
**Discovered By:** Giovanni + Claude Code during initial testing
