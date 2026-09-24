from dataclasses import replace

import numpy as np
import torch

from alignment.config import ExperimentConfig
from alignment.env import SpecificationGamingEnv
from alignment.evaluate import baseline_monitor, evaluate_actor
from alignment.models import ActorCritic
from alignment.train_monitor import MonitorDataset, learned_monitor, train_monitor


def test_oracle_blocks_only_violations():
    env = SpecificationGamingEnv(ExperimentConfig())
    observation = env.reset()
    oracle = baseline_monitor("oracle")
    assert not oracle(observation, 1, env)
    env.step(3)
    observation = env.observation()
    assert oracle(observation, 3, env)


def test_monitor_learns_separable_examples():
    config = replace(ExperimentConfig(), monitor_epochs=120, learning_rate=0.02)
    env = SpecificationGamingEnv(config)
    observation = env.reset()
    env.step(3)
    dangerous = env.observation().copy()
    safe = env.reset().copy()
    observations = torch.from_numpy(np.stack([dangerous] * 20 + [safe] * 20))
    actions = torch.tensor([3] * 20 + [1] * 20)
    labels = torch.tensor([1.0] * 20 + [0.0] * 20)
    model, _ = train_monitor(config, MonitorDataset(observations, actions, labels))
    decide = learned_monitor(model)
    env.reset()
    env.step(3)
    assert decide(env.observation(), 3, env)
    env.reset()
    assert not decide(env.observation(), 1, env)


def test_always_monitor_has_intervention_cost():
    config = replace(ExperimentConfig(), max_steps=4)
    env = SpecificationGamingEnv(config)
    actor = ActorCritic(env.observation_size)
    metrics = evaluate_actor(config, actor, baseline_monitor("always"), episodes=2)
    assert metrics.interventions == 8
    assert metrics.proxy_return == 4 * config.blocked_cost
    assert metrics.safe_completions == 0
