# LLM — шлюз і LLM-обробник

Сервіс `llm` (WP-10) — єдина точка звернення платформи до LLM:

- **шлюз** за [`contracts/openapi/llm.v1.yaml`](../../contracts/openapi/llm.v1.yaml): провайдери й моделі,
  псевдоніми моделей (`default`, `cheap`, `strong`), структуровані запити з валідацією виходу за JSON Schema,
  бюджети й ліміти частоти на рівнях platform → source → task, облік витрат;
- **LLM-обробник** за спільним протоколом [`handler.v1.yaml`](../../contracts/openapi/handler.v1.yaml)
  (`/v1/invocations`, `/v1/test-runs`, `/v1/connections`): виконує пакети типу `llm` (маніфест + промпти +
  схеми, коду немає). Приклад пакета — [`packages/jane.llm-event-extractor`](packages/jane.llm-event-extractor/).

Сервіс працює без оркестратора: усе потрібне приходить у запиті (пакет, вхідні дані, ліміти, scope).

## Незалежний запуск

Без Docker (з кореня репозиторію). Стан (бюджети, облік, провайдери, підключення, ключі ідемпотентності, job)
зберігається в PostgreSQL — у власній схемі сервісу (`JANE_LLM_DB_SCHEMA`, типово `llm`):

```
uv sync --all-packages
just up --project jane-wp10 postgres          # або будь-який PostgreSQL
# DSN — з `just env --project jane-wp10` (JANE_STACK_POSTGRES_DSN); пароль не комітьте
export JANE_LLM_DATABASE_URL=postgresql://...
uv run --package jane-llm python -m jane_llm  # http://127.0.0.1:8110
curl http://127.0.0.1:8110/v1/health
```

