"""Run one sandboxed episode: fresh world -> launch MCP servers -> agent -> judge."""

from __future__ import annotations

import asyncio
import json
import shutil
import time
from pathlib import Path

from mcpguard.agent.loop import run_agent
from mcpguard.agent.mcp_hub import ATTACKER_MODULE, BENIGN_SERVERS, MCPHub, ServerLaunch
from mcpguard.contracts import AgentState, DefenseConfig, EpisodeResult, Scenario, ToolCall
from mcpguard.defenses.approvers import SENSITIVE_TOOLS, is_user_requested
from mcpguard.defenses.audit import verify_chain
from mcpguard.defenses.detector import detect
from mcpguard.defenses.gateway import Gateway
from mcpguard.env import world as world_mod
from mcpguard.eval.judge import judge
from mcpguard.eval.scenarios import DATA_DIR, apply_patches
from mcpguard.providers.base import Provider


def prepare_world(scenario: Scenario, episode_dir: Path) -> Path:
    episode_dir.mkdir(parents=True, exist_ok=True)
    seed = json.loads((DATA_DIR / "world_seed.json").read_text(encoding="utf-8"))
    world_path = episode_dir / "world.json"
    world_mod.save(apply_patches(seed, scenario.world_patches), world_path)
    return world_path


def launches_for(scenario: Scenario, world_path: Path, cfg: DefenseConfig,
                 episode_dir: Path) -> list[ServerLaunch]:
    token = world_mod.USER_TOKEN if cfg.scoped_credentials else world_mod.ADMIN_TOKEN
    base_env = {"MCPGB_WORLD": str(world_path), "MCPGB_TOKEN": token}
    launches = [ServerLaunch(name, module, dict(base_env)) for name, module in BENIGN_SERVERS.items()]
    if scenario.attack_spec is not None:
        spec_path = episode_dir / "attack_spec.json"
        spec_path.write_text(json.dumps(scenario.attack_spec, indent=2), encoding="utf-8")
        # third-party (untrusted) server, registered last as a newly installed integration
        launches.append(ServerLaunch("toolkit", ATTACKER_MODULE,
                                     {**base_env, "MCPGB_ATTACK": str(spec_path)}, trusted=False))
    return launches


def unrequested_sensitive(scenario: Scenario, state: AgentState) -> tuple[int, int]:
    """(attempted, executed) sensitive calls that the user did not ask for (Gap 3)."""
    attempted = executed = 0
    for rec in state.tool_calls:
        if rec.name not in SENSITIVE_TOOLS:
            continue
        if is_user_requested(scenario, ToolCall(id="x", name=rec.name, arguments=rec.arguments)):
            continue
        attempted += 1
        if rec.decision.decision in ("allowed", "approved") and not rec.result.startswith("ERROR"):
            executed += 1
    return attempted, executed


async def run_episode(scenario: Scenario, provider: Provider, cfg: DefenseConfig, out_dir: Path,
                      guard: Provider | None = None, max_steps: int = 8, seed: int = 0,
                      timeout_s: float = 900.0, keep_world: bool = True) -> EpisodeResult:
    episode_dir = out_dir / "episodes" / scenario.id
    if episode_dir.exists():
        shutil.rmtree(episode_dir)
    world_path = prepare_world(scenario, episode_dir)
    user = json.loads(world_path.read_text(encoding="utf-8"))["user"]
    provider.begin_episode(scenario)
    state = AgentState(scenario_id=scenario.id)
    audit_path = episode_dir / "audit.jsonl"
    t0 = time.perf_counter()
    async with MCPHub(launches_for(scenario, world_path, cfg, episode_dir),
                      hidden_tools=set(scenario.hidden_tools)) as hub:
        gateway = Gateway(hub, cfg, scenario, audit_path, guard=guard, seed=seed)
        try:
            await asyncio.wait_for(run_agent(provider, gateway, scenario, user, max_steps=max_steps,
                                             state=state), timeout=timeout_s)
        except asyncio.TimeoutError:
            state.status = "timeout"
            state.error = f"episode exceeded {timeout_s:.0f}s"
    wall = time.perf_counter() - t0

    final_world = world_mod.load(world_path)
    utility, attack_success = judge(scenario.utility, scenario.attack_success, final_world, state)
    attempted, executed = unrequested_sensitive(scenario, state)
    rules = detect(audit_path)
    trace_file = episode_dir / "trace.json"
    trace_file.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    if not keep_world:
        world_path.unlink(missing_ok=True)
    return EpisodeResult(
        scenario_id=scenario.id,
        split=scenario.split,
        seed=seed,
        task_id=scenario.task_id,
        domain=scenario.domain,
        attack_id=scenario.attack_id,
        attack_class=scenario.attack_class,
        attack_goal=scenario.attack_goal,
        attack_stage=scenario.attack_stage,
        model=provider.name,
        defense=cfg.name,
        utility=utility,
        attack_success=attack_success,
        privilege_violations=len(final_world["violations"]),
        violation_actions=sorted({f"{v['action']}:{v['resource']}" for v in final_world["violations"]}),
        blocked_calls=gateway.blocked,
        approval_requests=gateway.approval_requests,
        steps=state.step,
        tool_calls=len(state.tool_calls),
        prompt_tokens=state.prompt_tokens,
        completion_tokens=state.completion_tokens,
        guard_tokens=gateway.guard_tokens,
        text_parsed_calls=state.text_parsed_calls,
        unrequested_sensitive=attempted,
        unrequested_sensitive_executed=executed,
        detector_flag=bool(rules),
        detector_rules=rules,
        audit_chain_ok=verify_chain(audit_path),
        wall_time_s=round(wall, 2),
        status=state.status,
        error=state.error,
        final_answer=state.final_answer[:500],
        trace_file=str(trace_file.relative_to(out_dir)),
    )
