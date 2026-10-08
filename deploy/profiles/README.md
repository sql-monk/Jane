# Профілі лімітів WP-14

Документи `PlatformLimits` (`contracts/schemas/common/limits.schema.json#/$defs/PlatformLimits`) для
підтримуваних середовищ, стек, що застосовує профіль, і harness вимірювання. [Рішення людини 2026-10-08](../../docs/delivery/WP-14.md#рішення-людини-2026-10-08-і-стан-критерію-13):
наживо прийнято лише `ci`; вимірювання `dev-laptop` ×3 виключено з обсягу, тож `dev-laptop` і `single-node` —
кандидати, **не перевірено на реальному середовищі**.

| Файл | Середовище | Статус |
|---|---|---|
| `dev-laptop.json` | ця машина: Windows 11 + Docker Desktop (6 CPU, 16 ГБ у Docker) | кандидат, **не перевірено на реальному середовищі** (вимірювання виключено рішенням людини 2026-10-08) |
| `ci.json` | GitHub Actions `ubuntu-latest` (4 vCPU, 16 ГБ), лише testsite і fake LLM | **прийнято наживо**, job `limits`: CI [36921026070](https://github.com/sql-monk/Jane/actions/runs/36921026070) `pass`, [36952287098](https://github.com/sql-monk/Jane/actions/runs/36952287098) `warn` без блокерів, останній на `main` — [37811082079](https://github.com/sql-monk/Jane/actions/runs/37811082079) `pass` ([звіт](../../docs/delivery/WP-14.md)) |
| `single-node.json` | одна Linux VM з Docker Compose, орієнтир 8 vCPU / 32 ГБ | кандидат, **не перевірено на реальному середовищі** |
| `thresholds.json` | пороги pass/fail harness для `dev-laptop` і `ci` | [опис](../../docs/operations/limits-validation.md) |
| `compose.stack.yaml`, `stack.py` | ізольований ланцюжок сервісів, профіль — `LIMITS_FILE` усіх сервісів | перевірено відтворенням прикладів і стартом сервісів із профілем |
| `harness/` | `limits_harness.py`, `metrics.py`, `probe_site.py`, пакет `harness.sandbox-probe` | тести без Docker; прогони — CI job `limits` |
| `check.py` | перевірка форми всіх трьох профілів за контрактом | |

Значення профілів — довідкові приклади WP-00 з двома змінами:

- у `dev-laptop` `sandbox.wall_time_ms` 30 000 → 60 000 і `timeouts.invocation_timeout_ms` 60 000 → 90 000, бо
  WP-13 на Docker Desktop зафіксував 30,7 с старту контейнера пісочниці при 1 с роботи екстрактора (e2e WP-13
  працює з 60 с);
- у `ci` бюджет LLM `0 USD / run` → `0.01 USD / day`. Нуль асистент читає як «викликів немає»
  (`spent >= amount` → `budget_exhausted` ще до першого виклику), тож зі змонтованим профілем онбординг не
  працював би навіть із безкоштовним fake-провайдером. `day`, а не `run`: бюджет `run` шлюз llm пропускає для
  викликів без `run_id` (асистент його не передає), а `day` діє завжди. 1 цент на добу пропускає fake-модель
  (ціна 0) і відмовляє платній: резервування одного виклику моделі за 1/5 USD за Mtok — 0,021 USD
  (вивід — у [звіті WP-14](../../docs/delivery/WP-14.md), фаза 2). `dev-laptop` і `single-node` лишають
  `5 USD / day`.

Числа `ci` підтвердили живі прогони job `limits` (таблиця вище); числа `dev-laptop` і `single-node` — довідкові,
не виміряні.

## Команди

```text
uv run --all-packages python deploy/profiles/check.py                                  # форма профілів
uv run --all-packages pytest deploy/profiles -q                                         # тести без Docker
uv run --all-packages python deploy/profiles/stack.py up --profile dev-laptop [--project P] [--telegram] [--probe]
uv run --all-packages python deploy/profiles/stack.py env --project P                  # адреси
uv run --all-packages python deploy/profiles/stack.py down --project P                 # + перевірка залишків
uv run --all-packages python deploy/profiles/harness/limits_harness.py plan --profile dev-laptop
uv run --all-packages python deploy/profiles/harness/limits_harness.py run --profile dev-laptop   # вільна машина!
```

Тести без Docker входять у `just unit` / `just check` (і CI job `unit`) окремою сесією pytest разом з `examples/`
(`EXTRA_UNIT_PATHS` у `scripts/dev.py`); окремо — командою вище. Типи — `uv run --all-packages mypy deploy/profiles`.

## Як профіль доходить до сервісів

1. **Оркестратор** читає `JANE_ORCHESTRATOR_LIMITS_FILE` **лише під час першого заповнення** документа лімітів
   у своїй БД. Далі — `GET /v1/limits/platform`, `PUT /v1/limits/platform` з `If-Match: <ETag>` (право
   `orchestrator:admin`), перевірка — `GET /v1/limits/effective?source_id=&task_id=&stage_id=`. Ефективні ліміти
   етапу (platform → source → task → stage, `hard_caps` зверху) оркестратор передає в кожен виклик колектора
   й обробника, тож runtime і storage отримують `sandbox`, `timeouts` тощо з профілю в запиті.
2. **Web Collector і Telegram Collector** приймають увесь профіль як `JANE_*_LIMITS_FILE` (групи, яких не
   моделюють, ігнорують) — це їхні ліміти й для автономних викликів.
3. **storage, handler-runtime, registry, llm, assistant** з WP-01b теж приймають увесь профіль як
   `JANE_<СЕРВІС>_LIMITS_FILE`: ліміти контракту, які сервіс моделює, беруть значення профілю (`/v1/info` →
   `limits.profile`, `limits.defaults`), решту ігнорують із рядком журналу старту
   `platform limits profile applied partially`; опечатка в профілі — `LimitError`, сервіс не стартує. Значення
   з запитів оркестратора й надалі звужуються стелями (`hard_caps`) профілю.

`compose.stack.yaml` робить саме це: монтує профіль як `LIMITS_FILE` у **всі** сервіси застосунку (orchestrator,
колектори, storage, handler-runtime, registry, llm, assistant), генерує виконавців оркестратора
(`.jane/executors-<проєкт>.json`) лише для запущених сервісів і налаштовує registry ↔ runtime ↔ колектори.
Нові ліміти діють для **нових** запусків. Обмеження сайту, провайдера й `hard_caps` можуть лише звузити профіль.

**Тайм-аут виклику LLM.** llm оголошує `provider.connect_timeout_ms`, `provider.request_timeout_ms` і
`provider.retries` як контрактні `timeouts.*` / `retries`, тож профіль (тайм-аут запиту 30 с — для
веб-завантажень) інакше обмежив би кожен виклик моделі 30 с замість типових 120 с сервісу. Стек перекриває лише
`JANE_LLM_LIMITS__PROVIDER__REQUEST_TIMEOUT_MS` значенням `JANE_LLM_PROVIDER_REQUEST_TIMEOUT_MS` (типово
120 000 — власне типове значення llm). `timeouts.request_timeout_ms` профілів **не** піднято: це послабило б
веб-завантаження колекторів. Підключення (`provider.connect_timeout_ms` 10 с) і повтори (3 спроби) llm бере з
профілю. Остаточну семантику `provider.*` вирішує WP-10 (запит у звіті WP-14). Асистент викликає llm синхронно
з власним `clients.request_timeout_ms` (30 с і в профілі, і типово) — довший виклик моделі він обірве раніше
(запит до WP-11).

| Змінна стеку | Типово | Що |
|---|---|---|
| `JANE_LLM_PROVIDER_REQUEST_TIMEOUT_MS` | `120000` | тайм-аут одного виклику провайдера LLM у стеку профілю |
| `JANE_ORCHESTRATOR_SCHEDULER_ENABLED` / `JANE_ORCHESTRATOR_RUN_WORKERS` | `true` / `true` | `false` у середовищі `stack.py up` — оркестратор без розкладів / воркерів ([резервування й відновлення](../../docs/operations/backup-restore.md)) |

Профіль `ci` має довідкову частоту 50 запитів/с на хост — лише для локального testsite в ізольованій мережі.
Для будь-якого реального сайту задайте нижчу межу на рівні джерела; профіль не є дозволом на таку частоту.
