"""Run one scenario live and show what the agent did, what the gateway decided and the verdict.

    python -m mcpguard.demo --list                                   # scenario ids
    python -m mcpguard.demo --scenario T09-RI-transfer --model ollama:qwen2.5:3b --defense none
    python -m mcpguard.demo --scenario T09-RI-transfer --model ollama:qwen2.5:3b --defense full
    python -m mcpguard.demo --scenario T01-PI-exfil --model agent:gullible --defense scoped

Artifacts (trace.json, audit.jsonl, world.json) are written to results/demo/.
"""

from __future__ import annotations

import argparse
import sys
import asyncio
import json
from pathlib import Path

from mcpguard.eval.run import ROOT, load_defenses, load_env_file
from mcpguard.eval.runner import run_episode
from mcpguard.eval.scenarios import build_scenarios
from mcpguard.eval.trace import render
from mcpguard.providers import make_provider


async def demo(scenario_id: str, model: str, defense: str, seed: int, temperature: float) -> None:
    scenarios = {s.id: s for s in build_scenarios()}
    if scenario_id not in scenarios:
        raise SystemExit(f"unknown scenario {scenario_id!r}; use --list")
    sc = scenarios[scenario_id]
    cfg = load_defenses()[defense]
    llm = not model.startswith("agent:")
    provider = make_provider(model, **({"temperature": temperature, "seed": seed} if llm else {}))
    guard = make_provider(model, temperature=0.0, seed=seed) if cfg.llm_guard and llm else None
    out = ROOT / "results" / "demo"
    print(f"Scenario {sc.id} ({sc.attack_class or 'benign'}, stage={sc.attack_stage or '-'}, goal={sc.attack_goal or '-'})")
    print(f"Defense '{defense}': {cfg.model_dump(exclude={'name'})}\n")
    try:
        res = await run_episode(sc, provider, cfg, out, guard=guard, seed=seed)
    finally:
        await provider.aclose()
        if guard:
            await guard.aclose()
    print(render(json.loads((out / res.trace_file).read_text(encoding="utf-8"))))
    print("\nVERDICT")
    print(f"  user task completed : {res.utility}")
    print(f"  attack succeeded    : {res.attack_success if res.attack_success is not None else 'n/a (benign)'}")
    print(f"  privilege violations: {res.privilege_violations} {res.violation_actions}")
    print(f"  gateway blocks      : {res.blocked_calls}, human approvals asked: {res.approval_requests}")
    print(f"  audit-log detector  : {'FLAGGED ' + ', '.join(res.detector_rules) if res.detector_flag else 'clean'}"
          f" (hash chain {'ok' if res.audit_chain_ok else 'BROKEN'})")
    print(f"  artifacts           : {Path(out / res.trace_file).parent}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenario")
    ap.add_argument("--model", default="ollama:qwen2.5:3b")
    ap.add_argument("--defense", default="full")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    load_env_file()
    if args.list or not args.scenario:
        for s in build_scenarios():
            print(f"{s.id:24s} {s.split:5s} {s.attack_class or 'benign':7s} {s.user_prompt[:70]}")
        return
    asyncio.run(demo(args.scenario, args.model, args.defense, args.seed, args.temperature))


if __name__ == "__main__":
    main()
