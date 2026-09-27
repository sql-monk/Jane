# Адаптер збереження і сценарії сумісності

Інтерфейс: [`python/src/jane_contracts/storage_adapter.py`](../python/src/jane_contracts/storage_adapter.py).
Власники: WP-07 — ядро сервісу storage, адаптери `filesystem` і `postgresql`, **набір тестів
сумісності** (перша віха, потрібна WP-08); WP-08 — `sqlserver`, `mongodb`, `minio`, `s3`.

## Поділ відповідальності

| Ядро storage (WP-07) | Адаптер (WP-07/08) |
|---|---|
| Спільний протокол обробника (`handler.v1`), валідація запиту | Підключення за `ResolvedConnection` (секрети вже розв'язані ядром) |
| Розв'язання `secret_refs` підключення в середовищі сервісу | Створення схеми/таблиць/колекцій/бакетів (`ensure_schema`) |
| Канонічний ключ сутності (`EntityKey` → рядок) | Атомарний `commit_entity`: унікальність delivery_key + CAS за `version` + запис історії |
| Злиття: часткове оновлення, `cleared`, порядок спостережень, визначення `stale_fields` — **чиста функція** | Ідемпотентний `put_object` за `object_key` |
| Вибір формату: RAW вебсторінок — HTML, інше — JSON (перевизначається `format` у маніфесті/параметрах) | Зберігання байтів як є |
| Повтор при `CONFLICT` (обмежено `limits.retries`) | Класифікація помилок: `AdapterError(retryable=…)` |
| `test_mode`: валідація без виклику адаптера, `WriteAck.status = simulated` | — |
| Читальний API `storage.v1` | `list_*`, `get_*`, `read_*` |

Адаптер не знає семантики злиття: це гарантує однакову поведінку всіх шести сховищ і дозволяє
замінити сховище без змін колектора чи екстрактора (критерій 3).

## Алгоритм ядра для одного EntityRecord

1. `delivery = adapter.get_delivery(delivery_key)` → якщо є, повернути збережені підтвердження з `duplicate: true`.
2. `snap = adapter.read_entity(type, key)`.
3. `new, applied, stale = merge(snap, record)` — для кожного поля з `fields`/`cleared`: застосувати, якщо
   `order_tuple(record.observation) > order_tuple(snap.field_orders[field])` (або поля ще немає), інакше — у `stale`.
   Поля, відсутні в `fields` і `cleared`, не змінюються.
4. `adapter.commit_entity(new=new, expected_version=snap.version | None, event=HistoryEvent(..., applied, stale))`.
5. `CONFLICT` → повторити з кроку 2; `DUPLICATE` → як у кроці 1; `COMMITTED` → `WriteAck(status = written | partially_stale | stale)`.

Ключ доставки для сутностей — `delivery_key` виклику + індекс сутності у вході
(`<delivery_key>#<n>`), для RAW — `delivery_key` виклику.

## Набір сумісності (обов'язковий для кожного адаптера)

Набір пише WP-07 як параметризовані pytest-тести, що приймають фабрику адаптера; WP-08 підключає
свої адаптери до того самого набору. Сценарії для об'єктних сховищ без підтримки сутностей
(`capabilities` без `entities`) позначаються як неприйнятні для них, а не пропускаються мовчки.

| № | Сценарій | Очікування |
|---|---|---|
| C-01 | Запис нової сутності | `COMMITTED`, `version = 1`, історія з 1 записом |
| C-02 | Повторна доставка того самого delivery_key (після рестарту адаптера) | `DUPLICATE`, стан і історія не змінились |
| C-03 | Нове спостереження того самого об'єкта з новими значеннями | `COMMITTED`, поля оновлено, новий запис історії |
| C-04 | Часткове оновлення (лише `price`) | Інші поля не змінились |
| C-05 | Явне очищення (`cleared: ["price"]`) | Поле відсутнє в `fields`, є в `cleared_fields`, `field_orders.price` = порядок очищення |
| C-06 | Запізніле спостереження (старіший `observed_at`) | Поточні поля не змінились; історія містить запис зі `stale_fields`; `WriteAck.status = stale` |
| C-07 | Змішане: одне поле новіше, інше — ні | `partially_stale`, застосовано лише новіше |
| C-08 | Однаковий `observed_at`, різний `sequence` (редагування Telegram) | Перемагає більший `sequence` |
| C-09 | Конкурентні коміти з одним `expected_version` (2 задачі) | Рівно один `COMMITTED`, інший `CONFLICT`; після повтору ядра обидва оновлення враховано |
| C-10 | `put_object` з тим самим `object_key` і sha256 | Повертає наявний `ObjectRecord`, без дубля |
| C-11 | `put_object` з тим самим `object_key`, інший sha256 | `AdapterError(retryable=False)` |
| C-12 | RAW HTML → `read_object_content` | Байти ідентичні, `media_type = text/html`; файловий адаптер пише `.html` |
| C-13 | Сутності у файловому адаптері | JSON-документ; формат можна перевизначити (`jsonl`) |
| C-14 | Unicode, спецсимволи й довгий ключ (`scope|{"sku":"A/1 ?#"}`) | Читається тим самим ключем |
| C-15 | `list_entities`/`list_history`/`list_objects` з пагінацією | Повний обхід без пропусків і дублів |
| C-16 | Недоступне сховище | `AdapterError(retryable=True)`; ядро повертає `HandlerResult.failed` з `failure.kind = connection_error, retryable: true` |

Тести сумісності запускаються на локальних сервісах із docker compose (WP-01); S3 — на
S3-сумісному замінникові, про що пишеться у звіті (критерій 12).
