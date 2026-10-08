# Фінальне рев'ю дельти M3 — потік C

Дата: 2026-10-09. Доручення: [HANDOFF-2026-10-09-stream-c.md](../HANDOFF-2026-10-09-stream-c.md).
Рецензент потоку C не був автором переглянутих інкрементів. Один прохід, без додаткових рецензентів
і повторення повних тестових наборів. База першого рев'ю — `main` `d37c522`;
переглянута інтеграційна ревізія — `041e20d` (початковий зріз `76a03f7` доповнено змінами інших потоків).

**Вердикт C-1: нових блокерів M3 у переглянутій дельті не знайдено.** Одну документальну неточність
виправлено; залишаються неблокувальне зауваження й відомі обмеження нижче. Це не фінальне приймання M3:
B2, фінальний CI, заповнення фінальної ревізії матриці та злиття в `main` належать потоку A/людині.

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

`uv sync` підготував лише власну `.venv`; запланований ContentReader repro скасовано до його запуску
за уточненням людини. Не запускалися pytest/just check/just e2e, backup/restore, новий CI або Docker-стеки.
Код сервісів, контракти, матриця, status.md та чужі worktree потоком C не змінювались.

## Відтворення після B2

**Ще не виконано.** На переглянутому `origin/codex/jane-integration` `041e20d` немає
`merge: accept B2` / accepted WP-01g. Згідно з handoff після публікації C-1 потік C зупиняється
й повідомляє людині; новий чистий клон, `just up`, 401/200, вхід адмінки та demo/telegram
мають бути відтворені після B2 на тодішній ревізії. Backup/restore повторювати не потрібно.
