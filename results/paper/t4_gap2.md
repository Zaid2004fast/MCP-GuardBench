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
