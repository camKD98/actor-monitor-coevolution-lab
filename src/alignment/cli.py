import argparse
import json
from dataclasses import replace
from pathlib import Path

import torch

from alignment.config import ExperimentConfig
from alignment.evaluate import baseline_monitor, evaluate_actor
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


def main() -> None:
    parser = argparse.ArgumentParser(prog="alignment-lab")
    parser.add_argument("--output", type=Path, default=Path("runs/baseline"))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--actor-episodes", type=int, default=1500)
    parser.add_argument("--monitor-episodes", type=int, default=500)
    args = parser.parse_args()
    config = replace(
        ExperimentConfig(),
        seed=args.seed,
        actor_episodes=args.actor_episodes,
        monitor_episodes=args.monitor_episodes,
    )
    print(json.dumps(run_experiment(config, args.output), indent=2))


if __name__ == "__main__":
    main()
