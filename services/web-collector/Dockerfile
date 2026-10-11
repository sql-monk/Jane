# syntax=docker/dockerfile:1
# Build context: repository root.
#   docker build -f services/web-collector/Dockerfile -t jane-web-collector .
# With JavaScript rendering (fetch.render_js: Playwright, headless Chromium and its libraries, about 1 GB more):
#   docker build -f services/web-collector/Dockerfile --build-arg EXTRAS="--extra render" -t jane-web-collector .
ARG PYTHON_IMAGE=python:3.12-slim
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.13

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS build
ARG EXTRAS=""
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /src
# Only what this service needs: workspace root, lock, shared libs, contracts (schemas for validation and
# the jane-contracts Protocols) and the service itself (including WP-03's strategies/discovery/, if present).
COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY contracts/ contracts/
COPY services/web-collector/ services/web-collector/
RUN uv sync --frozen --no-dev --no-editable --package jane-web-collector ${EXTRAS} \
 && mkdir -p services/web-collector/strategies

# Runtime base. With the render extra: headless Chromium and its system libraries, installed by the Playwright
# version locked in uv.lock (the one the service imports). The layer depends on uv.lock only, so a code change
# does not download the browser again. Without the extra nothing is added, and fetch.render_js URLs fail with
# not_implemented.
FROM ${PYTHON_IMAGE} AS runtime
ARG EXTRAS=""
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright
RUN --mount=from=uv,source=/uv,target=/usr/local/bin/uv \
    --mount=type=bind,source=uv.lock,target=/tmp/uv.lock \
    case "$EXTRAS" in \
      *render*) \
        version="$(python -c "import tomllib; print(next(p['version'] for p in tomllib.load(open('/tmp/uv.lock', 'rb'))['package'] if p['name'] == 'playwright'))")" \
        && UV_PYTHON_DOWNLOADS=never uv venv /tmp/playwright-cli \
        && uv pip install --no-cache --python /tmp/playwright-cli/bin/python "playwright==${version}" \
        && /tmp/playwright-cli/bin/playwright install --with-deps --only-shell chromium \
        && rm -rf /tmp/playwright-cli /var/lib/apt/lists/* ;; \
    esac

FROM runtime
RUN useradd --system --uid 10001 --no-create-home jane \
 && mkdir -p /var/lib/jane-web-collector && chown jane /var/lib/jane-web-collector
RUN mkdir -p /var/lib/jane-operations && chown jane /var/lib/jane-operations
ENV JANE_WEB_COLLECTOR_OPERATIONS_DIR=/var/lib/jane-operations
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
