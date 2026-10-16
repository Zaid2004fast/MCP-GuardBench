"""MCP client hub: launches stdio MCP servers and exposes their tools as one namespace.

Like many real MCP hosts, the hub merges all servers' tools into a flat namespace and
the *last registered* server wins on a name clash. This is the behaviour that tool
shadowing / name-collision attacks exploit; the allowlist defense pins tools to servers.
"""

from __future__ import annotations

import os
import sys
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcpguard.contracts import ToolSpec

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BENIGN_SERVERS = {
    "files": "mcpguard.servers.files_server",
    "mail": "mcpguard.servers.mail_server",
    "bank": "mcpguard.servers.bank_server",
}
ATTACKER_MODULE = "mcpguard.servers.attacker_server"


@dataclass
class ServerLaunch:
    name: str
    module: str
    env: dict[str, str] = field(default_factory=dict)
    trusted: bool = True


class MCPHub:
    def __init__(self, launches: list[ServerLaunch], hidden_tools: set[str] | None = None):
        self.launches = launches
        self.hidden_tools = hidden_tools or set()
        self.sessions: dict[str, ClientSession] = {}
        self.registry: dict[str, ToolSpec] = {}  # exposed name -> spec (last wins)
        self.all_tools: list[ToolSpec] = []  # every tool advertised, incl. shadowed ones
        self._stack = AsyncExitStack()

    async def __aenter__(self) -> "MCPHub":
        for launch in self.launches:
            env = {
                "PYTHONPATH": str(PROJECT_ROOT),
                "PYTHONIOENCODING": "utf-8",
                **launch.env,
            }
            for var in ("SYSTEMROOT", "PATH", "TEMP", "TMP"):
                if var in os.environ:
                    env.setdefault(var, os.environ[var])
            params = StdioServerParameters(
                command=sys.executable, args=["-m", launch.module], env=env, cwd=str(PROJECT_ROOT)
            )
            read, write = await self._stack.enter_async_context(stdio_client(params))
            session = await self._stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.sessions[launch.name] = session
            listed = await session.list_tools()
            for t in listed.tools:
                if launch.trusted and t.name in self.hidden_tools:
                    continue
                spec = ToolSpec(name=t.name, server=launch.name, description=t.description or "",
                                input_schema=t.inputSchema)
                self.all_tools.append(spec)
                self.registry[t.name] = spec
        return self

    async def __aexit__(self, *exc) -> None:
        await self._stack.aclose()

    def tools(self) -> list[ToolSpec]:
        return list(self.registry.values())

    async def call(self, server: str, name: str, arguments: dict) -> str:
        result = await self.sessions[server].call_tool(name, arguments)
        text = "\n".join(getattr(c, "text", "") for c in result.content)
        if result.isError and not text.startswith("ERROR"):
            text = f"ERROR: {text}"
        return text
