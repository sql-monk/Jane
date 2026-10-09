# Фінальне рев'ю дельти M3 — потік C

Дата: 2026-10-09. Доручення: [HANDOFF-2026-10-09-stream-c.md](../HANDOFF-2026-10-09-stream-c.md).
Рецензент потоку C не був автором переглянутих інкрементів. Один прохід, без додаткових рецензентів
і повторення повних тестових наборів. База першого рев'ю — `main` `d37c522`;
переглянута інтеграційна ревізія — `041e20d` (початковий зріз `76a03f7` доповнено змінами інших потоків).

**Вердикт C-1: нових блокерів M3 у переглянутій дельті не знайдено.** Одну документальну неточність
виправлено; залишаються неблокувальне зауваження й відомі обмеження нижче. Це не фінальне приймання M3:
Приймання B2 виконав потік A; фінальний CI, заповнення фінальної ревізії матриці та злиття в `main`
належать потоку A/людині.

## Інкременти й вердикти

| Інкремент / злиття | Вердикт | Що перевірено в коді та документах |
|---|---|---|
| WP-13r — `08b4110` | підтверджено, без нового блокера | `test_r04_active_replays.py`: Telegram у стані `running` з незавершеними каналами; runtime sync/async зі спостереженням sandbox; storage і LLM invocations із заблокованим завантаженням; registry з paused MinIO; assistant unknown-materials; orchestrator run/reprocessing під час активної екстракції. Повтор перевіряє 409 або той самий 202/job, інше тіло — 422; фінальні assertions перевіряють матеріали, RAW, invocation, usage, версії та запуски один раз. |
| WP-13t — `03a31fa` | A-2 закрито | `tests/e2e/conftest.py:150`: extractor публікується й погоджується у справжньому registry; `compose.e2e.yaml` спрямовує runtime/LLM на registry. `jane_e2e/registry.py` звіряє digest і архів; package-host більше не обслуговує архіви. Stand-in Material позначено **Т**, gate blob/Telegram/fake LLM — **З**. Формулювання ін'єкції та kill колектора звужено до фактичних доказів. `JANE_E2E_REQUIRED=1` у CI, hook відхиляє skip, `scripts/dev.py:170` повертає exit 5 як помилку обов'язкового e2e. |
| WP-14d — `0507ef9` | частина B / A-3 закриті з уточненням C-W1 | README веде до DEVELOPMENT, examples і operations; застаріле твердження про початок реалізації прибрано. Scheduler/workers передаються обома compose-конфігураціями; оновлення враховує стек-файл. Backup/restore описує контейнерні PostgreSQL-клієнти, новий проєкт і старт без застосунків. Профіль `ci` відокремлено від неперевірених кандидатів; рішення щодо dev-laptop записане. Offline examples/profiles включено в unit; `max_sub_half_gaps` покритий assertion. Неповні Docker-команди виправлено цим потоком. |
| WP-13s — `86cdece` | підтверджено, без нового блокера | FakeProvider утримує відповідь у межах налаштованого `fake.max_delay_ms`; e2e спостерігає hold-запис саме свого connection_id та running job. LLM completions sync/async, assistant onboarding/improvement перевіряють ключ, job, usage/costs і версії. `services/assistant/src/jane_assistant/unknown.py:66` обробляє недоступність необов'язкового оркестратора після оплаченої LLM-відповіді; автономний результат не втрачається. |
| B1 / WP-01h — `cdf261a` | B1 і SSRF runtime закриті в погодженій моделі довіри | `libs/jane-kit/src/jane_kit/content.py:188`: дозволені корені; `:211`: allowlist хоста/порту; `:231`: без redirects/proxy, bounded streaming/timeout; перевіряються розмір і SHA-256. LLM inputs/package archive, assistant material і runtime читають через ContentReader. `infra/compose.yaml:168` і `:228`: лише RAW objects, том для runtime/LLM `:ro`. Відоме обмеження проміжних каталогів — C-N1, без окремого repro за рішенням людини. |
| M3 should-fix — `69ab303` | заявлені виправлення збережені | SDK використовує registry-compatible `ZIP_STORED`, фіксовані атрибути/час/порядок; golden digest є в тесті. Keep-alive expiry/retries — у конфігурації; повтор transport failure лише для ідемпотентного методу або ключа, без повтору timeout. Egress перевіряє DNS-адреси й підключається до перевіреної адреси, включно з metadata та IPv4-in-IPv6. LLM/Telegram секрети читаються через закріплені компоненти шляху; невалідний api_base/порт дає validation error. `_feed_stored` фільтрує source_id у listing та detail; durable stored_object_id/ambiguity міграції 4/5 дають omission для неоднозначного RAW, без читання storage-таблиць. |
| WP-12d — `bf69429` | S-M2-10 розширено, без нового блокера | UI не перезаписує кінцевий статус швидкого improvement job; trace key містить observation/run; sample RAW знаходиться через storage API. Нові real-сценарії створюють дані публічними API, перевіряють problems, unknown, failed trace, витрати, повторну обробку та точний source-filter. Знято `test.fail` WP-09 зі збереженням `toContain`/`toEqual`. Звіт чесно залишає 24/26 повністю, один частково, один навмисно mock; часткове onboarding не оголошено повним. Зауваження fallback — C-W2. |
| B-5/B-6 — `8726647`, уточнення `a706c54` | узгоджено, фінальний gate лишається відкритим | Оновлена матриця/сценарії відділяють інтегровані докази від майбутньої фінальної ревізії, уточнюють реальні/замінні компоненти й часткове UI-покриття. `M3/open-requests.md` зводить власників, стан і блокери/після-M3 запити. Потік C ці файли не редагував. |
| WP-06c — `041e20d` (додано під час проходу) | без нового блокера; класифікація має явне evidence | Runtime класифікує timeout раніше за OOM; Docker враховує OOMKilled або SIGKILL за наявності memory limit, відділяє власний cancel через killed_by_runtime. Subprocess не заявляє memory enforcement. `test_classification.py` перевіряє ці розрізнення й пріоритет причин, без послаблення isolation-test. `evidence: sigkill` є евристикою, а `oom_killed` — підтвердженням рушія; це слід зберігати при інтерпретації діагностики. |

