# Модуль `jane_telegram_collector.telethon_client`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/telethon_client.py](../../../../../services/telegram-collector/src/jane_telegram_collector/telethon_client.py). Не редагуйте вручну.

MTProto backend on Telethon (optional extra ``telethon``: ``uv sync --package jane-telegram-collector --extra telethon``).

NOT verified against the real Telegram service (no test account in the project): the adapter follows the Telethon 1.x API and is covered only by the shared collector tests through the recorded backend.

The ``telegram_account`` connection (ADR-0006, README "Підключення"):

* ``params.api_id`` — application id from my.telegram.org (not a secret);
* ``secret_refs.api_hash`` — application hash;
* ``secret_refs.session`` — Telethon ``StringSession`` of an already authorized account (created offline, interactive login is not part of the service).

## Класи

### Клас `TelethonClientFactory`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.telethon_client` |
| Код | [telethon_client.py:63](../../../../../services/telegram-collector/src/jane_telegram_collector/telethon_client.py#L63) |

```python
class TelethonClientFactory: ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'telethon'` |  |

#### Метод `TelethonClientFactory.requires_account`

```python
def requires_account(self) -> bool: ...
```

Код: [telethon_client.py:66](../../../../../services/telegram-collector/src/jane_telegram_collector/telethon_client.py#L66).

#### Метод `TelethonClientFactory.open`

```python
async def open(self, account: ResolvedAccount, *, connect_timeout_s: float) -> TelegramClient: ...
```

Винятки в коді методу: `AccountUnauthorized`, `ClientUnavailable`.

Код: [telethon_client.py:69](../../../../../services/telegram-collector/src/jane_telegram_collector/telethon_client.py#L69).
