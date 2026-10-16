"""LLM provider interface and shared helpers."""

from __future__ import annotations

import json
import re
import uuid
from abc import ABC, abstractmethod
from typing import Any

from mcpguard.contracts import LLMResponse, ToolCall, ToolSpec


class Provider(ABC):
    name: str

    @abstractmethod
    async def chat(self, messages: list[dict[str, Any]], tools: list[ToolSpec]) -> LLMResponse: ...

    async def aclose(self) -> None:  # pragma: no cover - optional
        return None


def tools_to_openai(tools: list[ToolSpec]) -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {"name": t.name, "description": t.description, "parameters": t.input_schema},
        }
        for t in tools
    ]


def new_call_id() -> str:
    return "call_" + uuid.uuid4().hex[:12]


_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def parse_text_tool_call(content: str, tool_names: set[str]) -> ToolCall | None:
    """Recover a tool call that a small model emitted as plain text instead of a native call.

    Handles ``{"name": ..., "arguments": {...}}`` optionally wrapped in code fences or
    ``<tool_call>`` tags. Returns None unless the name matches an available tool.
    """
    if not content:
        return None
    cleaned = re.sub(r"</?tool_call>|```(?:json)?", "", content)
    for match in _JSON_BLOCK.finditer(cleaned):
        candidate = match.group(0)
        # try progressively shorter suffixes in case of trailing prose
        for end in range(len(candidate), 1, -1):
            if candidate[end - 1] != "}":
                continue
            try:
                obj = json.loads(candidate[:end])
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                name = obj.get("name") or obj.get("function") or obj.get("tool")
                args = obj.get("arguments", obj.get("parameters", obj.get("args", {})))
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}
                if isinstance(name, str) and name in tool_names and isinstance(args, dict):
                    return ToolCall(id=new_call_id(), name=name, arguments=args)
            break
    return None
