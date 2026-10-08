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
| 4 | WP-10/WP-04: `services/{llm,telegram-collector}/src/*/{connections,secret_files}.py`, відповідні `tests/test_secret_files.py` | `file:` читається через перевірені дескриптори відкритих об'єктів і всіх компонентів resolved шляху. Тести міняють symlink/reference, resolved target/parent до відкриття та target/parent після відкриття; дозволений safe symlink, NUL/бінарний файл/каталог також перевірені. Початковий коміт `e0cc576`; race у самому resolved target/parent виправлено після рев'ю 1 нижче. |
| 5 | WP-10: `services/llm/src/jane_llm/connections.py`, `tests/test_api_base.py` | Невалідний порт `:99999`/`:abc`, зламаний IPv6 URL → 422 з `/params/api_base`, без збереження підключення. Старі невалідні дані не отримують секретів і не викликають провайдер. Коміт `2f77ae6`. |
| 6 | WP-09: `services/orchestrator/src/jane_orchestrator/engine.py`, `tests/orch_support.py`, `tests/test_stored_raw.py`, `README.md` | Reprocessing запитує storage `GET /v1/objects` із `source_id` завдання; явно чуже джерело у summary/detail додатково відкидається. Два джерела мають однакові URL/material_id, але один material_id дає лише власне observation; повний запит дає 6 власних RAW, а не 12. |
| 7 | WP-09: `services/orchestrator/src/jane_orchestrator/{engine,db,service,stored_raw}.py`, `tests/test_stored_raw.py`, `README.md` | Відомий RAW id з фактичного storage write записується в item цього запису; id зі storage-read — у collect item reprocessing. Міграція 4 додає nullable `items.stored_object_id`, міграція 5 — durable ознаку неоднозначності; див. виправлення review 1 нижче. API збагачує наявні `ProblemGroup.samples[].stored_object_id` і `UnknownMaterial.stored_object_id` за source/observation/run (для sample — через invocation). Немає залежності від пам'яті процесу чи таблиць storage; RAW, що завершився після екстрактора, стає доступним при наступному читанні. Simulated/missing/неоднозначний id не вигадується. |

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

## Виправлення після рев'ю 1 — TOCTOU `file:` (пункт 4)

Рев'юер відтворив 4 витоки: після `secret_file()` resolved target або його батьківський каталог
замінюється symlink; `Path.read_text()` відкриває вже зовнішній файл. Попередня перевірка resolved pathname
була недостатньою. Repro автора зі сценарію рев'юера: `.jane/review-m3-toctou-repro.py`.
Справжній вихід до виправлення у `.jane/m3fix-review1-before.txt`:

```text
llm resolved-target-swap: outside-secret
llm resolved-parent-swap: outside-secret
telegram resolved-target-swap: outside-secret
telegram resolved-parent-swap: outside-secret
```

Нові pytest-регресії до виправлення:

```text
uv run --all-packages --locked pytest services/llm/tests/test_secret_files.py services/telegram-collector/tests/test_secret_files.py -v -k resolved_target_or_parent
FAILED services/llm/tests/test_secret_files.py::test_resolved_target_or_parent_swapped_before_open_is_not_read[target]
FAILED services/llm/tests/test_secret_files.py::test_resolved_target_or_parent_swapped_before_open_is_not_read[parent]
FAILED services/telegram-collector/tests/test_secret_files.py::test_resolved_target_or_parent_swapped_before_open_is_not_read[target]
FAILED services/telegram-collector/tests/test_secret_files.py::test_resolved_target_or_parent_swapped_before_open_is_not_read[parent]
======================= 4 failed, 8 deselected in 0.31s =======================
```

Повний log: `.jane/m3fix-review1-pytest-before.txt`.

