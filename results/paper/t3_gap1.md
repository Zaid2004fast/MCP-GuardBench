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
