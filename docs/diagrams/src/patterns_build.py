"""Generate one poster per pattern (docs/diagrams/patterns/NN-*.png).

Each card is a self-contained HTML file rendered to PNG with headless Chrome
(see docs/diagrams/README.md). Run this to (re)write the HTML files, then the
bash loop in the README recipe renders them.
"""
from __future__ import annotations
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE  # html files land next to this script, in patterns_html/
(HERE / "patterns_html").mkdir(exist_ok=True)

# color, accent bg, accent line per pattern
COLORS = {
    "blue":   ("#2563eb", "#eff6ff", "#bfdbfe"),
    "amber":  ("#b45309", "#fffbeb", "#fde68a"),
    "green":  ("#059669", "#ecfdf5", "#a7f3d0"),
    "purple": ("#7c3aed", "#f5f3ff", "#ddd6fe"),
    "red":    ("#dc2626", "#fef2f2", "#fecaca"),
    "slate":  ("#475569", "#f8fafc", "#e2e8f0"),
}

SPECS = [
    dict(num="01", name="Action-Selector", color="blue", stage="Decide",
         guardian="fixed action list",
         icon='<path d="M4 6h16v12H4z"/><path d="M8 10h8M8 14h5"/>',
         threat="Free tool-calling lets pasted text become a tool call.",
         insecure="model output IS the control flow &rarr; calls issue_refund",
         flow=["user intent", "router", "closed enum", "safe action"],
         protects="A bad action <b>cannot be expressed</b> — it is not in the enum.",
         limit="The content of an allowed action can still be influenced.",
         score="6/6", file="action_selector.py"),
    dict(num="02", name="Plan-Then-Execute", color="amber", stage="Plan",
         guardian="frozen plan",
         icon='<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9l6 6M15 9l-6 6"/>',
         threat="A ReAct loop lets each tool result rewrite the next step.",
         insecure="poisoned calendar event &rarr; mail to attacker@evil.com",
         flow=["plan (trusted)", "freeze steps", "execute", "send to boss"],
         protects="Recipient &amp; steps <b>cannot be rewritten</b> at runtime.",
         limit="The body of a planned step can still be coloured (P6).",
         score="5/6", file="plan_then_execute.py"),
    dict(num="03", name="LLM Map-Reduce", color="green", stage="Perceive",
         guardian="map-output sanitizer",
         icon='<rect x="3" y="4" width="7" height="7" rx="1"/><rect x="14" y="4" width="7" height="7" rx="1"/><rect x="8.5" y="14" width="7" height="6" rx="1"/>',
         threat="One poisoned doc in a shared prompt owns all of them.",
         insecure="one poisoned review steers the whole recommendation",
         flow=["isolated worker/doc", "typed facts", "drop invalid", "reduce"],
         protects="Hijack is confined to <b>one worker</b>; reduce takes typed fields only.",
         limit="A payload that fits the schema still casts one vote.",
         score="6/6", file="llm_map_reduce.py"),
    dict(num="04", name="Dual LLM", color="purple", stage="Perceive",
         guardian="privileged + symbolic memory",
         icon='<rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
         threat="If the deciding model reads untrusted text, it is already lost.",
         insecure="one model reads all CVs and decides &rarr; hijacked",
         flow=["quarantine reads", "typed handles", "privileged decides", "resolve"],
         protects="The privileged model <b>never sees</b> untrusted text.",
         limit="The quarantine model is compromised by design (harmless).",
         score="6/6", file="dual_llm.py"),
    dict(num="05", name="Code-Then-Execute", color="red", stage="Act",
         guardian="execution sandbox",
         icon='<path d="M8 9l-4 3 4 3M16 9l4 3-4 3M13 5l-2 14"/>',
         threat="exec() of model code over poisoned data runs anything.",
         insecure="poisoned field &rarr; import os; os.system(...) in-process",
         flow=["codegen", "AST allowlist", "sandbox run", "stdout"],
         protects="Un-allowed imports/calls are <b>refused before running</b>.",
         limit="A subprocess is not real isolation — use a container.",
         score="6/6", file="code_then_execute.py"),
    dict(num="06", name="Context-Minimization", color="slate", stage="Remember",
         guardian="context pruner",
         icon='<path d="M3 6h18M8 6l1-2h6l1 2M6 6l1 14h10l1-14"/><path d="M10 11v5M14 11v5"/>',
         threat="Append-only history lets an injection fire every later turn.",
         insecure="turn-1 payload still in context at turn 2 &rarr; re-fires",
         flow=["retrieve", "answer turn 1", "prune chunk", "clean turn 2"],
         protects="An injection <b>lives one turn</b>, not the whole session.",
         limit="The turn where the chunk is present is not protected.",
         score="6/6", file="context_minimization.py"),
]

