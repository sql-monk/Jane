# startCollection

Запустити збір (асинхронно)

Контракт: [contracts/openapi/collector.v1.yaml](../../../../../../contracts/openapi/collector.v1.yaml).

```http
POST /v1/collections
```

## Доступ

```json
{
  "scope": "collector:run",
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
        "telegramIncremental": {
          "value": {
            "mode": "incremental",
            "rules": {
              "account_connection_id": "tg-main",
              "channels": [
                {
                  "username": "city_events_example"
                }
              ],
              "collector": "telegram",
              "updates": {
                "edits": true,
                "new_messages": true
              }
            },
            "source_id": "news-tg",
            "source_kind": "telegram",
            "state_key": "news-tg"
          }
        },
        "webExplicitUrls": {
          "value": {
            "rules_ref": {
              "package_id": "shop-example.web-rules",
              "version": "1.0.0"
            },
            "source_id": "shop-example",
            "source_kind": "web",
            "urls": [
              "https://shop.example.test/product/a-100",
              "https://shop.example.test/product/b-200"
            ]
          }
        },
        "webFull": {
          "value": {
            "limits": {
              "crawl": {
                "max_pages_per_run": 20000
              },
              "queue": {
                "max_unacked_materials": 500
              }
            },
            "mode": "full",
            "rules_ref": {
              "package_id": "shop-example.web-rules",
              "version": "1.0.0"
            },
            "source_id": "shop-example",
            "source_kind": "web"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/CollectionRequest"
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
| `400` | Некоректний синтаксис запиту (`bad_request`). | так |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | так |

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
  "400": {
    "content": {
      "application/problem+json": {
        "examples": {
          "bad": {
            "value": {
              "code": "bad_request",
              "detail": "request body is not valid JSON",
              "status": 400,
              "title": "Bad request",
              "type": "urn:jane:problem:bad_request"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Некоректний синтаксис запиту (`bad_request`)."
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
  },
  "503": {
    "content": {
      "application/problem+json": {
        "examples": {
          "unavailable": {
            "value": {
              "code": "service_unavailable",
              "retry_after_seconds": 5,
              "retryable": true,
              "status": 503,
              "title": "Service unavailable",
              "type": "urn:jane:problem:service_unavailable"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`).",
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
  "x-jane-scope": "collector:run"
}
```

## Схеми

- [contracts/openapi/collector.v1.yaml#/components/schemas/CollectionRequest](../../../../../../contracts/openapi/collector.v1.yaml#/components/schemas/CollectionRequest)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed](../../../../../../contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobQueued](../../../../../../contracts/openapi/common.yaml#/components/examples/JobQueued)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
