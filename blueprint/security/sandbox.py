"""Two layers between generated code and your machine.

Layer 1 - static: an AST walk that *allowlists*. Anything not explicitly
permitted is rejected before execution. Denylists lose this game; there is
always one more dunder.

Layer 2 - dynamic: a separate interpreter process with a hard wall-clock
timeout, an empty environment, and (on POSIX) CPU and address-space rlimits, so
that a program which passes the AST check still cannot burn the box.

HONEST LIMITS - read before shipping this:
  * A subprocess is not a security boundary against a determined attacker. It
    shares the kernel, the filesystem and the network namespace.
  * `resource` rlimits are POSIX-only; on Windows only the timeout applies.
  * For production, run this inside an ephemeral container with no network
    (`--network=none`), a read-only rootfs and a seccomp profile - or gVisor /
    Firecracker. TODO tracked in the pattern README.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field

ALLOWED_IMPORTS = {"math", "statistics", "json"}

ALLOWED_CALLS = {
    "print", "len", "sum", "min", "max", "sorted", "round", "abs",
    "range", "enumerate", "zip", "list", "dict", "set", "tuple",
    "str", "int", "float", "bool", "any", "all", "items", "keys", "values",
    "append", "get", "join", "format", "lower", "upper", "strip", "split",
}

FORBIDDEN_NAMES = {
    "eval", "exec", "compile", "open", "input", "__import__", "globals",
    "locals", "vars", "getattr", "setattr", "delattr", "exit", "quit",
    "breakpoint", "memoryview", "os", "sys", "socket", "subprocess",
    "requests", "urllib", "shutil", "pickle", "importlib", "ctypes",
}


class SandboxViolation(Exception):
    """Raised when generated code asks for something outside the allowlist."""


@dataclass
class ExecResult:
    ok: bool
    stdout: str = ""
    error: str = ""
    violations: list[str] = field(default_factory=list)


def check_ast(source: str) -> list[str]:
    """Return every reason this code must not run. Empty list means clean."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"syntax_error: {exc.msg}"]

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in ALLOWED_IMPORTS:
                    violations.append(f"import not allowed: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in ALLOWED_IMPORTS:
                violations.append(f"import not allowed: {node.module}")
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                violations.append(f"dunder attribute access: {node.attr}")
            elif node.attr not in ALLOWED_CALLS and not isinstance(node.ctx, ast.Store):
                violations.append(f"attribute not allowed: {node.attr}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            violations.append(f"forbidden name: {node.id}")
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            violations.append("global/nonlocal not allowed")
    return violations


_PREAMBLE = """
import resource, sys
try:
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
except Exception:
    pass
"""


def run_sandboxed(source: str, timeout: float = 5.0) -> ExecResult:
    """Static check, then a throwaway process. Fails closed at both stages."""
    violations = check_ast(source)
    if violations:
        return ExecResult(ok=False, error="blocked by AST allowlist", violations=violations)

    preamble = _PREAMBLE if os.name != "nt" else ""
    with tempfile.TemporaryDirectory() as workdir:
        script = os.path.join(workdir, "program.py")
        with open(script, "w", encoding="utf-8") as handle:
            handle.write(preamble + source)
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-S", script],
                capture_output=True, text=True, timeout=timeout,
                cwd=workdir, env={"PATH": ""},
            )
        except subprocess.TimeoutExpired:
            return ExecResult(ok=False, error=f"timeout after {timeout}s")

    if completed.returncode != 0:
        return ExecResult(ok=False, error=completed.stderr.strip()[:500])
    return ExecResult(ok=True, stdout=completed.stdout.strip())
