# syntax=docker/dockerfile:1
# Build context: repository root. The service needs a container engine for its sandboxes:
#   docker run -v /var/run/docker.sock:/var/run/docker.sock --group-add <socket gid> ... (see README.md)
#   docker build -f services/handler-runtime/Dockerfile -t jane-handler-runtime .
ARG PYTHON_IMAGE=python:3.12-slim
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.13

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /src
# Only what this service needs: workspace root, lock, shared libs and the service itself.
COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY services/handler-runtime/ services/handler-runtime/
RUN uv sync --frozen --no-dev --no-editable --package jane-handler-runtime

FROM ${PYTHON_IMAGE}
RUN useradd --system --uid 10001 --no-create-home jane
COPY --from=build /app/.venv /app/.venv
# JSON Schemas / OpenAPI of the contracts: results and requests are validated against them.
COPY contracts/schemas /app/contracts/schemas
COPY contracts/openapi /app/contracts/openapi
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    JANE_HANDLER_RUNTIME_HOST=0.0.0.0 \
    JANE_HANDLER_RUNTIME_PORT=8000 \
    JANE_HANDLER_RUNTIME_CONTRACTS_DIR=/app/contracts
USER jane
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.environ['JANE_HANDLER_RUNTIME_PORT']}/v1/health\", timeout=2)"]
CMD ["python", "-m", "jane_handler_runtime"]
