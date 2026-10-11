# POST /v1/rules/validations

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L412). Не редагуйте вручну.

**Перевірити правила колектора без запуску**

| Властивість | Значення |
|---|---|
| operationId | `validateRules` |
| Метод і шлях | `POST /v1/rules/validations` |
| Scope | `collector:read`, `collector:run` |
| Ідемпотентність | не потрібна: pure validation without side effects |
| Теги | rules |

## Тіло запиту

Тип вмісту `application/json`, схема `WebRules` \| `TelegramRules`; обов'язкове: так.

Приклад `shop`:

```json
{
  "collector": "web",
  "scope": {
    "allowed_domains": [
      "shop.example.test"
    ],
    "include_subdomains": false,
    "path_prefixes": [
      "/"
    ],
    "exclude": [
      {
        "value": "shop.example.test/cart/**"
      },
      {
        "type": "regex",
        "value": ".*[?&]sort=.*"
      }
    ]
  },
  "strategies": [
    {
      "type": "sitemap",
      "strategy_id": "sitemap",
      "use_robots_txt": true,
      "priority": 10
    },
    {
      "type": "recursive",
      "strategy_id": "links",
      "follow": [
        {
          "value": "shop.example.test/catalog/**"
        },
        {
          "value": "shop.example.test/product/**"
        }
      ],
      "limits": {
        "crawl": {
          "max_depth": 3
        }
      }
    },
    {
      "type": "listing",
      "strategy_id": "categories",
      "start_urls": [
        "https://shop.example.test/catalog/kettles"
      ],
      "item_links": {
        "value": "a.product-card"
      },
      "next_page": {
        "type": "rel",
        "value": "next"
      }
    }
  ],
  "robots": {
    "mode": "respect"
  },
  "normalization": {
    "strip_query_params": [
      "utm_*",
      "sessionid"
    ],
    "trailing_slash": "remove"
  },
  "dedup": {
    "key": "canonical_url"
  },
  "priorities": [
    {
      "pattern": {
        "value": "shop.example.test/product/**"
      },
      "priority": 20
    }
  ],
  "sections": [
    {
      "section_id": "products",
      "patterns": [
        {
          "value": "shop.example.test/product/**"
        }
      ]
    },
    {
      "section_id": "catalog",
      "patterns": [
        {
          "value": "shop.example.test/catalog/**"
        }
      ]
    }
  ],
  "fetch": {
    "user_agent": "JaneBot/0.1 (+https://jane.invalid/bot)"
  },
  "revisit": {
    "mode": "if_changed"
  },
  "limits": {
    "rate": {
      "requests_per_second_per_host": 1,
      "respect_crawl_delay": true
    }
  }
}
```

Приклад `news`:

```json
{
  "collector": "web",
  "scope": {
    "allowed_domains": [
      "news.example.test"
    ],
    "include_subdomains": true
  },
  "strategies": [
    {
      "type": "feed",
      "urls": [
        "https://news.example.test/rss.xml"
      ],
      "autodiscover": true
    },
    {
      "type": "url_template",
      "template": "https://news.example.test/archive/{year}/{page}",
      "variables": {
        "year": {
          "values": [
            2025,
            2026
          ]
        },
        "page": {
          "range": {
            "start": 1,
            "end": 50
          }
        }
      },
      "stop_after_consecutive_misses": 3
    },
    {
      "type": "api_feed",
      "url": "https://news.example.test/api/articles?limit=50",
      "items_path": "$.items",
      "url_path": "$.url",
      "lastmod_path": "$.updated_at",
      "pagination": {
        "type": "next_url",
        "next_url_path": "$.next"
      }
    },
    {
      "type": "listing",
      "start_urls": [
        "https://news.example.test/search"
      ],
      "search": {
        "url_template": "https://news.example.test/search?q={query}",
        "queries": [
          "концерт",
          "виставка"
        ]
      }
    },
    {
      "type": "llm_explore",
      "goal": "знайти сторінки анонсів подій",
      "expected_entity_types": [
        "event"
      ]
    }
  ],
  "sections": [
    {
      "section_id": "articles",
      "patterns": [
        {
          "type": "regex",
          "value": "^news\\.example\\.test/\\d{4}/\\d{2}/.+"
        }
      ]
    }
  ]
}
```

Приклад `telegram`:

```json
{
  "collector": "telegram",
  "channels": [
    {
      "username": "city_events_example"
    },
    {
      "channel_id": "-1001234567890"
    }
  ],
  "history": {
    "enabled": true,
    "since": "2026-09-01T00:00:00Z"
  },
  "updates": {
    "new_messages": true,
    "edits": true
  },
  "media": {
    "download": false
  },
  "account_connection_id": "tg-main",
  "limits": {
    "telegram": {
      "max_messages_per_run": 5000,
      "max_flood_wait_seconds": 300
    }
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Результат перевірки (невалідні правила — теж 200 з valid=false). | `RulesValidation` |
| `400` | Некоректний синтаксис запиту (`bad_request`). | `problem` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `valid` | `boolean` | так |  |
| `supported` | `boolean` | ні | false — правила валідні за схемою, але ця реалізація колектора не виконує стратегію або її опцію (наприклад llm_explore, незареєстрована стратегія чи правила іншого колектора). Попередження містять точні JSON Pointer (`code: unsupported_strategy`); запуск збору з такими правилами повертає 422 validation_failed. Опції api_feed `method: POST` і `emit_items_as_materials: true` Web Collector виконує з WP-16. |
| `errors` | array of `FieldError` | так |  |
| `errors[].pointer` | `string` | ні | JSON Pointer (RFC 6901) до поля тіла запиту, наприклад '/stages/2/handler/version'. |
| `errors[].parameter` | `string` | ні | Ім'я query/path/header параметра. |
| `errors[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `errors[].message` | `string` | так |  |
| `warnings` | array of `FieldError` | ні |  |
| `warnings[].pointer` | `string` | ні | JSON Pointer (RFC 6901) до поля тіла запиту, наприклад '/stages/2/handler/version'. |
| `warnings[].parameter` | `string` | ні | Ім'я query/path/header параметра. |
| `warnings[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `warnings[].message` | `string` | так |  |

Приклад `ok`:

```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    {
      "pointer": "/strategies/1",
      "message": "recursive strategy without max_depth inherits limits.crawl.max_depth"
    }
  ],
  "supported": true
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `400`, `401`.
