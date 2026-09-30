# Перевірка профілів лімітів

Стан на 2026-09-30: протокол і кросплатформний harness готові, **вимірювань ще немає** (фаза 2 — коли
машина вільна від інших Docker-стеків). Цільові середовища підтвердила людина: `dev-laptop` (Windows 11 +
Docker Desktop) і `ci` (GitHub Actions `ubuntu-latest`). `single-node` лишається кандидатом, не перевіреним
на реальному середовищі, і harness для нього порогів не має.

## Що вимірюється

Harness — [`deploy/profiles/harness/limits_harness.py`](../../deploy/profiles/harness/limits_harness.py)
(лише Python і Docker; Windows і Linux). Він піднімає ізольований стек
([`stack.py`](../../deploy/profiles/stack.py) з профілем) і службовий
[`probe_site.py`](../../deploy/profiles/harness/probe_site.py): сайт, що журналює початок і кінець кожного
запиту **на боці сервера**. Тож частоту, паралельність, тайм-аути й повтори колектора видно ззовні, а не з
його власних лічильників.

| ID | Що | Як | Блокери (профіль не приймається) | Попередження |
|---|---|---|---|---|
| L1 | темп запитів на хост, один збір | web-collector, N сторінок probe-site, ліміти — з `LIMITS_FILE` профілю | усі сторінки запитані; ≤ ⌈1/інтервал⌉+1 запитів у будь-якому вікні 1 с; середнє з 5 сусідніх проміжків ≥ інтервал − допуск; жоден проміжок < ½ інтервалу | окремий проміжок < інтервал − допуск; середній темп < `min_efficiency`·ліміт; ефективна частота ≠ профіль |
| L2 | те саме, **два збори одного хоста одночасно** | як L1, два `POST /v1/collections` | ті самі межі для сумарного потоку до хоста | — |
| L3 | паралельні запити до хоста | сторінки відповідають через `slow_ms`, частота знята запитом | запитів «у польоті» ≤ `max_parallel_fetches_per_host` | паралельність не використовується; ефективне значення ≠ профіль |
| L4 | повтори, `Retry-After`, тайм-аут | 503 N разів → 200; 429 + `Retry-After`; сторінка довша за `request_timeout_ms` | кількість спроб = `min(N+1, max_attempts)`; проміжки ≥ ½ номінального backoff; 429 чекає `Retry-After`; тайм-аут: `max_attempts` спроб, кожна не коротша за 0,95·`request_timeout_ms`, код `source_unavailable` | проміжки не довші за backoff + інтервал + 2 с; спроба завершується близько тайм-ауту |
| L5 | backpressure | 60 сторінок, `max_unacked_materials` = 5, споживач мовчить | запитано ≤ cap + `max_parallel_fetches`; `unacked` ≤ cap + паралельність − 1; `paused_by_backpressure`; після споживання — усі матеріали, `succeeded` | `unacked` > cap |
| L6 | пісочниця | handler-runtime, службовий пакет `harness.sandbox-probe` (inline), ліміти профілю в запиті, як від оркестратора | 5 холодних стартів без тайм-аутів, p95 ≤ частка `wall_time_ms`; сон > `wall_time_ms` → `timeout`; `memory_mb` + 256 МБ → `resource_exceeded`; одночасних пісочниць ≤ `max_parallel_invocations` | примусова зупинка пізніше ніж `wall_time` + 30 с; `max_parallel_invocations` сервісу ≠ профіль |
| L7 | ресурси стеку | `docker stats` контейнерів проєкту кожні N с, `docker inspect` | пік сумарної пам'яті ≤ порога; жодного OOM-kill і рестарту | — |
| L8 | наскрізно | [`examples/jane_examples.py`](../../examples/README.md) на тому самому стеку | `verify` прикладу `ok` | каталог і перевірка цін довші за поріг |

