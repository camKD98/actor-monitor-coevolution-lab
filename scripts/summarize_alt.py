import glob
import json
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "runs"
for path in sorted(glob.glob(root + r"\DT-ALT-S*\results.json")):
    with open(path) as f:
        r = json.load(f)
    seed = r["config"]["seed"]
    print(f"=== seed {seed} ===")
    for rd in r["rounds"]:
        m = rd["attack_actor_vs_monitor"]
        rec = rd["monitor_recall"]
        print(
            f"  r{rd['round']:>2} ret={rd['actor_train_return_mean']:7.2f} "
            f"att={m['attempted_violations']:>3} exe={m['executed_violations']:>3} "
            f"int={m['interventions']:>3} | rec dir={rec['direct_sabotage_fresh']} "
            f"rev={rec['review_escalation_recall_at_block']} "
            f"maint={rec['maintenance_path_recall_at_block']}"
        )
    ev = r["evaluation"]["co_trained_direct_sabotage"]
    ho = r["evaluation"]["red_maintenance_path"]
    print(
        f"  final: co-trained att={ev['block_only']['attempted_violations']} "
        f"exe={ev['block_only']['executed_violations']} | held-out maint "
        f"exe={ho['block_only']['executed_violations']} int={ho['block_only']['interventions']}"
    )
