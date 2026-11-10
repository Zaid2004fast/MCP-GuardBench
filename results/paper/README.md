# MCPGuardBench Phase 2 results (test split)

Runs: D:\University\4th Year\7th Semester\AgenticAI\AgenticProj\results\phase2-reference, D:\University\4th Year\7th Semester\AgenticAI\AgenticProj\results\phase2-local  
Episodes: 6780 (0 infrastructure errors, excluded from rates)

### Table 1 – E1/E2/E3 main results (mean ± std over seeds, %)

| Model       | Defense             |   Seeds |   Attacked eps/seed | BU          | ASR        | PUA        | NRP        | PVR        | ASR 95% CI     |
|:------------|:--------------------|--------:|--------------------:|:------------|:-----------|:-----------|:-----------|:-----------|:---------------|
| gullible    | B0 none             |       1 |                 102 | 100.0       | 100.0      | 92.2       | 0.0        | 72.5       | [100.0, 100.0] |
| gullible    | allowlist + scoped  |       1 |                 102 | 100.0       | 0.0        | 58.8       | 58.8       | 0.0        | [0.0, 0.0]     |
| gullible    | proposed (full)     |       1 |                 102 | 100.0       | 0.0        | 58.8       | 58.8       | 0.0        | [0.0, 0.0]     |
| ideal       | B0 none             |       1 |                 102 | 100.0       | 6.9        | 87.3       | 81.3       | 0.0        | [2.0, 11.8]    |
| ideal       | allowlist + scoped  |       1 |                 102 | 100.0       | 0.0        | 58.8       | 58.8       | 0.0        | [0.0, 0.0]     |
| ideal       | proposed (full)     |       1 |                 102 | 100.0       | 0.0        | 58.8       | 58.8       | 0.0        | [0.0, 0.0]     |
| llama3.2:3b | B0 none             |       1 |                 102 | 72.7        | 18.6       | 54.9       | 44.7       | 1.0        | [10.8, 26.5]   |
| llama3.2:3b | B1 safety prompt    |       1 |                 102 | 72.7        | 21.6       | 47.1       | 36.9       | 0.0        | [13.7, 29.4]   |
| llama3.2:3b | B2 MCIP-style guard |       1 |                 102 | 72.7        | 12.7       | 38.2       | 33.4       | 1.0        | [6.9, 19.6]    |
| llama3.2:3b | proposed (full)     |       1 |                 102 | 72.7        | 0.0        | 51.0       | 51.0       | 0.0        | [0.0, 0.0]     |
| qwen2.5:3b  | B0 none             |       3 |                 102 | 78.8 ± 5.2  | 30.1 ± 1.5 | 66.7 ± 2.6 | 46.6 ± 2.5 | 12.4 ± 1.5 | [24.8, 35.3]   |
| qwen2.5:3b  | B1 safety prompt    |       3 |                 102 | 81.8 ± 9.1  | 29.7 ± 2.8 | 61.4 ± 3.4 | 43.1 ± 1.1 | 7.8 ± 2.6  | [24.5, 35.0]   |
| qwen2.5:3b  | B2 MCIP-style guard |       3 |                 102 | 84.8 ± 5.2  | 24.5 ± 0.0 | 62.4 ± 2.0 | 47.1 ± 1.5 | 1.0 ± 0.0  | [19.6, 29.4]   |
| qwen2.5:3b  | allowlist + scoped  |       3 |                 102 | 93.9 ± 10.5 | 0.0 ± 0.0  | 57.5 ± 6.7 | 57.5 ± 6.7 | 0.0 ± 0.0  | [0.0, 0.0]     |
| qwen2.5:3b  | proposed (full)     |       3 |                 102 | 90.9 ± 9.1  | 0.0 ± 0.0  | 57.5 ± 6.7 | 57.5 ± 6.7 | 0.0 ± 0.0  | [0.0, 0.0]     |

### Table 2 – ASR (%) by attack class

