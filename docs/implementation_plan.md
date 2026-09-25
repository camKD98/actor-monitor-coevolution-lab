# Adversarial Oversight Proof of Concept

Build a research-grounded, laptop-friendly reinforcement-learning study that trains a task agent and a separate monitor, measuring whether learned oversight reduces specification gaming without excessive false alarms.

## Summary

The first experiment uses small neural policies trained from random initialization in a custom safety gridworld. This is genuine model training and is a cleaner proof of concept than training a language model because it isolates the oversight mechanism. A later stage can transfer the protocol to a fine-tuned open language model if the result is informative.

The scientific claim is deliberately narrower than “policing solves alignment”: **under defined observability and supervision assumptions, can a separately trained monitor reduce undetected rule-breaking by a reward-seeking policy while preserving useful task performance?** Recursive “police the police” experiments should begin only after the one-monitor baseline is sound.

## Implementation steps

1. **Research map and pre-registration questions**
   - Maintain `docs/research_agenda.md` with the hypothesis, related fields, falsifiable predictions, threat model, assumptions, and open questions.
   - Cover AI Safety Gridworlds, specification gaming, AI control, trusted/untrusted monitoring, debate, iterated amplification, recursive reward modelling, weak-to-strong monitoring, nested oversight, and collusion.

2. **Minimal reproducible Python project**
   - Use a small `src/alignment/` package with PyTorch, NumPy, pytest, and Ruff.
   - Provide deterministic seeding, typed configuration, CLI entry points, and ignored local output directories.
   - Keep CPU defaults modest while permitting later CUDA runs on the Windows PC.

3. **Transparent specification-gaming environment**
   - Provide an observable proxy objective, hidden ground-truth safety/performance measure, legitimate task completion, and tempting exploit action.
   - Keep oracle labels in the harness and out of task-agent inputs.
   - Test transitions, rewards, labels, termination, and reproducibility.

4. **Unmonitored task-agent baseline**
   - Train a compact policy/value network from random initialization against proxy reward.
   - Confirm that it reliably learns the intended exploit before evaluating oversight.
   - Record proxy return, true utility, violation rate, and exploit success.

5. **Separate learned monitor**
   - Let the monitor see declared public evidence: current state and proposed action.
   - Penalize false negatives and false positives.
   - Compare no monitor, always/never alarm, rule-based, learned, and oracle monitors.
   - Include intervention cost so blocking everything is not counted as success.

6. **Adaptive/adversarial evaluation**
   - First evaluate a frozen actor and monitor, then allow the actor to adapt to the monitor.
   - Later alternate actor and monitor updates.
   - Hold out layouts/exploit variants and run multiple random seeds.
   - Report the complete safety–usefulness tradeoff, calibration, and false interventions.

7. **Recursive extension**
   - Introduce monitor decision/audit traces for future meta-monitoring.
   - Test depths 0–3 only after a meaningful first-level failure model exists.
   - Compare independent/model-diverse monitors with shared architectures to measure correlated failure.

8. **Portfolio-quality report**
   - Generate the report from saved run data.
   - Separate exploratory from confirmatory tests, include negative findings, and avoid extrapolating toy results to frontier systems.

## Current files

- `README.md` — overview; setup section still needs completion.
- `docs/research_agenda.md` — completed initial literature map and research questions.
- `pyproject.toml` — package/dependency configuration.
- `src/alignment/config.py` — experiment configuration.
- `src/alignment/env.py` — gridworld and hidden evaluation oracle.
- `src/alignment/models.py` — actor-critic and monitor networks.
- `src/alignment/train_agent.py` — REINFORCE-style actor-critic training.
- `src/alignment/train_monitor.py` — data collection and supervised monitor training.
- `src/alignment/evaluate.py` — monitor controls and aggregate metrics.
- `src/alignment/cli.py` — baseline experiment and artifact output.
- `tests/` — environment, monitor, and smoke tests.

## Completed verification

- [x] Create a clean project-specific environment on the Windows PC and install with development dependencies.
- [x] Run Ruff and the complete pytest suite.
- [x] Run a short CPU smoke experiment.
- [x] Confirm fixed-seed reproducibility.
- [x] Confirm the default unmonitored agent reliably learns the exploit.
- [x] Confirm the oracle blocks violations and always-alarm destroys utility.
- [x] Measure learned-monitor precision, recall, false-positive rate, ROC-AUC, and calibration.
- [x] Add held-out variants and multi-seed aggregation (contextual and dual-track, 5 seeds each).
- [x] Implement monitor-aware actor training against frozen monitor.

## Phase 4: Alternating training and coevolution dynamics (CURRENT)

