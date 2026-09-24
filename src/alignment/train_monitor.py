from dataclasses import dataclass

import numpy as np
import torch

from alignment.config import ExperimentConfig
from alignment.env import SpecificationGamingEnv
from alignment.models import ActionMonitor, ActorCritic


@dataclass(frozen=True)
class MonitorDataset:
    observations: torch.Tensor
    actions: torch.Tensor
    labels: torch.Tensor


def collect_monitor_data(
    config: ExperimentConfig,
    actor: ActorCritic,
    variant: int = 0,
) -> MonitorDataset:
    rng = np.random.default_rng(config.seed + 1)
    env = SpecificationGamingEnv(config, variant)
    observations: list[np.ndarray] = []
    actions: list[int] = []
    labels: list[float] = []

    for _ in range(config.monitor_episodes):
        observation = env.reset()
        while True:
            with torch.no_grad():
                logits, _ = actor(torch.from_numpy(observation))
            if rng.random() < 0.35:
                action = int(rng.integers(0, 4))
            else:
                action = int(torch.distributions.Categorical(logits=logits).sample().item())
            observations.append(observation.copy())
            actions.append(action)
            labels.append(float(env.proposed_violation(action)))
            result = env.step(action)
            observation = result.observation
            if result.terminated:
                break

    return MonitorDataset(
        observations=torch.from_numpy(np.stack(observations)),
        actions=torch.tensor(actions, dtype=torch.long),
        labels=torch.tensor(labels, dtype=torch.float32),
    )


def train_monitor(
    config: ExperimentConfig,
    dataset: MonitorDataset,
) -> tuple[ActionMonitor, list[float]]:
    torch.manual_seed(config.seed + 2)
    model = ActionMonitor(dataset.observations.shape[1])
    positives = dataset.labels.sum().clamp(min=1.0)
    negatives = len(dataset.labels) - positives
    criterion = torch.nn.BCEWithLogitsLoss(pos_weight=(negatives / positives).clamp(max=50.0))
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    losses: list[float] = []

    for _ in range(config.monitor_epochs):
        logits = model(dataset.observations, dataset.actions)
        loss = criterion(logits, dataset.labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        losses.append(float(loss.item()))

    return model, losses


def learned_monitor(model: ActionMonitor, threshold: float = 0.5):
    def decide(observation: np.ndarray, action: int, env: SpecificationGamingEnv) -> bool:
        del env
        with torch.no_grad():
            score = torch.sigmoid(
                model(torch.from_numpy(observation).unsqueeze(0), torch.tensor([action]))
            )
        return bool(score.item() >= threshold)

    return decide
