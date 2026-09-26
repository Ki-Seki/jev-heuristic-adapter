# Experiment B findings

Two rounds of synthetic execution feedback provided no clear advantage over the exact starting program: two cases gained 1 point, two regressed, and two were unchanged. The equally weighted six-condition mean changed from 58.22% to 58.11%. Cold compilation fees were 3.9–35.7 times the prompt-only fees, including synthesis and all revisions. This run does not justify adopting feedback as the default.

| Model | Task | Original | Improved prompt | + Feedback | Feedback vs prompt |
| --- | --- | ---: | ---: | ---: | ---: |
| gpt-6-luna | sst2 | 60.3% | 71.0% | 71.0% | +0.0 pp |
| gpt-6-luna | agnews | 27.0% | 60.7% | 61.7% | +1.0 pp |
| gpt-6-luna | banking77 | 28.3% | 35.3% | 33.0% | -2.3 pp |
| gpt-6-sol | sst2 | 68.3% | 65.7% | 66.7% | +1.0 pp |
| gpt-6-sol | agnews | 77.0% | 74.0% | 73.7% | -0.3 pp |
| gpt-6-sol | banking77 | 41.0% | 42.7% | 42.7% | +0.0 pp |

Each condition was run once on the same 300 unseen inputs per task. This is an exploratory comparison of frozen programs, not an estimate of generation variance. No programs were repaired, rejected, or selected using these test results. All 5,400 scored predictions completed without runtime/schema errors.

A material baseline failure: the Luna AG News program returns a string from `_collect_text(state)` and then applies `" ".join(...)` to that string, separating its characters. The word rules stop matching, and all 300 inputs fall back to sports (81/300 correct). Its +33.7-point prompt improvement therefore partly reflects avoiding this particular generation bug. We retained it rather than silently repairing or replacing it.

The complete shared collection used 33 model calls, including synthetic diagnostics, at an API usage estimate of $1.6424628. Tables charge each feedback deployment for its entire cold-start teacher cost even though this experiment shared teacher data and initial programs. Token usage, cache writes, all candidate sources, selected rounds and per-input predictions are retained. Test texts are not redistributed; pinned revisions, indices and checksums reproduce them.

`programs.jsonl` hashes use the harness's canonical-JSON SHA-256 function. `summary.json` records the measured harness source hashes; the measured engine is Git commit `a86a79e`.
