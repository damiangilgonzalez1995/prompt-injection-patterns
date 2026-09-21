# Accepted harness plan

Plan id: `c84daaf6e968038c8dfb2baee8954e6b143c530e010fb45093c610a2f80e1fe4`

| Kind | Component | Decision | Reason | Reevaluate when |
| --- | --- | --- | --- | --- |
| agent | base-agents | deferred | No substantial software implementation is planned. | substantial software implementation is introduced |
| capability | memory | selected | Local bounded project memory supports continuity without an external account. | — |
| guard | gitmoji-guard | deferred | No selected target and project policy justify this Claude-only commit guard. | Claude Code is selected and a governed software workflow adopts the convention |
| hook | code-hooks | deferred | Code-only gates would add unrelated behavior to this project. | a substantial software workflow is accepted |
| integration | context7 | excluded | External MCP connections require a separate, provider-specific consent flow and are outside this local harness plan. | — |
| route | harness-documents | selected | The accepted profile and plan are persisted under 02-DOCS/wiki/harness/. | — |
| skill | bro | selected | Included in the lightweight foundation for this software project. | — |
| skill | eli5 | selected | Included in the lightweight foundation for this software project. | — |
| skill | harness | selected | Included in the lightweight foundation for this software project. | — |
| skill | init | selected | Included in the lightweight foundation for this software project. | — |
| skill | orient | selected | Included in the lightweight foundation for this software project. | — |
| skill | python | selected | Detected python evidence inside the selected project root. | — |
| skill | show-me | selected | Included in the lightweight foundation for this software project. | — |
| skill | suggest | selected | Included in the lightweight foundation for this software project. | — |
| skill | unslop | selected | Included in the lightweight foundation for this software project. | — |
| workflow | sdd | deferred | The software scope is small, so specification overhead is not justified yet. | multiple related features; authentication or persistence; external integrations; cross-cutting changes |
