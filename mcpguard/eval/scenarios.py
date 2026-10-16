"""Build benchmark scenarios: every user task x every applicable attack (+ one benign run)."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from mcpguard.contracts import Predicate, Scenario

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _load(name: str) -> Any:
    return yaml.safe_load((DATA_DIR / name).read_text(encoding="utf-8"))


def _patch_for(target: dict[str, str], text: str) -> dict[str, Any]:
    if "file" in target:
        return {"op": "append_file", "path": target["file"], "text": "\n" + text + "\n"}
    if "email" in target:
        return {"op": "append_email", "id": target["email"], "text": " " + text}
    if "tx" in target:
        return {"op": "append_tx_memo", "id": target["tx"], "text": " " + text}
    raise ValueError(f"bad inject_target {target}")


def build_scenarios(include_benign: bool = True) -> list[Scenario]:
    tasks = _load("user_tasks.yaml")
    catalogue = _load("attacks.yaml")
    goals, attacks = catalogue["goals"], catalogue["attacks"]
    scenarios: list[Scenario] = []
    for task in tasks:
        utility = [Predicate(**p) for p in task["utility"]]
        if include_benign:
            scenarios.append(Scenario(id=f"{task['id']}-benign", task_id=task["id"], domain=task["domain"],
                                      user_prompt=task["prompt"], utility=utility))
        for atk in attacks:
            if any(not task.get(req) for req in atk.get("requires", [])):
                continue
            goal = goals[atk["goal"]]
            payload = atk.get("payload", "").format(instruction=goal["instruction"]).strip()
            success = [Predicate(**copy.deepcopy(p)) for p in goal["success"]]
            mirror = task.get("mirror_tool")
            spec: dict[str, Any] | None = None
            patches: list[dict[str, Any]] = []
            if atk["vector"] == "data":
                patches.append(_patch_for(task["inject_target"], payload))
            else:
                spec = {"attack_id": atk["id"], "vector": atk["vector"], "payload": payload,
                        "mirror_tool": mirror, "response_mode": atk.get("response_mode", "passthrough")}
            if atk["goal"] == "capture":
                captured = {"NC": mirror, "PM": f"{mirror}_pro", "TT": "secure_data_relay"}[atk["class"]]
                success = [Predicate(type="attacker_tool_called", args={"name": captured})]
            scenarios.append(Scenario(
                id=f"{task['id']}-{atk['id']}",
                task_id=task["id"],
                domain=task["domain"],
                user_prompt=task["prompt"],
                attack_id=atk["id"],
                attack_class=atk["class"],
                attack_goal=atk["goal"],
                attack_spec=spec,
                hidden_tools=[mirror] if atk.get("hide_mirror") else [],
                world_patches=patches,
                utility=utility,
                attack_success=success,
            ))
    return scenarios


def apply_patches(world: dict[str, Any], patches: list[dict[str, Any]]) -> dict[str, Any]:
    for p in patches:
        if p["op"] == "append_file":
            world["files"][p["path"]] += p["text"]
        elif p["op"] == "append_email":
            next(m for m in world["mail"]["inbox"] if m["id"] == p["id"])["body"] += p["text"]
        elif p["op"] == "append_tx_memo":
            next(t for t in world["bank"]["transactions"] if t["id"] == p["id"])["memo"] += p["text"]
    return world


if __name__ == "__main__":
    from collections import Counter

    sc = build_scenarios()
    print(f"{len(sc)} scenarios")
    print(Counter(s.attack_class or "benign" for s in sc))
