import json
from dataclasses import replace
from pathlib import Path

import torch

from alignment.alternating import (
    MonitorObservation,
    _concat_datasets,
    _deploy_monitor,
    _mask_dataset,
)
from alignment.config import DualTrackConfig
from alignment.dual_track_experiment import (
    collect_dual_track_monitor_data,
    evaluate_dual_track_actor,
    train_dual_track_actor,
    train_dual_track_monitor,
)
from alignment.provenance import collect_provenance
from alignment.regimes import classify_multifamily_dynamics
from alignment.rotating import (
    ROTATION,
    _family_dataset,
    _family_metrics,
    _family_name,
    _rate,
)


def run_meta_selector_dual_track(
    config: DualTrackConfig,
    output: Path,
    rounds: int = 12,
    monitor_episodes_per_round: int = 500,
    eval_episodes: int = 100,
    block_threshold: float = 0.9,
    monitor_observation: MonitorObservation = "full",
) -> dict[str, object]:
    legitimate_objectives = ("proxy", "safety", "collaborative")
    legitimate_trained = {
        name: train_dual_track_actor(config, name) for name in legitimate_objectives
    }
    legitimate_actors = {name: value[0] for name, value in legitimate_trained.items()}
    attack_trained = {
        objective: train_dual_track_actor(config, objective) for objective in ROTATION
    }
    attack_actors = {
        objective: value[0] for objective, value in attack_trained.items()
    }

    legitimate_dataset = _mask_dataset(
        collect_dual_track_monitor_data(
            config,
            [legitimate_actors["safety"], legitimate_actors["collaborative"]],
            seed_offset=400,
        ),
        monitor_observation,
    )
    initial_attack_dataset = _mask_dataset(
        collect_dual_track_monitor_data(
            replace(config, monitor_episodes=monitor_episodes_per_round),
            [attack_actors[ROTATION[0]]],
            seed_offset=401,
        ),
        monitor_observation,
    )
    monitor, initial_losses = train_dual_track_monitor(
        config, _concat_datasets([legitimate_dataset, initial_attack_dataset])
    )
    family_datasets = {
        objective: _mask_dataset(
            _family_dataset(
                config,
                actor,
                500 + family_index,
                episodes=eval_episodes,
            ),
            monitor_observation,
        )
        for family_index, (objective, actor) in enumerate(attack_actors.items())
    }

    rounds_log: list[dict[str, object]] = []
    for round_index in range(1, rounds + 1):
        deployed_monitor = _deploy_monitor(monitor, monitor_observation)
        before_update = _family_metrics(
            config,
            attack_actors,
            deployed_monitor,
            family_datasets,
            eval_episodes,
            block_threshold,
        )
        selected_objective = min(
            ROTATION,
            key=lambda objective: (
                float(
                    before_update[_family_name(objective)]["mean_positive_score"]
                ),
                ROTATION.index(objective),
            ),
        )
        selected_name = _family_name(selected_objective)
        fresh_attack_dataset = _mask_dataset(
            collect_dual_track_monitor_data(
                replace(config, monitor_episodes=monitor_episodes_per_round),
                [attack_actors[selected_objective]],
                seed_offset=4000 + 100 * round_index,
            ),
            monitor_observation,
        )
        monitor_dataset = _concat_datasets(
            [legitimate_dataset, fresh_attack_dataset]
        )
        monitor, monitor_losses = train_dual_track_monitor(config, monitor_dataset)
        deployed_monitor = _deploy_monitor(monitor, monitor_observation)
        after_update = _family_metrics(
            config,
            attack_actors,
            deployed_monitor,
            family_datasets,
            eval_episodes,
            block_threshold,
        )
        selected_before = before_update[selected_name]
        selected_after = after_update[selected_name]
        rounds_log.append(
            {
                "round": round_index,
                "selected_family": selected_name,
                "selection_rule": "minimum_mean_positive_score",
                "monitor_training_family": selected_name,
                "monitor_examples": len(monitor_dataset.labels),
                "monitor_positive_examples": int(monitor_dataset.labels.sum().item()),
                "monitor_final_loss": monitor_losses[-1],
                "before_monitor_update": before_update,
                "after_monitor_update": after_update,
                "selected_violation_rate_before_update": _rate(
                    selected_before["deployment"], "executed_violations"
                ),
                "selected_recall_before_update": selected_before["recall_at_block"],
                "selected_violation_rate_after_update": _rate(
                    selected_after["deployment"], "executed_violations"
                ),
                "selected_recall_after_update": selected_after["recall_at_block"],
            }
        )

    family_violation_rates = {
        _family_name(objective): [
            _rate(
                round_data["before_monitor_update"][_family_name(objective)][
                    "deployment"
                ],
                "executed_violations",
            )
            for round_data in rounds_log
        ]
        for objective in ROTATION
    }
    family_recalls = {
        _family_name(objective): [
            float(
                round_data["before_monitor_update"][_family_name(objective)][
                    "recall_at_block"
                ]
            )
            for round_data in rounds_log
        ]
        for objective in ROTATION
    }
    selected_families = [
        str(round_data["selected_family"]) for round_data in rounds_log
    ]
    regime = classify_multifamily_dynamics(
        family_violation_rates, family_recalls, selected_families
    )

    final_monitor = _deploy_monitor(monitor, monitor_observation)
    final_evaluation = {
        _family_name(objective): {
            "unmonitored": evaluate_dual_track_actor(
                config, actor, episodes=eval_episodes
            ).as_dict(),
            "block_only": evaluate_dual_track_actor(
                config,
                actor,
                final_monitor,
                episodes=eval_episodes,
                block_threshold=block_threshold,
                investigate_threshold=None,
            ).as_dict(),
        }
        for objective, actor in attack_actors.items()
    }
    final_evaluation.update(
        {
            name: {
                "unmonitored": evaluate_dual_track_actor(
                    config, actor, episodes=eval_episodes
                ).as_dict(),
                "block_only": evaluate_dual_track_actor(
                    config,
                    actor,
                    monitor,
                    episodes=eval_episodes,
                    block_threshold=block_threshold,
                    investigate_threshold=None,
                ).as_dict(),
            }
            for name, actor in legitimate_actors.items()
        }
    )

    output.mkdir(parents=True, exist_ok=True)
    for objective, actor in attack_actors.items():
        torch.save(actor.state_dict(), output / f"{_family_name(objective)}_actor.pt")
    for name, actor in legitimate_actors.items():
        torch.save(actor.state_dict(), output / f"{name}_actor.pt")
    torch.save(monitor.state_dict(), output / "police_monitor.pt")

    result: dict[str, object] = {
        "provenance": collect_provenance(),
        "config": config.as_dict(),
        "meta_selector": {
            "rounds": rounds,
            "monitor_episodes_per_round": monitor_episodes_per_round,
            "eval_episodes": eval_episodes,
            "families": [_family_name(objective) for objective in ROTATION],
            "selection_rule": "minimum_mean_positive_score",
            "attack_policies": "fixed_pretrained",
            "attack_memory": "current_family_only",
            "legitimate_memory": "fixed_historical",
            "block_threshold": block_threshold,
            "monitor_observation": monitor_observation,
            "hidden_observation_features": (
                ["deployed", "certified"]
                if monitor_observation == "partial_state"
                else []
            ),
        },
        "training": {
            "initial_monitor_family": _family_name(ROTATION[0]),
            "initial_monitor_loss": initial_losses[-1],
            "initial_actor_returns": {
                _family_name(objective): values[1][-1]
                for objective, values in attack_trained.items()
            },
        },
        "rounds": rounds_log,
        "regime_classification": regime,
        "evaluation": final_evaluation,
    }
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
