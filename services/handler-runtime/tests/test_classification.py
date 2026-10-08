"""How a finished sandbox run is classified (``Executor.interpret``), without a container engine.

The sandbox outcome is the raw fact a backend reports (exit code, engine OOM flag, output); these tests feed
the executor the outcomes seen on a real engine, e.g. CI 37850701212 (``limits``, L6): the cgroup OOM killer
stopped the runner, the container exited with ``137``, ``State.OOMKilled`` was not set and stdout was empty.
"""

from __future__ import annotations

from typing import Any

import pytest

from jane_handler_runtime import sandbox
from jane_handler_runtime.docker_sandbox import DockerSandbox
from jane_handler_runtime.executor import Executor, PreparedInvocation, now_rfc3339
from jane_handler_runtime.runtime import build_runtime
from jane_handler_runtime.sandbox import SandboxBackend, SandboxOutcome, SubprocessSandbox
from jane_handler_runtime.schemas import ContractSchemas, find_contracts_dir
from jane_handler_runtime.settings import Settings

SCHEMAS = ContractSchemas(find_contracts_dir(None))
MEMORY_MB = 64


async def prepared(
    settings: Settings, backend: SandboxBackend, h: Any
) -> tuple[Executor, PreparedInvocation]:
    executor = build_runtime(settings, backend=backend).executor
    body = h.invocation(
        h.probe,
        h.product_material(),
        params={"mode": "memory", "mb": 512},
        limits={"sandbox": {"memory_mb": MEMORY_MB}},
    )
    return executor, await executor.prepare(body)


def outcome(exit_code: int | None, **kw: Any) -> SandboxOutcome:
    return SandboxOutcome(exit_code=exit_code, stdout=b"", stderr=b"", duration_ms=420, **kw)


def classify(executor: Executor, prep: PreparedInvocation, result: SandboxOutcome) -> dict[str, Any]:
    interpreted = executor.interpret(prep, result, now_rfc3339())
    SCHEMAS.check("handler-result.schema.json", interpreted)
    return interpreted


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (137, True),
        (-9, True),
        (0, False),
        (1, False),
        (124, False),
        (143, False),
        (-15, False),
        (None, False),
    ],
)
def test_killed_by_sigkill(code: int | None, expected: bool) -> None:
    assert sandbox.killed_by_sigkill(code) is expected


async def test_sigkill_under_memory_limit_without_oom_flag_is_resource_exceeded(
    subprocess_settings: Settings, h: Any
) -> None:
    """The L6 race: exit 137, ``OOMKilled`` not (yet) set, empty runner output."""
    executor, prep = await prepared(subprocess_settings, DockerSandbox(), h)
    result = classify(executor, prep, outcome(137, oom_killed=False, backend="docker"))
    assert result["status"] == "failed"
    assert result["failure"]["kind"] == "resource_exceeded", result["failure"]
    assert result["failure"]["details"] == {"memory_mb": MEMORY_MB, "exit_code": 137, "evidence": "sigkill"}


async def test_engine_oom_flag_is_resource_exceeded(subprocess_settings: Settings, h: Any) -> None:
    executor, prep = await prepared(subprocess_settings, DockerSandbox(), h)
    result = classify(executor, prep, outcome(137, oom_killed=True, backend="docker"))
    assert result["failure"]["kind"] == "resource_exceeded"
    assert result["failure"]["details"]["evidence"] == "oom_killed"


async def test_ordinary_nonzero_exit_stays_execution_error(subprocess_settings: Settings, h: Any) -> None:
    executor, prep = await prepared(subprocess_settings, DockerSandbox(), h)
    result = classify(executor, prep, outcome(1, backend="docker"))
    assert result["failure"]["kind"] == "execution_error"
    assert result["failure"]["details"]["exit_code"] == 1


async def test_sigkill_sent_by_the_runtime_is_not_a_memory_kill(
    subprocess_settings: Settings, h: Any
) -> None:
    executor, prep = await prepared(subprocess_settings, DockerSandbox(), h)
    cancelled = classify(executor, prep, outcome(137, killed_by_runtime=True, backend="docker"))
    assert cancelled["failure"]["kind"] == "execution_error"
    timed_out = classify(executor, prep, outcome(137, timed_out=True, backend="docker"))
    assert timed_out["failure"]["kind"] == "timeout"


@pytest.mark.parametrize("code", [137, -9])
async def test_subprocess_backend_has_no_memory_limit(
    code: int, subprocess_settings: Settings, h: Any
) -> None:
    """No kernel memory limit in the subprocess backend: a SIGKILL there is not attributed to ``memory_mb``."""
    executor, prep = await prepared(subprocess_settings, SubprocessSandbox(allowed=True), h)
    result = classify(executor, prep, outcome(code, backend="subprocess"))
    assert result["failure"]["kind"] == "execution_error"
