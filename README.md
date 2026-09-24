# Jev Heuristic Adapter

Compile fixed decision tasks into reusable heuristic programs.

## How it works

Compared with [System One Adapter](https://github.com/typesafe-ai/system-one-adapter-python), the evaluation flow adds a compilation step after initializing the respective clients:

```diff
+ client.compile(questions, examples)
  response = client.system_one(state=state, questions=questions)
```

`compile()` asks an LLM to generate a reusable Python program for each fixed question.
`system_one()` executes that program for new input states and returns SDK answers.

## Comparison

![Jev and direct LLM calls pay for remote inference on each input; this adapter pays for code generation upfront and reuses local Python. Jev reports 70–500 ms, LLM latency depends on the model, and simple local rules can run in µs–ms. Accuracy remains task-dependent.](https://raw.githubusercontent.com/Ki-Seki/jev-heuristic-adapter/main/assets/comparison.svg)


## Quickstart

Open [example.ipynb](https://github.com/Ki-Seki/jev-heuristic-adapter/blob/main/example.ipynb) for an annotated walkthrough with generated source, predictions, and cache reuse.

## Acknowledgments

Thanks to:

- Jiayi Weng for [Learning Beyond Gradients](https://trinkle23897.github.io/learning-beyond-gradients/).
- TypeSafe for [System One Adapter](https://github.com/typesafe-ai/system-one-adapter-python).
