# invokeHandler

Виконати обробник над вхідними даними

Контракт: [contracts/openapi/handler.v1.yaml](../../../../../../contracts/openapi/handler.v1.yaml).

```http
POST /v1/invocations
```

## Опис із контракту

```text
`mode: sync` — 200 з HandlerResult (або 202, якщо не вклалося в
`limits.timeouts.sync_response_max_ms`); `mode: async` — одразу 202, результат —
`Job.result` (HandlerResult) за `GET /v1/jobs/{job_id}`.
Виконавець бере пакет із `package_archive` або з репозиторію за `handler` і перевіряє
дайджест, якщо його задано.
```

## Доступ

```json
{
  "scope": "handler:invoke",
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
| `traceparent` | `header` | ні |

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
  },
  {
    "description": "W3C Trace Context; сервіс продовжує трасу й передає її далі.",
    "in": "header",
    "name": "traceparent",
    "required": false,
    "schema": {
      "pattern": "^[0-9a-f]{2}-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$",
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
        "extract": {
          "$ref": "../examples/openapi/invocation-extract.json"
        },
        "localTest": {
          "$ref": "../examples/openapi/invocation-local-test.json"
        },
        "store": {
          "$ref": "../examples/openapi/invocation-store.json"
        }
      },
      "schema": {
        "$ref": "../schemas/handler-invocation.schema.json"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Обробник виконано (будь-який із чотирьох станів). | ні |
| `202` | Операцію прийнято до асинхронного виконання. | ні |
| `400` | Некоректний синтаксис запиту (`bad_request`). | так |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Пакет або підключення не знайдено (`not_found`). | так |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | так |
| `413` | Тіло перевищує `limits.transfer.max_request_body_bytes` — передайте вміст як blob (`payload_too_large`). | так |
| `422` | Невалідний запит, параметри не відповідають params_schema, `digest_mismatch`, `dependency_not_allowed`, `idempotency_key_reused`. | так |
| `429` | Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`). | так |
| `502` | Недоступний репозиторій, сховище чи провайдер LLM (`upstream_unavailable`). | так |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "empty": {
            "$ref": "../examples/openapi/result-extractor-empty.json"
          },
          "failedSchema": {
            "$ref": "../examples/openapi/result-extractor-failed.json"
          },
          "failedTimeout": {
            "$ref": "../examples/openapi/result-extractor-timeout.json"
          },
          "llm": {
            "$ref": "../examples/openapi/result-llm-success.json"
          },
          "storageDuplicate": {
            "$ref": "../examples/openapi/result-storage-duplicate.json"
          },
          "storageRaw": {
            "$ref": "../examples/openapi/result-storage-raw.json"
          },
          "storageStale": {
            "$ref": "../examples/openapi/result-storage-stale.json"
          },
          "storageWritten": {
            "$ref": "../examples/openapi/result-storage-written.json"
          },
          "success": {
            "$ref": "../examples/openapi/result-extractor-success.json"
          },
          "unrecognized": {
            "$ref": "../examples/openapi/result-extractor-unrecognized.json"
          }
        },
        "schema": {
          "$ref": "../schemas/handler-result.schema.json"
        }
      }
    },
    "description": "Обробник виконано (будь-який із чотирьох станів).",
    "headers": {
      "Idempotency-Replayed": {
        "$ref": "common.yaml#/components/headers/IdempotencyReplayed"
      }
    }
  },
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
  "404": {
    "content": {
      "application/problem+json": {
        "examples": {
          "package": {
            "value": {
              "code": "not_found",
              "detail": "shop-example.product-extractor@9.9.9",
              "status": 404,
              "title": "Package version not found",
              "type": "urn:jane:problem:not_found"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Пакет або підключення не знайдено (`not_found`)."
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
  "413": {
    "content": {
      "application/problem+json": {
        "examples": {
          "tooLarge": {
            "value": {
              "code": "payload_too_large",
              "details": {
                "limit": 10485760
              },
              "status": 413,
              "title": "Payload too large",
              "type": "urn:jane:problem:payload_too_large"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Тіло перевищує `limits.transfer.max_request_body_bytes` — передайте вміст як blob (`payload_too_large`)."
  },
  "422": {
    "content": {
      "application/problem+json": {
        "examples": {
          "digest": {
            "value": {
              "code": "digest_mismatch",
              "retryable": false,
              "status": 422,
              "title": "Package digest mismatch",
              "type": "urn:jane:problem:digest_mismatch"
            }
          },
          "validation": {
            "$ref": "common.yaml#/components/examples/ProblemValidation"
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Невалідний запит, параметри не відповідають params_schema, `digest_mismatch`, `dependency_not_allowed`, `idempotency_key_reused`."
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
  },
  "502": {
    "content": {
      "application/problem+json": {
        "examples": {
          "upstream": {
            "value": {
              "code": "upstream_unavailable",
              "detail": "registry did not respond",
              "retryable": true,
              "status": 502,
              "title": "Upstream unavailable",
              "type": "urn:jane:problem:upstream_unavailable"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Недоступний репозиторій, сховище чи провайдер LLM (`upstream_unavailable`)."
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
  "x-jane-scope": "handler:invoke"
}
```

## Схеми

- [contracts/schemas/handler-invocation.schema.json](../../../../../../contracts/schemas/handler-invocation.schema.json)
- [contracts/examples/openapi/invocation-extract.json](../../../../../../contracts/examples/openapi/invocation-extract.json)
- [contracts/examples/openapi/invocation-store.json](../../../../../../contracts/examples/openapi/invocation-store.json)
- [contracts/examples/openapi/invocation-local-test.json](../../../../../../contracts/examples/openapi/invocation-local-test.json)
- [contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed](../../../../../../contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed)
- [contracts/schemas/handler-result.schema.json](../../../../../../contracts/schemas/handler-result.schema.json)
- [contracts/examples/openapi/result-extractor-success.json](../../../../../../contracts/examples/openapi/result-extractor-success.json)
- [contracts/examples/openapi/result-extractor-empty.json](../../../../../../contracts/examples/openapi/result-extractor-empty.json)
- [contracts/examples/openapi/result-extractor-unrecognized.json](../../../../../../contracts/examples/openapi/result-extractor-unrecognized.json)
- [contracts/examples/openapi/result-extractor-failed.json](../../../../../../contracts/examples/openapi/result-extractor-failed.json)
- [contracts/examples/openapi/result-extractor-timeout.json](../../../../../../contracts/examples/openapi/result-extractor-timeout.json)
- [contracts/examples/openapi/result-storage-written.json](../../../../../../contracts/examples/openapi/result-storage-written.json)
- [contracts/examples/openapi/result-storage-duplicate.json](../../../../../../contracts/examples/openapi/result-storage-duplicate.json)
- [contracts/examples/openapi/result-storage-stale.json](../../../../../../contracts/examples/openapi/result-storage-stale.json)
- [contracts/examples/openapi/result-storage-raw.json](../../../../../../contracts/examples/openapi/result-storage-raw.json)
- [contracts/examples/openapi/result-llm-success.json](../../../../../../contracts/examples/openapi/result-llm-success.json)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobQueued](../../../../../../contracts/openapi/common.yaml#/components/examples/JobQueued)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/schemas/common/problem.schema.json](../../../../../../contracts/schemas/common/problem.schema.json)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
- [contracts/openapi/common.yaml#/components/examples/ProblemRateLimited](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemRateLimited)
