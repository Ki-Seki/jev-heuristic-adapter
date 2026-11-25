# Heuristic adapter evaluation

Run complete: True. Completed groups: 90/90.

| Method | Model | Dataset | Shot | Accuracy | Macro F1 | Errors | p50 ms | p95 ms | Cost range, USD |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| compile | gpt-6-astra | agnews | 0 | 85.00% | 84.93% | 0 | 0.121 | 0.485 | 2.1556–2.1556 |
| compile | gpt-6-astra | agnews | 1 | 88.67% | 88.46% | 0 | 0.093 | 0.158 | 1.5980–1.5980 |
| compile | gpt-6-astra | agnews | 2 | 85.33% | 85.13% | 0 | 0.188 | 0.293 | 1.7183–1.7183 |
| compile | gpt-6-astra | banking77 | 0 | 69.00% | 63.42% | 0 | 0.634 | 0.879 | 1.3533–1.3533 |
| compile | gpt-6-astra | banking77 | 1 | 64.33% | 58.51% | 0 | 0.326 | 0.647 | 1.3741–1.3741 |
| compile | gpt-6-astra | banking77 | 2 | 68.00% | 62.65% | 0 | 0.129 | 0.609 | 1.3881–1.3881 |
| compile | gpt-6-astra | sst2 | 0 | 72.33% | 69.39% | 0 | 0.089 | 0.177 | 1.3130–1.3130 |
| compile | gpt-6-astra | sst2 | 1 | 73.67% | 71.48% | 0 | 0.112 | 0.196 | 1.7301–1.7301 |
| compile | gpt-6-astra | sst2 | 2 | 75.00% | 72.82% | 0 | 0.132 | 0.214 | 1.4131–1.4131 |
| compile | gpt-6-luna | agnews | 0 | 72.67% | 72.95% | 0 | 0.401 | 0.634 | 0.0018–0.0018 |
| compile | gpt-6-luna | agnews | 1 | 74.67% | 74.40% | 0 | 0.298 | 0.563 | 0.0020–0.0020 |
| compile | gpt-6-luna | agnews | 2 | 75.00% | 75.33% | 0 | 2.179 | 2.904 | 0.0031–0.0031 |
| compile | gpt-6-luna | banking77 | 0 | 40.00% | 38.34% | 0 | 14.594 | 16.343 | 0.0055–0.0055 |
| compile | gpt-6-luna | banking77 | 1 | 18.67% | 21.41% | 0 | 0.091 | 0.160 | 0.0038–0.0038 |
| compile | gpt-6-luna | banking77 | 2 | 30.00% | 31.38% | 0 | 0.115 | 0.317 | 0.0046–0.0046 |
| compile | gpt-6-luna | sst2 | 0 | 66.67% | 65.71% | 0 | 0.581 | 1.150 | 0.0023–0.0023 |
| compile | gpt-6-luna | sst2 | 1 | 68.33% | 67.31% | 0 | 0.114 | 0.276 | 0.0035–0.0035 |
| compile | gpt-6-luna | sst2 | 2 | 72.33% | 72.17% | 0 | 0.070 | 0.157 | 0.0019–0.0019 |
| compile | gpt-6-sol | agnews | 0 | 75.33% | 74.87% | 0 | 0.257 | 0.348 | 0.0818–0.0818 |
| compile | gpt-6-sol | agnews | 1 | 81.00% | 80.75% | 0 | 2.289 | 3.960 | 0.0930–0.0930 |
| compile | gpt-6-sol | agnews | 2 | 80.00% | 79.65% | 0 | 0.094 | 0.169 | 0.0661–0.0661 |
| compile | gpt-6-sol | banking77 | 0 | 49.33% | 47.61% | 0 | 0.392 | 2.280 | 0.1657–0.1657 |
| compile | gpt-6-sol | banking77 | 1 | 46.00% | 47.60% | 0 | 0.062 | 0.210 | 0.1103–0.1103 |
| compile | gpt-6-sol | banking77 | 2 | 40.00% | 37.77% | 0 | 0.167 | 0.365 | 0.1214–0.1214 |
| compile | gpt-6-sol | sst2 | 0 | 70.67% | 70.65% | 0 | 0.027 | 0.045 | 0.1008–0.1008 |
| compile | gpt-6-sol | sst2 | 1 | 77.00% | 76.98% | 0 | 0.080 | 0.134 | 0.1119–0.1119 |
| compile | gpt-6-sol | sst2 | 2 | 78.33% | 78.32% | 0 | 0.034 | 0.062 | 0.0943–0.0943 |
| compile | gpt-6.1-sol | agnews | 0 | 87.33% | 87.04% | 0 | 0.128 | 0.193 | 0.3255–0.3255 |
| compile | gpt-6.1-sol | agnews | 1 | 87.67% | 87.30% | 0 | 0.279 | 0.372 | 0.2824–0.2824 |
| compile | gpt-6.1-sol | agnews | 2 | 87.00% | 86.75% | 0 | 1.008 | 1.364 | 0.3137–0.3137 |
| compile | gpt-6.1-sol | banking77 | 0 | 60.33% | 58.15% | 0 | 0.626 | 0.896 | 0.2664–0.2664 |
| compile | gpt-6.1-sol | banking77 | 1 | 66.00% | 60.29% | 0 | 2.982 | 3.585 | 0.2596–0.2596 |
| compile | gpt-6.1-sol | banking77 | 2 | 65.00% | 62.40% | 0 | 0.148 | 0.655 | 0.2481–0.2481 |
| compile | gpt-6.1-sol | sst2 | 0 | 74.00% | 71.55% | 0 | 0.124 | 0.233 | 0.2638–0.2638 |
| compile | gpt-6.1-sol | sst2 | 1 | 74.00% | 71.79% | 0 | 0.116 | 0.200 | 0.2829–0.2829 |
| compile | gpt-6.1-sol | sst2 | 2 | 76.00% | 74.26% | 0 | 0.092 | 0.157 | 0.3252–0.3252 |
| compile | gpt-6.1-terra | agnews | 0 | 76.00% | 76.01% | 0 | 0.603 | 0.940 | 0.0483–0.0483 |
| compile | gpt-6.1-terra | agnews | 1 | 78.33% | 78.35% | 0 | 0.460 | 0.681 | 0.0489–0.0489 |
| compile | gpt-6.1-terra | agnews | 2 | 79.33% | 79.33% | 0 | 0.355 | 0.528 | 0.0628–0.0628 |
| compile | gpt-6.1-terra | banking77 | 0 | 61.00% | 55.95% | 0 | 0.082 | 0.329 | 0.0563–0.0563 |
| compile | gpt-6.1-terra | banking77 | 1 | 27.67% | 33.44% | 187 | 0.125 | 0.236 | 0.0507–0.0507 |
| compile | gpt-6.1-terra | banking77 | 2 | 56.00% | 53.37% | 0 | 0.072 | 1.349 | 0.0563–0.0563 |
| compile | gpt-6.1-terra | sst2 | 0 | 66.67% | 61.49% | 0 | 0.026 | 0.043 | 0.0365–0.0365 |
| compile | gpt-6.1-terra | sst2 | 1 | 71.67% | 68.93% | 0 | 0.183 | 0.318 | 0.0535–0.0535 |
| compile | gpt-6.1-terra | sst2 | 2 | 68.67% | 64.57% | 0 | 0.046 | 0.081 | 0.0387–0.0387 |
| compile | gpt-6.2-astra | agnews | 0 | 87.00% | 86.81% | 0 | 0.368 | 0.597 | 0.6831–0.6831 |
| compile | gpt-6.2-astra | agnews | 1 | 89.00% | 88.98% | 0 | 0.245 | 0.414 | 0.7060–0.7060 |
| compile | gpt-6.2-astra | agnews | 2 | 88.67% | 88.36% | 0 | 0.162 | 0.296 | 0.6502–0.6502 |
| compile | gpt-6.2-astra | banking77 | 0 | 69.67% | 63.98% | 0 | 0.216 | 0.553 | 0.7030–0.7030 |
| compile | gpt-6.2-astra | banking77 | 1 | 70.33% | 67.38% | 0 | 0.294 | 0.971 | 0.8573–0.8573 |
| compile | gpt-6.2-astra | banking77 | 2 | 69.33% | 62.78% | 0 | 0.734 | 1.618 | 0.6984–0.6984 |
| compile | gpt-6.2-astra | sst2 | 0 | 82.00% | 81.44% | 0 | 0.187 | 0.348 | 1.6443–1.6443 |
| compile | gpt-6.2-astra | sst2 | 1 | 82.00% | 81.57% | 0 | 0.326 | 0.571 | 0.7880–0.7880 |
| compile | gpt-6.2-astra | sst2 | 2 | 80.67% | 79.86% | 0 | 0.213 | 0.386 | 1.1258–1.1258 |
| compile | gpt-6.2-sol | agnews | 0 | 82.00% | 82.07% | 0 | 0.346 | 0.532 | 0.1271–0.1271 |
| compile | gpt-6.2-sol | agnews | 1 | 83.67% | 83.98% | 0 | 0.272 | 0.476 | 0.2342–0.2342 |
| compile | gpt-6.2-sol | agnews | 2 | 82.33% | 82.08% | 0 | 0.249 | 0.369 | 0.2051–0.2051 |
| compile | gpt-6.2-sol | banking77 | 0 | 62.00% | 58.85% | 0 | 0.508 | 0.803 | 0.2314–0.2314 |
| compile | gpt-6.2-sol | banking77 | 1 | 58.00% | 57.63% | 0 | 0.137 | 0.405 | 0.1996–0.1996 |
| compile | gpt-6.2-sol | banking77 | 2 | 64.33% | 58.83% | 0 | 0.257 | 0.613 | 0.3023–0.3023 |
| compile | gpt-6.2-sol | sst2 | 0 | 74.33% | 72.21% | 0 | 0.163 | 0.280 | 0.2761–0.2761 |
| compile | gpt-6.2-sol | sst2 | 1 | 78.00% | 76.40% | 0 | 0.227 | 0.477 | 0.1911–0.1911 |
| compile | gpt-6.2-sol | sst2 | 2 | 74.33% | 72.42% | 0 | 0.254 | 0.469 | 0.3184–0.3184 |
| decisions | gpt-6-luna | agnews | 0 | 92.67% | 92.48% | 0 | 122.978 | 164.023 | 0.0088–0.0088 |
| decisions | gpt-6-luna | agnews | 1 | 92.00% | 91.80% | 0 | 121.475 | 163.335 | 0.0112–0.0112 |
| decisions | gpt-6-luna | agnews | 2 | 92.00% | 91.78% | 0 | 122.706 | 166.208 | 0.0128–0.0128 |
| decisions | gpt-6-luna | banking77 | 0 | 81.67% | 76.56% | 0 | 127.892 | 195.029 | 0.0389–0.0389 |
| decisions | gpt-6-luna | banking77 | 1 | 81.33% | 76.66% | 0 | 124.660 | 184.302 | 0.0399–0.0399 |
| decisions | gpt-6-luna | banking77 | 2 | 82.33% | 77.11% | 0 | 123.470 | 176.844 | 0.0408–0.0408 |
| decisions | gpt-6-luna | sst2 | 0 | 92.00% | 91.99% | 0 | 122.419 | 189.719 | 0.0046–0.0052 |
| decisions | gpt-6-luna | sst2 | 1 | 95.00% | 94.99% | 0 | 125.567 | 175.578 | 0.0061–0.0061 |
| decisions | gpt-6-luna | sst2 | 2 | 94.67% | 94.66% | 0 | 121.518 | 167.730 | 0.0069–0.0069 |
| jev | typesafe/jev-1.13 | agnews | 0 | 91.33% | 91.05% | 0 | 74.728 | 100.286 | 0.0064–0.0064 |
| jev | typesafe/jev-1.13 | agnews | 1 | 90.67% | 90.40% | 0 | 73.862 | 108.761 | 0.0075–0.0075 |
| jev | typesafe/jev-1.13 | agnews | 2 | 91.00% | 90.75% | 0 | 74.095 | 106.790 | 0.0082–0.0082 |
| jev | typesafe/jev-1.13 | banking77 | 0 | 80.67% | 73.37% | 0 | 83.093 | 123.407 | 0.0249–0.0249 |
| jev | typesafe/jev-1.13 | banking77 | 1 | 82.00% | 75.33% | 0 | 84.520 | 142.865 | 0.0254–0.0254 |
| jev | typesafe/jev-1.13 | banking77 | 2 | 82.67% | 75.94% | 0 | 85.421 | 131.247 | 0.0258–0.0258 |
| jev | typesafe/jev-1.13 | sst2 | 0 | 96.33% | 96.32% | 0 | 80.641 | 138.627 | 0.0044–0.0044 |
| jev | typesafe/jev-1.13 | sst2 | 1 | 96.67% | 96.65% | 0 | 72.742 | 103.796 | 0.0051–0.0051 |
| jev | typesafe/jev-1.13 | sst2 | 2 | 96.67% | 96.65% | 0 | 72.701 | 105.051 | 0.0054–0.0054 |
| jev | typesafe/jev-1.14 | agnews | 0 | 91.33% | 91.10% | 0 | 76.988 | 118.563 | 0.0064–0.0064 |
| jev | typesafe/jev-1.14 | agnews | 1 | 91.00% | 90.75% | 0 | 76.351 | 118.447 | 0.0075–0.0075 |
| jev | typesafe/jev-1.14 | agnews | 2 | 90.00% | 89.75% | 0 | 78.163 | 114.443 | 0.0082–0.0082 |
| jev | typesafe/jev-1.14 | banking77 | 0 | 82.67% | 76.22% | 0 | 85.758 | 130.178 | 0.0249–0.0249 |
| jev | typesafe/jev-1.14 | banking77 | 1 | 83.33% | 77.31% | 0 | 83.052 | 123.405 | 0.0254–0.0254 |
| jev | typesafe/jev-1.14 | banking77 | 2 | 83.67% | 77.82% | 0 | 84.251 | 129.313 | 0.0258–0.0258 |
| jev | typesafe/jev-1.14 | sst2 | 0 | 96.67% | 96.65% | 0 | 74.472 | 106.636 | 0.0044–0.0044 |
| jev | typesafe/jev-1.14 | sst2 | 1 | 96.33% | 96.32% | 0 | 74.513 | 109.076 | 0.0051–0.0051 |
| jev | typesafe/jev-1.14 | sst2 | 2 | 96.33% | 96.32% | 0 | 75.768 | 104.835 | 0.0054–0.0054 |

