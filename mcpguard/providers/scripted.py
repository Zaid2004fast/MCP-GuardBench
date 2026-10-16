"""Deterministic providers for tests and pipeline smoke runs (no LLM needed)."""

from __future__ import annotations

from typing import Any

from mcpguard.contracts import LLMResponse, ToolCall, ToolSpec
from mcpguard.providers.base import Provider, new_call_id


class ScriptedProvider(Provider):
    """Replays a fixed list of actions: ``{"tool": name, "args": {...}}`` or ``{"final": text}``."""

    def __init__(self, script: list[dict[str, Any]]):
        self.name = "scripted"
        self.script = list(script)

    async def chat(self, messages: list[dict[str, Any]], tools: list[ToolSpec]) -> LLMResponse:
        if not self.script:
            return LLMResponse(content="(script exhausted)")
        action = self.script.pop(0)
        if "final" in action:
            return LLMResponse(content=action["final"])
        return LLMResponse(tool_calls=[ToolCall(id=new_call_id(), name=action["tool"],
                                                arguments=action.get("args", {}))])
