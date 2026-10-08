# M3 should-fix — наскрізний інкремент потоку B

Дата: 2026-10-09. Гілка: `wp/m3-should-fix`. База: `3c98542`.
Статус: **review**, до незалежного вердикту та повного CI не прийнято.
Доручення: `docs/delivery/HANDOFF-2026-10-09-stream-b.md`, §3.4 з `origin/codex/jane-integration`.
`main`, checkout інтеграції потоку A, `wp01g`, `wp01h`, `libs/jane-kit/**`, `contracts/**`
та `docs/delivery/status.md` не змінювались цим інкрементом.

## Результат за пунктами

| № | Власник / файли | Поведінка й адресна перевірка |
|---|---|---|
| 1 | WP-06: `libs/extractor-sdk/src/jane_extractor_sdk/package.py`, `tests/test_sdk.py`, `README.md` | `build_archive` будує канонічний ZIP_STORED: порядок ASCII-шляхів, час 1980-01-01, права 0644, Unix, без extra/comment. Golden digest registry `sha256:e80692e640c2cb1a1976caaad1ba67460a0af0926012748f85748d15c6a404a0` збігається; перевірено розпакування й CLI прикладу. Коміт `4db7c27`. |
| 2 | WP-09: `services/orchestrator/src/jane_orchestrator/{core,executors,settings}.py`, `tests/test_executors.py`, `README.md` | Keep-alive з конфігурації: `executor_keepalive_expiry_ms=4000`, менше server keep-alive 5 с; `executor_stale_connection_retries=1`. Справжній HTTP-сервер перевіряє нове TCP-з'єднання після простою, повтор ідемпотентного/keyed запиту, відсутність повтору POST без ключа й вимкнення повторів. Коміт `236321c`. |
| 3 | WP-02: `services/web-collector/src/jane_web_collector/{egress,engine,fetcher,settings}.py`, `tests/test_egress_policy.py`, `README.md` | Заборонено link-local/metadata за замовчуванням (`egress_deny_link_local=true`), приватні/loopback адреси — за конфігурацією (`egress_deny_private=false` у dev). Кожне фактичне з'єднання після DNS та кожний redirect перевіряються; TCP йде на перевірений IP. Тести класифікують IPv4/IPv6, DNS, metadata, redirect для fetch/collection, приватні адреси. Коміт `6b67f1a`. |
| 4 | WP-10/WP-04: `services/{llm,telegram-collector}/src/*/connections.py`, відповідні `tests/test_secret_files.py` | `file:` повторно перевіряється й читається за розв'язаним дозволеним шляхом. Тести міняють symlink після перевірки/resolve, перевіряють дозволений symlink, NUL/бінарний файл/каталог. Коміт `e0cc576`. |
| 5 | WP-10: `services/llm/src/jane_llm/connections.py`, `tests/test_api_base.py` | Невалідний порт `:99999`/`:abc`, зламаний IPv6 URL → 422 з `/params/api_base`, без збереження підключення. Старі невалідні дані не отримують секретів і не викликають провайдер. Коміт `2f77ae6`. |
| 6 | WP-09: `services/orchestrator/src/jane_orchestrator/engine.py`, `tests/orch_support.py`, `tests/test_stored_raw.py`, `README.md` | Reprocessing запитує storage `GET /v1/objects` із `source_id` завдання; явно чуже джерело у summary/detail додатково відкидається. Два джерела мають однакові URL/material_id, але один material_id дає лише власне observation; повний запит дає 6 власних RAW, а не 12. |
| 7 | WP-09: `services/orchestrator/src/jane_orchestrator/{engine,db,service,stored_raw}.py`, `tests/test_stored_raw.py`, `README.md` | Відомий RAW id з фактичного storage write записується в item цього запису; id зі storage-read — у collect item reprocessing. Власна міграція 4 додає nullable `items.stored_object_id` та індекс. API збагачує наявні `ProblemGroup.samples[].stored_object_id` і `UnknownMaterial.stored_object_id` за source/observation/run (для sample — через invocation). Немає залежності від пам'яті процесу чи таблиць storage; RAW, що завершився після екстрактора, стає доступним при наступному читанні. Simulated/missing/неоднозначний id не вигадується. |