## Знахідки й обмеження

Власники — за `.claude/wp-paths.json`; рівні: **блокер M3**, **варто**, **примітка**.

| ID / рівень | Файл:рядок, доказ | Власник / рішення |
|---|---|---|
| C-W1 — **варто, виправлено** | `docs/operations/backup-restore.md:48` на `041e20d` та інші команди `docker compose -p`: конфігурація лежить у `infra/compose.yaml`, стекові env не переходять у батьківський shell. Read-only `docker compose -p jane-m3c-doc-review config --services` з кореня повернув exit 1, `no configuration file provided: not found`. | WP-14. Уточнено отримання container ID через labels саме свого проєкту; приклади використовують `docker exec`/`docker cp`/`docker port` і окремий ID нового PostgreSQL. Коміт `dee854d`. Репетиція backup не повторювалась. |
| C-W2 — **варто** | `web/admin/src/pages/ProblemsPage.tsx:356`: fallback бере перший RAW, а без `sample.observation_id` приймає будь-яке спостереження того самого material_id. За кількох RAW того самого observation також обирається перший. `contracts/openapi/orchestrator.v1.yaml:1691` не вимагає observation_id у sample; backend `stored_raw.py` навмисно опускає неоднозначний id. Це статична знахідка для неповних/неоднозначних samples, не дефект пройденого real-сценарію з одним RAW. | WP-12. Після M3 варто узгодити fallback з omission бекенду: вимагати точне спостереження й однозначний RAW або показувати недоступність. Код потік C не змінював, окремого прогону не додавав. |
| C-N1 — **примітка, відоме обмеження** | `libs/jane-kit/src/jane_kit/content.py:280`; [01h-content-policy.md](01h-content-policy.md), рядки 222–224: O_NOFOLLOW/inode захищають останній компонент; проміжні каталоги не закріплені. Атака потребує можливості підміни каталогу в дозволеному корені; runtime/LLM мають RAW mount лише для читання. | WP-01. За прямим уточненням людини окремий repro не потрібен. Не класифікується новим блокером M3. |
| C-N2 — **примітка, межа довіри B1** | [01h-content-policy.md](01h-content-policy.md), рядки 225–227: дозволений objects-root спільний для RAW різних джерел; політика ContentRef сама не розмежовує джерела. | WP-01/B2, потік A. Зберігається модель довірених автентифікованих викликачів; B2 перевіряється окремо. |
| C-N3 — **примітка, режими Playwright** | `web/admin/e2e/hybrid-m2-problems.spec.ts:35`, `hybrid-m2-cycle.spec.ts:30,323`: real-тести skip за відсутності real stack, mock-job навмисно їх не виконує. Це не доказ виконання real-набору в `web-mock-e2e`; receipts реального прогону наведені у WP-12/stream-b. | WP-12/01. Не знайдено нових `test.fail` або безумовних skip, що приховують переглянуті real-сценарії. Фінальний real gate належить A. |

