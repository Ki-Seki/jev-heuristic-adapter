# Classification evaluation

Seven GPT-6 / 6.1 / 6.2 models compile one program per task with **explicit `high`**
reasoning effort. SST-2, AG News, and Banking77 each use 300 fixed test examples
and 0/1/2 training examples: **63 new programs**, plus **2,700 Decisions API calls**
using GPT-6 Luna. Prior model outputs are never imported.

```sh
# Offline: inspect the matrix. This does not generate programs or download data.
uv run --locked --extra openai --group eval python -m evals plan

# After approving the experiment: freeze datasets, then run with a chosen budget.
uv run --locked --extra openai --group eval python -m evals prepare --output evals/runs/RUN_NAME
uv run --locked --extra openai --group eval python -m evals run --output evals/runs/RUN_NAME --budget-usd 50
```

Only `run` makes paid calls. Results are ordinary files under `evals/runs/RUN_NAME/`;
commit that directory to GitHub after the run. The illustrative $50 spend ceiling can stop an
unfinished run; it is not a promise that all retries fit. Re-run the same command
to resume recorded work. Use one process per run directory; use a new directory
for a genuinely fresh evaluation. A changed source or lockfile requires a new run.

## Protocol

- `tasks.json` pins dataset revisions, label definitions, two training row IDs,
  and test-cohort hashes. One-shot uses the first of the same two examples.
- Test rows match the earlier 300-example evaluation, excluding the upstream
  seed-0 cohort of 500. These are previously studied cohorts, not a new holdout.
- Every generation starts at 48k output tokens. Only a token-limit truncation
  increases the next cap to 96k, then 128k. API and syntax/loading failures may
  retry at the current cap, with at most **three total attempts**. SDK retries are off.
- Keep the first syntactically valid, loadable program. No example-correctness
  gate, test feedback, or selection by accuracy. Prediction errors stay in the score.
- Program latency measures trusted in-process execution, input copying and output
  validation. It excludes code generation and SDK answer wrapping. No sandbox is added.
- Costs include **all** attempts. Missing usage remains unknown and reserves a
  conservative estimate, rather than being counted as free. Prices are pinned
  in `api.py`; the spend check reserves output caps and a conservative input estimate.
- The Decisions API returns typed choices directly. Compiler reasoning effort and
  output-token caps do not apply to this separate endpoint.

## Files

`data.py` prepares inputs; `api.py` records calls and cost; `run.py` runs the two
methods; `results.py` writes metrics and a Markdown table. `__main__.py` only handles the CLI.

A run saves a `README.md` comparison table, full metrics in `summary.jsonl`,
generated `programs/`, per-example `predictions/`, and every request/response in
`calls/`, including failures and partial code. `data/` and `manifest.json` preserve
the inputs and source revisions; `run.json` states whether the experiment finished.
Everything remains readable on GitHub without unpacking an archive. Ruff skips
`evals/runs/` so committing results never reformats or rejects generated code.

The protocol follows [dhruvmehra/jevbench](https://github.com/dhruvmehra/jevbench/tree/c983cc4a7dd9fc142ca3b6c7a813cae0e963c902).
Its published Jev results use a different 500-example cohort and remain a historical
reference, not a fresh result from this runner.
