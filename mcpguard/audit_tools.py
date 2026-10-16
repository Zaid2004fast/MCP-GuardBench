"""Helpers to verify audit logs produced by a run."""

from __future__ import annotations

from pathlib import Path

from mcpguard.defenses.audit import verify_chain


def verify_audit_dir(root: Path) -> bool:
    logs = list(Path(root).rglob("audit.jsonl"))
    return bool(logs) and all(verify_chain(p) for p in logs)
