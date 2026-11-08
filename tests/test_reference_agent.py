"""Deterministic reference agents: every attack variant is reachable and judged correctly."""

import asyncio

import pytest

from mcpguard.contracts import DefenseConfig
from mcpguard.eval.runner import run_episode
from mcpguard.eval.scenarios import build_scenarios
from mcpguard.providers.reference import PLANS, ReferenceAgent

SCENARIOS = build_scenarios()
# one scenario per attack variant, on a task that every variant applies to
ONE_PER_VARIANT = {s.attack_id: s for s in SCENARIOS if s.task_id == "T01" and s.attack_id}


def run(sc, gullible, tmp_path, **defense):
    return asyncio.run(run_episode(sc, ReferenceAgent(gullible), DefenseConfig(name="t", **defense), tmp_path))


def test_every_task_has_a_plan():
    assert {s.task_id for s in SCENARIOS} == set(PLANS)


@pytest.mark.parametrize("attack_id", sorted(ONE_PER_VARIANT))
def test_gullible_agent_realises_every_attack_undefended(attack_id, tmp_path):
    r = run(ONE_PER_VARIANT[attack_id], True, tmp_path)
    assert r.attack_success is True, attack_id


@pytest.mark.parametrize("task_id", ["T01", "T09", "T11", "T15", "T16"])
def test_ideal_agent_completes_benign_tasks_under_full_defense(task_id, tmp_path):
    sc = next(s for s in SCENARIOS if s.id == f"{task_id}-benign")
    r = run(sc, False, tmp_path, allowlist=True, scoped_credentials=True, hitl=True)
    assert r.utility is True and r.privilege_violations == 0


def test_full_defense_stops_gullible_agent_on_injected_transfer(tmp_path):
    sc = next(s for s in SCENARIOS if s.id == "T09-RI-transfer")
    assert run(sc, True, tmp_path / "a").attack_success is True
    r = run(sc, True, tmp_path / "b", allowlist=True, scoped_credentials=True, hitl=True)
    assert r.attack_success is False and r.utility is True
