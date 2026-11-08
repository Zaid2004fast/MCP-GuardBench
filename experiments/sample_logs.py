"""Copy a representative sample of agent trajectories into logs/ (committed to git).

Full per-episode artefacts stay in results/<run>/.../episodes/ (git-ignored, they are
large). For every run, model and main defense this keeps one attacked episode per attack
class plus two benign episodes (seed 0): trace.json (messages, tool calls, gateway
decisions), audit.jsonl (hash-chained log) and the final world.json.

    python experiments/sample_logs.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mcpguard.eval.metrics import load_episodes  # noqa: E402
DEFENSES = ["none", "llm_guard", "allowlist+scoped", "hitl", "full"]


def main() -> None:
    out = ROOT / "logs"
    for run in ["phase2-reference", "phase2-local", "phase2-api"]:
        run_dir = ROOT / "results" / run
        if not (run_dir / "episodes.jsonl").exists():
            continue
        df = load_episodes(run_dir)
        df = df[(df["seed"] == 0) & df["defense"].isin(DEFENSES) & (df["status"] != "error")]
        picks = df.sort_values("scenario_id").groupby(
            ["model", "defense", df["attack_class"].fillna("benign")]).head(1)
        picks = picks[(picks["attack_class"].notna()) | picks.index.isin(
            df[df["attack_class"].isna()].sort_values("scenario_id").groupby(["model", "defense"]).head(2).index)]
        n = 0
        for _, r in picks.iterrows():
            slug = r["model"].replace(":", "_").replace("/", "_")
            src = (run_dir / slug / r["defense"] / f"seed{r['seed']}" / r["trace_file"]).parent
            if not src.exists():
                continue
            dst = out / run / slug / r["defense"] / r["scenario_id"]
            dst.mkdir(parents=True, exist_ok=True)
            for name in ("trace.json", "audit.jsonl", "world.json"):
                if (src / name).exists():
                    shutil.copy2(src / name, dst / name)
            n += 1
        print(f"{run}: copied {n} episodes to {out / run}")


if __name__ == "__main__":
    main()
