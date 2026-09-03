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


def test_a_program_that_raises_fails_closed_with_the_error():
    result = run_sandboxed("raise ValueError('boom')")
    assert not result.ok and "ValueError" in result.error


def test_posix_resource_limits_are_applied_where_available():
    """On Windows only the timeout applies - assert that honestly, per platform."""
    import os

    from patterns.p05_code_then_execute.sandbox import _PREAMBLE

    assert "RLIMIT_CPU" in _PREAMBLE and "RLIMIT_AS" in _PREAMBLE
    if os.name == "nt":
        pytest.skip("rlimits are POSIX-only; documented in sandbox.py")
    result = run_sandboxed("x = [0] * (400 * 1024 * 1024)")
    assert not result.ok, "address-space limit did not stop a 400MB allocation"
