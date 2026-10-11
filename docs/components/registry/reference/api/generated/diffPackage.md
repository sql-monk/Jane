# diffPackage

Відмінності між версіями або від батька (для форку)

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
GET /v1/packages/{package_id}/diff
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
| `from` | `query` | ні |
| `to` | `query` | так |
| `context_lines` | `query` | ні |

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
    "description": "Версія цього пакета; або `parent:<version>` — версія батька.",
    "in": "query",
    "name": "from",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "to",
    "required": true,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "context_lines",
    "required": false,
    "schema": {
      "default": 3,
      "minimum": 0,
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
| `200` | Відмінності. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "diff": {
            "value": {
              "files": [
                {
                  "path": "src/product_extractor/main.py",
                  "status": "modified",
                  "unified_diff": "@@ -10,3 +10,5 @@\n-    title = h1.text()\n+    title = h1.text() if h1 else og_title(tree)\n"
                },
                {
                  "path": "tests/og-title/page.html",
                  "status": "added"
                }
              ],
              "from": {
                "package_id": "shop-example.product-extractor",
                "version": "1.1.0"
              },
              "manifest_changes": [
                {
                  "new": "Fallback to og:title when h1 is missing.",
                  "old": "Initial version.",
                  "op": "replace",
                  "pointer": "/provenance/change_summary"
                }
              ],
              "to": {
                "package_id": "shop-example.product-extractor",
                "version": "1.2.0"
              }
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/PackageDiff"
        }
      }
    },
    "description": "Відмінності."
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
- [contracts/openapi/registry.v1.yaml#/components/schemas/PackageDiff](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/PackageDiff)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
