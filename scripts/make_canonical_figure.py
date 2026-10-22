"""Generate a compact SVG summary of canonical meta-selector memory results."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from html import escape
from pathlib import Path

GROUPS = [
    ("Current attack batch only", "DT-MEM2-4e2b86b-W1-S*"),
    ("Last 2 attack batches", "DT-MEM2-4e2b86b-W2-S*"),
    ("Last 3 attack batches", "DT-MEM2-4e2b86b-W3-S*"),
    ("All previous attack batches", "DT-MEM2-4e2b86b-CUM-S*"),
]

REGIME_COLORS = {
    "convergence": "#2b8a3e",
    "cycling": "#e67700",
    "escape": "#c92a2a",
    "indeterminate": "#868e96",
}


def summarize(pattern: str, runs_dir: Path) -> dict[str, object]:
    paths = sorted(runs_dir.glob(f"{pattern}/results.json"))
    regimes: Counter[str] = Counter()
    rounds = 0
    pre_evasion_rounds = 0
    post_caught_rounds = 0

    for path in paths:
        result = json.loads(path.read_text(encoding="utf-8"))
        regimes[result["regime_classification"]["regime"]] += 1
        for round_result in result["rounds"]:
            rounds += 1
            family = round_result["selected_family"]
            before = round_result["before_monitor_update"][family]["deployment"]
            after = round_result["after_monitor_update"][family]["deployment"]
            pre_evasion_rounds += before["executed_violations"] > 0
            post_caught_rounds += after["executed_violations"] == 0

    return {
        "runs": len(paths),
        "rounds": rounds,
        "regimes": regimes,
        "pre_evasion_rounds": pre_evasion_rounds,
        "post_caught_rounds": post_caught_rounds,
    }


def text(x: float, y: float, value: str, size: int = 12, anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
        f'text-anchor="{anchor}" fill="#212529">{escape(value)}</text>'
    )


def make_svg(summaries: list[tuple[str, dict[str, object]]]) -> str:
    width = 1020
    left = 245
    outcome_left = 625
    evasion_scale = 5.0
    seed_scale = 38.0
    top = 105
    row_height = 45
    height = top + row_height * len(summaries) + 95

    elements = [
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        text(40, 38, "Retaining more attack history reduced evasion", 22),
        text(
            40,
            62,
            "Partial-state monitor; 5 seeds × 12 rounds per memory condition",
            13,
        ),
        text(40, 91, "Monitor retraining history", 13),
        text(left, 91, "Evasion rounds before retraining", 13),
        text(outcome_left, 91, "Seed outcomes", 13),
    ]

    for tick in (0, 30, 60):
        x = left + tick * evasion_scale
        elements.extend(
            [
                (
                    f'<line x1="{x}" y1="{top - 12}" x2="{x}" '
                    f'y2="{top + row_height * len(summaries)}" stroke="#dee2e6"/>'
                ),
                text(x, top + row_height * len(summaries) + 18, str(tick), 11, "middle"),
            ]
        )

    for index, (label, summary) in enumerate(summaries):
        y = top + index * row_height
        evasions = int(summary["pre_evasion_rounds"])
        bar_width = evasions * evasion_scale
        elements.extend(
            [
                text(40, y + 19, label, 12),
                f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="24" fill="#1c7ed6"/>',
                text(left + bar_width + 7, y + 17, f"{evasions}/60", 12),
            ]
        )

        x = outcome_left
        for regime in ("convergence", "cycling", "indeterminate", "escape"):
            count = summary["regimes"].get(regime, 0)
            if count == 0:
                continue
            segment_width = count * seed_scale
            elements.extend(
                [
                    (
                        f'<rect x="{x:.1f}" y="{y}" width="{segment_width:.1f}" height="24" '
                        f'fill="{REGIME_COLORS[regime]}"/>'
                    ),
                    (
                        f'<text x="{x + segment_width / 2:.1f}" y="{y + 16:.1f}" font-size="11" '
                        'text-anchor="middle" fill="#ffffff">'
                        f"{count}</text>"
                    ),
                ]
            )
            x += segment_width

    legend_y = top + row_height * len(summaries) + 48
    legend_x = outcome_left
    for regime in ("convergence", "cycling", "indeterminate", "escape"):
        elements.extend(
            [
                (
                    f'<rect x="{legend_x}" y="{legend_y - 11}" width="12" height="12" '
                    f'fill="{REGIME_COLORS[regime]}"/>'
                ),
                text(legend_x + 17, legend_y, regime, 11),
            ]
        )
        legend_x += 95

    elements.extend(
        [
            text(
                40,
                height - 38,
                "All selected attack families were caught after monitor retraining in every round.",
                11,
            ),
            text(
                40,
                height - 20,
                "Generated from canonical results.json artifacts by scripts/make_canonical_figure.py.",
                10,
            ),
        ]
    )

    svg_header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Retaining more attack history reduced evasion">\n'
    )
    return svg_header + "\n".join(elements) + "\n</svg>\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("runs"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/figures/meta_selector_summary.svg"),
    )
    args = parser.parse_args()

    summaries = [(label, summarize(pattern, args.runs_dir)) for label, pattern in GROUPS]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(make_svg(summaries), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
