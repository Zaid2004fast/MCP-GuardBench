"""Build the admin-approved tool manifest (data/allowlist.json) from the trusted servers.

    python -m mcpguard.defenses.build_allowlist
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

from mcpguard.agent.mcp_hub import BENIGN_SERVERS, MCPHub, ServerLaunch
from mcpguard.defenses.gateway import ALLOWLIST_PATH, build_allowlist_entries
from mcpguard.eval.scenarios import DATA_DIR


async def build() -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        world = Path(tmp) / "world.json"
        world.write_text((DATA_DIR / "world_seed.json").read_text(encoding="utf-8"), encoding="utf-8")
        env = {"MCPGB_WORLD": str(world)}
        async with MCPHub([ServerLaunch(n, m, env) for n, m in BENIGN_SERVERS.items()]) as hub:
            # grant_access is an admin-only tool: the agent's manifest excludes it (least functionality)
            tools = [t for t in hub.tools() if t.name != "grant_access"]
            return build_allowlist_entries(tools)


def main() -> None:
    entries = asyncio.run(build())
    ALLOWLIST_PATH.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} pinned tools to {ALLOWLIST_PATH}")


if __name__ == "__main__":
    main()
