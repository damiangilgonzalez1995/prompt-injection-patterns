"""Last gate before text reaches a human.

Combines the n-gram leak detector with flat business rules (secrets, PII,
attacker-controlled addresses). Fails *closed*: when it trips, the caller gets
a safe refusal string, never the raw model output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from blueprint.security.ngram_overlap import analyze

SAFE_REFUSAL = (
    "I can't share that. I can help with your order, a return, or a product question."
)

SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "api_key": re.compile(r"\b(sk-[A-Za-z0-9_\-]{8,}|AKIA[0-9A-Z]{16})\b"),
    "internal_token": re.compile(r"\b[A-Z_]{4,}_TOKEN\s*=\s*\S+"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "untrusted_address": re.compile(
        r"\b\S+@(?:refund-desk|titan-clearance|evil)\.\w+\b", re.I
    ),
}


@dataclass
class FilterResult:
    safe: bool
    text: str
    reasons: list[str] = field(default_factory=list)


def filter_output(
    response: str,
    system_prompt: str = "",
    n: int = 8,
    extra_secrets: list[str] | None = None,
) -> FilterResult:
    reasons = [name for name, p in SECRET_PATTERNS.items() if p.search(response)]

    for secret in extra_secrets or []:
        if secret and secret in response:
            reasons.append("known_secret")

    if system_prompt:
        report = analyze(system_prompt, response, n=n)
        if report.leaked:
            reasons.append(f"system_prompt_ngram_overlap(n={n})")

    if reasons:
        return FilterResult(safe=False, text=SAFE_REFUSAL, reasons=reasons)
    return FilterResult(safe=True, text=response, reasons=[])