Прочитано `CLAUDE.md`, ТЗ §4–§5/§9/§10/§12, plan §3–§5, `DEVELOPMENT.md`, скіли
`jane-wp`, `jane-contracts`, `jane-handler-package`. Нових API/полів контрактів немає.

## Доказ регресії до виправлення 6–7

Тест і fake storage залишалися новими; лише `engine.py` тимчасово замінено байтами з HEAD `2f77ae6`,
після виконання автоматично відновлено незакомічену версію. Справжні оркестратор і PostgreSQL,
моки лише сусідів із валідацією storage/handler контрактів.

Команда: `uv run --all-packages --locked pytest services/orchestrator/tests/test_stored_raw.py -v -m integration`.
Повний вихід: `.jane/m3fix-6-7-before.txt` цього checkout.

```text
E       AssertionError: assert [('obs_job_7b...shop-mirror')] == [('obs_job_7b...hop-example')]
E         Left contains one more item: ('obs_job_0fe15a35baf041aea251_00000', 'shop-mirror')
services\orchestrator\tests\test_stored_raw.py:84: AssertionError
E       KeyError: 'stored_object_id'
services\orchestrator\tests\test_stored_raw.py:134: KeyError
============================= 2 failed in 54.70s ==============================
```

Середину diff пропущено; наведені рядки — зі справжнього виходу.

## Адресні перевірки після виправлення

Пункти 1–5:

```text
uv run --all-packages --locked pytest libs/extractor-sdk/tests/test_sdk.py services/orchestrator/tests/test_executors.py services/web-collector/tests/test_egress_policy.py services/llm/tests/test_secret_files.py services/telegram-collector/tests/test_secret_files.py services/llm/tests/test_api_base.py -v -m "not integration"
====================== 67 passed, 4 deselected in 7.27s =======================
```

Повний вихід: `.jane/m3fix-1-5-unit.txt`. Чотири deselected — PostgreSQL-варіанти LLM,
їх має виконати CI stack; це не локальний доказ PostgreSQL-backed LLM. Попередній запуск без маркера
дав `67 passed, 4 skipped` через відсутній dev-stack; він збережений у `.jane/m3fix-1-5-targeted.txt`.

Пункти 6–7: та сама адресна команда, двічі на **одному** власному тимчасовому PostgreSQL-контейнері
`jane-wp09-test-pg-<uuid>`, у кожного тесту окрема БД. Контейнер прибирає runner у `finally`.
Повні логи: `.jane/m3fix-6-7-after-1.txt`, `.jane/m3fix-6-7-after-2.txt`.

```text
services/orchestrator/tests/test_stored_raw.py::test_reprocessing_takes_only_raw_of_the_task_source PASSED [ 33%]
services/orchestrator/tests/test_stored_raw.py::test_problem_samples_and_unknown_materials_name_the_stored_raw PASSED [ 66%]
services/orchestrator/tests/test_stored_raw.py::test_stored_raw_migration_upgrades_an_existing_database PASSED [100%]
======================== 3 passed in 80.46s (0:01:20) =========================
```

Другий прогін на тому самому контейнері:

```text
services/orchestrator/tests/test_stored_raw.py::test_reprocessing_takes_only_raw_of_the_task_source PASSED [ 33%]
services/orchestrator/tests/test_stored_raw.py::test_problem_samples_and_unknown_materials_name_the_stored_raw PASSED [ 66%]
services/orchestrator/tests/test_stored_raw.py::test_stored_raw_migration_upgrades_an_existing_database PASSED [100%]
============================= 3 passed in 47.21s ==============================
```

Обидва прогони: 0 skipped. CI і незалежний вердикт залишаються обов'язковими для accepted.

