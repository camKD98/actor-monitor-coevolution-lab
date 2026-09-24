import argparse
import json
from dataclasses import replace
from pathlib import Path

import torch

from alignment.config import ContextualConfig, ExperimentConfig
from alignment.contextual_experiment import (
    collect_contextual_monitor_data,
    evaluate_contextual_actor,
    train_contextual_actor,
    train_contextual_monitor,
)
from alignment.evaluate import baseline_monitor, evaluate_actor
from alignment.provenance import collect_provenance
from alignment.train_agent import train_actor
from alignment.train_monitor import collect_monitor_data, learned_monitor, train_monitor


def run_experiment(config: ExperimentConfig, output: Path) -> dict[str, object]:
    actor, actor_returns = train_actor(config)
    fallback_actor, fallback_returns = train_actor(config, reward_mode="true")
    dataset = collect_monitor_data(config, actor)
    monitor, monitor_losses = train_monitor(config, dataset)
    monitors = {
        "none": None,
        "always": baseline_monitor("always"),
        "rule": baseline_monitor("rule"),
        "oracle": baseline_monitor("oracle"),
        "learned": learned_monitor(monitor),
    }
    metrics = {
        name: evaluate_actor(
            config,
            actor,
            decision,
            fallback_actor=fallback_actor if decision is not None else None,
        ).as_dict()
        for name, decision in monitors.items()
    }
    output.mkdir(parents=True, exist_ok=True)
    torch.save(actor.state_dict(), output / "actor.pt")
    torch.save(fallback_actor.state_dict(), output / "fallback_actor.pt")
    torch.save(monitor.state_dict(), output / "monitor.pt")
    result = {
        "provenance": collect_provenance(),
        "config": config.as_dict(),
        "training": {
            "final_actor_return": actor_returns[-1],
            "final_fallback_return": fallback_returns[-1],
            "final_monitor_loss": monitor_losses[-1],
            "monitor_examples": len(dataset.labels),
            "monitor_positive_examples": int(dataset.labels.sum().item()),
        },
        "evaluation": metrics,
    }
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def run_contextual_experiment(config: ContextualConfig, output: Path) -> dict[str, object]:
    objectives = (
        "proxy",
        "safety",
        "collaborative",
        "red_direct",
        "red_exfiltration",
    )
    trained = {name: train_contextual_actor(config, name) for name in objectives}
    actors = {name: value[0] for name, value in trained.items()}
    dataset = collect_contextual_monitor_data(
        config,
        [actors["safety"], actors["collaborative"], actors["red_direct"]],
    )
    monitor, monitor_losses = train_contextual_monitor(config, dataset)
    evaluation = {
        name: {
            "unmonitored": evaluate_contextual_actor(config, actor).as_dict(),
            "block_only": evaluate_contextual_actor(
                config,
                actor,
                monitor,
                investigate_threshold=None,
            ).as_dict(),
            "investigate": evaluate_contextual_actor(
                config,
                actor,
                monitor,
                block_threshold=1.1,
            ).as_dict(),
        }
        for name, actor in actors.items()
    }
    output.mkdir(parents=True, exist_ok=True)
    for name, actor in actors.items():
        torch.save(actor.state_dict(), output / f"{name}_actor.pt")
    torch.save(monitor.state_dict(), output / "police_monitor.pt")
    result = {
        "provenance": collect_provenance(),
        "config": config.as_dict(),
        "training": {
            "final_actor_returns": {name: values[1][-1] for name, values in trained.items()},
            "final_monitor_loss": monitor_losses[-1],
            "monitor_examples": len(dataset.labels),
            "monitor_positive_examples": int(dataset.labels.sum().item()),
            "held_out_action": "exfiltrate",
        },
        "evaluation": evaluation,
    }
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(prog="alignment-lab")
    parser.add_argument("--experiment", choices=("baseline", "contextual"), default="baseline")
    parser.add_argument("--output", type=Path, default=Path("runs/baseline"))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--actor-episodes", type=int, default=1500)
    parser.add_argument("--monitor-episodes", type=int, default=500)
    args = parser.parse_args()
    config_type = ContextualConfig if args.experiment == "contextual" else ExperimentConfig
    config = replace(
        config_type(),
        seed=args.seed,
        actor_episodes=args.actor_episodes,
        monitor_episodes=args.monitor_episodes,
    )
    run = run_contextual_experiment if args.experiment == "contextual" else run_experiment
    print(json.dumps(run(config, args.output), indent=2))


if __name__ == "__main__":
    main()
