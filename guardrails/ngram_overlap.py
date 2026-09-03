"""System-prompt leak detection by n-gram overlap.

Why n-grams and not a regex: an attacker who asks for the system prompt rarely
gets it back verbatim in one line. They get it paraphrased, split, translated,
or dripped out one clause at a time (reverse prompt engineering). What survives
all of that is *word sequence*. If 8-10 consecutive words of your system prompt
show up in a response, you are leaking, whatever the wrapper text says.

Pure logic, no model, no network - which is why this is the piece with the
tightest unit tests in the repo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_WORD = re.compile(r"[a-z0-9']+")


def normalize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def ngrams(text: str, n: int = 8) -> set[tuple[str, ...]]:
    words = normalize(text)
    if len(words) < n:
        return set()
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


@dataclass
class LeakReport:
    leaked: bool
    matches: list[str]
    n: int

    def __bool__(self) -> bool:
        return self.leaked


def analyze(system_prompt: str, response: str, n: int = 8, threshold: int = 1) -> LeakReport:
    shared = ngrams(system_prompt, n) & ngrams(response, n)
    matches = sorted(" ".join(g) for g in shared)
    return LeakReport(leaked=len(matches) >= threshold, matches=matches, n=n)


def detect_leak(system_prompt: str, response: str, n: int = 8, threshold: int = 1) -> bool:
    """True when `response` reproduces `n` consecutive words of the system prompt."""
    return analyze(system_prompt, response, n=n, threshold=threshold).leaked
