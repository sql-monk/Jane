# Асистент джерел (assistant)

Сервіс WP-11. Підключає нове джерело за назвою чи посиланням (пошук, уточнення, адаптивна вибірка,
аналіз, варіанти збору, пошук/перевірка/форк/створення екстракторів), вдосконалює екстрактори на
проблемних прикладах (нова версія або форк, тести на всіх прив'язках, погодження чи автоактивація з
відкатом) і аналізує невідомі матеріали — лише за увімкненим прапорцем «Передавати в LLM невідомі
сторінки». Контракт: `contracts/openapi/assistant.v1.yaml` (конвенції — скіл `jane-contracts`).

Асистент не має власних даних-результатів: пакети живуть у registry, джерела й завдання — в оркестраторі.
Сусіди (усе — за їхніми контрактами):

| Сусід | Навіщо | Операції |
|---|---|---|
| llm (`llm.v1`) | класифікація, аналіз, варіанти, код | `createCompletion` |
| collector web/telegram (`collector.v1`) | вибірка, перевірка правил | `startCollection`, `listCollectionMaterials`, `getCollection`, `cancelJob`, `validateRules` |
| registry (`registry.v1`) | пошук, форк, публікація, статуси, звіти тестів | `listPackages`, `getPackage`, `downloadPackageArchive`, `createPackage`, `publishPackageVersion`, `forkPackage`, `recordTestResults`, `setPackageVersionStatus` |
| handler-runtime (`handler.v1`) | тести без запису (чернетки — inline-архівом) | `startTestRun` |
| orchestrator (`orchestrator.v1`) | прив'язки спільного пакета, активація/відкат, групи проблем, створення джерела й завдання | `listTasks?package_id=`, `getTask`, `activateStageVersion`, `updateProblemGroup`, `createSource`, `createTask`, `getSource` |
| storage (`storage.v1`) | вміст `material_ref` проблемних прикладів | `getObject`, `getObjectContent` |

Не налаштований сусід → job завершується `failed` з кодом `upstream_unavailable` (без здогадок).

## Як працює

**Підключення** (`POST /v1/onboarding-sessions` → 202 Job; `labels.session_id` і `links.session` — адреса сесії):

1. URL, `@channel` або `t.me/…` — беруться як є; назва йде в пошуковий провайдер. Явний лідер
   (`onboarding.auto_select_confidence` і відрив `auto_select_margin`) обирається сам, інакше
   `needs_disambiguation` → `POST …/candidate-selection`.
2. Адаптивна вибірка: звичайний збір колектора (sitemap + стрічки + рекурсія від входу; для Telegram —
   історія), з кожної порції беруться найменш представлені «форми» URL, їх класифікує дешева модель.
   Впевненість = покриття вибірки за Гудом–Тьюрінгом (`1 − частка матеріалів типів, бачених менше
   ніж min_examples_per_type разів`) × середня впевненість моделі. Зупинка — при `min_confidence`;
   якщо раніше закінчились межа `llm.max_onboarding_samples`, матеріали або бюджет — `insufficient_sample`
   з поясненням. Збір колектора після цього скасовується.
3. Аналіз: типи матеріалів, сутності, поля, способи обходу (лише реальні стратегії, без `llm_explore` — ADR-0010).
4. Для кожного очікуваного типу сутності: пошук екстракторів у registry (за доменом і загалом), прогін
   на зразках через handler-runtime; частка успіхів ≥ `bind_threshold` → прив'язка, ≥ `fork_threshold`
   → форк з адаптацією, інакше генерація нового пакета (маніфест будує асистент, модель дає код, схему
   й очікування; код перевіряється статично, пакет — тестами `success` + `empty|unrecognized`).
5. Кілька варіантів правил з оцінкою охоплення (`estimated_materials`), вартості
   (`requests_per_run_estimate`, `llm_setup_cost`, `llm_cost_per_run`) і ризиків. Кожен варіант проходить
   захист (див. нижче), JSON Schema і `validateRules` колектора.
