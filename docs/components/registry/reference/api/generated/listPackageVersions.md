# listPackageVersions

Версії пакета

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
GET /v1/packages/{package_id}/versions
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
| `status` | `query` | ні |
| `cursor` | `query` | ні |
| `limit` | `query` | ні |

```json
[
  {
    "in": "path",
    "name": "package_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  },
  {
    "in": "query",
    "name": "status",
    "required": false,
    "schema": {
      "$ref": "#/components/schemas/VersionStatus"
    }
  },
  {
    "description": "Непрозорий курсор з `next_cursor` попередньої сторінки.",
    "in": "query",
    "name": "cursor",
    "required": false,
    "schema": {
      "maxLength": 2048,
      "type": "string"
    }
  },
  {
    "description": "Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму.",
    "in": "query",
    "name": "limit",
    "required": false,
    "schema": {
      "default": 50,
      "minimum": 1,
      "type": "integer"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Сторінка версій (від новіших). | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "versions": {
            "value": {
              "items": [
                {
                  "created_at": "2026-09-27T09:40:00Z",
                  "created_by": "llm",
                  "digest": "sha256:0f4c1c8f3e0f6a7d9b2c4e6f8a0b2c4d6e8f0a1b3c5d7e9f1a3b5c7d9e1f3a5b",
                  "package_id": "shop-example.product-extractor",
                  "status": "approved",
                  "test_status": "passed",
                  "version": "1.2.0"
                }
              ],
              "next_cursor": null
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/PackageVersionList"
        }
      }
    },
    "description": "Сторінка версій (від новіших)."
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
- [contracts/openapi/registry.v1.yaml#/components/schemas/VersionStatus](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/VersionStatus)
- [contracts/openapi/registry.v1.yaml#/components/schemas/PackageVersionList](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/PackageVersionList)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
