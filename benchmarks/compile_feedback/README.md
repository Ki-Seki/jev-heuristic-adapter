# Compile feedback experiment

Compare the current compiler prompt, an evidence-focused prompt, and the same
improved-prompt program followed by two rounds of execution feedback. These are
explicit experiments; the installed adapter's default compilation behavior is
unchanged.

Each model/task/method runs once. Models are `gpt-6-luna` and `gpt-6-sol`, both
using Responses, `high`, a 24,000-token output limit and SDK retries disabled.
The experiment uses the public classification tasks and label descriptions from
[dhruvmehra/jevbench](https://github.com/dhruvmehra/jevbench/tree/c983cc4a7dd9fc142ca3b6c7a813cae0e963c902).
The reused task definitions retain their upstream [MIT notice](UPSTREAM_LICENSE).

## Protocol

- Three tasks: SST-2, AG News and Banking77, 300 held-out inputs per task.
- Pin dataset revisions. Exclude the previously inspected seed-0 500-input cohort
  and its normalized duplicate texts; select distinct remaining texts with seed
  20260926. Verify the old cohort's checksum before freezing the new manifest.
- Preserve the upstream task definitions and label mapping, including the AG News
  ambiguity where tech-company earnings can be sci_tech in the instructions but
  business in the dataset. Do not relabel test answers.
- Generate synthetic diagnostics with `gpt-6-sol` from definitions alone, before
  compiling any program. Generate `max(6, ceil(120 / labels))` inputs per label:
  SST-2 120, AG News 120, Banking77 462. Split each label deterministically into
  roughly two-thirds feedback and one-third selection. No real training examples
  or test texts are included in model requests.
- Baseline and improved prompt each generate one program. The feedback arm reuses
  the *exact* improved-prompt program, then makes two additional model calls. It
  receives execution errors, prediction counts, confusions and at most 40 failed
  synthetic feedback examples per round. Selection texts/answers never enter the
  compiler conversation. Pick the highest synthetic selection accuracy, ties
  favoring the earliest candidate. Preserve every candidate, including failures.
- Freeze all programs before reading real evaluation texts. Exact synthetic/test
  text overlap aborts evaluation rather than silently resampling a better cohort.
- Use the real adapter for local serial inference, with one warmup. Count every
  runtime or output error as wrong. Report accuracy, macro-F1 over all declared
  labels, p50/p95, compilation fees and time, and relative-to-baseline changes.
- Charge a standalone feedback compilation for the full teacher cost, initial
  program and both revisions, even when it selects the initial program. Separately
  report the physical experiment fee, where shared requests are counted once.
  Cold time adds measured synthesis-family wall time, initial generation time and
  feedback-phase time; it depends on the recorded concurrency. CPU is not priced.
- Jev is a **historical reference on a different cohort/environment**, not a new
  paired run. Fee break-even is not quality equivalence. Bootstrap intervals are
  conditional on the frozen programs; one generation does not measure stochastic
  generation variance. Synthetic labels can be imperfect and favor teacher style.

## Run

For the branch-specific experiment, see [EXPERIMENT.md](../EXPERIMENT.md).
The full feedback ablation can be run explicitly:

```sh
uv run --locked --extra openai --with datasets==5.0.1 python -m benchmarks.compile_feedback.prepare --output .local/feedback-data
uv run --locked --extra openai python -m benchmarks.compile_feedback.run synthesize --method feedback --data .local/feedback-data --output .local/feedback-run
uv run --locked --extra openai python -m benchmarks.compile_feedback.run compile --method feedback --data .local/feedback-data --output .local/feedback-run
uv run --locked --extra openai python -m benchmarks.compile_feedback.run evaluate --method feedback --data .local/feedback-data --output .local/feedback-run
uv run --locked --extra openai python -m benchmarks.compile_feedback.report --run .local/feedback-run --data .local/feedback-data --output .local/feedback-report
```

Provider calls persist before a next stage begins. Completed identical requests
can be resumed; interrupted calls are never automatically resubmitted. The output
directory rejects protocol/code changes. Credentials are read from the process
environment or a hidden prompt, never persisted. `.local/` holds real input texts
and complete call traces; exported PR artifacts include all candidate sources,
synthetic examples, frozen input indices/checksums and per-input predictions.

Offline tests cover separation of feedback/selection/test inputs, bounded rounds,
selection of an earlier candidate after a regression, label normalization, failure
denominators, real-adapter replay, and cache-read/write token accounting.
