"""Plot a run's results: ASR per attack class, and the security-utility trade-off.

    python -m mcpguard.eval.plots results/phase1-baseline-local

Reads results/<run_name>/episodes.jsonl and writes asr_by_class.png and
security_utility.png next to it. Infra errors are excluded, as in metrics.py.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: only ever writes files
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CLASSES = ["PI", "NC", "PM", "OP", "UI", "FE", "TT", "RI", "PE", "CD"]
# fixed categorical order, so a series keeps its color across runs with the same models
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK_MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def load(run_dir: Path) -> pd.DataFrame:
    df = pd.read_json(run_dir / "episodes.jsonl", lines=True)
    return df[df["status"] != "error"]


def short_model(model: str) -> str:
    """'ollama:qwen2.5:1.5b' -> 'qwen2.5:1.5b', 'groq:openai/gpt-oss-20b' -> 'gpt-oss-20b'."""
    return model.split(":", 1)[-1].rsplit("/", 1)[-1]


def _style(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(INK_MUTED)
    ax.tick_params(colors=INK_MUTED)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def asr_by_class(df: pd.DataFrame, out: Path) -> None:
    attacked = df[df["attack_id"].notna()].copy()
    # one bar per model; if the run has several defenses, split by them too rather than averaging
    if attacked["defense"].nunique() > 1:
        attacked["series"] = attacked["model"].map(short_model) + " / " + attacked["defense"]
    else:
        attacked["series"] = attacked["model"].map(short_model)
    asr = (attacked.pivot_table(index="attack_class", columns="series", values="attack_success",
                                aggfunc="mean") * 100).reindex(CLASSES)

    series = list(asr.columns)
    width = 0.8 / len(series)
    x = np.arange(len(CLASSES))
    fig, ax = plt.subplots(figsize=(max(8, 1.1 * len(CLASSES) * max(1, len(series) / 2)), 4.5))
    for i, name in enumerate(series):
        xs = x - 0.4 + width * (i + 0.5)
        ax.bar(xs, asr[name], width * 0.9, label=name, color=PALETTE[i % len(PALETTE)])
        # a 0% bar has no height, so mark it to tell it apart from a class that wasn't run
        for xi, v in zip(xs, asr[name]):
            if v == 0:
                ax.text(xi, 1, "0", ha="center", va="bottom", fontsize=7, color=INK_MUTED)
    ax.set_xticks(x, CLASSES)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Attack success rate (%)", color=INK)
    ax.set_xlabel("Attack class", color=INK)
    ax.set_title("ASR by attack class", color=INK, loc="left")
    _style(ax)
    ax.legend(frameon=False, ncol=min(len(series), 3), loc="upper right")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def security_utility(df: pd.DataFrame, out: Path) -> None:
    keys = ["model", "defense"]
    attacked = df[df["attack_id"].notna()]
    benign = df[df["attack_id"].isna()]
    pts = pd.concat([
        benign.groupby(keys)["utility"].mean().mul(100).rename("BU"),
        attacked.groupby(keys)["attack_success"].mean().mul(100).rename("ASR"),
    ], axis=1).reset_index()
    missing = pts[pts["BU"].isna() | pts["ASR"].isna()]
    for _, r in missing.iterrows():
        print(f"skipping {r['model']} / {r['defense']}: no benign or no attacked episodes", file=sys.stderr)
    pts = pts.dropna(subset=["BU", "ASR"])

    models = sorted(df["model"].unique())
    fig, ax = plt.subplots(figsize=(7, 5))
    for _, r in pts.iterrows():
        ax.scatter(r["BU"], r["ASR"], s=60, color=PALETTE[models.index(r["model"]) % len(PALETTE)],
                   edgecolors="white", linewidths=1.5, zorder=3)
    # points at identical coordinates share one label instead of overprinting
    for (bu, asr), grp in pts.groupby(["BU", "ASR"]):
        label = "\n".join(f"{short_model(m)} / {d}" for m, d in zip(grp["model"], grp["defense"]))
        right = bu > 60  # put labels on the left of points near the right edge
        ax.annotate(label, (bu, asr), xytext=(-8 if right else 8, 0), textcoords="offset points",
                    ha="right" if right else "left", va="center", fontsize=9, color=INK)
    ax.set_xlim(-5, 115)
    ax.set_ylim(-5, 105)
    ax.set_xlabel("Benign utility (%)  ->  better", color=INK)
    ax.set_ylabel("ASR (%)  ->  worse", color=INK)
    ax.set_title("Security-utility trade-off (best: bottom right)", color=INK, loc="left")
    _style(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_dir", type=Path, help="results/<run_name> folder containing episodes.jsonl")
    args = ap.parse_args(argv)
    df = load(args.run_dir)
    for name, fn in [("asr_by_class.png", asr_by_class), ("security_utility.png", security_utility)]:
        fn(df, args.run_dir / name)
        print(f"wrote {args.run_dir / name}")


if __name__ == "__main__":
    main()
