"""Local open-weight models served by Ollama (native tool calling)."""

from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx

from mcpguard.contracts import LLMResponse, ToolCall, ToolSpec
from mcpguard.providers.base import Provider, new_call_id, parse_text_tool_call, tools_to_openai


def _to_ollama_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    id_to_name: dict[str, str] = {}
    for m in messages:
        if m["role"] == "assistant" and m.get("tool_calls"):
            calls = []
            for c in m["tool_calls"]:
                id_to_name[c["id"]] = c["function"]["name"]
                args = c["function"]["arguments"]
                calls.append({"function": {"name": c["function"]["name"],
                                           "arguments": json.loads(args) if isinstance(args, str) else args}})
            out.append({"role": "assistant", "content": m.get("content") or "", "tool_calls": calls})
        elif m["role"] == "tool":
            out.append({"role": "tool", "content": m["content"],
                        "tool_name": id_to_name.get(m.get("tool_call_id", ""), "")})
        else:
            out.append({"role": m["role"], "content": m.get("content") or ""})
    return out


class OllamaProvider(Provider):
    def __init__(self, model: str, host: str | None = None, temperature: float = 0.0,
                 num_ctx: int = 8192, timeout: float = 900.0):
        self.model = model
        self.name = f"ollama:{model}"
        self.host = host or os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.options = {"temperature": temperature, "num_ctx": num_ctx, "seed": 0}
        self.client = httpx.AsyncClient(timeout=timeout)

    async def chat(self, messages: list[dict[str, Any]], tools: list[ToolSpec]) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": _to_ollama_messages(messages),
            "tools": tools_to_openai(tools),
            "stream": False,
            "options": self.options,
        }
        t0 = time.perf_counter()
        r = await self.client.post(f"{self.host}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
        latency = time.perf_counter() - t0
        msg = data.get("message", {})
        calls = [
            ToolCall(id=new_call_id(), name=c["function"]["name"],
                     arguments=c["function"].get("arguments") or {})
            for c in msg.get("tool_calls") or []
        ]
        content = msg.get("content") or ""
        parsed = False
        if not calls:
            recovered = parse_text_tool_call(content, {t.name for t in tools})
            if recovered:
                calls, parsed = [recovered], True
        return LLMResponse(
            content=content,
            tool_calls=calls,
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            latency_s=latency,
            parsed_from_text=parsed,
        )

    async def aclose(self) -> None:
        await self.client.aclose()
