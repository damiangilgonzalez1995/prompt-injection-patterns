# Transcripts

What actually went to the model, and what came back - for every pattern
against every payload, without the defence and with it.

Current capture: mode `live`, model `openai:gpt-4o-mini`.

| Pattern | Guardian | Transcript |
|---|---|---|
| Action-Selector | fixed action list | [`p01_action_selector.md`](p01_action_selector.md) |
| Plan-Then-Execute | frozen plan | [`p02_plan_then_execute.md`](p02_plan_then_execute.md) |
| LLM Map-Reduce | map-output sanitizer | [`p03_llm_map_reduce.md`](p03_llm_map_reduce.md) |
| Dual LLM | privileged LLM + symbolic memory | [`p04_dual_llm.md`](p04_dual_llm.md) |
| Code-Then-Execute | execution sandbox | [`p05_code_then_execute.md`](p05_code_then_execute.md) |
| Context-Minimization | context pruner | [`p06_context_minimization.md`](p06_context_minimization.md) |

## Regenerate

```bash
# offline, deterministic, free (default)
python -m benchmark.capture_transcripts

# against a real model - needs a key in .env
pip install -e '.[llm]'
TEST_MODE=live python -m benchmark.capture_transcripts
```

## How to read these

Each call is collapsed into a `<details>` block that states two things
before you open it:

- **payload IS / is NOT in this prompt** - did untrusted text reach this
  context at all? This is the architectural question. Dual LLM and
  Context-Minimization win here: the payload is simply never present.
- **the model ate it** - given that the payload was present, did the model
  follow it? In mock mode the answer is always yes, by construction. In
  live mode it is the real model's decision.

The second line is why the first line matters. A defence that depends on
the model *not* eating a payload it can see is a defence that works until
the day it doesn't. A defence that keeps the payload out of the context
does not have that failure mode.
