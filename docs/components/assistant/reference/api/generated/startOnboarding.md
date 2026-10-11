# startOnboarding

Почати підключення джерела (назва сайту/каналу або точне посилання)

Контракт: [contracts/openapi/assistant.v1.yaml](../../../../../../contracts/openapi/assistant.v1.yaml).

```http
POST /v1/onboarding-sessions
```

## Опис із контракту

```text
202 + Job (`kind: onboarding`). Ідентифікатор створеної сесії — `Job.labels.session_id`, її адреса —
`Job.links.session` (`/v1/onboarding-sessions/{session_id}`); ті самі поля мають усі job сесії
(продовження після `selectCandidate`, `acceptProposal`). `Job.result` завершеного job — `OnboardingSession`
на момент завершення (зокрема `needs_disambiguation`, `proposals_ready`, `insufficient_sample`).
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
        "byName": {
          "value": {
            "auto_activation": false,
            "expected_entity_types": [
              "product"
            ],
            "limits": {
              "budget": {
                "amount": 2,
                "currency": "USD",
                "period": "total"
              },
              "max_onboarding_samples": 60
            },
            "query": "Shop Example kettles"
          }
        },
        "byUrl": {
          "value": {
            "crawl_hints": {
              "scope": {
                "allowed_domains": [
                  "news.example.test"
                ]
              }
            },
            "expected_entity_types": [
              "event"
            ],
            "query": "https://news.example.test/",
            "source_kind": "web"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/OnboardingRequest"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `202` | Підключення почато; `labels.session_id` і `links.session` — сесія. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |
| `429` | Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`). | так |

```json
{
  "202": {
    "content": {
      "application/json": {
        "examples": {
          "onboarding": {
            "$ref": "#/components/examples/JobOnboardingQueued"
          },
          "queued": {
            "$ref": "common.yaml#/components/examples/JobQueued"
          }
        },
        "schema": {
          "$ref": "common.yaml#/components/schemas/Job"
        }
      }
    },
    "description": "Підключення почато; `labels.session_id` і `links.session` — сесія.",
    "headers": {
      "Idempotency-Replayed": {
        "$ref": "common.yaml#/components/headers/IdempotencyReplayed"
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

- [contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingRequest](../../../../../../contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingRequest)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed](../../../../../../contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobQueued](../../../../../../contracts/openapi/common.yaml#/components/examples/JobQueued)
- [contracts/openapi/assistant.v1.yaml#/components/examples/JobOnboardingQueued](../../../../../../contracts/openapi/assistant.v1.yaml#/components/examples/JobOnboardingQueued)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
- [contracts/openapi/common.yaml#/components/examples/ProblemRateLimited](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemRateLimited)
