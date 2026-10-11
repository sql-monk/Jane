# startImprovement

Вдосконалити екстрактор на проблемних прикладах (нова версія або форк)

Контракт: [contracts/openapi/assistant.v1.yaml](../../../../../../contracts/openapi/assistant.v1.yaml).

```http
POST /v1/improvement-runs
```

## Опис із контракту

```text
LLM отримує вибірку проблем, поточний код, діагностику й успішні приклади. Нова версія
проходить нові й попередні тести й перевіряється на всіх прив'язках спільного пакета
(або оформлюється форком). Кількість спроб і витрати обмежені `limits.llm`. Якщо пакет
заборонено змінювати автоматично — лише пропозиція без публікації. Результат —
`Job.result` = ImprovementResult.
```

## Доступ

```json
{
  "scope": "assistant:use",
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
        "improve": {
          "value": {
            "bindings": [
              {
                "stage_id": "extract-products",
                "task_id": "shop-catalog"
              },
              {
                "stage_id": "extract-price",
                "task_id": "shop-price-check"
              }
            ],
            "limits": {
              "budget": {
                "amount": 1,
                "currency": "USD",
                "period": "run"
              },
              "max_improvement_attempts": 3
            },
            "package": {
              "package_id": "shop-example.product-extractor",
              "version": "1.2.0"
            },
            "policy": {
              "allow_fork": true,
              "approval": "manual"
            },
            "problem_group_id": "pg_01J9ZW0000000000000000001",
            "problem_samples": [
              {
                "diagnostics": [
                  {
                    "code": "extract.missing_selector",
                    "level": "warning",
                    "message": "selector .price matched 0 elements"
                  }
                ],
                "material_ref": {
                  "object_id": "obj_01J9ZQ4C00000000000000D9",
                  "storage_connection_id": "raw-files"
                }
              }
            ],
            "source_id": "shop-example",
            "successful_examples": [
              {
                "material_ref": {
                  "object_id": "obj_01J9ZQ4C00000000000000D1",
                  "storage_connection_id": "raw-files"
                }
              }
            ]
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/ImprovementRequest"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `202` | Операцію прийнято до асинхронного виконання. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |
| `429` | Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`). | так |

```json
{
  "202": {
    "content": {
      "application/json": {
        "examples": {
          "queued": {
            "$ref": "#/components/examples/JobQueued"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Job"
        }
      }
    },
    "description": "Операцію прийнято до асинхронного виконання.",
    "headers": {
      "Idempotency-Replayed": {
        "$ref": "#/components/headers/IdempotencyReplayed"
      },
      "Location": {
        "$ref": "#/components/headers/Location"
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
  },
  "429": {
    "content": {
      "application/problem+json": {
        "examples": {
          "rateLimited": {
            "$ref": "#/components/examples/ProblemRateLimited"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`).",
    "headers": {
      "Retry-After": {
        "$ref": "#/components/headers/RetryAfter"
      }
    }
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "assistant:use"
}
```

## Схеми

- [contracts/openapi/assistant.v1.yaml#/components/schemas/ImprovementRequest](../../../../../../contracts/openapi/assistant.v1.yaml#/components/schemas/ImprovementRequest)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed](../../../../../../contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobQueued](../../../../../../contracts/openapi/common.yaml#/components/examples/JobQueued)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
- [contracts/openapi/common.yaml#/components/examples/ProblemRateLimited](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemRateLimited)
