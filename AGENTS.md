# Agent Instructions

Read these files before making changes:

1. `HANDOFF.md` for current status, environment failure, and takeover order.
2. `docs/implementation_plan.md` for the approved project plan.
3. `docs/research_agenda.md` for hypotheses, threat model, metrics, and scientific limitations.

Use a clean project-local Python environment; do not rely on a global Conda environment. Install development dependencies with `python -m pip install -e ".[dev]"` and verify with Ruff and pytest.

The existing prototype is unverified. First establish that the unmonitored task agent reliably learns the designed exploit. Do not interpret monitor results until that baseline works. Keep oracle violation labels out of actor and monitor inputs, report safety and usefulness together, and do not treat toy-gridworld results as a general alignment claim.

Do not begin recursive oversight by stacking identical monitors. A deeper layer is meaningful only after the lower monitor has a defined error, corruption, or information-limitation model and the higher layer has a partially independent evidence channel.
