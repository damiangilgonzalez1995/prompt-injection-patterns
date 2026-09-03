<div align="center">

# Prompt Injection Patterns

**Six architectural defences against prompt injection — as runnable LangGraph blueprints, and as notebooks that teach them one by one.**

*Based on [arXiv:2506.08837](https://arxiv.org/abs/2506.08837) · OWASP LLM01:2025*

[![tests](https://img.shields.io/badge/tests-40%20passing-2ea44f?style=flat-square)](tests)
[![python](https://img.shields.io/badge/python-3.11%2B-3776ab?style=flat-square&logo=python&logoColor=white)](pyproject.toml)
[![langgraph](https://img.shields.io/badge/built%20on-LangGraph-1c3c3c?style=flat-square)](blueprint)
[![offline](https://img.shields.io/badge/runs%20offline-no%20API%20key-8957e5?style=flat-square)](#zero-setup)
[![license](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)

</div>

---

Two ways in, one idea:

- **`learning/`** — six self-contained Jupyter notebooks, one per pattern. Each
  builds the pattern as a LangGraph graph, shows the real source, and runs a live
  prompt-injection attack against the insecure and the secure version. Start here.
- **`blueprint/`** — the production code the notebooks teach: a clean LangGraph
  project (`llm/`, `agents/`, `security/`, `graph/`, `patterns/`) you import into
  your own app.

The whole thing runs offline against a deterministic mock model, so `pytest` and
every notebook work with **no API key**. Point it at a real model when you want to.

## The one idea

> **The system prompt is not a security boundary. The graph state is where the defence lives.**

Inside a transformer your instructions and the attacker's text are the same kind
of token; at inference time nothing ranks yours above theirs. So the defence
cannot be a better prompt — it has to be **structure**: in LangGraph, nodes never
call each other, they read and write a shared state, and that state is exactly
where untrusted content must be stopped from leaking into a privileged decision.

Every pattern here is one discipline for that state: an action the model
**cannot express**, a plan it **cannot rewrite**, a context it **never sees**.

```mermaid
flowchart LR
    subgraph NAIVE["❌ Naive agent — one context, no boundary"]
        direction LR
        U1["🙂 User request<br/>trusted"] --> CTX{{"LLM context<br/>same tokens,<br/>same privilege"}}
        D1["📄 External data<br/>email · doc · review<br/><b>untrusted</b>"] --> CTX
        CTX --> ACT1["🔧 tools · 💸 money · 🔑 secrets"]
    end
    subgraph SAFE["✅ Pattern — a trust boundary in the state"]
        direction LR
        U2["🙂 User request<br/>trusted"] --> DEC{{"Privileged node<br/>decides · holds tools"}}
        D2["📄 External data<br/><b>untrusted</b>"] --> Q["🔒 Quarantine node<br/>no tools, no authority"]
        Q -->|"typed, validated<br/>fields only"| DEC
        DEC --> ACT2["🔧 tools · 💸 money · 🔑 secrets"]
        Q -. "raw text never<br/>crosses" .-> DEC
    end
    classDef trusted fill:#dcfce7,stroke:#16a34a,color:#052e16;
    classDef danger fill:#fee2e2,stroke:#dc2626,color:#450a0a;
    classDef ctx fill:#fef9c3,stroke:#ca8a04,color:#422006;
    classDef quar fill:#ede9fe,stroke:#7c3aed,color:#2e1065;
    class U1,U2 trusted
    class D1,D2 danger
    class CTX ctx
    class DEC ctx
    class Q quar
    class ACT1,ACT2 danger
```

## Zero setup

```bash
git clone https://github.com/damian/prompt-injection-patterns
cd prompt-injection-patterns
pip install -e ".[dev]"

PIP_MODE=mock python -m blueprint.benchmark      # the whole matrix, offline
PIP_MODE=mock pytest                             # 40 attack/defence tests
pip install -e ".[learning]" && jupyter lab learning/   # the notebooks
```

Against a real model (OpenAI by default):

```bash
pip install -e ".[llm]"
cp .env.example .env        # OPENAI_API_KEY=sk-...
python -m blueprint.benchmark            # PIP_MODE defaults to live
```

## The catalogue

Each pattern is a compiled LangGraph with a `build_secure()` and a
`build_insecure()`. Offline mock numbers (`python -m blueprint.benchmark`),
attacks **blocked** — higher is better:

| # | Pattern | Guardian | Secure | Insecure | Notebook |
|---|---|---|:---:|:---:|---|
| 01 | [Action-Selector](blueprint/patterns/action_selector.py) | fixed action list | **6/6** | 0/6 | [nb](learning/01_action_selector.ipynb) |
| 02 | [Plan-Then-Execute](blueprint/patterns/plan_then_execute.py) | frozen plan | **5/6** | 0/6 | [nb](learning/02_plan_then_execute.ipynb) |
| 03 | [LLM Map-Reduce](blueprint/patterns/llm_map_reduce.py) | map-output sanitizer | **6/6** | 0/6 | [nb](learning/03_llm_map_reduce.ipynb) |
| 04 | [Dual LLM](blueprint/patterns/dual_llm.py) | privileged LLM + symbolic memory | **6/6** | 0/6 | [nb](learning/04_dual_llm.ipynb) |
| 05 | [Code-Then-Execute](blueprint/patterns/code_then_execute.py) | execution sandbox | **6/6** | 2/6 | [nb](learning/05_code_then_execute.ipynb) |
| 06 | [Context-Minimization](blueprint/patterns/context_minimization.py) | context pruner | **6/6** | 0/6 | [nb](learning/06_context_minimization.ipynb) |

Both graphs of a pattern run on the **same** injectable mock model, which obeys
every injection it sees — so a secure graph that survives is proving its
architecture, not a friendlier model. Plan-Then-Execute scores 5/6 on purpose:
the content of an already-planned step can still be coloured (the paper's
documented residual), and a test pins that fact. Code-Then-Execute's insecure
baseline is 2/6 because two payloads are out of scope for a pure code agent.

### Six patterns, six places to put the boundary

Each pattern takes the same untrusted content and denies it a *different* kind of
power. Pick the one whose trade-off your task can pay.

```mermaid
flowchart TD
    X["💣 Untrusted content<br/>arrives inside data the agent must process"]
    X --> P1 & P2 & P3 & P4 & P5 & P6
    P1["<b>01 · Action-Selector</b><br/>🎯 the model emits a label<br/>from a closed enum<br/><i>cannot express a bad action</i>"]
    P2["<b>02 · Plan-Then-Execute</b><br/>🧊 plan frozen before<br/>untrusted data is read<br/><i>cannot rewrite the plan</i>"]
    P3["<b>03 · LLM Map-Reduce</b><br/>🧩 one isolated worker per item,<br/>typed reduce<br/><i>blast radius of one</i>"]
    P4["<b>04 · Dual LLM</b><br/>🚧 privileged model never<br/>sees untrusted text<br/><i>never enters the context</i>"]
    P5["<b>05 · Code-Then-Execute</b><br/>📜 program vetted by an<br/>AST allowlist + sandbox<br/><i>cannot run un-allowed code</i>"]
    P6["<b>06 · Context-Minimization</b><br/>🧹 untrusted content pruned<br/>from history after use<br/><i>injection lives one turn</i>"]

    classDef attack fill:#fee2e2,stroke:#dc2626,color:#450a0a;
    classDef pat fill:#f0fdf4,stroke:#16a34a,color:#052e16;
    class X attack
    class P1,P2,P3,P4,P5,P6 pat
```

And, quickly, which one to reach for:

```mermaid
flowchart TD
    S{"Can you enumerate<br/>every allowed action?"} -->|yes| A["01 Action-Selector"]
    S -->|no| M{"Many untrusted items<br/>of one shape?"}
    M -->|yes| B["03 LLM Map-Reduce"]
    M -->|no| C{"Is the task<br/>computational?"}
    C -->|yes| D["05 Code-Then-Execute"]
    C -->|no| E{"Does the agent hold<br/>consequential tools?"}
    E -->|yes| F["04 Dual LLM<br/>+ 02 Plan-Then-Execute"]
    E -->|no| G["06 Context-Minimization"]
    classDef q fill:#fef9c3,stroke:#ca8a04,color:#422006;
    classDef ans fill:#eff6ff,stroke:#2563eb,color:#1e3a8a;
    class S,M,C,E q
    class A,B,D,F,G ans
```

## How the blueprint is laid out

```mermaid
flowchart TB
    subgraph BP["🏗️ blueprint/ — production LangGraph code"]
        direction TB
        LLM["🧠 <b>llm/</b><br/>LLMModel enum · provider factory<br/>+ injectable mock model"]
        AG["🎭 <b>agents/</b><br/>BaseAgent · AgentType roles<br/>typed channels"]
        SEC["🛡️ <b>security/</b><br/>ngram leak · classifier · output filter<br/>sandbox · symbolic memory · verdict"]
        GR["🔗 <b>graph/</b><br/>state.py = trust model<br/>builder.py"]
        PAT["📐 <b>patterns/</b><br/>6 compiled LangGraphs<br/>build_secure() / build_insecure()"]
        ATK["💣 <b>attacks/</b><br/>6 indirect payloads"]
    end
    LEARN["📓 <b>learning/</b><br/>6 runnable notebooks"]
    TESTS["✅ <b>tests/</b><br/>40 attack/defence tests"]
    BENCH["📊 <b>benchmark.py</b><br/>every pattern × every payload"]

    LLM --> AG --> PAT
    SEC --> PAT
    GR --> PAT
    ATK --> PAT
    PAT --> BENCH
    PAT --> LEARN
    PAT --> TESTS
    ATK --> TESTS

    classDef layer fill:#eff6ff,stroke:#2563eb,color:#1e3a8a;
    classDef sec fill:#ede9fe,stroke:#7c3aed,color:#2e1065;
    classDef out fill:#f0fdf4,stroke:#16a34a,color:#052e16;
    class LLM,AG,GR,PAT,ATK layer
    class SEC sec
    class LEARN,TESTS,BENCH out
```

The trust model lives in [`blueprint/graph/state.py`](blueprint/graph/state.py):
every state field is labelled **trusted**, **quarantined**, or **audit**, and the
rule never changes — a node that holds tools or writes the answer reads trusted
and typed fields only; a node that reads quarantined text holds no authority.

### Security through state synchronisation

The clearest example is Dual LLM. Two agents share only the graph state:

```mermaid
flowchart TD
  CV[CV poisoned] --> SM[[SymbolicMemory in state<br/>DOC_3 to raw text]]
  CV --> Q[quarantine agent<br/>no tools, no authority]
  Q --> F{{CandidateFacts<br/>typed, validated}}
  F --> PR[privileged agent<br/>reads handles + facts only]
  PR --> DEC[decision]
  SM -. never crosses into .-> PR
```

The quarantine node writes only typed `CandidateFacts` into the state; the
privileged node reads only those. The raw CV text sits in `SymbolicMemory` behind
an opaque handle, resolved to a real value only when a tool call runs — never back
into the privileged prompt. The two agents "synchronise" through the state, built
so untrusted text cannot travel across it. That is the whole pattern.

## Using it in your project

```python
from blueprint.patterns import dual_llm
from blueprint.llm.models import LLMModel

graph = dual_llm.build_secure(LLMModel.GPT_4O_MINI)   # a compiled LangGraph
final = graph.invoke({"untrusted": some_document})
print(final["answer"])
```

Swap the pattern's fake tools for your real ones, keep the state's trust labels,
and the guarantee travels with it. Patterns compose: Plan-Then-Execute for control
flow, Dual LLM for the steps that read hostile content, Context-Minimization across
the conversation, the `security/` layer on both ends.

## Docs

- [`docs/threat-model.md`](docs/threat-model.md) — why the vulnerability is
  architectural, the attack taxonomy, defence in depth. Start here if injection is
  new to you.
- [`docs/paper-summary.md`](docs/paper-summary.md) — the paper distilled.

## Limitations

1. **No pattern gives an absolute guarantee for a general-purpose agent** — the
   paper's own conclusion. Guarantees come from narrowing the task.
2. **The guardrails are probabilistic**; the architecture is what holds.
3. **The sandbox is not an isolation boundary** — use a container, gVisor or
   Firecracker for anything real (see `blueprint/security/sandbox.py`).
4. **The benchmark is a teaching instrument, not a certification.** Real
   adversaries do not draw from a list of six.

## References

- Beurer-Kellner et al. (2025), *Design Patterns for Securing LLM Agents against
  Prompt Injections* — [arXiv:2506.08837](https://arxiv.org/abs/2506.08837)
- OWASP GenAI Security Project — **LLM01:2025 Prompt Injection**
- Simon Willison — [the dual-LLM pattern and the prompt injection archive](https://simonwillison.net/tags/prompt-injection/)

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship the patterns.
