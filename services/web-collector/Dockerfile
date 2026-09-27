# syntax=docker/dockerfile:1
# Build context: repository root.
#   docker build -f services/web-collector/Dockerfile -t jane-web-collector .
ARG PYTHON_IMAGE=python:3.12-slim
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.13

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /src
# Only what this service needs: workspace root, lock, shared libs, contracts (schemas for validation and
# the jane-contracts Protocols) and the service itself (including WP-03's strategies/discovery/, if present).
COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY contracts/ contracts/
COPY services/web-collector/ services/web-collector/
RUN uv sync --frozen --no-dev --no-editable --package jane-web-collector \
 && mkdir -p services/web-collector/strategies

FROM ${PYTHON_IMAGE}
RUN useradd --system --uid 10001 --no-create-home jane \
 && mkdir -p /var/lib/jane-web-collector && chown jane /var/lib/jane-web-collector
COPY --from=build /app/.venv /app/.venv
COPY --from=build /src/contracts/openapi /app/contracts/openapi
COPY --from=build /src/contracts/schemas /app/contracts/schemas
COPY --from=build /src/contracts/examples /app/contracts/examples
COPY --from=build /src/services/web-collector/strategies /app/strategies
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    JANE_WEB_COLLECTOR_HOST=0.0.0.0 \
    JANE_WEB_COLLECTOR_PORT=8101 \
    JANE_WEB_COLLECTOR_STATE_DIR=/var/lib/jane-web-collector \
    JANE_WEB_COLLECTOR_CONTRACTS_DIR=/app/contracts \
    JANE_WEB_COLLECTOR_DISCOVERY_PATH=/app/strategies/discovery
USER jane
VOLUME ["/var/lib/jane-web-collector"]
EXPOSE 8101
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.environ['JANE_WEB_COLLECTOR_PORT']}/v1/health\", timeout=2)"]
CMD ["python", "-m", "jane_web_collector"]
