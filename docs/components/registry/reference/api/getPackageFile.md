# GET /v1/packages/{package_id}/versions/{version}/file

> Згенеровано `scripts/docs_reference.py` з [registry.v1.yaml](../../../../../contracts/openapi/registry.v1.yaml#L448). Не редагуйте вручну.

**Один файл версії (для редактора й diff в адмінці)**

| Властивість | Значення |
|---|---|
| operationId | `getPackageFile` |
| Метод і шлях | `GET /v1/packages/{package_id}/versions/{version}/file` |
| Scope | `registry:read` |
| Ідемпотентність | — |
| Теги | versions |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `package_id` | path | `string` | так |  |
| `version` | path | `string` | так |  |
| `path` | query | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Вміст файла. | `string`, `string` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200 (text/plain)

Тип вмісту `text/plain`.

Приклад `приклад`:

```json
"def extract(material, params, ctx):\n    ...\n"
```

### Відповідь 200 (application/octet-stream)

Тип вмісту `application/octet-stream`.

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
