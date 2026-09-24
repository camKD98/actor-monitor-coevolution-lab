from dataclasses import replace

from alignment.cli import run_experiment
from alignment.config import ExperimentConfig


def test_short_experiment_writes_results(tmp_path):
    config = replace(
        ExperimentConfig(),
        actor_episodes=5,
        monitor_episodes=5,
        monitor_epochs=2,
        max_steps=8,
    )
    result = run_experiment(config, tmp_path)
    assert (tmp_path / "results.json").exists()
    assert (tmp_path / "actor.pt").exists()
    assert (tmp_path / "fallback_actor.pt").exists()
    assert result["provenance"]["git_commit"]
    assert set(result["evaluation"]) == {"none", "always", "rule", "oracle", "learned"}
