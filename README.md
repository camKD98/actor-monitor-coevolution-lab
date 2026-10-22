# Actor–Monitor Coevolution Lab

A small, reproducible AI-control research project studying **when learned oversight keeps pace with adaptive agents**.

The project trains reward-seeking policies in a safety gridworld, trains separate monitors to detect unsafe actions, and then varies what the monitor can observe and remember. The central question is not simply whether a static monitor can catch a known attack, but whether alternating actor–monitor adaptation **converges to a safe equilibrium, cycles through repeated evasion and adaptation, or allows the actor to escape oversight**.

This is a controlled toy environment for studying oversight dynamics. It is not evidence that recursive monitoring solves alignment, and the results should not be read as claims about frontier AI systems.

The repository is under active development; the README and compact report summarize the canonical artifact-backed results, while exploratory variants and next steps are tracked in the research agenda and experiment ledger.

## Main result

The canonical experiments support a **structural account** of oversight dynamics: the outcome depends on what evidence the monitor can see, how much prior attack evidence it retains, and whether the attacker can switch to a family the monitor has not recently learned.

The canonical attacker is an idealized selector among three fixed attack policies; legitimate actors are evaluated separately.

### Monitor observation

| Monitor condition | Canonical result | Interpretation |
|---|---:|---|
| Full-state observation, fixed attack policies | Convergence at 5/5 seeds | The monitor sees the proposed action and all public state features, including `deployed` and `certified`, and learns a rule that catches all three attack families. |
| Partial-state observation, fixed attack policies | Cycling at 4/5 seeds; 1 indeterminate | Hiding `deployed` and `certified` removes the cue shared by all attack families. The monitor catches a selected attack after retraining, while the attacker switches family and can evade before the next update. |

Action-only and attack-capability-collapse variants test whether low violation counts reflect successful oversight rather than missing observational context or lost attack capability.

### Retained attack history

Under partial observation, the monitor retrains on the current attack batch, the last 2 batches, the last 3 batches, or all previous batches.

| Monitor retraining history | Evasion before update | Seed outcomes |
|---|---:|---|
| Current attack batch only | 43/60 | 4 cycling, 1 indeterminate |
| Last 2 attack batches | 24/60 | 2 convergence, 2 cycling, 1 indeterminate |
| Last 3 attack batches | 13/60 | 1 convergence, 4 indeterminate |
| All previous attack batches | 6/60 | 5 convergence |

![Canonical meta-selector summary](docs/figures/meta_selector_summary.svg)

The strongest current result is a controlled regime transition: with policies, thresholds, selector, monitor capacity, and classification criteria held fixed, changing monitor observability and attack memory changes the measured dynamics from convergence toward Red-Queen cycling.

## Documentation

- [Research agenda](docs/research_agenda.md): hypotheses, literature context, threat model, metrics, and interpretation rules.
- [Formal analysis](docs/formal_analysis.md): game-theoretic model and predicted convergence/cycling/escape conditions.
- [Experiment log](docs/experiment_log.md): canonical commands, commits, artifact hashes, quantitative results, and limitations.
- [Canonical meta-selector summary](docs/canonical_meta_summary.md): table generated directly from canonical `results.json` artifacts.
- [Implementation plan](docs/implementation_plan.md): development roadmap and completed verification.
- [Compact report](docs/report.md): short public-facing summary of the logged results.

`AGENTS.md`, `TASKS.md`, and `LEARNINGS.md` are development and reproducibility notes rather than primary report documents.

## Environments

The project includes three related experiment families:

1. **Baseline specification-gaming gridworld** — establishes that an unmonitored policy learns an exploit and that learned monitoring can block it while preserving legitimate task completion.
2. **Contextual-escalation environment** — introduces legitimate, proxy, safety, collaborative, and red-team roles with overlapping preparation paths and held-out attack families.
3. **Dual-track coevolution environment** — uses a shared dual-use `CONFIGURE` action whose safety depends on context. Three attack families share the final violating action but differ in prerequisite structure. Alternating actor–monitor experiments measure convergence, cycling, and escape.

## Quickstart

Use a project-local virtual environment on Windows.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

Run the baseline experiment:

```powershell
.\.venv\Scripts\alignment-lab.exe --output '.\runs\baseline'
```

Run a canonical-style partial-state coevolution experiment:

```powershell
.\.venv\Scripts\alignment-lab.exe `
    --experiment dual_track_meta_selector `
    --monitor-observation partial_state `
    --attack-memory-rounds 1 `
    --seed 17 `
    --rounds 12 `
    --actor-episodes 1500 `
    --monitor-episodes 500 `
    --output '.\runs\example-partial-state'
```

Raw run artifacts are intentionally kept under ignored `runs/` directories. Claim-relevant runs are recorded in `docs/experiment_log.md` with the Git commit, clean/dirty state, command, artifact SHA-256, configuration, results, and limitations.

## Interpretation rules

- Report attempted and executed violations separately.
- Report safety and usefulness together, including false positives and intervention costs.
- Keep hidden oracle labels out of actor and monitor inputs.
- Treat adversarial actors as engineered stress tests, not naturally emergent deception.
- Treat five adjacent seeds as a small seed sweep, not a universal guarantee.
- Do not describe toy-gridworld results as a general claim about frontier AI safety.

## Provenance and AI assistance

This repository was developed with AI coding assistance under human research direction. Canonical claims are tied to committed commands, clean-tree provenance, and hash-recorded artifacts in `docs/experiment_log.md`; exploratory results are labelled as such.

## License

Source code is released under the [MIT License](LICENSE). Documentation and reports under `docs/` are released under [CC BY 4.0](docs/LICENSE.md).
