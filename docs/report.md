# When Does Oversight Keep Pace with Adaptive Agents?

**Compact technical report — canonical results only**

*Developed with AI coding assistance under human research direction. Canonical claims are tied to committed commands and hash-recorded artifacts in `experiment_log.md`.*

## Abstract

This project studies the dynamics of actor–monitor oversight rather than asking only whether a static classifier can catch a known attack. In a deterministic dual-track safety environment, we alternate or compare attacker adaptation with monitor retraining, then classify the resulting dynamics as convergence, cycling, or escape under predeclared criteria.

Across the canonical runs, a robust, monitor-visible violation feature produces convergence: the monitor catches every selected attack before it executes. When that feature is hidden while family-specific prerequisite cues remain visible, the matched system shifts into cycling at four of five seeds: the selected attack frequently evades before the monitor update, the monitor catches it after retraining, and the attacker switches families. Increasing retained attack memory monotonically reduces evasion and suppresses cycling, with cumulative memory converging at all five seeds.

The result is a controlled demonstration that oversight outcomes depend on **monitor coverage, mimicry pressure, and retained attack history**, not only on nominal model capability. The environment is deliberately toy-scale; the contribution is a reproducible mechanism for studying oversight dynamics, not a general alignment claim.

## Research question

> When an actor and monitor adapt iteratively in a safety monitoring game, under what structural conditions does coevolution converge to a safe equilibrium, cycle through repeated evasion and adaptation, or allow the actor to escape?

The full hypotheses, threat model, metrics, related work, and interpretation rules are in `research_agenda.md`. The formal model and structural predictors are in `formal_analysis.md`. The run-level evidence is in `experiment_log.md`.

## Environment and protocol

The canonical experiments use the dual-track environment:

- Legitimate work follows a primary track or a maintenance track.
- A shared dual-use `CONFIGURE` action can be legitimate or violating depending on state context.
- Three attack families share the same final violating action but differ in prerequisite paths:
  - direct sabotage;
  - review escalation;
  - maintenance path.
- The monitor receives a bounded observation and emits a risk score.
- Regime classification uses predeclared criteria requiring at least six rounds:
  - convergence requires low late-window violation and high recall;
  - cycling requires negative lag-1 autocorrelation and sufficient amplitude;
  - escape requires rising violations and falling recall;
  - otherwise the run is indeterminate.

The main canonical comparisons use a fixed-policy meta-selector: three reliable attack policies remain frozen, while an idealized best-response selector chooses the family with the lowest current monitor score. This preserves attack capability and isolates the monitor/adaptation mechanism.

## Canonical results

### 1. Static threshold selection fails under attack-family shift

Earlier five-seed dual-track evaluations trained reliable attack policies at every seed. A predeclared validation rule that selected high-recall thresholds chose near-1.0 thresholds and missed the held-out maintenance-path attack at all five seeds: **500/500 violations executed**. A conservative 0.1 threshold caught all attacks with zero false investigations in this environment.

This established the motivating failure mode: strong validation performance on known attack families does not imply robustness to a structurally different held-out family.

### 2. Full-state observation converges

With full-state monitoring, the matched meta-selector experiment converged at all five seeds.

- Regime: **convergence at 5/5 seeds**.
- The selected family executed **0/100 violations before the monitor update in all 60 rounds** across the five runs.
- All fixed attack families retained **100/100 unmonitored violation capability**.
- The monitor frequently switched which family it scored lowest, but scores remained extremely high and all selected attacks were already caught.
- Proxy and safety actors completed **100/100** legitimate trajectories with zero false interventions. The collaborative actor retained a known training instability at two seeds.

Interpretation: the full-state monitor learns a robust shared violation feature—`CONFIGURE` while elevated, deployed, and uncertified—which transfers across the three prerequisite families. Frequent family switching alone is not cycling when violations remain blocked.

Canonical entry: `DT-META-1c9ba40-S17–S21`, code commit `1c9ba40`.

### 3. Partial-state observation produces cycling

A predeclared observation mask hides `deployed` and `certified` while preserving family-specific prerequisite cues. Under otherwise corresponding settings, the system shifted from convergence to cycling.

