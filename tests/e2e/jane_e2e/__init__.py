"""Helpers of the Jane end-to-end acceptance tests (WP-13).

* :mod:`jane_e2e.stack` - the full stack under a unique compose project (infra + application services);
* :mod:`jane_e2e.clients` - contract-validating HTTP clients for every Jane API;
* :mod:`jane_e2e.materials` - explicitly labelled stand-ins for components that are not merged yet.

Only real services are exercised; substitutes of *external* systems (fake LLM, fake Telegram, SeaweedFS
for S3) and stand-ins for not-yet-merged components are always named as such in the scenario.
"""
