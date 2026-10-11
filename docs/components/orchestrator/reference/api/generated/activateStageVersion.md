# activateStageVersion

Активувати версію пакета в етапі (або відкотити до попередньої)

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
POST /v1/tasks/{task_id}/stages/{stage_id}/activations
```

## Опис із контракту

```text
Змінює `stages[].handler` завдання з аудитом. Для етапу `kind: collect` активується версія
**правил колектора** (ТЗ §8, §10): змінюється `stages[].collector.rules`, пакет має бути
`kind: collector-rules` (інакше 422); `previous` — правила етапу або, якщо етап їх не задавав,
`Source.collector_rules` джерела (після активації чи відкату етап явно посилається на версію).
- `activate` — людина активує версію; версія має бути `approved` у репозиторії.
- `rollback` — повернення до попередньої активації (або до вказаної версії).
- `auto_activate` — автоматична активація (асистент після перевірок). Приймається лише якщо
  політика дозволяє: `Source.change_policy.llm_versions = auto_after_checks` **і** пакет
  має `auto_changes_allowed = true` **і** версія пройшла тести на всіх прив'язках: агрегат
  registry `PackageVersion.test_summary.status = passed` (останній звіт кожного `context`
  пройшов); якщо registry не віддає `test_summary` — `test_status = passed`. Інакше — 403
  `access_denied_by_policy` (у `details.reason`: `source_policy`,
  `package_auto_changes_forbidden` або `tests_not_passed`), активація не виконується.
```

## Доступ

```json
{
  "scope": [
    "orchestrator:write",
    "orchestrator:admin"
  ],
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
| `task_id` | `path` | так |
| `stage_id` | `path` | так |
| `Idempotency-Key` | `header` | так |

```json
[
  {
    "in": "path",
    "name": "task_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  },
  {
    "in": "path",
    "name": "stage_id",
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
        "activate": {
          "value": {
            "kind": "activate",
            "package": {
              "digest": "sha256:0f4c1c8f3e0f6a7d9b2c4e6f8a0b2c4d6e8f0a1b3c5d7e9f1a3b5c7d9e1f3a5b",
              "package_id": "shop-example.product-extractor",
              "version": "1.2.0"
            },
            "reason": "tests passed on all bindings"
          }
        },
        "autoActivate": {
          "value": {
            "kind": "auto_activate",
            "package": {
              "package_id": "shop-example.product-extractor",
              "version": "1.3.0"
            },
            "reason": "assistant improvement job_01J9ZX0000000000000000IMP passed tests on 2 bindings"
          }
        },
        "rollback": {
          "value": {
            "kind": "rollback",
            "reason": "regression on category pages"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/ActivationRequest"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Активацію виконано. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `403` | Автоактивацію заборонено політикою (`access_denied_by_policy`) або бракує scope (`forbidden`). | так |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "activated": {
            "value": {
              "activated_at": "2026-09-27T10:20:00Z",
              "activated_by": "admin@example.org",
              "activation_id": "act_01J9ZV0000000000000000001",
              "kind": "activate",
              "package": {
                "package_id": "shop-example.product-extractor",
                "version": "1.2.0"
              },
              "previous": {
                "package_id": "shop-example.product-extractor",
                "version": "1.1.0"
              },
              "reason": "tests passed on all bindings",
              "stage_id": "extract-products",
              "task_id": "shop-catalog"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Activation"
        }
      }
    },
    "description": "Активацію виконано."
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
          "policy": {
            "value": {
              "code": "access_denied_by_policy",
              "details": {
                "reason": "package_auto_changes_forbidden"
              },
              "retryable": false,
              "status": 403,
              "title": "Automatic activation is not allowed",
              "type": "urn:jane:problem:access_denied_by_policy"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Автоактивацію заборонено політикою (`access_denied_by_policy`) або бракує scope (`forbidden`)."
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
  "x-jane-scope": [
    "orchestrator:write",
    "orchestrator:admin"
  ]
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/ActivationRequest](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/ActivationRequest)
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/Activation](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/Activation)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/schemas/common/problem.schema.json](../../../../../../contracts/schemas/common/problem.schema.json)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
