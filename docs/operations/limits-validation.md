# Перевірка профілів лімітів

Профіль лімітів вважається перевіреним, коли вимірювання на реальному стеку показують, що сервіси дотримуються його значень: темпу й паралельності запитів до хоста, повторів, backpressure, обмежень пісочниці, ресурсів стеку й тривалості наскрізного сценарію. Вимірювання виконує `deploy/profiles/harness/limits_harness.py`; пороги прийнятності — `deploy/profiles/thresholds.json`. Профілі — [deploy/profiles/README.md](../../deploy/profiles/README.md).

## Зміст

- [Сценарії](#сценарії)
- [Запуск вимірювань](#запуск-вимірювань)
- [Результати й вердикт](#результати-й-вердикт)
- [Результати приймання](#результати-приймання)

## Сценарії

| Сценарій | Що вимірюється | Ліміти профілю |
|---|---|---|
| L1 | темп запитів до одного хоста, один збір | `rate.*` |
| L2 | той самий темп, два одночасні збори одного хоста | `rate.*` спільно для платформи |
| L3 | запити в польоті до одного хоста (повільні сторінки) | `concurrency.max_parallel_fetches_per_host` |
| L4 | `5xx` із подальшим успіхом, `429` + `Retry-After`, тайм-аут запиту | `retries.*`, `timeouts.request_timeout_ms` |
| L5 | пауза збору, доки споживач не підтвердить матеріали | `queue.max_unacked_materials` |
| L6 | холодний старт пісочниці, межа часу, межа пам'яті, паралельні пісочниці | `sandbox.*`, `concurrency.max_parallel_invocations` |
| L7 | пікова пам'ять стеку, OOM і перезапуски (`docker stats`, `docker inspect`) | ресурси хоста |
| L8 | приклад каталогу й перевірки цін за розкладом: тривалість і результати | наскрізний сценарій |

Запити L1–L5 ідуть на інструментований сайт `probe-site` (`harness/probe_site.py`, compose-профіль `limits-probe`): він записує прихід і завершення кожного запиту, тому вимірювання відбувається поза компонентом, що перевіряється. L6 використовує тестовий пакет `harness.sandbox-probe`.

Що саме перевіряється для профілю, показує команда `plan` (без Docker):

```powershell
uv run --all-packages python deploy/profiles/harness/limits_harness.py plan --profile ci
```

Уривок виводу (2026-10-11, ревізія `48389a3`):

```text
"L3": "12 pages answering after 2000 ms, in flight <= 2",
"L5": "60 pages, max_unacked 5, hold 8 s",
"L6": "5 cold starts p95 <= 0.5 x 30 s, sleep 35 s -> timeout, alloc 768 MB -> resource_exceeded, 4 parallel -> <= 2 sandboxes",
"L7": "docker stats every 5 s, total peak <= 10240 MiB, no OOM/restarts",
"L8": "catalog <= 180 s, price check <= 90 s, effects verified"
```

## Запуск вимірювань

Вимірювання потребує вільного Docker-хоста: `run` відмовляється працювати, якщо на хості є сторонні контейнери (`machine.max_foreign_containers` у порогах).

```powershell
uv run --all-packages python deploy/profiles/harness/limits_harness.py run --profile ci
```

| Параметр | Дія |
|---|---|
| `--profile` | `dev-laptop` (типово) або `ci`; для `single-node` порогів немає |
| `--project` | compose-проєкт, типово `jane-limits-<профіль>` |
| `--only L1,L3` | лише вказані сценарії |
| `--repeat N` | кількість повторів (типово з порогів: `dev-laptop` — 3, `ci` — 1); між повторами перезапускаються Web Collector, Handler Runtime і Orchestrator |
| `--keep` | не видаляти стек після вимірювань |
| `--no-up` | використати вже запущений стек (`stack.py up --probe`) |
| `--allow-busy` | вимірювати на зайнятому хості; результат позначається як непридатний для приймання |

Без `--keep` harness видаляє стек командою `stack.py down` (контейнери, томи, образи, пісочниці). Тривалість одного повтору для `ci` — близько 7 хвилин плюс 3–10 хвилин на запуск стеку (оцінка команди `plan`).

## Результати й вердикт

Результати записуються в `.jane/limits/<профіль>-<час UTC>/` (каталог поза Git):

| Файл | Зміст |
|---|---|
| `environment.json` | хост, версія Docker, Git SHA, дайджест профілю |
| `raw/*.jsonl`, `raw/*.json` | журнал запитів `probe-site`, відповіді сервісів, вибірки `docker stats` |
| `results.json` | кожна перевірка зі значенням, порогом і результатом |
| `summary.md` | таблиця результатів |

Кожна перевірка має результат `ok`, `warn` або `fail`; загальний вердикт — `pass`, `warn` (блокерів немає, є попередження) або `fail`. Облікові дані у файли не пишуться. Повторна оцінка збережених даних:

```powershell
uv run --all-packages python deploy/profiles/harness/limits_harness.py evaluate .jane/limits/<каталог прогону>
```

## Результати приймання

Вимірювання для приймання виконує job `limits` у CI (`.github/workflows/ci.yml`, лише ручний запуск `workflow_dispatch`) на чистому runner `ubuntu-24.04` з профілем `ci`; артефакт `limits-ci-<run>-<attempt>` містить каталог `.jane/limits/`.

| Прогін CI | Ревізія | Дата | Вердикт (з журналу job) |
|---|---|---|---|
| [37953732904](https://github.com/sql-monk/Jane/actions/runs/37953732904) | `9d9fb4c` | 2026-10-09 | `pass` |
| [36908333153](https://github.com/sql-monk/Jane/actions/runs/36908333153) | `c2b1d28` | 2026-10-01 | `warn` |

`9d9fb4c` — предок поточної ревізії `48389a3` (26 комітів). Вердикти взято з журналів job `limits` через `gh api` 2026-10-11. Локально на хості документування вимірювання не запускалися: на ньому працюють сторонні контейнери, тож результат був би непридатним для приймання.
