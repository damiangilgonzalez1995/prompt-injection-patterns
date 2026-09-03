# legacy/

The first implementation of this repo: a plain-Python, offline, mock-driven
catalogue. It still runs and its tests still pass, but the project has moved to
the LangGraph architecture in `blueprint/` (built step by step in `learning/`).

Kept for reference and because its attack catalogue, guardrails and verdict
logic were ported into `blueprint/security/` and `blueprint/attacks/`.

Run it from the repo root with the `legacy.` prefix, e.g.
`python -m legacy.patterns.p04_dual_llm.demo`.