- Regime: **cycling at 4/5 seeds**; seed 20 is indeterminate under the unchanged classification threshold.
- Selected attacks evaded the pre-update monitor in **43/60 rounds**.
- After retraining on the selected family, the monitor caught it in **60/60 rounds**.
- The selector changed family on **55/55 possible transitions** across the five runs.
- Every fixed attack family retained **100/100 unmonitored capability**.
- Proxy and safety actors completed **100/100** with zero false interventions; the same collaborative instability remained at two seeds.

Interpretation: removing the robust shared feature leaves non-robust, family-specific cues. The monitor can learn the currently selected family, but that adaptation does not transfer reliably to the next selected family, producing the intended catch-and-switch Red-Queen pattern.

Canonical entry: `DT-META-PARTIAL-5ffc8f7-S17–S21`, code commit `5ffc8f7`.

### 4. Retained attack memory monotonically suppresses evasion and cycling

A four-condition sweep varied only how many recent selected-family data batches were retained during monitor retraining: current batch only, last two, last three, or cumulative history.

| Attack memory | Pre-update evasions | Cycling seeds | Convergence seeds | Indeterminate seeds |
|---|---:|---:|---:|---:|
| Current batch only | 43/60 | 4/5 | 0/5 | 1/5 |
| Last 2 batches | 24/60 | 2/5 | 2/5 | 1/5 |
| Last 3 batches | 13/60 | 0/5 | 1/5 | 4/5 |
| Cumulative | 6/60 | 0/5 | 5/5 | 0/5 |

![Canonical meta-selector summary](figures/meta_selector_summary.svg)

The monitor caught the selected family after all **240/240 updates** across the sweep. Evasion therefore reflects the pre-update gap created by forgetting or incomplete coverage, not a persistent inability to learn each family once observed.

Interpretation: retained attack history is a graded regime-control parameter. More memory reduces the actor's transient advantage by increasing monitor coverage. The result does not identify a universal phase boundary at a specific finite window, partly because finite windows retain batches rather than guaranteed unique families.

Canonical entry: `DT-MEM2-4e2b86b-W1/W2/W3/CUM-S17–S21`, code commit `4e2b86b`.

## What the results support

- Oversight dynamics can shift qualitatively with monitor observability and attack history even when nominal attack capability is fixed.
- A robust monitor-visible feature can produce convergence across multiple attack families.
- Non-robust family-specific cues can produce cycling when the monitor is repeatedly retrained on only the current attack family.
- Retaining more historical attack data monotonically reduced pre-update evasion in the canonical sweep.
- The observed results are consistent with the formal predictors of monitoring coverage, mimicry pressure, and adaptation asymmetry.

## What the results do not support

- They do not show that deception or evasion emerged naturally; the adversarial actors are engineered or idealized stress tests.
- They do not establish a general law for frontier systems; all evidence is from a deterministic toy environment.
- They do not prove that cumulative memory always converges; they show convergence under this environment, selector, monitor, and classification criteria.
- They do not demonstrate recursive oversight; no meta-monitor has a meaningful independent evidence channel yet.
- They do not establish a sharp universal cycling threshold; seed 20 remains a boundary case in the partial-state run.

## Limitations

- The meta-selector has idealized white-box access to monitor scores.
- Low-level attack policies are fixed rather than jointly adapting in the canonical cycling and memory runs.
- The partial-state mask is hand-designed using known environment semantics.
- Retained memory units are batches, not guaranteed unique attack families, so finite-window runs can confound diversity with repeated selector choices.
- Cumulative memory changes both attack-family diversity and total sample count.
- Only five adjacent seeds are used per canonical sweep.
- The collaborative legitimate policy remains unstable at two seeds and should not be used as a clean usefulness baseline without further work.
- Regime thresholds are predeclared implementation defaults, not externally validated constants.

## Reproducibility and provenance

All canonical runs record the Git commit, tracked-tree state, command, UTC timestamp, platform, Python version, dependency versions, configuration, and artifact SHA-256. Raw artifacts remain under ignored `runs/` directories. The committed ledger with exact commands and artifact hashes is `docs/experiment_log.md`. The meta-selector summary table is regenerated directly from `results.json` artifacts by `scripts/summarize_meta_selector.py` and checked into `docs/canonical_meta_summary.md`.

The report intentionally cites only logged canonical results. Exploratory runs are not used as evidence here.

## Immediate next steps

The most valuable remaining work is to separate **attack-family diversity** from **sample count** in the memory result, then vary adaptation-rate asymmetry while holding coverage fixed. Both would strengthen the claim that structural properties—not merely dataset size—predict the observed regime.