6. `POST …/proposals/{id}/acceptance` → 202: публікація правил і пакетів (`draft`), звіти тестів, чернетки
   Source і TaskConfig. `activate: true` (або `auto_activation` у запиті — тоді рекомендований варіант
   приймається сам) і всі тести зелені → версії погоджуються, джерело й завдання створюються в оркестраторі.

**Вдосконалення** (`POST /v1/improvement-runs` → 202; `Job.result` = `ImprovementResult`):
групування проблем за джерелом і характером (сигнатура `unrecognized`, вид збою, коди діагностики) →
модель отримує групи, код, схеми, діагностику, успішні приклади → кандидат проходить старі тести, нові
тести з проблемних прикладів (`origin: problem_sample`), регресії на успішних прикладах і тести з
параметрами кожної прив'язки (`listTasks?package_id=` + `getTask`). Ламає прив'язки інших джерел або
несумісно змінює схему спільного пакета → форк для цього джерела (`policy.allow_fork`), інакше
`unresolved`. `auto_changes_allowed = false` → `proposal_only`, нічого не публікується.
`policy.approval = auto_after_checks` → погодження й `auto_activate` на всіх цільових прив'язках; якщо
оркестратор відмовив на одній — уже активовані відкочуються (`kind: rollback`). Стан групи проблем
(`in_progress` → `resolved` / `unresolved` з поясненням) оновлюється в оркестраторі — так невирішене видно
в адмінці. Нові типи сутностей лише пропонуються (`suggested_entity_types`).

**Невідомі матеріали** (`POST /v1/unknown-materials`): `forward_unknown_to_llm = false` → 403
`access_denied_by_policy` без жодного виклику LLM; інакше класифікація й пропозиція
(`new_extractor`, `extend_rules`, `expand_entity_types`, `none`).

**Вміст джерел — дані, не інструкції.** Інструкції моделі — сталі тексти (`prompts.py`); вміст сторінок,
код і діагностика — лише в `data`. Вихід моделі не довіряється: правила обмежуються хостами джерела
(плюс домени, які дозволив *користувач* у `crawl_hints`), `robots` завжди `respect`, без `llm_explore` і
лімітів у правилах; код без заборонених імпортів і викликів; маніфест за схемою. Відхилене видно в
`risks` варіанту.

## Незалежний запуск

Без Docker (з кореня репозиторію):

```
uv sync --all-packages
JANE_ASSISTANT_LLM_URL=http://127.0.0.1:8110 JANE_ASSISTANT_REGISTRY_URL=http://127.0.0.1:8105 \
JANE_ASSISTANT_COLLECTOR_WEB_URL=http://127.0.0.1:8101 JANE_ASSISTANT_HANDLER_RUNTIME_URL=http://127.0.0.1:8106 \
uv run --package jane-assistant python -m jane_assistant
curl http://127.0.0.1:8000/v1/health
```

Проти моків сусідів із контрактів: `uv run contracts/tools/mock.py <api> --port <порт>` для кожного сусіда.

У Docker (контекст збірки — корінь репозиторію; образ містить `contracts/schemas` для локальної валідації):

```
docker build -f services/assistant/Dockerfile -t jane-assistant .
docker run --rm -p 8000:8000 -e JANE_ASSISTANT_LLM_URL=http://llm:8000 jane-assistant
```

Кілька екземплярів: запускаються як звичайні процеси чи контейнери. Сесії підключення, job і ключі
ідемпотентності зараз зберігаються в пам'яті екземпляра (`InMemorySessionStore`, `InMemoryJobStore`,
`InMemoryIdempotencyStore`), тож без спільного сховища запит про сесію має потрапити на той екземпляр,
що її створив (sticky routing за `session_id`/`job_id`). Для справжнього горизонтального масштабування
треба реалізувати протоколи `SessionStore` / `JobStore` / `IdempotencyStore` на власній БД сервісу
(див. «Відомі обмеження» у звіті WP-11).

