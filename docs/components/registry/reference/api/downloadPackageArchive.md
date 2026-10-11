# GET /v1/packages/{package_id}/versions/{version}/archive

> Згенеровано `scripts/docs_reference.py` з [registry.v1.yaml](../../../../../contracts/openapi/registry.v1.yaml#L424). Не редагуйте вручну.

**Архів версії для автономного використання (ETag = дайджест)**

| Властивість | Значення |
|---|---|
| operationId | `downloadPackageArchive` |
| Метод і шлях | `GET /v1/packages/{package_id}/versions/{version}/archive` |
| Scope | `registry:read` |
| Ідемпотентність | — |
| Теги | versions |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `package_id` | path | `string` | так |  |
| `version` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | zip-архів; заголовок `ETag` дорівнює `"sha256:…"`. | `string` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/zip`.

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
