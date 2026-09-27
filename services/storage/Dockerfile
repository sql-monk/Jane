# syntax=docker/dockerfile:1
# Build context: repository root.
#   docker build -f services/storage/Dockerfile -t jane-storage .
# The image contains the storage core and every adapter under services/storage/adapters/*
# (distribution name jane-storage-<directory>); a new adapter directory needs no change here.
ARG PYTHON_IMAGE=python:3.12-slim
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.13

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /src
COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY contracts/python/ contracts/python/
COPY services/storage/ services/storage/
RUN set -eu; \
    args="--package jane-storage"; \
    for dir in services/storage/adapters/*/; do \
      [ -f "${dir}pyproject.toml" ] && args="$args --package jane-storage-$(basename "$dir")"; \
    done; \
    echo "uv sync $args"; \
    uv sync --frozen --no-dev --no-editable $args

FROM ${PYTHON_IMAGE}
RUN useradd --system --uid 10001 --no-create-home jane \
    && mkdir -p /var/lib/jane/storage && chown jane /var/lib/jane/storage
COPY --from=build /app/.venv /app/.venv
# Contracts are used to validate HandlerInvocation and Connection documents at runtime.
COPY contracts/openapi/ /app/contracts/openapi/
COPY contracts/schemas/ /app/contracts/schemas/
COPY contracts/examples/ /app/contracts/examples/
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    JANE_CONTRACTS_DIR=/app/contracts \
    JANE_STORAGE_HOST=0.0.0.0 \
    JANE_STORAGE_PORT=8000
USER jane
VOLUME ["/var/lib/jane/storage"]
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.environ['JANE_STORAGE_PORT']}/v1/health\", timeout=2)"]
CMD ["python", "-m", "jane_storage"]
