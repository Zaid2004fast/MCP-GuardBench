"""Draw the system architecture (docs/architecture.png, used by the README and the paper).

    python docs/architecture.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

INK, MUTED, ACCENT, WARN = "#0b0b0b", "#52514e", "#2a78d6", "#e34948"
FILL, GATE = "#f4f3ef", "#e8f0fb"


def box(ax, x, y, w, h, title, body="", fill=FILL, edge=INK, dashed=False, tag=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=edge,
                                lw=1.1, ls="--" if dashed else "-"))
    ax.text(x + w / 2, y + h - 0.16, title, ha="center", va="top", fontsize=8.2, weight="bold", color=INK)
    if body:
        ax.text(x + w / 2, y + h - 0.44, body, ha="center", va="top", fontsize=6.6, color=MUTED, linespacing=1.25)
    if tag:
        ax.text(x + w - 0.05, y + 0.06, tag, ha="right", va="bottom", fontsize=6.4, color="white", weight="bold",
                bbox=dict(boxstyle="round,pad=0.18", fc=INK, ec=INK))


def arrow(ax, a, b, text="", color=INK, dashed=False, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=9, lw=1.0, color=color,
                                 ls="--" if dashed else "-", connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.08, text, ha="center", fontsize=6.4, color=color)


def main() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.6)
    ax.axis("off")

    box(ax, 0.1, 4.3, 1.9, 1.0, "User task", "scenario prompt\n(dev / test split)")
    box(ax, 0.1, 2.0, 1.9, 2.0, "LLM agent", "ReAct loop, native\ntool calls\nAgentState trace\nloop guard, timeout\nOllama / Groq /\nOpenRouter")
    box(ax, 2.5, 1.25, 2.7, 4.05, "Defense gateway", "", fill=GATE, edge=ACCENT)
    box(ax, 2.65, 4.1, 2.4, 0.75, "Tool allowlist", "pinned server+name+desc hash", tag="Gap 1")
    box(ax, 2.65, 3.2, 2.4, 0.75, "MCIP-style LLM guard", "base-paper defense (B2)", dashed=True)
    box(ax, 2.65, 2.3, 2.4, 0.75, "Risk-tiered approval", "oracle / fatigue / approve-all", tag="Gap 3")
    box(ax, 2.65, 1.35, 2.4, 0.85, "Hash-chained audit log", "+ post-hoc rule detector\n+ argument verification", tag="Gap 3")
    box(ax, 5.6, 2.6, 1.5, 1.4, "MCP client hub", "stdio sessions\nflat namespace\nlast-registered\nwins")
    box(ax, 7.5, 4.65, 2.4, 0.6, "files server", "read/write/list/grant")
    box(ax, 7.5, 3.95, 2.4, 0.6, "mail server", "inbox/read/send")
    box(ax, 7.5, 3.25, 2.4, 0.6, "bank server", "balance/tx/transfer")
    box(ax, 7.5, 2.15, 2.4, 0.95, "UNTRUSTED toolkit", "PI NC PM OP UI FE TT PE\n(poisoned / shadowing /\nmalicious responses)", edge=WARN)
    box(ax, 5.6, 0.1, 4.3, 1.6, "Sandbox world (per episode)", "files + canary secrets | mailbox | bank | ACLs\n"
        "service token vs user-scoped token, server-side check\nRI / CD payloads injected into data\n"
        "privilege-violation log | attacker sink", tag="Gap 2")
    box(ax, 0.1, 0.1, 5.0, 0.8, "Evaluation harness", "deterministic judges on final world + trace | ASR PUA NRP BU PVR | "
        "stop rate, approvals,\ndetector R/P | tokens, latency | seeds, bootstrap CI, McNemar | reference agents")

    arrow(ax, (1.05, 4.3), (1.05, 4.0))
    arrow(ax, (2.0, 3.3), (2.5, 3.3), "tool call")
    arrow(ax, (2.5, 2.7), (2.0, 2.7), "result / blocked")
    arrow(ax, (5.2, 3.3), (5.6, 3.3))
    for y in (4.95, 4.25, 3.55, 2.62):
        arrow(ax, (7.1, 3.3), (7.5, y))
    arrow(ax, (8.7, 2.15), (8.7, 1.7), "read / write")
    # baseline path (MSB setting) bypasses the gateway: drawn underneath it
    ax.plot([2.0, 2.25, 2.25, 5.4, 5.4], [2.1, 2.1, 1.07, 1.07, 2.75], color=MUTED, lw=1.0, ls="--")
    arrow(ax, (5.4, 2.75), (5.6, 2.75), color=MUTED)
    ax.text(3.85, 1.1, "baseline B0: no gateway, admin token", ha="center", va="bottom", fontsize=6.4, color=MUTED)
    arrow(ax, (5.6, 0.7), (5.1, 0.6), "judge")
    fig.tight_layout()
    out = Path(__file__).with_name("architecture.png")
    fig.savefig(out, dpi=220)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
