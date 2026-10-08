# WP-14d. Точки входу документації й експлуатація (фінальне рев'ю M3)

**Гілка:** `wp/14d-docs-entrypoints` · **База:** `3c98542` (= `main` `d37c522` + запис у `status.md`) ·
**Доручення:** наскрізне, координатор за фінальним рев'ю M3 (без `.jane-wp`) · **Стан:** review

## Результат

Усі 9 знахідок фінального рев'ю виправлено в дозволених шляхах; нові команди резервування й відновлення один раз
відрепетирувано на малому стеку (`postgres` + `orchestrator`), обидва способи — `just up` і `stack.py`.

| Знахідка | Файл | Суть зміни |
|---|---|---|
| 1 | [`README.md`](../../../README.md) | прибрано «проєктування, реалізацію не розпочато»; розділ «Швидкий старт» із посиланнями на `DEVELOPMENT.md`, `examples/README.md`, `docs/operations/README.md` (+ резервування), `deploy/profiles/README.md`, `web/admin/README.md`, `docs/acceptance/matrix.md`; посилання на `contracts/README.md` |
| 2 | [`DEVELOPMENT.md`](../../../DEVELOPMENT.md) | посилання на `examples/` і `docs/operations/`; замість «`web` (no-op до WP-12)» і «застосунок створює WP-12» — фактичні job CI (`web`, `isolation`, `stack`, `adapters`, `e2e`, `limits`) і посилання на `web/admin/README.md`; `just web` запускає й `build` |
| 3 | [`infra/compose.yaml`](../../../infra/compose.yaml), [`deploy/profiles/compose.stack.yaml`](../../../deploy/profiles/compose.stack.yaml) | оркестратор отримує `JANE_ORCHESTRATOR_SCHEDULER_ENABLED: ${…:-true}` і `JANE_ORCHESTRATOR_RUN_WORKERS: ${…:-true}` із середовища `just up` / `stack.py up`; опис вимкнення — `backup-restore.md`, `docs/operations/README.md`, `infra/README.md`, `deploy/profiles/README.md` (таблиця змінних стеку) |
| 4 | [`docs/operations/backup-restore.md`](../../operations/backup-restore.md) | конкретні команди dev-стеку через контейнер (`docker compose -p <P> exec -T postgres pg_dump … --format=custom`, `pg_restore --list`, `docker compose -p <P> cp`); звідки адреса й облікові дані (`just env --format json` → `db-<сервіс>`; для `stack.py` — `env.JANE_PG_<СЕРВІС>_PASSWORD` у `.jane/stack-<P>.json` + `docker compose -p <P> port postgres 5432`); порядок відновлення в новий проєкт (`just up --project <NEW> postgres` → `pg_restore` → застосунок без планувальника й воркерів → увімкнення); зауваження про Git Bash (`MSYS_NO_PATHCONV=1`) і версію клієнта |
| 5 | [`docs/operations/README.md`](../../operations/README.md), [`deploy/profiles/README.md`](../../../deploy/profiles/README.md), [`docs/operations/limits-validation.md`](../../operations/limits-validation.md), [`docs/delivery/WP-14.md`](../WP-14.md) | прибрано «стан після WP-01a», «перевірені — dev-laptop», «числа ще не виміряні» і старий `warn` 36908333153 як поточний стан; `ci` — прийнято наживо (36921026070 `pass`, 36952287098 `warn`, 37811082079 на `main` `pass`), `dev-laptop` і `single-node` — «не перевірено на реальному середовищі»; у WP-14.md — розділ «Рішення людини 2026-10-08 і стан критерію 13»; таблиця «Результати» limits-validation доповнена прогонами після 36908333153 |
| 6 | `docs/operations/README.md` | `docker compose ... up -d --build <сервіс>` → `just up --project <P> <сервіс>` / та сама команда `stack.py up …` / повна команда `docker compose -f infra/compose.yaml -p <P> up -d --build --wait <сервіс>` |
| 7 | [`infra/README.md`](../../../infra/README.md) | збірка адмінки — `corepack pnpm --dir web/admin install --frozen-lockfile` + `build`; `just web` — повна перевірка (install, lint, typecheck, test, build); порт (зокрема `proxy`) змінюється при перестворенні контейнера, `just up` друкує новий |
| 8 | [`examples/jane_examples.py`](../../../examples/jane_examples.py), [`examples/tests/test_examples.py`](../../../examples/tests/test_examples.py), [`examples/README.md`](../../../examples/README.md) | час журналу драйвера — UTC з `Z` (`[17:31:22Z] …`) + тест; у README: 409 для source/task у кроці `telegram` після `demo` очікувані, `unknown_materials: 7` — сторінки категорій, `.jane/examples-<проєкт>.json` лишається після `down` |
| 9 | [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) | лише коментарі: `isolation` (тести є — `services/handler-runtime/tests/test_isolation.py`) і `web` (не no-op) |

