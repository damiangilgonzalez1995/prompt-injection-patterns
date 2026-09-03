"""Shared side-by-side demo renderer, so every pattern looks the same."""

from __future__ import annotations

import os
import sys
from types import ModuleType

from attacks.payloads import PAYLOADS, Payload
from core.verdict import is_compromised

try:  # Windows consoles default to cp1252 and choke on box-drawing chars
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

_COLOR = sys.stdout.isatty() and os.getenv("NO_COLOR") is None


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


RED, GREEN, DIM, BOLD, CYAN = "31", "32", "2", "1", "36"


def _short(text: str, width: int = 88) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


def side_by_side(title: str, insecure: ModuleType, secure: ModuleType, payloads=PAYLOADS) -> int:
    print()
    print(_c(f"  {title}", BOLD))
    print(_c("  " + "─" * 76, DIM))

    blocked = 0
    for payload in payloads:
        run_i = insecure.run_payload(payload)
        run_s = secure.run_payload(payload)
        bad_i, why_i = is_compromised(payload, run_i)
        bad_s, why_s = is_compromised(payload, run_s)
        blocked += not bad_s

        print(f"\n  {_c(payload.id, CYAN)}  {_c('(' + payload.target + ')', DIM)}")
        print(f"    {_c('insecure', DIM)}  {_c('COMPROMISED' if bad_i else 'safe', RED if bad_i else GREEN)}"
              f"  {_c(why_i, DIM)}")
        print(f"              {_c(_short(run_i.answer), DIM)}")
        print(f"    {_c('secure  ', DIM)}  {_c('COMPROMISED' if bad_s else 'BLOCKED', RED if bad_s else GREEN)}"
              f"  {_c(why_s, DIM)}")
        print(f"              {_c(_short(run_s.answer), DIM)}")

    total = len(payloads)
    print(_c("\n  " + "─" * 76, DIM))
    print(f"  secure implementation blocked {_c(f'{blocked}/{total}', BOLD)} attacks\n")
    return blocked


def demo_for(title: str, module_path: str) -> None:
    """Entry point used by every patterns/*/demo.py."""
    import importlib

    insecure = importlib.import_module(f"{module_path}.insecure_agent")
    secure = importlib.import_module(f"{module_path}.secure_agent")
    side_by_side(title, insecure, secure)
