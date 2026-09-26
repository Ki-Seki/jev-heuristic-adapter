# Experiment B: bounded execution feedback

This branch's launcher defaults to `--method feedback`: start from the exact
Experiment A program, run synthetic diagnostics, request two revisions, and select
on a separate synthetic selection set. Real test inputs are opened only after all
candidate choices are frozen. The existing package `compile()` remains unchanged;
feedback is an explicit experiment, not a hidden example-acceptance gate.

The measured results use shared harness commit `a86a79e`. The branch-specific
launcher adds method selection without changing prompts or inference. Both PRs
share the same baseline and initial prompt programs, so their comparison does not
mix different initial generations.

See [the protocol and run commands](compile_feedback/README.md),
[the measured results](compile_feedback/results/RESULTS.md), and
[the interpretation](compile_feedback/results/FINDINGS.md).
