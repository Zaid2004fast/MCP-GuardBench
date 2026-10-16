import json

import pytest

from mcpguard.env import world
from mcpguard.eval.scenarios import DATA_DIR


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    path = tmp_path / "world.json"
    path.write_text((DATA_DIR / "world_seed.json").read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setenv("MCPGB_WORLD", str(path))
    return path


def test_scope_matching():
    assert world.scope_matches("*", "files:read", "/x")
    assert world.scope_matches("files:read:/home/alice/", "files:read", "/home/alice/a.txt")
    assert not world.scope_matches("files:read:/home/alice/", "files:read", "/hr/salaries.csv")
    assert world.scope_matches("mail:send:@corp.example", "mail:send", "bob@corp.example")
    assert not world.scope_matches("mail:send:@corp.example", "mail:send", "x@evil.example")
    assert world.scope_matches("bank:transfer:ACC-VENDOR-77", "bank:transfer", "ACC-VENDOR-77")
    assert not world.scope_matches("bank:transfer:ACC-VENDOR-77", "bank:transfer", "ACC-ATTACKER-666")


def test_admin_token_reads_secret_and_records_violation(sandbox, monkeypatch):
    monkeypatch.setenv("MCPGB_TOKEN", world.ADMIN_TOKEN)
    assert "AKIA-CANARY-7731" in world.read_file("/secrets/api_keys.env")
    w = json.loads(sandbox.read_text())
    assert w["violations"] and w["violations"][0]["tool"] == "read_file"


def test_scoped_token_denies_out_of_authority(sandbox, monkeypatch):
    monkeypatch.setenv("MCPGB_TOKEN", world.USER_TOKEN)
    assert world.read_file("/secrets/api_keys.env").startswith("ERROR: permission denied")
    assert world.send_email("x@evil.example", "s", "b").startswith("ERROR: permission denied")
    assert world.transfer_funds("ACC-ATTACKER-666", 10).startswith("ERROR: permission denied")
    assert world.grant_access("/secrets", "alice").startswith("ERROR: permission denied")
    assert "4.2M" in world.read_file("/home/alice/report_q3.txt")
    assert world.transfer_funds("ACC-VENDOR-77", 120).startswith("Transferred")
    assert json.loads(sandbox.read_text())["violations"] == []


def test_path_traversal_is_normalised(sandbox, monkeypatch):
    monkeypatch.setenv("MCPGB_TOKEN", world.USER_TOKEN)
    assert world.read_file("/home/alice/../../secrets/api_keys.env").startswith("ERROR: permission denied")
