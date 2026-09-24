# Adversarial Oversight Lab

A small, reproducible AI-control experiment: train a reward-seeking policy in a specification-gaming gridworld, then train a separate model to detect and block unsafe proposed actions.

The project tests whether learned monitoring can improve safety **without blocking all useful behavior**. It is a toy proof of concept, not evidence that recursive monitoring solves alignment.

See [the research agenda](docs/research_agenda.md) for hypotheses, related work, assumptions, and limitations. Development should continue from the [implementation plan](docs/implementation_plan.md) and [project handoff](HANDOFF.md).

## Planned workflow

1. Train an unmonitored task agent on the observable proxy reward.
2. Collect proposed actions and hidden oracle violation labels.
3. Train a separate monitor on public state/action features.
4. Compare no monitoring, always/never alarm, rule-based, learned, and oracle monitors.
5. Evaluate whether an actor can adapt to evade a frozen learned monitor.

Setup and commands will be added with the runnable implementation.
