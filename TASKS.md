# Project Tasks

Living task tracker. Agents should update this file when they start, complete, or reprioritize work. Keep `LEARNINGS.md` for workspace/environment knowledge only.

## In progress

- [ ] Add structurally diverse attack families and held-out variants
  - Current random validation is perfect on the known direct attack but fails to select a threshold that transfers to held-out exfiltration.
  - Add monitor-training attacks that vary action identity and escalation structure while retaining a separate final attack family.
  - Keep model selection and final held-out evaluation strictly separated.

## Next

- [ ] Implement an imperfect rule baseline
  - Current rule and oracle are identical; a genuinely fallible rule baseline is needed.
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
