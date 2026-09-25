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
