"""Run every pattern graph against every payload, secure and insecure.

    PIP_MODE=mock python -m blueprint.benchmark        # offline, deterministic
    python -m blueprint.benchmark                      # against the real model
"""

from __future__ import annotations

import os

from blueprint.attacks.payloads import PAYLOADS
from blueprint.graph.builder import run, verdict_for
from blueprint.llm.provider import default_model
from blueprint.patterns import REGISTRY


def main() -> int:
    model = default_model()
    print(f"\n  model: {model.model_id} ({model.provider})\n")
    print(f"  {'pattern':<22} {'secure':>7} {'insecure':>9}")
    total = len(PAYLOADS)
    for _key, (mod, label, _guard) in REGISTRY.items():
        secure = mod.build_secure(model)
        insecure = mod.build_insecure(model)
        s = sum(not verdict_for(p, run(secure, p))[0] for p in PAYLOADS)
        i = sum(not verdict_for(p, run(insecure, p))[0] for p in PAYLOADS)
        print(f"  {label:<22} {s:>4}/{total} {i:>6}/{total}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
