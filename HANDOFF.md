# Project Handoff

## Current status

The research agenda and initial runnable prototype have been written. The prototype includes a specification-gaming gridworld, a small actor-critic model, supervised action monitor, baseline monitors, evaluation harness, CLI, and tests.

The code has **not yet been validated end to end**. Do not treat any experimental result as established.

## Why work stopped on the Mac

The available global Conda environment was:

- Python 3.12
- PyTorch 2.2.2
- NumPy 1.26.4
- pytest 9.1.1
- macOS Darwin 21.6.0

Pytest runs repeatedly ended in native segmentation faults. One crash occurred during PyTorch backward; others occurred during evaluation or pytest plugin shutdown. The environment also had globally installed plugins such as `pytest-rerunfailures` and Hypothesis. Disabling plugin autoload did not eliminate every crash. Individual tests printed as passing before some process crashes, but the suite must be considered unverified.

This appears more likely to be a broken/incompatible global native environment than an ordinary Python failure. Establish a clean environment on the PC before diagnosing application code from those stack traces.

## Recommended takeover sequence

1. Copy the entire `Alignment` directory, including hidden files, to the PC.
2. Use Git for subsequent work; note that this directory was inside a parent repository on the Mac rather than initialized as its own repository.
3. Install a current supported 64-bit Python version, preferably Python 3.11 or 3.12.
4. Create a project-local virtual environment.
5. Install the package with `python -m pip install -e ".[dev]"`.
6. Run `python -m ruff check .`.
7. Run `python -m pytest`.
8. Run a reduced experiment first:
   `alignment-lab --actor-episodes 50 --monitor-episodes 25 --output runs/smoke`
9. Inspect `runs/smoke/results.json`, then run the default experiment only after the smoke run is healthy.

For an NVIDIA GPU, install the PyTorch build recommended by the official PyTorch installer for the PC's CUDA/driver setup rather than guessing a CUDA wheel. The current code is CPU-only in practice because tensors and models are never moved to CUDA; explicit device support remains to be implemented.

## Known implementation gaps

- The default training regime has not been shown to learn the exploit reliably.
- The monitor dataset and classifier have not been evaluated on held-out data.
- The “rule” and “oracle” monitors are currently equivalent; a genuinely imperfect rule baseline is still needed.
- Metrics currently omit false-positive rate, precision/recall, ROC-AUC, and calibration.
- No adaptive-evasion, alternating-training, multi-seed aggregation, or recursive oversight code exists yet.
- The environment is intentionally simple and may make monitoring trivial.
- The CLI saves aggregate JSON and model weights, but no per-episode data or plots.
- Device selection/CUDA support is not implemented.

## Important scientific guardrails

Read `docs/research_agenda.md` and `docs/implementation_plan.md` before extending the code. In particular:

- verify the task agent actually specification-games before claiming monitoring helps;
- count attempted and executed violations separately;
- charge intervention costs and expose false positives;
- keep hidden oracle labels out of model inputs;
- use held-out variants and multiple seeds;
- do not add recursive monitors until first-level monitors have meaningful failure modes;
- describe results as evidence about a toy control protocol, not a solution to alignment.
