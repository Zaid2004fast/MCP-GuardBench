"""CLI: run the benchmark for a set of models x defenses.

    python -m mcpguard.eval.run --config configs/baseline_local.yaml
    python -m mcpguard.eval.run --models ollama:qwen2.5:1.5b --defenses none --limit-per-class 2
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd
import yaml

from mcpguard.contracts import DefenseConfig, EpisodeResult, Scenario
from mcpguard.eval.metrics import per_class, summarize
from mcpguard.eval.runner import run_episode
from mcpguard.eval.scenarios import build_scenarios
from mcpguard.providers import make_provider

ROOT = Path(__file__).resolve().parents[2]
DEFENSES_FILE = ROOT / "configs" / "defenses.yaml"


def load_defenses() -> dict[str, DefenseConfig]:
    raw = yaml.safe_load(DEFENSES_FILE.read_text(encoding="utf-8"))
    return {name: DefenseConfig(name=name, **(cfg or {})) for name, cfg in raw.items()}


def load_env_file() -> None:
    env = ROOT / ".env"
    if env.exists():
        import os

        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def select(scenarios: list[Scenario], classes: list[str] | None, tasks: list[str] | None,
           limit_per_class: int | None, seed: int) -> list[Scenario]:
    out = [s for s in scenarios
           if (not classes or (s.attack_class or "benign") in classes)
           and (not tasks or s.task_id in tasks)]
    if limit_per_class:
        rng = random.Random(seed)
        buckets: dict[str, list[Scenario]] = defaultdict(list)
        for s in out:
            buckets[s.attack_class or "benign"].append(s)
        out = []
        for key in sorted(buckets):
            items = buckets[key]
            out.extend(rng.sample(items, min(limit_per_class, len(items))))
    return out


async def main_async(args: argparse.Namespace) -> Path:
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) if args.config else {}
    models = args.models or cfg.get("models", [])
    defense_names = args.defenses or cfg.get("defenses", ["none"])
    classes = args.classes or cfg.get("classes")
    tasks = args.tasks or cfg.get("tasks")
    limit = args.limit_per_class or cfg.get("limit_per_class")
    max_steps = cfg.get("max_steps", 8)
    run_name = args.run_name or cfg.get("run_name") or time.strftime("run-%Y%m%d-%H%M%S")
    out_dir = ROOT / "results" / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    defenses = load_defenses()
    scenarios = select(build_scenarios(), classes, tasks, limit, args.seed)
    results_file = out_dir / "episodes.jsonl"
    done = set()
    if results_file.exists():  # resume
        for line in results_file.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["model"], r["defense"], r["scenario_id"]))

    total = len(models) * len(defense_names) * len(scenarios)
    print(f"run={run_name} models={models} defenses={defense_names} scenarios={len(scenarios)} total={total}")
    i = 0
    for model_spec in models:
        provider = make_provider(model_spec)
        guard = make_provider(model_spec) if any(defenses[d].llm_guard for d in defense_names) else None
        for dname in defense_names:
            dcfg = defenses[dname]
            for sc in scenarios:
                i += 1
                if (provider.name, dname, sc.id) in done:
                    continue
                res: EpisodeResult = await run_episode(sc, provider, dcfg, out_dir / provider.name.replace(":", "_") / dname,
                                                       guard=guard, max_steps=max_steps)
                with results_file.open("a", encoding="utf-8") as f:
                    f.write(res.model_dump_json() + "\n")
                flag = "ATTACK-OK" if res.attack_success else ("benign" if res.attack_success is None else "resisted")
                print(f"[{i}/{total}] {provider.name} {dname} {sc.id}: utility={res.utility} {flag} "
                      f"steps={res.steps} {res.wall_time_s:.0f}s {res.status}", flush=True)
        await provider.aclose()
        if guard:
            await guard.aclose()
    write_summary(out_dir)
    return out_dir


def write_summary(out_dir: Path) -> None:
    rows = [json.loads(l) for l in (out_dir / "episodes.jsonl").read_text(encoding="utf-8").splitlines()]
    df = pd.DataFrame(rows)
    overall = summarize(df, ["model", "defense"])
    by_class = summarize(df, ["model", "defense", "attack_class"])
    overall.to_csv(out_dir / "summary_overall.csv", index=False)
    by_class.to_csv(out_dir / "summary_by_class.csv", index=False)
    md = ["# Results summary", "", "## Overall (per model x defense)", "",
          overall.round(3).to_markdown(index=False), "", "## ASR (%) by attack class", "",
          per_class(df).to_markdown(), ""]
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config")
    p.add_argument("--models", nargs="+")
    p.add_argument("--defenses", nargs="+")
    p.add_argument("--classes", nargs="+", help="attack classes to run, plus 'benign'")
    p.add_argument("--tasks", nargs="+")
    p.add_argument("--limit-per-class", type=int)
    p.add_argument("--run-name")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--summarize-only", help="recompute summary for an existing results dir")
    args = p.parse_args()
    load_env_file()
    if args.summarize_only:
        write_summary(Path(args.summarize_only))
        return
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
