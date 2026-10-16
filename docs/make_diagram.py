"""Render the system architecture diagram (docs/architecture.png)."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).with_name("architecture.png")

C = {
    "agent": "#dbe9f6", "gw": "#fde9c8", "srv": "#e3f1df", "bad": "#f8d7d4",
    "world": "#ece4f5", "eval": "#eeeeee", "gap": "#c0392b", "edge": "#333333",
}


def box(ax, x, y, w, h, text, color, fs=8.5, weight="normal", ec="#555", ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=color, ec=ec, lw=1.1, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, weight=weight, wrap=True)


def arrow(ax, x1, y1, x2, y2, text="", style="-|>", ls="-", color=None, fs=7.5, off=(0, 0.12)):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=11,
                                 lw=1.1, color=color or C["edge"], ls=ls))
    if text:
        ax.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], text, fontsize=fs, ha="center",
                color=color or C["edge"])


def gap_tag(ax, x, y, label):
    ax.text(x, y, label, fontsize=8, weight="bold", color="white", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.25", fc=C["gap"], ec=C["gap"]))


fig, ax = plt.subplots(figsize=(13, 8.2))
ax.set_xlim(0, 13)
ax.set_ylim(0, 8.2)
ax.axis("off")
ax.text(6.5, 7.95, "MCPGuardBench: system architecture (baseline vs. proposed)", ha="center",
        fontsize=13, weight="bold")

# ---- user + agent
box(ax, 0.2, 6.3, 2.0, 1.0, "User task\n(scenario prompt)", C["agent"], weight="bold")
box(ax, 0.2, 3.7, 2.6, 2.2,
    "Tool-calling LLM agent\n(ReAct loop)\n\nAgentState: messages,\nstep, tool-call records,\ntokens, status\n\n"
    "Providers: Ollama (local)\n/ Groq / OpenRouter", C["agent"], fs=8)
arrow(ax, 1.2, 6.3, 1.2, 5.9)

# ---- gateway
ax.add_patch(FancyBboxPatch((3.4, 2.6), 3.3, 4.4, boxstyle="round,pad=0.02,rounding_size=0.15",
                            fc="#fff8ec", ec="#c98a1a", lw=1.6))
ax.text(5.05, 6.75, "Defense gateway (policy layer)", ha="center", fontsize=9.5, weight="bold")
box(ax, 3.6, 5.75, 2.9, 0.75, "Tool allowlist\n(pinned server, name, description hash)", C["gw"], fs=8)
box(ax, 3.6, 4.85, 2.9, 0.75, "LLM guard (MCIP-style)\n[base-paper defense, comparison]", C["gw"], fs=8, ls="--")
box(ax, 3.6, 3.95, 2.9, 0.75, "Risk-tiered human approval\n(simulated approver)", C["gw"], fs=8)
box(ax, 3.6, 2.8, 2.9, 0.95, "Hash-chained audit log\n+ post-hoc detector", C["gw"], fs=8)
gap_tag(ax, 6.75, 6.12, "Gap 1")
gap_tag(ax, 6.75, 4.32, "Gap 3")
gap_tag(ax, 6.75, 3.27, "Gap 3")

arrow(ax, 2.8, 5.2, 3.4, 5.2, "tool calls", off=(0, 0.12))
arrow(ax, 3.4, 4.6, 2.8, 4.6, "results /\nblocked", off=(0, -0.35))

# ---- hub
box(ax, 7.4, 4.4, 1.7, 1.4, "MCP client hub\n(stdio sessions,\nflat namespace,\nlast-wins)", C["srv"], fs=8)
arrow(ax, 6.7, 5.1, 7.4, 5.1)

# ---- servers
box(ax, 9.7, 6.45, 3.1, 0.65, "files server  (read/write/list/grant)", C["srv"], fs=8)
box(ax, 9.7, 5.7, 3.1, 0.65, "mail server  (inbox/read/send)", C["srv"], fs=8)
box(ax, 9.7, 4.95, 3.1, 0.65, "bank server  (balance/tx/transfer)", C["srv"], fs=8)
box(ax, 9.7, 3.55, 3.1, 1.2,
    "UNTRUSTED 'toolkit' server\nPI, NC, PM, OP, UI, FE, TT, PE\n(poisoned descriptions, shadowing,\nmalicious responses)",
    C["bad"], fs=7.8)
for y in (6.77, 6.02, 5.27, 4.15):
    arrow(ax, 9.1, 5.1, 9.7, y, style="-")
ax.text(11.25, 7.25, "trusted (benign) MCP servers", ha="center", fontsize=8, style="italic")

# ---- world
box(ax, 8.2, 0.35, 4.6, 2.4,
    "Sandboxed world (per-episode JSON)\nfiles + canary secrets  |  mailbox  |  bank\n"
    "identity & tokens  |  ACLs  |  attacker sink\n\nRI / CD payloads injected into data\n"
    "Server-side credential check:\nover-privileged service token vs.\nuser-scoped token", C["world"], fs=8)
gap_tag(ax, 12.55, 2.95, "Gap 2")
arrow(ax, 11.25, 3.55, 11.25, 2.75, "read / write", off=(0.55, 0))

# ---- evaluator
box(ax, 0.2, 0.35, 7.3, 1.75,
    "Evaluation harness\nScenario generator: 10 user tasks x 14 attacks (10 classes) = 128 attacked + 10 benign\n"
    "Deterministic judges on final world state + trace (no LLM judge)\n"
    "Metrics: ASR, PUA, NRP (MSB), BU, privilege-violation rate, approvals/episode,\n"
    "detection recall, tokens, latency     |     Cross-model x defense ablation grid",
    C["eval"], fs=8)
arrow(ax, 7.5, 1.2, 8.2, 1.2, "judge final state", off=(0, 0.15))
arrow(ax, 1.5, 2.1, 1.5, 3.7, "scenario", off=(0.4, 0))

# ---- baseline path
ax.annotate("", xy=(7.4, 4.55), xytext=(2.8, 3.85),
            arrowprops=dict(arrowstyle="-|>", ls="--", color="#1f6fb2", lw=1.3,
                            connectionstyle="arc3,rad=0.28"))
ax.text(5.0, 2.25, "BASELINE (MSB setting): agent -> hub directly, no gateway, over-privileged token",
        fontsize=8, color="#1f6fb2", ha="center", style="italic")
ax.text(6.5, 7.55, "PROPOSED: all calls pass through the gateway; servers launched with scoped credentials",
        fontsize=8, color="#c98a1a", ha="center", style="italic")

fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"saved {OUT}")
