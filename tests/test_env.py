import numpy as np
import pytest

from alignment.config import ExperimentConfig
from alignment.env import SpecificationGamingEnv


def test_exploit_has_high_proxy_and_low_true_reward():
    config = ExperimentConfig(size=5)
    env = SpecificationGamingEnv(config)
    env.reset()
    env.step(3)
    assert env.proposed_violation(3)
    result = env.step(3)
    assert result.violation
    assert result.proxy_reward > config.goal_reward
    assert result.true_reward < 0


def test_goal_is_safe():
    env = SpecificationGamingEnv(ExperimentConfig(size=5))
    env.reset()
    for action in [1, 1, 1, 1, 3, 3, 3, 3]:
        result = env.step(action)
    assert result.terminated
    assert not result.violation
    assert env.position == env.goal


def test_reset_is_deterministic():
    env = SpecificationGamingEnv(ExperimentConfig())
    first = env.reset()
    env.step(1)
    second = env.reset()
    np.testing.assert_array_equal(first, second)


def test_invalid_action_is_rejected():
    env = SpecificationGamingEnv(ExperimentConfig())
    with pytest.raises(ValueError):
        env.step(4)
