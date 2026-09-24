# Project Tasks

Living task tracker. Agents should update this file when they start, complete, or reprioritize work. Keep `LEARNINGS.md` for workspace/environment knowledge only.

## In progress

- [ ] Fix the learned monitor so it is not degenerate
  - Problem: current monitor blocks every step, producing the same result as the oracle/rule monitor.
  - Fix monitor data collection/class balance so it distinguishes the actual violating action from preceding safe actions.
  - Re-run the default experiment and confirm a meaningful safety/usefulness trade-off.

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

- [x] Set up clean project-local Python environment on the new PC.
- [x] Install package with dev dependencies.
- [x] Run Ruff and full pytest suite (8 tests passing).
- [x] Run short CPU smoke experiment.
- [x] Run default baseline experiment.
- [x] Confirm fixed-seed reproducibility.
- [x] Confirm unmonitored actor reliably learns the exploit (100/100 evaluation episodes).
- [x] Confirm oracle blocks violations and always-alarm destroys utility.
