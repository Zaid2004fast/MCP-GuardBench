# Results summary

## Overall (per model x defense)

| model               | defense       |   n_attack |      ASR |   PUA |   PVR |   blocked_per_ep |   approvals_per_ep |   tool_calls_per_ep |   tokens_per_ep |   sec_per_ep |   errors |      NRP |   BU |
|:--------------------|:--------------|-----------:|---------:|------:|------:|-----------------:|-------------------:|--------------------:|----------------:|-------------:|---------:|---------:|-----:|
| ollama:qwen2.5:1.5b | none          |        128 | 0.242188 | 0.57  | 0.094 |                0 |                  0 |               1.203 |         1805.31 |       17.099 |        0 | 0.43219  |  0.8 |
| ollama:qwen2.5:1.5b | safety_prompt |        128 | 0.242188 | 0.539 | 0.07  |                0 |                  0 |               1.109 |         1883.14 |       17.274 |        0 | 0.408508 |  0.8 |

## ASR (%) by attack class

| attack_class   |   ollama:qwen2.5:1.5b |
|:---------------|----------------------:|
| CD             |                   0   |
| FE             |                   0   |
| NC             |                 100   |
| OP             |                  90   |
| PE             |                   0   |
| PI             |                   0   |
| PM             |                  55   |
| RI             |                   0   |
| TT             |                   0   |
| UI             |                  32.5 |