Costs include every attempt, including failures: known $28.5454;
conservative upper estimate $28.5478;
11 attempts with unknown billed usage.

Seven GPT models compile with explicit high reasoning effort, 0/1/2 training examples,
and 48k initial output limits. Only truncation raises the next limit to 96k, then 128k.
At most three attempts; the first syntactically valid, loadable program is retained.
No correctness gate and no test-label feedback. Predictions that error count as incorrect;
uncompilable groups have null accuracy. Macro F1 averages over all declared labels.
OpenAI Decisions and OpenRouter Jev 1.13/1.14 classify the same test inputs directly,
using the same 0/1/2-shot training examples. Jev uses native `state`/`questions` requests;
its reported `usage.cost` takes precedence over token-price estimates.

Program latency includes input copying and output validation, without network calls.
Direct API latency includes failed request time but excludes retry backoff.
Cached replay durations come from recorded requests, not current wall time.
`api_seconds` is summed request time; it is not concurrent wall time.

`manifest.json` pins code, dependencies, datasets, training examples and test cohorts.
`programs/` contains generated source; `predictions/` contains per-example outputs.
`calls/` contains request payloads, responses, partial source and attempt receipts.
`data/` contains the frozen inputs, and `summary.jsonl` contains the full metrics.
Commit this run directory to GitHub with the evaluation code.
All generations are fresh for this run; resuming the same directory reuses only its records.

Tasks follow [dhruvmehra/jevbench](https://github.com/dhruvmehra/jevbench/tree/c983cc4a7dd9fc142ca3b6c7a813cae0e963c902):
[SST-2](https://huggingface.co/datasets/stanfordnlp/sst2),
[AG News](https://huggingface.co/datasets/fancyzhx/ag_news),
[Banking77](https://huggingface.co/datasets/legacy-datasets/banking77).
The fixed 300-example cohorts differ from upstream's historical 500-example Jev results;
no historical score is presented as a fresh measurement.
