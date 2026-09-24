# Project Tasks

Living task tracker. Agents should update this file when they start, complete, or reprioritize work. Keep `LEARNINGS.md` for workspace/environment knowledge only.

## In progress

- [ ] Build the contextual-escalation experiment
  - First slice implemented: legitimate work/research, access escalation, direct override, and held-out exfiltration.
  - Separate proxy, safety-penalized, direct red-team, and exfiltration red-team policies now train independently.
  - The police trains only on safety/direct-red-team trajectories; exfiltration actions are excluded from its dataset.
  - Seed 17 result: both red-team policies execute 100/100 unmonitored violations. Block-only stops the known direct attack but misses 100/100 held-out exfiltration attacks; costly investigation stops both while preserving 100/100 completion for proxy, safety, and collaborative task policies.
  - Legitimate collaboration and exfiltration now share research/access/share preparation; role protocols use explicit supervised pretraining plus RL curriculum, so red-team behavior is engineered rather than emergent.
  - Bounded investigation now checks access scope, privileged mutation, and external-transfer evidence without reading the hidden violation label; confirmed violations quarantine the actor instead of allowing repeated retries.
  - Next: sweep police thresholds/costs to measure the intervention frontier, then run multiple seeds.
  - Preserve the completed gridworld as a mechanism-validation baseline.

## Next

- [ ] Add monitor classification metrics and calibration
  - Precision, recall, false-positive rate, ROC-AUC, calibration curve.
  - Select monitor threshold on a validation split before final evaluation.
- [ ] Implement an imperfect rule baseline
  - Current rule and oracle are identical; a genuinely fallible rule baseline is needed.
- [ ] Add held-out environment variants and multi-seed aggregation
  - Separate train/evaluation layouts or exploit positions.
  - Aggregate results across multiple seeds.
- [ ] Implement adaptive actor training against a frozen monitor
  - Train the actor while aware of the monitor; measure increased undetected violations.
- [ ] Implement alternating actor-monitor training
  - Update actor and monitor in rounds; test robustness on held-out variants.

## Backlog / later

- [ ] Recursive oversight extension (depth 1–3)
  - Only after the first-level monitor has a defined failure/corruption/information-limitation model.
  - Ensure higher layer has partially independent evidence channel.
- [ ] Save per-episode data and generate plots/tables
  - Do this only after the baseline is validated.
- [ ] Explicit CUDA / device selection
- [ ] Language-model transfer experiment
  - Only if earlier phases produce a clear question worth transferring.

## Completed

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
