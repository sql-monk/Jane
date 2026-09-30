# syntax=docker/dockerfile:1
# Build context: repository root.
#   docker build -f services/telegram-collector/Dockerfile -t jane-telegram-collector .
#   docker build -f services/telegram-collector/Dockerfile --build-arg EXTRAS="--extra telethon" -t jane-telegram-collector .
ARG PYTHON_IMAGE=python:3.12-slim
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.13

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS build
ARG EXTRAS=""
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /src
# Only what this service needs: workspace root, lock, shared libs, contracts (schemas for request and rules
# validation) and the service itself.
COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY contracts/ contracts/
COPY services/telegram-collector/ services/telegram-collector/
RUN uv sync --frozen --no-dev --no-editable --package jane-telegram-collector ${EXTRAS}

FROM ${PYTHON_IMAGE}
RUN useradd --system --uid 10001 --no-create-home jane \
 && mkdir -p /var/lib/jane-telegram-collector && chown jane /var/lib/jane-telegram-collector
COPY --from=build /app/.venv /app/.venv
COPY --from=build /src/contracts/openapi /app/contracts/openapi
COPY --from=build /src/contracts/schemas /app/contracts/schemas
COPY --from=build /src/contracts/examples /app/contracts/examples
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    JANE_TELEGRAM_COLLECTOR_HOST=0.0.0.0 \
    JANE_TELEGRAM_COLLECTOR_PORT=8102 \
    JANE_TELEGRAM_COLLECTOR_STATE_DIR=/var/lib/jane-telegram-collector \
    JANE_TELEGRAM_COLLECTOR_CONTRACTS_DIR=/app/contracts
USER jane
VOLUME ["/var/lib/jane-telegram-collector"]
EXPOSE 8102
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.environ['JANE_TELEGRAM_COLLECTOR_PORT']}/v1/health\", timeout=2)"]
CMD ["python", "-m", "jane_telegram_collector"]
