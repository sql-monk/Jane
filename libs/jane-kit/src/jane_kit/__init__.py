"""jane-kit: shared building blocks for Jane services.

Modules: ``config`` (settings, inherited limits), ``logs`` (structured JSON logs), ``metrics``
(Prometheus), ``health``, ``errors`` (Problem details), ``idempotency``, ``jobs`` (202 + job_id),
``clients`` (HTTP client base), ``contracts`` (OpenAPI validation, contract client, mocks),
``codegen`` (client generation), ``service`` (FastAPI app factory), ``devstack`` (local stack info).
"""

__version__ = "0.1.0"
