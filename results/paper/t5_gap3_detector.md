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