This is the primary next phase. The goal is to implement alternating actor-monitor training and characterize the dynamics.

### Implementation steps

1. **Alternating training loop** — implement a training loop that alternates:
   - Train actor for N episodes against frozen monitor
   - Retrain monitor on new actor behavior + historical data
   - Repeat for K rounds
   - Record per-round metrics: actor violation rate, monitor recall, threshold, evasion rate

2. **Dynamics sweep** — run alternating training across parameter variations:
   - Number of rounds (5, 10, 20, 50)
   - Episodes per round (100, 500, 1500)
   - Both environments (contextual + dual-track)
   - Multiple seeds per configuration

3. **Regime classification** — develop metrics to classify observed dynamics:
   - Convergence: metrics stabilize (violation rate, recall approach constants)
   - Cycling: metrics oscillate (actor evasion rate and monitor recall alternate)
   - Escape: actor violation rate monotonically increases while monitor recall decreases

4. **Environment structure variations** — test predictions by modifying:
   - Monitor observation (full state vs. partial vs. action-only)
   - Action space (add/remove actions to change mimicry capacity)
   - Information asymmetry (what the actor knows about monitoring)

## Phase 5: Formal analysis (PARALLEL)

Develop the game-theoretic formalization alongside the empirical work.

1. **Game model** — formalize the actor-monitor interaction as an extensive-form game with:
   - Actor: private type (intent), public actions, information set includes monitor existence
   - Monitor: observes actions and partial state, emits risk score
   - Intervention rule: threshold-based with investigation option
   - Payoffs: actor gets violation reward minus detection cost; monitor gets correct classification minus false alarm cost

2. **Equilibrium analysis** — characterize Nash equilibria:
   - When does a pure strategy equilibrium exist where all attacks are caught?
   - When do only mixed strategy equilibria exist (cycling)?
   - Under what conditions does no equilibrium exist (divergence)?

3. **Structural conditions** — derive conditions on environment parameters:
   - Monitoring coverage: fraction of attack paths distinguishable from legitimate paths
   - Mimicry capacity: whether observationally identical attack paths exist
   - Adaptation rate asymmetry: relative learning speed of actor vs. monitor

4. **Connection to existing theory** — relate results to:
   - Balcan et al. non-convergence in adversarial robustness games
   - Red Queen dynamics and arms race / trench warfare distinction
   - Thomson et al. AI-Control Games static equilibrium analysis

## Remaining development (deferred)

- [ ] Recursive oversight extension (only after dynamics characterization).
- [ ] Language-model transfer (only if formal analysis produces testable predictions at scale).
- [ ] Add regenerated plots/tables and a report.

## Contextual-escalation experiment

The completed gridworld is a mechanism-validation baseline, not the main research environment. The next experiment adds several comparably capable learned roles without assuming that one learned agent is inherently trusted:

1. A safety-penalized task actor trained to avoid known violations.
2. A proxy-reward task actor that may specification-game when a shortcut is useful.
3. A dedicated red-team actor with a back-loaded objective for reaching a prohibited outcome.
4. A police monitor trained on bounded public state and trajectory evidence from safety and red-team behavior.

The first implementation contains legitimate work, useful research, access escalation, a direct violation used during monitor training, and a separate exfiltration action omitted from monitor training for held-out evaluation. Legitimate collaboration and exfiltration share research/access/share preparation. A three-region police protocol can allow low-risk actions, block high-risk actions, or pay to investigate intermediate-risk actions. Investigation checks bounded authorization evidence—granted access, privileged mutation, external transfer, and elevated-scope authorization—without reading the hidden violation label. This remains a hand-coded evidence and adjudication channel, not a learned investigator.

At seed 17, block-only monitoring stops the known direct attack but misses the held-out exfiltration attack. Bounded investigation stops both at a measurable cost while preserving all evaluated legitimate completions. Confirmed violations quarantine the actor instead of permitting repeated retries. The role policies use explicit protocol pretraining and curriculum states, so red-team behavior is engineered rather than naturally emerging.

Red-team behavior is a source of adversarial training data, not evidence that deceptive alignment emerged naturally. Keep some attack families unavailable during monitor training so final evaluation measures generalization rather than repeated fitting to every discovered attack.

## Risks and interpretation

- The toy environment tests a control mechanism, not a general alignment solution.
- The oracle already knows which behavior is unsafe; this does not solve value specification.
- Recursive layers add no information if every monitor receives the same oracle-derived signal and has the same errors.
- Similar architectures and datasets can create correlated failures.
- A hierarchy cannot make failure probability literally zero without strong assumptions about independence, observability, and final adjudication.
