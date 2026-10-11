# Архів попередньої документації

Тут зберігається документація Jane, чинна до перебудови за [вимогами до документації](../DOCUMENTATION_REQUIREMENTS.md). Файли перенесено командою `git mv` з ревізії `6ed7bfa`, тому `git log --follow` показує їхню історію. Нова документація цих текстів не використовує; актуальний зміст — у [docs/README.md](../docs/README.md).

Шлях в архіві повторює початковий: `docs-archive/legacy/<початковий шлях>`.

## Що лишилося в активній структурі

| Що | Чому |
|---|---|
| `TECHNICAL_SPECIFICATION.md`, `plan.md`, `recomendations.md` | джерела вимог |
| `AGENTS.md`, `CLAUDE.md`, `services/*/CLAUDE.md`, `.agents/skills/` | чинні інструкції агентів |
| `DOCUMENTATION_REQUIREMENTS.md`, `.agents/skills/jane-documentation/` | вимоги до документації |
| `contracts/README.md`, `contracts/docs/*.md` | нормативна частина контрактів |
| README і промпти всередині пакетів обробників | частина артефакту пакета |

## Перелік переміщень

### Кореневі й допоміжні README

| Початковий шлях | В архіві |
|---|---|
| `README.md` | [legacy/README.md](legacy/README.md) |
| `DEVELOPMENT.md` | [legacy/DEVELOPMENT.md](legacy/DEVELOPMENT.md) |
| `deploy/profiles/README.md` | [legacy/deploy/profiles/README.md](legacy/deploy/profiles/README.md) |
| `examples/README.md` | [legacy/examples/README.md](legacy/examples/README.md) |
| `examples/shops/README.md` | [legacy/examples/shops/README.md](legacy/examples/shops/README.md) |
| `infra/README.md` | [legacy/infra/README.md](legacy/infra/README.md) |
| `tests/e2e/README.shared-hosts.md` | [legacy/tests/e2e/README.shared-hosts.md](legacy/tests/e2e/README.shared-hosts.md) |
| `tests/fixtures/testsite/README.md` | [legacy/tests/fixtures/testsite/README.md](legacy/tests/fixtures/testsite/README.md) |

### README модулів

| Початковий шлях | В архіві |
|---|---|
| `libs/extractor-sdk/README.md` | [legacy/libs/extractor-sdk/README.md](legacy/libs/extractor-sdk/README.md) |
| `libs/jane-kit/README.md` | [legacy/libs/jane-kit/README.md](legacy/libs/jane-kit/README.md) |
| `services/assistant/README.md` | [legacy/services/assistant/README.md](legacy/services/assistant/README.md) |
| `services/handler-runtime/README.md` | [legacy/services/handler-runtime/README.md](legacy/services/handler-runtime/README.md) |
| `services/llm/README.md` | [legacy/services/llm/README.md](legacy/services/llm/README.md) |
| `services/orchestrator/README.md` | [legacy/services/orchestrator/README.md](legacy/services/orchestrator/README.md) |
| `services/registry/README.md` | [legacy/services/registry/README.md](legacy/services/registry/README.md) |
| `services/storage/README.md` | [legacy/services/storage/README.md](legacy/services/storage/README.md) |
| `services/storage/adapters/files/README.md` | [legacy/services/storage/adapters/files/README.md](legacy/services/storage/adapters/files/README.md) |
| `services/storage/adapters/minio/README.md` | [legacy/services/storage/adapters/minio/README.md](legacy/services/storage/adapters/minio/README.md) |
| `services/storage/adapters/mongodb/README.md` | [legacy/services/storage/adapters/mongodb/README.md](legacy/services/storage/adapters/mongodb/README.md) |
| `services/storage/adapters/postgres/README.md` | [legacy/services/storage/adapters/postgres/README.md](legacy/services/storage/adapters/postgres/README.md) |
| `services/storage/adapters/s3/README.md` | [legacy/services/storage/adapters/s3/README.md](legacy/services/storage/adapters/s3/README.md) |
| `services/storage/adapters/sqlserver/README.md` | [legacy/services/storage/adapters/sqlserver/README.md](legacy/services/storage/adapters/sqlserver/README.md) |
| `services/telegram-collector/README.md` | [legacy/services/telegram-collector/README.md](legacy/services/telegram-collector/README.md) |
| `services/web-collector/README.md` | [legacy/services/web-collector/README.md](legacy/services/web-collector/README.md) |
| `services/web-collector/strategies/discovery/README.md` | [legacy/services/web-collector/strategies/discovery/README.md](legacy/services/web-collector/strategies/discovery/README.md) |
| `web/admin/README.md` | [legacy/web/admin/README.md](legacy/web/admin/README.md) |

