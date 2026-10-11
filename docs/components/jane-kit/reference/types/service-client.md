# ServiceClient

Асинхронний HTTP-клієнт до публічного API сервісу. Додає контекст trace/request ID, обмежує тайм-аути й повторює лише дозволені запити. Модуль: `jane_kit.clients`; [декларації та всі параметри](generated/jane_kit.clients.md#jane_kitclientsserviceclient).

## Створення й закриття

`ServiceClient(base_url, limits=None, *, headers=None, transport=None)` створює власний `httpx.AsyncClient`. Без `limits` застосовує `ClientLimits()`. `headers` копіюються; `transport` дозволяє підключити власний транспорт. Пряме присвоєння `client.limits` після створення не перебудовує transport timeouts і pool limits.

Використовуй `async with`, або виклич `await client.aclose()` у `finally`. `aclose()` повертає `None`, передає закриття транспорту в httpx; після нього клієнт потрібно створити заново.

## request

Повертає `httpx.Response`, якщо статус менший за 400. Параметри `json`, `params`, `headers` передаються до httpx; `idempotency_key` формує `Idempotency-Key`. Сигнатура — [request](generated/jane_kit.clients.md#jane_kitclientsserviceclientrequest).

| Умова | Поведінка |
|---|---|
| Безпечний метод або заданий `idempotency_key` | Дозволено обмежені повтори |
| Інший метод без ключа | Одна спроба, навіть за тимчасової помилки |
| HTTP 400+ | `RemoteError` зі статусом, тілом і розібраним Problem за можливості |
| `ConnectError`, `ReadError`, `ReadTimeout`, `RemoteProtocolError` | Повтор за дозволом; остання помилка передається caller |
| Інша транспортна помилка httpx | Передається caller без цієї retry-гілки |

Повтор HTTP-помилки додатково потребує `RemoteError.retryable == True` і невичерпаного `max_attempts`. `retryable` бере значення з Problem, якщо воно задане; інакше перевіряє `RETRY_STATUSES` або статус 500+. Затримка використовує `Retry-After` чи backoff із jitter та `max_backoff_ms`. Точні множини методів і статусів — [clients.py](../../../../../libs/jane-kit/src/jane_kit/clients.py).

## get_json і post_json

`get_json(url, **kw)` та `post_json(url, json, *, idempotency_key=None, **kw)` викликають `request`, потім `.json()`. Результат — розібраний JSON без додаткової перевірки бізнес-схеми. Крім помилок `request`, невалідний JSON може спричинити `ValueError`.

## wait_for_job

`wait_for_job(job_url)` опитує адресу job до термінального стану. Повертає `dict` також для `failed` або `cancelled`: caller має перевірити `status`. Нетермінальна job після `job_wait_timeout_ms` спричиняє `TimeoutError`; помилки HTTP/JSON передаються з `get_json`. Частота — `job_poll_interval_ms`.

## new_idempotency_key

Статичний `new_idempotency_key()` повертає новий UUID як `str`. Створи його один раз на логічну операцію й повторно використовуй для того самого запиту. Зміна тіла потребує нового ключа.

## Приклад

Після [мінімального запуску Jane Kit](../../quickstart.md), у другому терміналі виконай цей код через Python:

```python
import asyncio
from jane_kit.clients import ServiceClient

async def main():
    async with ServiceClient("http://127.0.0.1:8190") as client:
        response = await client.request("GET", "/hello")
        assert response.json() == {"message": "Jane"}
        info = await client.get_json("/v1/info")
        print(info["service_name"])

asyncio.run(main())
```

Для операцій, які змінюють стан, передавай ключ і перевіряй схему відповіді за [контрактом](../../../../../contracts/README.md). Ліміти та їхнє спадкування — [конфігурація Jane Kit](../../configuration.md).
