# recordTestResults

Записати звіт прогону тестів версії (від handler-runtime або асистента)

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
POST /v1/packages/{package_id}/versions/{version}/test-results
```

## Доступ

```json
{
  "scope": "registry:write",
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
| `Idempotency-Key` | `header` | так |

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
    "description": "Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований\nключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь\n(заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом —\n422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress`\n(retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`.\n",
    "example": "0b7d5c1e-3f7e-4a53-9d0e-5a0f5c0a9b11",
    "in": "header",
    "name": "Idempotency-Key",
    "required": true,
    "schema": {
      "maxLength": 255,
      "minLength": 1,
      "pattern": "^[\\x21-\\x7E]+$",
      "type": "string"
    }
  }
]
```

## Тіло запиту

```json
{
  "content": {
    "application/json": {
      "examples": {
        "report": {
          "value": {
            "context": "bindings:shop-catalog/extract-products",
            "report": {
              "cases": [
                {
                  "name": "product-a100",
                  "passed": true
                },
                {
                  "name": "category-page-empty",
                  "passed": true
                }
              ],
              "failed": 0,
              "package": {
                "package_id": "shop-example.product-extractor",
                "version": "1.2.0"
              },
              "passed": 2
            },
            "runner": "handler-runtime@0.1.0"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/TestResultsRecord"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Версія з оновленим test_status. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "version": {
            "$ref": "#/components/examples/PackageVersion"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/PackageVersion"
        }
      }
    },
    "description": "Версія з оновленим test_status."
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
  "422": {
    "content": {
      "application/problem+json": {
        "examples": {
          "idempotencyReused": {
            "$ref": "#/components/examples/ProblemIdempotencyReused"
          },
          "validation": {
            "$ref": "#/components/examples/ProblemValidation"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо)."
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "registry:write"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/schemas/common/defs.schema.json#/$defs/SemVer](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/SemVer)
- [contracts/openapi/registry.v1.yaml#/components/schemas/TestResultsRecord](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/TestResultsRecord)
- [contracts/openapi/registry.v1.yaml#/components/schemas/PackageVersion](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/PackageVersion)
- [contracts/openapi/registry.v1.yaml#/components/examples/PackageVersion](../../../../../../contracts/openapi/registry.v1.yaml#/components/examples/PackageVersion)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