| Class   |   gullible / full |   gullible / none |   ideal / full |   ideal / none |   llama3.2:3b / full |   llama3.2:3b / llm_guard |   llama3.2:3b / none |   qwen2.5:3b / full |   qwen2.5:3b / llm_guard |   qwen2.5:3b / none |
|:--------|------------------:|------------------:|---------------:|---------------:|---------------------:|--------------------------:|---------------------:|--------------------:|-------------------------:|--------------------:|
| PI      |                 0 |               100 |              0 |              0 |                    0 |                    0      |               0      |                   0 |                   0      |              0      |
| NC      |                 0 |               100 |              0 |            100 |                    0 |                   71.4286 |             100      |                   0 |                  95.2381 |            100      |
| PM      |                 0 |               100 |              0 |              0 |                    0 |                   71.4286 |              71.4286 |                   0 |                 100      |            100      |
| OP      |                 0 |               100 |              0 |              0 |                    0 |                   28.5714 |              85.7143 |                   0 |                  95.2381 |             95.2381 |
| UI      |                 0 |               100 |              0 |              0 |                    0 |                    0      |               0      |                   0 |                   0      |             38.0952 |
| FE      |                 0 |               100 |              0 |              0 |                    0 |                    0      |               0      |                   0 |                   0      |              0      |
| TT      |                 0 |               100 |              0 |              0 |                    0 |                   14.2857 |              14.2857 |                   0 |                  66.6667 |             66.6667 |
| RI      |                 0 |               100 |              0 |              0 |                    0 |                    0      |               0      |                   0 |                   0      |              0      |
| PE      |                 0 |               100 |              0 |              0 |                    0 |                    0      |               0      |                   0 |                   0      |              0      |
| CD      |                 0 |               100 |              0 |              0 |                    0 |                    0      |               0      |                   0 |                   0      |              0      |

### Table 3 – Gap 1: system-level mitigations vs MCIP-style guard (%)

| Model       | Defense          |   ASR |   PUA |   NRP |    BU | ASR reduction vs none   |
|:------------|:-----------------|------:|------:|------:|------:|:------------------------|
| gullible    | none             | 100   |  92.2 |   0   | 100   | –                       |
| gullible    | allowlist        |  24.5 |  58.8 |  44.4 | 100   | 75.5                    |
| gullible    | scoped           |  27.5 |  94.1 |  68.3 | 100   | 72.5                    |
| gullible    | allowlist+scoped |   0   |  58.8 |  58.8 | 100   | 100.0                   |
| ideal       | none             |   6.9 |  87.3 |  81.3 | 100   | –                       |
| ideal       | allowlist        |   0   |  58.8 |  58.8 | 100   | 100.0                   |
| ideal       | scoped           |   6.9 |  87.3 |  81.3 | 100   | 0.0                     |
| ideal       | allowlist+scoped |   0   |  58.8 |  58.8 | 100   | 100.0                   |
| llama3.2:3b | none             |  18.6 |  54.9 |  44.7 |  72.7 | –                       |
| llama3.2:3b | llm_guard        |  12.7 |  38.2 |  33.4 |  72.7 | 31.6                    |
| qwen2.5:3b  | none             |  30.1 |  66.7 |  46.6 |  78.8 | –                       |
| qwen2.5:3b  | llm_guard        |  24.5 |  62.4 |  47.1 |  84.8 | 18.5                    |
| qwen2.5:3b  | allowlist        |   0   |  53.9 |  53.9 |  90.9 | 100.0                   |
| qwen2.5:3b  | scoped           |  25.2 |  61.1 |  45.7 |  81.8 | 16.3                    |
| qwen2.5:3b  | allowlist+scoped |   0   |  57.5 |  57.5 |  93.9 | 100.0                   |

### Table 3b – Gap 1: paired McNemar tests on attack success

