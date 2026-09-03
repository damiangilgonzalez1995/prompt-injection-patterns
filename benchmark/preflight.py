"""One tiny call to confirm the live setup works before spending on the suite.

    python -m benchmark.preflight

Reports the resolved mode, provider, model and key status, then - in live mode -
makes a single cheap request and prints what came back.
"""

from __future__ import annotations

import os

from core.llm import Prompt, constant, get_llm


def main() -> int:
    mode = os.getenv("TEST_MODE", "mock").lower()
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    key_var = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
    key = os.getenv(key_var, "")
    model = os.getenv(
        "ANTHROPIC_MODEL" if provider == "anthropic" else "OPENAI_MODEL", "gpt-4o-mini"
    )

    if key and not key.startswith(("sk-", "PASTE")):
        key_status = "set (unusual prefix)"
    elif key.startswith("PASTE"):
        key_status = "PLACEHOLDER - edit .env"
    elif key:
        key_status = f"set ({key[:7]}...{key[-4:]})"
    else:
        key_status = "MISSING"

    print(f"\n  TEST_MODE     {mode}")
    print(f"  LLM_PROVIDER  {provider}")
    print(f"  model         {model}")
    print(f"  {key_var:<13} {key_status}\n")

    if mode != "live":
        print("  Mock mode: no key needed, nothing to check.")
        print("  Set TEST_MODE=live in .env to test a real model.\n")
        return 0

    if key_status in {"MISSING", "PLACEHOLDER - edit .env"}:
        print(f"  Cannot run live: {key_var} is not a real key.\n")
        return 1

    print("  Making one test call...")
    try:
        llm = get_llm(constant("unused in live mode"), name="preflight")
        reply = llm.invoke(
            Prompt(system="Reply with exactly one word.", user="Say the word: ready")
        )
    except Exception as exc:  # noqa: BLE001 - the point is to show the raw failure
        print(f"  FAILED: {type(exc).__name__}: {exc}\n")
        return 1

    print(f"  model replied: {reply.strip()!r}")
    print(f"  adapter: {type(llm).__name__}, calls recorded: {len(llm.calls)}")
    print("\n  Live mode works. Safe to run the suite.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
