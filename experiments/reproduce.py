"""Reproduce the Phase 2 experiments and rebuild every table/figure of the paper.

    python experiments/reproduce.py reference     # E0: deterministic agents, no LLM (~1 h on 6 cores)
    python experiments/reproduce.py local         # E1-E5 on local Ollama models (long: see README)
    python experiments/reproduce.py api           # E1-E5 on Groq/OpenRouter models (needs keys)
    python experiments/reproduce.py report        # tables + figures + failure analysis from saved runs
    python experiments/reproduce.py all           # reference + local + report

Every step is resumable: re-running skips episodes that are already in episodes.jsonl.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "experiments" / "configs"
RESULTS = ROOT / "results"

STAGES = {
    "reference": ["e0_reference_agents.yaml"],
    # order matters only for what finishes first; runs share results/phase2-local
    "local": ["e1_baseline_local.yaml", "e2_basepaper_local.yaml", "e3_proposed_local.yaml",
              "e4_gaps_local.yaml", "e5_ablation_local.yaml", "e4b_approvers_local.yaml",
              "e_secondary_local.yaml"],
    "api": ["api_main.yaml", "api_msb_overlap.yaml", "api_gaps.yaml"],
}
# (run folder, model, defense) for the failure analysis of the proposed system
FAILURE_TARGETS = [("phase2-local", "ollama:qwen2.5:3b", "full"),
                   ("phase2-local", "ollama:qwen2.5:3b", "none"),
                   ("phase2-reference", "agent:gullible", "full"),
                   ("phase2-api", "groq:openai/gpt-oss-120b", "full")]


def sh(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def run_stage(stage: str) -> None:
    for cfg in STAGES[stage]:
        sh("-m", "mcpguard.eval.run", "--config", str(CFG / cfg))


def report() -> None:
    runs = [str(RESULTS / r) for r in ("phase2-reference", "phase2-local", "phase2-api")
            if (RESULTS / r / "episodes.jsonl").exists()]
    sh("-m", "mcpguard.eval.report", "--runs", *runs, "--out", str(RESULTS / "paper"))
    for run, model, defense in FAILURE_TARGETS:
        if (RESULTS / run / "episodes.jsonl").exists():
            slug = model.split(":", 1)[-1].replace("/", "-").replace(":", "-")
            sh("-m", "mcpguard.eval.failures", str(RESULTS / run), "--model", model, "--defense", defense,
               "--out", str(RESULTS / "paper" / f"failures_{slug}_{defense}.md"))
    for run in runs:
        sh("-m", "mcpguard.eval.plots", run)
    sh(str(ROOT / "experiments" / "sample_logs.py"))
    # the paper \input's tables and figures from paper/generated/
    import shutil
    gen = ROOT / "paper" / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    for f in list((RESULTS / "paper").glob("*.tex")) + list((RESULTS / "paper").glob("*.png")):
        shutil.copy2(f, gen / f.name)
    shutil.copy2(ROOT / "docs" / "architecture.png", gen / "architecture.png")
    print(f"copied tables and figures to {gen}")


def main() -> None:
    targets = sys.argv[1:] or ["all"]
    for t in targets:
        if t == "all":
            run_stage("reference")
            run_stage("local")
            report()
        elif t == "report":
            report()
        elif t in STAGES:
            run_stage(t)
        else:
            raise SystemExit(f"unknown target {t!r}; choose from reference, local, api, report, all")


if __name__ == "__main__":
    main()
