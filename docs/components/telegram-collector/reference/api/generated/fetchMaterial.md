# fetchMaterial

Синхронно отримати один матеріал

Контракт: [contracts/openapi/collector.v1.yaml](../../../../../../contracts/openapi/collector.v1.yaml).

```http
POST /v1/fetches
```

## Опис із контракту

```text
Коротка операція: один URL або одне повідомлення. Перевіряє scope й robots, якщо передано
правила. Кожен виклик — нове спостереження (новий `observation_id`), тому ключ
ідемпотентності не потрібен. Якщо джерело підтвердило, що матеріалу немає (сайт відповів
HTTP 404 або 410; повідомлення Telegram не існує чи видалене), — `404 not_found`; інші
помилки джерела — `502 source_unavailable`.
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

Параметрів у контракті немає.

## Тіло запиту

```json
{
  "content": {
    "application/json": {
      "examples": {
        "telegram": {
          "value": {
            "source_kind": "telegram",
            "telegram": {
              "channel_username": "city_events_example",
              "message_id": 4521
            }
          }
        },
        "web": {
          "value": {
            "content_delivery": "auto",
            "rules_ref": {
              "package_id": "shop-example.web-rules",
              "version": "1.0.0"
            },
            "source_id": "shop-example",
            "source_kind": "web",
            "url": "https://shop.example.test/product/a-100"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/FetchRequest"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Матеріал із метаданими. | ні |
| `400` | Некоректний синтаксис запиту (`bad_request`). | так |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `403` | Заборонено robots.txt або політикою доступу (`access_denied_by_policy`). | так |
| `404` | Джерело підтвердило, що матеріалу немає (`not_found`, `retryable: false`): web — сайт відповів HTTP 404 або 410 (`details.http_status`); Telegram — повідомлення не існує або видалене (`details.reason: message_not_found`).  | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |
| `429` | Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`). | так |
| `502` | Джерело недоступне або повернуло помилку (`source_unavailable`). Web: `details.http_status` — статус відповіді сайту (крім 404/410, див. 404) або останньої спроби після повторів. Telegram: `details.reason` — `channel_unavailable` (канал не знайдено, приватний чи без доступу) або `account_unauthorized` (сесію відхилено); для них `retryable: false`, бо повтор нічого не змінить.  | так |
| `500` | Непередбачена помилка сервісу (`internal_error`, retryable). | так |
| `501` | Правила просять `fetch.render_js`, але в цьому колекторі немає headless-браузера (рендеринг вимкнено, Playwright чи Chromium не встановлено або браузер не стартує; `not_implemented`, `retryable: false`). Причина — у `detail`; те саме видно в `GET /v1/info` → `capabilities.render_js`.  | так |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | так |
| `504` | `fetch.render_js`: DOM сторінки не вдалося отримати з браузера за `collector.render_timeout_ms` (`timeout`, `retryable: true`).  | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "blob": {
            "$ref": "../examples/openapi/material-web-blob.json"
          },
          "telegram": {
            "$ref": "../examples/openapi/material-telegram.json"
          },
          "web": {
            "$ref": "../examples/openapi/material-web.json"
          }
        },
        "schema": {
          "$ref": "../schemas/material.schema.json"
        }
      }
    },
    "description": "Матеріал із метаданими."
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
  "403": {
    "content": {
      "application/problem+json": {
        "examples": {
          "robots": {
            "value": {
              "code": "access_denied_by_policy",
              "detail": "disallowed by robots.txt for user-agent JaneBot",
              "status": 403,
              "title": "Access denied by policy",
              "type": "urn:jane:problem:access_denied_by_policy"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Заборонено robots.txt або політикою доступу (`access_denied_by_policy`)."
  },
  "404": {
    "content": {
      "application/problem+json": {
        "examples": {
          "telegram": {
            "value": {
              "code": "not_found",
              "detail": "message 4521 not found in city_events_example",
              "details": {
                "reason": "message_not_found"
              },
              "retryable": false,
              "status": 404,
              "title": "Not found",
              "type": "urn:jane:problem:not_found"
            }
          },
          "web": {
            "value": {
              "code": "not_found",
              "detail": "source returned HTTP 404",
              "details": {
                "http_status": 404
              },
              "retryable": false,
              "status": 404,
              "title": "Not found",
              "type": "urn:jane:problem:not_found"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Джерело підтвердило, що матеріалу немає (`not_found`, `retryable: false`): web — сайт відповів\nHTTP 404 або 410 (`details.http_status`); Telegram — повідомлення не існує або видалене\n(`details.reason: message_not_found`).\n"
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
  },
  "500": {
    "content": {
      "application/problem+json": {
        "examples": {
          "internal": {
            "value": {
              "code": "internal_error",
              "retryable": true,
              "status": 500,
              "title": "Internal error",
              "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
              "type": "urn:jane:problem:internal_error"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Непередбачена помилка сервісу (`internal_error`, retryable)."
  },
  "501": {
    "content": {
      "application/problem+json": {
        "examples": {
          "noBrowser": {
            "value": {
              "code": "not_implemented",
              "detail": "fetch.render_js: rendering is disabled (JANE_WEB_COLLECTOR_RENDER_ENABLED=false)",
              "retryable": false,
              "status": 501,
              "title": "Not implemented",
              "type": "urn:jane:problem:not_implemented"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Правила просять `fetch.render_js`, але в цьому колекторі немає headless-браузера (рендеринг вимкнено,\nPlaywright чи Chromium не встановлено або браузер не стартує; `not_implemented`, `retryable: false`).\nПричина — у `detail`; те саме видно в `GET /v1/info` → `capabilities.render_js`.\n"
  },
  "502": {
    "content": {
      "application/problem+json": {
        "examples": {
          "channel": {
            "value": {
              "code": "source_unavailable",
              "details": {
                "reason": "channel_unavailable"
              },
              "retryable": false,
              "status": 502,
              "title": "Source unavailable",
              "type": "urn:jane:problem:source_unavailable"
            }
          },
          "upstream": {
            "value": {
              "code": "source_unavailable",
              "details": {
                "http_status": 503
              },
              "retryable": true,
              "status": 502,
              "title": "Source unavailable",
              "type": "urn:jane:problem:source_unavailable"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Джерело недоступне або повернуло помилку (`source_unavailable`). Web: `details.http_status` —\nстатус відповіді сайту (крім 404/410, див. 404) або останньої спроби після повторів. Telegram:\n`details.reason` — `channel_unavailable` (канал не знайдено, приватний чи без доступу) або\n`account_unauthorized` (сесію відхилено); для них `retryable: false`, бо повтор нічого не змінить.\n"
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
  },
  "504": {
    "content": {
      "application/problem+json": {
        "examples": {
          "renderTimeout": {
            "value": {
              "code": "timeout",
              "detail": "render: the DOM was not taken within collector.render_timeout_ms=30000",
              "retryable": true,
              "status": 504,
              "title": "Timeout",
              "type": "urn:jane:problem:timeout"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "`fetch.render_js`: DOM сторінки не вдалося отримати з браузера за `collector.render_timeout_ms`\n(`timeout`, `retryable: true`).\n"
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-no-idempotency-key": "read-only for Jane state; every call is a new observation by design",
  "x-jane-scope": "collector:run"
}
```

## Схеми

- [contracts/openapi/collector.v1.yaml#/components/schemas/FetchRequest](../../../../../../contracts/openapi/collector.v1.yaml#/components/schemas/FetchRequest)
- [contracts/schemas/material.schema.json](../../../../../../contracts/schemas/material.schema.json)
- [contracts/examples/openapi/material-web.json](../../../../../../contracts/examples/openapi/material-web.json)
- [contracts/examples/openapi/material-web-blob.json](../../../../../../contracts/examples/openapi/material-web-blob.json)
- [contracts/examples/openapi/material-telegram.json](../../../../../../contracts/examples/openapi/material-telegram.json)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/schemas/common/problem.schema.json](../../../../../../contracts/schemas/common/problem.schema.json)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
- [contracts/openapi/common.yaml#/components/examples/ProblemRateLimited](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemRateLimited)
