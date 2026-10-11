# Storage: типи й публічні члени

Generated довідник перелічує всі публічні декларації поточного source: класи/інтерфейси/протоколи, конструктори, методи, функції, поля, властивості й constants. Сторінка кожного модуля містить сигнатури, parameters/results, source links та доступність property. Ручні пояснення нижче допомагають вибрати точку розширення; generated файли змінює тільки генератор.

## Навігація

| Завдання | Типи та модулі |
|---|---|
| Повний перелік | [Generated index](generated/README.md) |
| Відкрити HTTP застосунок | [app.build_app](generated/jane_storage.app.md) |
| Запис через відкритий адаптер | [StorageEngine](generated/jane_storage.engine.md) |
| Перевірити й виконати пакет | [StorageHandler](generated/jane_storage.handler.md) |
| Чисте злиття entity | [merge, MergeResult, InvalidRecord](generated/jane_storage.merge.md) |
| Реалізувати адаптер | [StorageAdapter](../../../../../contracts/python/src/jane_contracts/storage_adapter.py), [compat suite](generated/jane_storage.compat.suite.md) |
| Дізнатися формат RAW | [formats](generated/jane_storage.formats.md) |
| Connections/pool/policy | [connections](generated/jane_storage.connections.md), [policy](generated/jane_storage.policy.md) |
| Canonical archive/catalog | [packages](generated/jane_storage.packages.md) |
| Всі шість адаптерів | Generated index, секції jane_storage_files/postgres/minio/s3/mongodb/sqlserver |

## Результати й винятки

StorageEngine повертає WriteAck, merge — frozen MergeResult із snapshot/applied/stale й read-only property status. StorageAdapter errors перетворюються handler у failed результат; InvalidRecord відхиляє семантично некоректні fields/cleared. ConflictRetriesExhausted є retryable AdapterError. Сигнатури кожного методу й source links зберігає generated page.

## Приклад використання

HTTP-приклад у [quickstart](../../quickstart.md#перший-запис) є мінімальним стороннім застосунком. Для власного Python адаптера реалізуйте StorageAdapter та запустіть compat suite; підміна StorageEngine фейком не перевіряє семантику merge. [Класи і власні дані](../../internals.md).
