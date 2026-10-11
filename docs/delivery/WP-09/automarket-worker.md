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
Повний `just check` не запускався для цього вузького доповнення. Незалежне рев’ю прийняло зміну;
фактичні результати й початкові падіння наведені нижче.

## Незалежне рев’ю 1 і діагностика

Рев’юер підтвердив `10 passed in 113.41s` для нових тестів, mypy, ruff, форматування та
`WP-09: 5 changed file(s), 0 outside ownership`. Його ширший запуск дав
`1 failed, 46 passed, 62 deselected in 149.03s`: у `test_every_operation_matches_contract`
запуск не досяг `succeeded` за незмінні 30 секунд (`test_contract.py:53`). Окремий повтор
також дав `1 failed in 64.46s`. Початковий вердикт — changes requested до діагностики.

Автор перевірив точний сценарій на базі `0b554fc` в окремому checkout і на `e595c1c`.
Обидва пройшли; тайм-аут і перевірки не змінювалися. Тимчасовий read-only діагностичний
hook лише мав читати статуси й помилки тестової черги при падінні; сценарій на зміні пройшов.
Причинність попередніх тайм-аутів не доведена. Ці результати не замінюють записаних падінь.

```powershell
uv run --group dev --package jane-orchestrator pytest services/orchestrator/tests/test_contract.py::test_every_operation_matches_contract -q
```

```text
# База 0b554fc, окремий checkout
1 passed in 146.84s (0:02:26)
# Зміна e595c1c, із read-only diagnostic hook
1 passed in 104.57s (0:01:44)
```

Незалежний рев’юер повторив точний сценарій на незміненому `e595c1c` із `login=false`:

```text
1 passed in 47.64s
```

Вердикт щодо фільтра `task_ids` — **accepted**: блокуюче зауваження закрите успішним
повтором без skip, зміни тайм-ауту чи послаблення перевірок. Попередні падіння збережено в цьому звіті.

## Складання окремого образу

За дорученням координатора образ зібрано з чистого checkout `e595c1c`:

```powershell
docker build -f services/orchestrator/Dockerfile -t jane-automarket-orchestrator:e595c1c .
docker image inspect jane-automarket-orchestrator:e595c1c --format '{{.Id}}'
```

```text
#22 naming to docker.io/library/jane-automarket-orchestrator:e595c1c 1.0s done
#22 unpacking to docker.io/library/jane-automarket-orchestrator:e595c1c 8.8s done
#22 DONE 22.1s
sha256:6ed92b88115eb6ef03480473f37e1fcba599d9c23aa78453dfac98a5f500dec2
```

Поточні контейнери й порти не змінювалися. Для worker-only контейнера координатор має
вимкнути HTTP health-check образу: команда `python -m jane_orchestrator worker` не відкриває HTTP.

## Запити до координатора

Зібрати окремий образ і запустити worker з указаним allowlist, налаштованими виконавцями та
спільною службовою БД оркестратора. Синхронізація підключень і бюджетів лишилася спільною для
процесу. Публічний API і контрактний документ платформи додаткового поля не потребують.

## Виправлення після CI-рев’ю 2

На `main` у ревізії `582cae3`, CI run `38113752875`, `just types` виявив
`services/orchestrator/tests/test_task_workers.py:126: Need type annotation for "rows" [var-annotated]`.
Початкова локальна перевірка mypy охопила лише `src` (20 файлів) і пропустила типи тестів,
які CI перевіряє разом із кодом сервісу (34 файли).

Додано `rows: dict[str, str]`: у цьому тесті SQL повертає пари `task_id` і `status`
для двох створених задач; обидва значення — рядки. SQL, перевірки, параметри worker і runtime
залишилися без змін. Тести PostgreSQL не повторювалися для анотації. Образ і контейнери
не збиралися й не запускалися під час виправлення; freeze розгортання збережено.

```powershell
uv run --group dev --package jane-orchestrator mypy services/orchestrator/src services/orchestrator/tests
uv run --group dev --package jane-orchestrator ruff check services/orchestrator/tests/test_task_workers.py
uv run --group dev --package jane-orchestrator ruff format --check services/orchestrator/tests/test_task_workers.py
```

```text
Success: no issues found in 34 source files
All checks passed!
1 file already formatted
```

Незалежний рев’юер підтвердив форму SQL-результату, незмінність SQL та перевірок і повторив
повний mypy: `Success: no issues found in 34 source files`, exit code 0. Вердикт — **accepted**.
Службовий код лишився на `e595c1c`; виправлення охоплює лише анотацію тесту й цей звіт.
