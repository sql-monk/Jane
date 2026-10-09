"""jane-kit: shared building blocks for Jane services.

Modules: ``config`` (settings, inherited limits), ``logs`` (structured JSON logs), ``metrics``
(Prometheus), ``health``, ``errors`` (Problem details), ``idempotency``, ``jobs`` (202 + job_id),
``stores`` (shared PostgreSQL / SQLite job and idempotency stores with leases and fencing), ``secrets``
(secret references and destination allowlists of managed connections), ``schemas`` (contract schema
validation), ``rules`` (collector rules), ``content`` (ContentRef reading and writing), ``clients`` (HTTP
client base), ``contracts`` (OpenAPI validation, contract client, mocks), ``codegen`` (client generation),
``service`` (FastAPI app factory), ``devstack`` (local stack info), ``auth`` (ADR-0005).
"""

__version__ = "0.1.0"
