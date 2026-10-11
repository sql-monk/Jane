# getPackageFile

Один файл версії (для редактора й diff в адмінці)

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
GET /v1/packages/{package_id}/versions/{version}/file
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
| `version` | `path` | так |
| `path` | `query` | так |

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
    "in": "path",
    "name": "version",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/SemVer"
    }
  },
  {
    "in": "query",
    "name": "path",
    "required": true,
    "schema": {
      "$ref": "../schemas/package-manifest.schema.json#/$defs/PackagePath"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Вміст файла. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/octet-stream": {
        "schema": {
          "contentMediaType": "application/octet-stream",
          "type": "string"
        }
      },
      "text/plain": {
        "example": "def extract(material, params, ctx):\n    ...\n",
        "schema": {
          "type": "string"
        }
      }
    },
    "description": "Вміст файла."
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
- [contracts/schemas/common/defs.schema.json#/$defs/SemVer](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/SemVer)
- [contracts/schemas/package-manifest.schema.json#/$defs/PackagePath](../../../../../../contracts/schemas/package-manifest.schema.json#/$defs/PackagePath)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
