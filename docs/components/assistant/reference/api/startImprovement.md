# POST /v1/improvement-runs

> Згенеровано `scripts/docs_reference.py` з [assistant.v1.yaml](../../../../../contracts/openapi/assistant.v1.yaml#L351). Не редагуйте вручну.

**Вдосконалити екстрактор на проблемних прикладах (нова версія або форк)**

| Властивість | Значення |
|---|---|
| operationId | `startImprovement` |
| Метод і шлях | `POST /v1/improvement-runs` |
| Scope | `assistant:use` |
| Ідемпотентність | обов'язковий `Idempotency-Key` |
| Теги | improvement |

LLM отримує вибірку проблем, поточний код, діагностику й успішні приклади. Нова версія проходить нові й попередні тести й перевіряється на всіх прив'язках спільного пакета (або оформлюється форком). Кількість спроб і витрати обмежені `limits.llm`. Якщо пакет заборонено змінювати автоматично — лише пропозиція без публікації. Результат — `Job.result` = ImprovementResult.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `Idempotency-Key` | header | `string` | так | Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований ключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь (заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом — 422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress` (retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`. |

## Тіло запиту

Тип вмісту `application/json`, схема `ImprovementRequest`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `package` | `package-ref` | так | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `package.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `package.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `package.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `source_id` | `string` | ні |  |
| `problem_group_id` | `string` | ні |  |
| `problem_samples` | array of `ProblemSample` | так | мін. елементів `1` |
| `problem_samples[].material` | `material` | ні | Матеріал, отриманий колектором (ТЗ §5): вміст (RAW) і метадані. Кожне отримання — нове спостереження з новим observation_id (ТЗ §11); material_id стабільний для того самого об'єкта джерела; revision описує версію вмісту. Повторна технічна доставка того самого спостереження має той самий observation_id і не створює нових записів. |
| `problem_samples[].material.material_id` | `string` | так | Стабільний ідентифікатор об'єкта в джерелі. Web: 'web:' + sha256(канонічний URL)[:32]; Telegram: 'tg:&lt;channel_id>:&lt;message_id>'. Однаковий для всіх спостережень того самого об'єкта.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `problem_samples[].material.observation_id` | `string` | так | Унікальний ідентифікатор цього отримання (ULID/UUIDv7 — монотонний у межах колектора).; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `problem_samples[].material.source` | `object` | так |  |
| `problem_samples[].material.locator` | `object` | так | Посилання на першоджерело. |
| `problem_samples[].material.fetched_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `problem_samples[].material.published_at` | `string` (date-time) | ні | Час публікації, якщо його надає джерело. |
| `problem_samples[].material.edited_at` | `string` (date-time) | ні | Час редагування, якщо його надає джерело. |
| `problem_samples[].material.format` | `object` | так |  |
| `problem_samples[].material.revision` | `object` | так | Версія вмісту. Однаковий content_sha256 у двох спостереженнях означає незмінений вміст. |
| `problem_samples[].material.content` | `InlineContent` \| `BlobContent` | так | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `problem_samples[].material.attachments` | array of `object` | ні | Додаткові файли (медіа Telegram, PDF за посиланням), кожен як ContentRef з описом. |
| `problem_samples[].material.http` | `object` | ні |  |
| `problem_samples[].material.discovery` | `object` | ні | Як матеріал було знайдено. |
| `problem_samples[].material.collector` | `object` | так |  |
| `problem_samples[].material.diagnostics` | array of `DiagnosticMessage` | ні |  |
| `problem_samples[].material.metadata` | `object` | ні | Додаткові метадані джерела (наприклад title, автор повідомлення, кількість переглядів). Відкритий об'єкт. Telegram: service_action — дія службового повідомлення каналу (channel_create, pin_message, chat_edit_title…); таке повідомлення зазвичай має порожній текст, тож завдання може відфільтрувати його умовою material.metadata.service_action not_exists. |
| `problem_samples[].material_ref` | `MaterialRef` | ні | Посилання на збережений матеріал (storage API) — асистент сам читає вміст. |
| `problem_samples[].material_ref.storage_connection_id` | `string` | так |  |
| `problem_samples[].material_ref.object_id` | `string` | так |  |
| `problem_samples[].result` | `handler-result` | ні | Результат виконання обробника з діагностикою (ТЗ §5, §9). Пов'язаний із вхідними даними (inputs) і точною версією пакета (handler). Чотири стани ТЗ §9: success — успішна обробка; empty — коректна відсутність потрібних сутностей; unrecognized — невідомий або частково розібраний формат; failed — помилка виконання чи невідповідність результату схемі. Помилка обробника — це відповідь 200 зі status=failed; HTTP-помилка означає, що виклик не відбувся. |
| `problem_samples[].result.invocation_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `problem_samples[].result.handler` | `package-ref` | так | Фактично виконана версія (digest заповнено завжди). |
| `problem_samples[].result.handler_kind` | enum: `extractor`, `storage`, `llm`, `transform`, `collector-rules` | так | Тип обробника (і пакета). 'collector-rules' — правила колектора, що версіонуються в тому самому репозиторії. |
| `problem_samples[].result.status` | enum: `success`, `empty`, `unrecognized`, `failed` | так |  |
| `problem_samples[].result.inputs` | array of `InputRef` | так | Посилання на вхідні дані в порядку запиту. |
| `problem_samples[].result.output` | `HandlerOutput` | ні | Вихід за типом обробника: extractor — entities; llm — data (+ usage); storage — writes; transform — data або entities. Великий вихід — через *_ref. |
| `problem_samples[].result.unrecognized` | `object` | ні | Заповнюється, коли status = unrecognized. |
| `problem_samples[].result.failure` | `object` | ні | Заповнюється, коли status = failed. |
| `problem_samples[].result.diagnostics` | `Diagnostics` | ні |  |
| `problem_samples[].result.usage` | `Usage` | ні |  |
| `problem_samples[].result.delivery_key` | `string` | ні |  |
| `problem_samples[].result.duplicate` | `boolean` | ні | true — цей delivery_key уже виконано; повернуто збережений результат без повторного ефекту. |
| `problem_samples[].result.test_mode` | `boolean` | ні |  |
| `problem_samples[].result.started_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `problem_samples[].result.finished_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `problem_samples[].diagnostics` | array of `DiagnosticMessage` | ні |  |
| `problem_samples[].diagnostics[].level` | enum: `debug`, `info`, `warning`, `error` | так |  |
| `problem_samples[].diagnostics[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_.-]{0,127}$"` |
| `problem_samples[].diagnostics[].message` | `string` | так | макс. довжина `4000` |
| `problem_samples[].diagnostics[].pointer` | `string` | ні | JSON Pointer у вихідних даних (наприклад '/entities/3/fields/price'). |
| `problem_samples[].diagnostics[].material_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `problem_samples[].diagnostics[].selector` | `string` | ні | CSS/XPath/JSONPath, з яким пов'язано повідомлення (для екстракторів). |
| `successful_examples` | array of `ProblemSample` | ні |  |
| `successful_examples[].material` | `material` | ні | Матеріал, отриманий колектором (ТЗ §5): вміст (RAW) і метадані. Кожне отримання — нове спостереження з новим observation_id (ТЗ §11); material_id стабільний для того самого об'єкта джерела; revision описує версію вмісту. Повторна технічна доставка того самого спостереження має той самий observation_id і не створює нових записів. |
| `successful_examples[].material.material_id` | `string` | так | Стабільний ідентифікатор об'єкта в джерелі. Web: 'web:' + sha256(канонічний URL)[:32]; Telegram: 'tg:&lt;channel_id>:&lt;message_id>'. Однаковий для всіх спостережень того самого об'єкта.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `successful_examples[].material.observation_id` | `string` | так | Унікальний ідентифікатор цього отримання (ULID/UUIDv7 — монотонний у межах колектора).; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `successful_examples[].material.source` | `object` | так |  |
| `successful_examples[].material.locator` | `object` | так | Посилання на першоджерело. |
| `successful_examples[].material.fetched_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `successful_examples[].material.published_at` | `string` (date-time) | ні | Час публікації, якщо його надає джерело. |
| `successful_examples[].material.edited_at` | `string` (date-time) | ні | Час редагування, якщо його надає джерело. |
| `successful_examples[].material.format` | `object` | так |  |
| `successful_examples[].material.revision` | `object` | так | Версія вмісту. Однаковий content_sha256 у двох спостереженнях означає незмінений вміст. |
| `successful_examples[].material.content` | `InlineContent` \| `BlobContent` | так | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `successful_examples[].material.attachments` | array of `object` | ні | Додаткові файли (медіа Telegram, PDF за посиланням), кожен як ContentRef з описом. |
| `successful_examples[].material.http` | `object` | ні |  |
| `successful_examples[].material.discovery` | `object` | ні | Як матеріал було знайдено. |
| `successful_examples[].material.collector` | `object` | так |  |
| `successful_examples[].material.diagnostics` | array of `DiagnosticMessage` | ні |  |
| `successful_examples[].material.metadata` | `object` | ні | Додаткові метадані джерела (наприклад title, автор повідомлення, кількість переглядів). Відкритий об'єкт. Telegram: service_action — дія службового повідомлення каналу (channel_create, pin_message, chat_edit_title…); таке повідомлення зазвичай має порожній текст, тож завдання може відфільтрувати його умовою material.metadata.service_action not_exists. |
| `successful_examples[].material_ref` | `MaterialRef` | ні | Посилання на збережений матеріал (storage API) — асистент сам читає вміст. |
| `successful_examples[].material_ref.storage_connection_id` | `string` | так |  |
| `successful_examples[].material_ref.object_id` | `string` | так |  |
| `successful_examples[].result` | `handler-result` | ні | Результат виконання обробника з діагностикою (ТЗ §5, §9). Пов'язаний із вхідними даними (inputs) і точною версією пакета (handler). Чотири стани ТЗ §9: success — успішна обробка; empty — коректна відсутність потрібних сутностей; unrecognized — невідомий або частково розібраний формат; failed — помилка виконання чи невідповідність результату схемі. Помилка обробника — це відповідь 200 зі status=failed; HTTP-помилка означає, що виклик не відбувся. |
| `successful_examples[].result.invocation_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `successful_examples[].result.handler` | `package-ref` | так | Фактично виконана версія (digest заповнено завжди). |
| `successful_examples[].result.handler_kind` | enum: `extractor`, `storage`, `llm`, `transform`, `collector-rules` | так | Тип обробника (і пакета). 'collector-rules' — правила колектора, що версіонуються в тому самому репозиторії. |
| `successful_examples[].result.status` | enum: `success`, `empty`, `unrecognized`, `failed` | так |  |
| `successful_examples[].result.inputs` | array of `InputRef` | так | Посилання на вхідні дані в порядку запиту. |
| `successful_examples[].result.output` | `HandlerOutput` | ні | Вихід за типом обробника: extractor — entities; llm — data (+ usage); storage — writes; transform — data або entities. Великий вихід — через *_ref. |
| `successful_examples[].result.unrecognized` | `object` | ні | Заповнюється, коли status = unrecognized. |
| `successful_examples[].result.failure` | `object` | ні | Заповнюється, коли status = failed. |
| `successful_examples[].result.diagnostics` | `Diagnostics` | ні |  |
| `successful_examples[].result.usage` | `Usage` | ні |  |
| `successful_examples[].result.delivery_key` | `string` | ні |  |
| `successful_examples[].result.duplicate` | `boolean` | ні | true — цей delivery_key уже виконано; повернуто збережений результат без повторного ефекту. |
| `successful_examples[].result.test_mode` | `boolean` | ні |  |
| `successful_examples[].result.started_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `successful_examples[].result.finished_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `successful_examples[].diagnostics` | array of `DiagnosticMessage` | ні |  |
| `successful_examples[].diagnostics[].level` | enum: `debug`, `info`, `warning`, `error` | так |  |
| `successful_examples[].diagnostics[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_.-]{0,127}$"` |
| `successful_examples[].diagnostics[].message` | `string` | так | макс. довжина `4000` |
| `successful_examples[].diagnostics[].pointer` | `string` | ні | JSON Pointer у вихідних даних (наприклад '/entities/3/fields/price'). |
| `successful_examples[].diagnostics[].material_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `successful_examples[].diagnostics[].selector` | `string` | ні | CSS/XPath/JSONPath, з яким пов'язано повідомлення (для екстракторів). |
| `bindings` | array of `object` | ні | Усі прив'язки спільного пакета, на яких нова версія має пройти перевірку. |
| `bindings[].task_id` | `string` | так |  |
| `bindings[].stage_id` | `string` | так |  |
| `policy` | `object` | ні |  |
| `policy.approval` | enum: `manual`, `auto_after_checks` | ні | типово `"manual"` |
| `policy.allow_fork` | `boolean` | ні | типово `true` |
| `limits` | `llm` | ні |  |
| `limits.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `limits.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `limits.budget.amount` | `number` | так | мін. `0` |
| `limits.budget.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `limits.budget.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `limits.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `limits.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `limits.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |

Приклад `improve`:

```json
{
  "package": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0"
  },
  "source_id": "shop-example",
  "problem_group_id": "pg_01J9ZW0000000000000000001",
  "problem_samples": [
    {
      "material_ref": {
        "storage_connection_id": "raw-files",
        "object_id": "obj_01J9ZQ4C00000000000000D9"
      },
      "diagnostics": [
        {
          "level": "warning",
          "code": "extract.missing_selector",
          "message": "selector .price matched 0 elements"
        }
      ]
    }
  ],
  "successful_examples": [
    {
      "material_ref": {
        "storage_connection_id": "raw-files",
        "object_id": "obj_01J9ZQ4C00000000000000D1"
      }
    }
  ],
  "bindings": [
    {
      "task_id": "shop-catalog",
      "stage_id": "extract-products"
    },
    {
      "task_id": "shop-price-check",
      "stage_id": "extract-price"
    }
  ],
  "policy": {
    "approval": "manual",
    "allow_fork": true
  },
  "limits": {
    "max_improvement_attempts": 3,
    "budget": {
      "amount": 1,
      "currency": "USD",
      "period": "run"
    }
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `202` | Операцію прийнято до асинхронного виконання. | `job` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |
| `429` | Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`). | `problem` |

