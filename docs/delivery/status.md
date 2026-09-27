# Статус пакетів робіт

Веде координатор. Статуси: `ready → active → review → accepted` або `blocked` (з причиною). Див. [plan.md](../../plan.md) §1, §6.

| WP | Назва | Хвиля | Статус | Гілка | Виконавець / рев'юер | Примітка |
|---|---|---|---|---|---|---|
| 00 | Архітектура й контракти | 0 | accepted | `wp/00-architecture-contracts` | агент / wp-reviewer (2 раунди) | злито `e2714ec` |
| 01 | Каркас, CI, dev-стек | 0 | accepted | `wp/01-scaffold-ci` | агент / wp-reviewer (2 раунди + інтеграційне виправлення) | злито `4468cee` |
| 02 | Web Collector: ядро | 1 | active | `wp/02-web-collector-core` | агент / wp-reviewer | фінальне виправлення після рев'ю 2 (хибний succeeded), перевірка координатором |
| 03 | Web Collector: стратегії пошуку | 1 | — | | | після M0 |
| 04 | Telegram Collector | 1 | active | `wp/04-telegram-collector` | агент | слот 3 |
| 05 | Репозиторій обробників | 1 | review | `wp/05-registry` | агент / wp-reviewer | |
| 06 | Runtime обробників і SDK | 1 | accepted | `wp/06-handler-runtime` | агент / wp-reviewer (2 раунди) | злито `e59aa86` |
| 07 | Збереження: ядро + files + PostgreSQL | 1 | accepted | `wp/07-storage-core` | агент / wp-reviewer (2 раунди) | злито `6f57834` |
| 08 | Адаптери збереження | 1 | active | `wp/08-storage-adapters` | агент / wp-reviewer | виправлення після рев'ю 1 (дублі історії: s3 412, mongodb гонка) |
| 09 | Оркестратор | 1 | active | `wp/09-orchestrator` | агент / wp-reviewer | виправлення після рев'ю 1 (cancelling, retries, overlap) |
| 10 | LLM-шлюз і LLM-обробник | 1 | active | `wp/10-llm` | агент / wp-reviewer | виправлення після рев'ю 1 (ін'єкція в retry_hint, secret_refs) |
| 11 | Асистент джерел | 1 | active | `wp/11-assistant` | агент / wp-reviewer | виправлення після рев'ю 1 (кілька екземплярів) |
| 12 | Адмінка | 1 | active | `wp/12-admin` | агент | слот 3 |
| 13 | Інтеграція й приймання | 2 | active | `wp/13-acceptance` | агент | фаза 1: матриця, сценарії, каркас e2e |
| 14 | Профілі лімітів і експлуатація | 2 | — | | | після M1 |

## Віхи
| Віха | Умова | Стан |
|---|---|---|
| M0 | WP-00 і WP-01 прийняті | досягнуто 2026-09-27 (`4468cee`) |
| M1 | WP-02, 06, 07 + база 09 | — |
| M2 | Усі WP хвилі 1 | — |
| M3 | WP-13, WP-14, фінальне рев'ю | — |

