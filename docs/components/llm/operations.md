# LLM: експлуатація

Бюджет, usage, jobs та ідемпотентність потрібно зберігати разом у власному постійному store. Memory-режим придатний лише для локальної демонстрації й тестів.

[Спостереження](#спостереження) · [Оновлення](#оновлення) · [Резервування](#резервування) · [Відновлення](#відновлення) · [Типові проблеми](#типові-проблеми)

## Спостереження

Health перевіряє state store. Info показує provider_kinds/store/limits; providers, aliases, budgets та usage доступні окремими API. Зіставляйте provider/model/purpose і scope із trace_id у структурованих журналах. Перевіряйте не тільки HTTP 200, а й completion.valid/validation_errors та finish_reason.

`GET /v1/usage` дає облік токенів і вартості з group_by/filter контракту; `/metrics` — технічні метрики. Fake response з cost=0 не підтверджує налаштування реального pricing або провайдерського білінгу. Expired reservation charged at estimate може збільшити spent після аварії навіть без отриманої відповіді.

## Оновлення

Завершіть jobs, збережіть стан, providers/aliases/connections/budgets та pinned пакети. Після оновлення увімкніть той самий PostgreSQL schema й перевірте health, info та aliases. Seed додає лише відсутні записи; змініть існуючий provider через API з ETag/If-Match. У memory після рестарту відновіть потрібні definitions із seed і прийміть втрату старого usage/keys.

Під час open PostgresStore створює власну схему/DDL й Jane Kit state migrations; ручне редагування таблиць сусідніх сервісів не є частиною процедури. Перед зміною PostgreSQL-структури перегляньте [store.py](../../../services/llm/src/jane_llm/store.py) та релевантні [multi-instance tests](../../../services/llm/tests/test_multi_instance.py).

## Резервування

Зупиніть власні jobs і provider виклики, після чого зробіть consistent backup db_schema, включно з config/counters/reservations/usage/invocations/jobs/idempotency. Приклад із PostgreSQL client tools та вже налаштованими PGHOST/PGUSER/PGPASSWORD:

```powershell
pg_dump --format=custom --file=llm.backup --schema=llm --dbname=llm_db
```

Вкажіть власні database/schema і захистіть backup, бо конфігурація містить secret refs та usage. Значення secrets з env/files резервуйте окремо. Локальні package dirs і seed зберігайте поряд з операторською конфігурацією.

## Відновлення

Відновлюйте у нову власну базу, не поверх активного store:

```powershell
pg_restore --dbname=llm_restore --no-owner llm.backup
```

Налаштуйте DSN нової бази й потрібні secrets; запустіть один екземпляр, перевірте providers/aliases/budgets, групування usage та завершені jobs. Потім перевірте локальний fake completion із новим ключем і доступність старих idempotency записів у межах TTL. Повернення до старої бази можливе до нових production записів; після нових витрат потрібне узгодження двох станів, не просте перемикання.

Власний PostgreSQL backup/restore у цьому модульному пакеті не виконувався; координатор має окреме [platform evidence](../../delivery/documentation/DOC-08.md). Зовнішній LLM у модульній перевірці не викликався.

## Типові проблеми

| Симптом | Причина або перевірка | Дія |
|---|---|---|
| Старт вимагає DATABASE_URL | Default store=postgres | Встановіть DSN або свідомо оберіть memory |
| `not_found` model | Alias/provider/models | Створіть alias або виправте model ID |
| Provider disabled / unsupported kind | Provider.enabled і встановлені adapters | Увімкніть підтримуваний provider |
| `budget_exhausted` | Budget windows, reservations, currencies | Перегляньте usage і budget; не повторюйте безмежно |
| HTTP 200, `valid=false` | Schema retries вичерпано або truncated output | Перегляньте validation_errors/max_output_tokens |
| Provider timeout | provider.request_timeout_ms та attempts | Узгодьте timeout клієнта й gateway; async для довгих викликів |
| ContentRef denied | blob_roots/download_host_allowlist | Надайте мінімально потрібний root/host |
| 412 на редагуванні | Застарілий ETag | Перечитайте документ і перегляньте concurrent change |
| Budget рахується окремо у процесах | store=memory | Перейдіть на спільну власну PostgreSQL-схему |

[Конфігурація](configuration.md), [API](reference/api/README.md).
