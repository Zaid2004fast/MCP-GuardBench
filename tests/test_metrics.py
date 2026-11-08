"""Metric aggregation and statistics (deterministic, no servers)."""

import math

import pandas as pd

from mcpguard.eval.metrics import fmt, summarize, summarize_seeds
from mcpguard.eval.stats import bootstrap_ci, mcnemar, paired_compare


def ep(seed, sid, attacked, success, utility, defense="none", **kw):
    base = dict(model="m", defense=defense, seed=seed, scenario_id=sid, status="done",
                attack_id="A" if attacked else None, attack_class="PI" if attacked else None,
                attack_success=success if attacked else None, utility=utility, privilege_violations=0,
                blocked_calls=0, approval_requests=0, tool_calls=1, prompt_tokens=10, completion_tokens=5,
                guard_tokens=0, wall_time_s=1.0, text_parsed_calls=0, unrequested_sensitive=0,
                unrequested_sensitive_executed=0, detector_flag=False)
    base.update(kw)
    return base


def test_msb_metrics_and_seed_std():
    rows = []
    for seed, (s1, s2) in enumerate([(True, False), (True, True)]):
        rows += [ep(seed, "a1", True, s1, True), ep(seed, "a2", True, s2, False),
                 ep(seed, "b1", False, None, True)]
    df = pd.DataFrame(rows)
    per_seed = summarize(df, ["model", "defense", "seed"]).set_index("seed")
    assert per_seed.loc[0, "ASR"] == 0.5 and per_seed.loc[1, "ASR"] == 1.0
    assert per_seed.loc[0, "PUA"] == 0.5 and per_seed.loc[0, "NRP"] == 0.25
    assert per_seed.loc[0, "BU"] == 1.0
    agg = summarize_seeds(df, ["model", "defense"], ["ASR"]).iloc[0]
    assert agg["ASR_mean"] == 0.75 and math.isclose(agg["ASR_std"], math.sqrt(0.125))
    assert agg["n_seeds"] == 2


def test_errors_are_excluded_and_counted():
    df = pd.DataFrame([ep(0, "a1", True, True, True), ep(0, "a2", True, False, True, status="error")])
    row = summarize(df, ["model", "defense"]).iloc[0]
    assert row["ASR"] == 1.0 and row["errors"] == 1


def test_stop_rate_and_detector_metrics():
    df = pd.DataFrame([
        ep(0, "a1", True, True, True, unrequested_sensitive=1, unrequested_sensitive_executed=1, detector_flag=True),
        ep(0, "a2", True, False, True, unrequested_sensitive=1, detector_flag=True),
        ep(0, "a3", True, False, True),
        ep(0, "b1", False, None, True, detector_flag=True),
    ])
    row = summarize(df, ["model", "defense"]).iloc[0]
    assert row["stop_rate"] == 0.5 and row["unreq_exec_rate"] == 0.5
    assert row["det_recall"] == 1.0 and math.isclose(row["det_precision"], 1 / 3)
    assert row["det_fpr"] == 1.0


def test_mcnemar_and_bootstrap():
    assert mcnemar(0, 0) == 1.0
    assert math.isclose(mcnemar(0, 6), 2 / 64)
    lo, hi = bootstrap_ci([1, 0] * 50)
    assert lo < 0.5 < hi
    df = pd.DataFrame([ep(0, f"a{i}", True, True, True) for i in range(6)]
                      + [ep(0, f"a{i}", True, False, True, defense="full") for i in range(6)])
    res = paired_compare(df, "m", "none", "full")
    assert res["n_pairs"] == 6 and res["only_A"] == 6 and res["p_mcnemar"] < 0.05


def test_fmt():
    assert fmt(0.5543, 0.031) == "55.4 ± 3.1"
    assert fmt(float("nan")) == "n/a"
