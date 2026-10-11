# Assistant: експлуатація

Запуск у dev-стеку, моніторинг, журнали, оновлення, резервування, масштабування й типові проблеми Assistant. Команди перевірено 2026-10-11 на Windows 11 з Docker Desktop 29.8, ревізія `48389a3`; на Linux не перевірялися.

## Зміст

- [Запуск у dev-стеку](#запуск-у-dev-стеку)
- [Моніторинг](#моніторинг)
- [Журнали](#журнали)
- [Оновлення й міграції](#оновлення-й-міграції)
- [Резервування й відновлення](#резервування-й-відновлення)
- [Масштабування](#масштабування)
- [Власність даних](#власність-даних)
- [Тести](#тести)
- [Типові проблеми](#типові-проблеми)

## Запуск у dev-стеку

Профіль `assistant` піднімає Assistant разом із LLM gateway і PostgreSQL. Assistant отримує власну базу `jane_assistant`, ключ доступу до шлюзу й адреси LLM gateway, Handler Runtime і Storage.

```powershell
just up --project jane-doc-llm llm assistant
```

Уривок виводу (порти задано змінними `JANE_PORT_POSTGRES`, `JANE_PORT_LLM`, `JANE_PORT_ASSISTANT`; без них порти обирає Docker):

```text
 Container jane-doc-llm-assistant-1 Healthy 

project: jane-doc-llm   (stack file: .jane/stack-jane-doc-llm.json)
  postgres   127.0.0.1:18540
  llm        http://127.0.0.1:18541
  assistant  http://127.0.0.1:18542
  db-assistant postgresql://127.0.0.1:18540/jane_assistant
```

`capabilities` з `GET /v1/info` (з ключем адміністратора з `just env`) у цьому стеку:

```json
{"operations": ["onboarding", "improvement", "unknown_materials"], "search_provider": "none", "neighbours": {"llm": true, "registry": false, "collector_web": false, "collector_telegram": false, "handler_runtime": true, "orchestrator": false, "storage": true}, "local_schema_validation": true, "state": "postgresql"}
```

Registry, колектори й Orchestrator у базовому стеку не підключено — додайте `infra/compose.local.yaml` за зразком `infra/compose.local.example.yaml`. Handler Runtime і Storage в цьому запуску не стартували: Assistant знає їхні адреси, але звернення до них завершилися б `upstream_unavailable`.

Таблиці стану, створені під час старту:

```powershell
docker exec jane-doc-llm-postgres-1 psql -U jane -d jane_assistant -c '\dt jane_assistant.*'
```

```text
                    List of tables
     Schema     |    Name     | Type  |     Owner      
----------------+-------------+-------+----------------
 jane_assistant | idempotency | table | jane_assistant
 jane_assistant | jobs        | table | jane_assistant
 jane_assistant | sessions    | table | jane_assistant
(3 rows)
```

Прибирання: команда нижче зупиняє стек і **видаляє всі його дані** — томи баз, локально зібрані образи й файл `.jane/stack-jane-doc-llm.json` зі згенерованими паролями.

```powershell
just down -v --project jane-doc-llm
```

## Моніторинг

| Точка | Що показує |
|---|---|
| `GET /v1/health` | `ok` або `down` (HTTP 503); перевірка `state` — доступність сховища стану |
| `GET /v1/info` | `capabilities.neighbours` (які сусіди налаштовані), `search_provider`, `local_schema_validation`, `state`; ефективні контрактні ліміти |
| `GET /metrics` | загальні HTTP-метрики `jane_http_*`; власних метрик Assistant немає |
| `GET /v1/onboarding-sessions?status=…` | сесії за станами, зокрема `failed` і `insufficient_sample` з причинами |
| `GET /v1/improvement-runs?status=failed` | невдалі запуски вдосконалення |

Витрати Assistant на моделі видно в LLM gateway: `GET /v1/usage?group_by=purpose` (мета `onboarding`, `improvement`, `unknown_material`). Перевірка `state` не охоплює сусідів: їхню доступність показують помилки job.

## Журнали

Журнал — JSON (`JANE_ASSISTANT_LOG_FORMAT=json`) або текст (`console`). Ключові записи:

| Повідомлення | Рівень | Значення |
|---|---|---|
| `configured limits` | INFO | ефективні ліміти й шлях до `contracts/schemas` |
| `crawl_hints.limits ignored` | INFO | ліміти з `crawl_hints` не відповідають схемі й не застосовані |
| `proposal rules invalid` | INFO | варіант відкинуто: правила не пройшли перевірку |
| `generated package not tested` | WARNING | архів згенерованого пакета більший за `transfer.inline_max_bytes` |
| `problem group not updated` | WARNING | Orchestrator не прийняв оновлення групи проблем |
| `binding task not readable` | WARNING | завдання прив'язки не прочиталося |
| `expected entity types not read from the orchestrator` | WARNING | порада для невідомого матеріалу без очікуваних типів |
| `rollback failed` | ERROR | не вдалося відкотити активацію на прив'язці — потрібне ручне втручання |
| `state heartbeat failed` | WARNING | не вдалося оновити оренди в PostgreSQL |

Вміст матеріалів і відповіді моделі в журнал не пишуться.

## Оновлення й міграції

- Таблиці стану створюються й доповнюються під час старту (міграція jane-kit під advisory-блокуванням `jane-assistant-<схема>`). Окремої команди міграції немає.
- Під час штатної зупинки екземпляр скасовує свої job і записує причину; сесії цих job стають `cancelled`. Перед оновленням дочекайтеся завершення активних сесій (`GET /v1/onboarding-sessions?status=sampling&status=analyzing&status=applying`) або попередьте користувачів.
- Після оновлення Assistant із новими лімітами чи промптами старі сесії не перераховуються; нова поведінка діє для нових запусків.

Загальний порядок — [оновлення](../../operations/upgrades.md).

## Резервування й відновлення

Дані — схема `jane_assistant` (сесії, job, ключі ідемпотентності). Резервна копія — `pg_dump` схеми. Без копії втрачаються незавершені сесії та історія; результати прийнятих варіантів лишаються в Registry й Orchestrator. Процедуру для платформи — [резервування й відновлення](../../operations/backup-restore.md). У цій документації резервування схеми не виконувалося.

## Масштабування

- **Кілька екземплярів** — лише з `JANE_ASSISTANT_STATE_DSN`: будь-який екземпляр читає й продовжує сесію чи job іншого, переходи сесії захищені оптимістичною версією, job — орендами. Перевіряють інтеграційні тести `services/assistant/tests/test_state.py`.
- **Без PostgreSQL** — один екземпляр; стан зникає під час перезапуску.
- Навантаження визначають сусіди: тривалість вибірки — швидкість колектора й ліміти хоста; вартість — модель. Паралельність одного екземпляра — `jobs.max_concurrent_jobs`.

Загальні правила — [масштабування](../../operations/scaling.md).

## Власність даних

Assistant володіє лише своїм станом. Пакети й правила, які він створює, належать Registry; джерела, завдання, активації й групи проблем — Orchestrator; витрати на моделі обліковує LLM gateway. Карта платформи — [власність даних](../../architecture/data-ownership.md).

## Тести

| Команда | Що перевіряє | Результат 2026-10-11 |
|---|---|---|
| `just test assistant` | unit, сценарії на контрактних фейках, процесний e2e, контрактні тести | 131 passed, 9 deselected |
| `just test assistant -k process_e2e` | повний цикл окремим процесом | 1 passed |
| `just integration --project jane-doc-llm services/assistant` | стан у PostgreSQL, кілька екземплярів | 9 passed |

## Типові проблеми

| Симптом | Причина | Що зробити |
|---|---|---|
| сесія `failed`, `upstream_unavailable`: `collector is not configured for the assistant` | адресу колектора не задано | `JANE_ASSISTANT_COLLECTOR_WEB_URL` або `…_TELEGRAM_URL` |
| job `failed`: `LLM request failed: HTTP 404: not_found` | у LLM gateway немає псевдоніма `cheap` чи `strong` | `PUT /v1/model-aliases/cheap` і `…/strong` у шлюзі |
| job `failed` з `upstream_unavailable`, у `detail` — HTTP 401 або 403 від шлюзу | токен Assistant не прийнято шлюзом або без дозволу `llm:invoke` | `JANE_ASSISTANT_SERVICE_TOKEN_REF` і ключ з `llm:invoke` у шлюзі |
| сесія `failed`, `validation_failed`: `no search provider configured` | назва замість URL без пошукового провайдера | URL або `@канал`, або `JANE_ASSISTANT_SEARCH_PROVIDER` |
| сесія `insufficient_sample` | впевненість нижча за поріг у межах вибірки чи бюджету; збір не завершився | `sample.message`; більше `max_onboarding_samples`, бюджет, точніші `crawl_hints` |
| `activated: false` після `activate: true` | не всі екстрактори пройшли тести, Orchestrator не налаштовано або активацію вимкнено | `extractors[].test_report`, `JANE_ASSISTANT_ORCHESTRATOR_URL`, `JANE_ASSISTANT_ONBOARDING_ALLOW_ACTIVATION` |
| вдосконалення `unresolved` | спроби не пройшли перевірок, бюджет, форк заборонено | `unresolved_reason`, `test_reports` |
| 403 `access_denied_by_policy` | `forward_unknown_to_llm: false` | увімкніть прапорець у джерелі чи завданні |
| `local_schema_validation: false` | не знайдено `contracts/schemas` | `JANE_ASSISTANT_CONTRACTS_DIR` |
| сервіс не стартує після зміни пошуку | `static` без файла або `http_json` без шаблону URL | задайте `…_SEARCH_STATIC_FILE` або `…_SEARCH_URL_TEMPLATE` |