Для демонстрації без БД: `JANE_LLM_STORE=memory` (стан у пам'яті процесу — лише один екземпляр і тести).

У Docker (контекст збірки — корінь репозиторію):

```
docker build -f services/llm/Dockerfile -t jane-llm .
docker run --rm -p 8110:8110 -e JANE_LLM_DATABASE_URL=postgresql://... jane-llm
```

**Кілька екземплярів:** запустіть кілька процесів/контейнерів з однаковими `JANE_LLM_DATABASE_URL` і
`JANE_LLM_DB_SCHEMA`. Бюджети, облік витрат, ліміти частоти, ключі ідемпотентності, результати викликів і
job — у спільному PostgreSQL, не в пам'яті процесу; перевірку бюджету й резервування виконує одна транзакція з
`SELECT … FOR UPDATE` на рядках лічильників, тож разом екземпляри не перевитрачають бюджет
(`tests/test_multi_instance.py` — два справжні процеси). Схема створюється при старті (під advisory lock).

## Тести

```
just test llm                                              # unit + contract (memory store)
just up --project jane-wp10 postgres
just integration --project jane-wp10 services/llm          # ті самі сценарії на PostgreSQL + 2 процеси
just down -v --project jane-wp10
```

| Файл | Що перевіряє |
|---|---|
| `tests/test_budget.py` | **Перевищення бюджету зупиняє виклики**: 429 `budget_exhausted` без звернення до провайдера; бюджет платформи з конфігурації; бюджет запиту лише звужує; повтор з тим самим `Idempotency-Key` не витрачає бюджет удруге; LLM-обробник повертає `failed/budget_exhausted` і не кешує його під ключем доставки |
| `tests/test_injection.py` | **Ін'єкція у вмісті не змінює поведінку** (див. нижче) |
| `tests/test_multi_instance.py` | два процеси сервісу з одним PostgreSQL: спільний бюджет під конкурентним навантаженням, спільний облік і ідемпотентність |
| `tests/test_contract.py` | усі операції `llm.v1` і `handler.v1` через `ContractClient` (запити й відповіді за схемами) |
| `tests/test_service.py` | повтори за схемою, 502 з вивільненням резерву, ліміти частоти й токенів, тести пакета через `/v1/test-runs`, простежуваність результату, seed-файл, публікація в registry (мок з контракту), завантаження пакета з registry з перевіркою дайджесту, адаптер Anthropic проти локального замінника API |
| `tests/test_units.py` | промпт і розмежувачі, фейкова модель, вікна бюджетів, розв'язання секретів, семантика резервувань |

Фікстура `store_kind` проганяє кожен сценарій на `memory` і (з маркером `integration`) на PostgreSQL.

## Захист від ін'єкцій: як тест доводить його

Вміст джерел — дані, не інструкції (ТЗ §11):

1. **Канали.** Довірені `instructions` (від викликача чи пакета) і преамбула платформи йдуть лише в системний
   канал провайдера; недовірені `data` — лише в канал користувача, кожна частина між розмежувачами
   `<<<JANE-DATA <nonce> …>>>` / `<<<JANE-END <nonce>>>>`. Nonce — 128 випадкових біт на кожен запит, його
   оголошено в системному каналі. Шаблон входу пакета після підстановки вмісту теж іде як дані.
2. **Нейтралізація.** Будь-яке `<<<` у даних замінюється (`‹‹‹`), тож дані не можуть підробити розмежувач,
   навіть знаючи nonce.
3. **Вихід** перевіряється за схемою; шлюз не має інструментів і не виконує дій з відповіді; підказка для
   повтору за схемою містить лише JSON-вказівники й ключові слова схеми, без значень з даних; секретів у
   промптах немає.

**Чому тест змістовний.** Фейковий провайдер `fake` навмисно моделює **слухняну** модель
([`providers/fake.py`](src/jane_llm/providers/fake.py)): він, як модель, читає nonce із системного каналу,
вважає даними лише текст між *точними* розмежувачами з цим nonce, а все інше — інструкціями, і **виконує**
фразу `ignore previous instructions … {json}` в інструкціях (відповідає цим JSON). Тож:

| Випадок у `tests/test_injection.py` | Очікування | Що доводить |
|---|---|---|
| корисне навантаження в `instructions` (контроль) | фейк відповідає JSON атакувальника | фейк слухняний, навантаження дієве |
| наївний промпт — дані просто дописано в текст (контроль) | фейк захоплено | без розділення атака працює |
| підроблений розмежувач із *справжнім* nonce без нейтралізації (контроль) | фейк захоплено | нейтралізація `<<<` несуча |
| те саме навантаження **в даних через шлюз**: просто текстом, як «SYSTEM MESSAGE», з підробленим розмежувачем і вгаданим nonce, з підробленим розмежувачем і **злитим** nonce (тестова фабрика nonce) | відповідь така сама, як без навантаження (`product`) | шлюз тримає вміст у каналі даних |
| LLM-обробник: матеріал з ін'єкцією | ті самі сутності, що й для чистого матеріалу, без `HACKED` | захист діє й у ланцюжку |

Пакет `jane.llm-event-extractor` містить тест `prompt-injection-is-data` (очікується `empty`).

## Конфігурація

Змінні середовища з префіксом `JANE_LLM_`:

| Змінна | Типово | Опис |
|---|---|---|
| `JANE_LLM_HOST` / `JANE_LLM_PORT` | `127.0.0.1` (у контейнері `0.0.0.0`) / `8110` | адреса |
| `JANE_LLM_STORE` | `postgres` | `postgres` або `memory` (лише тести/демо) |
| `JANE_LLM_DATABASE_URL` | — | DSN PostgreSQL (обов'язковий для `postgres`) |
| `JANE_LLM_DB_SCHEMA` | `llm` | власна схема сервісу |
| `JANE_LLM_SEED_FILE` | — | YAML/JSON з провайдерами, псевдонімами, підключеннями, бюджетами (створюються лише відсутні), приклад — [`config/seed.example.yaml`](config/seed.example.yaml) |
| `JANE_LLM_FAKE_PROVIDER_ENABLED` | `true` | реєструвати провайдера `fake` і псевдонім `default` → `fake/fake-deterministic-1` (якщо `default` ще не задано) |
| `JANE_LLM_PACKAGES_DIR` | вбудований `services/llm/packages` | локальні LLM-пакети (`<dir>/**/jane-package.json`) |
| `JANE_LLM_REGISTRY_URL` / `JANE_LLM_REGISTRY_TOKEN` | — | репозиторій обробників для пакетів за `handler` (архів `…/archive`) |
| `JANE_LLM_LOG_LEVEL` / `JANE_LLM_LOG_FORMAT` | `INFO` / `json` | журнали |
| `JANE_LLM_AUTH_MODE` | `none` | значення для `/v1/info` (перевірка токенів у цьому WP не реалізована, див. звіт) |
| `JANE_LLM_LIMITS_FILE` | — | файл `PlatformLimits` (`defaults`, `hard_caps`) |
| `JANE_LLM_LIMITS__<ГРУПА>__<ПАРАМЕТР>` | — | перевизначення, напр. `JANE_LLM_LIMITS__LLM__BUDGET__AMOUNT=5` |
| `JANE_LLM_LIMITS__HARD_CAPS__…` | — | жорсткі стелі платформи |

**Провайдери й підключення.** Провайдер (`PUT /v1/providers/{id}`) має `kind` (`fake`, `anthropic`), моделі з
цінами й `connection_id`. Підключення (`PUT /v1/connections/{id}`, `kind: llm_provider`) містить лише несекретні
`params` і `secret_refs` (`env:VAR`, `file:/run/secrets/x`); значення розв'язує цей сервіс у своєму середовищі,
через API вони не проходять і в БД не зберігаються; `params`, схожі на секрети, відхиляються (`secret_detected`).
`POST /v1/connections/{id}/test` показує `secrets_resolved` без значень.

- **`anthropic`** — Anthropic Messages API через офіційний SDK `anthropic`: `params.api_base` (необов'язково),
  `secret_refs.api_key`; структурований вихід — `output_config.format` (JSON Schema) для моделей з
  `supports_structured_output`. Моделі й ціни за замовчуванням — з конфігурації (seed), приклад:
  `claude-opus-5` ($5/$25 за 1M токенів), `claude-haiku-4-5` ($1/$5). **Не перевірено на реальному сервісі**
  (ключа немає); форма запиту перевірена проти локального замінника API.
- **`fake`** — детермінований провайдер для тестів цього й інших WP. Відповідь: ін'єкція в інструкціях (див.
  вище) → перший збіг зі скриптів підключення (`params.responses: [{when_data_contains | when_data_matches,
  output | output_text | error: unavailable|rejected}]`) → мінімальне значення, що відповідає схемі →
  `fake:<sha256>`. Токени — `ceil(символи / 4)`. Ціни задаються в моделі провайдера (типово 0).

## Ліміти

Рівні: типові значення сервісу → платформа (файл, змінні середовища) → запит (автономний режим), `hard_caps`
обмежують результат. `GET /v1/info` → `limits` (поля з `limits.schema.json`).

| Параметр | Типово | Опис |
|---|---|---|
| `llm.budget` | 10 USD / day | бюджет платформи, якщо немає збереженого `PUT /v1/budgets/platform/platform` |
| `llm.max_requests_per_minute` | 60 | викликів провайдерів на хвилину для всієї платформи (усі екземпляри) |
| `llm.max_input_tokens_per_request` | 100000 | оцінка вхідних токенів понад це — 422 `limit_exceeded` |
| `llm.max_output_tokens_per_request` | 4096 | верхня межа `max_output_tokens` |
| `gateway.default_max_output_tokens` | 1024 | якщо ні запит, ні пакет не задали |
| `gateway.max_schema_retries` | 1 | типове й максимальне число повторів при виході не за схемою |
| `gateway.chars_per_token_estimate` | 3.0 | консервативна оцінка вхідних токенів для резерву бюджету |
| `gateway.reservation_ttl_seconds` | 900 | резерв старший за це (екземпляр упав під час виклику) списується за оцінкою |
| `gateway.max_data_part_bytes` | 2000000 | найбільша частина даних (вміст матеріалу, архів пакета) |
| `provider.connect_timeout_ms` / `provider.request_timeout_ms` | 5000 / 120000 | тайм-аути викликів провайдера (контракт `timeouts.*`) |
| `provider.retries.max_attempts` | 2 | спроби виклику провайдера (контракт `retries`) |
| `registry.connect_timeout_ms` / `request_timeout_ms` / `max_attempts` | 5000 / 30000 / 3 | виклики репозиторію обробників |
| `jobs.max_concurrent_jobs` / `max_queued_jobs` / `job_timeout_ms` | 4 / 1000 / 3600000 | асинхронні job (jane-kit) |
| `idempotency.idempotency_ttl_seconds` | 86400 | скільки пам'ятається `Idempotency-Key` (контракт `transfer.idempotency_ttl_seconds`) |

**Бюджети.** Бюджет платформи — збережене визначення або `llm.budget`; бюджети джерела й завдання — лише
визначені через `PUT /v1/budgets/{scope_type}/{scope_id}` (оркестратор синхронізує сюди `llm.budget` джерел і
завдань); `limits.llm.budget` запиту звужує найконкретніший рівень запиту (`min` зі збереженим). Scope
запиту — `scope.source_id/task_id/run_id` (для обробника — з `context.trace`). Перед **кожним** викликом
провайдера резервується найгірша оцінка вартості (оцінка вхідних токенів + `max_output_tokens` за ціною моделі);
виклик відбувається лише якщо `витрачено + зарезервовано + оцінка ≤ ліміт` для кожного застосовного бюджету,
інакше 429 `budget_exhausted` (з `details` і `Retry-After` до скидання періоду) і провайдер не викликається.
Після виклику резерв замінюється фактичною вартістю. Періоди: `day`/`week`/`month` (UTC), `total`, `run` (за
`run_id`). `status.exhausted` у `/v1/budgets` означає «витрачено ≥ ліміту»; виклики зупиняються раніше, якщо
наступна оцінка не вміщується. Витрати `test_mode` рахуються в тому самому бюджеті й позначаються в обліку.
`max_requests_per_minute` застосовується до платформи, джерела, завдання (з визначень) і провайдера
(`Provider.limits`).

## LLM-обробник

`POST /v1/invocations` (заголовок `Idempotency-Key` = `delivery.delivery_key`; якщо заголовка немає —
використовується `delivery_key`). Пакет: `package_archive` (inline base64 zip або `file://`/`download_url`) →
локальний каталог → registry; `handler.digest` перевіряється (`digest_mismatch`). Для кожного входу — один
структурований запит: інструкції пакета → системний канал, вхід (метадані й вміст матеріалу або заповнений
`input_template`) → дані. Вихід — `output.data`; для кожного `output.entities[]` маніфесту з типом `T` елементи
масиву `T + "s"` (або `T`) стають сутностями; ключові поля `message`/`material`/`material_id` беруться з
`material_id`; `observation` — з матеріалу; поля валідуються за схемою сутності. Стани: `success`, `empty`,
`failed` (`schema_mismatch`, `budget_exhausted`, `invalid_params`). Повтор доставки — збережений результат із
`duplicate: true`; `failed/budget_exhausted` під ключем не зберігається (повторна доставка після збільшення
бюджету виконається). `POST /v1/test-runs` — тести маніфесту й `extra_cases` у `test_mode` (job → `TestReport`).

**Публікація пакета** (registry.v1, WP-05):

```
uv run --package jane-llm python -m jane_llm.packages digest services/llm/packages/jane.llm-event-extractor
uv run --package jane-llm python -m jane_llm.packages publish services/llm/packages/jane.llm-event-extractor --registry http://127.0.0.1:8105
```

## Приклад виклику зі стороннього застосунку

```python
import uuid
import httpx

with httpx.Client(base_url="http://127.0.0.1:8110") as client:
    r = client.post(
        "/v1/completions",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json={
            "model": "default",
            "instructions": "Classify the page type.",
            "data": [{"name": "page", "media_type": "text/html", "text": "<h1>Kettle A-100</h1>"}],
            "output_schema": {
                "type": "object",
                "required": ["page_type"],
                "properties": {"page_type": {"enum": ["product", "category", "article", "other"]}},
            },
            "scope": {"purpose": "other", "task_id": "my-task"},
        },
    )
    if r.status_code == 429:
        print(r.json()["code"])  # budget_exhausted | rate_limited
    else:
        result = r.json()
        print(result["valid"], result["output"], result["usage"]["cost"])
```

## Спостережуваність

- `GET /v1/health` (перевірка `store`), `GET /v1/info` (можливості: `handler_kinds`, `provider_kinds`, ліміти).
- `GET /metrics` — Prometheus: HTTP-метрики jane-kit, `jane_llm_requests_total{provider,model,outcome}`,
  `jane_llm_budget_rejections_total{scope_type}`.
- Журнали — JSON у stdout з `trace_id`, `request_id`, `job_id`; запис `completion` — провайдер, модель,
  токени, вартість, `test_mode`, тривалість (без вмісту даних і секретів).
- Помилки — `application/problem+json` (`budget_exhausted`, `rate_limited`, `upstream_unavailable`,
  `limit_exceeded`, `secret_detected`, `digest_mismatch`, …).