## Журнал
- 2026-09-27 — ініціалізовано репозиторій, інструменти координатора (CLAUDE.md, хуки, `jane-wp`, `wp-reviewer`).
- 2026-09-27 — запущено хвилю 0: WP-00 і WP-01 (окремі worktree, база `4832751`).
- 2026-09-27 — публічний репозиторій: https://github.com/sql-monk/Jane.
- 2026-09-27 — рішення людини: хвиля 1 запускається слотами (до 4 агентів одночасно, порядок plan.md §6); кожен WP зливається в `main` одразу після прийняття, не чекаючи кінця хвилі, після злиття — push і CI.
- 2026-09-27 — WP-00 прийнято (рев'ю 2 раунди) і злито в main; контракти на main зелені. WP-01 — виправлення після рев'ю 1; guard_bash посилено (refs між worktree).
- 2026-09-27 — WP-01 прийнято і злито; на main `just check` зелений, gitleaks 0. **M0 досягнуто.** Встановлено git pre-commit (gitleaks). guard_bash дозволяє read-only `git merge-tree`/`merge-base`.
- 2026-09-27 — хвиля 1, слот 1: запущено WP-09, WP-02, WP-06, WP-07 (база `39de0b4`).
- 2026-09-27 — ліміт сесії перервав слот 1; агентів відновлено з тих самих worktree. CI на main зелений (`ef5a879`).
- 2026-09-27 — WP-07 на рев'ю; запущено WP-11.
- 2026-09-27 — WP-06 на рев'ю; запущено WP-05 (узгодити канонічний архів з WP-06/07).
- 2026-09-27 — WP-02 на рев'ю; запущено WP-10. WP-07 повернуто: типовий формат RAW не за ТЗ §5.

## Відкриті запити між власниками
| Від | Кому | Запит | Стан |
|---|---|---|---|
| WP-07 | координатор / WP-01 | `scripts/dev.py` `members()`: додати `services/storage/adapters/*`, щоб `just types` перевіряв адаптери | зроблено координатором |
| WP-07 | WP-01 | спільний помічник `ContentRef` у jane-kit (ADR-0004) | відкрито |
| WP-07 | WP-05 | канонічний архів і дайджест пакета (zip stored, відсортовано, дата 1980, 0644); дайджести в прикладах WP-00 не реальні | передати WP-05 |
| WP-07 | WP-00 | задокументувати `DeliveryRecord.acks`; простір імен етапу в storage.v1; приклад `storage-files.json` `format.raw: html` vs `original` | зміна контракту через contract-guardian |
| WP-07 | WP-09 | `Idempotency-Key` = `delivery_key`; `handler.digest` з registry або `/v1/info` | передати WP-09 |
| WP-06 | WP-05 | перевірка `dependencies.python` за профілем `python-extractor@1`; канонічний архів (`build_archive` у SDK) | передано WP-05 |
| WP-06 | WP-00 | `/v1/connections*` у handler.v1 необов'язкові для виконавців без підключень | зміна контракту через contract-guardian |
| WP-06 | WP-01 | застарілий коментар job `isolation` у `ci.yml`; Docker на runner | відкрито |
| WP-02 | WP-00 | чи викликає ядро `on_fetched` для не-2xx і чи ділиться ресурсом `ctx.fetch`; конвенція `params` для підключень `kind=http` | зміна контракту через contract-guardian |
| WP-02 | WP-01 | `contracts/python` у uv workspace (зараз path-залежність) | необов'язково |
| WP-07 рев'ю | WP-00 | `default` формату в `package-manifest.schema.json` узгодити з описом і ТЗ §5 | зміна контракту через contract-guardian |
- 2026-09-27 — WP-06 і WP-02 повернуто після рев'ю 1 (кілька екземплярів, контракт connections, lease/fencing, тайм-аути з рівнів лімітів). WP-07 — рев'ю 2.
- 2026-09-27 — WP-07 прийнято (2 раунди) і злито; на main `just check` зелений, gitleaks 0. Адаптери додано в `just types`.
- 2026-09-27 — WP-09 на рев'ю (2 нестабільні падіння з 7 — рецензент ганяє повторно); запущено WP-08.
| WP-09 | WP-00 | форма входу `select: problems` і виходу етапу збереження; `ProblemGroup.note`; чи застосовуються активації до `collector.rules` | зміна контракту через contract-guardian |
| WP-09 | WP-00 / WP-07 | фільтр `storage.v1 /v1/objects` за кількома `material_id` | зміна контракту через contract-guardian |
| WP-09 | WP-01 | перевірка JWT у jane-kit | відкрито |
| WP-09 | WP-02 / WP-04 | ідемпотентний `POST /v1/collections`; `limits.queue.max_unacked_materials` із запиту; `rules_ref` без registry для M1 | WP-02 виконав; передати WP-04 |
| WP-09 | WP-05 | registry віддає `kind`, `auto_changes_allowed`, `status`, `test_status`, `digest` | передати WP-05 |
| WP-09 | WP-14 | профіль `PlatformLimits` для `JANE_ORCHESTRATOR_LIMITS_FILE` | після M1 |
| WP-10 | WP-00 | контракт перетворення виходу LLM на EntityRecord; семантика `BudgetStatus.exhausted` і рівень бюджету із запиту | зміна контракту через contract-guardian |
| WP-10 | WP-09 | синхронізувати бюджети й підключення `llm_provider` (`PUT /v1/budgets`, `PUT /v1/connections`); `context.trace` у викликах | передати WP-09 (рев'ю) |
| WP-10 | координатор / WP-01 | не додавати до workspace залежностей, що тягнуть `httpx2` (ламає TestClient і mypy) | правило |
| WP-11 | WP-00 | поле пропозиції в `ImprovementResult` при `proposal_only`; `llm.min_onboarding_confidence`; де клієнт бере `session_id` з 202 Job | зміна контракту через contract-guardian |
| WP-11 | WP-01 / координатор | асистент (і нові сервіси) у compose і proxy | відкрито |
- 2026-09-27 — другий ліміт сесії перервав WP-05, WP-08 і рев'ю WP-02/WP-09; відновлено. WP-06 прийнято (2 раунди) і злито; main зелений, gitleaks 0. WP-10 і WP-11 на рев'ю.
- 2026-09-27 — запущено WP-04 і WP-12.

## Наскрізні питання
| Питання | Де знайдено | Рішення | Стан |
|---|---|---|---|
| Без автентифікації `PUT /v1/connections` з довільним `api_base`/хостом і `secret_refs: env:<будь-яка змінна>` дозволяє вивести значення змінних середовища на чужий хост | рев'ю WP-10 | `env:` — лише змінні з налаштовуваним префіксом (типово `JANE_SECRET_`), `file:` — лише з налаштовуваного каталогу, хости підключень — з allowlist; оновити ADR-0006 і застосувати в усіх виконавцях із підключеннями (WP-02, 04, 07, 08, 09, 10) | WP-10 — у виправленнях; решта — окремим дорученням після M1 |
- 2026-09-27 — WP-11 і WP-10 повернуто після рев'ю 1. Знайдено наскрізну вразливість `secret_refs` (див. «Наскрізні питання»).
- 2026-09-27 — WP-09 повернуто після рев'ю 1: зависання в `cancelling`, kill витрачає retries, гонка `overlap: queue`. Рішення: оркестратор синхронізує бюджети LLM рівнів source/task у шлюз.
| WP-05 | WP-06 | `build_archive` SDK → `ZIP_STORED` (канонічний архів registry/storage), опис `JANE_REGISTRY_RUNTIME_PROFILES` | доручення-доповнення WP-06 після M1 |
| WP-05 | WP-00 | канонічний алгоритм архіву в `handler-packages.md`; дайджести прикладів — ілюстративні; код «профіль недоступний»; `jane-package.json` у diff лише в `manifest_changes` | зміна контракту через contract-guardian |
- 2026-09-27 — WP-05 на рев'ю. WP-02: рев'ю 2 знайшло хибний термінальний `succeeded` при «завислому» власнику — фінальне виправлення, перевіряє координатор (20× прогонів).
| WP-08 | WP-00 | розділ «Об'єктні сховища» в storage-adapter.md під схему «подія в знімку (`pending`)»; порядок `list_entities` залежить від адаптера | після рев'ю WP-08, через contract-guardian |
| WP-08 | WP-07 | `chunk_bytes`, `retry_max_attempts` у `ServiceLimits.adapters` | необов'язково |
| WP-08 | координатор / WP-01 | CI: сервіси `sqlserver mongodb minio s3` для інтеграційних тестів адаптерів | відкрито |
- 2026-09-27 — WP-08 на рев'ю; запущено WP-13 (фаза 1).
- 2026-09-27 — WP-08 повернуто після рев'ю 1: дубль історії в s3/minio (компенсація на 412) і mongodb (гонка двох екземплярів); схему `pending` визнано коректною.
