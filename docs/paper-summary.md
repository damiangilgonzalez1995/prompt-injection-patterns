# Paper summary: *Design Patterns for Securing LLM Agents against Prompt Injections*

Beurer-Kellner, Debenedetti, Dobler, Fischer, Fritz, Grosse, Hedler, Rehberger,
Sallou, Sivaramakrishnan, Vero, Zanchettin, Zhu et al. (2025).
[arXiv:2506.08837](https://arxiv.org/abs/2506.08837) - IBM, Google, ETH Zurich,
Microsoft, Invariant Labs.

---

## The thesis in one paragraph

You cannot train prompt injection away, and you cannot instruct it away. As long
as an agent (a) processes untrusted content and (b) can take consequential
actions, some input will eventually flip its behaviour. So stop trying to make
the model reliable and start constraining what it is *architecturally able to
do*. The paper's central principle:

> **Once an LLM agent has ingested untrusted input, it must be constrained so
> that it is impossible for that input to trigger any consequential action.**

Every pattern below is one way to satisfy that sentence, trading some generality
for a guarantee you can actually reason about.

## The trade-off the paper is honest about

There is no free lunch. Each pattern buys security by removing agency:

```
       utility  <------------------------------------------->  security
    free-form ReAct agent                         Action-Selector
    (any tool, any order)                    (one label from a fixed enum)
```

The paper's conclusion is deliberately unglamorous: **no pattern gives a
guarantee for a general-purpose agent.** Guarantees come from narrowing the
task. Pick the narrowest pattern your use case tolerates.

## The six patterns

| # | Pattern | Core constraint | Gives up |
|---|---|---|---|
| 1 | **Action-Selector** | The agent maps intent to one action from a closed list and cannot feed results back | Multi-step work, tool composition |
| 2 | **Plan-Then-Execute** | The plan is fixed before untrusted data is read; execution cannot add steps | Adapting the plan to what it finds |
| 3 | **LLM Map-Reduce** | Each untrusted item is handled by an isolated worker; only typed output aggregates | Reasoning across documents |
| 4 | **Dual LLM** | A privileged model never touches untrusted text; symbolic handles cross the gap | Rich context in the planner |
| 5 | **Code-Then-Execute** | The model writes a formal program once; a sandbox runs it | Mid-run judgement calls |
| 6 | **Context-Minimization** | Untrusted content is pruned from history after use | Long-range conversational memory |

## Additional design principles worth stealing

- **Least privilege for tools.** An agent that cannot issue a refund cannot be
  tricked into issuing one. Scope tools per-task, not per-application.
- **Structured channels beat prose.** Anywhere untrusted content crosses a
  boundary, force it through a schema. A validator is a boundary an injection
  cannot talk its way past.
- **Assume the model will be compromised.** Design so that a fully hijacked
  model still cannot reach anything consequential. Both the insecure *and*
  secure agents in this repo run on the same gullible model for exactly this
  reason.
- **Human-in-the-loop is a budget, not a blanket.** Confirm high-impact actions
  only; if you confirm everything, users click through everything.

## How this repository maps to the paper

| Paper | This repo |
|---|---|
| Pattern definitions | `patterns/pNN_*/secure_agent.py` (docstring = the pattern's rationale) |
| Case studies | Each pattern's demo scenario, kept close to the paper's |
| "No absolute guarantee" | Plan-Then-Execute deliberately scores 4/6 - see its README |
| Threat background | `docs/threat-model.md` |

## What the paper does not claim

- That these patterns stop *all* injections. They bound consequences.
- That they suit general-purpose assistants. They suit scoped agents.
- That guardrails/classifiers are sufficient. They are complementary, and
  probabilistic.
