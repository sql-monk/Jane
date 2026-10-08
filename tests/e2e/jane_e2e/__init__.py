"""Helpers of the Jane end-to-end acceptance tests (WP-13).

* :mod:`jane_e2e.stack` - the full stack under a unique compose project (infra + application services);
* :mod:`jane_e2e.clients` - contract-validating HTTP clients for every Jane API;
* :mod:`jane_e2e.materials` - a ``Material`` that the test, as a third-party application, builds itself as the
  input of a direct executor call (not a replacement of the Web Collector in a chain);
* :mod:`jane_e2e.registry` - publication of the packages of this checkout to the REAL registry.

Only real services are exercised; substitutes of *external* systems (fake LLM, fake Telegram, SeaweedFS
for S3, the gated ``download_url`` of ``package-host``) are always named as such in the scenario.
"""
