#!/bin/sh
# Runs inside the PostgreSQL image on every `just up`; psql variables quote passwords safely in SQL.
set -eu
exec psql -X -v ON_ERROR_STOP=1 \
  -v handler_runtime_password="$JANE_PG_HANDLER_RUNTIME_PASSWORD" \
  -v orchestrator_password="$JANE_PG_ORCHESTRATOR_PASSWORD" \
  -v registry_password="$JANE_PG_REGISTRY_PASSWORD" \
  -v llm_password="$JANE_PG_LLM_PASSWORD" \
  -v assistant_password="$JANE_PG_ASSISTANT_PASSWORD" \
  -v storage_results_password="$JANE_PG_STORAGE_RESULTS_PASSWORD" \
  -f /opt/jane/provision.sql
