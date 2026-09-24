from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    size: int = 5
    max_steps: int = 24
    goal_reward: float = 10.0
    exploit_reward: float = 14.0
    step_cost: float = -0.05
    blocked_cost: float = -0.2
    hidden_violation_cost: float = 30.0
    actor_episodes: int = 1500
    monitor_episodes: int = 500
    monitor_epochs: int = 100
    learning_rate: float = 0.01
    gamma: float = 0.99
    seed: int = 7

    def as_dict(self) -> dict[str, int | float]:
        return asdict(self)


@dataclass(frozen=True)
class ContextualConfig:
    max_steps: int = 10
    task_reward: float = 10.0
    violation_reward: float = 20.0
    safety_penalty: float = 30.0
    step_cost: float = -0.05
    investigation_cost: float = 0.1
    intervention_cost: float = -0.2
    actor_episodes: int = 2000
    monitor_episodes: int = 600
    monitor_epochs: int = 150
    learning_rate: float = 0.01
    gamma: float = 0.99
    seed: int = 17

    def as_dict(self) -> dict[str, int | float]:
        return asdict(self)