## Регресії, автономність і злиття

- Переглянута продукційна дельта не читає чужих таблиць. Orchestrator використовує storage API,
  а stored RAW provenance зберігає у власній БД. Автономні виконавці не набули обов'язкової залежності
  від оркестратора; виправлення unknown-materials цю незалежність посилює.
- Нові продукційні timeout/size/delay/keep-alive параметри налаштовуються через Settings/ServiceLimits.
  Числа фікстур/gate задають тестовий сценарій; сервісні обмеження не замінені ними.
- Переглянуті нові R-04 assertions перевіряють роботу до й після повтору та кінцеві ефекти;
  компонент, який приймають, не замокано. У нових R-04 сценаріях немає xfail/skip.
  Обов'язковий e2e hook не відхиляє `wasxfail`; нових xfail у переглянутій дельті не знайдено.
- Конфлікт `services/llm/README.md` у `cdf261a` не втратив WP-13s:
  рядки 67–68 містять обидва test_fake_provider/test_content_policy, таблиця лімітів — fake.max_delay_ms
  разом із ContentRef-політикою. Конфлікт CI у `bf69429` зберіг і `web-mock-e2e` (`ci.yml:90`),
  і `JANE_E2E_REQUIRED: "1"` (`:205`).
- Посилання на branch CI у звітах — попередні докази авторів/рецензентів, не нові прогони C.
  `37853233033` у stream-b правильно позначений як cancelled загалом із success окремих необхідних job;
  він не оголошений повним фінальним CI. Фінального CI потік C не запускав.

## Команди цього проходу

Читання: `git fetch origin`, `git log --first-parent d37c522..origin/codex/jane-integration`,
`git diff <merge>^1 <merge>`, адресні читання коду/тестів/документів. Власний checkout — лише `integ-c`.

```text
uv sync --all-packages --locked
Resolved 105 packages in 10ms
Prepared 19 packages in 15.07s
Installed 101 packages in 2.73s
exit 0

docker compose -p jane-m3c-doc-review config --services
no configuration file provided: not found
exit 1

git diff --check
exit 0; без виводу
```

Під час C-1 `uv sync` підготував лише власну `.venv`; запланований ContentReader repro скасовано до його запуску
за уточненням людини. Не запускалися pytest/just check/just e2e, backup/restore, новий CI або Docker-стеки.
Код сервісів, контракти, матриця, status.md та чужі worktree потоком C не змінювались.

## Відтворення після B2

