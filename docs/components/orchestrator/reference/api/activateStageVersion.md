# POST /v1/tasks/{task_id}/stages/{stage_id}/activations

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L539). Не редагуйте вручну.

**Активувати версію пакета в етапі (або відкотити до попередньої)**

| Властивість | Значення |
|---|---|
| operationId | `activateStageVersion` |
| Метод і шлях | `POST /v1/tasks/{task_id}/stages/{stage_id}/activations` |
| Scope | `orchestrator:write`, `orchestrator:admin` |
| Ідемпотентність | обов'язковий `Idempotency-Key` |
| Теги | tasks |

Змінює `stages[].handler` завдання з аудитом. Для етапу `kind: collect` активується версія **правил колектора** (ТЗ §8, §10): змінюється `stages[].collector.rules`, пакет має бути `kind: collector-rules` (інакше 422); `previous` — правила етапу або, якщо етап їх не задавав, `Source.collector_rules` джерела (після активації чи відкату етап явно посилається на версію).
- `activate` — людина активує версію; версія має бути `approved` у репозиторії.
- `rollback` — повернення до попередньої активації (або до вказаної версії).
- `auto_activate` — автоматична активація (асистент після перевірок). Приймається лише якщо політика дозволяє: `Source.change_policy.llm_versions = auto_after_checks` **і** пакет має `auto_changes_allowed = true` **і** версія пройшла тести на всіх прив'язках: агрегат registry `PackageVersion.test_summary.status = passed` (останній звіт кожного `context` пройшов); якщо registry не віддає `test_summary` — `test_status = passed`. Інакше — 403 `access_denied_by_policy` (у `details.reason`: `source_policy`, `package_auto_changes_forbidden` або `tests_not_passed`), активація не виконується.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `task_id` | path | `string` | так |  |
| `stage_id` | path | `string` | так |  |
| `Idempotency-Key` | header | `string` | так | Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований ключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь (заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом — 422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress` (retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`. |

## Тіло запиту

Тип вмісту `application/json`, схема `ActivationRequest`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `kind` | enum: `activate`, `rollback`, `auto_activate` | так | auto_activate приймається лише за дозволу політики джерела й пакета (інакше 403 access_denied_by_policy). |
| `package` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `package.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `package.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `package.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `reason` | `string` | ні | макс. довжина `2000` |

Приклад `activate`:

```json
{
  "kind": "activate",
  "package": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0",
    "digest": "sha256:0f4c1c8f3e0f6a7d9b2c4e6f8a0b2c4d6e8f0a1b3c5d7e9f1a3b5c7d9e1f3a5b"
  },
  "reason": "tests passed on all bindings"
}
```

Приклад `rollback`:

```json
{
  "kind": "rollback",
  "reason": "regression on category pages"
}
```

Приклад `autoActivate`:

```json
{
  "kind": "auto_activate",
  "package": {
    "package_id": "shop-example.product-extractor",
    "version": "1.3.0"
  },
  "reason": "assistant improvement job_01J9ZX0000000000000000IMP passed tests on 2 bindings"
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Активацію виконано. | `Activation` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `403` | Автоактивацію заборонено політикою (`access_denied_by_policy`) або бракує scope (`forbidden`). | `problem` |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `activation_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `task_id` | `string` | так |  |
| `stage_id` | `string` | так |  |
| `package` | `package-ref` | так | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `package.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `package.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `package.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `previous` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `previous.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `previous.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `previous.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `kind` | enum: `activate`, `rollback`, `auto_activate` | так |  |
| `reason` | `string` | ні |  |
| `activated_by` | `string` | ні |  |
| `activated_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |

Приклад `activated`:

```json
{
  "activation_id": "act_01J9ZV0000000000000000001",
  "task_id": "shop-catalog",
  "stage_id": "extract-products",
  "package": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0"
  },
  "previous": {
    "package_id": "shop-example.product-extractor",
    "version": "1.1.0"
  },
  "kind": "activate",
  "reason": "tests passed on all bindings",
  "activated_by": "admin@example.org",
  "activated_at": "2026-09-27T10:20:00Z"
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `403`, `409`, `422`.