### Архітектурні рішення

| Початковий шлях | В архіві |
|---|---|
| `docs/adr/0001-baseline-stack.md` | [legacy/docs/adr/0001-baseline-stack.md](legacy/docs/adr/0001-baseline-stack.md) |
| `docs/adr/0002-package-registry.md` | [legacy/docs/adr/0002-package-registry.md](legacy/docs/adr/0002-package-registry.md) |
| `docs/adr/0003-python-sandbox.md` | [legacy/docs/adr/0003-python-sandbox.md](legacy/docs/adr/0003-python-sandbox.md) |
| `docs/adr/0004-large-materials.md` | [legacy/docs/adr/0004-large-materials.md](legacy/docs/adr/0004-large-materials.md) |
| `docs/adr/0005-authentication.md` | [legacy/docs/adr/0005-authentication.md](legacy/docs/adr/0005-authentication.md) |
| `docs/adr/0006-secrets-and-connections.md` | [legacy/docs/adr/0006-secrets-and-connections.md](legacy/docs/adr/0006-secrets-and-connections.md) |
| `docs/adr/0007-target-environments.md` | [legacy/docs/adr/0007-target-environments.md](legacy/docs/adr/0007-target-environments.md) |
| `docs/adr/0008-api-and-delivery-semantics.md` | [legacy/docs/adr/0008-api-and-delivery-semantics.md](legacy/docs/adr/0008-api-and-delivery-semantics.md) |
| `docs/adr/0009-data-ownership-and-autonomy.md` | [legacy/docs/adr/0009-data-ownership-and-autonomy.md](legacy/docs/adr/0009-data-ownership-and-autonomy.md) |
| `docs/adr/0010-llm-exploration-in-assistant.md` | [legacy/docs/adr/0010-llm-exploration-in-assistant.md](legacy/docs/adr/0010-llm-exploration-in-assistant.md) |
| `docs/adr/README.md` | [legacy/docs/adr/README.md](legacy/docs/adr/README.md) |

### Приймання й експлуатація

| Початковий шлях | В архіві |
|---|---|
| `docs/acceptance/matrix.md` | [legacy/docs/acceptance/matrix.md](legacy/docs/acceptance/matrix.md) |
| `docs/acceptance/scenarios.md` | [legacy/docs/acceptance/scenarios.md](legacy/docs/acceptance/scenarios.md) |
| `docs/operations/README.md` | [legacy/docs/operations/README.md](legacy/docs/operations/README.md) |
| `docs/operations/backup-restore.md` | [legacy/docs/operations/backup-restore.md](legacy/docs/operations/backup-restore.md) |
| `docs/operations/limits-validation.md` | [legacy/docs/operations/limits-validation.md](legacy/docs/operations/limits-validation.md) |

### Звіти й передачі робіт

