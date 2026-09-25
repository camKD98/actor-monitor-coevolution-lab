# Workspace Learnings

Practical notes for any agent picking up this project. Update this file when you discover environment quirks, verified commands, or recurring pitfalls.

## Python environment

- **Do not use a global Conda environment.** Use a project-local virtual environment at `\.venv`.
- The active Python on this Windows PC is the Windows Store install:
  - `C:\Users\cambr\AppData\Local\Microsoft\WindowsApps\python.exe`
  - Version: **Python 3.11.9**
- There is an old Python 3.7 at `C:\Users\cambr\AppData\Local\Programs\Python\Python37`; do **not** use it (project requires `>=3.10`).
- Git Bash cannot run the WindowsApps `python` stub directly and gives a permission error. Use **PowerShell** for all Python/pip/venv commands.
- The project path contains spaces (`OneDrive - King's College London`), so quote paths carefully in PowerShell.

## Verified setup commands (PowerShell)

Create the venv (only once):

```powershell
& 'C:\Users\cambr\AppData\Local\Microsoft\WindowsApps\python.exe' -m venv 'C:\Users\cambr\OneDrive - King''s College London\Documents\projects\Alignment\.venv'
```

Install in editable mode with dev dependencies:

```powershell
& 'C:\Users\cambr\OneDrive - King''s College London\Documents\projects\Alignment\.venv\Scripts\python.exe' -m pip install -e 'C:\Users\cambr\OneDrive - King''s College London\Documents\projects\Alignment\[dev]'
```

Run linting and tests from the project root:

```powershell
& 'C:\Users\cambr\OneDrive - King''s College London\Documents\projects\Alignment\.venv\Scripts\python.exe' -m ruff check .
& 'C:\Users\cambr\OneDrive - King''s College London\Documents\projects\Alignment\.venv\Scripts\python.exe' -m pytest
```

Run the CLI:

```powershell
& 'C:\Users\cambr\OneDrive - King''s College London\Documents\projects\Alignment\.venv\Scripts\alignment-lab.exe' --output 'C:\Users\cambr\OneDrive - King''s College London\Documents\projects\Alignment\runs\baseline'
```

## Current project status