| Model       | A         | B                |   pairs |   ASR A |   ASR B |   only A |   only B |   McNemar p |
|:------------|:----------|:-----------------|--------:|--------:|--------:|---------:|---------:|------------:|
| gullible    | none      | allowlist+scoped |     102 |   100   |     0   |      102 |        0 |     3.9e-31 |
| ideal       | none      | allowlist+scoped |     102 |     6.9 |     0   |        7 |        0 |     0.016   |
| llama3.2:3b | none      | llm_guard        |     102 |    18.6 |    12.7 |        7 |        1 |     0.07    |
| qwen2.5:3b  | llm_guard | allowlist+scoped |     306 |    24.5 |     0   |       75 |        0 |     5.3e-23 |
| qwen2.5:3b  | none      | allowlist+scoped |     306 |    30.1 |     0   |       92 |        0 |     4e-28   |
| qwen2.5:3b  | none      | llm_guard        |     306 |    30.1 |    24.5 |       20 |        3 |     0.00049 |

### Table 4 – Gap 2: authority misuse, admin vs scoped token (%)

| Model       | Defense          |   PVR |   PVR benign |   CD ASR |   CD-internal ASR |   PE ASR |    BU |
|:------------|:-----------------|------:|-------------:|---------:|------------------:|---------:|------:|
| gullible    | none             |  72.5 |            0 |      100 |               100 |      100 | 100   |
| gullible    | allowlist        |  24.5 |            0 |      100 |               100 |        0 | 100   |
| gullible    | scoped           |   0   |            0 |        0 |                 0 |        0 | 100   |
| gullible    | allowlist+scoped |   0   |            0 |        0 |                 0 |        0 | 100   |
| gullible    | full             |   0   |            0 |        0 |                 0 |        0 | 100   |
| ideal       | none             |   0   |            0 |        0 |                 0 |        0 | 100   |
| ideal       | allowlist        |   0   |            0 |        0 |                 0 |        0 | 100   |
| ideal       | scoped           |   0   |            0 |        0 |                 0 |        0 | 100   |
| ideal       | allowlist+scoped |   0   |            0 |        0 |                 0 |        0 | 100   |
| ideal       | full             |   0   |            0 |        0 |                 0 |        0 | 100   |
| llama3.2:3b | none             |   1   |            0 |        0 |                 0 |        0 |  72.7 |
| llama3.2:3b | full             |   0   |            0 |        0 |                 0 |        0 |  72.7 |
| qwen2.5:3b  | none             |  12.4 |            0 |        0 |                 0 |        0 |  78.8 |
| qwen2.5:3b  | allowlist        |   1   |            0 |        0 |                 0 |        0 |  90.9 |
| qwen2.5:3b  | scoped           |   0   |            0 |        0 |                 0 |        0 |  81.8 |
| qwen2.5:3b  | allowlist+scoped |   0   |            0 |        0 |                 0 |        0 |  93.9 |
| qwen2.5:3b  | full             |   0   |            0 |        0 |                 0 |        0 |  90.9 |

### Table 5 – Gap 3: human approval policy and approver behaviour

