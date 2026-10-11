# startTestRun

Прогнати тести пакета без запису в робочі дані

Контракт: [contracts/openapi/handler.v1.yaml](../../../../../../contracts/openapi/handler.v1.yaml).

```http
POST /v1/test-runs
```

## Опис із контракту

```text
Завжди `test_mode`. Запускає тести з маніфесту (`tests: all` або перелік імен) і додаткові
випадки (наприклад проблемні приклади). Результат — `Job.result` = TestReport
(`handler-result.schema.json#/$defs/TestReport`).
```

## Доступ

```json
{
  "scope": "handler:test",
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
        "allTests": {
          "value": {
            "handler": {
              "package_id": "shop-example.product-extractor",
              "version": "1.2.0"
            },
            "tests": "all"
          }
        },
        "withProblemSample": {
          "value": {
            "extra_cases": [
              {
                "compare": "subset",
                "expected": {
                  "entities": [
                    {
                      "entity_type": "product",
                      "fields": {
                        "price": {
                          "amount": 899,
                          "currency": "UAH"
                        }
                      },
                      "key": {
                        "natural": {
                          "sku": "C-300"
                        },
                        "scope": "shop-example"
                      },
                      "observation": {
                        "observation_id": "obs_01J9ZQ4A0000000000000009",
                        "observed_at": "2026-09-26T10:00:00Z"
                      }
                    }
                  ]
                },
                "expected_status": "success",
                "input": {
                  "kind": "material",
                  "material": {
                    "collector": {
                      "name": "web-collector",
                      "version": "0.1.0"
                    },
                    "content": {
                      "data": "<html><h1>C-300</h1><div class=\"price-new\">899 UAH</div></html>",
                      "encoding": "utf-8",
                      "kind": "inline",
                      "media_type": "text/html"
                    },
                    "fetched_at": "2026-09-26T10:00:00Z",
                    "format": {
                      "media_type": "text/html"
                    },
                    "locator": {
                      "url": "https://shop.example.test/product/c-300"
                    },
                    "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
                    "observation_id": "obs_01J9ZQ4A0000000000000009",
                    "revision": {
                      "content_sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
                    },
                    "source": {
                      "kind": "web"
                    }
                  }
                },
                "name": "problem-sample-2026-09-26"
              }
            ],
            "handler": {
              "package_id": "shop-example.product-extractor",
              "version": "1.3.0-draft.1"
            },
            "package_archive": {
              "kind": "blob",
              "media_type": "application/zip",
              "sha256": "3b8f0e5b1c1d0e7f9a2b4c6d8e0f1a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d2e4f",
              "size_bytes": 18422,
              "uri": "s3://jane-drafts/assistant/product-extractor-1.3.0-draft.1.zip"
            },
            "tests": "all"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/TestRunRequest"
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
| `404` | Ресурс не знайдено (`not_found`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

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
  "x-jane-scope": "handler:test"
}
```

## Схеми

- [contracts/openapi/handler.v1.yaml#/components/schemas/TestRunRequest](../../../../../../contracts/openapi/handler.v1.yaml#/components/schemas/TestRunRequest)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed](../../../../../../contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobQueued](../../../../../../contracts/openapi/common.yaml#/components/examples/JobQueued)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
