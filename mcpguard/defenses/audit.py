"""Tamper-evident audit log: every gateway event is appended as a hash-chained JSON line."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any


class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.prev_hash = "0" * 64
        self.path.write_text("", encoding="utf-8")

    def log(self, event: str, **data: Any) -> None:
        entry = {"ts": time.time(), "event": event, "prev": self.prev_hash, **data}
        body = json.dumps(entry, sort_keys=True, default=str)
        entry["hash"] = hashlib.sha256(body.encode()).hexdigest()
        self.prev_hash = entry["hash"]
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")


def verify_chain(path: Path) -> bool:
    """Return True if no audit entry was modified, removed or reordered."""
    prev = "0" * 64
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        claimed = entry.pop("hash")
        if entry["prev"] != prev:
            return False
        body = json.dumps(entry, sort_keys=True, default=str)
        if hashlib.sha256(body.encode()).hexdigest() != claimed:
            return False
        prev = claimed
    return True