### Відповідь 202

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `job_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `kind` | `string` | так | Вид операції в межах сервісу, наприклад 'collection', 'invocation', 'test_run', 'run', 'onboarding', 'improvement', 'upstream_port'.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `progress` | `JobProgress` | ні |  |
| `progress.completed` | `integer` | ні | мін. `0` |
| `progress.total` | `integer \| null` | ні | Відома загальна кількість одиниць; null — невідома (наприклад під час рекурсивного обходу).; мін. `0` |
| `progress.unit` | `string` | ні |  |
| `progress.message` | `string` | ні |  |
| `progress.counters` | `object` | ні | Довільні лічильники, наприклад {"fetched": 10, "skipped_robots": 2}. |
| `progress.updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `result` | `object` | ні | Результат, коли status = succeeded. Форма залежить від 'kind' і описана в API відповідної операції. Великий результат передається як result_ref. |
| `result_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `error` | `problem` | ні | Причина, коли status = failed. Для cancelled причина — у cancellation. |
| `error.type` | `string` (uri-reference) | так | URI типу проблеми: 'urn:jane:problem:&lt;code>'. |
| `error.title` | `string` | так | Короткий людський опис типу проблеми. |
| `error.status` | `integer` | так | мін. `400`; макс. `599` |
| `error.detail` | `string` | ні | Пояснення конкретного випадку. Без секретів і без вмісту матеріалів. |
| `error.instance` | `string` (uri-reference) | ні |  |
| `error.code` | `string` | так | Стабільний машинний код у snake_case. Відомі коди — $defs/KnownErrorCode. Сервіс може додати власний код лише разом з оновленням каталогу в contracts/.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.retryable` | `boolean` | ні | true — ту саму операцію (з тим самим Idempotency-Key) можна безпечно повторити пізніше. |
| `error.retry_after_seconds` | `integer` | ні | Дублює заголовок Retry-After для клієнтів, які читають лише тіло.; мін. `0` |
| `error.errors` | array of `FieldError` | ні | Помилки окремих полів або параметрів (для validation_failed). |
| `error.errors[].pointer` | `string` | ні | JSON Pointer (RFC 6901) до поля тіла запиту, наприклад '/stages/2/handler/version'. |
| `error.errors[].parameter` | `string` | ні | Ім'я query/path/header параметра. |
| `error.errors[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.errors[].message` | `string` | так |  |
| `error.trace_id` | `string` | ні |  |
| `error.details` | `object` | ні | Додаткові структуровані дані, специфічні для коду (наприклад 'limit', 'actual' для limit_exceeded). |
| `cancellation` | `JobCancellation` | ні |  |
| `cancellation.requested_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `cancellation.requested_by` | `string` | ні |  |
| `cancellation.reason` | `string` | ні | макс. довжина `1000` |
| `idempotency_key` | `string` | ні | макс. довжина `255` |
| `links` | `object` | ні | Пов'язані ресурси: self, cancel, result, run, collection тощо. |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |

Приклад `queued`:

```json
{
  "job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "kind": "collection",
  "status": "queued",
  "created_at": "2026-09-27T10:00:00Z",
  "links": {
    "self": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
    "cancel": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F/cancel"
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `422`, `429`.
- Операція асинхронна: `202` повертає job; стан, прогрес і результат — через `GET /v1/jobs/{job_id}`.
