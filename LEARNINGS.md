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

## Miscellany

- The installed PyTorch is the CPU wheel. Explicit CUDA/device selection is not implemented.
- Output directories under `runs/` are ignored by git.
