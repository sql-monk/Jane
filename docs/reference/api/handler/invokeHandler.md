# POST /v1/invocations

> Згенеровано `scripts/docs_reference.py` з [handler.v1.yaml](../../../../contracts/openapi/handler.v1.yaml#L54). Не редагуйте вручну.

**Виконати обробник над вхідними даними**

| Властивість | Значення |
|---|---|
| operationId | `invokeHandler` |
| Метод і шлях | `POST /v1/invocations` |
| Scope | `handler:invoke` |
| Ідемпотентність | обов'язковий `Idempotency-Key` |
| Теги | invocations |

`mode: sync` — 200 з HandlerResult (або 202, якщо не вклалося в `limits.timeouts.sync_response_max_ms`); `mode: async` — одразу 202, результат — `Job.result` (HandlerResult) за `GET /v1/jobs/{job_id}`. Виконавець бере пакет із `package_archive` або з репозиторію за `handler` і перевіряє дайджест, якщо його задано.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `Idempotency-Key` | header | `string` | так | Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований ключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь (заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом — 422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress` (retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`. |
| `traceparent` | header | `string` | ні | W3C Trace Context; сервіс продовжує трасу й передає її далі. |

## Тіло запиту

Тип вмісту `application/json`, схема `handler-invocation`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `handler` | `package-ref` | так | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `handler.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `handler.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `handler.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `package_archive` | `InlineContent` \| `BlobContent` | ні | Необов'язковий архів пакета (автономний режим або тест чернетки без репозиторію). Якщо handler.digest заданий — виконавець перевіряє збіг дайджесту архіву. |
| `params` | `object` | ні | Параметри етапу; валідуються за params_schema маніфесту пакета. |
| `inputs` | array of `MaterialInput` \| `EntitiesInput` \| `DataInput` | так | мін. елементів `1` |
| `connections` | `object` | ні | Логічне ім'я з required_connections маніфесту → connection_id, відомий виконавцю. Значення секретів сюди не передаються. |
| `context` | `InvocationContext` | ні |  |
| `context.trace` | `TraceContext` | ні | Контекст простежуваності, що передається між етапами. Поля HTTP-заголовків W3C 'traceparent'/'tracestate' мають пріоритет, якщо є. |
| `context.trace.trace_id` | `string` | ні | шаблон `"^[a-f0-9]{32}$"` |
| `context.trace.run_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `context.trace.task_id` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `context.trace.stage_id` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `context.trace.source_id` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `context.attempt` | `integer` | ні | Номер спроби (1 — перша).; мін. `1` |
| `context.test_mode` | `boolean` | ні | Режим тестування без запису в робочі дані (ТЗ §10): збереження виконує валідацію й повертає очікувані підтвердження без запису; LLM використовує той самий бюджет, але позначає витрати як тестові.; типово `false` |
| `context.requested_by` | `string` | ні |  |
| `delivery` | `Delivery` | так | Ідентичність доставки для ідемпотентності (ТЗ §11). delivery_key детермінований: повтор тієї самої доставки (після збою, повторної спроби) має той самий ключ, нове спостереження — новий. Рекомендоване правило оркестратора: sha256(run_id \| stage_id \| item_key), де item_key — observation_id вхідного матеріалу або '&lt;upstream invocation_id>/&lt;index>'. HTTP-заголовок Idempotency-Key дорівнює delivery_key. |
| `delivery.delivery_key` | `string` | так | мін. довжина `1`; макс. довжина `255` |
| `limits` | `limits` | ні | Ефективні ліміти етапу. Виконавець застосовує min(ці значення, власні hard_caps). |
| `limits.concurrency` | `object` | ні |  |
| `limits.concurrency.max_parallel_fetches` | `integer` | ні | Одночасні завантаження одного збору колектора (на збір: кожен збір окремо, на будь-якому екземплярі; спільний для всіх зборів ліміт хоста — max_parallel_fetches_per_host).; мін. `1` |
| `limits.concurrency.max_parallel_fetches_per_host` | `integer` | ні | Одночасні запити до одного хоста джерела (host[:port]) від усієї платформи: усіх зборів і одноразових запитів колектора разом, також усіх його екземплярів, що ділять сховище стану (один вузол, спільний каталог стану). Якщо активні на хості збори мають різні значення, діє найменше. Екземпляри з окремими сховищами стану — окремі колектори й між собою цей ліміт не узгоджують.; мін. `1` |
| `limits.concurrency.max_parallel_invocations` | `integer` | ні | Одночасні виклики обробника (на екземпляр сервісу-виконавця або на етап).; мін. `1` |
| `limits.concurrency.max_parallel_runs_per_task` | `integer` | ні | Скільки запусків одного завдання можуть іти одночасно.; мін. `1` |
| `limits.concurrency.max_parallel_stage_items` | `integer` | ні | Скільки елементів один етап запуску обробляє одночасно.; мін. `1` |
| `limits.rate` | `object` | ні |  |
| `limits.rate.requests_per_second_per_host` | `number` | ні | Частота стартів запитів до одного хоста джерела; область дії — як у concurrency.max_parallel_fetches_per_host (уся платформа: усі збори, одноразові запити й екземпляри зі спільним сховищем стану). Інтервал між стартами = max(1 / requests_per_second_per_host, min_delay_ms_per_host, Crawl-delay за respect_crawl_delay); між активними на хості зборами діє найбільший інтервал. |
| `limits.rate.min_delay_ms_per_host` | `integer` | ні | Мінімальний інтервал між стартами запитів до одного хоста джерела; область дії у Web Collector — як у requests_per_second_per_host. Telegram Collector (єдиний «хост» — API Telegram) застосовує його до викликів API одного збору.; мін. `0` |
| `limits.rate.burst_per_host` | `integer` | ні | мін. `1` |
| `limits.rate.respect_crawl_delay` | `boolean` | ні | Враховувати Crawl-delay з robots.txt (може лише збільшити затримку). |
| `limits.crawl` | `object` | ні |  |
| `limits.crawl.max_depth` | `integer` | ні | мін. `0` |
| `limits.crawl.max_pages_per_run` | `integer` | ні | мін. `1` |
| `limits.crawl.max_bytes_per_run` | `integer` | ні | мін. `1` |
| `limits.crawl.max_material_bytes` | `integer` | ні | Більший матеріал обривається з діагностикою 'truncated' або відкидається (за налаштуванням колектора).; мін. `1` |
| `limits.crawl.max_redirects` | `integer` | ні | мін. `0` |
| `limits.crawl.max_links_per_page` | `integer` | ні | мін. `0` |
| `limits.crawl.max_seed_urls` | `integer` | ні | Максимальна кількість URL у явному переліку (TaskInput.urls, CollectionRequest.urls, seed_list).; мін. `1` |
| `limits.crawl.max_frontier_size` | `integer` | ні | Максимальна кількість URL у черзі обходу.; мін. `1` |
| `limits.crawl.revisit_interval_seconds` | `integer` | ні | Мінімальний інтервал повторного відвідування того самого URL.; мін. `0` |
| `limits.timeouts` | `object` | ні |  |
| `limits.timeouts.connect_timeout_ms` | `integer` | ні | мін. `1` |
| `limits.timeouts.request_timeout_ms` | `integer` | ні | мін. `1` |
| `limits.timeouts.invocation_timeout_ms` | `integer` | ні | Тайм-аут одного виклику обробника (вкл. пісочницю).; мін. `1` |
| `limits.timeouts.stage_timeout_ms` | `integer` | ні | мін. `1` |
| `limits.timeouts.run_timeout_ms` | `integer` | ні | мін. `1` |
| `limits.timeouts.sync_response_max_ms` | `integer` | ні | Якщо синхронна операція не встигає — сервіс повертає 202 + Job.; мін. `1` |
| `limits.retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `limits.retries.max_attempts` | `integer` | ні | Загальна кількість спроб, включно з першою.; мін. `1` |
| `limits.retries.initial_backoff_ms` | `integer` | ні | мін. `0` |
| `limits.retries.max_backoff_ms` | `integer` | ні | мін. `0` |
| `limits.retries.backoff_multiplier` | `number` | ні | мін. `1` |
| `limits.retries.jitter` | `boolean` | ні |  |
| `limits.queue` | `object` | ні |  |
| `limits.queue.max_queue_depth` | `integer` | ні | Максимальна кількість задач у черзі оркестратора для завдання; при переповненні збір пригальмовується (backpressure).; мін. `1` |
| `limits.queue.max_inflight_materials` | `integer` | ні | Скільки матеріалів одного запуску можуть одночасно перебувати в обробці.; мін. `1` |
| `limits.queue.max_unacked_materials` | `integer` | ні | Розмір буфера колектора: скільки отриманих, але ще не забраних споживачем матеріалів він тримає, перш ніж призупинити обхід.; мін. `1` |
| `limits.sandbox` | `object` | ні |  |
| `limits.sandbox.cpu_cores` | `number` | ні |  |
| `limits.sandbox.memory_mb` | `integer` | ні | мін. `16` |
| `limits.sandbox.wall_time_ms` | `integer` | ні | мін. `1` |
| `limits.sandbox.max_output_bytes` | `integer` | ні | мін. `1` |
| `limits.sandbox.max_processes` | `integer` | ні | мін. `1` |
| `limits.sandbox.tmpfs_mb` | `integer` | ні | мін. `0` |
| `limits.llm` | `object` | ні |  |
| `limits.llm.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `limits.llm.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.llm.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.llm.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `limits.llm.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `limits.llm.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `limits.llm.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |
| `limits.transfer` | `object` | ні |  |
| `limits.transfer.inline_max_bytes` | `integer` | ні | Вміст до цього розміру можна передавати inline; більший — лише blob.; мін. `0` |
| `limits.transfer.max_request_body_bytes` | `integer` | ні | мін. `1` |
| `limits.transfer.transit_ttl_seconds` | `integer` | ні | Час життя транзитних blob-об'єктів.; мін. `60` |
| `limits.transfer.download_url_ttl_seconds` | `integer` | ні | мін. `1` |
| `limits.transfer.job_retention_seconds` | `integer` | ні | мін. `60` |
| `limits.transfer.idempotency_ttl_seconds` | `integer` | ні | Скільки сервіс пам'ятає Idempotency-Key для повтору відповіді.; мін. `60` |
| `limits.telegram` | `object` | ні |  |
| `limits.telegram.max_messages_per_run` | `integer` | ні | мін. `1` |
| `limits.telegram.max_media_bytes` | `integer` | ні | мін. `0` |
| `limits.telegram.max_flood_wait_seconds` | `integer` | ні | Якщо Telegram вимагає чекати довше — збір призупиняється з помилкою rate_limited замість блокування воркера.; мін. `0` |
| `mode` | enum: `sync`, `async` | ні | sync — чекати результат (200); async — одразу 202 + Job. Навіть для sync сервіс може повернути 202, якщо не вкладається в limits.timeouts.sync_response_max_ms.; типово `"sync"` |

Приклад `extract`:

```json
{
  "handler": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0",
    "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
  },
  "params": {
    "currency_default": "UAH"
  },
  "inputs": [
    {
      "kind": "material",
      "material": {
        "material_id": "web:3704326c60776c53169680099e2eed31",
        "observation_id": "obs_01J9ZQ4A0000000000000001",
        "source": {
          "source_id": "shop-example",
          "kind": "web",
          "name": "Shop Example"
        },
        "locator": {
          "url": "https://shop.example.test/product/a-100",
          "final_url": "https://shop.example.test/product/a-100",
          "canonical_url": "https://shop.example.test/product/a-100"
        },
        "fetched_at": "2026-09-27T10:00:05Z",
        "format": {
          "media_type": "text/html",
          "charset": "utf-8",
          "language": "uk",
          "content_kind": "page"
        },
        "revision": {
          "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07",
          "source_revision": "\"etag-a100-v3\""
        },
        "content": {
          "kind": "inline",
          "media_type": "text/html",
          "encoding": "utf-8",
          "data": "<html><head><title>Kettle A-100</title></head><body><h1>Kettle A-100</h1><span class=\"price\">1299.00 UAH</span><span class=\"stock\">in stock</span></body></html>",
          "size_bytes": 160,
          "sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
        },
        "http": {
          "status": 200,
          "headers": {
            "content-type": "text/html; charset=utf-8",
            "etag": "\"etag-a100-v3\""
          }
        },
        "discovery": {
          "strategy": "sitemap",
          "depth": 0,
          "section": "products",
          "priority": 10
        },
        "collector": {
          "name": "web-collector",
          "version": "0.1.0",
          "rules": {
            "package_id": "shop-example.web-rules",
            "version": "1.0.0",
            "digest": "sha256:bd33d6b0fb860947abb60fbf898610d7ad28e279daf21106399995dcd911674a"
          },
          "collection_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F"
        },
        "metadata": {
          "title": "Kettle A-100"
        }
      }
    }
  ],
  "context": {
    "trace": {
      "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
      "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
      "task_id": "shop-catalog",
      "stage_id": "extract-products",
      "source_id": "shop-example"
    },
    "attempt": 1,
    "test_mode": false
  },
  "delivery": {
    "delivery_key": "4e0f59b654487ead879d66581cc35e08fa0e764526255ce939f572a8844b2699"
  },
  "limits": {
    "sandbox": {
      "cpu_cores": 1,
      "memory_mb": 512,
      "wall_time_ms": 20000,
      "max_output_bytes": 1048576
    },
    "timeouts": {
      "invocation_timeout_ms": 30000,
      "sync_response_max_ms": 25000
    }
  },
  "mode": "sync"
}
```

Приклад `store`:

```json
{
  "handler": {
    "package_id": "jane.storage-postgresql",
    "version": "1.0.0",
    "digest": "sha256:8751adf49b3d26c9a59f6ecc83f52feccc0edade6db1a98c1a0155b0380a045b"
  },
  "params": {
    "table_prefix": "shop_"
  },
  "inputs": [
    {
      "kind": "entities",
      "entities": [
        {
          "entity_type": "product",
          "schema": "shop-example.product-extractor@1.2.0#product",
          "key": {
            "scope": "shop-example",
            "natural": {
              "sku": "A-100"
            }
          },
          "fields": {
            "sku": "A-100",
            "title": "Kettle A-100",
            "price": {
              "amount": 1299.0,
              "currency": "UAH"
            },
            "availability": "in_stock",
            "url": "https://shop.example.test/product/a-100"
          },
          "completeness": "full",
          "observation": {
            "observation_id": "obs_01J9ZQ4A0000000000000001",
            "observed_at": "2026-09-27T10:00:05Z",
            "material_id": "web:3704326c60776c53169680099e2eed31",
            "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
          },
          "provenance": {
            "package": {
              "package_id": "shop-example.product-extractor",
              "version": "1.2.0",
              "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
            },
            "invocation_id": "inv_01J9ZQ4B00000000000000A1",
            "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
            "stage_id": "extract-products"
          },
          "confidence": 0.98
        }
      ],
      "from_invocation_id": "inv_01J9ZQ4B00000000000000A1"
    }
  ],
  "connections": {
    "target": "results-pg"
  },
  "context": {
    "trace": {
      "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
      "task_id": "shop-catalog",
      "stage_id": "store-products",
      "source_id": "shop-example"
    },
    "attempt": 2
  },
  "delivery": {
    "delivery_key": "f3ce262f5fc6e6c0e84e0f993688161677dfee6ff663a4b60cbd5d6a12ff03bf"
  }
}
```

Приклад `localTest`:

```json
{
  "handler": {
    "package_id": "shop-example.product-extractor",
    "version": "1.3.0-draft.1"
  },
  "package_archive": {
    "kind": "blob",
    "uri": "file:///var/lib/jane/drafts/product-extractor-1.3.0-draft.1.zip",
    "media_type": "application/zip",
    "size_bytes": 18422,
    "sha256": "78cb506de56864fed15e4c936b0c6481a2653a9fe9000e48fd281fea26a5b758"
  },
  "inputs": [
    {
      "kind": "material",
      "material": {
        "material_id": "web:3704326c60776c53169680099e2eed31",
        "observation_id": "obs_01J9ZQ4A0000000000000001",
        "source": {
          "source_id": "shop-example",
          "kind": "web",
          "name": "Shop Example"
        },
        "locator": {
          "url": "https://shop.example.test/product/a-100",
          "final_url": "https://shop.example.test/product/a-100",
          "canonical_url": "https://shop.example.test/product/a-100"
        },
        "fetched_at": "2026-09-27T10:00:05Z",
        "format": {
          "media_type": "text/html",
          "charset": "utf-8",
          "language": "uk",
          "content_kind": "page"
        },
        "revision": {
          "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07",
          "source_revision": "\"etag-a100-v3\""
        },
        "content": {
          "kind": "inline",
          "media_type": "text/html",
          "encoding": "utf-8",
          "data": "<html><head><title>Kettle A-100</title></head><body><h1>Kettle A-100</h1><span class=\"price\">1299.00 UAH</span><span class=\"stock\">in stock</span></body></html>",
          "size_bytes": 160,
          "sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
        },
        "http": {
          "status": 200,
          "headers": {
            "content-type": "text/html; charset=utf-8",
            "etag": "\"etag-a100-v3\""
          }
        },
        "discovery": {
          "strategy": "sitemap",
          "depth": 0,
          "section": "products",
          "priority": 10
        },
        "collector": {
          "name": "web-collector",
          "version": "0.1.0",
          "rules": {
            "package_id": "shop-example.web-rules",
            "version": "1.0.0",
            "digest": "sha256:bd33d6b0fb860947abb60fbf898610d7ad28e279daf21106399995dcd911674a"
          },
          "collection_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F"
        },
        "metadata": {
          "title": "Kettle A-100"
        }
      }
    }
  ],
  "context": {
    "attempt": 1,
    "test_mode": true,
    "requested_by": "admin@example.org"
  },
  "delivery": {
    "delivery_key": "test-01J9ZU0000000000000000001"
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Обробник виконано (будь-який із чотирьох станів). | `handler-result` |
| `202` | Операцію прийнято до асинхронного виконання. | `job` |
| `400` | Некоректний синтаксис запиту (`bad_request`). | `problem` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Пакет або підключення не знайдено (`not_found`). | `problem` |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | `problem` |
| `413` | Тіло перевищує `limits.transfer.max_request_body_bytes` — передайте вміст як blob (`payload_too_large`). | `problem` |
| `422` | Невалідний запит, параметри не відповідають params_schema, `digest_mismatch`, `dependency_not_allowed`, `idempotency_key_reused`. | `problem` |
| `429` | Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`). | `problem` |
| `502` | Недоступний репозиторій, сховище чи провайдер LLM (`upstream_unavailable`). | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `invocation_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `handler` | `package-ref` | так | Фактично виконана версія (digest заповнено завжди). |
| `handler.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `handler.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `handler.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `handler_kind` | enum: `extractor`, `storage`, `llm`, `transform`, `collector-rules` | так | Тип обробника (і пакета). 'collector-rules' — правила колектора, що версіонуються в тому самому репозиторії. |
| `status` | enum: `success`, `empty`, `unrecognized`, `failed` | так |  |
| `inputs` | array of `InputRef` | так | Посилання на вхідні дані в порядку запиту. |
| `inputs[].kind` | enum: `material`, `entities`, `data` | так |  |
| `inputs[].material_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `inputs[].observation_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `inputs[].content_sha256` | `string` | ні | шаблон `"^[a-f0-9]{64}$"` |
| `inputs[].from_invocation_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `output` | `HandlerOutput` | ні | Вихід за типом обробника: extractor — entities; llm — data (+ usage); storage — writes; transform — data або entities. Великий вихід — через *_ref. |
| `output.entities` | array of `entity` | ні |  |
| `output.entities[].entity_type` | `string` | так | Тип сутності зі схеми результату пакета (наприклад 'product', 'price', 'event').; шаблон `"^[a-z][a-z0-9_]{0,63}$"` |
| `output.entities[].schema` | `string` | ні | Посилання на схему сутності всередині пакета: '&lt;package_id>@&lt;version>#&lt;entity_type>'. |
| `output.entities[].key` | `EntityKey` | так | Ідентичність об'єкта. natural — значення ключових полів схеми (наприклад {"sku": "A-1"}); scope — простір імен (зазвичай source_id), щоб однакові SKU різних джерел не злилися. Сховище будує канонічний рядок ключа: scope + '\|' + пари natural, відсортовані за іменем, серіалізовані як JSON без пробілів. |
| `output.entities[].fields` | `object` | так | Значення полів. Відсутнє поле — без змін; null заборонено (для очищення — 'cleared'). |
| `output.entities[].cleared` | array of `string` | ні | Поля, які треба явно очистити в поточному стані. |
| `output.entities[].completeness` | enum: `full`, `partial` | ні | full — обробник заявляє, що передав усі поля, які знайшов у матеріалі (інформативно; семантику злиття не змінює); partial — лише частину полів (наприклад, завдання перевірки ціни).; типово `"partial"` |
| `output.entities[].observation` | `ObservationOrder` | так | Порядок спостережень. Порівняння: спочатку observed_at (час отримання матеріалу колектором), потім sequence (ревізія джерела, якщо є), потім observation_id лексикографічно. Більше — новіше. Час обробки чи доставки в порівнянні не бере участі. |
| `output.entities[].provenance` | `Provenance` | ні |  |
| `output.entities[].confidence` | `number` | ні | мін. `0`; макс. `1` |
| `output.entities_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `output.data` | — | ні |  |
| `output.data_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `output.writes` | array of `WriteAck` | ні |  |
| `output.writes[].status` | enum: `written`, `duplicate`, `stale`, `partially_stale`, `simulated` | так | written — записано; duplicate — цей delivery_key уже записано, повтор без ефекту; stale — запізніле спостереження, лише в історії; partially_stale — частину полів застосовано, частину ні; simulated — test_mode, запису не було. |
| `output.writes[].target` | `object` | так |  |
| `output.writes[].object` | `StoredObjectRef` | ні | Посилання на збережений об'єкт (RAW або документ результатів), за яким його можна прочитати через storage API або повторно обробити. |
| `output.writes[].entity` | `object` | ні |  |
| `output.writes[].applied_fields` | array of `string` | ні |  |
| `output.writes[].stale_fields` | array of `string` | ні |  |
| `output.writes[].delivery_key` | `string` | ні |  |
| `unrecognized` | `object` | ні | Заповнюється, коли status = unrecognized. |
| `unrecognized.partial` | `boolean` | так | true — частину даних розібрано (вони в output), false — формат не розпізнано взагалі. |
| `unrecognized.reason` | `string` | ні |  |
| `unrecognized.signature` | `string` | ні | Короткий відбиток характеру проблеми для групування (наприклад 'missing-selector:.price'). |
| `failure` | `object` | ні | Заповнюється, коли status = failed. |
| `failure.kind` | enum: `execution_error`, `schema_mismatch`, `timeout`, `resource_exceeded`, `sandbox_violation`, `dependency_error`, `connection_error`, `budget_exhausted`, `invalid_params` | так |  |
| `failure.message` | `string` | так |  |
| `failure.retryable` | `boolean` | ні |  |
| `failure.details` | `object` | ні |  |
| `diagnostics` | `Diagnostics` | ні |  |
| `diagnostics.messages` | array of `DiagnosticMessage` | ні |  |
| `diagnostics.messages[].level` | enum: `debug`, `info`, `warning`, `error` | так |  |
| `diagnostics.messages[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_.-]{0,127}$"` |
| `diagnostics.messages[].message` | `string` | так | макс. довжина `4000` |
| `diagnostics.messages[].pointer` | `string` | ні | JSON Pointer у вихідних даних (наприклад '/entities/3/fields/price'). |
| `diagnostics.messages[].material_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `diagnostics.messages[].selector` | `string` | ні | CSS/XPath/JSONPath, з яким пов'язано повідомлення (для екстракторів). |
| `diagnostics.validation_errors` | array of `object` | ні | Невідповідності виходу схемі пакета (для failure.kind = schema_mismatch). |
| `diagnostics.validation_errors[].pointer` | `string` | так |  |
| `diagnostics.validation_errors[].message` | `string` | так |  |
| `diagnostics.validation_errors[].schema_pointer` | `string` | ні |  |
| `diagnostics.metrics` | `object` | ні |  |
| `diagnostics.metrics.duration_ms` | `integer` | ні | мін. `0` |
| `diagnostics.metrics.cpu_ms` | `integer` | ні | мін. `0` |
| `diagnostics.metrics.peak_memory_mb` | `number` | ні | мін. `0` |
| `diagnostics.metrics.output_bytes` | `integer` | ні | мін. `0` |
| `diagnostics.logs_ref` | `InlineContent` \| `BlobContent` | ні | stdout/stderr виконання (обрізані до limits.sandbox.max_output_bytes). |
| `usage` | `Usage` | ні |  |
| `usage.llm` | `object` | ні |  |
| `usage.llm.provider` | `string` | ні |  |
| `usage.llm.model` | `string` | ні |  |
| `usage.llm.input_tokens` | `integer` | ні | мін. `0` |
| `usage.llm.output_tokens` | `integer` | ні | мін. `0` |
| `usage.llm.cost` | `Money` | ні |  |
| `delivery_key` | `string` | ні |  |
| `duplicate` | `boolean` | ні | true — цей delivery_key уже виконано; повернуто збережений результат без повторного ефекту. |
| `test_mode` | `boolean` | ні |  |
| `started_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `finished_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |

Приклад `success`:

```json
{
  "invocation_id": "inv_01J9ZQ4B00000000000000A1",
  "handler": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0",
    "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
  },
  "handler_kind": "extractor",
  "status": "success",
  "inputs": [
    {
      "kind": "material",
      "material_id": "web:3704326c60776c53169680099e2eed31",
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
    }
  ],
  "output": {
    "entities": [
      {
        "entity_type": "product",
        "schema": "shop-example.product-extractor@1.2.0#product",
        "key": {
          "scope": "shop-example",
          "natural": {
            "sku": "A-100"
          }
        },
        "fields": {
          "sku": "A-100",
          "title": "Kettle A-100",
          "price": {
            "amount": 1299.0,
            "currency": "UAH"
          },
          "availability": "in_stock",
          "url": "https://shop.example.test/product/a-100"
        },
        "completeness": "full",
        "observation": {
          "observation_id": "obs_01J9ZQ4A0000000000000001",
          "observed_at": "2026-09-27T10:00:05Z",
          "material_id": "web:3704326c60776c53169680099e2eed31",
          "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
        },
        "provenance": {
          "package": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.0",
            "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
          },
          "invocation_id": "inv_01J9ZQ4B00000000000000A1",
          "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
          "stage_id": "extract-products"
        },
        "confidence": 0.98
      }
    ]
  },
  "diagnostics": {
    "messages": [
      {
        "level": "info",
        "code": "extract.selector_fallback",
        "message": "used og:title as title fallback",
        "material_id": "web:3704326c60776c53169680099e2eed31"
      }
    ],
    "metrics": {
      "duration_ms": 412,
      "cpu_ms": 180,
      "peak_memory_mb": 61.5,
      "output_bytes": 812
    }
  },
  "delivery_key": "4e0f59b654487ead879d66581cc35e08fa0e764526255ce939f572a8844b2699",
  "duplicate": false,
  "test_mode": false,
  "started_at": "2026-09-27T10:00:06Z",
  "finished_at": "2026-09-27T10:00:06.412Z"
}
```

Приклад `empty`:

```json
{
  "invocation_id": "inv_01J9ZQ4B00000000000000A2",
  "handler": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0",
    "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
  },
  "handler_kind": "extractor",
  "status": "empty",
  "inputs": [
    {
      "kind": "material",
      "material_id": "web:3704326c60776c53169680099e2eed31",
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
    }
  ],
  "output": {
    "entities": []
  },
  "diagnostics": {
    "messages": [
      {
        "level": "info",
        "code": "extract.no_products",
        "message": "category page without product cards"
      }
    ]
  },
  "delivery_key": "4e0f59b654487ead879d66581cc35e08fa0e764526255ce939f572a8844b2699",
  "duplicate": false,
  "test_mode": false,
  "started_at": "2026-09-27T10:00:06Z",
  "finished_at": "2026-09-27T10:00:06.412Z"
}
```

Приклад `unrecognized`:

```json
{
  "invocation_id": "inv_01J9ZQ4B00000000000000A3",
  "handler": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0",
    "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
  },
  "handler_kind": "extractor",
  "status": "unrecognized",
  "inputs": [
    {
      "kind": "material",
      "material_id": "web:3704326c60776c53169680099e2eed31",
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
    }
  ],
  "output": {
    "entities": [
      {
        "entity_type": "product",
        "schema": "shop-example.product-extractor@1.2.0#product",
        "key": {
          "scope": "shop-example",
          "natural": {
            "sku": "A-100"
          }
        },
        "fields": {
          "sku": "A-100",
          "title": "Kettle A-100"
        },
        "completeness": "partial",
        "observation": {
          "observation_id": "obs_01J9ZQ4A0000000000000001",
          "observed_at": "2026-09-27T10:00:05Z",
          "material_id": "web:3704326c60776c53169680099e2eed31",
          "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
        },
        "provenance": {
          "package": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.0",
            "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
          },
          "invocation_id": "inv_01J9ZQ4B00000000000000A1",
          "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
          "stage_id": "extract-products"
        },
        "confidence": 0.98
      }
    ]
  },
  "diagnostics": {
    "messages": [
      {
        "level": "warning",
        "code": "extract.missing_selector",
        "message": "selector .price matched 0 elements",
        "selector": ".price",
        "material_id": "web:3704326c60776c53169680099e2eed31"
      }
    ]
  },
  "delivery_key": "4e0f59b654487ead879d66581cc35e08fa0e764526255ce939f572a8844b2699",
  "duplicate": false,
  "test_mode": false,
  "started_at": "2026-09-27T10:00:06Z",
  "finished_at": "2026-09-27T10:00:06.412Z",
  "unrecognized": {
    "partial": true,
    "reason": "price block not found",
    "signature": "missing-selector:.price"
  }
}
```

Приклад `failedSchema`:

```json
{
  "invocation_id": "inv_01J9ZQ4B00000000000000A4",
  "handler": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0",
    "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
  },
  "handler_kind": "extractor",
  "status": "failed",
  "inputs": [
    {
      "kind": "material",
      "material_id": "web:3704326c60776c53169680099e2eed31",
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
    }
  ],
  "output": {
    "entities": []
  },
  "diagnostics": {
    "validation_errors": [
      {
        "pointer": "/entities/0/fields/price/amount",
        "message": "'1 299,00' is not of type 'number'",
        "schema_pointer": "/properties/price/properties/amount/type"
      }
    ],
    "metrics": {
      "duration_ms": 390
    }
  },
  "delivery_key": "4e0f59b654487ead879d66581cc35e08fa0e764526255ce939f572a8844b2699",
  "duplicate": false,
  "test_mode": false,
  "started_at": "2026-09-27T10:00:06Z",
  "finished_at": "2026-09-27T10:00:06.412Z",
  "failure": {
    "kind": "schema_mismatch",
    "message": "1 entity does not match schema product",
    "retryable": false
  }
}
```

Приклад `failedTimeout`:

```json
{
  "invocation_id": "inv_01J9ZQ4B00000000000000A5",
  "handler": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0",
    "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
  },
  "handler_kind": "extractor",
  "status": "failed",
  "inputs": [
    {
      "kind": "material",
      "material_id": "web:3704326c60776c53169680099e2eed31",
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
    }
  ],
  "output": {},
  "diagnostics": {
    "metrics": {
      "duration_ms": 20004
    }
  },
  "delivery_key": "4e0f59b654487ead879d66581cc35e08fa0e764526255ce939f572a8844b2699",
  "duplicate": false,
  "test_mode": false,
  "started_at": "2026-09-27T10:00:06Z",
  "finished_at": "2026-09-27T10:00:06.412Z",
  "failure": {
    "kind": "timeout",
    "message": "wall time limit 20000 ms exceeded; sandbox killed",
    "retryable": false,
    "details": {
      "wall_time_ms": 20000
    }
  }
}
```

Приклад `storageWritten`:

```json
{
  "invocation_id": "inv_01J9ZQ4C00000000000000C1",
  "handler": {
    "package_id": "jane.storage-postgresql",
    "version": "1.0.0",
    "digest": "sha256:8751adf49b3d26c9a59f6ecc83f52feccc0edade6db1a98c1a0155b0380a045b"
  },
  "handler_kind": "storage",
  "status": "success",
  "inputs": [
    {
      "kind": "entities",
      "from_invocation_id": "inv_01J9ZQ4B00000000000000A1"
    }
  ],
  "output": {
    "writes": [
      {
        "status": "written",
        "target": {
          "adapter": "postgresql",
          "connection_id": "results-pg"
        },
        "entity": {
          "entity_type": "product",
          "canonical_key": "shop-example|{\"sku\":\"A-100\"}",
          "version": 1
        },
        "applied_fields": [
          "availability",
          "price",
          "sku",
          "title",
          "url"
        ],
        "stale_fields": [],
        "delivery_key": "f3ce262f5fc6e6c0e84e0f993688161677dfee6ff663a4b60cbd5d6a12ff03bf"
      }
    ]
  },
  "delivery_key": "f3ce262f5fc6e6c0e84e0f993688161677dfee6ff663a4b60cbd5d6a12ff03bf",
  "duplicate": false,
  "test_mode": false,
  "started_at": "2026-09-27T10:00:07Z",
  "finished_at": "2026-09-27T10:00:07.050Z"
}
```

Приклад `storageDuplicate`:

```json
{
  "invocation_id": "inv_01J9ZQ4C00000000000000C1",
  "handler": {
    "package_id": "jane.storage-postgresql",
    "version": "1.0.0",
    "digest": "sha256:8751adf49b3d26c9a59f6ecc83f52feccc0edade6db1a98c1a0155b0380a045b"
  },
  "handler_kind": "storage",
  "status": "success",
  "inputs": [
    {
      "kind": "entities",
      "from_invocation_id": "inv_01J9ZQ4B00000000000000A1"
    }
  ],
  "output": {
    "writes": [
      {
        "status": "duplicate",
        "target": {
          "adapter": "postgresql",
          "connection_id": "results-pg"
        },
        "entity": {
          "entity_type": "product",
          "canonical_key": "shop-example|{\"sku\":\"A-100\"}",
          "version": 1
        },
        "applied_fields": [
          "availability",
          "price",
          "sku",
          "title",
          "url"
        ],
        "stale_fields": [],
        "delivery_key": "f3ce262f5fc6e6c0e84e0f993688161677dfee6ff663a4b60cbd5d6a12ff03bf"
      }
    ]
  },
  "delivery_key": "f3ce262f5fc6e6c0e84e0f993688161677dfee6ff663a4b60cbd5d6a12ff03bf",
  "duplicate": true,
  "test_mode": false,
  "started_at": "2026-09-27T10:00:07Z",
  "finished_at": "2026-09-27T10:00:07.050Z"
}
```

Приклад `storageStale`:

```json
{
  "invocation_id": "inv_01J9ZQ4C00000000000000C3",
  "handler": {
    "package_id": "jane.storage-postgresql",
    "version": "1.0.0",
    "digest": "sha256:8751adf49b3d26c9a59f6ecc83f52feccc0edade6db1a98c1a0155b0380a045b"
  },
  "handler_kind": "storage",
  "status": "success",
  "inputs": [
    {
      "kind": "entities",
      "from_invocation_id": "inv_01J9ZQ4B00000000000000A1"
    }
  ],
  "output": {
    "writes": [
      {
        "status": "stale",
        "target": {
          "adapter": "postgresql",
          "connection_id": "results-pg"
        },
        "entity": {
          "entity_type": "product",
          "canonical_key": "shop-example|{\"sku\":\"A-100\"}",
          "version": 2
        },
        "applied_fields": [],
        "stale_fields": [
          "availability",
          "price"
        ],
        "delivery_key": "089001a35679a33ef3db0ca350db9b9a2f0136e0e327577b04b3b98127470961"
      }
    ]
  },
  "delivery_key": "089001a35679a33ef3db0ca350db9b9a2f0136e0e327577b04b3b98127470961",
  "duplicate": false,
  "test_mode": false,
  "started_at": "2026-09-27T10:00:07Z",
  "finished_at": "2026-09-27T10:00:07.050Z"
}
```

Приклад `storageRaw`:

```json
{
  "invocation_id": "inv_01J9ZQ4C00000000000000C2",
  "handler": {
    "package_id": "jane.storage-files",
    "version": "1.0.0",
    "digest": "sha256:b2d691abc92053497acfe8f61d6cd32488b126a4aeb6e080c63d966ecd096a94"
  },
  "handler_kind": "storage",
  "status": "success",
  "inputs": [
    {
      "kind": "material",
      "material_id": "web:3704326c60776c53169680099e2eed31",
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
    }
  ],
  "output": {
    "writes": [
      {
        "status": "written",
        "target": {
          "adapter": "filesystem",
          "connection_id": "raw-files"
        },
        "object": {
          "object_id": "obj_01J9ZQ4C00000000000000D1",
          "adapter": "filesystem",
          "connection_id": "raw-files",
          "locator": {
            "path": "raw/shop-example/2026/09/27/web_3704326c60776c53169680099e2eed31/obs_01J9ZQ4A0000000000000001.html"
          },
          "media_type": "text/html",
          "size_bytes": 160,
          "sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
        },
        "delivery_key": "ad3d9ed239718c9b5beeb8ccb95cc602926cea0cf4ff7548925ef3cb42c72574"
      }
    ]
  },
  "started_at": "2026-09-27T10:00:07Z",
  "finished_at": "2026-09-27T10:00:07.020Z"
}
```

Приклад `llm`:

```json
{
  "invocation_id": "inv_01J9ZT0D00000000000000E1",
  "handler": {
    "package_id": "jane.llm-event-extractor",
    "version": "1.0.0",
    "digest": "sha256:3dcc2f9a7203d535c892df2884b4dbd27d3d159daba59d293bcf4bafbe603bb2"
  },
  "handler_kind": "llm",
  "status": "success",
  "inputs": [
    {
      "kind": "material",
      "material_id": "tg:-1001234567890:4521",
      "observation_id": "obs_01J9ZT0C0000000000000004"
    }
  ],
  "output": {
    "entities": [
      {
        "entity_type": "event",
        "key": {
          "scope": "news-tg",
          "natural": {
            "message": "tg:-1001234567890:4521"
          }
        },
        "fields": {
          "title": "Концерт",
          "starts_at": "2026-10-12T19:00:00+03:00",
          "venue": "Філармонія",
          "price": "free"
        },
        "observation": {
          "observation_id": "obs_01J9ZT0C0000000000000004",
          "observed_at": "2026-09-27T12:30:00Z",
          "sequence": 1790503800000,
          "material_id": "tg:-1001234567890:4521"
        }
      }
    ],
    "data": {
      "events": [
        {
          "title": "Концерт",
          "starts_at": "2026-10-12T19:00:00+03:00",
          "venue": "Філармонія",
          "price": "free"
        }
      ]
    }
  },
  "usage": {
    "llm": {
      "provider": "fake",
      "model": "fake-deterministic-1",
      "input_tokens": 412,
      "output_tokens": 96,
      "cost": {
        "amount": 0.0,
        "currency": "USD"
      }
    }
  },
  "started_at": "2026-09-27T12:30:01Z",
  "finished_at": "2026-09-27T12:30:02Z"
}
```

### Відповідь 202

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `job_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `kind` | `string` | так | Вид операції в межах сервісу, наприклад 'collection', 'invocation', 'test_run', 'run', 'onboarding', 'improvement', 'upstream_port'.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `progress` | `JobProgress` | ні |  |
| `progress.completed` | `integer` | ні | мін. `0` |
| `progress.total` | `integer \| null` | ні | Відома загальна кількість одиниць; null — невідома (наприклад під час рекурсивного обходу).; мін. `0` |
| `progress.unit` | `string` | ні |  |
| `progress.message` | `string` | ні |  |
| `progress.counters` | `object` | ні | Довільні лічильники, наприклад {"fetched": 10, "skipped_robots": 2}. |
| `progress.updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `result` | `object` | ні | Результат, коли status = succeeded. Форма залежить від 'kind' і описана в API відповідної операції. Великий результат передається як result_ref. |
| `result_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `error` | `problem` | ні | Причина, коли status = failed. Для cancelled причина — у cancellation. |
| `error.type` | `string` (uri-reference) | так | URI типу проблеми: 'urn:jane:problem:&lt;code>'. |
| `error.title` | `string` | так | Короткий людський опис типу проблеми. |
| `error.status` | `integer` | так | мін. `400`; макс. `599` |
| `error.detail` | `string` | ні | Пояснення конкретного випадку. Без секретів і без вмісту матеріалів. |
| `error.instance` | `string` (uri-reference) | ні |  |
| `error.code` | `string` | так | Стабільний машинний код у snake_case. Відомі коди — $defs/KnownErrorCode. Сервіс може додати власний код лише разом з оновленням каталогу в contracts/.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.retryable` | `boolean` | ні | true — ту саму операцію (з тим самим Idempotency-Key) можна безпечно повторити пізніше. |
| `error.retry_after_seconds` | `integer` | ні | Дублює заголовок Retry-After для клієнтів, які читають лише тіло.; мін. `0` |
| `error.errors` | array of `FieldError` | ні | Помилки окремих полів або параметрів (для validation_failed). |
| `error.errors[].pointer` | `string` | ні | JSON Pointer (RFC 6901) до поля тіла запиту, наприклад '/stages/2/handler/version'. |
| `error.errors[].parameter` | `string` | ні | Ім'я query/path/header параметра. |
| `error.errors[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.errors[].message` | `string` | так |  |
| `error.trace_id` | `string` | ні |  |
| `error.details` | `object` | ні | Додаткові структуровані дані, специфічні для коду (наприклад 'limit', 'actual' для limit_exceeded). |
| `cancellation` | `JobCancellation` | ні |  |
| `cancellation.requested_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `cancellation.requested_by` | `string` | ні |  |
| `cancellation.reason` | `string` | ні | макс. довжина `1000` |
| `idempotency_key` | `string` | ні | макс. довжина `255` |
| `links` | `object` | ні | Пов'язані ресурси: self, cancel, result, run, collection тощо. |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |

Приклад `queued`:

```json
{
  "job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "kind": "collection",
  "status": "queued",
  "created_at": "2026-09-27T10:00:00Z",
  "links": {
    "self": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
    "cancel": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F/cancel"
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `400`, `401`, `404`, `409`, `413`, `422`, `429`, `502`, `503`.
- Операція асинхронна: `202` повертає job; стан, прогрес і результат — через `GET /v1/jobs/{job_id}`.
