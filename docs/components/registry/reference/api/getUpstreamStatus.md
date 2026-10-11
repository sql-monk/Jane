# GET /v1/packages/{package_id}/upstream

> Згенеровано `scripts/docs_reference.py` з [registry.v1.yaml](../../../../../contracts/openapi/registry.v1.yaml#L680). Не редагуйте вручну.

**Оновлення батьківського пакета для форку**

| Властивість | Значення |
|---|---|
| operationId | `getUpstreamStatus` |
| Метод і шлях | `GET /v1/packages/{package_id}/upstream` |
| Scope | `registry:read` |
| Ідемпотентність | — |
| Теги | forks |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `package_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Стан відносно батька. | `UpstreamStatus` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `409` | Пакет не є форком (`conflict`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `fork_of` | `package-ref` | так | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `fork_of.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `fork_of.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `fork_of.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `last_ported_version` | `string` | ні | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `parent_latest_version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `newer_parent_versions` | array of `string` | так |  |

Приклад `behind`:

```json
{
  "fork_of": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0"
  },
  "last_ported_version": "1.2.0",
  "parent_latest_version": "1.3.0",
  "newer_parent_versions": [
    "1.3.0"
  ]
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `409`.
