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
| C-N4 — **примітка, межа інструмента; надалі закрито B-11** | Під час C-2 браузерний tab не створився: прихований виклик — timeout; видимий — `Timed out waiting for Browser webview to attach`. HTTP адмінки й API пройшли, власний вхід C через UI не спостерігався. | Подальший real-прогін B-11 підтвердив вхід; receipt звірено у «Дельта 2» нижче. C не приписує собі виконання цього UI-прогону. |

**Нових блокерів у виконаних сценаріях не знайдено.** C-2 — функціональне відтворення документації
після B2; воно не замінює вимірювання лімітів dev-laptop або фінальний CI/real UI gate потоку A.
Повний локальний `just check`/`just e2e`, новий CI і повторний backup/restore не запускались.

## Дельта 2

Дата: 2026-10-09. Доручення: [HANDOFF-2026-10-09-stream-c-3.md](../HANDOFF-2026-10-09-stream-c-3.md), C-4.
Один статичний прохід по результатах злиттів; без pytest, lint/typecheck, Docker, CI dispatch або нового
раунду рев'ю безпеки B2. Рецензент C не був автором B2 чи WP-06d.
Початковий зріз пп. 1–2: **`3a4e29c59d620c4e12b692b9968db6266a8405e6`**, тоді B-11 ще не було.
Продовження за четвертим handoff: B-11 `97ea4c4` уже в origin; фінальна переглянута вершина —
**`19d58a1b2cf1590a5f780871b31ba0b595d9009b`**. B2/WP-06d повторно не переглядалися;
виконано один статичний прохід лише по B-11 і його наявних доказах, без запуску тестів.

### Злиття → вердикт → знахідки

| Злиття | Вердикт | Знахідки / фактичний статичний доказ |
|---|---|---|
| B2 — `5fd7acd` (батьки `4f0b2a9`, `5c36792`) | Злиття зберегло перевірений B2 і попередні інкременти; нових блокерів немає | База B2 — `3ec9358`; набори шляхів у `3ec9358..7b41bf4` і `5fd7acd^1..5fd7acd` однакові: 61/61, без пропущених або додаткових файлів. 58 із 61 кінцевого файла збігаються байт у байт із `7b41bf4`, зокрема весь код, тести, конфігурація та lockfile. Три відмінності — лише документи, пояснені нижче. Scope-таблиці й wiring усіх восьми сервісів, сервісні токени та генерація ключів збережені. |
| WP-06d — `3e13f68` (`065a15a`…`7fe87b9`) | Тест не послаблено й не проходить порожньо; нових блокерів немає | Єдина зміна коду злиття — `services/handler-runtime/tests/test_app.py:129`: параметризація sync/async, перевірка HTTP 200/202, очікування кінцевого job result за 202. Усі попередні кінцеві assertions збережено. Probe виконує справжній `socket.create_connection`; незмінний Docker isolation-тест відокремлює перевірку мережевого ізолювання від API-класифікації (C-N5). |
| B-11 — `97ea4c4`, B-7 / B-8 / B-9 | Злиття переглянуто, нових блокерів немає; C-N4 закрито receipt | Wrapper бере ключ рівно одного matching stack, template передає AUTH_SCOPES, ADR відповідає B2, беклог зберігає відкритий C-W2/R33. Сирі логи: 16 passed/1 failed на `7eed2e1`, потім 1 passed на `48af2a1` після Bearer у трьох прямих GET одного тесту; решта 16 сценаріїв, wrapper, UI/сервіси та fixture незмінні. Це 16+1 підтверджених сценаріїв, не один повний зелений прогін фінального SHA. |

### Збереження B2 і попередніх змін

- `services/handler-runtime/src/jane_handler_runtime/executor.py`, `sandbox.py`, `docker_sandbox.py`
  збігаються байт у байт із першим батьком B2. Класифікація WP-06c, ознака власного kill і розрізнення
  OOM/SIGKILL не переписані. Незмінний B2 `test_classification.py` також не входить у дельту злиття.
  Відмінність runtime README від гілки B2 — саме збережений опис WP-06c у `services/handler-runtime/README.md:40`;
  розділ B2 «Автентифікація» (`:209`) присутній разом із ним.
