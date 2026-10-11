# Web Collector: інтеграція

Як використовувати Web Collector зі стороннього застосунку, як він працює в складі Jane і як замінити його сумісною реалізацією. Операції, схеми запитів і відповідей, пагінація та модель помилок описані один раз для всіх колекторів — у довіднику [collector.v1](../../reference/api/collector/README.md); тут — специфіка Web Collector.

## Зміст

- [Самостійне використання](#самостійне-використання)
- [Правила збору](#правила-збору)
- [Повторні збори](#повторні-збори)
- [Доставка матеріалів](#доставка-матеріалів)
- [Помилки](#помилки)
- [Композиція в Jane](#композиція-в-jane)
- [Заміна сумісною реалізацією](#заміна-сумісною-реалізацією)

## Самостійне використання

Сторонньому застосунку достатньо HTTP-клієнта. Типовий цикл:

1. `POST /v1/collections` з `Idempotency-Key` → `202` і `job_id` (він же `collection_id`).
2. `GET /v1/collections/{id}/materials?after=<курсор>&wait_ms=<мс>` у циклі, доки `end_of_stream` не стане `true`. Кожен запит з `after` підтверджує попередні матеріали.
3. Останній курсор підтвердити ще одним запитом з `after`.
4. `GET /v1/collections/{id}/errors` — помилки окремих URL; `GET /v1/collections/{id}` — підсумок.

Приклад на Python (`httpx`): каталог ноутбуків тестового сайту стратегією `listing`. Виконано проти колектора на порту 18101 і тестового сайту на 18110 командою `uv run --package jane-web-collector python collect_client.py`.

```python
import httpx

BASE = "http://127.0.0.1:18101"
request = {
    "source_kind": "web",
    "source_id": "testsite",
    "state_key": "testsite-laptops",
    "mode": "incremental",
    "rules": {
        "collector": "web",
        "scope": {"allowed_domains": ["127.0.0.1"]},
        "strategies": [{"type": "listing", "start_urls": ["http://127.0.0.1:18110/catalog/laptops/"],
                        "item_links": {"value": "main ul a"}}],
    },
}

with httpx.Client(base_url=BASE, timeout=60) as client:
    started = client.post("/v1/collections", json=request, headers={"Idempotency-Key": "laptops-2026-10-11"})
    started.raise_for_status()
    collection_id = started.json()["job_id"]
    cursor = None
    while True:
        params = {"limit": 50, "wait_ms": 5000}
        if cursor:
            params["after"] = cursor  # acknowledges everything up to this cursor
        page = client.get(f"/v1/collections/{collection_id}/materials", params=params).json()
        for material in page["items"]:
            print(material["locator"]["canonical_url"], material["discovery"]["strategy"])
        cursor = page["next_cursor"] or cursor
        if page["end_of_stream"]:
            break
    if cursor:
        client.get(f"/v1/collections/{collection_id}/materials", params={"after": cursor})
    summary = client.get(f"/v1/collections/{collection_id}").json()
    print(summary["status"], summary["stats"]["emitted"], summary["stats"]["acknowledged"])
    errors = client.get(f"/v1/collections/{collection_id}/errors").json()["items"]
    print("errors:", len(errors))
```

Вивід:

```text
http://127.0.0.1:18110/catalog/laptops/ listing
http://127.0.0.1:18110/product/laptop-one listing
http://127.0.0.1:18110/product/laptop-two listing
http://127.0.0.1:18110/product/laptop-three listing
http://127.0.0.1:18110/catalog/laptops/?page=2 listing
http://127.0.0.1:18110/product/laptop-four listing
http://127.0.0.1:18110/product/laptop-five listing
succeeded 7 7
errors: 0
```

Сторінки списку `listing` теж видає як матеріали — це HTML-сторінки сайту. Щоб отримувач не обробляв їх, призначте їм розділ (`sections`) і фільтруйте за `discovery.section`.

Без `auth_mode=none` кожен запит потребує заголовка `Authorization: Bearer <ключ>` з правами `collector:run` і `collector:read` ([configuration.md](configuration.md#процес-і-api)). Клієнт для Python можна згенерувати з OpenAPI: `just gen-client contracts/openapi/collector.v1.yaml <каталог>`.

## Правила збору

Правила — документ `WebRules` зі [collector-rules.schema.json](../../../contracts/schemas/collector-rules.schema.json). Джерела правил у запиті:

| Поле запиту | Звідки правила |
|---|---|
| `rules` | inline у запиті |
| `rules_ref` | `RULES_DIR/<package_id>/<version>/`, потім Registry; перевіряються `digest` і `sha256` файлів |

`POST /v1/rules/validations` перевіряє правила без збору. Відповідь розрізняє `valid` (схема) і `supported` (чи виконає цей екземпляр). Приклад для правил зі стратегією `llm_explore`:

```json
{"valid":true,"supported":false,"errors":[],"warnings":[{"pointer":"/strategies/0","code":"unsupported_strategy","message":"strategy llm_explore is not executed by the collector (ADR-0010: LLM exploration is done by the assistant)"},{"pointer":"/strategies/1","message":"recursive strategy without max_depth inherits limits.crawl.max_depth"}]}
```

Особливості, які варто знати:

- `urls` у запиті збору **замінюють** стратегії правил однією стратегією `seed_list` з ідентифікатором `request-urls`; межі, `robots`, нормалізація й ліміти правил діють.
- Навігаційні документи (стрічки, sitemap, сторінки API) проходять ті самі `scope` і `robots.txt`, що й сторінки: шлях стрічки має входити в `path_prefixes`.
- `state_key` типово дорівнює `source_id`, а без нього — `collection_id`. Два збори з одним `state_key` одночасно не виконуються: другий отримує `409 conflict`.
- `robots.mode: owner_policy` вимикає `robots.txt` і `Crawl-delay` лише для ресурсу, який контролює користувач, з обов'язковими `confirmed_owner: true` і `justification`.
- Стратегії, їхні параметри й поведінку описує [контракт стратегій](../../../contracts/docs/discovery-strategy.md); підсумок — у [internals.md](internals.md#стратегії-пошуку).

## Повторні збори

Історія URL зберігається за `state_key` і використовується в зборах `mode: incremental`:

| `revisit.mode` | Відомі успішні URL |
|---|---|
| `never` (типово) | не завантажуються; їхні збережені посилання продовжують `recursive` |
| `interval` | завантажуються, якщо старші за `crawl.revisit_interval_seconds` |
| `if_changed` | умовний запит (`If-None-Match`, `If-Modified-Since`); `304` — не матеріал |

- `lastmod` кандидата (sitemap з `use_lastmod_for_revisit`, `feed`, `api_feed` з `lastmod_path`), новіший за попереднє завантаження, змушує завантажити URL попри `revisit`.
- URL, що минулого разу завершилися 4xx або 5xx, пробуються знову.
- Сторінки списків `listing` і навігаційні документи читаються повністю в кожному зборі.
- `dedup.key: canonical_url_and_content` видає URL повторно лише за зміни вмісту.
- `GET /v1/states/{state_key}` показує кількість відомих URL і курсори стратегій; `DELETE /v1/states/{state_key}` скидає історію (`409`, якщо збір із цим ключем виконується).

У `mode: full` завантажується все, але історія оновлюється, тож наступний `incremental` її використає.

## Доставка матеріалів

`content_delivery` у запиті:

| Значення | Поведінка |
|---|---|
| `auto` (типово) | inline до `transfer.inline_max_bytes`, більше — транзитний blob; без транзитного сховища — помилка URL `limit_exceeded` |
| `inline` | лише inline; більше — `limit_exceeded` |
| `blob` | завжди транзитний blob; без `TRANSIT_DIR` запит відхиляється `422` |

Транзитний blob — файл у `TRANSIT_DIR` з посиланням `file://` і `expires_at` (`transfer.transit_ttl_seconds`). Отримувач має мати доступ до цього каталогу (той самий вузол або спільний том).

## Помилки

| Ситуація | Разове отримання (`POST /v1/fetches`) | Збір |
|---|---|---|
| Заборонено `robots.txt` або політикою адрес | `403 access_denied_by_policy` | запис у `/errors`, `skipped_robots` |
| URL або переадресація поза межами | `422 out_of_scope` | URL не потрапляє в чергу (`skipped_out_of_scope`) |
| Сайт відповів 404 або 410 | `404 not_found` | `/errors`: `not_found` з `http_status` |
| Інший 4xx, 5xx або мережа після повторів | `502 source_unavailable` | `/errors`: `source_unavailable` |
| 429 після повторів, довгий `Retry-After` | `429 rate_limited` з `Retry-After` | `/errors`: `rate_limited` |
| Немає браузера для `render_js` | `501 not_implemented` | `/errors`: `not_implemented` |
| Матеріал не вміщується в доставку | `422 limit_exceeded` | `/errors`: `limit_exceeded` |
| Недійсні правила чи запит | `422 validation_failed` | `422` на `POST /v1/collections` |
| Файл стану зайнятий | `503 service_unavailable`, `Retry-After` | так само |

Помилки окремих URL не зупиняють збір і не роблять його `failed`. Формат відповіді — `application/problem+json` ([errors.md](../../../contracts/docs/errors.md)).

## Композиція в Jane

Orchestrator — звичайний клієнт `collector.v1`: для запуску завдання він створює збір із правилами джерела (`rules_ref` пакета правил з Registry або inline), читає `/materials` з `wait_ms` (типово 1000 мс у його налаштуваннях), передає матеріали етапам обробників через `handler.v1` і підтверджує курсор лише після приймання. Колектор нічого не знає про Orchestrator, обробники й сховища.

Assistant використовує `POST /v1/fetches` і короткі збори, щоб отримати вибірку сторінок нового джерела, а `POST /v1/rules/validations` — щоб перевірити запропоновані правила.

У dev-стеку (`infra/compose.yaml`) сервіс працює з `auth_mode=api_key`, ключами `admin`, `orchestrator`, `assistant` і власним токеном до Registry; стан — у томі `web-collector-data`.

## Заміна сумісною реалізацією

Будь-який сервіс, що реалізує `collector.v1` для `source_kind: web` і приймає `WebRules`, може замінити Web Collector: Orchestrator обирає колектор за адресою, а не за реалізацією. Вимоги до заміни:

- ті самі операції, коди помилок і семантика курсора: `after` підтверджує, `end_of_stream` — лише коли збір завершено й буфер прочитано;
- `Idempotency-Key` для `POST /v1/collections`;
- `GET /v1/info` з `capabilities.strategies`, щоб клієнти знали, які стратегії виконуються;
- матеріали за [material.schema.json](../../../contracts/schemas/material.schema.json) зі стабільним `material_id` для того самого канонічного URL.

Відповідність перевіряють контрактні тести сервісу (`services/web-collector/tests/test_contract.py`) — їх можна взяти за зразок для іншої реалізації. Щоб додати лише новий спосіб пошуку, сервіс замінювати не потрібно — див. [підключення стратегії](../../../services/web-collector/strategies/discovery/README.md).
