# createPackage

Створити пакет (без версій)

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
POST /v1/packages
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
| `Idempotency-Key` | `header` | так |

```json
[
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
        "extractor": {
          "value": {
            "auto_changes_allowed": true,
            "kind": "extractor",
            "package_id": "shop-example.product-extractor",
            "title": "Shop Example product cards"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/PackageCreate"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `201` | Пакет створено. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `403` | Бракує прав (`forbidden`) або дію заборонено політикою (`access_denied_by_policy`). | так |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "201": {
    "content": {
      "application/json": {
        "examples": {
          "created": {
            "$ref": "#/components/examples/Package"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Package"
        }
      }
    },
    "description": "Пакет створено.",
    "headers": {
      "ETag": {
        "$ref": "common.yaml#/components/headers/ETag"
      },
      "Location": {
        "$ref": "common.yaml#/components/headers/Location"
      }
    }
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
  "403": {
    "content": {
      "application/problem+json": {
        "examples": {
          "forbidden": {
            "value": {
              "code": "forbidden",
              "detail": "scope registry:write required",
              "status": 403,
              "title": "Forbidden",
              "type": "urn:jane:problem:forbidden"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Бракує прав (`forbidden`) або дію заборонено політикою (`access_denied_by_policy`)."
  },
  "409": {
    "content": {
      "application/problem+json": {
        "examples": {
          "conflict": {
            "value": {
              "code": "conflict",
              "detail": "resource already exists",
              "status": 409,
              "title": "Conflict",
              "type": "urn:jane:problem:conflict"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`)."
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

- [contracts/openapi/registry.v1.yaml#/components/schemas/PackageCreate](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/PackageCreate)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/common.yaml#/components/headers/ETag](../../../../../../contracts/openapi/common.yaml#/components/headers/ETag)
- [contracts/openapi/registry.v1.yaml#/components/schemas/Package](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/Package)
- [contracts/openapi/registry.v1.yaml#/components/examples/Package](../../../../../../contracts/openapi/registry.v1.yaml#/components/examples/Package)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