Пороги — [`deploy/profiles/thresholds.json`](../../deploy/profiles/thresholds.json) (обсяги сценаріїв,
допуски, бюджет пам'яті, тривалості, кількість повторів). Допуск для проміжків — `max(частка·інтервал,
абсолютний)`: планувальник подій Python на Windows має крок таймера ~15,6 мс, а колектор резервує час
старту, а не момент відправлення. Тому блокер — середнє з 5 проміжків і вікно 1 с, а окремий короткий
проміжок — попередження, якщо він не менший за половину інтервалу.

| Поріг | `dev-laptop` | `ci` |
|---|---|---|
| повторів усього набору (між повторами — рестарт web-collector, handler-runtime, orchestrator) | 3 | 1 |
| сторінок L1 / L2 | 30 / 2×15 | 200 / 2×100 |
| допуск проміжку (частка / абсолютний) | 0,1 / 20 мс | 0,2 / 5 мс |
| p95 холодного старту пісочниці | ≤ 0,5 · `wall_time_ms` (профіль: 60 с → ≤ 30 с) | ≤ 0,5 · 30 с |
| пік пам'яті стеку | ≤ 6 ГіБ (з 16 ГБ машини) | ≤ 10 ГіБ (з 16 ГБ runner) |
| каталог / перевірка цін | ≤ 300 с / ≤ 120 с | ≤ 180 с / ≤ 90 с |
| сторонніх контейнерів на хості | 0 | 0 |

Профіль приймається для середовища, лише якщо всі блокери пройшли в кожному повторі на чистій ревізії
(`git_dirty: false`) і на вільному хості. Попередження записуються в звіт з поясненням.

## Запуск

```text
uv run --all-packages python deploy/profiles/harness/limits_harness.py plan --profile dev-laptop
uv run --all-packages python deploy/profiles/harness/limits_harness.py run --profile dev-laptop
uv run --all-packages python deploy/profiles/harness/limits_harness.py evaluate .jane/limits/<каталог прогону>
```

- `plan` — що саме буде виміряно з поточними значеннями профілю й оцінка тривалості (без Docker).
- `run` — `stack.py up` (проєкт `jane-limits-<profile>`, з `probe-site`), сценарії L1–L8, `--repeat` разів,
  `stack.py down`. Якщо на хості працюють сторонні контейнери, `run` **відмовляється** (код 2);
  `--allow-busy` дозволяє лише димовий прогін, позначений у підсумку як непридатний для приймання.
  `--only L1,L3`, `--keep` (не прибирати стек), `--no-up` (стек уже піднято з `--probe`).
- `evaluate` — повторно друкує вердикти збереженого прогону.

Орієнтовна тривалість (оцінка `plan`, без вимірювань): `dev-laptop` ≈ 8 хв на повтор × 3 + старт і
прибирання стеку 3–10 хв (перше збирання образів довше) ≈ **30–40 хв**; `ci` ≈ 7 хв + старт ≈ **10–15 хв**.
Найдовші частини — L4 (3 × `request_timeout_ms` = 30 с) і L6 (сон довший за `wall_time_ms`).

## Сирі метрики й журнал доказів

Кожен прогін пише `.jane/limits/<profile>-<UTC-час>/` (каталог у `.gitignore`, секретів немає):

| Файл | Вміст |
|---|---|
| `environment.json` | час, Git SHA і `git_dirty`, ОС і Python, Docker (версія, NCPU, MemTotal, ядро), профіль і його sha256, sha256 порогів, кількість сторонніх контейнерів |
| `raw/r<повтор>-L*-probe.jsonl` | журнал probe-site: шлях, початок і кінець запиту (epoch, висока роздільність), статус |
| `raw/r<повтор>-L*-collection*.json`, `raw/r1-L4c-errors.json` | стан збору колектора (`effective_limits`, `stats`, `paused_by_backpressure`), помилки URL |
| `raw/r<повтор>-L6-runtime.jsonl` | тривалості й результати викликів пісочниці, вибірки кількості пісочниць |
| `raw/resources.jsonl` | `docker stats` (пам'ять, CPU) усіх контейнерів проєкту |
| `raw/r1-L8-examples.json` | запуски й перевірка прикладу |
| `results.json`, `summary.md` | метрики, кожна перевірка (значення, межа, результат, серйозність), вердикти |

Для звіту WP-14 фази 2 зберігайте весь каталог прогону (архівом поза Git або артефактом CI), а в
`docs/delivery/WP-14.md` — `summary.md`, рішення «прийнято/відхилено» по кожному профілю й обґрунтування
змін чисел. Поки такого журналу немає, критерій 13 **не підтверджено** в частині «перевірені профілі».

## Як профіль `ci` застосовується в CI

Зараз `.github/workflows/ci.yml` (власник WP-01) профілів не використовує: job `e2e` бере накладку WP-13 з
типовими лімітами сервісів, `stack` — `just up` без застосунків. Щоб `ci` став перевіреним профілем CI,
потрібен окремий job (запит до WP-01 у звіті WP-14), наприклад:

```yaml
  limits:
    needs: contract
    if: github.event_name == 'workflow_dispatch' || github.event_name == 'schedule'
    runs-on: ubuntu-24.04
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          version: ${{ env.UV_VERSION }}
          enable-cache: true
      - run: uv sync --all-packages --locked
      - run: uv run --all-packages python deploy/profiles/harness/limits_harness.py run --profile ci
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: limits-ci-${{ github.run_id }}
          path: .jane/limits/
```

На GitHub runner сторонніх контейнерів немає, тож умова вільного хоста виконується сама. Для нічного прогону
в `on:` треба додати `schedule` (зараз лише push, pull_request, workflow_dispatch). Застосування профілю поза harness — через
`stack.py up --profile ci`: оркестратор і колектори читають `deploy/profiles/ci.json`, решта сервісів
отримує значення в запитах оркестратора. Якщо `tests/e2e` мають працювати під профілем `ci`, накладка
WP-13 має монтувати `deploy/profiles/ci.json` так само (запит до WP-13).

## Що вже видно без вимірювань

- **Профіль як `LIMITS_FILE`.** storage, handler-runtime, registry, llm, assistant не стартують із повним
  `PlatformLimits` (перевірено тестом `test_services_that_reject_the_whole_profile_as_limits_file`, xfail).
  Застосовувати профіль до них напряму не можна, доки власники не почнуть ігнорувати групи, яких не
  моделюють (як колектори). L6 тому передає ліміти пісочниці в запиті, як оркестратор, і попереджає, якщо
  `max_parallel_invocations` сервісу відрізняється від профілю.
- **Пісочниця на Docker Desktop.** WP-13 зафіксував 30,7 с старту контейнера при 1 с роботи екстрактора; у
  `dev-laptop` `sandbox.wall_time_ms` піднято з 30 000 до 60 000 мс (`invocation_timeout_ms` — 90 000),
  як у e2e WP-13. Це рішення за спостереженням, його перевіряє L6.
- **Ліміт частоти на рівні збору.** У web-collector `HostLimiter` створюється для кожного збору окремо, тож
  два одночасні збори одного хоста (наприклад, каталог і перевірка цін) можуть разом перевищити
  `requests_per_second_per_host`. Самоперевірка harness на локальному процесі один раз показала 20 запитів/с
  при ліміті 10. Крім того, окремі запити одного збору інколи приходять парою з проміжком кілька мілісекунд
  (резервується час, а не момент відправлення). Обидва ефекти — вимірювання L1/L2 фази 2, не висновок.
