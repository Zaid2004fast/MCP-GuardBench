"""Structured contracts shared across the agent, gateway and evaluator."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# ----------------------------------------------------------------------- scenarios


class Predicate(BaseModel):
    """A check evaluated over the final world state, the trace and the final answer."""

    type: str
    args: dict[str, Any] = Field(default_factory=dict)


class Scenario(BaseModel):
    id: str
    task_id: str
    domain: str
    user_prompt: str
    attack_id: str | None = None  # None = benign episode
    attack_class: str | None = None
    attack_goal: str | None = None
    attack_spec: dict[str, Any] | None = None  # passed to attacker_server
    hidden_tools: list[str] = Field(default_factory=list)  # benign tools replaced by attacker
    world_patches: list[dict[str, Any]] = Field(default_factory=list)  # data-plane injections
    utility: list[Predicate]
    attack_success: list[Predicate] = Field(default_factory=list)  # any() -> attack succeeded


# --------------------------------------------------------------------------- tools


class ToolSpec(BaseModel):
    name: str
    server: str
    description: str
    input_schema: dict[str, Any]


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]


class LLMResponse(BaseModel):
    content: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_s: float = 0.0
    parsed_from_text: bool = False  # tool call recovered from plain-text output


Decision = Literal["allowed", "blocked", "approved", "denied"]


class GatewayDecision(BaseModel):
    decision: Decision
    layer: str | None = None  # which defense produced the decision
    reason: str = ""


class ToolCallRecord(BaseModel):
    step: int
    name: str
    server: str | None
    arguments: dict[str, Any]
    result: str
    decision: GatewayDecision
    latency_s: float = 0.0


# ------------------------------------------------------------------------ agent


class AgentState(BaseModel):
    """Full observable state of one agent episode."""

    scenario_id: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
    step: int = 0
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    final_answer: str = ""
    status: Literal["running", "done", "max_steps", "error"] = "running"
    error: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    llm_latency_s: float = 0.0
    text_parsed_calls: int = 0


# ------------------------------------------------------------------------ defenses


class DefenseConfig(BaseModel):
    name: str = "none"
    safety_prompt: bool = False  # MCP-SafetyBench-style prompt defense
    llm_guard: bool = False  # MCIP-style detector (base-paper defense)
    allowlist: bool = False  # pinned (server, tool, description-hash) registry
    scoped_credentials: bool = False  # servers get the user's least-privilege token
    hitl: bool = False  # human approval before sensitive actions
    hitl_approver: Literal["oracle", "deny_all", "approve_all"] = "oracle"
    audit: bool = True  # tamper-evident audit log (always on, detection is post hoc)


# ------------------------------------------------------------------------- results


class EpisodeResult(BaseModel):
    scenario_id: str
    task_id: str
    domain: str
    attack_id: str | None
    attack_class: str | None
    attack_goal: str | None
    model: str
    defense: str
    utility: bool
    attack_success: bool | None
    privilege_violations: int
    blocked_calls: int
    approval_requests: int
    steps: int
    tool_calls: int
    prompt_tokens: int
    completion_tokens: int
    wall_time_s: float
    status: str
    error: str | None = None
    final_answer: str = ""
    trace_file: str | None = None
