# Storage: будова

API готує пакет, підключення та input, після чого StorageHandler застосовує спільний StorageEngine до відкритого адаптера. [Source](../../../services/storage/src/jane_storage/) містить алгоритми; [StorageAdapter](../../../contracts/python/src/jane_contracts/storage_adapter.py) визначає межу змінного сховища.

[Компоненти](#компоненти) · [Алгоритм](#алгоритм) · [Власні дані](#власні-дані) · [Стани](#стани) · [Розробка](#розробка)

## Компоненти

```text
services/storage/
├── src/jane_storage/app.py          # API, jobs, connections, читання
├── src/jane_storage/handler.py      # Перевірка й виконання пакетів
├── src/jane_storage/engine.py       # Доставка й compare-and-swap commit
├── src/jane_storage/merge.py        # Чиста семантика полів EntityRecord
├── src/jane_storage/connections.py  # Secret refs і pool адаптерів
├── src/jane_storage/packages.py     # Каталог і canonical archives
├── adapters/                       # Шість реалізацій StorageAdapter
└── tests/                          # HTTP, core, swap, policy, contract
```

StorageHandler використовує каталог, pool і engine; engine залежить від протоколу адаптера.

![StorageHandler використовує каталог, pool і engine; engine залежить від протоколу адаптера.](../../diagrams/storage/types.light.png)

[Темна тема](../../diagrams/storage/types.dark.png) · [Редаговане джерело](../../diagrams/storage/types.drawio)

## Алгоритм

Для entity запису delivery key розширюється суфіксом номера input. Відомий delivery record повертає duplicate ack. Для нового запису engine читає snapshot, обчислює merge і commits з expected_version. CONFLICT перечитує state та повторює до conflict_retries.max_attempts; вичерпання дає retryable failure.

Поле в `fields` задає значення, пропущене поле лишається, а `cleared` видаляє поле й пам’ятає очищення. `null` і одночасне set/clear одного поля відхиляються. Порядок спостережень визначає [order_tuple](../../../contracts/python/src/jane_contracts/storage_adapter.py): тільки новіше спостереження змінює поле. Запізнілі поля потрапляють в history, не перезаписуючи актуальні. Version зростає навіть для stale-only спостереження.

Merge розрізняє пропущене поле, set, clear та запізніле спостереження.

![Merge розрізняє пропущене поле, set, clear та запізніле спостереження.](../../diagrams/storage/merge-process.light.png)

[Темна тема](../../diagrams/storage/merge-process.dark.png) · [Редаговане джерело](../../diagrams/storage/merge-process.drawio)

## Власні дані

Логічна модель: snapshot ключа entity_type/canonical_key, history event версії, delivery record із ack, RAW/result object bytes і metadata. Фізичне розміщення визначає адаптер; схема нижче не приписує filesystem SQL foreign keys.

Snapshot, history й delivery об’єднуються ключами; objects мають власні метадані.

![Snapshot, history й delivery об’єднуються ключами; objects мають власні метадані.](../../diagrams/storage/data.light.png)

[Темна тема](../../diagrams/storage/data.dark.png) · [Редаговане джерело](../../diagrams/storage/data.drawio)

Filesystem зберігає `entities`, `history`, `deliveries`, `objects` та `index/objects`. Object meta-файл є commit marker; entity commit має recovery незавершеного запису. [Файловий адаптер](../../../services/storage/adapters/files/src/jane_storage_files/__init__.py). HTTP jobs/results/connections — process memory; їхній backup не замінює backup адаптерних даних.

## Стани

Jobs використовують Jane Kit стани queued/running/cancelling/succeeded/failed/cancelled; HandlerResult success/empty/failed і WriteAck written/partially_stale/stale/duplicate/simulated — окремі поняття. Помилка adapter виконання може бути HTTP 200 із failed HandlerResult.

Job переходить у terminal state після завершення або скасування роботи.

![Job переходить у terminal state після завершення або скасування роботи.](../../diagrams/storage/jobs.light.png)

[Темна тема](../../diagrams/storage/jobs.dark.png) · [Редаговане джерело](../../diagrams/storage/jobs.drawio)

## Розробка

```powershell
uv run --all-packages pytest services/storage/tests/test_core.py services/storage/tests/test_app.py
uv run --all-packages pytest services/storage/adapters/files/tests/test_compat.py
```

Перші тести перевіряють real core та HTTP; другі — контракт filesystem адаптера. Для зовнішніх адаптерів потрібні їхні явно налаштовані інфраструктурні fixtures. [Compat suite](../../../services/storage/src/jane_storage/compat/suite.py), [публічні типи](reference/types/README.md).

## Застосовність діаграм

Context/deployment/dependencies об’єднані в context, класи/протоколи — types, логічна ER — data, алгоритм — merge-process, API-послідовність — write-flow в [integration](integration.md), jobs — jobs. Окрема схема UI сценаріїв N/A: Storage не має власного UI; сценарій клієнта наведено в quickstart.
