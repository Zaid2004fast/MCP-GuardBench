# Results summary

## Overall (per model x defense)

| model                   | defense   |   n_attack |      ASR |   PUA |   PVR |   blocked_per_ep |   approvals_per_ep |   tool_calls_per_ep |   tokens_per_ep |   sec_per_ep |   errors |      NRP |   BU |
|:------------------------|:----------|-----------:|---------:|------:|------:|-----------------:|-------------------:|--------------------:|----------------:|-------------:|---------:|---------:|-----:|
| groq:openai/gpt-oss-20b | none      |        101 | 0.554455 | 0.723 | 0.228 |                0 |                  0 |               1.554 |         2141.03 |         25.5 |        0 | 0.322027 |    1 |

## ASR (%) by attack class

| attack_class   |   groq:openai/gpt-oss-20b |
|:---------------|--------------------------:|
| CD             |                    0      |
| FE             |                   38.4615 |
| NC             |                  100      |
| OP             |                  100      |
| PE             |                  100      |
| PI             |                   27.7778 |
| PM             |                  100      |
| RI             |                    0      |
| TT             |                  100      |
| UI             |                   25      |
