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
- Ruff and pytest pass (`8 passed in ~15s`).
- Default seed (`seed=7`) gives a fully deterministic pipeline.
- The unmonitored actor reliably learns the designed exploit: 100/100 evaluation episodes reach the exploit cell.
- Reproducibility verified: two identical default runs produced identical `results.json`.
- Active tasks and next steps are tracked in `TASKS.md`.

## Known issues

- The learned monitor is currently degenerate: it blocks every step, producing the same result as the oracle/rule monitor. This prevents meaningful safety/usefulness trade-off measurements.

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
