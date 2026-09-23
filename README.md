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

Indicative comparison for repeated inputs sharing a fixed question definition.

| Dimension | Jev API | System One Adapter (LLM API) | This adapter |
| --- | --- | --- | --- |
| Repeat-call latency | ~70–500 ms, vendor-reported | Model-dependent LLM response time | **Local Python execution**; µs–ms for simple rules |
| First-call cost | One Jev API call | One LLM inference call | Upfront LLM code generation per question |
| Marginal cost | Jev API fees per input | LLM token charges per input | **Local compute only; no LLM tokens** |
| Accuracy | Learned decisions; task-dependent | Depends on the model and task | Depends on generated rules; can be exact for explicit logic |
| Best fit | Low-latency typed decisions | Flexible language and semantic tasks | **High-volume inputs with stable questions** |

Jev latency is [reported by TypeSafe](https://typesafe.ai/blog/introducing-system-one-models-and-jev); local latency depends on the generated program and input size.

## Quickstart

Open [example.ipynb](example.ipynb) for an annotated walkthrough with generated source, predictions, and cache reuse.

## Acknowledgments

Thanks to:

- Jiayi Weng for [Learning Beyond Gradients](https://trinkle23897.github.io/learning-beyond-gradients/).
- TypeSafe for [System One Adapter](https://github.com/typesafe-ai/system-one-adapter-python).
