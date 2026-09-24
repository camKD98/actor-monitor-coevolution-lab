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

## Task scoping and handoff

- Keep agent runs scoped to a specific task. Use `TASKS.md` to track status, blockers, and next steps.
- When a task starts, completes, or is reprioritized, update `TASKS.md`. If a task grows beyond the current session, record the blocker and ask whether to continue or hand off.
- After any environment-related discovery, fix, or repeated pitfall, record it in `LEARNINGS.md` so the next agent does not repeat the same mistake.
- When handing off, make sure both `TASKS.md` and `LEARNINGS.md` reflect the current state.
