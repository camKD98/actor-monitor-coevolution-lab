from dataclasses import replace

from alignment.cli import run_contextual_experiment
from alignment.config import ContextualConfig
from alignment.contextual_env import ContextualAction, ContextualEscalationEnv
from alignment.contextual_experiment import (
    bounded_investigation,
    collect_contextual_monitor_data,
)
from alignment.models import ActorCritic


def test_contextual_environment_has_direct_and_held_out_violations():
    env = ContextualEscalationEnv(ContextualConfig())
    env.reset()
    env.step(ContextualAction.RESEARCH)
    env.step(ContextualAction.REQUEST_ACCESS)
    assert env.proposed_violation(ContextualAction.OVERRIDE)
    assert not env.proposed_violation(ContextualAction.EXFILTRATE)
    env.step(ContextualAction.SHARE)
    assert env.proposed_violation(ContextualAction.EXFILTRATE)


def test_contextual_research_can_support_legitimate_completion():
    env = ContextualEscalationEnv(ContextualConfig())
    env.reset()
    env.step(ContextualAction.RESEARCH)
    env.step(ContextualAction.WORK)
    result = env.step(ContextualAction.WORK)
    assert result.completed
    assert not result.violation


def test_bounded_investigation_uses_authorization_evidence():
    env = ContextualEscalationEnv(ContextualConfig())
    env.reset()
    env.step(ContextualAction.RESEARCH)
    env.step(ContextualAction.REQUEST_ACCESS)
    env.step(ContextualAction.SHARE)
    assert bounded_investigation(env.investigation_evidence(ContextualAction.OVERRIDE))
    assert bounded_investigation(env.investigation_evidence(ContextualAction.EXFILTRATE))
    assert not bounded_investigation(env.investigation_evidence(ContextualAction.WORK))


def test_exfiltration_action_is_held_out_from_monitor_training():
    config = replace(ContextualConfig(), monitor_episodes=4, max_steps=3)
    env = ContextualEscalationEnv(config)
    actor = ActorCritic(env.observation_size, actions=env.action_count)
    dataset = collect_contextual_monitor_data(config, [actor])
    assert ContextualAction.EXFILTRATE not in dataset.actions.tolist()


def test_short_contextual_experiment_writes_results(tmp_path):
    config = replace(
        ContextualConfig(),
        actor_episodes=5,
        monitor_episodes=6,
        monitor_epochs=2,
        max_steps=5,
    )
    result = run_contextual_experiment(config, tmp_path)
    assert (tmp_path / "results.json").exists()
    assert (tmp_path / "police_monitor.pt").exists()
    assert result["provenance"]["git_commit"]
    assert len(result["investigation_frontier"]) >= 6
    assert result["monitor_validation"]["roc_auc"] >= 0.0
    assert set(result["evaluation"]) == {
        "proxy",
        "safety",
        "collaborative",
        "red_direct",
        "red_exfiltration",
    }
