"""Open-weight models behind any OpenAI-compatible endpoint (Groq, OpenRouter, vLLM...)."""

from __future__ import annotations

import asyncio
import json
import re
import os
import time
from typing import Any

import httpx

from mcpguard.contracts import LLMResponse, ToolCall, ToolSpec
from mcpguard.providers.base import Provider, new_call_id, parse_text_tool_call, tools_to_openai

ENDPOINTS = {
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "openai-compat": (os.environ.get("OPENAI_COMPAT_BASE_URL", ""), "OPENAI_COMPAT_API_KEY"),
}


class OpenAICompatProvider(Provider):
    def __init__(self, endpoint: str, model: str, temperature: float = 0.0, timeout: float = 120.0,
                 max_retries: int = 12):
        base_url, key_env = ENDPOINTS[endpoint]
        key = os.environ.get(key_env)
        if not key:
            raise RuntimeError(f"{key_env} is not set (see .env.example)")
        self.name = f"{endpoint}:{model}"
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout, headers={"Authorization": f"Bearer {key}"})

    async def chat(self, messages: list[dict[str, Any]], tools: list[ToolSpec]) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools_to_openai(tools),
            "tool_choice": "auto",
            "temperature": self.temperature,
            "seed": 0,
        }
        t0 = time.perf_counter()
        for attempt in range(self.max_retries):
            r = await self.client.post(f"{self.base_url}/chat/completions", json=payload)
            if r.status_code in (429, 500, 502, 503):
                wait = max(float(r.headers.get("retry-after", 0)), 2 ** min(attempt, 6))
                await asyncio.sleep(min(wait, 90))
                continue
            if r.status_code == 400 and "tool" in r.text.lower():
                # some providers reject malformed model-generated tool calls; surface as text
                return LLMResponse(content=f"[provider error] {r.text[:300]}",
                                   latency_s=time.perf_counter() - t0)
            r.raise_for_status()
            break
        else:
            r.raise_for_status()
        data = r.json()
        msg = data["choices"][0]["message"]
        calls = []
        for c in msg.get("tool_calls") or []:
            args = c["function"].get("arguments") or "{}"
            try:
                parsed_args = json.loads(args) if isinstance(args, str) else args
            except json.JSONDecodeError:
                parsed_args = {"_raw": args}
            calls.append(ToolCall(id=c.get("id") or new_call_id(), name=c["function"]["name"],
                                  arguments=parsed_args))
        content = re.sub(r"<think>.*?</think>", "", msg.get("content") or "", flags=re.DOTALL).strip()
        parsed = False
        if not calls:
            recovered = parse_text_tool_call(content, {t.name for t in tools})
            if recovered:
                calls, parsed = [recovered], True
        usage = data.get("usage") or {}
        return LLMResponse(
            content=content,
            tool_calls=calls,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            latency_s=time.perf_counter() - t0,
            parsed_from_text=parsed,
        )

    async def aclose(self) -> None:
        await self.client.aclose()