- `libs/jane-kit/src/jane_kit/content.py` і `.github/workflows/ci.yml` збігаються байт у байт із першим
  батьком B2. ContentReader/B1, `web-mock-e2e` і обов'язковий e2e gate не загублені.
  B2-доповнення `infra/compose.yaml` — auth-конфігурація; дозволені RAW-корені та read-only монтування
  runtime/LLM (`:190`, `:299`) збережено. Відоме C-N1 не переоцінювалося, repro не запускався.
- Should-fix лишилися на місці: LLM settings додає SecretStr registry token без вилучення secret-policy/
  api_base/лімітів; settings Web/Telegram Collector B2 не змінює. Orchestrator додає token_ref і SecretStr,
  зберігаючи scheduler/run_workers, клієнтські ліміти й retry policy. README цих сервісів доповнено auth,
  попередні налаштування та обмеження не вилучено. Результати цих файлів збігаються з перевіреним B2.
- Три відмінні від `7b41bf4` документи: `docs/delivery/M3/01g-auth.md` містить передачу `5c36792` замість
  CI-placeholder; `docs/operations/backup-restore.md` зберіг виправлення C-W1 разом з auth-доповненнями;
  runtime README зберіг WP-06c. Втрати змін під час об'єднання не знайдено.

### Scope, токени й ключі

- Усі вісім продукційних app передають таблиці у `create_app`: collectors — COLLECTOR, runtime — HANDLER,
  storage — merge(HANDLER, STORAGE), LLM — merge(HANDLER, LLM), assistant — ASSISTANT, registry — REGISTRY,
  orchestrator — ORCHESTRATOR. Джерела: `services/*/src/*/app.py`, зокрема runtime `:161`, registry `:262`,
  orchestrator `:82`. Додаткового продукційного FastAPI/mount, що обходив би цю фабрику, не знайдено.
- `libs/jane-kit/src/jane_kit/service.py:101` встановлює загальний `Depends(authorize)`, а `:82` викликає
  перевірку таблиць на старті. `auth.py:712` використовує метод і шаблон **підібраного маршруту**;
  відсутній запис дає Forbidden (`:725`), потрібний scope перевіряється через principal (`:731`). HEAD
  успадковує GET, а метод без власного запису не отримує дозволу. `auth.py:763` відхиляє неповну таблицю
  на старті. Бізнесоперації, що після злиття лишилися без перевірки scope, не знайдені.
- `/v1/info` та приватні `/metrics`/службові сторінки навмисно допускають будь-який **дійсний** токен
  (`auth.py:90`); це визначена поведінка B2, а не випадіння бізнес-scope. Публічні шляхи — точний health
  і metrics за відповідним налаштуванням; режим none на нелокальному host відхиляється без явного
  test-винятку (`auth.py:750`). Scope-таблиці `auth_scopes.py` і їхній контрактний equality-тест збережені;
  тут тест не запускався.
- Вихідні токени лишилися токенами власного сервісу: orchestrator resolves token_ref і передає
  `cfg.token.get_secret_value()` (`services/orchestrator/src/jane_orchestrator/executors.py:119`);
  assistant бере власні refs/default і bearer_header (`services/assistant/src/jane_assistant/clients.py:296`);
  runtime/LLM розкривають SecretStr лише для запиту до registry (`packages.py:190` / `app.py:168`);
  registry додає власний token для runtime info (`services/registry/src/jane_registry/profiles.py:127`).
  Incoming principal/header не підміняє ці токени. Compose налаштовує хеші й scopes відповідних identities.
