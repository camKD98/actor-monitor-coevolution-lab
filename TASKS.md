# Project Tasks

Living task tracker. Agents should update this file when they start, complete, or reprioritize work. Keep `LEARNINGS.md` for workspace/environment knowledge only.

## In progress

- Fixed-policy meta-selector cycling experiment implemented and verified (38 tests). It keeps
  reliable family policies frozen, selects the current monitor's lowest-scored family, and trains
  the monitor only on that family. A six-round smoke run switches family every round and classifies
  as cycling; maintenance evades before and is caught after updates in rounds 3 and 5. Next: commit
  and run the canonical 12-round, five-seed sweep before interpreting robustness.

## Next — Coevolution dynamics (primary research direction)

### A. Alternating training implementation (empirical, parallelizable)
- [x] Implement alternating actor-monitor training loop in the dual-track environment
  - Train actor for N episodes against frozen monitor → retrain monitor on new behavior → repeat K rounds
  - Record per-round metrics: actor violation rate, monitor recall, evasion rate, returns
  - Support configurable rounds, episodes-per-round, and which actor role to co-train
- [x] Run initial alternating training sweep (dual-track, seeds 17–21)
  - Start with 10 rounds, 500 episodes/round
  - Classify dynamics: does it converge, cycle, or allow escape?
- [ ] Run parameter sweeps varying rounds (5, 10, 20, 50) and episodes/round (100, 500, 1500)
- [ ] Run environment structure variations:
  - [x] Partial monitor observation (action-only vs. full state)
  - [x] Sequential attack-family rotation with current-family-only attack memory
  - Modified action space (add/remove actions to change mimicry capacity)
  - Varied information asymmetry

### C. Regime classification metrics (bridges A and B)
- [x] Define quantitative regime classification criteria
  - Convergence: per-round violation rate and recall variance below threshold for last N rounds
  - Cycling: autocorrelation of per-round metrics is significantly negative at lag 1
  - Escape: monotonic increase in actor violation rate over last N rounds
- [x] Validate regime classification on initial sweep data
  - Full-state runs classify as convergence; rotating runs remain indeterminate when actors lose attack capability.

## Backlog / lower priority

- [ ] Fix collaborative actor training instability (2/5 seeds fail)
- [ ] Investigate monitor-aware actor penalty scaling (currently too small to affect behavior)
- [ ] Implement an imperfect rule baseline
- [ ] Save per-episode data and generate plots/tables
- [ ] Recursive oversight extension (only after dynamics characterization)
- [ ] Language-model transfer (only if formal analysis produces testable predictions at scale)
- [ ] Explicit CUDA / device selection

## Completed

- [x] Formal game-theoretic analysis (B) — see `docs/formal_analysis.md`.
  - Static actor-monitor game formalized as an extensive-form / POSG game with private actor type and partial monitor observation.
  - Nash-equilibrium characterization: pure catch-all equilibrium exists iff attack and legitimate observable features are disjoint; mixed equilibria when they overlap or investigation costs bind.
  - Dynamic alternating training modeled as iterated best response; convergence/cycling/escape conditions tied to monitoring coverage, mimicry capacity, and adaptation-rate asymmetry.
  - Connections to Thomson et al. (2024), Balcan et al. (2023), Mertikopoulos et al. (2018), Dieckmann et al. (1995), Zhang (2025/2026).

- [x] Run five-seed dual-track evaluation (DT-adaa83f-S17–S21).
  - All three non-adaptive red-team families reliably learn their attacks (100/100 at all 5 seeds).
  - Predeclared recall rule selects near-1.0 thresholds; held-out maintenance-path evades at all 5 seeds (500/500).
  - Conservative threshold 0.1 catches all attacks with 0 false investigations on legitimate actors.
  - Monitor-aware actors do not meaningfully differ from non-adaptive actors.
  - Collaborative actor fails at 2/5 seeds; aware_direct_sabotage fails at 1/5 seeds.
- [x] Design and implement dual-track held-out variant with genuinely different escalation structure.
  - New `DualTrackEnv` with parallel primary (develop/test/deploy) and maintenance (review/patch/certify) tracks.
  - Shared dual-use `CONFIGURE` action: legitimate pre-deployment vs. violation post-deployment, depending on state context.
  - Three attack families share the same final action but differ in prerequisite chains: direct sabotage (tested path), review escalation (reviewed-only path), maintenance path (patched path).
  - Non-adaptive and monitor-aware red-team actors implemented as separate conditions.
  - Strict train → freeze → validation → test pipeline with predeclared threshold selection rule (≥95% validation recall, minimize legitimate investigations).
  - Legitimate actors traverse the same intermediate states (elevated, deployed) as attack actors.
  - 27 tests passing including 13 new tests for the dual-track environment.
- [x] Match validation support to frozen-policy deployment trajectories.
  - This reduces deletion deployment failure from 2/5 to 1/5 seeds but does not change held-out exfiltration failure (1/5 seeds).
  - Score-boundary sensitivity remains; do not tune a margin after inspecting final outcomes.
- [x] Add monitor classification metrics and validation-only threshold selection.
  - Validation precision, recall, and ROC-AUC are perfect across seeds 17–21, but selected thresholds miss held-out exfiltration at four of five seeds.
  - This negative result shows that random in-distribution validation is not evidence of attack-family generalization.
- [x] Build and evaluate the first contextual-escalation experiment.
  - Added proxy, safety, collaborative, direct-red-team, and held-out-exfiltration roles with overlapping preparation.
  - Added bounded authorization investigation, quarantine, provenance capture, and a threshold frontier.
  - Five-seed evaluation found material score instability: threshold 0.1 misses held-out exfiltration at one of five seeds, while block-only misses it at four of five.
  - The proxy actor independently learns the direct exploit at seed 20; safety and collaborative actors remain safe across all five seeds.
- [x] Fix the learned-monitor baseline and establish a safety/usefulness comparison.
  - Root cause: the monitor already separated the safe precursor from the violation, but the exploit-only actor repeatedly retried a blocked action.
  - Added an independently true-reward-trained fallback policy; its actions remain subject to the deployment-time monitor.
  - Corrected the hidden violation cost so violating is worse than a safe timeout and the fallback can learn the legitimate goal.
  - Default seed: no monitor executes 100/100 violations; always-alarm completes 0/100 goals; learned monitor blocks all 100 violations and completes 100/100 legitimate goals.
- [x] Set up clean project-local Python environment on the new PC.
- [x] Install package with dev dependencies.
- [x] Run Ruff and full pytest suite (8 tests passing).
- [x] Run short CPU smoke experiment.
- [x] Run default baseline experiment.
- [x] Confirm fixed-seed reproducibility.
- [x] Confirm unmonitored actor reliably learns the exploit (100/100 evaluation episodes).
- [x] Confirm oracle blocks violations and always-alarm destroys utility.
