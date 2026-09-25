# Project Tasks

Living task tracker. Agents should update this file when they start, complete, or reprioritize work. Keep `LEARNINGS.md` for workspace/environment knowledge only.

## In progress

- [ ] Add monitor classification metrics and calibration
  - Implemented stratified train/validation splitting and outcome-based frontier accounting.
  - Implemented precision, recall, false-positive rate, ROC-AUC, Brier score, confusion matrix, and calibration bins.
  - Implemented validation-only investigation-threshold selection with explicit missed-violation and investigation costs.
  - Next: commit, run canonical multi-seed evaluation, and assess held-out performance without retuning.

## Next

- [ ] Implement an imperfect rule baseline
  - Current rule and oracle are identical; a genuinely fallible rule baseline is needed.
- [ ] Add held-out environment variants
  - Separate train/evaluation layouts or escalation structures beyond the held-out action.
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
