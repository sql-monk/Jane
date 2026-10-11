# analyzeUnknownMaterial

Проаналізувати невідомий матеріал (викликає оркестратор лише за увімкненим прапорцем)

Контракт: [contracts/openapi/assistant.v1.yaml](../../../../../../contracts/openapi/assistant.v1.yaml).

```http
POST /v1/unknown-materials
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
        "unknown": {
          "value": {
            "forward_unknown_to_llm": true,
            "material": {
              "collector": {
                "name": "web-collector",
                "version": "0.1.0"
              },
              "content": {
                "data": "<html><h1>Gift cards</h1></html>",
                "encoding": "utf-8",
                "kind": "inline",
                "media_type": "text/html"
              },
              "fetched_at": "2026-09-27T10:05:00Z",
              "format": {
                "media_type": "text/html"
              },
              "locator": {
                "url": "https://shop.example.test/gift-cards"
              },
              "material_id": "web:0a1b2c3d4e5f60718293a4b5c6d7e8f9",
              "observation_id": "obs_01J9ZQ5A0000000000000007",
              "revision": {
                "content_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
              },
              "source": {
                "kind": "web",
                "source_id": "shop-example"
              }
            },
            "source_id": "shop-example",
            "task_id": "shop-catalog"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/UnknownMaterialRequest"
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
| `403` | forward_unknown_to_llm не увімкнено — асистент не викликає LLM (`access_denied_by_policy`). | так |
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
  "403": {
    "content": {
      "application/problem+json": {
        "examples": {
          "flagOff": {
            "value": {
              "code": "access_denied_by_policy",
              "status": 403,
              "title": "Forwarding unknown pages to LLM is disabled",
              "type": "urn:jane:problem:access_denied_by_policy"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "forward_unknown_to_llm не увімкнено — асистент не викликає LLM (`access_denied_by_policy`)."
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

- [contracts/openapi/assistant.v1.yaml#/components/schemas/UnknownMaterialRequest](../../../../../../contracts/openapi/assistant.v1.yaml#/components/schemas/UnknownMaterialRequest)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed](../../../../../../contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobQueued](../../../../../../contracts/openapi/common.yaml#/components/examples/JobQueued)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/schemas/common/problem.schema.json](../../../../../../contracts/schemas/common/problem.schema.json)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
- [contracts/openapi/common.yaml#/components/examples/ProblemRateLimited](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemRateLimited)
