"""Entry point.

* ``python -m jane_orchestrator`` — API (+ worker threads unless ``JANE_ORCHESTRATOR_RUN_WORKERS=false``);
  host/port from ``JANE_ORCHESTRATOR_HOST/PORT``.
* ``python -m jane_orchestrator worker`` — workers only (``..._LIMITS__ENGINE__WORKERS`` threads), no HTTP;
  run as many processes as needed, they share the queue in PostgreSQL.
"""

from __future__ import annotations

import logging
import signal
import sys
import threading
from types import FrameType

from jane_kit.logs import configure_logging
from jane_kit.service import run

from .app import build_app
from .core import Core
from .engine import Engine, Worker
from .settings import Settings, resolve_service_limits


def run_workers(settings: Settings) -> None:
    configure_logging(settings.service_name, settings.log_level, settings.log_format, settings.instance_id)
    limits = resolve_service_limits(settings).limits
    core = Core(settings, limits)
    core.open()
    engine = Engine(core)
    count = max(1, limits.engine.workers)
    workers = [
        Worker(engine, f"{settings.instance_id}-w{i}", scheduler=settings.scheduler_enabled)
        for i in range(count)
    ]
    stop = threading.Event()

    def on_signal(signum: int, _frame: FrameType | None) -> None:
        logging.getLogger("jane.orchestrator").info("stopping workers", extra={"signal": signum})
        stop.set()

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)
    for w in workers:
        w.start()
    logging.getLogger("jane.orchestrator").info("workers started", extra={"count": count})
    while not stop.wait(1.0):
        pass
    for w in workers:
        w.stop()
    core.close()


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    settings = Settings()
    if args[:1] == ["worker"]:
        run_workers(settings)
        return
    run(build_app(settings), settings)


if __name__ == "__main__":
    main()
