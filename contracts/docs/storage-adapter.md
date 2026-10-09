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

## Об'єктні сховища (minio, s3) і файлова система

Сутності зберігаються як JSON-документи з тією самою семантикою, що й у БД — злиття, `cleared`,
порядок спостережень і визначення `stale_fields` робить ядро, адаптер дає лише атомарність:

| Об'єкт | Ключ (у бакеті підключення, префікс з `params.prefix`) | Вміст |
|---|---|---|
| Знімок сутності | `entities/<entity_type>/<sha256(canonical_key)>.json` | `EntitySnapshot` (включно з `version`, `field_orders`, `cleared_fields`, `canonical_key`; у minio/s3 — також `pending` із подією цієї версії до перенесення) |
| Подія історії | `history/<entity_type>/<sha256(canonical_key)>/<version:012d>.json` | `HistoryEvent` |
| Запис доставки | `deliveries/<sha256(delivery_key)>.json` | `DeliveryRecord` |
| RAW / документ | `objects/<object_key>` + `objects/<object_key>.meta.json` | байти + метадані Material |

`commit_entity` для об'єктного сховища:
1. Заявка `deliveries/<h>.json` з `If-None-Match: *`: завершена доставка → `DUPLICATE`,
   незавершена чинна заявка → `CONFLICT`; власник/вік заявки визначає відновлення.
2. CAS `entities/…json` з `If-Match` прочитаного ETag (нова сутність — `If-None-Match: *`).
   Знімок містить новий стан, версію й подію історії у `pending`: **це єдина точка коміту**.
3. Перенести `pending` у `history/…/<version:012d>.json`, потім зняти `pending` умовним записом.
   Збій перенесення не губить подію: читання історії враховує `pending`, наступний читач/коміт
   повторює перенесення. Осиротіла подія не займає версію перед CAS знімка.
4. При 412/тайм-ауті CAS адаптер звіряє знімок і нашу подію: застосований коміт → `COMMITTED`;
   програна гонка → компенсація лише власної заявки й `CONFLICT`, ядро повторює за `limits.retries`.
   Докладний протокол і межа умовного видалення MinIO —
   [S3 README](../../services/storage/adapters/s3/README.md#розкладка-й-атомарність).

Умовні записи: MinIO і S3 підтримують `If-None-Match: *` та `If-Match` на `PutObject`; якщо
S3-сумісний замінник у тестах їх не підтримує — це дефект середовища, а не підстава пропустити
сценарій (звіт WP-08 фіксує, на чому перевірено). Файловий адаптер використовує ту саму схему
ключів з атомарним `os.replace` і файлом-блокуванням на ключ сутності (`O_CREAT|O_EXCL`) замість ETag.
Сценарії, що вимагають цих механізмів: C-01…C-09 (сутності, дедуплікація, часткове оновлення,
очищення, запізнілі дані, конкуренція), C-14…C-15 (ключі, пагінація історії) — **обов'язкові**.

### Порядок читання сутностей

`list_entities` гарантує курсорний обхід у порядку конкретного адаптера, без спільної гарантії
«новіші першими». У межах вибраного `entity_type` files/postgresql впорядковують за `canonical_key`,
sqlserver — за `key_hash`, mongodb — за `_id`, minio/s3 — за ключем об'єкта (хеш `canonical_key`).
`updated_since` фільтрує записи,
але не задає порядок. Курсор — непрозорий; між адаптерами його не переносити. Послідовні сторінки
не є транзакційним знімком при конкурентних записах. Реалізації — [адаптери](../../services/storage/adapters).

## Набір сумісності (обов'язковий для кожного адаптера)

Набір пише WP-07 як параметризовані pytest-тести, що приймають фабрику адаптера; WP-08 підключає
свої адаптери до того самого набору. **Усі сценарії C-01…C-16 обов'язкові для всіх шести
адаптерів** (filesystem, postgresql, sqlserver, mongodb, minio, s3): кожен початковий адаптер
зберігає і RAW, і структуровані результати з історією (ТЗ §12 п.12). `capabilities` кожного
адаптера = `{"objects", "entities", "history"}`; пропускати сценарії сутностей чи історії не можна.

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
