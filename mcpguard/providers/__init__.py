"""Model providers. Spec format: ``<backend>:<model>``, e.g. ``ollama:qwen2.5:3b``,
``groq:llama-3.3-70b-versatile``, ``openrouter:qwen/qwen3-32b``.

Deterministic reference agents (no LLM): ``agent:gullible`` follows every injected
instruction it can see (worst case), ``agent:ideal`` never does (utility ceiling)."""

from __future__ import annotations

from mcpguard.providers.base import Provider


def make_provider(spec: str, **kwargs) -> Provider:
    backend, _, model = spec.partition(":")
    if backend == "ollama":
        from mcpguard.providers.ollama import OllamaProvider

        return OllamaProvider(model, **kwargs)
    if backend == "agent":
        from mcpguard.providers.reference import ReferenceAgent

        return ReferenceAgent(gullible=(model == "gullible"))
    if backend in ("groq", "openrouter", "openai-compat"):
        from mcpguard.providers.openai_compat import OpenAICompatProvider

        return OpenAICompatProvider(backend, model, **kwargs)
    raise ValueError(f"unknown provider backend {backend!r} in {spec!r}")