`docs/acceptance/**`, `AGENTS.md` і код сервісів не змінено. Розділ автентифікації `docs/operations/README.md` і
рядки токенів/allowlist у compose-файлах не чіпав (паралельні доручення); мої правки compose — лише два рядки
оркестратора в кожному файлі.

## Репетиція резервування й відновлення (2026-10-08, Windows 11 + Docker Desktop, Compose v5.5.1)

Проєкти `jane-14d` (джерело), `jane-14d-restore` (відновлення через `just up`), `jane-14d-sp` (відновлення
через `stack.py`); `puluj-g-*` і чужі стеки не чіпались. Дані створено через API оркестратора:
`PUT /v1/connections/raw-files` і `/results-pg` (200), `POST /v1/sources` з `examples/documents/source.testsite-shop.json`
(201), `PUT /v1/limits/platform` з `If-Match: "v1"` (`profile: wp14d-backup-rehearsal`,
`crawl.max_pages_per_run: 777`, відповідь 200, `ETag "v2"`). Знімок — `.jane/wp14d-snapshot.py` (health, джерела,
підключення, ETag і значення лімітів платформи через публічний API).

```text
$ just up --project jane-14d postgres orchestrator
...
project: jane-14d   (stack file: .jane/stack-jane-14d.json)
  postgres   127.0.0.1:56516
  orchestrator http://127.0.0.1:56529
  db-orchestrator postgresql://127.0.0.1:56516/jane_orchestrator
  ...
exit 0
$ docker exec jane-14d-orchestrator-1 printenv | grep -E "SCHEDULER|RUN_WORKERS"     # типово
JANE_ORCHESTRATOR_RUN_WORKERS=true
JANE_ORCHESTRATOR_SCHEDULER_ENABLED=true

$ python .jane/wp14d-snapshot.py http://127.0.0.1:56529          # до копії
{"connections": ["raw-files", "results-pg"], "crawl.max_pages_per_run": 777, "health": "ok", "limits_etag": "\"v2\"", "limits_profile": "wp14d-backup-rehearsal", "sources": ["testsite-shop"]}

# 1. Вимкнути планувальник і воркери
$ JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false JANE_ORCHESTRATOR_RUN_WORKERS=false just up --project jane-14d orchestrator
  orchestrator http://127.0.0.1:52304
exit 0
JANE_ORCHESTRATOR_RUN_WORKERS=false
JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false
# рядок "orchestrator started": limits.engine.workers = 2, фактично запущено "workers": 0
"workers": 2
"workers": 0

# 2. Копія (PowerShell)
$ docker compose -p jane-14d exec -T postgres pg_dump -U jane_orchestrator -d jane_orchestrator --format=custom --file=/tmp/jane_orchestrator.dump
exit 0
$ docker compose -p jane-14d exec -T postgres pg_restore --list /tmp/jane_orchestrator.dump   # перші рядки й кількість TABLE DATA
;
; Archive created at 2026-10-08 17:29:52 UTC
;     dbname: jane_orchestrator
;     TOC Entries: 86
;     Compression: gzip
;     Dump Version: 1.16-0
;     Format: CUSTOM
...
;     Dumped from database version: 18.6 (Debian 18.6-1.pgdg13+2)
;     Dumped by pg_dump version: 18.6 (Debian 18.6-1.pgdg13+2)
TABLE DATA entries: 14
$ docker compose -p jane-14d cp postgres:/tmp/jane_orchestrator.dump .jane/backup-jane-14d/jane_orchestrator.dump
 jane-14d-postgres-1 Copied jane-14d-postgres-1:/tmp/jane_orchestrator.dump to .jane/backup-jane-14d/jane_orchestrator.dump
exit 0
Hash : 23F3EE29AC6BD983451A221BCC28DC7795391361CF5A313975885308510EA081      (34524 байти)

# 3. Новий проєкт: спершу лише PostgreSQL
$ just up --project jane-14d-restore postgres
$ docker compose -f …\infra\compose.yaml -p jane-14d-restore up -d --wait --wait-timeout 600 --build postgres
$ docker compose -f …\infra\compose.yaml -p jane-14d-restore run --rm --no-deps pg-provision
CREATE ROLE (×6) / ALTER ROLE (×6) / CREATE DATABASE (×6) / ALTER DATABASE (×6) / REVOKE (×9)
project: jane-14d-restore   (stack file: .jane/stack-jane-14d-restore.json)
  postgres   127.0.0.1:64214
exit 0
$ docker compose -p jane-14d-restore cp .jane/backup-jane-14d/jane_orchestrator.dump postgres:/tmp/jane_orchestrator.dump
exit 0
$ docker compose -p jane-14d-restore exec -T postgres pg_restore -U jane_orchestrator -d jane_orchestrator --exit-on-error --no-owner /tmp/jane_orchestrator.dump
exit 0
$ docker compose -p jane-14d-restore exec -T postgres psql -U jane_orchestrator -d jane_orchestrator -Atc "select count(*) from sources" -c "select count(*) from connections"
1
2

# 4. Застосунок після відновлення, без планувальника й воркерів
$ $env:JANE_ORCHESTRATOR_SCHEDULER_ENABLED="false"; $env:JANE_ORCHESTRATOR_RUN_WORKERS="false"; just up --project jane-14d-restore orchestrator
  orchestrator http://127.0.0.1:52995
exit 0
false
false
$ python .jane/wp14d-snapshot.py http://127.0.0.1:52995
{"connections": ["raw-files", "results-pg"], "crawl.max_pages_per_run": 777, "health": "ok", "limits_etag": "\"v2\"", "limits_profile": "wp14d-backup-rehearsal", "sources": ["testsite-shop"]}
"workers": 0}            # журнал старту; рядків рівня error немає (4 збіги "error" — це логер uvicorn.error, level info)

# 5. Увімкнення: та сама команда без змінних
$ just up --project jane-14d-restore orchestrator
  orchestrator http://127.0.0.1:50323
exit 0
true
true
"workers": 2}
$ python .jane/wp14d-snapshot.py http://127.0.0.1:50323
{"connections": ["raw-files", "results-pg"], "crawl.max_pages_per_run": 777, "health": "ok", "limits_etag": "\"v2\"", "limits_profile": "wp14d-backup-rehearsal", "sources": ["testsite-shop"]}

# 6. Той самий архів через stack.py (накладка профілю; паролі — з файлу стеку just up)
$ just up --project jane-14d-sp postgres
  postgres   127.0.0.1:56892
exit 0
$ docker compose -p jane-14d-sp cp .jane/backup-jane-14d/jane_orchestrator.dump postgres:/tmp/jane_orchestrator.dump
exit 0
$ docker compose -p jane-14d-sp exec -T postgres pg_restore -U jane_orchestrator -d jane_orchestrator --exit-on-error --no-owner /tmp/jane_orchestrator.dump
exit 0
$ docker compose -p jane-14d-sp exec -T postgres rm /tmp/jane_orchestrator.dump
rm exit 0
$ $env:JANE_ORCHESTRATOR_SCHEDULER_ENABLED="false"; $env:JANE_ORCHESTRATOR_RUN_WORKERS="false"
$ uv run --all-packages python deploy/profiles/stack.py up --project jane-14d-sp --profile ci --services orchestrator
$ docker compose -f …\infra\compose.yaml -f …\deploy\profiles\compose.stack.yaml -p jane-14d-sp up -d --build --wait --wait-timeout 900 orchestrator
project: jane-14d-sp   profile: ci   stack file: C:/repos/Jane/.claude/worktrees/wp14d/.jane/stack-jane-14d-sp.json
  orchestrator       http://127.0.0.1:61546
exit 0
false
false
/cfg/limits/platform.json
"workers": 0}
$ python .jane/wp14d-snapshot.py http://127.0.0.1:61546
{"connections": ["raw-files", "results-pg"], "crawl.max_pages_per_run": 777, "health": "ok", "limits_etag": "\"v2\"", "limits_profile": "wp14d-backup-rehearsal", "sources": ["testsite-shop"]}
# profile лишився wp14d-backup-rehearsal: LIMITS_FILE (ci) не перезаписав відновлений документ лімітів

# 7. Прибирання
$ uv run --all-packages python deploy/profiles/stack.py down --project jane-14d-sp
{
  "project": "jane-14d-sp",
  "leftovers": {}
}
exit 0
$ just down --project jane-14d -v
 Volume jane-14d_postgres-data Removed
 Network jane-14d_default Removed
exit 0
$ just down --project jane-14d-restore -v
 Image jane-14d-restore-orchestrator:latest Removed
 Network jane-14d-restore_default Removed
exit 0
$ docker ps -a / docker volume ls / docker network ls / docker images  (фільтр jane-14d)
(порожньо)
```