## Тести

```
just test assistant                  # unit + наскрізні сценарії + контрактні (одна команда)
just test assistant -m contract      # лише контрактні
```

Сценарії (`tests/test_onboarding.py`, `test_improvement.py`, `test_unknown.py`) запускають справжній
застосунок асистента; сусіди — фейки, прив'язані до контрактів (`tests/assistant_fakes`): кожен запит
асистента перевіряється за схемою запиту сусіда, кожна відповідь фейка — за схемою відповіді; порушення
валять тест. Фейкова LLM детермінована (диспетчеризація за `output_schema.title`), може «піддатись
ін'єкції», щоб перевірити захист. Тести пакетів справді виконуються (мінімальний замінник runtime).

## Конфігурація

Змінні середовища з префіксом `JANE_ASSISTANT_`:

| Змінна | Типово | Опис |
|---|---|---|
| `HOST` / `PORT` | `127.0.0.1` / `8000` (у контейнері `0.0.0.0`) | адреса прослуховування |
| `LOG_LEVEL` / `LOG_FORMAT` | `INFO` / `json` | журнали (JSON у stdout) |
| `METRICS_ENABLED` | `true` | `/metrics` (Prometheus) |
| `HEALTH_CHECK_TIMEOUT_MS` | `2000` | тайм-аут перевірок `/v1/health` |
| `AUTH_MODE` | `none` | значення для `/v1/info` |
| `LLM_URL`, `REGISTRY_URL`, `COLLECTOR_WEB_URL`, `COLLECTOR_TELEGRAM_URL`, `HANDLER_RUNTIME_URL`, `ORCHESTRATOR_URL`, `STORAGE_URL` | — | адреси сусідів |
| `SERVICE_TOKEN_ENV` | — | **ім'я** змінної з bearer-токеном для сусідів (значення в конфігурації немає) |
| `SEARCH_PROVIDER` | `none` | `none`, `static`, `http_json` |
| `SEARCH_STATIC_FILE` | — | JSON `[{"title","url"?,"telegram_username"?,"description"?,"aliases"?}]` |
| `SEARCH_URL_TEMPLATE`, `SEARCH_ITEMS_PATH`, `SEARCH_TITLE_FIELD`, `SEARCH_URL_FIELD`, `SEARCH_DESCRIPTION_FIELD` | —, `results`, `title`, `url`, `description` | HTTP-пошук з JSON-відповіддю |
| `LLM_MODEL_CHEAP` / `LLM_MODEL_STRONG` | `cheap` / `strong` | псевдоніми моделей шлюзу |
| `CONTRACTS_DIR` | пошук угору / `/app/contracts` | де `contracts/schemas` для локальної валідації |
| `GENERATED_CODE_ALLOWED_MODULES` | `re, html, json, math, datetime, decimal, string, unicodedata, itertools, functools, collections, typing, dataclasses` | політика імпортів згенерованого коду (JSON-список) |
| `ONBOARDING_ALLOW_ACTIVATION` | `true` | чи може прийняття з `activate: true` створювати джерело й завдання |
| `DEFAULT_STORAGE_PACKAGE` / `DEFAULT_STORAGE_CONNECTION` | — | `package_id@version` і `connection_id` етапу збереження в чернетці завдання |
| `LIMITS_FILE` | — | файл `PlatformLimits` (TOML/JSON/YAML) |
| `LIMITS__<ГРУПА>__<ПАРАМЕТР>` / `LIMITS__HARD_CAPS__…` | — | перевизначення й жорсткі стелі |

## Ліміти

Рівні: типові значення → платформа (файл, потім змінні середовища) → запит (`limits` у тілі —
контрактний `limits.llm`); `hard_caps` обмежують результат. `GET /v1/info` → `limits` показує контрактні
поля (`llm.*`, `transfer.*`, `timeouts.*`, `retries`); решта — внутрішні.

