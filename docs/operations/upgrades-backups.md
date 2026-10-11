# Оновлення й резервні копії

Сервіс володіє власним станом. Резервування має охопити і метадані, і байти об’єктів, на які вони посилаються.

## Що зберігати

| Власник | Постійний стан |
|---|---|
| Orchestrator | Власна PostgreSQL база: завдання, запуски, черга, аудит |
| Registry | PostgreSQL метадані та content-addressed архіви у S3/MinIO або files |
| Handler Runtime, LLM, Assistant | Власні PostgreSQL state/job/idempotency; конфігурація провайдерів |
| Колектори | Власні SQLite-каталоги стану та потрібний вміст |
| Storage | Дані й delivery ledger обраних адаптерів, індекси, RAW, сутності та історія |

Memory-режим не зберігається після перезапуску. Тимчасовий package cache можна відбудувати з Registry; втрата постійного RAW не компенсується кешем. Секрети й runtime-конфігурація резервуються окремо під контролем оператора.

## Порядок оновлення

1. Зафіксуй ревізії коду, images, контрактів і профілів; зупини прийняття нових запусків.
2. Дочекайся завершення або скасуй активні роботи, зупини writer-процеси.
3. Зроби узгоджену копію власних баз і blob/adapter сховищ.
4. Перевір сумісність версій, запусти сервіси. Їхній startup застосовує власні pending migrations там, де це реалізовано.
5. Перевір health, info, збережені версії пакетів і контрольний запис/читання.
6. Дозволь нові запуски після перевірки результату.

Для Orchestrator міграції серіалізуються advisory lock у [db.py](../../services/orchestrator/src/jane_orchestrator/db.py). Відкат коду не є відкатом схеми: зворотне читання нової схеми потрібно перевірити окремо; за несумісності відновлюється погоджена копія.

## Приклад копії PostgreSQL

Команди для тестового `jane-demo`, створеного [швидким стартом](../getting-started/README.md). Перед ними зупини writer-сервіси. Створення dump усередині контейнера з подальшим `docker cp` зберігає двійкові байти й на Windows.

```powershell
New-Item -ItemType Directory -Force .jane/backups
$pg = docker ps --filter "label=com.docker.compose.project=jane-demo" --filter "label=com.docker.compose.service=postgres" --format "{{.ID}}"
docker exec $pg pg_dump -U jane -d jane_orchestrator -Fc -f /tmp/orchestrator.dump
docker cp "${pg}:/tmp/orchestrator.dump" .jane/backups/orchestrator.dump
```

Для відновлення перевіряй копію в окремій тестовій базі. Не замінюй активну базу до перевірки стану й узгодження часу відновлення.

```powershell
docker exec $pg createdb -U jane documentation_restore
docker exec $pg pg_restore -U jane -d documentation_restore --no-owner --no-privileges /tmp/orchestrator.dump
docker exec $pg psql -U jane -d documentation_restore -c "SELECT count(*) FROM tasks;"
```

Зістав кількість і вміст джерел, завдань, запусків та schema_migrations із копією. Для повного відновлення віднови також Registry blob і сховища Storage, звір SHA-256, дай сервісам доступ до узгоджених paths/endpoints.

## Репетиція повного резервування

Для ізольованого стенду з назвою `jane-docs-*` є [виконуваний приклад](examples/backup_restore.py). Він зупиняє власні writer-сервіси, копіює шість PostgreSQL-баз і чотири томи, відновлює копії в нові тестові ресурси й порівнює вміст. Після перевірки видаляються лише створені клони; початкові сервіси запускаються знову.

```powershell
uv run --all-packages python docs/operations/examples/backup_restore.py --project jane-docs-20261011
```

Команда потребує вже запущеного стенду з цією назвою. Повний фактичний результат і межі застосування — у [звіті DOC-08](../delivery/documentation/DOC-08.md). Для іншої інфраструктури адаптуй процедуру до власників даних, перевір відновлення й узгодженість посилань, перш ніж замінювати робочі дані.
