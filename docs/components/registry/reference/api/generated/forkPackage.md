# forkPackage

Створити незалежний форк від версії

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
POST /v1/packages/{package_id}/forks
```

## Опис із контракту

```text
Копіює вміст версії `from_version` у новий пакет `new_package_id` з `fork_of`
(батько, вихідна версія, дайджест). Підключення й секрети не копіюються (їх у пакеті й
немає); налаштування `auto_changes_allowed` — з запиту.
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
        "fork": {
          "value": {
            "from_version": "1.2.0",
            "new_package_id": "acme.product-extractor",
            "title": "ACME fork of Shop Example product cards"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/ForkRequest"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `201` | Форк створено; перша версія має fork_of. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | так |

```json
{
  "201": {
    "content": {
      "application/json": {
        "examples": {
          "fork": {
            "value": {
              "auto_changes_allowed": false,
              "created_at": "2026-09-27T11:00:00Z",
              "deprecated": false,
              "fork_of": {
                "digest": "sha256:0f4c1c8f3e0f6a7d9b2c4e6f8a0b2c4d6e8f0a1b3c5d7e9f1a3b5c7d9e1f3a5b",
                "package_id": "shop-example.product-extractor",
                "version": "1.2.0"
              },
              "kind": "extractor",
              "latest_version": "1.2.0",
              "package_id": "acme.product-extractor",
              "title": "ACME fork of Shop Example product cards",
              "updated_at": "2026-09-27T11:00:00Z"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Package"
        }
      }
    },
    "description": "Форк створено; перша версія має fork_of.",
    "headers": {
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
- [contracts/openapi/registry.v1.yaml#/components/schemas/ForkRequest](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/ForkRequest)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/registry.v1.yaml#/components/schemas/Package](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/Package)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
