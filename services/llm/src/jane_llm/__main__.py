"""Entry point: ``python -m jane_llm`` (host/port from ``JANE_LLM_HOST/PORT``)."""

from __future__ import annotations

from jane_kit.service import run

from .app import build_app
from .settings import Settings


def main() -> None:
    settings = Settings()
    run(build_app(settings), settings)


if __name__ == "__main__":
    main()
