# Project Tasks

Living task tracker. Agents should update this file when they start, complete, or reprioritize work. Keep `LEARNINGS.md` for workspace/environment knowledge only.

## In progress

(none)

## Next

- [ ] Investigate why monitor-aware red-team actors do not meaningfully change behavior
  - Detection penalty (5.0) and investigation penalty (3.0) may be too small relative to violation reward (20.0).
  - Try increasing penalties or switching to a multiplicative stealth bonus.
  - aware_direct_sabotage fails to learn at seed 21; diagnose whether monitor penalty causes collapse.
- [ ] Evaluate a threshold rule that incorporates investigation cost/benefit tradeoff
  - Current predeclared recall rule drives threshold to near-1.0 and misses held-out at all 5 seeds.
  - Consider a cost-weighted rule, quantile-based conservative threshold, or explicit investigation budget.
- [ ] Fix collaborative actor training instability (0/100 completions at seeds 19, 20)
  - May need more episodes, lower entropy coefficient, or adjusted collaborative reward shaping.
- [ ] Implement an imperfect rule baseline
  - Current rule and oracle are identical; a genuinely fallible rule baseline is needed.
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