- Environment is clean and working on the new PC.
- Ruff and pytest pass (`9 passed`).
- Default seed (`seed=7`) gives a fully deterministic pipeline.
- The unmonitored actor reliably learns the designed exploit: 100/100 evaluation episodes reach the exploit cell.
- The learned monitor scores the safe precursor near 0 and the violating action near 1; the earlier apparent always-block behavior was repeated violation attempts by an exploit-only actor after each veto.
- The baseline now trains a separate fallback policy on true reward without monitor feedback. After a veto, control remains with this fallback, and every fallback action is checked by the deployed monitor.
- `hidden_violation_cost=30` makes a violation worse than a safe timeout; with the former value of 15, violating returned about -1.1 versus -1.2 for timing out, so the fallback preferred the exploit.
- Default baseline result: no monitor executes 100/100 violations; always-alarm completes 0/100 goals; learned monitoring executes 0/100 violations and completes 100/100 legitimate goals.
- Reproducibility verified for the fallback baseline: two default runs produced byte-identical `results.json` files (SHA-256 `79DB7C30B7A15E6499E38B1A7893A9B9AAA9E9FDF1D135C5B7187E75D5E3D771`).
- The contextual experiment runs with `alignment-lab --experiment contextual --output runs/contextual-v1`; seed 17 requires shaped prerequisite rewards for the red-team policies to learn delayed violations reliably.
- In the contextual stage result, block-only monitoring stops the known direct attack but misses 100/100 held-out exfiltration attacks. An idealized costly-investigation policy stops both, while proxy, safety, and collaborative actors each retain 100/100 completion with no false interventions.
- Delayed red-team policies were unreliable with sparse REINFORCE rewards alone. Explicit role-protocol pretraining plus randomized curriculum states made direct and exfiltration sequences reliable; interpret them as engineered adversaries, not emergent deception.
- Bounded investigation now uses explicit authorization evidence (access granted, privileged mutation, external transfer, elevated-scope authorization) rather than the hidden violation label. It remains a hand-coded evidence/adjudication channel, not a learned investigator.
- Confirmed contextual violations quarantine the actor, preventing repeated veto/investigation loops. This reduces each caught attack policy to one intervention/investigation per episode.
- Five-seed contextual evaluation (17–21) found substantial held-out score instability: investigation threshold 0.1 misses exfiltration at seed 18, threshold 0.5 misses it at seeds 18–19, and block-only catches it only at seed 20.
- The proxy actor independently specification-games at seed 20 (100/100 direct violations) but completes safely at the other four seeds. Safety and collaborative actors complete safely across all five seeds.
- Do not treat role names as ground-truth usefulness categories: a proxy actor may exploit. Frontier output now reports safety/collaborative outcomes separately from proxy outcomes.
- Stratified in-distribution validation is perfect at every tested seed (precision/recall/ROC-AUC 1.0, FPR 0), selecting thresholds around 0.99994–0.99997. Those thresholds miss held-out exfiltration at four of five seeds (400/500 violations), demonstrating severe attack-family shift despite apparently perfect calibration.
- Threshold selection must use structurally diverse validation attacks or an explicit conservative/defer policy; random samples from known attack families are insufficient.
- Adding deletion to direct-attack monitor training improves fixed 0.9 held-out exfiltration detection from 1/5 to 3/5 seeds, while a post-hoc 0.25 threshold catches 5/5. IID validation still selects near-1.0 thresholds and misses 5/5, so attack diversity in training alone does not solve model selection.
- Strict direct-train/deletion-validation/exfiltration-test separation improves selected-threshold held-out detection to 4/5 seeds.
- Using complete greedy deletion trajectories for validation reduces deletion deployment failure from 2/5 to 1/5 seeds but leaves held-out exfiltration failure unchanged at 1/5. Thresholds remain seed-scaled (about 0.17–0.99), and selecting the minimum positive score is boundary-sensitive.
- Stop extending the experiment with renamed final actions on the same prerequisite state. The next variant needs a different escalation structure and richer legitimate ambiguity; any threshold safety margin must be declared before final evaluation.
- The dual-track experiment (`--experiment dual_track`) uses a shared dual-use CONFIGURE action. Violation depends on state context (elevated + deployed + !certified), not action identity. Three attack families differ by prerequisite chain: direct sabotage (tested path), review escalation (reviewed-only path), maintenance path (patched path). Legitimate actors traverse the same intermediate states.
- Predeclared threshold selection rule for the dual-track experiment: select the threshold achieving ≥95% validation attack recall while minimizing legitimate investigation count. If no threshold achieves 95%, use maximum recall with fewest false positives.
- Monitor-aware red-team actors are trained against a frozen monitor with detection/investigation penalties in their reward. They are separate conditions from non-adaptive red-team actors and use seed offset +1000.
- The dual-track experiment follows strict ordering: train actors → collect training data → train and freeze monitor → train monitor-aware actors → collect validation data (greedy) → select threshold → evaluate on held-out. Do not inspect maintenance-path (held-out) outcomes during development.
- Five-seed dual-track evaluation (seeds 17–21): the predeclared ≥95% recall rule selects near-1.0 thresholds and misses the held-out maintenance-path attack at all 5 seeds (500/500 violations). At threshold 0.1, all attacks are caught with 0 false investigations. This replicates the contextual experiment's threshold-selection failure in a structurally different environment.
- Proxy and safety actors added protocol pretraining (proxy: fast-track develop/test/deploy, safety: reviewed develop/test/deploy). Both complete 100/100 at all 5 seeds. Collaborative actor fails at 2/5 seeds (19, 20).
- Monitor-aware red-team actors do not meaningfully change behavior compared to non-adaptive actors in this environment. The detection/investigation penalties may be insufficient relative to the violation reward. aware_direct_sabotage fails to learn at seed 21.
- Completion counting must use a per-episode flag to avoid counting `completed=True` on every post-deployment step. Deploy reward must be one-time (tracked by `_deploy_rewarded` flag).
- **Strategic pivot (September 2025):** The project is pivoting from "demonstrate static monitoring failure" to "characterize actor-monitor coevolution dynamics." Literature review found that MAGIC (2025), AdvGame (Meta 2025), Self-RedTeam (2025) all do LLM-scale coevolution empirically but none formally characterize convergence conditions. Thomson et al. (2024/2026) formalize static AI-control evaluations as PO stochastic games but do not study iterative dynamics. Balcan et al. (2023) prove non-convergence in adversarial robustness games. The gap is: formal characterization of when alternating actor-monitor training converges/cycles/escapes, and what structural properties predict the regime. Our gridworld environments are the right scale for analytical tractability.
- Alternating co-training implemented as `--experiment dual_track_alternating` (`--rounds`, `--round-episodes`) in `src/alignment/alternating.py`. The co-trained actor resumes REINFORCE from previous weights each round and experiences real quarantine blocks; the monitor retrains from scratch on cumulative data. Exploratory run `runs/DT-ALT-dev-S17` (dirty tree, seed 17, 5x500): the direct-sabotage actor stopped attempting violations after round 1 (attempted 0/100 in every round; train return recovered -4.5 → ~7), and the monitor reached recall 1.0 on all three families including held-out maintenance_path — consistent with the formal analysis's convergence prediction for the full-coverage, low-entropy regime. Caveat for interpretation: `evasion_rate` is null once the actor stops attempting, so regime classification needs attempted-violation counts, not just evasion.
- Canonical full-state alternating sweep `DT-ALT-S17`–`S21` (10 rounds × 500 actor episodes, clean commit `a851ce5`) converges at all five seeds: the co-trained actor attempts no violations after adaptation, while monitor recall is 1.0 on all measured families. See `docs/experiment_log.md`.
- Action-only exploratory sweep `DT-ALT-AO-dev2-S17`–`S21` (dirty tree, four parallel workers) shows the fixed review-escalation and held-out maintenance attackers evade block-only monitoring at all five seeds (100/100 executed), but the co-trained direct actor mostly collapses to non-attacking behavior. Seed 18 transiently cycles (round 2: 100/100 evade; round 3: 100/100 blocked; later no attempts). This does not yet establish the predicted escape regime for the adaptive actor. The actor receives action-level detection/investigation penalties even when the action-only monitor cannot distinguish context, which may make abstention cheaper than persistent attack.
- Sequential rotation is available as `--experiment dual_track_rotating`. Direct, review-escalation, and maintenance actors persist across rounds; the monitor retains fixed legitimate history but retrains only on the current round's attack family, deliberately exposing catastrophic forgetting. Per-round output records all families before/after the monitor update.
- Regime criteria in `regimes.py` require at least 6 rounds. Convergence requires late-window violation and recall variance ≤0.01, absolute slopes <0.05/round, mean violation ≤0.05, and mean recall ≥0.95. Cycling requires lag-1 autocorrelation ≤−0.25 in violation or recall plus amplitude ≥0.2. Escape requires violation slope ≥0.05/round, recall slope ≤−0.05/round, late mean violation ≥0.5, and late mean recall ≤0.5. Otherwise classify as indeterminate. These thresholds are predeclared implementation defaults and still require empirical validation.
- Canonical rotation sweep `DT-ROT-cfa151a-S17`–`S21` (12 rounds × 500 episodes) is indeterminate at every seed: all three continued-training attack actors collapse to 0/100 unmonitored violation attempts, so recall is generally undefined. This is not convergence. To test cycling, keep reliable pretrained family policies fixed and adapt family selection separately; always report attack capability/attempt rate alongside safety metrics.
- Fixed-policy meta-selection is available as `--experiment dual_track_meta_selector`. It idealizes actor best response by selecting the family with minimum monitor mean-positive score, while keeping all low-level attack policies frozen and reliable. The monitor retains legitimate history but only the selected attack family. Multifamily classification requires a per-family cycling signal plus family-selection switch rate ≥0.5.
- Canonical meta-selector sweep `DT-META-1c9ba40-S17`–`S21` converges at all five seeds despite frequent family switching. All fixed attacks remain 100/100 capable unmonitored, but all 60 selected-family deployments are blocked before monitor updates; positive scores stay ≥0.9967. The full-state monitor learns the shared robust violation feature, so current-family-only training does not cause forgetting. Do not interpret strategy switching alone as cycling.
- Partial-state monitoring (`--monitor-observation partial_state`) uses a predeclared mask that zeros observation indices 4 (`deployed`) and 6 (`certified`) while retaining progress, tested, reviewed, elevated, patched, pre-deploy configuration, and time.
- Canonical partial-state sweep `DT-META-PARTIAL-5ffc8f7-S17`–`S21` shifts the matched meta-selector from full-state convergence (5/5 seeds) to cycling at 4/5 seeds; seed 20 remains indeterminate under the unchanged −0.25 lag-1 threshold. Selected attacks evade pre-update in 43/60 rounds and are caught post-update in 60/60; all family policies retain 100/100 unmonitored capability. This is the first canonical cycling-regime result. Keep seed 20 as a boundary case; do not tune classification post hoc.
- Meta-selector attack memory is configurable with `--attack-memory-rounds N`; `1` is current-family-only, `N>1` retains the last N attack data batches, and `0` is cumulative. The predeclared canonical comparison is windows 1, 2, 3, and cumulative under the same partial-state protocol, 12 rounds, seeds 17–21. Low-data six-round smoke runs for window 3/cumulative are indeterminate and only validate execution.
- Key related papers for the new direction: Thomson et al. "Games for AI Control" (IASEAI 2026), Balcan et al. "Nash Equilibria and Pitfalls of Adversarial Training" (AISTATS 2023), Mertikopoulos et al. "Cycles in Adversarial Regularized Learning" (SODA 2018), Dieckmann et al. Red Queen predator-prey dynamics (1995).
- Active tasks and next steps are tracked in `TASKS.md`.

## Known issues

- The learned monitor currently matches the oracle on the default layout. Classification metrics, threshold calibration, held-out variants, and multiple seeds are still needed before interpreting monitor robustness.

## Scientific guardrails

- Verify the task agent actually specification-games before claiming monitoring helps.
- Count attempted and executed violations separately.
- Charge intervention costs and expose false positives.
- Keep hidden oracle labels out of actor and monitor inputs.
- Use held-out variants and multiple seeds.
- Do not add recursive monitors until the first-level monitor has a defined failure/corruption/information-limitation model.
- Describe all results as evidence about a toy control protocol, not a general alignment claim.

## Research provenance

- Claim-relevant runs embed Git commit, tracked-tree dirty state, command, UTC timestamp, platform, Python, and dependency versions in `results.json`.
- Raw artifacts stay under ignored `runs/`; `docs/experiment_log.md` is the committed ledger containing commands, artifact hashes, results, interpretations, and limitations.
- Run canonical experiments from a clean tracked tree at a committed revision. Untracked editor files such as `.vscode/` do not mark the tracked tree dirty.

## Miscellany

- The installed PyTorch is the CPU wheel. Explicit CUDA/device selection is not implemented.
- Output directories under `runs/` are ignored by git.
