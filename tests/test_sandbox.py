"""The sandbox is the one place where a bug means real code execution."""

import pytest

from patterns.p05_code_then_execute.sandbox import check_ast, run_sandboxed


@pytest.mark.parametrize(
    "source",
    [
        "import os",
        "import subprocess, sys",
        "from socket import socket",
        "__import__('os').system('ls')",
        "open('/etc/passwd').read()",
        "eval('1+1')",
        "exec('x=1')",
        "().__class__.__bases__",
        "getattr(object, 'mro')",
    ],
)
def test_dangerous_source_is_rejected_statically(source):
    assert check_ast(source), f"allowlist let this through: {source}"


def test_allowed_program_runs_and_returns_stdout():
    result = run_sandboxed("vals=[1,2,3]\nprint(sum(vals))")
    assert result.ok and result.stdout == "6"


def test_blocked_program_never_executes():
    result = run_sandboxed("import os\nos.system('echo pwned')")
    assert not result.ok and result.violations and "pwned" not in result.stdout


def test_syntax_error_is_a_violation_not_a_crash():
    assert any("syntax_error" in v for v in check_ast("def ("))


def test_runaway_loop_is_killed_by_the_timeout():
    result = run_sandboxed("while True:\n    pass", timeout=1.0)
    assert not result.ok and "timeout" in result.error
