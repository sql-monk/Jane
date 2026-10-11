# WP-09. Окремий worker для каталогу автобазарів

**Гілка:** `wp/09-targeted-catalog-worker` · **База:** `0b554fc` · **Стан:** review

## Результат

Додано внутрішній параметр `engine.task_ids` у [Settings](../../../services/orchestrator/src/jane_orchestrator/settings.py).
У [Engine](../../../services/orchestrator/src/jane_orchestrator/engine.py) він обмежує захоплення збору,
елементів етапів, створення запланованих запусків і завершення запусків заданими task ID.
Відсутній параметр або `[]` зберігає загальну чергу й FIFO. Фільтр передається SQL-параметром;
lease, `FOR UPDATE SKIP LOCKED`, ключі доставки й правила спроб не змінюються.

## Конфігурація

| Параметр | Типово | Формат |
|---|---|---|
| `JANE_ORCHESTRATOR_LIMITS__ENGINE__TASK_IDS` | `[]` — усі задачі | JSON-масив або CSV |

Приклад для окремого процесу з тією самою власною PostgreSQL БД оркестратора й налаштованими виконавцями:

```powershell
$env:JANE_ORCHESTRATOR_LIMITS__ENGINE__TASK_IDS = '["ads-autoria","ads-rst"]'
uv run --package jane-orchestrator python -m jane_orchestrator worker
```

Альтернативне значення — `ads-autoria,ads-rst`. Порожній рядок, порожній елемент, нестроковий ID
або невалідний JSON спричиняє помилку; помилкова конфігурація не розширює вибірку до всіх задач.
Налаштування описано в [README](../../../services/orchestrator/README.md#ліміти).

## Відповідність критеріям і DoD

| Умова | Перевірка | Результат |
|---|---|---|
| Окремий worker обходить старішу чужу задачу й не захоплює її | PostgreSQL тест `test_targeted_claims_bypass_older_task_and_keep_leases_and_delivery_key` | Пройдено |
| Загальний worker обробляє обидві задачі в FIFO | Той самий тест: старіша задача захоплюється першою; згодом дозволена задача доступна загальному worker | Пройдено |
| Кілька worker не дублюють захоплення | Чинний feed lease недоступний другому worker | Пройдено |
| Відновлення не дублює ефекти | Втрата item lease, перехоплення з тим самим ключем і номером спроби, один ефект storage та один replay | Пройдено |
| Планувальник і завершення не змінюють чужі запуски | PostgreSQL тест `test_targeted_scheduler_and_housekeeping_leave_other_tasks_for_general_worker` | Пройдено |
| Зміна конфігурації без коду | Unit-тести JSON, CSV, `[]` і відхилення помилкових значень | Пройдено |
| API за контрактом | Наявні контрактні тести входять у запуск без integration; внутрішній параметр не входить до PlatformLimits | Пройдено |
| Dockerfile, health, журнали, метрики | Наявні механізми не змінювалися | Без змін |
| Власність шляхів | Лише `services/orchestrator/**` і цей звіт WP-09 | Перевірено |

## Команди й фактичний вивід

```powershell
uv run --group dev --package jane-orchestrator pytest services/orchestrator/tests/test_task_workers.py -q
```

```text
..........                                                               [100%]
10 passed in 51.55s
```

```powershell
uv run --group dev --package jane-orchestrator pytest services/orchestrator/tests -m 'not integration' -q
```

```text
...............................................                          [100%]
47 passed, 62 deselected in 74.45s (0:01:14)
```

```powershell
uv run --group dev --package jane-orchestrator mypy services/orchestrator/src
```

```text
Success: no issues found in 20 source files
```

```powershell
uv run --group dev --package jane-orchestrator ruff check services/orchestrator/src services/orchestrator/tests/test_task_workers.py
uv run --group dev --package jane-orchestrator ruff format --check services/orchestrator/src services/orchestrator/tests/test_task_workers.py
```

```text
All checks passed!
21 files already formatted
```

## Межі перевірки

Черга й міграції перевірені на справжній ізольованій PostgreSQL БД, створеній тестовою fixture.
Колектор і storage — замінники сусідів, які перевіряють запити та відповіді за контрактами.
Нове налаштування не перевірено на реальному сервісі в поточному стеку; запуск контейнера,
інтеграцію пакетів і даних автобазарів виконує координатор. Main і поточні контейнери не змінювалися.
Повний `just check` не запускався для цього вузького доповнення. Незалежне рев’ю очікується.

## Запити до координатора

Зібрати окремий образ і запустити worker з указаним allowlist, налаштованими виконавцями та
спільною службовою БД оркестратора. Синхронізація підключень і бюджетів лишилася спільною для
процесу. Публічний API і контрактний документ платформи додаткового поля не потребують.
