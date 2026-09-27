"""Entry point: ``python -m jane_web_collector`` (host/port from ``JANE_WEB_COLLECTOR_HOST/PORT``)."""

from __future__ import annotations

from jane_kit.service import run

from .app import build_app
from .settings import Settings


def main() -> None:
    settings = Settings()
    run(build_app(settings), settings)


if __name__ == "__main__":
    main()