| Початковий шлях | В архіві |
|---|---|
| `docs/delivery/HANDOFF-2026-09-30.md` | [legacy/docs/delivery/HANDOFF-2026-09-30.md](legacy/docs/delivery/HANDOFF-2026-09-30.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-a.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-a.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-a.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-b-2.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-b-2.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-b-2.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-b-3.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-b-3.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-b-3.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-b-4.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-b-4.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-b-4.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-b-5.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-b-5.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-b-5.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-b.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-b.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-b.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-c-2.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-c-2.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-c-2.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-c-3.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-c-3.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-c-3.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-c-4.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-c-4.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-c-4.md) |
| `docs/delivery/HANDOFF-2026-10-09-stream-c.md` | [legacy/docs/delivery/HANDOFF-2026-10-09-stream-c.md](legacy/docs/delivery/HANDOFF-2026-10-09-stream-c.md) |
| `docs/delivery/M3/01g-auth-coordinator.md` | [legacy/docs/delivery/M3/01g-auth-coordinator.md](legacy/docs/delivery/M3/01g-auth-coordinator.md) |
| `docs/delivery/M3/01g-auth.md` | [legacy/docs/delivery/M3/01g-auth.md](legacy/docs/delivery/M3/01g-auth.md) |
| `docs/delivery/M3/01h-content-policy.md` | [legacy/docs/delivery/M3/01h-content-policy.md](legacy/docs/delivery/M3/01h-content-policy.md) |
| `docs/delivery/M3/13t-real-registry.md` | [legacy/docs/delivery/M3/13t-real-registry.md](legacy/docs/delivery/M3/13t-real-registry.md) |
| `docs/delivery/M3/14d-docs.md` | [legacy/docs/delivery/M3/14d-docs.md](legacy/docs/delivery/M3/14d-docs.md) |
| `docs/delivery/M3/cleanup-plan.md` | [legacy/docs/delivery/M3/cleanup-plan.md](legacy/docs/delivery/M3/cleanup-plan.md) |
| `docs/delivery/M3/final-gate.md` | [legacy/docs/delivery/M3/final-gate.md](legacy/docs/delivery/M3/final-gate.md) |
| `docs/delivery/M3/final-review-delta.md` | [legacy/docs/delivery/M3/final-review-delta.md](legacy/docs/delivery/M3/final-review-delta.md) |
| `docs/delivery/M3/final-review.md` | [legacy/docs/delivery/M3/final-review.md](legacy/docs/delivery/M3/final-review.md) |
| `docs/delivery/M3/m3-should-fix.md` | [legacy/docs/delivery/M3/m3-should-fix.md](legacy/docs/delivery/M3/m3-should-fix.md) |
| `docs/delivery/M3/open-requests.md` | [legacy/docs/delivery/M3/open-requests.md](legacy/docs/delivery/M3/open-requests.md) |
| `docs/delivery/M3/stream-b.md` | [legacy/docs/delivery/M3/stream-b.md](legacy/docs/delivery/M3/stream-b.md) |
| `docs/delivery/M3/stream-c.md` | [legacy/docs/delivery/M3/stream-c.md](legacy/docs/delivery/M3/stream-c.md) |
| `docs/delivery/WP-00.md` | [legacy/docs/delivery/WP-00.md](legacy/docs/delivery/WP-00.md) |
| `docs/delivery/WP-01.md` | [legacy/docs/delivery/WP-01.md](legacy/docs/delivery/WP-01.md) |
| `docs/delivery/WP-02.md` | [legacy/docs/delivery/WP-02.md](legacy/docs/delivery/WP-02.md) |
| `docs/delivery/WP-03.md` | [legacy/docs/delivery/WP-03.md](legacy/docs/delivery/WP-03.md) |
| `docs/delivery/WP-04.md` | [legacy/docs/delivery/WP-04.md](legacy/docs/delivery/WP-04.md) |
| `docs/delivery/WP-05.md` | [legacy/docs/delivery/WP-05.md](legacy/docs/delivery/WP-05.md) |
| `docs/delivery/WP-06.md` | [legacy/docs/delivery/WP-06.md](legacy/docs/delivery/WP-06.md) |
| `docs/delivery/WP-07.md` | [legacy/docs/delivery/WP-07.md](legacy/docs/delivery/WP-07.md) |
| `docs/delivery/WP-08.md` | [legacy/docs/delivery/WP-08.md](legacy/docs/delivery/WP-08.md) |
| `docs/delivery/WP-09.md` | [legacy/docs/delivery/WP-09.md](legacy/docs/delivery/WP-09.md) |
| `docs/delivery/WP-10.md` | [legacy/docs/delivery/WP-10.md](legacy/docs/delivery/WP-10.md) |
| `docs/delivery/WP-11.md` | [legacy/docs/delivery/WP-11.md](legacy/docs/delivery/WP-11.md) |
| `docs/delivery/WP-12.md` | [legacy/docs/delivery/WP-12.md](legacy/docs/delivery/WP-12.md) |
| `docs/delivery/WP-12/admin-refresh.md` | [legacy/docs/delivery/WP-12/admin-refresh.md](legacy/docs/delivery/WP-12/admin-refresh.md) |
| `docs/delivery/WP-13.md` | [legacy/docs/delivery/WP-13.md](legacy/docs/delivery/WP-13.md) |
| `docs/delivery/WP-14.md` | [legacy/docs/delivery/WP-14.md](legacy/docs/delivery/WP-14.md) |
| `docs/delivery/WP-15.md` | [legacy/docs/delivery/WP-15.md](legacy/docs/delivery/WP-15.md) |
| `docs/delivery/WP-15/companion-deploy-profiles.patch` | [legacy/docs/delivery/WP-15/companion-deploy-profiles.patch](legacy/docs/delivery/WP-15/companion-deploy-profiles.patch) |
| `docs/delivery/WP-15/companion-jane-kit.patch` | [legacy/docs/delivery/WP-15/companion-jane-kit.patch](legacy/docs/delivery/WP-15/companion-jane-kit.patch) |
| `docs/delivery/WP-16.md` | [legacy/docs/delivery/WP-16.md](legacy/docs/delivery/WP-16.md) |
| `docs/delivery/WP-17.md` | [legacy/docs/delivery/WP-17.md](legacy/docs/delivery/WP-17.md) |
| `docs/delivery/WP-18.md` | [legacy/docs/delivery/WP-18.md](legacy/docs/delivery/WP-18.md) |
| `docs/delivery/WP-19.md` | [legacy/docs/delivery/WP-19.md](legacy/docs/delivery/WP-19.md) |
| `docs/delivery/WP-19/ci.md` | [legacy/docs/delivery/WP-19/ci.md](legacy/docs/delivery/WP-19/ci.md) |
| `docs/delivery/WP-19/contracts-r1.md` | [legacy/docs/delivery/WP-19/contracts-r1.md](legacy/docs/delivery/WP-19/contracts-r1.md) |
| `docs/delivery/WP-19/contracts-r2.md` | [legacy/docs/delivery/WP-19/contracts-r2.md](legacy/docs/delivery/WP-19/contracts-r2.md) |
| `docs/delivery/WP-19/review-r1.md` | [legacy/docs/delivery/WP-19/review-r1.md](legacy/docs/delivery/WP-19/review-r1.md) |
| `docs/delivery/WP-19/review-r2.md` | [legacy/docs/delivery/WP-19/review-r2.md](legacy/docs/delivery/WP-19/review-r2.md) |
| `docs/delivery/WP-19/telegram-pagination-followup.md` | [legacy/docs/delivery/WP-19/telegram-pagination-followup.md](legacy/docs/delivery/WP-19/telegram-pagination-followup.md) |
| `docs/delivery/WP-19/telegram-pagination-review.md` | [legacy/docs/delivery/WP-19/telegram-pagination-review.md](legacy/docs/delivery/WP-19/telegram-pagination-review.md) |
| `docs/delivery/WP-19/workspace-doc-followup.md` | [legacy/docs/delivery/WP-19/workspace-doc-followup.md](legacy/docs/delivery/WP-19/workspace-doc-followup.md) |
| `docs/delivery/WP-20.md` | [legacy/docs/delivery/WP-20.md](legacy/docs/delivery/WP-20.md) |
| `docs/delivery/WP-21.md` | [legacy/docs/delivery/WP-21.md](legacy/docs/delivery/WP-21.md) |
| `docs/delivery/WP-23/c2-workspace.md` | [legacy/docs/delivery/WP-23/c2-workspace.md](legacy/docs/delivery/WP-23/c2-workspace.md) |
| `docs/delivery/WP-23/c3-format.md` | [legacy/docs/delivery/WP-23/c3-format.md](legacy/docs/delivery/WP-23/c3-format.md) |
| `docs/delivery/WP-23/c4-cleanup.md` | [legacy/docs/delivery/WP-23/c4-cleanup.md](legacy/docs/delivery/WP-23/c4-cleanup.md) |
| `docs/delivery/post-m3/README.md` | [legacy/docs/delivery/post-m3/README.md](legacy/docs/delivery/post-m3/README.md) |
| `docs/delivery/post-m3/final-ci.md` | [legacy/docs/delivery/post-m3/final-ci.md](legacy/docs/delivery/post-m3/final-ci.md) |
| `docs/delivery/post-m3/stream-a-handoff.md` | [legacy/docs/delivery/post-m3/stream-a-handoff.md](legacy/docs/delivery/post-m3/stream-a-handoff.md) |
| `docs/delivery/post-m3/stream-b-handoff.md` | [legacy/docs/delivery/post-m3/stream-b-handoff.md](legacy/docs/delivery/post-m3/stream-b-handoff.md) |
| `docs/delivery/post-m3/stream-b.md` | [legacy/docs/delivery/post-m3/stream-b.md](legacy/docs/delivery/post-m3/stream-b.md) |
| `docs/delivery/post-m3/stream-c-handoff.md` | [legacy/docs/delivery/post-m3/stream-c-handoff.md](legacy/docs/delivery/post-m3/stream-c-handoff.md) |
| `docs/delivery/post-m3/stream-c.md` | [legacy/docs/delivery/post-m3/stream-c.md](legacy/docs/delivery/post-m3/stream-c.md) |
| `docs/delivery/status.md` | [legacy/docs/delivery/status.md](legacy/docs/delivery/status.md) |
