"""Entry point: ``python -m jane_storage`` (host/port from ``JANE_STORAGE_HOST/PORT``)."""

from __future__ import annotations

from jane_kit.service import run

from .app import build_app
from .settings import Settings


def main() -> None:
    settings = Settings()
    run(build_app(settings), settings)


if __name__ == "__main__":
    main()