**C-2 завершено, 2026-10-09, із неперевіреним браузерним входом через недоступний інструмент.**
B2 прийнято й злито потоком A `5fd7acd` з маркером `merge: accept B2`;
CI [37857870977](https://github.com/sql-monk/Jane/actions/runs/37857870977) на коді
`7b41bf4c6733f65a32340841a4f7dd7f61bad914` — 13/13 success,
e2e `75 passed in 1403.48s`, без skipped/xfail/failed.
Своя додаткова адресна перевірка C: auth 37 passed; JWKS-мутант падає на `20 == 1`, файл відновлено
байт у байт; тимчасовий review-worktree прибрано. Деталі — [stream-c.md](stream-c.md).

Чистий клон: `b3b11016de6d3bb2b421dd8cb8ccf4a66ee4c29e`, окремий тимчасовий каталог поза репозиторієм.
Послідовність документів: README → DEVELOPMENT → examples → operations; для входу — README адмінки.
Проєкти лише власні: `jane-m3c-dev-e09161a4` і `jane-m3c-examples-e09161a4`.

| Документ | Команда / дія | Результат |
|---|---|---|
| DEVELOPMENT | `uv sync --all-packages` | exit 0, чистий клон до встановлення без змін |
| DEVELOPMENT / infra | `uvx --from rust-just just up --project jane-m3c-dev-e09161a4` | exit 0; PostgreSQL/SQL Server/MongoDB/MinIO/S3/testsite/proxy піднято, ключ згенеровано |
| web/admin README | з `web/admin`: `corepack pnpm install --frozen-lockfile`, `corepack pnpm build` | exit 0; Node 24, pnpm 11.27.1; production assets створено |
| DEVELOPMENT / operations | `just up --project <P> proxy web-collector telegram-collector handler-runtime storage orchestrator registry llm assistant` (через документований uvx) | exit 0; усі вісім застосунків healthy |
| DEVELOPMENT / web/admin README | `uvx --from rust-just just env --project <P> --format json` | exit 0; ключ адміністратора доступний як `auth.admin_api_key`, значення не публікується |
| operations / web/admin README | GET через proxy `/api/<сервіс>/v1/health`, `/api/<сервіс>/v1/info`; Authorization Bearer із документованого ключа | для всіх восьми: health 200; info без ключа 401, із ключем 200 |
| web/admin README | HTTP GET `/` і браузерний вхід за ключем | HTTP 200 із production assets; вхід **не перевірено** — браузерний міст не приєднав webview (C-N4) |
| DEVELOPMENT | `uvx --from rust-just just down -v --project jane-m3c-dev-e09161a4` | exit 0; власних контейнерів, мереж і томів не залишилося |
| examples | `uv run --all-packages python deploy/profiles/stack.py up --project jane-m3c-examples-e09161a4 --profile dev-laptop --telegram` | exit 0; реальні сервіси, Telegram із записаним backend |
| examples | `uv run --all-packages python examples/jane_examples.py demo --project <P>` | exit 0; `ok: true`, 23 RAW, 16 сутностей; price-check за розкладом, 4 partial-оновлення, title збережено |
| examples | `uv run --all-packages python examples/jane_examples.py telegram --project <P>` | exit 0; `ok: true`, історія 3 матеріали, зміни 2, у підсумку 5 RAW / 3 події; lecture_version 2; Telegram **З** |
| examples | `uv run --all-packages python deploy/profiles/stack.py down --project <P>` | exit 0; `leftovers: {}`; власних контейнерів, мереж і томів не залишилося |
| backup-restore | статичне звірення dump/restore й післявідновлювальних API-команд | API-перевірки вже вимагають ключ нового стеку; dump/restore виконуються клієнтами БД, B2 їх не змінює; повторної репетиції не було |

`<P>` у dev-рядках — `jane-m3c-dev-e09161a4`, у examples — `jane-m3c-examples-e09161a4`.
HTTP виконано невеликим Python-клієнтом із тими самими документованими URL/заголовком.
Витяги фактичного виводу (форматування HTTP-рядків скорочено):

```text
web-collector      health=200 without_key=401 with_key=200
telegram-collector health=200 without_key=401 with_key=200
handler-runtime    health=200 without_key=401 with_key=200
storage            health=200 without_key=401 with_key=200
orchestrator       health=200 without_key=401 with_key=200
registry           health=200 without_key=401 with_key=200
llm                health=200 without_key=401 with_key=200
assistant          health=200 without_key=401 with_key=200
admin /: 200

demo exit: 0
"ok": true, "failures": [], "raw_objects": 23, "entities": 16
"platform_profile": "dev-laptop"
telegram exit: 0
"ok": true, "failures": [], "raw_objects": 5
"lecture_version": 2
"substitute": "Telegram = recorded backend of telegram-collector (З)"
examples-down exit: 0
"leftovers": {}
example cycle exit: 0
Owned clean clone exists: False
```

Summary й повні логи збережено в ignored `.jane/m3c-c2-evidence.json`,
`.jane/m3c-c2-examples-summary.json`, `.jane/m3c-c2-*.txt`. Ключі не потрапляють у звіт/коміт.
Чистий клон перед видаленням мав порожній `git status --porcelain`; клон і власний review-worktree
видалено, обидва compose-проєкти без контейнерів/мереж/томів. Чужі ресурси не прибиралися.

| ID / рівень | Доказ | Власник / рішення |
|---|---|---|
| C-W3 — **варто, виправлено** | `examples/README.md:31` досі стверджував, що SDK build_archive використовує deflate й інший digest; виправлення `69ab303` уже перейшло на канонічний ZIP_STORED. | WP-14, документація. Твердження актуалізовано цим потоком, код і тести не змінювались. |
| C-N4 — **примітка, межа інструмента** | Браузерний tab не створився: прихований виклик — timeout; видимий — `Timed out waiting for Browser webview to attach`. Доступний лише in-app browser. HTTP адмінки й API пройшли, вхід через UI не спостерігався. | Потік A / фінальний UI gate. Це не доказ помилки продукту; C не оголошує браузерний вхід перевіреним. |

**Нових блокерів у виконаних сценаріях не знайдено.** C-2 — функціональне відтворення документації
після B2; воно не замінює вимірювання лімітів dev-laptop або фінальний CI/real UI gate потоку A.
Повний локальний `just check`/`just e2e`, новий CI і повторний backup/restore не запускались.
