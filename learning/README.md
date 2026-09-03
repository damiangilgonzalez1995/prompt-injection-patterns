# learning/

Six self-contained notebooks, one per pattern. Each one:

1. states the threat and the guardian idea (with a diagram),
2. builds the pattern as a **LangGraph** graph,
3. shows the real source from `blueprint/`,
4. runs a live prompt-injection attack against the insecure and the secure
   version — on the same model, so the difference is architecture, not prompting,
5. prints all six payloads side by side.

## Run

```bash
pip install -e ".[learning]"
jupyter lab learning/
```

They run offline by default (`PIP_MODE=mock`). Set `PIP_MODE=live` in the setup
cell to run against a real model.

| Notebook | Pattern | Guardian |
|---|---|---|
| `01_action_selector.ipynb` | Action-Selector | fixed action list |
| `02_plan_then_execute.ipynb` | Plan-Then-Execute | frozen plan |
| `03_llm_map_reduce.ipynb` | LLM Map-Reduce | map-output sanitizer |
| `04_dual_llm.ipynb` | Dual LLM | privileged LLM + symbolic memory |
| `05_code_then_execute.ipynb` | Code-Then-Execute | execution sandbox |
| `06_context_minimization.ipynb` | Context-Minimization | context pruner |

`_build_notebooks.py` regenerates all six from a single spec.
