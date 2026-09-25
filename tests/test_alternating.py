from dataclasses import replace

from alignment.alternating import run_alternating_dual_track
from alignment.config import DualTrackConfig


def test_alternating_runs_three_rounds(tmp_path):
    config = replace(
        DualTrackConfig(),
        actor_episodes=5,
        monitor_episodes=6,
        monitor_epochs=2,
        max_steps=8,
    )
    result = run_alternating_dual_track(
        config,
        tmp_path,
        rounds=3,
        episodes_per_round=4,
        monitor_episodes_per_round=6,
        eval_episodes=5,
    )
    assert (tmp_path / "results.json").exists()
    assert (tmp_path / "police_monitor.pt").exists()
    assert (tmp_path / "co_trained_actor.pt").exists()

    rounds = result["rounds"]
    assert len(rounds) == 3
    for i, entry in enumerate(rounds, start=1):
        assert entry["round"] == i
        assert "actor_train_return_mean" in entry
        assert "monitor_recall" in entry
        assert "evasion_rate" in entry
        metrics = entry["attack_actor_vs_monitor"]
        for key in (
            "attempted_violations",
            "executed_violations",
            "interventions",
            "return_mean",
        ):
            assert key in metrics
        # Monitor data accumulates across rounds.
        assert entry["monitor_examples"] > 0


def test_alternating_final_evaluation_structure(tmp_path):
    config = replace(
        DualTrackConfig(),
        actor_episodes=5,
        monitor_episodes=6,
        monitor_epochs=2,
        max_steps=8,
    )
    result = run_alternating_dual_track(
        config,
        tmp_path,
        rounds=2,
        episodes_per_round=4,
        monitor_episodes_per_round=6,
        eval_episodes=5,
    )
    expected_actors = {
        "proxy",
        "safety",
        "collaborative",
        "red_review_escalation",
        "red_maintenance_path",
        "co_trained_direct_sabotage",
    }
    assert set(result["evaluation"]) == expected_actors
    for actor_metrics in result["evaluation"].values():
        assert set(actor_metrics) == {"unmonitored", "block_only", "investigate"}
    assert result["alternating"]["co_train_objective"] == "red_direct_sabotage"
    assert result["alternating"]["held_out_family"] == "maintenance_path"
    assert "threshold_selection" in result["training"]


def test_alternating_action_only_monitor(tmp_path):
    config = replace(
        DualTrackConfig(),
        actor_episodes=5,
        monitor_episodes=6,
        monitor_epochs=2,
        max_steps=8,
    )
    result = run_alternating_dual_track(
        config,
        tmp_path,
        rounds=2,
        episodes_per_round=4,
        monitor_episodes_per_round=6,
        eval_episodes=5,
        monitor_observation="action_only",
    )
    assert result["alternating"]["monitor_observation"] == "action_only"
    assert len(result["rounds"]) == 2
    assert set(result["evaluation"]) == {
        "proxy",
        "safety",
        "collaborative",
        "red_review_escalation",
        "red_maintenance_path",
        "co_trained_direct_sabotage",
    }
