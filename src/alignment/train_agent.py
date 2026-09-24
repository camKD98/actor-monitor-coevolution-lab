from collections.abc import Callable
from typing import Literal

import numpy as np
import torch
from torch.distributions import Categorical

from alignment.config import ExperimentConfig
from alignment.env import SpecificationGamingEnv
from alignment.models import ActorCritic

MonitorFn = Callable[[np.ndarray, int, SpecificationGamingEnv], bool]


def seed_everything(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)


def train_actor(
    config: ExperimentConfig,
    monitor: MonitorFn | None = None,
    variant: int = 0,
    reward_mode: Literal["proxy", "true"] = "proxy",
) -> tuple[ActorCritic, list[float]]:
    seed_everything(config.seed + (100 if reward_mode == "true" else 0))
    env = SpecificationGamingEnv(config, variant)
    model = ActorCritic(env.observation_size)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    episode_returns: list[float] = []

    for _ in range(config.actor_episodes):
        observation = env.reset()
        log_probabilities: list[torch.Tensor] = []
        values: list[torch.Tensor] = []
        rewards: list[float] = []
        entropies: list[torch.Tensor] = []

        while True:
            tensor = torch.from_numpy(observation)
            logits, value = model(tensor)
            distribution = Categorical(logits=logits)
            action = distribution.sample()
            action_index = int(action.item())
            blocked = monitor is not None and monitor(observation, action_index, env)
            result = env.blocked_step() if blocked else env.step(action_index)
            log_probabilities.append(distribution.log_prob(action))
            values.append(value)
            entropies.append(distribution.entropy())
            rewards.append(result.proxy_reward if reward_mode == "proxy" else result.true_reward)
            observation = result.observation
            if result.terminated:
                break

        returns: list[float] = []
        running_return = 0.0
        for reward in reversed(rewards):
            running_return = reward + config.gamma * running_return
            returns.append(running_return)
        returns_tensor = torch.tensor(list(reversed(returns)), dtype=torch.float32)
        values_tensor = torch.stack(values)
        advantage = returns_tensor - values_tensor.detach()
        policy_loss = -(torch.stack(log_probabilities) * advantage).mean()
        value_loss = torch.nn.functional.mse_loss(values_tensor, returns_tensor)
        entropy = torch.stack(entropies).mean()
        loss = policy_loss + 0.5 * value_loss - 0.01 * entropy
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        episode_returns.append(sum(rewards))

    return model, episode_returns
