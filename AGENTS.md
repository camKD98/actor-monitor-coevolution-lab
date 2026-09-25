# Agent Instructions

Read these files before making changes:

1. `LEARNINGS.md` for workspace environment quirks, verified commands, and recurring pitfalls.
2. `TASKS.md` for current task status, blockers, and next steps.
3. `docs/implementation_plan.md` for the approved project plan.
4. `docs/research_agenda.md` for hypotheses, threat model, metrics, and scientific limitations.

Use a clean project-local Python environment; do not rely on a global Conda environment. Install development dependencies with `python -m pip install -e ".[dev]"` and verify with Ruff and pytest. See `LEARNINGS.md` for the exact Windows/PowerShell commands that are known to work.

The existing prototype is unverified. First establish that the unmonitored task agent reliably learns the designed exploit. Do not interpret monitor results until that baseline works. Keep oracle violation labels out of actor and monitor inputs, report safety and usefulness together, and do not treat toy-gridworld results as a general alignment claim.

Do not begin recursive oversight by stacking identical monitors. A deeper layer is meaningful only after the lower monitor has a defined error, corruption, or information-limitation model and the higher layer has a partially independent evidence channel.

## Committing changes

- Prefer small, focused commits with clear messages.
- **Auto-commit tiny passing fixes** (e.g., a one-line lint fix or a passing test adjustment) after Ruff/pytest pass.
- **Ask before committing** non-trivial changes (new features, behavior changes, anything the user may want to review or name differently).
- Never commit if no changes exist.
- Do not push unless explicitly asked.
- Do not include secrets, API keys, or raw run outputs in commits.

## Research run provenance

Treat this repository as the basis of a future research paper. Any result used to guide development or support a claim must be reproducible after scripts evolve.

- Run claim-relevant experiments from a committed code state whenever possible. Do not silently treat exploratory dirty-tree runs as canonical.
- Every saved run must record the Git commit, tracked-tree dirty state, exact command, UTC timestamp, Python version, dependency versions, seed, and complete configuration.
- Keep raw artifacts under ignored `runs/` directories; do not commit model weights or bulk raw outputs.
- **Commit experiment code before updating `docs/experiment_log.md`.** The required order is: finish and verify code → commit the code/configuration → run the experiment from that clean commit → hash the artifact → update and commit the ledger in a separate follow-up commit. Never log a run as canonical without an existing immutable code commit to reference.
- Maintain `docs/experiment_log.md` as the committed experiment ledger. For each relevant run, record:
  - a stable run ID and purpose;
  - code commit and tracked-tree state;
  - exact command and working directory;
  - artifact location and `results.json` SHA-256;
  - configuration/seeds and train/validation/evaluation split details;
  - key quantitative results;
  - what the result supports and does not support;
  - known confounders, failures, and follow-up decisions.
- If a result was produced before provenance capture or from a dirty tree, label it exploratory and rerun from a clean commit before citing it as canonical.
- Never overwrite a canonical run directory. Use a new run ID for reruns or changed code/configuration.
- Paper tables and plots must be generated from logged artifacts whose hashes match the ledger, not from remembered or manually transcribed values.
- Avoid running a full multi-seed sweep from a dirty tree when the intended result may become canonical. Before committing, use only the smallest smoke run needed to validate execution and artifact structure. Then ask for commit approval, commit the verified experiment code, and run the full sweep once from that clean commit. A later commit cannot retroactively make a dirty-tree run canonical, even if the relevant source files appear unchanged.

## Parallel experiment execution

- Parallelize independent, relatively cheap experiment runs (especially separate random seeds) when they have no shared mutable outputs.
- On this PC (AMD Ryzen 5 3600, 6 physical cores / 12 logical processors, 16 GB RAM), use at most **four concurrent experiment workers** by default. This preserves headroom for Windows and Devin while materially reducing sweep time.
- Give every worker a distinct output directory and log file. Never run concurrent workers against the same artifact directory.
- Launch additional queued runs only when a worker slot becomes available, and verify each process exit code plus the presence and parseability of `results.json` before treating the batch as complete.
- Do not generalize this limit to memory-heavy models, GPU workloads, database mutations, or tasks with shared state. Reduce concurrency when per-worker memory use is substantial or when the machine becomes unresponsive.

## Task scoping and handoff

- Keep agent runs scoped to a specific task. Use `TASKS.md` to track status, blockers, and next steps.
- When a task starts, completes, or is reprioritized, update `TASKS.md`. If a task grows beyond the current session, record the blocker and ask whether to continue or hand off.
- After any environment-related discovery, fix, or repeated pitfall, record it in `LEARNINGS.md` so the next agent does not repeat the same mistake.
- When handing off, make sure both `TASKS.md` and `LEARNINGS.md` reflect the current state.
