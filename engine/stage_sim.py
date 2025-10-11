"""
Stage-level simulation utilities that chain multiple combats together to mimic
the flow of an entire stage. The current implementation focuses on the warrior
using the square sword and shield loadout against rank-based monster pools.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
import argparse
import random
from typing import Dict, List, Optional, Sequence

try:
    import yaml  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    raise ModuleNotFoundError(
        "Missing dependency 'pyyaml'. Install it with 'pip install pyyaml' before using stage simulations."
    ) from exc

from .combat_sim import DiceTables, simulate_warrior_vs_monster
from .monster_loader import Monster, get_monster_by_name, load_monsters


class StageScenarioError(ValueError):
    """Raised when a stage simulation scenario is malformed."""


@dataclass(frozen=True)
class MonsterStageStats:
    name: str
    faced: int = 0
    wins: int = 0
    losses: int = 0

    @property
    def win_rate(self) -> float:
        return self.wins / self.faced if self.faced else 0.0

    def record_win(self) -> "MonsterStageStats":
        return replace(self, faced=self.faced + 1, wins=self.wins + 1)

    def record_loss(self) -> "MonsterStageStats":
        return replace(self, faced=self.faced + 1, losses=self.losses + 1)


@dataclass(frozen=True)
class StageScenario:
    name: str
    description: str
    hero_class: str
    fights_per_run: int
    iterations: int
    seed: Optional[int]
    monsters: Sequence[Monster]
    source_path: Optional[Path] = None


@dataclass
class StageSimulationResult:
    scenario: StageScenario
    stage_wins: int
    monsters_cleared: List[int]
    monster_stats: Dict[str, MonsterStageStats]

    @property
    def success_rate(self) -> float:
        return self.stage_wins / self.scenario.iterations if self.scenario.iterations else 0.0

    @property
    def average_monsters_cleared(self) -> float:
        if not self.monsters_cleared:
            return 0.0
        return sum(self.monsters_cleared) / len(self.monsters_cleared)

    @property
    def cleared_distribution(self) -> Dict[int, int]:
        return dict(Counter(self.monsters_cleared))

    def top_threats(self, limit: int = 5) -> List[MonsterStageStats]:
        stats = [entry for entry in self.monster_stats.values() if entry.faced]
        return sorted(stats, key=lambda entry: (entry.losses, -entry.win_rate), reverse=True)[:limit]

    def format_summary(self) -> str:
        lines: List[str] = []
        lines.append(
            f"{self.scenario.name} — {self.scenario.iterations} runs, "
            f"{self.scenario.fights_per_run} fights/run ({self.success_rate * 100:.1f}% clears)"
        )
        lines.append(f"Average monsters cleared: {self.average_monsters_cleared:.2f}")

        distribution = self.cleared_distribution
        if distribution:
            dist_parts = ", ".join(f"{cleared}:{count}" for cleared, count in sorted(distribution.items()))
            lines.append(f"Clears distribution (monsters defeated per run): {dist_parts}")

        threats = self.top_threats()
        if threats:
            lines.append("Top threats (most stage-ending losses):")
            for stat in threats:
                lines.append(
                    f"  - {stat.name}: faced {stat.faced}, win rate {stat.win_rate * 100:.1f}%, "
                    f"losses {stat.losses}"
                )

        total_fights = sum(stat.faced for stat in self.monster_stats.values())
        lines.append(f"Total combats simulated: {total_fights}")
        return "\n".join(lines)


def _validate_positive_int(value: object, field_name: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise StageScenarioError(f"Field '{field_name}' must be a positive integer.")
    return value


def _resolve_monster_pool(
    monsters: Sequence[Monster],
    *,
    names: Optional[Sequence[str]],
    rank: Optional[int],
) -> List[Monster]:
    if names:
        resolved: List[Monster] = []
        for name in names:
            resolved.append(get_monster_by_name(name, list(monsters)))
        return resolved

    if rank is None:
        raise StageScenarioError("Stage configuration must provide either 'monsters' or 'monster_rank'.")

    pool = [monster for monster in monsters if monster.rank == rank]
    if not pool:
        raise StageScenarioError(f"No monsters found for rank {rank}.")
    return pool


def load_stage_scenario(path: Path) -> StageScenario:
    if not path.exists():
        raise FileNotFoundError(f"Stage scenario file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise StageScenarioError("Scenario file must contain a mapping at the top level.")

    name = str(data.get("name") or path.stem)
    description = str(data.get("description") or "")

    hero_section = data.get("hero") or {}
    if not isinstance(hero_section, dict):
        raise StageScenarioError("Field 'hero' must be a mapping.")

    hero_class = str(hero_section.get("class") or "warrior").lower()
    if hero_class != "warrior":
        raise StageScenarioError("Stage simulation currently supports only the warrior hero.")

    stage_section = data.get("stage") or {}
    if not isinstance(stage_section, dict):
        raise StageScenarioError("Field 'stage' must be a mapping.")

    fights_per_run = _validate_positive_int(stage_section.get("fights_per_run", 6), "stage.fights_per_run")

    iterations_value = data.get("iterations", 100)
    iterations = _validate_positive_int(iterations_value, "iterations")

    seed_raw = data.get("seed")
    seed: Optional[int]
    if seed_raw is None:
        seed = None
    else:
        if not isinstance(seed_raw, int):
            raise StageScenarioError("Field 'seed' must be an integer if provided.")
        seed = seed_raw

    monsters_dataset = load_monsters()
    monster_names_raw = stage_section.get("monsters")
    if monster_names_raw is not None:
        if not isinstance(monster_names_raw, list):
            raise StageScenarioError("Field 'stage.monsters' must be a list of monster names.")
        monster_names: Optional[List[str]] = [str(name) for name in monster_names_raw]
    else:
        monster_names = None

    monster_rank = stage_section.get("monster_rank")
    if monster_rank is not None and not isinstance(monster_rank, int):
        raise StageScenarioError("Field 'stage.monster_rank' must be an integer.")

    monster_pool = _resolve_monster_pool(
        monsters_dataset,
        names=monster_names,
        rank=monster_rank,
    )

    return StageScenario(
        name=name,
        description=description,
        hero_class=hero_class,
        fights_per_run=fights_per_run,
        iterations=iterations,
        seed=seed,
        monsters=tuple(monster_pool),
        source_path=path,
    )


def simulate_stage(scenario: StageScenario) -> StageSimulationResult:
    rng = random.Random(scenario.seed)
    dice_tables = DiceTables.from_loader()
    stats = {monster.name: MonsterStageStats(name=monster.name) for monster in scenario.monsters}

    stage_wins = 0
    monsters_cleared: List[int] = []

    for _ in range(scenario.iterations):
        cleared = 0
        stage_success = True
        # Allow repeats to account for reshuffles during a stage.
        sequence = rng.choices(scenario.monsters, k=scenario.fights_per_run)

        for monster in sequence:
            combat_seed = rng.randint(0, 2**32 - 1)
            combat = simulate_warrior_vs_monster(
                monster.name,
                seed=combat_seed,
                max_bouts=80,
                dice_tables=dice_tables,
                monsters=scenario.monsters,
            )
            current_stats = stats[monster.name]

            if combat.winner == "Warrior":
                stats[monster.name] = current_stats.record_win()
                cleared += 1
            else:
                stats[monster.name] = current_stats.record_loss()
                stage_success = False
                break

        if stage_success:
            stage_wins += 1

        monsters_cleared.append(cleared)

    return StageSimulationResult(
        scenario=scenario,
        stage_wins=stage_wins,
        monsters_cleared=monsters_cleared,
        monster_stats=stats,
    )


def run_stage_scenario(
    scenario: StageScenario,
    *,
    iterations: Optional[int] = None,
    fights_per_run: Optional[int] = None,
    seed: Optional[int] = None,
) -> StageSimulationResult:
    effective = scenario
    if iterations is not None or fights_per_run is not None or seed is not None:
        effective = replace(
            scenario,
            iterations=iterations if iterations is not None else scenario.iterations,
            fights_per_run=fights_per_run if fights_per_run is not None else scenario.fights_per_run,
            seed=seed if seed is not None else scenario.seed,
        )
    return simulate_stage(effective)


def _default_scenario_path() -> Path:
    return Path("simulations") / "scenarios" / "stage1_baseline.yaml"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run a stage-level simulation scenario.")
    parser.add_argument(
        "scenario",
        nargs="?",
        default=str(_default_scenario_path()),
        help="Path to the scenario YAML file (default: simulations/scenarios/stage1_baseline.yaml)",
    )
    parser.add_argument("--iterations", type=int, help="Override the iteration count.")
    parser.add_argument("--fights", type=int, help="Override fights per run.")
    parser.add_argument("--seed", type=int, help="Override the random seed.")
    args = parser.parse_args(argv)

    scenario_path = Path(args.scenario)
    scenario = load_stage_scenario(scenario_path)
    result = run_stage_scenario(
        scenario,
        iterations=args.iterations,
        fights_per_run=args.fights,
        seed=args.seed,
    )

    print(result.format_summary())
    return 0


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())
