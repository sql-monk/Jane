# GET /v1/info

> Згенеровано `scripts/docs_reference.py` з [common.yaml](../../../../../contracts/openapi/common.yaml#L459). Не редагуйте вручну.

**Версія, підтримувані версії API й можливості сервісу**

| Властивість | Значення |
|---|---|
| operationId | `getServiceInfo` |
| Метод і шлях | `GET /v1/info` |
| Scope | без автентифікації |
| Ідемпотентність | — |
| Теги | system |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Опис сервісу. | `ServiceInfo` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `service` | `string` | так | Ім'я сервісу, наприклад `web-collector`. |
| `version` | `string` | так | Версія збірки сервісу. |
| `api_versions` | array of `string` | так |  |
| `capabilities` | `object` | ні | Можливості конкретної реалізації (наприклад підтримувані стратегії, типи обробників, адаптери). |
| `auth_mode` | enum: `none`, `api_key`, `jwt` | ні |  |
| `limits` | `PlatformLimits` | ні | Ліміти, налаштовані в цьому сервісі (типові значення й hard_caps), у формі PlatformLimits. Ефективні ліміти для конкретного джерела/завдання/етапу обчислює лише оркестратор (`GET /v1/limits/effective`); автономний сервіс застосовує min(limits із запиту, свої hard_caps). |
| `limits.profile` | `string` | ні | Ім'я профілю середовища, з якого взято значення (див. docs/adr/0007-target-environments.md). |
| `limits.defaults` | `limits` | так | Модель лімітів з успадкуванням (ТЗ §13.1 п.5, критерій 13). Один і той самий об'єкт Limits задається на рівнях platform → source → task → stage; кожне поле необов'язкове. Ефективне значення: глибоке злиття за рівнями, нижчий рівень перекриває вищий; відсутнє поле успадковується (null заборонено — щоб 'скинути' до успадкованого, поле просто не передають). Після злиття кожне числове поле обмежується platform.hard_caps (min). Під час виконання значення додатково лише звужуються обмеженнями конкретного сайту чи сервісу (robots.txt Crawl-delay, Retry-After, Telegram flood-wait, ліміти провайдера LLM) — вони ніколи не послаблюються конфігурацією. Сервіс, що отримав limits у запиті (автономний режим), застосовує min(ліміти запиту, власні hard_caps). Типові значення — у сервісних конфігураціях і профілях WP-14; довідковий профіль — contracts/examples/schemas/limits/*.json. |
| `limits.defaults.concurrency` | `object` | ні |  |
| `limits.defaults.rate` | `object` | ні |  |
| `limits.defaults.crawl` | `object` | ні |  |
| `limits.defaults.timeouts` | `object` | ні |  |
| `limits.defaults.retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `limits.defaults.queue` | `object` | ні |  |
| `limits.defaults.sandbox` | `object` | ні |  |
| `limits.defaults.llm` | `object` | ні |  |
| `limits.defaults.transfer` | `object` | ні |  |
| `limits.defaults.telegram` | `object` | ні |  |
| `limits.hard_caps` | `limits` | ні | Модель лімітів з успадкуванням (ТЗ §13.1 п.5, критерій 13). Один і той самий об'єкт Limits задається на рівнях platform → source → task → stage; кожне поле необов'язкове. Ефективне значення: глибоке злиття за рівнями, нижчий рівень перекриває вищий; відсутнє поле успадковується (null заборонено — щоб 'скинути' до успадкованого, поле просто не передають). Після злиття кожне числове поле обмежується platform.hard_caps (min). Під час виконання значення додатково лише звужуються обмеженнями конкретного сайту чи сервісу (robots.txt Crawl-delay, Retry-After, Telegram flood-wait, ліміти провайдера LLM) — вони ніколи не послаблюються конфігурацією. Сервіс, що отримав limits у запиті (автономний режим), застосовує min(ліміти запиту, власні hard_caps). Типові значення — у сервісних конфігураціях і профілях WP-14; довідковий профіль — contracts/examples/schemas/limits/*.json. |
| `limits.hard_caps.concurrency` | `object` | ні |  |
| `limits.hard_caps.rate` | `object` | ні |  |
| `limits.hard_caps.crawl` | `object` | ні |  |
| `limits.hard_caps.timeouts` | `object` | ні |  |
| `limits.hard_caps.retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `limits.hard_caps.queue` | `object` | ні |  |
| `limits.hard_caps.sandbox` | `object` | ні |  |
| `limits.hard_caps.llm` | `object` | ні |  |
| `limits.hard_caps.transfer` | `object` | ні |  |
| `limits.hard_caps.telegram` | `object` | ні |  |

Приклад `info`:

```json
{
  "service": "example-service",
  "version": "0.1.0",
  "api_versions": [
    "v1"
  ],
  "capabilities": {},
  "auth_mode": "jwt"
}
```

Приклад `assistantCi`:

```json
{
  "service": "assistant",
  "version": "0.1.0",
  "api_versions": [
    "v1"
  ],
  "capabilities": {},
  "auth_mode": "jwt",
  "limits": {
    "profile": "ci",
    "defaults": {
      "concurrency": {
        "max_parallel_fetches": 4,
        "max_parallel_fetches_per_host": 2,
        "max_parallel_invocations": 2,
        "max_parallel_runs_per_task": 1,
        "max_parallel_stage_items": 2
      },
      "rate": {
        "requests_per_second_per_host": 50,
        "min_delay_ms_per_host": 0,
        "burst_per_host": 10,
        "respect_crawl_delay": true
      },
      "crawl": {
        "max_depth": 5,
        "max_pages_per_run": 5000,
        "max_bytes_per_run": 2147483648,
        "max_material_bytes": 10485760,
        "max_redirects": 5,
        "max_links_per_page": 2000,
        "max_seed_urls": 100000,
        "max_frontier_size": 100000,
        "revisit_interval_seconds": 86400
      },
      "timeouts": {
        "connect_timeout_ms": 10000,
        "request_timeout_ms": 30000,
        "invocation_timeout_ms": 60000,
        "stage_timeout_ms": 3600000,
        "run_timeout_ms": 21600000,
        "sync_response_max_ms": 25000
      },
      "retries": {
        "max_attempts": 3,
        "initial_backoff_ms": 1000,
        "max_backoff_ms": 60000,
        "backoff_multiplier": 2,
        "jitter": true
      },
      "queue": {
        "max_queue_depth": 10000,
        "max_inflight_materials": 100,
        "max_unacked_materials": 500
      },
      "sandbox": {
        "cpu_cores": 1,
        "memory_mb": 512,
        "wall_time_ms": 30000,
        "max_output_bytes": 4194304,
        "max_processes": 16,
        "tmpfs_mb": 64
      },
      "llm": {
        "max_requests_per_minute": 20,
        "max_input_tokens_per_request": 32000,
        "max_output_tokens_per_request": 4096,
        "budget": {
          "amount": 0.01,
          "currency": "USD",
          "period": "day"
        },
        "max_improvement_attempts": 3,
        "max_onboarding_samples": 60,
        "min_onboarding_confidence": 0.8
      },
      "transfer": {
        "inline_max_bytes": 262144,
        "max_request_body_bytes": 16777216,
        "transit_ttl_seconds": 604800,
        "download_url_ttl_seconds": 3600,
        "job_retention_seconds": 604800,
        "idempotency_ttl_seconds": 86400
      },
      "telegram": {
        "max_messages_per_run": 10000,
        "max_media_bytes": 20971520,
        "max_flood_wait_seconds": 600
      }
    },
    "hard_caps": {
      "sandbox": {
        "memory_mb": 1024,
        "cpu_cores": 1,
        "wall_time_ms": 60000
      }
    }
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
