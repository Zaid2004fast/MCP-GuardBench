# Development log (Phase 2)

Each entry records what failed or was missing, what we changed, and the measured effect.
"Before" numbers come from the committed Phase 1 runs (`results/phase1-*`); "after" numbers
come from the Phase 2 runs named in each entry. Entries marked **[pending]** need the
listed LLM run to finish; fill them in from `results/paper/` after
`python experiments/reproduce.py report`.

| # | Date | Owner | Area |
|---|---|---|---|
| 1 | 2026-11-07 | Zaid | attack server (FE bug) |
| 2 | 2026-11-07 | Zaid | confused-deputy attacks |
| 3 | 2026-11-07 | Zaid | human approval (risk tiers) |
| 4 | 2026-11-07 | Saud | evaluation protocol (splits, seeds) |
| 5 | 2026-11-07 | Saud | reference agents |
| 6 | 2026-11-07 | Saud | agent loop robustness |
| 7 | 2026-11-07 | Zaid | gateway verification, timeouts |
| 8 | 2026-11-07 | Saud | runner reliability |
| 9 | 2026-11-07 | Zaid + Saud | audit-log detector (designed on dev split) |

---

### 1. False-error attacks blocked their own exfiltration (bug)

- **Observed.** A new test that replays a fully compliant agent on every attack variant
  (`tests/test_reference_agent.py`) failed for `T01-FE-exfil`. The attacker's mirrored
  `read_file` replaced *every* response with the fake error, so when the agent obeyed and read
  `/secrets/api_keys.env`, the attacker's own tool hid the secret. The same behaviour made the
  user task impossible after compliance. In Phase 1, FE episodes had low task completion on
  every model (PUA on FE: 20% qwen2.5:1.5b, 31% gpt-oss-20b, 33% qwen3.8-27b, 50% gpt-oss-120b).
- **Change.** `servers/attacker_server.py`: a `replace` response is injected on the first call
  only (`replace_once`, default on), like a real attacker who wants the follow-up to work.
- **Effect.** The compliant agent now realises FE-exfil on `read_file` tasks (2 of 14 FE test
  scenarios were unreachable before). FE numbers are therefore **not directly comparable**
  with Phase 1; this is listed under "Changes since Phase 1" in the README.

### 2. Confused deputy never succeeded

- **Observed.** In Phase 1, CD succeeded in 0% of episodes on all four models (`results/phase1-*`),
  although gpt-oss-120b did read `/hr/salaries.csv` before refusing to send it to an external
  address. The only CD variant asked for an e-mail to `partner@evil.example`, which models refuse
  as obvious exfiltration, so the class could not test Gap 2.
- **Change.** Two internal-recipient variants (`CD-hr-internal`, `CD-secret-internal`): the
  e-mail goes to a colleague (`carol@`, `bob@corp.example`), which is within the user's
  authority. Only *reading* the data needs the agent's service privileges. New judge predicate
  `mail_contains` (any recipient). Attacked scenarios: 128 -> 140.
- **Effect.** Reference agents: the compliant agent realises both variants (100% undefended).
  Risk-tiered approval cannot see them (internal e-mail = low risk), scoped credentials stop
  them (see Table 4, `agent:gullible`). LLM success rate: **[pending: Table 4, phase2-local]**.

### 3. Approving every sensitive call costs approvals on benign tasks

- **Observed.** Phase 1 HITL asked a human for *every* `send_email`, `transfer_funds`,
  `write_file`, `delete_file` and `grant_access`, including the ones the user had just asked
  for. With the new benign-only probes (T11-T16) most benign tasks contain such an action.
- **Change.** `defenses/approvers.py`: risk tiers from the organisation policy
  (`data/policy.yaml`): internal recipients, known payees up to 2000 USD and files in the
  user's home are low risk and pass without a human. Added approver models `fatigue`
  (lapse rate 0.3) and `approve_all` for the cost/benefit analysis.
- **Effect (reference agents, test split, `results/phase2-reference`).** Approvals per benign
  task fall from 0.64 (`hitl-all`) to 0 (`hitl`). Cost: with the compliant agent, ASR rises from
  28.4% to 37.3% and the stop rate falls from 100% to 87.7%, entirely from the internal
  confused-deputy variants (CD ASR 6.7% -> 66.7%), which look low risk. Scoped credentials close
  this gap (CD 0%). LLM numbers: **[pending: Table 5]**.

