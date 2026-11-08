"""Render an episode trajectory (trace.json) as readable text or Markdown.

    python -m mcpguard.eval.trace results/<run>/<model>/<defense>/seed0/episodes/T09-RI-transfer/trace.json

Shows, per step: the model's visible reasoning / message, each tool call with its
arguments, the gateway decision (which layer allowed, blocked or asked a human) and the
tool result, i.e. the observe -> reason -> act -> observe transitions of the agent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _short(text: Any, n: int = 220) -> str:
    s = str(text).replace("\n", " ⏎ ")
    return s if len(s) <= n else s[: n - 1] + "…"


def render(trace: dict[str, Any], markdown: bool = False, width: int = 220) -> str:
    out: list[str] = []
    msgs = trace["messages"]
    records = {(r["step"], r["name"], json.dumps(r["arguments"], sort_keys=True)): r for r in trace["tool_calls"]}
    out.append(f"scenario {trace['scenario_id']} | status={trace['status']} | steps={trace['step']} | "
               f"tokens={trace['prompt_tokens'] + trace['completion_tokens']}")
    user = next((m["content"] for m in msgs if m["role"] == "user"), "")
    out.append(f"USER: {_short(user, width)}")
    step = 0
    for m in msgs:
        if m["role"] == "assistant":
            step += 1
            if m.get("content"):
                out.append(f"[{step}] THOUGHT/MSG: {_short(m['content'], width)}")
            for c in m.get("tool_calls") or []:
                args = c["function"]["arguments"]
                args_d = json.loads(args) if isinstance(args, str) else args
                rec = records.get((step, c["function"]["name"], json.dumps(args_d, sort_keys=True)))
                gate = ""
                if rec:
                    d = rec["decision"]
                    gate = f"  -> gateway: {d['decision']}" + (f" by {d['layer']}" if d.get("layer") else "")
                    if rec.get("server"):
                        gate += f" (server={rec['server']})"
                out.append(f"[{step}] CALL {c['function']['name']}({_short(json.dumps(args_d), width)}){gate}")
        elif m["role"] == "tool":
            out.append(f"     RESULT: {_short(m['content'], width)}")
    out.append(f"FINAL: {_short(trace.get('final_answer', ''), width)}")
    if trace.get("error"):
        out.append(f"ERROR: {trace['error']}")
    text = "\n".join(out)
    return f"```text\n{text}\n```" if markdown else text


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
        sys.stdout.reconfigure(encoding="utf-8")
    for arg in sys.argv[1:]:
        print(render(json.loads(Path(arg).read_text(encoding="utf-8"))))
        print()


if __name__ == "__main__":
    main()