Виправлення не перечитує pathname після перевірки: два service-owned `secret_files.py` читають
саме відкритий і перевірений файловий об'єкт. POSIX відкриває компоненти absolute resolved шляху
від filesystem root через `dir_fd`, `O_DIRECTORY` і `O_NOFOLLOW`; leaf — також `O_NOFOLLOW`,
`fstat` має підтвердити regular file до читання байтів. Відкриті directory/file descriptors утримуються
до завершення читання, тому підміна pathname після open не перенаправляє fd.
Можливості `dir_fd` та потрібні flags перевіряються; непідтримана платформа відмовляє у читанні.
Використані API задокументовані в [Python os](https://docs.python.org/3/library/os.html#os.open).

Windows відкриває кожен компонент із `FILE_FLAG_OPEN_REPARSE_POINT` і перевіряє атрибути
відкритого handle, відкидаючи reparse points і неправильний тип. Усі directory handles утримуються
без `FILE_SHARE_DELETE`, який потрібний також для rename; фактичний final handle path має збігтися
з перевіреним resolved path. CRT fd отримує той самий handle, `fstat` підтверджує regular file,
байти читаються лише після перевірок. Семантика: [CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew),
[GetFinalPathNameByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew).
Safe symlink підтриманий: його дозволений target розв'язується перед цим проходом.
`libs/jane-kit/**`, потік A, контракти та інші пункти M3 не змінювались.

Адресні тести на Windows після виправлення (`.jane/m3fix-review1-secret-after.txt`):

```text
uv run --all-packages --locked pytest services/llm/tests/test_secret_files.py services/telegram-collector/tests/test_secret_files.py -v
============================= 16 passed in 0.33s ==============================
```

Додані також 4 сценарії target/parent swap **після open, до першого байта**: POSIX читає старий
перевірений fd; Windows забороняє delete/rename, поки handles утримуються. У тесті підмінено лише
OS stream wrapper на межі читання, самі компоненти й файлові операції справжні.

Додаткова Linux-перевірка обох читачів на справжній POSIX FS у власному контейнері
`jane-m3fix-review1-posix`, readonly mount цього checkout; контейнер автоматично видаляється:

```text
docker run --rm --name jane-m3fix-review1-posix --mount type=bind,source=C:/repos/Jane/.claude/worktrees/wpm3fix,target=/repo,readonly python:3.12-slim python /repo/.jane/review1_posix.py
llm POSIX resolved-none: PASS
llm POSIX resolved-target: PASS
llm POSIX resolved-parent: PASS
llm POSIX resolved-opened-target: PASS
llm POSIX resolved-opened-parent: PASS
telegram-collector POSIX resolved-none: PASS
telegram-collector POSIX resolved-target: PASS
telegram-collector POSIX resolved-parent: PASS
telegram-collector POSIX resolved-opened-target: PASS
telegram-collector POSIX resolved-opened-parent: PASS
10 passed; real POSIX filesystem, no skipped
```

Log: `.jane/m3fix-review1-posix.txt`. Це адресні filesystem-сценарії, не повний local e2e.

Контрактна регресія на реальних apps (`.jane/m3fix-review1-contract.txt`):

```text
uv run --all-packages --locked pytest services/llm/tests/test_contract.py services/telegram-collector/tests/test_contract.py -v -m "contract and not integration"
======================= 3 passed, 2 deselected in 1.27s =======================
```

Два deselected — PostgreSQL-варіанти LLM; їх виконає full CI stack.
Ruff / format і strict mypy обох сервісів, додатково читачі з `--platform linux`:

```text
All checks passed!
35 files already formatted
Success: no issues found in 17 source files
Success: no issues found in 16 source files
Success: no issues found in 2 source files
```

Logs: `.jane/m3fix-review1-lint.txt`, `.jane/m3fix-review1-lint-types.txt`.
Коміт цього виправлення `c07d91a` спочатку залишався локальним до повного висновку рев'ю 1.
Повний review 1 отримано: два findings (TOCTOU і неоднозначний RAW). Координатор доручив після
адресного виправлення обох запушити гілку й запустити новий full workflow dispatch на фінальному SHA.
CI `37850604947` на старому `3b45a7b` не є фінальним доказом для виправленого інкременту.

## Виправлення після рев'ю 1 — finding 2: неоднозначні RAW (пункт 7)

Repro рев'юера `.jane/review-m3-ambiguous-raw-repro.py` повертає два валідні RAW object_id для одного
source/observation. Page map перезаписував id останньою копією, а collect item маршрутизував лише
перше спостереження. Вихід автора до виправлення (`.jane/m3fix-review1-ambiguity-before.txt`):

```text
storage valid RAW ids for same source/observation: ['obj_79886e6c09d14e92ad63', 'obj_review_duplicate']
reprocessing collect stored id: obj_review_duplicate
reprocessing problem sample stored id: obj_review_duplicate
storage contract violations: []
```

Координатор обрав omission для неоднозначної копії, без нового контракту. Міграція 5 додає
внутрішній `items.stored_object_ambiguous` з default false та частковий індекс. У межах однієї сторінки
storage різні id для того самого observation дають підтверджену неоднозначність; між сторінками
collect metadata об'єднується з уже записаними id/ознакою в тій самій feed-транзакції. Ознака не
скидається наступним повтором id, DAG для вже прийнятого observation удруге не запускається.
`stored_raw_id` враховує durable ознаку відповідного source/observation/run, тому collect, sample
і unknown material не вибирають довільну копію. Повтор того самого `object_id` залишається known.
README уточнено; `ReprocessRequest` і `contracts/**` не змінювались.

Нові регресії до виправлення (`.jane/m3fix-review1-ambiguity-pytest-before.txt`):

```text
uv run --all-packages --locked pytest services/orchestrator/tests/test_stored_raw.py -v -k ambiguous_raw
E           AssertionError: assert 'obj_ambiguous_0' == None
FAILED services/orchestrator/tests/test_stored_raw.py::test_reprocessing_omits_ambiguous_raw_references[distinct-objects-1]
FAILED services/orchestrator/tests/test_stored_raw.py::test_reprocessing_omits_ambiguous_raw_references[distinct-objects-100]
================= 2 failed, 2 passed, 3 deselected in 30.55s ==================
```

Два passed — повторення того самого id, два failed — різні id на сторінці або між сторінками.
Виправлений набір запускається двічі на одному власному PostgreSQL-контейнері:

```text
uv run --all-packages --locked pytest services/orchestrator/tests/test_stored_raw.py services/orchestrator/tests/test_contract.py -v
```

Повні логи: `.jane/m3fix-review1-ambiguity-after-1.txt`, `.jane/m3fix-review1-ambiguity-after-2.txt`.
Набір містить 4 storage-read випадки (same/distinct id × page size 1/100), попередні RAW/source/race
регресії, міграцію з наявних schema 3 і 4, обидва контрактні сценарії оркестратора. Компонент справжній;
PostgreSQL справжній; storage/runtime — контрактні сусіди; API-відповіді з omission валідовано за OpenAPI.
Новий API instance читає ту саму ознаку з БД. Обидва прогони завершились на одному власному PostgreSQL:

```text
======================= 10 passed in 101.30s (0:01:41) ========================
======================== 10 passed in 73.91s (0:01:13) ========================
```

0 skipped, 0 deselected. Після другого прогону контейнер видалено runner-ом у `finally`.

Адресні Ruff / strict mypy (`.jane/m3fix-review1-ambiguity-lint.txt`, `.jane/m3fix-review1-ambiguity-types.txt`):

```text
All checks passed!
21 files already formatted
Success: no issues found in 21 source files
```

Task-scoped ownership після обох виправлень (`.jane/m3fix-review1-final-ownership.txt`):

```text
Base 3c98542: 28 files; 0 outside the explicit cross-owner assignment
```

Друга finding змінює лише `services/orchestrator/**` та цей звіт (6 файлів від `c07d91a`).
До accepted залишаються review 2 лише виправлень та full CI на остаточному code SHA; ідентифікатор
CI передається координатору в журнал потоку B після push/dispatch. Старий `37850604947` не фінальний.
