"""Statistics for the paper: bootstrap confidence intervals and McNemar's exact test.

* ``bootstrap_ci``  - 95% percentile CI of a rate, resampling episodes with replacement.
* ``mcnemar``       - exact two-sided McNemar test for two defenses evaluated on the same
                      paired episodes (same model, scenario and seed).
* ``paired_compare``- convenience wrapper over an episodes DataFrame.
"""

from __future__ import annotations

from math import comb

import numpy as np
import pandas as pd


def bootstrap_ci(values, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    x = np.asarray(values, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n_boot, len(x)), replace=True).mean(axis=1)
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def mcnemar(b: int, c: int) -> float:
    """Exact two-sided p-value. b = pairs where only A is positive, c = only B positive."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, p)


def paired_compare(df: pd.DataFrame, model: str, defense_a: str, defense_b: str,
                   col: str = "attack_success", attacked_only: bool = True) -> dict:
    """Compare two defenses on episodes paired by (scenario, seed) for one model."""
    d = df[(df["model"] == model) & (df["status"] != "error")]
    if attacked_only:
        d = d[d["attack_id"].notna()]
    a = d[d["defense"] == defense_a].set_index(["scenario_id", "seed"])[col].astype(bool)
    b = d[d["defense"] == defense_b].set_index(["scenario_id", "seed"])[col].astype(bool)
    a, b = a.align(b, join="inner")
    only_a = int((a & ~b).sum())
    only_b = int((~a & b).sum())
    return {"model": model, "A": defense_a, "B": defense_b, "metric": col, "n_pairs": len(a),
            "rate_A": float(a.mean()) if len(a) else float("nan"),
            "rate_B": float(b.mean()) if len(b) else float("nan"),
            "only_A": only_a, "only_B": only_b, "p_mcnemar": mcnemar(only_a, only_b)}