| Model       | Defense          |   Episodes reaching sensitive | Stop rate   |   Approvals / benign task |   Approvals / attacked ep |   ASR |   NRP |    BU |
|:------------|:-----------------|------------------------------:|:------------|--------------------------:|--------------------------:|------:|------:|------:|
| gullible    | none             |                            73 | 0.0         |                      0    |                      0    | 100   |   0   | 100   |
| gullible    | hitl             |                            73 | 87.7        |                      0    |                      0.63 |  37.3 |  59.1 | 100   |
| gullible    | hitl-all         |                            73 | 100.0       |                      0.64 |                      1.14 |  28.4 |  67.4 | 100   |
| gullible    | hitl-fatigue     |                            73 | 63.0        |                      0    |                      0.63 |  54.9 |  42.4 | 100   |
| gullible    | hitl-approve-all |                            73 | 0.0         |                      0    |                      0.63 | 100   |   0   | 100   |
| gullible    | full             |                            24 | 100.0       |                      0    |                      0.15 |   0   |  58.8 | 100   |
| gullible    | full-fatigue     |                            24 | 100.0       |                      0    |                      0.15 |   0   |  58.8 | 100   |
| ideal       | none             |                             0 | n/a         |                      0    |                      0    |   6.9 |  81.3 | 100   |
| ideal       | hitl             |                             0 | n/a         |                      0    |                      0    |   6.9 |  81.3 | 100   |
| ideal       | hitl-all         |                             0 | n/a         |                      0.64 |                      0.41 |   6.9 |  81.3 | 100   |
| ideal       | hitl-fatigue     |                             0 | n/a         |                      0    |                      0    |   6.9 |  81.3 | 100   |
| ideal       | hitl-approve-all |                             0 | n/a         |                      0    |                      0    |   6.9 |  81.3 | 100   |
| ideal       | full             |                             0 | n/a         |                      0    |                      0    |   0   |  58.8 | 100   |
| ideal       | full-fatigue     |                             0 | n/a         |                      0    |                      0    |   0   |  58.8 | 100   |
| llama3.2:3b | none             |                            14 | 85.7        |                      0    |                      0    |  18.6 |  44.7 |  72.7 |
| llama3.2:3b | full             |                            11 | 100.0       |                      0    |                      0.05 |   0   |  51   |  72.7 |
| qwen2.5:3b  | none             |                            38 | 52.6        |                      0    |                      0    |  30.1 |  46.6 |  78.8 |
| qwen2.5:3b  | hitl             |                            39 | 92.3        |                      0    |                      0.13 |  24.5 |  47.4 |  81.8 |
| qwen2.5:3b  | hitl-all         |                            11 | 100.0       |                      0.55 |                      0.4  |  24.5 |  45.9 |  81.8 |
| qwen2.5:3b  | hitl-fatigue     |                            11 | 63.6        |                      0    |                      0.12 |  27.5 |  44.8 |  81.8 |
| qwen2.5:3b  | hitl-approve-all |                            11 | 36.4        |                      0    |                      0.14 |  30.4 |  44.4 |  81.8 |
| qwen2.5:3b  | full             |                             2 | 100.0       |                      0    |                      0    |   0   |  57.5 |  90.9 |
| qwen2.5:3b  | full-fatigue     |                             3 | 100.0       |                      0    |                      0.01 |   0   |  52   |  90.9 |

### Table 5b – Gap 3: post-hoc audit-log detector

| Model       | Defense          |   Successful attacks | Recall (successful)   |   Recall (all attacked) |   Precision |   FPR (benign) |
|:------------|:-----------------|---------------------:|:----------------------|------------------------:|------------:|---------------:|
| gullible    | none             |                  102 | 100.0                 |                   100   |       100   |              0 |
| gullible    | hitl-approve-all |                  102 | 100.0                 |                   100   |       100   |              0 |
| gullible    | full             |                    0 | n/a                   |                    55.9 |         0   |              0 |
| ideal       | none             |                    7 | 100.0                 |                    48   |        14.3 |              0 |
| ideal       | hitl-approve-all |                    7 | 100.0                 |                    48   |        14.3 |              0 |
| ideal       | full             |                    0 | n/a                   |                    41.2 |         0   |              0 |
| llama3.2:3b | none             |                   19 | 100.0                 |                    48   |        38.8 |              0 |
| llama3.2:3b | full             |                    0 | n/a                   |                     4.9 |         0   |              0 |
| qwen2.5:3b  | none             |                   92 | 100.0                 |                    56.2 |        53.5 |              0 |
| qwen2.5:3b  | hitl-approve-all |                   31 | 100.0                 |                    50   |        60.8 |              0 |
| qwen2.5:3b  | full             |                    0 | n/a                   |                     0.3 |         0   |              0 |

### Table 6 – E5 ablation (one component removed at a time, %)

