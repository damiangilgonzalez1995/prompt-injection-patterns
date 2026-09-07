# learning/

Six self-contained notebooks, one per pattern.

**`01`, `02` and `03` are the rewritten ones.** They share a single running example —
a furniture-shop support agent whose order records contain a note planted by a
third party — and they run against a **real model** (`openai:gpt-3.5-turbo` via
`langchain.agents.create_agent`), so the attack lands or fails on its own merits
rather than by script. Each shows the same tools on both sides: what changes is
the wiring, never the capability list.

Notebooks `04`–`06` are still the older generated versions (a stand-in "LLM"
that is a plain function, LangGraph graphs, `PIP_MODE=mock`) and are next in
line for the same treatment.

## Run

```bash
pip install -e ".[learning]"
export OPENAI_API_KEY=...      # required by 01, 02 and 03
jupyter lab learning/
```

`04`–`06` still run offline by default (`PIP_MODE=mock`); set `PIP_MODE=live`
in their setup cell to use a real model.

| Notebook | Pattern | Guardian | State |
|---|---|---|---|
| `01_action_selector.ipynb` | Action-Selector | the model never reads tool output | rewritten, live model |
| `02_plan_then_execute.ipynb` | Plan-Then-Execute | the plan is frozen before any data is read | rewritten, live model |
| `03_llm_map_reduce.ipynb` | LLM Map-Reduce | one isolated model per document + an output schema | rewritten, live model |
| `04_dual_llm.ipynb` | Dual LLM | privileged LLM + symbolic memory | rewritten, live model |
| `05_code_then_execute.ipynb` | Code-Then-Execute | execution sandbox | generated |
| `06_context_minimization.ipynb` | Context-Minimization | context pruner | generated |

Read them in order: `02` opens where `01` ends. Action-Selector lets the model
pick a **set of independent actions** up front — several is fine, but none of
them can use what another returned. Plan-Then-Execute buys exactly that: an
ordered sequence where step 2's argument can be **bound** to a field of step 1's
result, with the whole sequence frozen before any data is read. Neither pattern
lets an LLM read a tool result. `03` is the first one that does — and it pays
for it by isolating each document in its own call and forcing every worker's
output through a narrow schema, so a poisoned document buys only its own fields.
