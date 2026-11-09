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