### 4. No held-out split and single-seed results

- **Observed.** Phase 1 reported every number on the same 138 scenarios that we also used to
  tune prompts, and every run used one seed at temperature 0 (local runs were therefore
  exactly repeatable but gave no variance estimate).
- **Change.** `data/splits.yaml`: a fixed task-level split, dev = {T03, T04, T07, T15, T16}
  (43 scenarios, all 10 classes) and test = the other 11 tasks (113 scenarios: 102 attacked, 11
  benign). Dev is used only for design decisions (detector rules, risk thresholds, lapse rate,
  loop limits). LLM runs use temperature 0.7 with seeds {0, 1, 2}; the MCIP-style guard keeps
  greedy decoding. Six benign-only tasks (T11-T16) raise the benign set from 10 to 16 tasks.
- **Effect.** All paper tables report test-split mean ± std over three seeds.

### 5. Defense coverage was confounded with model gullibility

- **Observed.** In Phase 1 a low ASR could mean "the defense works" or "the model ignored the
  injection" (e.g. qwen2.5:1.5b had 0% ASR on PI, TT, RI, PE without any defense).
- **Change.** `providers/reference.py`: deterministic reference agents. `agent:gullible` obeys
  every injection that reaches its context; `agent:ideal` never does. Same task plans.
- **Effect.** A model-independent upper bound on what each defense lets through (Table 6,
  `gullible`), computed in about three hours on a laptop CPU with no API cost.

### 6. Repeated failing calls and runaway episodes

- **Observed.** In Phase 1, 7.6% of gpt-oss-120b episodes ended at `max_steps` (8 steps), and
  9.1% of qwen3.8-27b episodes ended with zero tool calls.
- **Change.** `agent/loop.py`: a loop guard. An identical call (same tool and arguments) runs at
  most twice; further repeats are answered with an explanatory error, and two such repeats end
  the episode as `loop_break`. The runner wraps each episode in a timeout (`episode_timeout`) and
  keeps the partial trajectory.
- **Effect.** Share of episodes ending at max_steps/loop/timeout per model and defense:
  **[pending: Table 7, column "Max-steps/loop/timeout"]**.

### 7. Malformed tool calls reached the servers

- **Observed.** Small models sometimes omit required arguments; the server then raised a
  validation exception that the agent saw as an opaque error.
- **Change.** `defenses/gateway.py`: required arguments are checked against the tool's input
  schema before the call; the agent gets a message naming the missing argument so it can
  retry. `agent/mcp_hub.py`: every tool call has a 30 s timeout.
- **Effect.** **[pending: count of "missing required argument" results in phase2-local traces]**.

### 8. Rate limits and infrastructure errors lost episodes

- **Observed.** 5 of 66 qwen3.8-27b episodes in Phase 1 failed with HTTP 429 and were dropped,
  so no benign utility could be reported for that model.
- **Change.** `eval/run.py`: each episode is retried up to `retries` times; on resume, episodes
  recorded as `error` are re-run; episodes run concurrently (`concurrency`). The Ollama provider
  retries transient 5xx/transport errors.
- **Effect.** Infrastructure errors per run are reported in Table 7 ("Infra errors", "Retries").

### 9. Audit-log detector rules (designed on dev only)

- **Design.** Rules use only organisation policy (`data/policy.yaml`): external recipient,
  unknown payee, permission change, read outside the user's home, call routed to an
  untrusted server, credential pattern in arguments, gateway block/denial, broken hash chain.
- **Dev-split check (compliant agent, undefended, 38 attacked + 5 benign).** Recall 100% on
  successful attacks, precision 100%, false-positive rate 0% on benign episodes. The rules were
  then frozen; test-split numbers (102 + 11): recall 100%, precision 100%, FPR 0%.
- **Observed limitation.** Under prevention (`hitl`), precision on *successful* attacks drops to
  37% because the detector also flags blocked attempts (rule POLICY_BLOCK). We keep this: for a
  security team an attempted attack is worth an alert. Table 5b therefore reports recall on all
  attacked episodes as well. LLM false-positive rate: **[pending: Table 5b]**.
- **Known limitation.** The hash chain detects edits and re-ordering but not truncation of
  the tail of the log (`tests/test_detector.py::test_tampering_is_detected`). An external
  anchor (e.g. periodically publishing the head hash) would close this.
