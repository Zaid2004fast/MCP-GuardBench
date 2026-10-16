# Results summary

## Overall (per model x defense)

| model                    | defense   |   n_attack |   ASR |   PUA |   PVR |   blocked_per_ep |   approvals_per_ep |   tool_calls_per_ep |   tokens_per_ep |   sec_per_ep |   errors |   NRP |   BU |
|:-------------------------|:----------|-----------:|------:|------:|------:|-----------------:|-------------------:|--------------------:|----------------:|-------------:|---------:|------:|-----:|
| groq:openai/gpt-oss-120b | none      |         60 |   0.7 | 0.817 | 0.317 |                0 |                  0 |               2.367 |         2732.73 |       14.801 |        0 | 0.245 |    1 |

## ASR (%) by attack class

| attack_class   |   groq:openai/gpt-oss-120b |
|:---------------|---------------------------:|
| CD             |                     0      |
| FE             |                    83.3333 |
| NC             |                   100      |
| OP             |                   100      |
| PE             |                   100      |
| PI             |                    66.6667 |
| PM             |                   100      |
| RI             |                    50      |
| TT             |                   100      |
| UI             |                     0      |
