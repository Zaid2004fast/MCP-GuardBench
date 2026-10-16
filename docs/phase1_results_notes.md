**Coverage.** Qwen2.5-1.5B ran locally on all 138 scenarios, both undefended and with the safety prompt. The Groq free tier caps each model at 200k tokens per day, so the API models have less coverage:

- gpt-oss-20B completed 110 of 138 scenarios.
- Qwen3.8-27B and gpt-oss-120B ran a stratified sample of 66 scenarios: 6 per attack class plus 6 benign.

Five Qwen3.8-27B benign episodes failed with HTTP 429 (rate limit) and are excluded from every rate, so its BU is not reported. All runs use temperature 0 and a single seed. All other episodes completed with no harness errors. Full results for every model are scheduled for Phase 2.

**What the initial results show.**

1. **Vulnerability grows with model capability.** Undefended ASR rises from 24.2% (Qwen2.5-1.5B) and 28.3% (Qwen3.8-27B) to 55.4% (gpt-oss-20B) and 70.0% (gpt-oss-120B). The two gpt-oss models also complete every benign task they ran (BU 100%). This matches MSB's central finding that stronger tool-users are more exploitable (MSB average ASR 40.35%). It is evidence that our re-implementation of the taxonomy behaves like the base benchmark.
2. **Planning-stage (tool signature) attacks dominate.** Name collision (tool shadowing) succeeded in 100% of episodes for every model and defense. Out-of-scope parameters succeeded in 83–100%, consistent with MSB, where OP was also the strongest class (76.5%). Preference manipulation succeeded in 50–100%. Response-stage attacks were weaker (0–47% by model).
3. **The prompt-level defense does nothing.** The MCP-SafetyBench-style safety prompt left ASR unchanged at 24.2%, lowered PUA from 57.0% to 53.9%, and lowered NRP from 43.2% to 40.9%. This reproduces the null result reported in [2] and motivates Gap 1.
4. **Most successful attacks travel through untrusted tools.** For every model, 93–100% of successful attacks were delivered by tools of the untrusted server rather than by injected data. This is exactly the surface a pinned allowlist removes, so it supports H1. The residual (retrieval injection on gpt-oss-120B) is the part the allowlist cannot stop.
5. **Authority misuse is real and partly invisible to ASR.** Privilege escalation (PE) succeeded in 100% of gpt-oss episodes: following a poisoned description, the agent called `grant_access` using its over-privileged service token. Up to 31.7% of attacked episodes contained at least one action beyond the user's own authority (PVR).

   Confused-deputy exfiltration did not succeed on any model (0%). However, gpt-oss-120B *read* `/hr/salaries.csv` before declining to forward it. ASR counts that episode as a failed attack, but the PVR metric records it as an unauthorised access. Benign episodes produced zero violations, so PVR is specific to attacks. Together these motivate Gap 2.
