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
