# jane_telegram_collector.telethon_client

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.telethon_client.TelethonClientFactory](#jane_telegram_collectortelethon_clienttelethonclientfactory)
- [jane_telegram_collector.telethon_client.TelethonClientFactory.name](#jane_telegram_collectortelethon_clienttelethonclientfactoryname)
- [jane_telegram_collector.telethon_client.TelethonClientFactory.requires_account](#jane_telegram_collectortelethon_clienttelethonclientfactoryrequires_account)
- [jane_telegram_collector.telethon_client.TelethonClientFactory.open](#jane_telegram_collectortelethon_clienttelethonclientfactoryopen)

## jane_telegram_collector.telethon_client.TelethonClientFactory

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/telethon_client.py:63](../../../../../../services/telegram-collector/src/jane_telegram_collector/telethon_client.py#L63).

```python
class TelethonClientFactory:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_telegram_collector.telethon_client.md#jane_telegram_collectortelethon_clienttelethonclientfactoryname) | Поле | ні |
| [requires_account](jane_telegram_collector.telethon_client.md#jane_telegram_collectortelethon_clienttelethonclientfactoryrequires_account) | Метод | ні |
| [open](jane_telegram_collector.telethon_client.md#jane_telegram_collectortelethon_clienttelethonclientfactoryopen) | Метод | ні |

## jane_telegram_collector.telethon_client.TelethonClientFactory.name

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/telethon_client.py:64](../../../../../../services/telegram-collector/src/jane_telegram_collector/telethon_client.py#L64).

```python
name = 'telethon'
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.telethon_client.TelethonClientFactory.requires_account

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/telethon_client.py:66](../../../../../../services/telegram-collector/src/jane_telegram_collector/telethon_client.py#L66).

```python
def requires_account(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_telegram_collector.telethon_client.TelethonClientFactory.open

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/telethon_client.py:69](../../../../../../services/telegram-collector/src/jane_telegram_collector/telethon_client.py#L69).

```python
async def open(self, account: ResolvedAccount, *, connect_timeout_s: float) -> TelegramClient:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `account` | `ResolvedAccount` | `—` | positional-or-keyword |
| `connect_timeout_s` | `float` | `—` | keyword-only |

Результат: `TelegramClient`.

Явні `raise` у тілі: `AccountUnauthorized`, `ClientUnavailable`. Винятки викликаних залежностей описуються у ручному довіднику.