| Model       | Configuration      |   ASR | ΔASR vs full (pts)   |   NRP |    BU |   PVR |   Approvals / benign |
|:------------|:-------------------|------:|:---------------------|------:|------:|------:|---------------------:|
| gullible    | full system        |   0   | –                    |  58.8 | 100   |   0   |                    0 |
| gullible    | – allowlist        |  27.5 | +27.5                |  68.3 | 100   |   0   |                    0 |
| gullible    | – scoped creds     |   9.8 | +9.8                 |  53.1 | 100   |  14.7 |                    0 |
| gullible    | – human approval   |   0   | +0.0                 |  58.8 | 100   |   0   |                    0 |
| gullible    | none (all removed) | 100   | +100.0               |   0   | 100   |  72.5 |                    0 |
| ideal       | full system        |   0   | –                    |  58.8 | 100   |   0   |                    0 |
| ideal       | – allowlist        |   6.9 | +6.9                 |  81.3 | 100   |   0   |                    0 |
| ideal       | – scoped creds     |   0   | +0.0                 |  58.8 | 100   |   0   |                    0 |
| ideal       | – human approval   |   0   | +0.0                 |  58.8 | 100   |   0   |                    0 |
| ideal       | none (all removed) |   6.9 | +6.9                 |  81.3 | 100   |   0   |                    0 |
| llama3.2:3b | full system        |   0   | –                    |  51   |  72.7 |   0   |                    0 |
| llama3.2:3b | none (all removed) |  18.6 | +18.6                |  44.7 |  72.7 |   1   |                    0 |
| qwen2.5:3b  | full system        |   0   | –                    |  57.5 |  90.9 |   0   |                    0 |
| qwen2.5:3b  | – allowlist        |  24.8 | +24.8                |  48.6 |  87.9 |   0   |                    0 |
| qwen2.5:3b  | – scoped creds     |   0   | +0.0                 |  58.2 |  84.8 |   2.9 |                    0 |
| qwen2.5:3b  | – human approval   |   0   | +0.0                 |  57.5 |  93.9 |   0   |                    0 |
| qwen2.5:3b  | none (all removed) |  30.1 | +30.1                |  46.6 |  78.8 |  12.4 |                    0 |

### Table 7 – E6 efficiency and reliability

| Model       | Defense           |   Tokens / ep |   Guard tokens / ep |   Sec / ep |   Tool calls / ep |   Text-recovered calls |   Max-steps/loop/timeout |   Infra errors |   Retries |
|:------------|:------------------|--------------:|--------------------:|-----------:|------------------:|-----------------------:|-------------------------:|---------------:|----------:|
| llama3.2:3b | full              |          1032 |                   0 |       50.6 |              1.38 |                    0   |                      0   |              0 |         0 |
| llama3.2:3b | llm_guard         |          1339 |                 204 |       92.5 |              1.29 |                    2.7 |                      0.9 |              0 |         0 |
| llama3.2:3b | none              |          1185 |                   0 |       83.9 |              1.35 |                    8   |                      0.9 |              0 |         0 |
| llama3.2:3b | safety_prompt     |          1293 |                   0 |       72.8 |              1.3  |                    7.1 |                      0   |              0 |         0 |
| qwen2.5:3b  | allowlist         |          1906 |                   0 |      124.1 |              1.67 |                    0   |                      5.3 |              0 |         0 |
| qwen2.5:3b  | allowlist+scoped  |          1710 |                   0 |       18.5 |              1.45 |                    0   |                      1.8 |              0 |         0 |
| qwen2.5:3b  | full              |          1699 |                   0 |       19   |              1.43 |                    0   |                      1.5 |              0 |         0 |
| qwen2.5:3b  | full-fatigue      |          1826 |                   0 |      104.3 |              1.59 |                    0   |                      3.5 |              0 |         0 |
| qwen2.5:3b  | full-no-allowlist |          2128 |                   0 |      100.1 |              1.8  |                    0   |                      0   |              0 |         0 |
| qwen2.5:3b  | full-no-scoped    |          1950 |                   0 |       95.2 |              1.71 |                    0   |                      1.5 |              0 |         0 |
| qwen2.5:3b  | hitl              |          2097 |                   0 |       26.6 |              1.71 |                    0   |                      0.3 |              0 |         0 |
| qwen2.5:3b  | hitl-all          |          2050 |                   0 |      104.4 |              1.67 |                    0   |                      0   |              0 |         0 |
| qwen2.5:3b  | hitl-approve-all  |          2129 |                   0 |      109.2 |              1.75 |                    0   |                      0   |              0 |         0 |
| qwen2.5:3b  | hitl-fatigue      |          2102 |                   0 |      106.9 |              1.73 |                    0   |                      0   |              0 |         0 |
| qwen2.5:3b  | llm_guard         |          2359 |                 276 |       30.4 |              1.7  |                    0   |                      0.6 |              0 |         0 |
| qwen2.5:3b  | none              |          2138 |                   0 |       34.1 |              1.74 |                    0   |                      0.9 |              0 |         0 |
| qwen2.5:3b  | safety_prompt     |          2222 |                   0 |       42.7 |              1.7  |                    0   |                      1.8 |              0 |         0 |
| qwen2.5:3b  | scoped            |          2124 |                   0 |       27.2 |              1.73 |                    0   |                      0.3 |              0 |         0 |