Спостереження, що ввійшли в документацію:

- у Git Bash `docker compose exec … --file=/tmp/x.dump` перетворює `/tmp/...` на шлях Windows
  (`could not open output file "C:/Users/…/Temp/jane_orchestrator.dump"`) — у PowerShell і Linux такого немає;
  у документі — `MSYS_NO_PATHCONV=1`;
- `docker compose -p <P> exec|cp|port` працює без `-f` (Compose v5.5.1), тож командам не потрібні змінні паролів
  compose-файлу;
- `pg_dump` / `pg_restore` у контейнері від ролі сервісу пароля не просять (локальний сокет dev-образу);
- `stack.py up` бере облікові дані з файлу стеку `just up` (ті самі ключі), тому відновлення під `stack.py`
  працює без ручного перенесення паролів.

Не репетирувалось: архіви registry (MinIO/S3), томи storage і колекторів (SQLite), SQL Server, MongoDB, повний
ланцюжок із даними запусків, час відновлення на робочих обсягах — у `backup-restore.md` це сказано прямо.

## Команди перевірки та їхній вивід

```text
$ uv run --all-packages ruff check examples/jane_examples.py examples/tests/test_examples.py
All checks passed!
$ uv run --all-packages ruff format --check examples/jane_examples.py examples/tests/test_examples.py
2 files already formatted
$ uv run --all-packages mypy examples/jane_examples.py
Success: no issues found in 1 source file

# новий тест до виправлення (рядок драйвера тимчасово повернуто):
$ uv run --all-packages pytest examples -q -k progress_log
examples\tests\test_examples.py:203: AssertionError
FAILED examples/tests/test_examples.py::test_progress_log_time_names_its_zone
1 failed, 25 deselected in 1.60s
# після виправлення:
$ uv run --all-packages pytest examples -q
..........................                                               [100%]
26 passed in 7.32s

$ python .jane/wp14d_compose_config.py   # docker compose config --format json, фіктивні паролі, COMPOSE_PROFILES=*
infra/compose.yaml: default  -> {'JANE_ORCHESTRATOR_SCHEDULER_ENABLED': 'true', 'JANE_ORCHESTRATOR_RUN_WORKERS': 'true'}
infra/compose.yaml: env=false -> {'JANE_ORCHESTRATOR_SCHEDULER_ENABLED': 'false', 'JANE_ORCHESTRATOR_RUN_WORKERS': 'false'}
infra + compose.stack.yaml: default  -> {'JANE_ORCHESTRATOR_SCHEDULER_ENABLED': 'true', 'JANE_ORCHESTRATOR_RUN_WORKERS': 'true'}
infra + compose.stack.yaml: env=false -> {'JANE_ORCHESTRATOR_SCHEDULER_ENABLED': 'false', 'JANE_ORCHESTRATOR_RUN_WORKERS': 'false'}
exit 0

$ python .jane/wp14d_links.py   # відносні шляхи й #якорі (slug GitHub) у змінених .md
11 Markdown files, 122 local links, 0 problem(s)

$ for r in 36921026070 36952287098 37811082079; do gh run view … ; gh run view $r --log --job <limits> | grep -o "verdict: [a-z]*"; done
36921026070  a97a5f3 codex/jane-integration workflow_dispatch success  limits: verdict: pass
36952287098  fc494f1 codex/jane-integration workflow_dispatch success  limits: verdict: warn
37811082079  d37c522 main workflow_dispatch success  limits: verdict: pass

$ uv run --all-packages pytest deploy/profiles -q
FAILED deploy/profiles/tests/test_profiles_harness.py::test_harness_collector_scenarios_run_against_a_local_collector
1 failed, 56 passed in 13.59s
# KeyError: 'max_sub_half_gaps' (deploy/profiles/harness/metrics.py:163). Те саме без змін WP-14d (git stash):
1 failed, 56 deselected in 9.58s
```

