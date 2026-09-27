# syntax=docker/dockerfile:1
# Sandbox image of runtime profile python-extractor@1 (ADR-0003).
# Build context: repository root (the runtime CLI `jane-handler-runtime build-image` sends only the files below).
#   docker build -f services/handler-runtime/sandbox/python-extractor-1/Dockerfile -t jane/python-extractor:1 .
ARG PYTHON_IMAGE=python:3.12.12-slim-bookworm
FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Exact library versions of the profile; nothing is installed at run time (the sandbox has no network).
COPY services/handler-runtime/sandbox/python-extractor-1/requirements.txt /opt/jane/requirements.txt
RUN pip install --no-deps -r /opt/jane/requirements.txt && pip check

# The SDK (standard library only) with its runner: python -I -m jane_extractor_sdk.runner /work
COPY libs/extractor-sdk/src/jane_extractor_sdk /usr/local/lib/python3.12/site-packages/jane_extractor_sdk
RUN python -m compileall -q /usr/local/lib/python3.12/site-packages/jane_extractor_sdk \
    && mkdir -p /work && chmod 0755 /work \
    && python -c "import jane_extractor_sdk, lxml, selectolax, bs4, parsel, jsonpath_ng, dateutil"

LABEL org.opencontainers.image.title="jane python-extractor@1" \
      io.jane.runtime-profile="python-extractor@1"

# /work is owned by root and read-only for the sandbox user; the runtime copies package and input there.
USER 65534:65534
WORKDIR /tmp
CMD ["python", "-I", "-m", "jane_extractor_sdk.runner", "/work"]
