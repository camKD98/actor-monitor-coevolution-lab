from dataclasses import replace

from alignment.config import DualTrackConfig
from alignment.meta_selector import run_meta_selector_dual_track
from alignment.regimes import classify_dynamics, classify_multifamily_dynamics
from alignment.rotating import run_rotating_dual_track


def test_classify_convergence():
    result = classify_dynamics(
        [0.0, 0.02, 0.0, 0.01, 0.0, 0.0],
        [0.96, 0.98, 1.0, 0.99, 1.0, 1.0],
    )
    assert result["regime"] == "convergence"


def test_classify_cycling():
    result = classify_dynamics(
        [0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
        [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0],
    )
    assert result["regime"] == "cycling"
    assert result["violation_rate"]["lag_1_autocorrelation"] < -0.9


def test_classify_escape():
    result = classify_dynamics(
        [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        [1.0, 0.9, 0.7, 0.5, 0.25, 0.0],
    )
    assert result["regime"] == "escape"


def test_short_series_is_indeterminate():
    result = classify_dynamics([0.0, 1.0, 0.0], [1.0, 0.0, 1.0])
    assert result["regime"] == "indeterminate"


def test_classify_requires_matched_series():
    try:
        classify_dynamics([0.0, 1.0, 0.0], [1.0, 0.0])
    except ValueError as error:
        assert "equal length" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_classify_multifamily_cycling():
    result = classify_multifamily_dynamics(
        {
            "direct": [0.0, 1.0, 1.0, 0.0, 1.0, 1.0],
            "review": [1.0, 0.0, 1.0, 1.0, 0.0, 1.0],
            "maintenance": [1.0, 1.0, 0.0, 1.0, 1.0, 0.0],
        },
        {
            "direct": [1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            "review": [0.0, 1.0, 0.0, 0.0, 1.0, 0.0],
            "maintenance": [0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        },
        ["review", "maintenance", "direct", "review", "maintenance", "direct"],
    )
    assert result["regime"] == "cycling"
    assert result["selection_switch_rate"] == 1.0


def test_rotating_experiment_runs_three_rounds(tmp_path):
    config = replace(
        DualTrackConfig(),
        actor_episodes=5,
        monitor_episodes=6,
        monitor_epochs=2,
        max_steps=8,
    )
    result = run_rotating_dual_track(
        config,
        tmp_path,
        rounds=3,
        episodes_per_round=4,
        monitor_episodes_per_round=6,
        eval_episodes=5,
    )
    assert (tmp_path / "results.json").exists()
    assert [entry["active_family"] for entry in result["rounds"]] == [
        "review_escalation",
        "maintenance_path",
        "direct_sabotage",
    ]
    for entry in result["rounds"]:
        assert set(entry["before_monitor_update"]) == {
            "direct_sabotage",
            "review_escalation",
            "maintenance_path",
        }
        assert set(entry["after_monitor_update"]) == {
            "direct_sabotage",
            "review_escalation",
            "maintenance_path",
        }
    assert result["rotation"]["attack_memory"] == "current_family_only"
    assert result["regime_classification"]["regime"] in {
        "convergence",
        "cycling",
        "escape",
        "indeterminate",
    }


def test_meta_selector_keeps_fixed_attack_policies(tmp_path):
    config = replace(
        DualTrackConfig(),
        actor_episodes=5,
        monitor_episodes=6,
        monitor_epochs=2,
        max_steps=8,
    )
    result = run_meta_selector_dual_track(
        config,
        tmp_path,
        rounds=3,
        monitor_episodes_per_round=6,
        eval_episodes=5,
    )
    assert (tmp_path / "results.json").exists()
    assert result["meta_selector"]["attack_policies"] == "fixed_pretrained"
    assert len(result["rounds"]) == 3
    for entry in result["rounds"]:
        assert entry["selected_family"] in {
            "direct_sabotage",
            "review_escalation",
            "maintenance_path",
        }
        assert set(entry["before_monitor_update"]) == {
            "direct_sabotage",
            "review_escalation",
            "maintenance_path",
        }
    assert result["regime_classification"]["regime"] == "indeterminate"


def test_meta_selector_partial_state_mask(tmp_path):
    config = replace(
        DualTrackConfig(),
        actor_episodes=5,
        monitor_episodes=6,
        monitor_epochs=2,
        max_steps=8,
    )
    result = run_meta_selector_dual_track(
        config,
        tmp_path,
        rounds=3,
        monitor_episodes_per_round=6,
        eval_episodes=5,
        monitor_observation="partial_state",
    )
    assert result["meta_selector"]["monitor_observation"] == "partial_state"
    assert result["meta_selector"]["hidden_observation_features"] == [
        "deployed",
        "certified",
    ]
    assert len(result["rounds"]) == 3
