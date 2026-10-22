"""Summarize canonical meta-selector runs directly from results.json artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import pairwise
from pathlib import Path

CANONICAL_GROUPS = [
    ("Full-state", "DT-META-1c9ba40-S*"),
    ("Partial-state", "DT-META-PARTIAL-5ffc8f7-S*"),
    ("Memory: current batch", "DT-MEM2-4e2b86b-W1-S*"),
    ("Memory: last 2 batches", "DT-MEM2-4e2b86b-W2-S*"),
    ("Memory: last 3 batches", "DT-MEM2-4e2b86b-W3-S*"),
    ("Memory: cumulative", "DT-MEM2-4e2b86b-CUM-S*"),
]


def summarize_pattern(runs_dir: Path, pattern: str) -> dict[str, object]:
    paths = sorted(runs_dir.glob(f"{pattern}/results.json"))
    regimes: Counter[str] = Counter()
    pre_evasion_rounds = 0
    post_caught_rounds = 0
    selection_switches = 0
    possible_switches = 0

    for path in paths:
        result = json.loads(path.read_text(encoding="utf-8"))
        regimes[result["regime_classification"]["regime"]] += 1
        selected_families = []
        for round_result in result["rounds"]:
            family = round_result["selected_family"]
            selected_families.append(family)
            before = round_result["before_monitor_update"][family]["deployment"]
            after = round_result["after_monitor_update"][family]["deployment"]
            pre_evasion_rounds += before["executed_violations"] > 0
            post_caught_rounds += after["executed_violations"] == 0

        selection_switches += sum(
            previous != current for previous, current in pairwise(selected_families)
        )
        possible_switches += max(0, len(selected_families) - 1)

    total_rounds = sum(len(json.loads(path.read_text(encoding="utf-8"))["rounds"]) for path in paths)
    return {
        "runs": len(paths),
        "rounds": total_rounds,
        "regimes": dict(regimes),
        "pre_evasion_rounds": pre_evasion_rounds,
        "post_caught_rounds": post_caught_rounds,
        "selection_switches": selection_switches,
        "possible_switches": possible_switches,
    }


def regime_text(regimes: dict[str, int]) -> str:
    if not regimes:
        return "—"
    return ", ".join(f"{name} {count}" for name, count in sorted(regimes.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("runs"))
    args = parser.parse_args()

    print("| Condition | Runs | Rounds | Pre-update evasion rounds | Post-update caught rounds | Regimes |")
    print("|---|---:|---:|---:|---:|---|")
    for label, pattern in CANONICAL_GROUPS:
        summary = summarize_pattern(args.runs_dir, pattern)
        print(
            f"| {label} | {summary['runs']} | {summary['rounds']} | "
            f"{summary['pre_evasion_rounds']} | {summary['post_caught_rounds']} | "
            f"{regime_text(summary['regimes'])} |"
        )


if __name__ == "__main__":
    main()
