# Assistant: інтеграція

Як користуватися Assistant зі стороннього застосунку чи з Admin UI: підключення джерела, вдосконалення екстрактора, аналіз невідомих матеріалів; як Assistant працює в складі Jane і як його замінити. Усі тривалі операції повертають 202 і job; POST-операції вимагають заголовка `Idempotency-Key`. Повні схеми — [reference/api](reference/api/README.md).

## Зміст

- [Загальні правила](#загальні-правила)
- [Підключення джерела](#підключення-джерела)
- [Вдосконалення екстрактора](#вдосконалення-екстрактора)
- [Невідомий матеріал](#невідомий-матеріал)
- [Списки](#списки)
- [Помилки](#помилки)
- [Композиція в Jane](#композиція-в-jane)
- [Заміна сумісною реалізацією](#заміна-сумісною-реалізацією)

## Загальні правила

- Дозвіл для всіх операцій — `assistant:use`.
- `POST /v1/onboarding-sessions`, `…/acceptance`, `/v1/improvement-runs`, `/v1/unknown-materials` повертають 202 з job і заголовком `Location`; стан — `GET /v1/jobs/{job_id}`, скасування — `POST /v1/jobs/{job_id}/cancel`.
- Повтор з тим самим `Idempotency-Key` і тілом повертає той самий job (`Idempotency-Replayed: true`); інше тіло — 422 `idempotency_key_reused`.
- Поле `limits` запиту — контрактне `limits.llm`: бюджет запуску, спроби, розмір вибірки, поріг впевненості ([configuration.md](configuration.md#група-llm-контракт-limitsllm)).

## Підключення джерела

![Послідовність підключення джерела](../../diagrams/assistant/onboarding-sequence.light.png#gh-light-mode-only)
![Послідовність підключення джерела](../../diagrams/assistant/onboarding-sequence.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/assistant/onboarding-sequence.light.png), [темне](../../diagrams/assistant/onboarding-sequence.dark.png); джерело — [onboarding-sequence.drawio](../../diagrams/assistant/onboarding-sequence.drawio).

### Початок сесії

`POST /v1/onboarding-sessions`:

| Поле | Обов'язкове | Зміст |
|---|---|---|
| `query` | так | URL сайту, `@канал`, `t.me/<канал>` або назва (назва потребує пошукового провайдера) |
| `source_kind` | ні | `web` або `telegram`, якщо з `query` не зрозуміло |
| `expected_entity_types` | ні | які сутності потрібні; аналіз обмежується ними |
| `crawl_hints` | ні | підказки обходу: `scope` (`allowed_domains`, `include_subdomains`, `path_prefixes`, `include`, `exclude`…), `strategies` (обмежують вибірку заданими стратегіями), `limits` (документ `limits.schema.json`; `crawl.max_pages_per_run` може лише зменшити вибірку), `dedup` |
| `limits` | ні | `limits.llm` запуску |
| `auto_activation` | ні | `true` — після аналізу автоматично прийняти рекомендований варіант з активацією; типово `false` |

```json
{"query": "https://shop.example.test/", "expected_entity_types": ["product"], "limits": {"budget": {"amount": 1, "currency": "USD", "period": "run"}}}
```

Відповідь — job з посиланням на сесію в `links.session` (уривок реальної відповіді):

```json
{"job_id": "job_8c52d64d5c7b44cf94f1932f6363364b", "kind": "onboarding", "status": "queued", "links": {"self": "/v1/jobs/job_8c52d64d5c7b44cf94f1932f6363364b", "cancel": "/v1/jobs/job_8c52d64d5c7b44cf94f1932f6363364b/cancel", "session": "/v1/onboarding-sessions/onb_6f19c16f53f34e47809df081fa839c89"}, "labels": {"session_id": "onb_6f19c16f53f34e47809df081fa839c89"}}
```

### Стан сесії

`GET /v1/onboarding-sessions/{session_id}` — головне джерело стану для клієнта: `status`, `candidates`, `selected_candidate_id`, `sample`, `analysis`, `proposals`, `costs`, `job_id`, `error`. Стани й переходи — [internals.md](internals.md#стани-сесії).

- **`needs_disambiguation`** — кілька кандидатів без явного переможця. Виберіть: `POST /v1/onboarding-sessions/{id}/candidate-selection` з `{"candidate_id": "cand_2"}`; відповідь — сесія в `sampling`, роботу продовжує новий job. Повторний вибір того самого кандидата повертає той самий стан; вибір в іншому стані — 409 `conflict`.
- **`insufficient_sample`** — вибірка не дала впевненості в межах лімітів або бюджету; `sample.message` пояснює причину. Збільште `max_onboarding_samples`, бюджет чи уточніть `crawl_hints` і почніть нову сесію.
- **`proposals_ready`** — є варіанти.

Аналіз (`analysis`) містить тип джерела, способи обходу (`discovery_methods`), типи матеріалів з кількістю й прикладами URL і сутності з полями. Кожен варіант (`proposals[]`):

| Поле | Зміст |
|---|---|
| `proposal_id`, `title`, `summary`, `recommended` | ідентифікатор, назва, пояснення, чи рекомендовано |
| `collector_rules` | правила колектора, перевірені `validateRules` колектора |
| `extractors[]` | для кожного типу сутності: `action` (`bind_existing`, `fork`, `create`), пакет, `match_score`, `tested_on_samples` (`passed`, `failed`) |
| `coverage` | оцінка кількості матеріалів і типи сутностей |
| `cost` | `requests_per_run_estimate`, `llm_setup_cost` (витрати сесії), `llm_cost_per_run` |
| `risks[]` | ризики: неперевірені екстрактори, тести на скорочених сторінках, межі обходу |

### Прийняття варіанта

`POST /v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance`:

```json
{"activate": true, "source_id": "shop-example"}
```

`source_id` — опційно, інакше він утворюється з хоста або назви каналу. Job прийняття:

1. Публікує правила колектора й пакети `create`/`fork` у Registry (новий пакет, форк або нова версія) і записує результати тестів.
2. Формує чернетки джерела (`source_draft`) і завдання (`task_drafts`): етап `collect`, етап обробника для кожного екстрактора з прив'язкою за шаблонами URL чи типами вмісту, опційно етап збереження (`JANE_ASSISTANT_DEFAULT_STORAGE_PACKAGE`), ручний розклад, `limits` з `crawl_hints`.
3. Якщо `activate: true`, усі екстрактори пройшли тести, активацію дозволено (`JANE_ASSISTANT_ONBOARDING_ALLOW_ACTIVATION`) і Orchestrator налаштовано: погоджує версії (`approved`) і створює джерело й завдання в Orchestrator.

Результат job: `collector_rules`, `extractors[]` (дія, пакет, звіт тестів), `source_draft`, `task_drafts`, `activated`. Без активації чернетки можна передати Orchestrator вручну. Прийняття можливе лише в `proposals_ready`, інакше 409.

## Вдосконалення екстрактора

`POST /v1/improvement-runs` — нова версія пакета-екстрактора за проблемними прикладами. Приклад тіла з контракту:

```json
{
  "package": {"package_id": "shop-example.product-extractor", "version": "1.2.0"},
  "source_id": "shop-example",
  "problem_group_id": "pg_01J9ZW0000000000000000001",
  "problem_samples": [
    {"material_ref": {"storage_connection_id": "raw-files", "object_id": "obj_01J9ZQ4C00000000000000D9"},
     "diagnostics": [{"level": "warning", "code": "extract.missing_selector", "message": "selector .price matched 0 elements"}]}
  ],
  "successful_examples": [{"material_ref": {"storage_connection_id": "raw-files", "object_id": "obj_01J9ZQ4C00000000000000D1"}}],
  "bindings": [{"task_id": "shop-catalog", "stage_id": "extract-products"}],
  "policy": {"approval": "manual", "allow_fork": true},
  "limits": {"max_improvement_attempts": 3, "budget": {"amount": 1, "currency": "USD", "period": "run"}}
}
```

| Поле | Зміст |
|---|---|
| `package` | версія, яку вдосконалюють; лише пакети `kind: extractor` |
| `problem_samples[]` | зразок `material` inline або `material_ref` у Storage; опційно `result` і `diagnostics` попереднього виклику |
| `successful_examples[]` | приклади, що мають і далі працювати (регресії) |
| `bindings[]` | прив'язки для перевірки; без них — усі завдання, що використовують пакет (з Orchestrator) |
| `policy.approval` | `manual` (типово) або `auto_after_checks` — погодити й активувати на прив'язках |
| `policy.allow_fork` | дозволити форк, якщо нова версія ламає прив'язки інших джерел (типово `true`) |
| `problem_group_id` | група проблем Orchestrator, стан якої оновлюється |

Результат job (`ImprovementResult`):

| `outcome` | Значення |
|---|---|
| `new_version` | опубліковано нову версію пакета |
| `fork_created` | опубліковано версію у форку для цього джерела, бо зміна ламає інші прив'язки |
| `proposal_only` | пакету заборонено автоматичні зміни (`auto_changes_allowed: false`): нічого не опубліковано, `proposal` містить змінені файли, маніфест і diff |
| `unresolved` | жодна спроба не пройшла перевірок, вичерпано бюджет або форк заборонено; `unresolved_reason` пояснює |

Також: `version`, `attempts`, `test_reports[]`, `activated`, `suggested_entity_types` (пропозиція розширити очікувані типи джерела — вирішує користувач), `costs`. Алгоритм — [internals.md](internals.md#вдосконалення).

## Невідомий матеріал

`POST /v1/unknown-materials` — для матеріалу, якому не відповідає жоден обробник. Клієнт передає ефективне значення прапорця джерела чи завдання «Передавати в LLM невідомі сторінки»; Assistant перевіряє його й без нього не викликає модель:

| Поле | Зміст |
|---|---|
| `source_id`, `task_id` | джерело й завдання (рівні бюджету в шлюзі) |
| `forward_unknown_to_llm` | має бути `true`, інакше 403 `access_denied_by_policy` без виклику моделі |
| `material` | матеріал за `material.schema.json` (перевіряється, інакше 422) |
| `limits` | `limits.llm` запуску |

Результат job: `classification` (`material_type`, `confidence`) і `suggestion` (`action` = `new_extractor`, `extend_rules`, `expand_entity_types` або `none`; `details`). Реальний приклад — [quickstart.md](quickstart.md#невідомий-матеріал).

Розбіжність з описом контракту `assistant.v1` («викликає оркестратор лише за увімкненим прапорцем»): у ревізії `48389a3` Orchestrator цю операцію не викликає. Невідомі матеріали він реєструє (`GET /v1/unknown-materials` Orchestrator), а за увімкненого прапорця передає етапу завдання, що читає `unmatched_materials`, — наприклад, етапу LLM. Операцію Assistant викликає сам клієнт.

## Списки

- `GET /v1/onboarding-sessions?limit=&cursor=&status=` — короткий стан сесій, новіші першими; `status` можна повторювати.
- `GET /v1/improvement-runs?limit=&cursor=&package_id=&source_id=&problem_group_id=&status=` — job вдосконалення з `result` для завершених.

Курсор непрозорий; чужий або пошкоджений — 422. Уривок реальної відповіді списку сесій:

```json
{"items": [{"session_id": "onb_123558efc42c430ba6ebdf4140e02dda", "status": "failed", "query": "Shop Example", "created_at": "2026-10-11T10:01:08.717272Z", "job_id": "job_459f1407a09842a491220190990b7498", "error": {"type": "urn:jane:problem:validation_failed", "title": "Validation failed", "status": 422, "detail": "no search provider configured; give an exact URL or @channel", "code": "validation_failed", "retryable": false}, "proposal_count": 0}], "next_cursor": "WyIyMDI2LTEwLTExVDEwOjAxOjA4LjcxNzI3MloiLCJvbmJfMTIzNTU4ZWZjNDJjNDMwYmE2ZWJkZjQxNDBlMDJkZGEiXQ"}
```

## Помилки

Синхронні помилки — `application/problem+json` ([модель помилок](../../../contracts/docs/errors.md)):

| HTTP | `code` | Коли |
|---|---|---|
| 422 | `validation_failed` | тіло не за контрактом, невалідні `limits`, матеріал не за схемою, пошкоджений курсор |
| 403 | `access_denied_by_policy` | `forward_unknown_to_llm: false` |
| 404 | `not_found` | сесію, кандидата чи варіант не знайдено |
| 409 | `conflict` | дія не відповідає стану сесії або сесію змінили паралельно |
| 503 | `service_unavailable` | черга job переповнена |

Помилки під час роботи job (сусід недоступний, бюджет, невалідна відповідь моделі) потрапляють у `error` job і сесії; як їх тлумачити — [dependencies.md](dependencies.md) і [operations.md](operations.md#типові-проблеми).

## Композиція в Jane

- **Admin UI** — сторінки підключення джерела й вдосконалення: створює сесії, показує варіанти, приймає, запускає вдосконалення з групи проблем, відновлює списки після перезавантаження.
- **Orchestrator** — Assistant створює в ньому джерела й завдання, читає прив'язки пакетів, активує й відкочує версії на етапах і оновлює стан груп проблем. У `infra/compose.local.example.yaml` Assistant зареєстровано як виконавця Orchestrator з роллю `assistant`, але код Orchestrator ревізії `48389a3` Assistant не викликає.
- **LLM gateway** — усі виклики моделі з `scope.run_id` запуску: бюджет `period: run` рахується шлюзом атомарно для всіх екземплярів.
- **Registry, колектори, Handler Runtime, Storage** — див. [dependencies.md](dependencies.md).

У dev-стеку Assistant підключено лише до LLM gateway, Handler Runtime і Storage. Для повного підключення джерел скопіюйте `infra/compose.local.example.yaml` в `infra/compose.local.yaml` (поза Git): він додає адреси Registry, Orchestrator і колекторів, а `just up` враховує цей файл. У цій документації стек з `compose.local.yaml` не запускався.

## Заміна сумісною реалізацією

Сумісна реалізація має відповідати `contracts/openapi/assistant.v1.yaml` (і `common.yaml`): 202 і job для тривалих операцій, ідемпотентність, курсорні списки, 403 для невідомого матеріалу без прапорця. Admin UI й Orchestrator звертаються лише до цих операцій. Контрактні тести сервісу — `services/assistant/tests/test_contract.py` (входять у `just test assistant`).

Свої сусіди Assistant викликає строго за їхніми контрактами, тому кожного з них можна замінити сумісною реалізацією; так працюють тести на контрактних фейках (`services/assistant/tests/assistant_fakes/`).