- `new_api_keys` у jane-kit/dev.py/profile stack і e2e credentials залишають генерацію окремих ключів
  із SHA-256, збереження наявних ключів та доповнення старого stack-файла. Джерела:
  `libs/jane-kit/src/jane_kit/devstack.py:53`, `scripts/dev.py:312`, `deploy/profiles/stack.py:252`,
  `tests/e2e/jane_e2e/stack.py:224`. `scripts/dev.py:485` при up друкує спосіб отримання ключа, його значення
  не друкує; stack-файли залишаються під ignored `.jane/` (`.gitignore:30`). Auth-клієнти examples/e2e
  й key tables compose збігаються з перевіреною гілкою. Вхід адмінки та шаблон scopes належать майбутньому B-11.

### Знахідки й межі

| ID / рівень | Файл:рядок, доказ | Власник / рішення |
|---|---|---|
| C-N5 — **примітка, межа доказу WP-06d** | `services/handler-runtime/tests/test_app.py:129` перевіряє API-класифікацію мережевої спроби через subprocess fixture (`tests/conftest.py:85`). У `test_app.py:143`–`:146` лишилися failed/sandbox_violation/непорожні socket events; за 202 результат читається з кінцевого job. `tests/packages/probe/src/probe/main.py:29` справді відкриває socket. Ізоляцію ядром доводить окремий незмінний `tests/test_isolation.py:106`: контрольний bridge-контейнер досягає сервера, sandbox повертає OSError unreachable і sandbox.network_blocked. | WP-06. WP-06d не підміняє Docker isolation-тест і не заявляється його новим запуском. Незавершений job або відсутній result не можуть задовольнити кінцеві assertions. Нового блокера немає. |
| C-N4 — **примітка, закрито B-11** | `web/admin/e2e/fixtures.ts:36` виконує login за ключем, `:60` використовує його в admin fixture. Сирі `b11-real.log` / `b11-registry.log` підтвердили 16+1 сценаріїв, auth.spec.ts присутній у повному прогоні; fingerprint бекенду та admin_key_consistent — true. | WP-12 / потік B. Вхід за ключем підтверджено на зведеній ревізії B-11; C лише звірив готові докази, UI не запускав. |
| C-N6 — **примітка, уточнення storage-критерію** | `docs/adr/0005-authentication.md:30` явно дозволяє dev-ключ лише у sessionStorage; `web/admin/src/auth/session.ts:16` так його зберігає. `e2e/fixtures.ts:44` перевіряє HTML, URL і localStorage. Формулювання «сховище браузера» у попередньому handoff ширше за чинний ADR. | WP-00 / WP-12. Критерій цього приймання: не відображати ключ, не класти в URL/localStorage; sessionStorage дозволений ADR. B-11 не змінює цю поведінку; новим блокером вона не є. |

**Підсумок незалежного статичного рев'ю `d37c522..19d58a1`: нових блокерів M3 не знайдено.**
C-1 разом із «Дельта 2» покриває інтегровані інкременти цього зрізу, включно з B-11.
C-W1/C-W3 виправлені, C-W2 лишається після M3, C-N4 закрито; відомі примітки C-N1–C-N3, C-N5/C-N6 збережені.
C-4 завершено. Фінальне приймання, матриця й status.md — потоку A; CI 37863992541 перевіряє попередній
SHA `8d7683b` без B-11, підсумок цього CI окремо ведеться в stream-c.md.

Фактичний вивід статичного порівняння (`.jane/m3c-delta2-audit.txt`, ignored):

```text
B2 base: 3ec9358768dc3e5ada05d5ac13b148d28d934727
B2 branch files: 61; merge files: 61
Branch-only paths: []
Merge-only paths: []
Merged blobs differing from tested B2 code:
  docs/delivery/M3/01g-auth.md
  docs/operations/backup-restore.md
  services/handler-runtime/README.md
Pre-merge preserved executor.py: True
Pre-merge preserved sandbox.py: True
Pre-merge preserved docker_sandbox.py: True
Pre-merge preserved content.py: True
Pre-merge preserved ci.yml: True
```

Команди цього проходу: `git fetch origin` (на старті й перед підсумком), адресні `git diff`/`git show`,
`rg`, читання вихідних файлів і порівняння Git blobs. Тимчасові worktree/clone, Docker-ресурси та CI
не створювалися. Власні зміни C — лише цей документ і `M3/stream-c.md`.