Останній збій — **не від цих змін** і поза дозволеними шляхами: `SELF_TEST_THRESHOLDS["rate"]` у
`deploy/profiles/tests/test_profiles_harness.py` не має ключа `max_sub_half_gaps`, який WP-14c (`300fdba`) зробив
обов'язковим у `metrics.rate_checks`. `just check` і CI каталог `deploy/profiles` не запускають, тому збій не
помічено. Запит нижче.

## CI

CI [37819395884](https://github.com/sql-monk/Jane/actions/runs/37819395884) (`workflow_dispatch`, повний
набір job, бо змінено compose) на `f21947f`: **12/12 job успішні**. Push-прогін 37819391925 того самого SHA
скасовано правилом `concurrency` (його замінив повний прогін).

```text
$ gh run view 37819395884 --json status,conclusion,headSha,jobs
completed success f21947f
  lint: success   unit: success   web: success   isolation: success   contract: success
  stack: success  adapters (minio|s3|mongodb|sqlserver): success   e2e: success   limits: success
# з журналів job:
limits: verdict: pass   results: .jane/limits/ci-20261008T175521Z
e2e:    62 passed in 1224.11s (0:20:24)
stack:  232 passed, 889 deselected in 214.18s (0:03:34)
```

`limits` і `e2e` піднімали стек профілю й e2e-стек уже зі зміненими compose-файлами — змінні оркестратора з
типовим `true` поведінки не змінили. Останній коміт (лише цей розділ звіту) запушено з `[skip ci]`.

## Відомі обмеження

- Репетиція — лише PostgreSQL оркестратора на малому стеку; решта сховищ не репетирувалась (див. вище).
- `docs/acceptance/matrix.md` (рядок 13) ще каже «профілі WP-14 поки кандидати без вимірювань» — поза
  дозволеними шляхами.

## Запити до інших власників

| Кому | Що потрібно | Навіщо |
|---|---|---|
| Координатор / WP-13 | узгодити рядок 13 [матриці](../../acceptance/matrix.md) з розділом [«Рішення людини 2026-10-08 і стан критерію 13»](../WP-14.md#рішення-людини-2026-10-08-і-стан-критерію-13) | матриця суперечить рішенню й документації профілів |
| Власник WP-14 (`deploy/profiles/tests`) | додати `"max_sub_half_gaps"` у `SELF_TEST_THRESHOLDS["rate"]` (`test_profiles_harness.py:581`); розглянути запуск `pytest deploy/profiles` у CI | самотест harness падає з `KeyError` від `300fdba` |