| Параметр | Типово | Опис |
|---|---|---|
| `llm.budget` | 2 USD / `run` | витрати одного job; асистент зупиняється сам, шлюз — теж (`budget_exhausted`) |
| `llm.max_onboarding_samples` | 60 | верхня межа класифікованих матеріалів (фактично — адаптивно менше) |
| `llm.max_improvement_attempts` | 3 | спроби моделі на один запуск вдосконалення (0 → одразу `unresolved`) |
| `llm.max_input_tokens_per_request` / `max_output_tokens_per_request` | 16000 / 4000 | дані обрізаються (~4 символи на токен) |
| `llm.max_requests_per_minute` | 30 | передається шлюзу |
| `onboarding.min_confidence` | 0.8 | поріг достатньої впевненості вибірки |
| `onboarding.sample_batch_size` | 10 | матеріалів на один запит класифікації |
| `onboarding.fetch_ratio` | 3 | збір вибірки може отримати до `max_onboarding_samples × fetch_ratio` матеріалів |
| `onboarding.min_examples_per_type` / `max_examples_per_type` | 2 / 3 | коли тип «розрізнено» / скільки прикладів у аналіз і тести |
| `onboarding.max_sample_chars` | 6000 | текст одного матеріалу для моделі |
| `onboarding.max_candidates`, `auto_select_confidence`, `auto_select_margin` | 5, 0.8, 0.2 | пошук і автовибір кандидата |
| `onboarding.max_candidate_packages`, `bind_threshold`, `fork_threshold` | 5, 0.9, 0.5 | підбір готових екстракторів |
| `onboarding.max_generation_attempts` | 2 | спроби згенерувати пакет, що проходить тести |
| `onboarding.max_proposals` | 4 | варіантів збору |
| `onboarding.collection_poll_wait_ms`, `max_empty_polls` | 1000, 30 | long-poll матеріалів вибірки |
| `onboarding.requests_overhead_ratio` | 0.05 | запас запитів понад оцінку матеріалів |
| `improvement.max_problem_samples`, `max_successful_examples`, `max_sample_chars`, `max_file_chars` | 10, 5, 6000, 20000 | обсяг даних для моделі |
| `unknown.min_confidence`, `max_sample_chars` | 0.6, 6000 | нижче — пропозиція `none` |
| `transfer.inline_max_bytes` | 262144 | чернетка пакета до runtime inline; більша — `payload_too_large` |
| `clients.*` (тайм-аути, повтори, опитування job) | див. jane-kit | виклики сусідів |
| `jobs.*`, `idempotency.*` | див. jane-kit | job і ключі ідемпотентності |

## Приклад виклику зі стороннього застосунку

```python
import time

import httpx

with httpx.Client(base_url="http://127.0.0.1:8000") as client:
    job = client.post(
        "/v1/onboarding-sessions",
        json={"query": "https://shop.example.test/", "expected_entity_types": ["product"]},
        headers={"Idempotency-Key": "onboard-shop-1"},
    ).json()
    session_id = job["labels"]["session_id"]
    while client.get(f"/v1/jobs/{job['job_id']}").json()["status"] not in {
        "succeeded",
        "failed",
        "cancelled",
    }:
        time.sleep(1)
    session = client.get(f"/v1/onboarding-sessions/{session_id}").json()
    best = next(p for p in session.get("proposals", []) if p["recommended"])
    accept = client.post(
        f"/v1/onboarding-sessions/{session_id}/proposals/{best['proposal_id']}/acceptance",
        json={"activate": False, "source_id": "shop-example"},
        headers={"Idempotency-Key": "accept-shop-1"},
    ).json()
    print(accept["job_id"])  # Job.result = AcceptanceResult (опубліковані версії, звіти тестів, чернетки)
```