### B-11: ключ, шаблон, ADR і real-receipt

- `web/admin/scripts/e2e.mjs:27` вибирає `--project` / JANE_STACK_FILE / єдиний matching proxy URL;
  відсутній/неоднозначний stack чи ключ зупиняє запуск. JSON/ключ не додаються до помилки читання.
  `JANE_ADMIN_E2E_API_KEY` у дочірньому env завжди перезаписується ключем вибраного stack, незалежний
  env key не є fallback. Ключ не додається в URL або публічний config. `fixtures.ts:36` входить за ключем,
  `:68` звіряє Bearer усіх UI API-запитів і після сценарію перевіряє відсутність ключа в HTML/URL/localStorage.
  sessionStorage — явний виняток чинного ADR (C-N6), не оголошується порожнім.
- `templates/service/src/jane_template_service/app.py:29` задає POST example, GET job і POST cancel
  scope handler:invoke; `:67` передає таблицю у create_app. Новий тест `tests/test_app.py:115` перевіряє
  401 без токена, 403 з bare-token, дозволений 202/200 з потрібним scope, зокрема читання й cancel job.
  Він не мокав шаблон і не послаблював старі asserts; злиті app/test тотожні перевіреним фінальним файлам B.
  Повторного pytest C не було.
- Уточнення `docs/adr/0005-authentication.md:35` відповідають B2: info — дійсний token без окремого scope,
  metrics — відкритий за замовчуванням або token за METRICS_PUBLIC=false; none — loopback із явним
  test-винятком; 401 unauthenticated, 403 forbidden, 503 за недоступного порожнього JWKS-кешу.
  Таблиця scopes, сервісні refs і межа живого IdP узгоджені з переглянутим B2. OpenAPI не змінено.
- `M3/open-requests.md` зберіг попередній B-6, закрив лише реалізовані auth-запити, додав R32 scopes в OpenAPI
  і відкритий R33/C-W2 після M3. Живий IdP, producer ContentRef, спільні job stores та інші відкриті запити
  не оголошено закритими через B2. Код ProblemsPage не змінювався.
- Читання готових файлів у b11-real виконано з integ-c, без модифікацій чужого checkout і без запуску
  браузера/команд тестування. `b11-source.json` — `7eed2e1`, backend match/admin_key_consistent — true.
  Engine/auth fingerprint збігаються з Git `97ea4c4`: a6143284… / 391325a8… .
  Порівняння `7eed2e1..97ea4c4`: web/admin/src, services, jane-kit, wrapper і fixture незмінні;
  `7eed2e1..48af2a1` у web/admin/e2e змінює лише hybrid-registry.spec.ts.
  Виправлення додає Bearer до трьох GET і assertion HTTP 200; старі assertions про версії/порт збережено.
  Після адресного контролю — лише форматування рядка й документи, нового runtime/UI коду немає.

```text
b11-real.log, 7eed2e18799ad8ae36c40ca48b8b004f9943fdb3:
Running 17 tests using 1 worker
1 failed
16 passed (4.1m)
EXIT_CODE=1
auth.spec.ts present: True

b11-registry.log, 48af2a1bdf075a27f1568fbc2d5ca088ec03d65d:
Running 1 test using 1 worker
1 passed (26.9s)
EXIT_CODE=0

7eed2e1 -> 97ea4c4 changed web/admin/src: none
7eed2e1 -> 97ea4c4 changed services: none
7eed2e1 -> 97ea4c4 changed libs/jane-kit: none
7eed2e1 -> 48af2a1 changed test files: web/admin/e2e/hybrid-registry.spec.ts
backend match: True
admin_key_consistent: True
```

Єдина початкова відмова — тестовий прямий GET без Authorization (401), а не дефект UI/сервісів;
повний прогін лишається 16/1. Адресний контроль закрив саме його; повторний повний real-набір C не запускався.
Безсекретний витяг статичних звірок — `.jane/m3c-b11-static.txt` у власному integ-c (ignored).
