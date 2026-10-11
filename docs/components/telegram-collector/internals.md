# Telegram Collector: будова

Компоненти коду, алгоритм збору каналу, ревізії повідомлень, власні дані й гарантії Telegram Collector. Код — `services/telegram-collector/src/jane_telegram_collector/` (ревізія `48389a3`).

## Зміст

- [Компоненти](#компоненти)
- [Збір каналу](#збір-каналу)
- [Ревізії й редагування](#ревізії-й-редагування)
- [Виклики Telegram API](#виклики-telegram-api)
- [Стани збору](#стани-збору)
- [Власні дані](#власні-дані)
- [Гарантії](#гарантії)

## Компоненти

![Компоненти Telegram Collector і бекенди клієнта](../../diagrams/telegram-collector/components.light.png#gh-light-mode-only)
![Компоненти Telegram Collector і бекенди клієнта](../../diagrams/telegram-collector/components.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/telegram-collector/components.light.png), [темне](../../diagrams/telegram-collector/components.dark.png); джерело — [components.drawio](../../diagrams/telegram-collector/components.drawio).

| Модуль | Відповідальність |
|---|---|
| `app.py` | HTTP API `collector.v1`; health, info, метрики, job — із `jane-kit` |
| `engine.py` | `Engine`: старт і відновлення зборів, разове отримання, GC, можливості |
| `collector.py` | `TelegramRun`: план каналу, історія, зміни, видача повідомлень, курсори |
| `client.py` | інтерфейси `TelegramClient`, `ClientFactory`, типи повідомлень і помилок, вибір бекенда |
| `recorded.py` | бекенд `recorded` і `Recording` для запису каналів |
| `telethon_client.py` | бекенд `telethon` (MTProto) |
| `materials.py` | Material повідомлення, `revision.sequence`, доставка inline або blob |
| `connections.py` | підключення `telegram_account`, політика секретів і хостів |
| `state.py`, `stores.py` | власний стан SQLite, job і `Idempotency-Key` |
| `rules.py` | перевірка й завантаження правил |

## Збір каналу

![Збір одного каналу: план, історія, зміни, помилки й повтори](../../diagrams/telegram-collector/channel-run.light.png#gh-light-mode-only)
![Збір одного каналу: план, історія, зміни, помилки й повтори](../../diagrams/telegram-collector/channel-run.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/telegram-collector/channel-run.light.png), [темне](../../diagrams/telegram-collector/channel-run.dark.png); джерело — [channel-run.drawio](../../diagrams/telegram-collector/channel-run.drawio).

Канали правил обробляються по черзі. Для кожного:

1. **Пошук каналу** за `username` або `channel_id`. Недоступний канал — запис `not_found` у `/errors`, перехід до наступного.
2. **План** (зберігається в `channel_progress` збору):
   - `mode: full` або немає курсора — **історія**: повідомлення після `history.from_message_id − 1`, від старих до нових, сторінками `collector.history_page_size`, з фільтром `history.since`. Поточний `pts` каналу запам'ятовується на старті, тож наступний `incremental` побачить і редагування, зроблені під час читання історії;
   - `incremental` з `pts` у курсорі — **зміни**: `getChannelDifference` від `pts` сторінками `collector.changes_page_size`; нові й відредаговані повідомлення фільтруються за `updates.new_messages` і `updates.edits`;
   - курсор без `pts` (попередній збір зупинився посеред історії) — дочитати історію після `last_message_id`;
   - `history.enabled: false` без курсора — почати з поточного верху каналу, нічого не видаючи.
3. **«Різниця завелика»** — запис `source_unavailable` у `/errors`; нові повідомлення дочитуються з історії після останнього відомого, редагування за проміжок втрачено.
4. **Видача** кожного повідомлення — нижче; після сторінки змін курсор отримує новий `pts`.
5. **Канал завершено** — курсор має `pts` і `last_message_id`, прогрес — `done`; після перезапуску завершені канали пропускаються.

Бюджет `telegram.max_messages_per_run` зупиняє збір як `succeeded` зі `stopped_by: telegram.max_messages_per_run`; наступний збір продовжує з курсора.

## Ревізії й редагування

- `revision.sequence` = секунди `edit_date` (для нередагованого — `date`) × 1000 + номер ревізії в межах тієї самої секунди. Так кожна нова ревізія має строго більший номер, навіть якщо Telegram дає `edit_date` з точністю до секунди.
- Для кожного `material_id` у межах `state_key` колектор пам'ятає останню видану ревізію (`tg_seen`: `sequence` і SHA-256 тексту). У зборах `incremental` повідомлення з тим самим текстом і `sequence` або зі старішим `sequence` пропускається як дубль (`stats.duplicates`).
- Редагування — нове спостереження того самого `material_id` з `is_edit: true`; попередні спостереження не змінюються.
- `POST /v1/fetches` нічого не записує, але номер ревізії бере з уже виданих колектором ревізій, тож він узгоджений зі зборами.

## Виклики Telegram API

Кожен виклик проходить `TelegramRun.call`:

- пауза `rate.min_delay_ms_per_host` від попереднього виклику збору;
- межа часу `timeouts.request_timeout_ms`;
- `FloodWait` до `telegram.max_flood_wait_seconds` — чекати й повторити; довший — збір `failed` з `rate_limited` і `retry_after_seconds`;
- `ClientUnavailable` і тайм-аут — повтор з експоненційною паузою до `retries.max_attempts`, потім збір `failed` з `source_unavailable`;
- відкриття клієнта — та сама політика повторів з `timeouts.connect_timeout_ms`.

Збій збору записується в `/errors` разом зі статусом `failed` в одній транзакції; прогрес і курсори до збою зберігаються.

## Стани збору

Життєвий цикл збору, оренда, перехоплення зупиненого збору іншим екземпляром, скасування й прострочення — ті самі, що в Web Collector; схема й пояснення — [стани збору Web Collector](../web-collector/internals.md#стани-збору). Специфіка Telegram:

- новий власник збору скидає прапорець `paused_by_backpressure` попереднього й вирішує заново;
- збір продовжується точно після останнього виданого повідомлення, бо кожне повідомлення записується в одній транзакції з прогресом і курсором.

## Власні дані

Файл `STATE_DIR/state.db` (SQLite, режим WAL) належить лише Telegram Collector ([карта власності даних](../../../contracts/docs/data-ownership.md)).

![ER-схема власного стану Telegram Collector у SQLite](../../diagrams/telegram-collector/state-er.light.png#gh-light-mode-only)
![ER-схема власного стану Telegram Collector у SQLite](../../diagrams/telegram-collector/state-er.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/telegram-collector/state-er.light.png), [темне](../../diagrams/telegram-collector/state-er.dark.png); джерело — [state-er.drawio](../../diagrams/telegram-collector/state-er.drawio).

| Таблиця | Ключ | Зміст | Час життя |
|---|---|---|---|
| `collections` | `collection_id` | запит, правила, статус, результат, лічильники, оренда, `acked_seq` | запис — назавжди (після прострочення — позначка) |
| `channel_progress` | `collection_id`, `channel_key` | фаза каналу в зборі: `after_id`, `pts`, підсумок | до прострочення збору |
| `materials` | `collection_id`, `seq` | буфер непідтверджених матеріалів | до підтвердження |
| `errors` | `collection_id`, `seq` | помилки каналів і повідомлень | до прострочення |
| `tg_cursors` | `state_key`, `channel_id` | `last_message_id`, `last_edit_date`, `pts`, `username` | до `DELETE /v1/states/{key}` |
| `tg_seen` | `state_key`, `material_id` | остання видана ревізія: `sequence`, SHA-256 | до `DELETE /v1/states/{key}` |
| `connections` | `connection_id` | підключення `telegram_account` (лише посилання на секрети) | до видалення |
| `jobs`, `idempotency` | `job_id`, `key` | job і ключі ідемпотентності (`jane-kit`) | `job_retention_seconds`, `idempotency_ttl_seconds` |
| `counters` | `name` | лічильники послідовностей | постійно |

Формат файла має версію `PRAGMA user_version = 1`. Файл версії 0 (колектори до WP-16, `tg_seen.sequence` у секундах) мігрується автоматично під час відкриття; файл новішої версії сервіс відмовляється відкривати.

## Гарантії

- **Курсор не пропускає повідомлень**: повідомлення, прогрес, курсор і видана ревізія записуються в одній транзакції з перевіркою оренди.
- **Редагування не губляться між зборами**, поки Telegram зберігає різницю змін; інакше — явний запис у `/errors`.
- **Повторна доставка ревізії не дає дубля** в межах `state_key`.
- **Порядок ревізій**: `revision.sequence` строго зростає для кожної нової ревізії повідомлення.
- **Доставка «хоча б один раз» до підтвердження**, ідемпотентний старт за `Idempotency-Key` — як у Web Collector.
