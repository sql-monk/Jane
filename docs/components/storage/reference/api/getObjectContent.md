# GET /v1/objects/{object_id}/content

> Згенеровано `scripts/docs_reference.py` з [storage.v1.yaml](../../../../../contracts/openapi/storage.v1.yaml#L768). Не редагуйте вручну.

**Вміст збереженого об'єкта (байти в оригінальному медіатипі)**

| Властивість | Значення |
|---|---|
| operationId | `getObjectContent` |
| Метод і шлях | `GET /v1/objects/{object_id}/content` |
| Scope | `storage:read` |
| Ідемпотентність | — |
| Теги | objects |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `object_id` | path | `string` | так |  |
| `connection_id` | query | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Вміст; Content-Type — медіатип об'єкта (будь-який: `text/html`, `text/plain`, `application/json`, `application/pdf`, `image/*`…; перелічені нижче — приклади, решта — `*/*`); підтримується Range. | `string`, `string`, `string`, —, `string` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200 (application/octet-stream)

Тип вмісту `application/octet-stream`.

### Відповідь 200 (text/html)

Тип вмісту `text/html`.

Приклад `приклад`:

```json
"<html><head><title>Kettle A-100</title></head></html>"
```

### Відповідь 200 (text/plain)

Тип вмісту `text/plain`.

Приклад `приклад`:

```json
"Event 1: concert at 19:00"
```

### Відповідь 200 (application/json)

Тип вмісту `application/json`.

Приклад `приклад`:

```json
{}
```

### Відповідь 200 (*/*)

Тип вмісту `*/*`.

Приклад `приклад`:

```json
"Kettle A-100 1299 UAH"
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