Тест 7 утримує RAW-запис у сусіда до реєстрації проблеми: спочатку id відсутній, після завершення RAW —
правильний id. Simulated test-run не має id; новий API instance без workers читає ту саму durable прив'язку;
повторна обробка використовує id прочитаного RAW. Обидві відповіді API валідовано за наявним OpenAPI.
Міграція перевіряється на новій БД через startup та на schema 3 із записом, який зберігається після upgrade;
другий виклик migrate не змінює даних. Тест коректно очікує 3 проблемні samples для 2 observations:
одна проблема виникла і в live, і в reprocessing запуску.

Ruff для змінених компонентів / strict mypy оркестратора:

```text
All checks passed!
101 files already formatted
Success: no issues found in 22 source files
```

Логи: `.jane/m3fix-lint.txt`, `.jane/m3fix-orch-types.txt`.
Повні локальні `just check`/`just e2e` не запускались згідно з handoff.
Залишений попередником `.jane/m3fix-6-orch-integration.txt` має `1 failed, 39 passed` і втрату PostgreSQL
під час тесту backpressure; його не враховано як доказ готовності. Остаточний gate — CI stack/e2e.

## Власність і секрети

Це явно доручений handoff §3.4 інкремент із п'ятьма власниками, а не один номер `.jane-wp`.
Стандартний check-diff для одного WP показує чужі власності; виняток охоплює лише області таблиці вище
і цей звіт. Додатково `.jane/m3fix_ownership.py` перевіряє **delta від 3c98542** через справжню функцію
`check` з `.claude/hooks/jane_wp.py` та `.claude/wp-paths.json` для кожного власника.
Результат у `.jane/m3fix-ownership.txt`:

```text
M3 report (handoff section 3.4): 1 task-scoped files
WP-02: 6 task-scoped files
WP-04: 2 task-scoped files
WP-06: 3 task-scoped files
WP-09: 11 task-scoped files
WP-10: 3 task-scoped files
Base 3c98542: 26 files; 0 outside the explicit cross-owner assignment
```

Inherited зміна `status.md` у базовому
`3c98542` не належить цьому інкременту. Файли потоку A не редагувалися.

Окремий gitleaks для попередніх п'яти комітів:

```text
5 commits scanned.
scanned ~51187 bytes (51.19 KB) in 503ms
no leaks found
```

Повний лог: `.jane/m3fix-previous-commits-secrets.txt`. Новий staged diff також сканується перед commit.
Тестові матеріали/секрети — локальні фікстури; зовнішні LLM/Telegram сервіси не перевірено.

## CI і review

Після push запускається `gh workflow run ci --ref wp/m3-should-fix` для повного stack/adapters/e2e.
Ідентифікатор запуску, його точний SHA й результат передаються координатору для журналу потоку B;
живі запуски доступні в [Actions цієї гілки](https://github.com/sql-monk/Jane/actions?query=branch%3Awp%2Fm3-should-fix).
Авторська локальна перевірка сама по собі не закриває gate CI. Незалежний reviewer призначає координатор.

## Запити до інших власників

1. **WP-00 / coordinator:** чи має `stored_materials` обирати конкретний RAW `object_id` або `observation_id`?
   Наявний `material_ids` обирає всі спостереження матеріалу цього джерела в заданому часовому вікні;
   виправлення source_id не перетворює його на точний вибір однієї ревізії. Для UI «цей конкретний RAW»
   потрібне рішення контракту (після погодження — contract-guardian і оновлення споживачів).
   `ReprocessRequest` і `contracts/**` тут не змінювались.
2. **WP-12d:** після прийняття й злиття цього інкременту прибрати локальний `test.fail` у real-сценарії
   «reprocessing one stored material takes only RAW of the task's source», запустити цей real-тест.
   Ці файли належать іншому виконавцю й тут не редагувались.
3. **Потік A:** final M3 CI/матриця/real admin gate й остаточний merge до main лишаються вашим дорученням.
