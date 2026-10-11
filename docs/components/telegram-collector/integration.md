# Telegram Collector: інтеграція

Як використовувати Telegram Collector зі стороннього застосунку, як підключити реальний Telegram або власний клієнт і як колектор працює в складі Jane. Операції, схеми, пагінація й помилки спільні для колекторів — у довіднику [collector.v1](../../reference/api/collector/README.md); тут — специфіка Telegram.

## Зміст

- [Самостійне використання](#самостійне-використання)
- [Правила](#правила)
- [Матеріал повідомлення](#матеріал-повідомлення)
- [Формат записаного каналу](#формат-записаного-каналу)
- [Реальний Telegram через Telethon](#реальний-telegram-через-telethon)
- [Власний клієнт](#власний-клієнт)
- [Помилки](#помилки)
- [Композиція в Jane](#композиція-в-jane)
- [Заміна сумісною реалізацією](#заміна-сумісною-реалізацією)

## Самостійне використання

Цикл той самий, що в будь-якого колектора `collector.v1`: `POST /v1/collections` з `Idempotency-Key`, читання `GET /v1/collections/{id}/materials` з `after` (підтвердження) і `wait_ms`, `GET /v1/collections/{id}/errors`. Приклад клієнта на Python — [інтеграція Web Collector](../web-collector/integration.md#самостійне-використання); для Telegram змінюються лише `source_kind: "telegram"` і правила. Покроковий приклад на записаному каналі — [quickstart.md](quickstart.md).

Особливості запитів:

- `urls` у запиті збору не приймаються (`422`).
- `POST /v1/fetches` потребує `telegram.channel_username` або `telegram.channel_id` і `telegram.message_id`.
- `state_key` типово дорівнює `source_id`, без нього — `collection_id`; одночасний другий збір із тим самим `state_key` — `409 conflict`.
- `GET /v1/states/{state_key}` повертає курсори каналів; `DELETE /v1/states/{state_key}` скидає їх, і наступний `incremental` знову читає історію.

## Правила

Документ `TelegramRules` із [collector-rules.schema.json](../../../contracts/schemas/collector-rules.schema.json):

| Поле | Типово | Значення |
|---|---|---|
| `channels[]` | — | `username` (4–64 символи) або `channel_id` (`-100...`) |
| `history.enabled` | `true` | читати історію в `full` і в першому `incremental`; `false` — почати з поточного верху каналу |
| `history.since` | — | лише повідомлення не старші за дату |
| `history.from_message_id` | — | почати з цього `message_id` |
| `updates.new_messages` | `true` | нові повідомлення в `incremental` |
| `updates.edits` | `true` | редагування в `incremental` |
| `media.download`, `media.kinds` | `false`, усі | завантажувати медіа вказаних типів |
| `account_connection_id` | `DEFAULT_ACCOUNT_CONNECTION_ID` | підключення `telegram_account` |
| `limits` | — | ліміти рівня джерела |

Перевірка без збору — `POST /v1/rules/validations`; правила `collector: "web"` цей колектор позначає `supported: false`.

## Матеріал повідомлення

| Поле | Значення |
|---|---|
| `material_id` | `tg:<channel_id>:<message_id>` — однаковий для всіх ревізій |
| `locator.url` | `https://t.me/<username>/<message_id>`; без username — `https://t.me/c/<внутрішній id>/<message_id>` |
| `published_at`, `edited_at` | `date` і `edit_date` повідомлення |
| `revision.sequence` | секунди `edit_date` (або `date`) × 1000 + номер ревізії в межах секунди |
| `revision.source_revision` | секунди `edit_date` або `date` |
| `revision.is_edit` | `true` для редагованого повідомлення |
| `format.content_kind` | `message`; текст — `text/plain`, UTF-8 |
| `discovery.strategy` | `telegram_history` або `telegram_updates` |

Завантажені медіа — у `attachments` (`name`, `role` = тип медіа, `content` — посилання на вміст inline або blob); завеликі чи пропущені — діагностика `media_too_large`, `media_skipped`. У `metadata` — `views`, `author`, перелік медіа і для службових повідомлень каналу `service_action` у snake case, наприклад `pin_message`. Повна схема — [material.schema.json](../../../contracts/schemas/material.schema.json).

## Формат записаного каналу

Бекенд `recorded` читає `<RECORDINGS_DIR>/<username або channel_id>.json`, а якщо такого файла немає — шукає канал серед усіх `*.json` каталогу.

```json
{
  "channel": {"channel_id": "-1001234567890", "username": "city_events_example", "title": "City events"},
  "required_secrets": ["session"],
  "messages": [
    {"id": 1, "date": "2026-09-01T10:00:00Z", "text": "...", "edit_date": null, "views": 10,
     "media": [{"kind": "photo", "name": "p.jpg", "media_type": "image/jpeg", "data_base64": "..."}]}
  ],
  "events": [{"pts": 1, "message": {"id": 1, "date": "2026-09-01T10:00:00Z", "text": "..."}}],
  "min_pts": 0,
  "faults": [{"method": "history", "flood_wait": 3, "count": 1}]
}
```

| Ключ | Призначення |
|---|---|
| `messages` | поточний стан повідомлень — для історії й разового отримання |
| `events` | оновлення з `pts` — для `incremental`; кожне несе стан повідомлення після оновлення |
| `min_pts` | оновлення до цього `pts` втрачено — колектор отримує «різниця завелика» |
| `required_secrets` | секрети, які має розв'язати підключення, інакше — неавторизована сесія |
| `faults` | імітація збоїв для тестів: `flood_wait`, `delay_ms`, `unavailable`; використані рахуються в `<файл>.faults.json` |

Файл перечитується на кожен виклик, тож нові пости й редагування можна дописувати під час роботи. Зручно — класом `jane_telegram_collector.recorded.Recording` (`create`, `post`, `edit`, `redeliver`), як у [quickstart.md](quickstart.md#нові-повідомлення-й-редагування).

## Реальний Telegram через Telethon

**Не перевірено на реальному сервісі**: у проєкті немає тестового облікового запису; адаптер написано за API Telethon 1.x. Кроки:

1. Встановити extra: `uv sync --package jane-telegram-collector --extra telethon`.
2. Отримати `api_id` і `api_hash` на my.telegram.org і заздалегідь створити Telethon `StringSession` авторизованого облікового запису (інтерактивного входу в сервісі немає).
3. Передати секрети через середовище з префіксом `JANE_SECRET_` (наприклад `JANE_SECRET_TG_API_HASH`, `JANE_SECRET_TG_SESSION`) або файлами в `SECRET_FILES_DIR`.
4. Запустити з `JANE_TELEGRAM_COLLECTOR_CLIENT_BACKEND=telethon`.
5. Створити підключення `PUT /v1/connections/tg-main` з тілом як у [connection.telegram-account.json](../../../examples/telegram/connection.telegram-account.json) (замінивши `api_id`) і перевірити `POST /v1/connections/tg-main/test` — він показує, чи розв'язуються секрети, але до Telegram не звертається.
6. У правилах указати `"account_connection_id": "tg-main"` або задати `DEFAULT_ACCOUNT_CONNECTION_ID`.

Без підключення бекенд `telethon` відхиляє збір: `422`, «the telethon client needs a telegram_account connection».

## Власний клієнт

`JANE_TELEGRAM_COLLECTOR_CLIENT_BACKEND=<module>:<factory>` підключає іншу реалізацію без зміни сервісу. Фабрика реалізує `ClientFactory`, клієнт — `TelegramClient` з `jane_telegram_collector.client`:

```python
class TelegramClient(Protocol):
    async def resolve(self, *, username: str | None = None, channel_id: str | None = None) -> ChannelInfo: ...
    async def history(self, channel: ChannelInfo, *, after_id: int, limit: int, since: datetime | None = None) -> list[TgMessage]: ...
    async def get_message(self, channel: ChannelInfo, message_id: int) -> TgMessage | None: ...
    async def changes(self, channel: ChannelInfo, *, pts: int, limit: int) -> ChangeBatch: ...
    async def download_media(self, channel: ChannelInfo, media: TgMedia, *, max_bytes: int) -> bytes: ...
    async def close(self) -> None: ...
```

Помилки клієнт повідомляє винятками `FloodWait(seconds)`, `ClientUnavailable` (тимчасовий збій), `ChannelUnavailable`, `AccountUnauthorized` — колектор сам застосовує паузи, повтори й коди помилок.

## Помилки

| Ситуація | Разове отримання | Збір |
|---|---|---|
| Повідомлення немає | `404 not_found`, `reason: message_not_found` | — |
| Канал недоступний | `502 source_unavailable`, `reason: channel_unavailable` | `/errors`: `not_found` для каналу, збір триває |
| FloodWait | `429 rate_limited` з `Retry-After` одразу | чекає до `telegram.max_flood_wait_seconds`, далі `failed` з `rate_limited` |
| Тимчасовий збій після повторів | `502 source_unavailable` (повторюваний) | `failed`, `source_unavailable` |
| Неавторизована сесія | `502 source_unavailable`, `reason: account_unauthorized` | `failed`, те саме |
| Різниця змін завелика | — | `/errors`: `source_unavailable`, нові повідомлення з історії |
| Повідомлення не вміщується в доставку | `422 limit_exceeded` | `/errors`: `limit_exceeded`, збір триває |

## Композиція в Jane

Orchestrator працює з Telegram Collector так само, як із Web Collector: створює збір із правилами джерела, читає `/materials` і підтверджує курсор після приймання матеріалів обробниками. Для періодичних перевірок він повторює збір `incremental` з тим самим `state_key`, і колектор віддає лише нові повідомлення й редагування. Обробники отримують редагування як нові спостереження й упорядковують їх за `revision.sequence`.

У dev-стеку (`infra/compose.yaml`) сервіс працює з `auth_mode=api_key` і томом `telegram-collector-data`; бекенд — типовий `recorded`.

## Заміна сумісною реалізацією

Інший сервіс може замінити Telegram Collector, якщо реалізує `collector.v1` для `source_kind: telegram`, приймає `TelegramRules` і зберігає ті самі властивості матеріалів: стабільний `material_id` повідомлення, строго зростаючий `revision.sequence` для ревізій і семантику курсора `after`. Контрактні тести сервісу — `services/telegram-collector/tests/test_contract.py`. Якщо потрібен лише інший доступ до Telegram, замінювати сервіс не треба — достатньо [власного клієнта](#власний-клієнт).