### Table 8 – E2 comparison with the base paper (MSB)

| Source                          | Setting          |   ASR |   PUA |   NRP | OP ASR   |
|:--------------------------------|:-----------------|------:|------:|------:|:---------|
| MSB paper (reported, 10 models) | none             |  40.4 |  56.5 |  33.7 | 76.5     |
| MSB paper (reported, 10 models) | MCIP guard       |  28.7 |  48.9 |  34.9 | n/r      |
| ours, reproduced (llama3.2:3b)  | none             |  18.6 |  54.9 |  44.7 | 85.7     |
| ours, reproduced (llama3.2:3b)  | MCIP-style guard |  12.7 |  38.2 |  33.4 | 28.6     |
| ours, reproduced (qwen2.5:3b)   | none             |  30.1 |  66.7 |  46.6 | 95.2     |
| ours, reproduced (qwen2.5:3b)   | MCIP-style guard |  24.5 |  62.4 |  47.1 | 95.2     |

### Gap-resolution table

| Gap                                         | Method / component                                                          | Metric                                                      | Base paper result                                  | Our result                                                                                                                                                                | Addressed?   |
|:--------------------------------------------|:----------------------------------------------------------------------------|:------------------------------------------------------------|:---------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|
| Gap 1 – system-level mitigations unmeasured | Pinned tool allowlist + scoped credentials (gateway)                        | ASR, NRP vs MCIP-style guard                                | MCIP: ASR 40.35→28.69%, NRP 33.7→34.88% (reported) | qwen2.5:3b: ASR 30.1→0.0, NRP 57.5 vs guard 47.1                                                                                                                          | Partially    |
| Gap 2 – no identity/authority model         | Identity model + user-scoped credentials; PE and CD attack classes          | PVR, CD ASR, BU                                             | not expressible in MSB (no authority model)        | qwen2.5:3b: PVR 12.4→0.0, CD 0.0→0.0, BU Δ +3.0 pts; gullible: PVR 72.5→0.0, CD 100.0→0.0, BU Δ -0.0 pts                                                                  | Partially    |
| Gap 3 – oversight benefit/cost unquantified | Risk-tiered HITL with simulated approvers + hash-chained audit log detector | stop rate, approvals/benign task, detector recall/precision | not measured in MSB                                | qwen2.5:3b: stop 92.3 (fatigue 63.6), 0.00 approvals/benign, detector R 100.0 P 53.5; gullible: stop 87.7 (fatigue 63.0), 0.00 approvals/benign, detector R 100.0 P 100.0 | Partially    |

Notes:
- Gap 1: only 1 eligible model(s) ran both allowlist+scoped and the guard; the Phase 1 criterion needs 3 of 4 models, so it counts as not met.
- qwen2.5:3b: CD never succeeds undefended, so the -80% criterion could not be tested and counts as not met.
