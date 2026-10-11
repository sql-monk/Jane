# getUpstreamStatus

Оновлення батьківського пакета для форку

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
GET /v1/packages/{package_id}/upstream
```

## Доступ

```json
{
  "scope": "registry:read",
  "security": [
    {
      "bearerAuth": []
    }
  ]
}
```

## Параметри

| Ім’я | Розміщення | Обов’язковий |
|---|---|---|
| `package_id` | `path` | так |

```json
[
  {
    "in": "path",
    "name": "package_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Стан відносно батька. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `409` | Пакет не є форком (`conflict`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "behind": {
            "value": {
              "fork_of": {
                "package_id": "shop-example.product-extractor",
                "version": "1.2.0"
              },
              "last_ported_version": "1.2.0",
              "newer_parent_versions": [
                "1.3.0"
              ],
              "parent_latest_version": "1.3.0"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/UpstreamStatus"
        }
      }
    },
    "description": "Стан відносно батька."
  },
  "401": {
    "content": {
      "application/problem+json": {
        "examples": {
          "unauthenticated": {
            "value": {
              "code": "unauthenticated",
              "status": 401,
              "title": "Unauthenticated",
              "type": "urn:jane:problem:unauthenticated"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Немає або недійсний токен (`unauthenticated`)."
  },
  "404": {
    "content": {
      "application/problem+json": {
        "examples": {
          "notFound": {
            "$ref": "#/components/examples/ProblemNotFound"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Ресурс не знайдено (`not_found`)."
  },
  "409": {
    "content": {
      "application/problem+json": {
        "examples": {
          "notFork": {
            "value": {
              "code": "conflict",
              "status": 409,
              "title": "Package is not a fork",
              "type": "urn:jane:problem:conflict"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Пакет не є форком (`conflict`)."
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "registry:read"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/openapi/registry.v1.yaml#/components/schemas/UpstreamStatus](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/UpstreamStatus)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/schemas/common/problem.schema.json](../../../../../../contracts/schemas/common/problem.schema.json)