CARD = """<!doctype html><html><head><meta charset="utf-8"><style>
:root{{--ink:#1f2937;--muted:#6b7280;--line:#e5e7eb;--red:#dc2626;--green:#059669}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#fff}}
body{{font-family:"Segoe UI",system-ui,-apple-system,sans-serif;color:var(--ink);width:1040px;padding:26px}}
.card{{border:1px solid var(--line);border-top:5px solid {accent};border-radius:16px;padding:24px 26px 22px;background:#fff}}
.top{{display:flex;align-items:center;gap:14px;margin-bottom:12px}}
.badge{{width:44px;height:44px;border-radius:11px;background:{accent};color:#fff;display:flex;align-items:center;justify-content:center;font-size:19px;font-weight:700;flex:0 0 44px}}
.tt h2{{font-size:23px;letter-spacing:-.3px}}
.pill{{display:inline-block;margin-top:3px;font-size:11.5px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;color:{accent};background:{accbg};border:1px solid {accln};border-radius:20px;padding:2px 10px}}
.stage{{margin-left:auto;font-size:12px;color:var(--muted);background:#f8fafc;border:1px solid var(--line);border-radius:20px;padding:3px 12px}}
.stage b{{color:var(--ink)}}
.ic{{width:26px;height:26px;color:{accent}}}
.threat{{font-size:14.5px;color:var(--muted);line-height:1.45;margin:2px 0 16px}}
.rowlab{{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#94a3b8;margin:0 0 7px}}
.bad,.good{{display:flex;align-items:center;gap:10px;font-size:13.5px;border-radius:10px;padding:10px 13px;margin-bottom:9px}}
.bad{{background:#fef2f2;border:1px solid #fecaca;color:#7f1d1d}}
.good{{background:#ecfdf5;border:1px solid #a7f3d0;color:#065f46}}
.tag{{font-size:11px;font-weight:700;border-radius:6px;padding:2px 7px;flex:0 0 auto}}
.tagbad{{background:var(--red);color:#fff}} .taggood{{background:var(--green);color:#fff}}
.flow{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:2px}}
.chip{{font-size:12px;background:{accbg};border:1px solid {accln};color:{accent};border-radius:8px;padding:4px 9px;font-weight:600}}
.sep{{color:#cbd5e1;font-size:13px}}
.pn{{display:grid;grid-template-columns:22px 1fr;gap:9px;margin-top:14px}}
.pn .m{{font-size:13.5px;line-height:1.4}}
.pn .ok{{color:var(--green);font-weight:800;font-size:15px}}
.pn .no{{color:var(--red);font-weight:800;font-size:15px}}
.pn .m b{{color:var(--ink)}} .pn .m span{{color:var(--muted)}}
.foot{{display:flex;justify-content:space-between;align-items:center;margin-top:18px;border-top:1px solid var(--line);padding-top:12px;font-size:12.5px;color:var(--muted)}}
.foot .sc b{{color:var(--green)}} .foot code{{font-family:"Cascadia Code",Consolas,monospace;color:{accent}}}
</style></head><body>
<div class="card">
  <div class="top">
    <span class="badge">{num}</span>
    <div class="tt"><h2>{name}</h2><span class="pill">{guardian}</span></div>
    <span class="stage">guards <b>{stage}</b></span>
  </div>
  <div class="threat"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="vertical-align:-6px;margin-right:6px">{icon}</svg>{threat}</div>

  <div class="rowlab">The mechanism</div>
  <div class="bad"><span class="tag tagbad">INSECURE</span>{insecure}</div>
  <div class="good"><span class="tag taggood">SECURE</span>
    <div class="flow">{flow}</div>
  </div>

  <div class="pn"><span class="ok">&#10003;</span><div class="m"><b>Protects.</b> <span>{protects}</span></div></div>
  <div class="pn"><span class="no">&times;</span><div class="m"><b>Limit.</b> <span>{limit}</span></div></div>

  <div class="foot">
    <div class="sc">secure <b>{score}</b> &nbsp;·&nbsp; insecure baseline 0/6 (mock)</div>
    <div><code>blueprint/patterns/{file}</code></div>
  </div>
</div>
</body></html>"""


def main() -> None:
    for s in SPECS:
        acc, accbg, accln = COLORS[s["color"]]
        flow = ' <span class="sep">&rsaquo;</span> '.join(f'<span class="chip">{c}</span>' for c in s["flow"])
        html = CARD.format(accent=acc, accbg=accbg, accln=accln, num=s["num"], name=s["name"],
                           guardian=s["guardian"], stage=s["stage"], icon=s["icon"], threat=s["threat"],
                           insecure=s["insecure"], flow=flow, protects=s["protects"], limit=s["limit"],
                           score=s["score"], file=s["file"])
        p = HERE / "patterns_html" / f"{s['num']}.html"
        p.write_text(html, encoding="utf-8")
        print("wrote", p.name)


if __name__ == "__main__":
    main()
