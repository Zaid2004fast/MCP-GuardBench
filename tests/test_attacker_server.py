import importlib
import inspect
import json

import pytest


@pytest.fixture
def attacker(tmp_path, monkeypatch):
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"vector": "description", "payload": "x"}))
    monkeypatch.setenv("MCPGB_ATTACK", str(spec))
    import mcpguard.servers.attacker_server as mod

    return importlib.reload(mod)


def test_every_mirror_builds_with_and_without_extra_param(attacker):
    for name, (impl, params, _) in attacker.MIRRORS.items():
        for extra in (None, "verification_code"):
            fn = attacker._build(name, impl, params, extra)
            sig = inspect.signature(fn)
            if extra:
                assert sig.parameters[extra].default is inspect.Parameter.empty
            attacker.mcp.add_tool(fn, name=f"{name}_{extra}")  # FastMCP must accept the schema
