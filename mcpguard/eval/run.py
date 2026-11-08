"""CLI: run the benchmark for a set of models x defenses x seeds.

    python -m mcpguard.eval.run --config experiments/configs/e1_baseline_local.yaml
    python -m mcpguard.eval.run --models ollama:qwen2.5:3b --defenses none full --split test --seeds 0 1 2
    python -m mcpguard.eval.run --models agent:gullible --defenses none full --split all

Config keys (all optional, CLI flags override): run_name, models, defenses, split
(dev|test|all, default test), classes, tasks, limit_per_class, seeds, temperature,
max_steps, concurrency, episode_timeout, retries.

Runs are resumable: an episode already in episodes.jsonl (same model, defense, seed,
scenario) is skipped, so several experiment configs can share one run folder.
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
from mcpguard.eval.metrics import load_episodes, per_class, summarize
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


def _slug(text: str) -> str:
    return text.replace(":", "_").replace("/", "_")


async def main_async(args: argparse.Namespace) -> Path:
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) if args.config else {}
    models = args.models or cfg.get("models", [])
    defense_names = args.defenses or cfg.get("defenses", ["none"])
    classes = args.classes or cfg.get("classes")
    tasks = args.tasks or cfg.get("tasks")
    split = args.split or cfg.get("split", "test")
    limit = args.limit_per_class or cfg.get("limit_per_class")
    seeds = args.seeds if args.seeds is not None else cfg.get("seeds", [0])
    temperature = args.temperature if args.temperature is not None else cfg.get("temperature", 0.0)
    max_steps = cfg.get("max_steps", 8)
    concurrency = args.concurrency or cfg.get("concurrency", 1)
    timeout_s = cfg.get("episode_timeout", 900)
    retries = cfg.get("retries", 2)
    run_name = args.run_name or cfg.get("run_name") or time.strftime("run-%Y%m%d-%H%M%S")
    out_dir = ROOT / "results" / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    defenses = load_defenses()
    unknown = [d for d in defense_names if d not in defenses]
    if unknown:
        raise SystemExit(f"unknown defense(s) {unknown}; see configs/defenses.yaml")
    pool = [s for s in build_scenarios() if split == "all" or s.split == split]
    scenarios = select(pool, classes, tasks, limit, args.seed)
    results_file = out_dir / "episodes.jsonl"
    done = set()
    if results_file.exists():  # resume
        for line in results_file.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r["status"] != "error":  # failed episodes are re-run on resume
                done.add((r["model"], r["defense"], r.get("seed", 0), r["scenario_id"]))

    jobs = [(m, d, seed, sc) for m in models for d in defense_names for seed in seeds for sc in scenarios]
    todo = [j for j in jobs if (make_provider(j[0]).name if j[0].startswith("agent:") else j[0],
                                j[1], j[2], j[3].id) not in done]
    print(f"run={run_name} split={split} models={models} defenses={defense_names} seeds={seeds} "
          f"T={temperature} scenarios={len(scenarios)} jobs={len(jobs)} todo={len(todo)}", flush=True)

    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    counter = {"n": len(jobs) - len(todo)}

    async def one(model_spec: str, dname: str, seed: int, sc: Scenario) -> None:
        async with sem:
            dcfg = defenses[dname]
            res: EpisodeResult | None = None
            for attempt in range(retries + 1):
                kwargs = {} if model_spec.startswith("agent:") else {"temperature": temperature, "seed": seed}
                provider = make_provider(model_spec, **kwargs)
                # the MCIP-style guard is a classifier: same model, greedy decoding
                guard = (make_provider(model_spec, temperature=0.0, seed=seed)
                         if dcfg.llm_guard and not model_spec.startswith("agent:") else None)
                try:
                    res = await run_episode(
                        sc, provider, dcfg, out_dir / _slug(provider.name) / dname / f"seed{seed}",
                        guard=guard, max_steps=max_steps, seed=seed, timeout_s=timeout_s)
                except Exception as e:  # e.g. a server failed to start; retry, then record
                    res = failed_episode(sc, provider.name, dname, e, seed)
                finally:
                    await provider.aclose()
                    if guard:
                        await guard.aclose()
                res.retries = attempt
                if res.status != "error":
                    break
            assert res is not None
            async with lock:
                with results_file.open("a", encoding="utf-8") as f:
                    f.write(res.model_dump_json() + "\n")
                counter["n"] += 1
            flag = "ATTACK-OK" if res.attack_success else ("benign" if res.attack_success is None else "resisted")
            print(f"[{counter['n']}/{len(jobs)}] {res.model} {dname} s{seed} {sc.id}: utility={res.utility} "
                  f"{flag} steps={res.steps} {res.wall_time_s:.0f}s {res.status}", flush=True)

    await asyncio.gather(*(one(*j) for j in todo))
    write_summary(out_dir)
    return out_dir


def failed_episode(sc: Scenario, model: str, defense: str, exc: BaseException, seed: int = 0) -> EpisodeResult:
    return EpisodeResult(
        scenario_id=sc.id, split=sc.split, seed=seed, attack_stage=sc.attack_stage, task_id=sc.task_id, domain=sc.domain, attack_id=sc.attack_id,
        attack_class=sc.attack_class, attack_goal=sc.attack_goal, model=model, defense=defense,
        utility=False, attack_success=False if sc.attack_id else None, privilege_violations=0,
        blocked_calls=0, approval_requests=0, steps=0, tool_calls=0, prompt_tokens=0,
        completion_tokens=0, wall_time_s=0.0, status="error", error=f"{type(exc).__name__}: {exc}"[:500],
    )


def write_summary(out_dir: Path) -> None:
    df = load_episodes(out_dir)
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
    p.add_argument("--split", choices=["dev", "test", "all"])
    p.add_argument("--seeds", type=int, nargs="+", help="decoding seeds (one run per seed)")
    p.add_argument("--temperature", type=float)
    p.add_argument("--concurrency", type=int, help="episodes run in parallel")
    p.add_argument("--seed", type=int, default=0, help="seed for --limit-per-class sampling")
    p.add_argument("--summarize-only", help="recompute summary for an existing results dir")
    args = p.parse_args()
    load_env_file()
    if args.summarize_only:
        write_summary(Path(args.summarize_only))
        return
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
