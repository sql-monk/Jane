# Storage: інтеграція

Використовуйте `handler.v1` для запису та `storage.v1` для читання. [Мінімальний Python-клієнт](quickstart.md#перший-запис) працює без Orchestrator і був перевірений з реальним filesystem-адаптером.

## Виклик і відповіді

`HandlerInvocation` містить `handler` із package_id/version, `inputs`, binding `connections.target` і `delivery.delivery_key`. Для replay збережіть ті самі тіло, delivery key та `Idempotency-Key`; зміна спостереження — нова доставка. `context.test_mode=true` перевіряє виклик і повертає simulated acknowledgements без запису.

HTTP 200 може містити `HandlerResult.status=failed`; перевіряйте `status` і `failure`, а не лише HTTP-статус. Короткий sync завершується одразу, довгий після `timeouts.sync_response_max_ms` повертає 202 із Job і Location. Опитуйте Job до terminal state; не припускайте, що accepted означає записаний результат.

Послідовність запису показує перевірку повтору й обмежені повтори конфлікту.

![Послідовність запису показує перевірку повтору й обмежені повтори конфлікту.](../../diagrams/storage/write-flow.light.png)

[Темна тема](../../diagrams/storage/write-flow.dark.png) · [Редаговане джерело](../../diagrams/storage/write-flow.drawio)

## Читання

`GET /v1/entities` фільтрує за `connection_id`, `entity_type` та канонічним `key`; історія — `GET /v1/entity-history`. `GET /v1/objects` віддає посилання на збережені об’єкти, `GET /v1/objects/{id}` — метадані й material, якщо його можна відновити. `/content` підтримує HTTP Range для preview. Пагінація використовує `items`/`next_cursor`; клієнт передає курсор без змін.

## Заміна адаптера

1. Встановіть дистрибутив адаптера, який реалізує StorageAdapter, і пройдіть його compatibility suite.
2. Створіть connection потрібного kind із параметрами й `secret_refs`.
3. Змініть `handler.package_id` та binding `connections.target` у клієнті або етапі; природний ключ, observation та delivery залишають ту саму семантику.
4. Запишіть тестове спостереження й перевірте entities/history через API нового сховища.

Наприклад, заміна `jane.storage-files` на `jane.storage-postgresql` потребує `kind=postgresql`, доступної бази, схеми й дозволеного hostname. Дані зі старого filesystem не переносяться автоматично. [Параметри адаптерів](../../../services/storage/adapters/), [перевірка заміни](../../../services/storage/tests/test_adapter_swap.py).

## Композиція в Jane

Orchestrator отримує матеріал/результати попередніх етапів і сам викликає storage-пакет. Логічний потік Collector → Extractor → Storage не означає прямого виклику Collector у Storage. Один і той самий HTTP-контракт доступний сторонньому клієнту. [Навігація API](reference/api/README.md).
