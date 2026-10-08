# Передача: потік A — координатор M3 (2026-10-09)

Цей документ дає змогу **повністю замінити** координатора потоку A (сесія Claude 7, що працювала 2026-10-08…09).
Прочитавши його, ти маєш довести проєкт до віхи **M3**. Підагенти попередньої сесії недоступні — весь стан лежить у
git, на origin і в цьому документі. Звітам агентів не вір на слово: перевіряй `git log`/`git status`/CI.

## 0. Що прочитати першим

1. `CLAUDE.md` — заборони, мови (документи українською, код/коміти англійською), команди.
2. `plan.md` §3–§7 (DoD, WP-13/WP-14 «Готово, коли», віхи; **M3** = прийняті WP-13 і WP-14, усі 13 критеріїв ТЗ §12
   підтверджені на фінальній ревізії, пройдено незалежне фінальне рев'ю; проєкт готовий, коли запуск відтворюється
   лише за документацією). ТЗ: `TECHNICAL_SPECIFICATION.md` §12.
3. Кінець `docs/delivery/status.md` (сесія 7: паузи, три потоки) і [M3/final-review.md](M3/final-review.md).
4. Доручення інших потоків: [stream-b](HANDOFF-2026-10-09-stream-b.md), [stream-b-2](HANDOFF-2026-10-09-stream-b-2.md),
   [stream-b-3](HANDOFF-2026-10-09-stream-b-3.md), [stream-c](HANDOFF-2026-10-09-stream-c.md); журнали
   [M3/stream-b.md](M3/stream-b.md), `M3/stream-c.md` (коли потік C його опублікує).
5. Інструменти: рецензент `.claude/agents/wp-reviewer.md` (Codex: `.codex/agents/wp-reviewer.toml`), охоронець
   контрактів `contract-guardian`; скіли `jane-wp`, `jane-contracts`.

## 1. Загальна картина

- `main` = `origin/main` = **`d37c522`** (людина перемотала fast-forward 2026-10-08). Уся подальша робота — в
  інтеграційній гілці **`codex/jane-integration`**; на момент запису вершина **`041e20d`**. `main` — її предок.
- **У `main` зливає лише людина** (fast-forward), після фінального gate. Ти даєш їй команди.
- Рішення людини, які діють:
  - вимірювання профілю `dev-laptop` ×3 (WP-14) **виключено** з обсягу; критерій 13 — S-M2-09 + живе прийняття
    профілю `ci`; `dev-laptop`/`single-node` — «не перевірено на реальному середовищі»;
  - **швидко без суттєвої втрати якості, мінімум перевірок**: важкі перевірки — у GitHub CI, нові сценарії локально
    ×2, одне незалежне рев'ю на кодовий інкремент (≤2 раунди; виправлення після раунду 1 координатор перевіряє сам —
    репро/мутант рецензента, без раунду 2); документальні зміни — без тестів і рецензентів;
  - робота розділена на **три потоки координаторів** (A, B, C), що зливають в одну інтеграційну гілку;
  - на прохання «призупини» — зупинити агентів, зупинити (не видаляти) їхні Docker-контейнери, записати стан у
    `status.md`; «продовжуй» — відновити.
- Контейнери **`puluj-g-*`** — сторонній проєкт людини; **ніколи** не зупиняти/видаляти. Docker — лише власні
  compose-проєкти з унікальною назвою; `docker system prune` заборонено.

## 2. Потоки

| Потік | Хто | Обсяг | Стан на момент запису |
|---|---|---|---|
| **A** | **ти** | B2 (автентифікація), фінальний gate M3, `status.md` | див. §3 |
| B | Codex (окремий застосунок; напряму не доступний — комунікація через документи в інтеграційній гілці й людину) | 1-ша черга: WP-12d, WP-13s, WP-14d, should-fix — **злито**; 2-га: B-5 матриця/сценарії, B-6 беклог — **злито** `8726647`; 3-тя ([stream-b-3](HANDOFF-2026-10-09-stream-b-3.md)): B-7 (адмінка бере ключ зі стек-файлу + **один real-прогін адмінки на зведеній ревізії** — це real-перевірка фінального gate; таблиця scopes у `templates/service`), B-8 (ADR-0005 за рішеннями B2), B-9 (позначити в беклозі закрите B2) | готує B-7/B-8 поверх `origin/wp/01g2-service-auth`; **зливає лише після появи `merge: accept B2`** в історії інтеграційної гілки |
| C | окремий агент (напряму не доступний) | C-1: фінальне рев'ю дельти всіх злиттів після `d37c522`, крім B2 → `docs/delivery/M3/final-review-delta.md`; C-2: повторне відтворення з чистого клону лише за документацією **після** `merge: accept B2` | C-1 у процесі; проміжний `M3/stream-c.md` лежить **незакоміченим** у worktree `integ-c`. Його підозра про TOCTOU проміжних каталогів у `ContentReader` — уже відоме обмеження ([01h-content-policy.md:222-223](M3/01h-content-policy.md)), не блокер |

**Маркер для B і C:** злиття B2 в інтеграційну гілку має містити в повідомленні рядок **`merge: accept B2`** — за ним
вони стартують B-7/B-8/C-2.

## 3. Стан потоку A

### 3.1 Злито в `codex/jane-integration` після `d37c522` (з доказами)

| Злиття | Що | Доказ |
|---|---|---|
| `08b4110` | WP-13r: R-04 під час активної роботи (7 виконавців) | рев'ю accepted; CI 37814680885: 12/12, e2e 71 passed |
| `03a31fa` | WP-13t: реальний registry в e2e-фікстурах, `JANE_E2E_REQUIRED=1`, формулювання матриці | рев'ю accepted; CI 37825596907: 12/12, e2e 71 passed, 0 skipped |
| `0507ef9` (B) | WP-14d: точки входу документації, backup/restore, змінні планувальника, тести examples/profiles у `just check` | рев'ю accepted; CI 37819395884, 37848025370 |
| `86cdece` (B) | WP-13s: R-04 для LLM completions і задач асистента; затримка фейкового LLM; дефект `unknown.py` | рев'ю accepted; CI 37847417132: e2e 75 passed |
| `cdf261a` | **B1** / WP-01h: спільний `ContentReader` (jane-kit) для llm/assistant/runtime, корені `file://` і allowlist `download_url`; runtime/llm читають RAW storage лише для читання | рев'ю безпеки r1 changes requested → виправлено, перевірено координатором (мутант 6 failed); CI 37846393926 (e2e 71), 37852086269 |
| `69ab303` (B) | M3 should-fix: SDK канонічний архів, keep-alive оркестратора, політика адрес Web Collector, TOCTOU секретів, порт llm, WP-09 `source_id` у повторній обробці, `stored_object_id` | рев'ю r2 accepted; CI 37853233033 (основні job) |
| `bf69429` (B) | WP-12d: S-M2-10 адмінка на real API (24/1/1), новий CI job `web-mock-e2e` | рев'ю r2 accepted; CI 37850908072 |
| `8726647` (B) | B-5 (матриця/сценарії під фінальну ревізію, з розділом «Фінальна ревізія» із заповнювачами), B-6 (`M3/open-requests.md`) | документи, без тестів |
| `041e20d` | WP-06c: класифікація OOM (exit 137 без `OOMKilled` → `resource_exceeded`) — причина нестабільного L6 у `limits` | рев'ю accepted; CI 37857509190 |

Повний CI на зведеній ревізії **`cdf261a`** (до should-fix, WP-12d, WP-06c): [37853683903](https://github.com/sql-monk/Jane/actions/runs/37853683903) —
12/12, e2e **75 passed**, `limits` verdict `warn` (L2, не падіння).

### 3.2 B2 — автентифікація (блокер безпеки M3; ще НЕ злито)

- Блокер з фінального рев'ю: ADR-0005 вимагає перевірки токена й scopes у кожному сервісі; на `d37c522` — лише
  orchestrator/registry. Рішення координатора: реалізувати й `api_key`, і `jwt` (ADR прийнятий).
- Гілка на origin: **`wp/01g2-service-auth`** (локально в worktree `.claude/worktrees/wp01g` вона називається
  `wp/01g-service-auth` — після rebase її запушено під новим ім'ям, бо force push заборонено; стара
  `origin/wp/01g-service-auth` `0a5b56b` — до rebase, **не використовувати**). HEAD `5c36792`, код —
  `7b41bf4` (база `3ec9358` з B1/WP-13s/WP-14d/should-fix/WP-12d; без WP-06c). Звіт: `docs/delivery/M3/01g-auth.md`.
- Зроблено: модуль `auth.py`/`auth_scopes.py` у jane-kit (режими `none`/`api_key`/`jwt`; ключі — хеш або `secret_ref`;
  JWT лише RS*/PS*/ES* за JWKS; 401 `unauthenticated`/403 problem+json; fail-closed; `none` лише на loopback; таблиці
  scopes = операції OpenAPI, тест звіряє множини); підключення в **усіх 8 сервісах**; власні сервісні токени
  (orchestrator → виконавці, assistant → кожен сусід, registry → runtime, llm → registry); стеки `just up`/e2e/профілі/
  приклади в режимі `api_key` (ключі 9 ідентичностей у `.jane/`, сервісам — хеші); `handler.v1` invocations у runtime і
  llm вимагають `handler:invoke`. CI до рев'ю: 37850701212 — 12/12, e2e 71 passed (L6 у першій спробі — причина
  OOM-класифікації, виправлено WP-06c).
- **Рев'ю безпеки, раунд 1 — changes requested** (рецензент a51ab…; решту коду визнав коректною: обходи шляхів
  fail-closed, alg-confusion, `compare_digest`, сервісні токени, секретів у журналах/CI немає):
  1. **(блокер)** `libs/jane-kit/src/jane_kit/auth.py` `_refresh`/`key`: поки немає жодного успішного завантаження
     JWKS, cooldown не діяв — кожен анонімний запит із підробленим `kid` звертався до IdP (репро: IdP 503,
     cooldown=10, 20 запитів → 20 завантажень), запити вишиковувались під lock по тайм-ауту 5 с.
  2. тести нормалізації шляхів (`//v1/x`, `/V1/x`, `/v1/%74x`, `/v1/health/../x`, `/v1/health/`, `/v1/health%2f` →
     401; HEAD з GET; OPTIONS поза таблицею → 403);
  3. застарілий `authenticate()` у `services/orchestrator/src/jane_orchestrator/auth.py`;
  4. `ExecutorConfig.token` → `SecretStr` (`services/orchestrator/.../settings.py`);
  5. README registry: відсутній `actor` у JWT/ключі → `human`.
  `/metrics` відкритий за замовчуванням — задокументоване рішення (йде в ADR через B-8).
- Автор вніс виправлення і **зупинився** (на вимогу людини), усе закомічено й запушено:
  - `origin/wp/01g2-service-auth` HEAD **`5c36792`** (лише документація, `[skip ci]`); останній кодовий коміт —
    **`7b41bf4`**; виправлення рев'ю — `fe977e4`. База — `codex/jane-integration` `3ec9358` (без WP-06c `041e20d` і
    без пізніших документальних комітів — злиття їх підтягне). Docker-проєктів автора не лишилось.
  - Звіт `docs/delivery/M3/01g-auth.md`: розділи «Rebase на інтеграційну ревізію і L6», «Виправлення після рев'ю 1»,
    «Передача». Конфлікти rebase були в `services/llm/src/jane_llm/settings.py` (імпорти) і
    `services/handler-runtime/README.md` — збережено обидві сторони. Нові шляхи B1/WP-13s до сервісів Jane — з
    токенами; `ContentReader` і R-04-«шлюзи» ходять лише до `package-host` (токен не потрібен).
  - За автором: п. 1 — до IdP не частіше одного запиту за cooldown з будь-якої причини, зокрема після невдачі;
    паралельні запити не завантажують JWKS вдруге; без ключів — одразу 503 з `Retry-After` без нового запиту й без
    повторного warning; відомий `kid` працює з кешу під час і після невдалого оновлення; тест «IdP 503, 20 запитів → 1
    завантаження», на старому коді обидва нові тести падають. П. 2–5 зроблено (`authenticate()` перенесено в
    тестовий `orch_support.py`). Локально: ruff/mypy чисті; auth-тести jane-kit і сервісів +
    `test_logic`/`test_executors` orchestrator — `98 passed, 1 skipped` (postgres-параметр llm).
  - Повний CI на `7b41bf4`: **[37857870977](https://github.com/sql-monk/Jane/actions/runs/37857870977)** — на момент
    зупинки success: lint, unit, contract, web, web-mock-e2e, isolation, adapters ×4; **ще виконувались `e2e`,
    `stack`, `limits`**. L6 у `limits` ще може впасти через OOM-класифікацію, бо гілка не містить WP-06c — це не
    дефект B2 (виправлено в `041e20d`, перевіриться у фінальному CI).
  - Запити автора до інших власників: WP-00/ADR (`/v1/info`, `/metrics`, scopes) → B-8; WP-12 ключ real-e2e зі
    стек-файлу і WP-01 scopes у `templates/service` → B-7; WP-06 OOM → уже закрито `041e20d`.

**Що зробити з B2:**
1. `git fetch origin`; переконайся, що `origin/wp/01g2-service-auth` = `5c36792` (або новіше, якщо хтось продовжив);
   прочитай «Передачу» в `01g-auth.md`; worktree `wp01g` має бути чистим.
2. Перевір CI 37857870977: усі job success, рядок e2e без skip (`JANE_E2E_REQUIRED=1`), `stack`. Падіння лише L6
   у `limits` з симптомом OOM (`execution_error`, exit 137) — відоме й закрите WP-06c, B2 не блокує. Інше червоне —
   з'ясуй причину; виправлення в новій гілці від `5c36792` (агентом або сам), один CI.
3. **Сам перевір виправлення рев'ю** (без раунду 2): прочитай `git diff 0a5b56b..origin/wp/01g2-service-auth --
   libs/jane-kit/src/jane_kit/auth.py libs/jane-kit/tests/test_auth.py services/orchestrator`; запусти
   `uv run --all-packages python -m pytest libs/jane-kit/tests/test_auth.py -q`; **мутант**: прибери в `auth.py`
   запам'ятовування часу невдалої спроби JWKS — тест «IdP 503, N запитів → ≤1 завантаження за cooldown» має впасти
   (зразок скрипта мутанта — як для B1: читати файл, підмінити, запустити, відновити байт у байт у `finally`);
   переконайся, що п. 2–5 зроблено.
4. Злиття (з `integ-a`): `git pull --ff-only origin codex/jane-integration`, потім
   `git merge --no-ff origin/wp/01g2-service-auth -m "merge: accept B2 / WP-01g service authentication …"` (маркер
   **`merge: accept B2`** обов'язковий). Очікувані конфлікти: `services/handler-runtime/README.md` і, можливо,
   `executor.py`/settings з WP-06c (`041e20d`); README/settings llm, orchestrator, web-collector, telegram з should-fix;
   `infra/compose.yaml`, `tests/e2e/compose.e2e.yaml` (B1 allowlist/монтування); `.github/workflows/ci.yml`
   (`web-mock-e2e`, env e2e). Розв'язуй, **зберігаючи обидві сторони**. Після злиття: ruff, адресні тести
   jane-kit `test_auth`/`test_content`, `just test handler-runtime` (без Docker), `just test orchestrator` unit.
   Push інтеграційної гілки. Якщо розв'язання конфліктів у коді нетривіальне — одразу фінальний CI (див. §4) на
   результаті, він же буде фінальним, якщо B/C більше нічого не зіллють.
5. Запиши в `status.md` (розділ сесії 7) і оновити [M3/final-review.md](M3/final-review.md) таблицю «Дороблення».

### 3.3 Фінальний gate M3 (після B2, B-7/B-8, C-1/C-2)

1. Дочекайся: B — `B-7`/`B-8` злито (журнал `M3/stream-b.md`, розділ «Третя черга», там же `N passed` real-прогону
   адмінки на зведеній ревізії); C — `M3/final-review-delta.md` (C-1) і розділ «Відтворення після B2» (C-2) злито.
   Блокери, які вони назвуть у коді сервісів, — виправити (агентом), одне рев'ю, один адресний прогін.
2. **Один** повний CI на остаточній вершині: `gh workflow run ci --ref codex/jane-integration` (push у цю гілку CI не
   запускає — workflow реагує лише на `main` і `wp/**`). Перевір: 12+ job success (зокрема `web-mock-e2e`), рядок e2e
   (`N passed`, 0 skipped/xfailed), `limits` verdict (`pass` або `warn` — `warn` зафіксувати чесно).
3. Заповни розділ **«Фінальна ревізія»** на початку `docs/acceptance/matrix.md` (заповнювачі `<SHA>`, `<CI run>`,
   `<рядок e2e>` підготував B-5): SHA коду, на якому пройшов CI; якщо після нього йдуть лише документальні коміти —
   так і написати («код ідентичний `<SHA>`»). Додай результат real-прогону адмінки (B-7) і вердикт C.
4. `status.md`: таблиця WP — 13 і 14 → `accepted` (з посиланнями), віха **M3 — досягнуто** з датою й SHA; короткий
   підсумок у [M3/final-review.md](M3/final-review.md) (блокери B1/B2 закрито, дельта-рев'ю C, відтворення C-2).
5. Дай людині команди (вона виконує сама; Claude не має права пушити `main`):
   ```bash
   git -C C:/repos/Jane merge --ff-only origin/codex/jane-integration
   ```
   ```bash
   git -C C:/repos/Jane push origin main
   ```
   Основний checkout `C:\repos\Jane` стоїть на `main` (чистий). Після push перевір `gh run list --branch main`
   (якщо вершина має `[skip ci]`, push CI не запустить — тоді `gh workflow run ci --ref main`).

## 4. Робочі правила й пастки

- **Checkouts:** твій — `C:\repos\Jane\.claude\worktrees\integ-a` (на гілці `codex/jane-integration`); потоки B і C
  зливають із detached `integ-b`/`integ-c` через `git push origin HEAD:codex/jane-integration`. **Перед кожним своїм
  злиттям — `git pull --ff-only`.** Не працюй в `integ-b`/`integ-c`/чужих worktree.
- Старий checkout `C:\Users\aleks\.codex\worktrees\fix-agent-hooks-ci\Jane` **прибрав Codex** — не покладайся на
  checkouts у `.codex\worktrees`.
- Хук `guard_bash` забороняє force push завжди; у checkout з `.jane-wp` — push у main, `git merge`, refspec із `:`,
  видалення гілок. Перебазовану гілку, яка вже є на origin, пушать **під новим ім'ям** (`…2-…`).
- Нові інкременти: worktree `.claude/worktrees/<id>` на гілці `wp/NN<x>-*` від інтеграційної вершини; `.jane-wp`
  (`WP-NN`) — для робіт одного власника; для наскрізних доручень координатора `.jane-wp` не створюють, але звіт групує
  файли за власниками з `.claude/wp-paths.json`. Звіти наскрізних робіт — `docs/delivery/M3/<id>.md`.
- CI: push у `wp/**` запускає lint/types/unit/contract/web/web-mock-e2e/isolation; `stack`, `adapters`, `e2e`,
  `limits` — лише `workflow_dispatch` (`gh workflow run ci --ref <гілка>`). У job e2e діє `JANE_E2E_REQUIRED=1`.
  Concurrency-група скасовує push-прогін, коли той самий ref запущено через dispatch.
- Повідомлення комітів — англійською; документи — українською. Коміти з лише документацією — `[skip ci]`.
- Windows/Git Bash: у Python-heredoc шляхи з `\U…` пиши як raw-рядок `r"""…"""`; пиши файли з `newline="\n"`;
  `git rev-parse --short A B` з двома аргументами падає — по одному.
- Документи не дублюй у пам'ять агента; правда — у git (`status.md`, `M3/*.md`, звіти WP).

## 5. Карта worktree (на момент запису)

Активні: `integ-a` (A), `integ-b` (B), `integ-c` (C), `wp01g` (B2, локальна гілка `wp/01g-service-auth` = origin
`wp/01g2-service-auth`). Відпрацьовані й злиті: `wp01h`, `wp06c`, `wp12d`, `wp13r`, `wp13s2`, `wp13t`, `wp14d`,
`wpm3fix`; незадіяний порожній `wp13s` (гілка `wp/13s-r04-llm-assistant` без комітів). Десятки старіших worktree
(`agent-*`, `wp01b…wp14c`, `wpflaky*`) — історичні. Прибирання worktree/гілок — **після M3 і лише з дозволу людини**.

## 6. Після M3 (не блокує)

Беклог — [M3/open-requests.md](M3/open-requests.md) (31 група): уточнення контрактів через contract-guardian (409 у
`llm.v1` completions, `object_ids` у `ReprocessRequest`, `DeliveryRecord.acks` тощо), рефакторинг jane-kit (спільні
`JobStore`/`IdempotencyStore`), бюджет 0/`period` асистента, `provider.*` тайм-аут llm, спільний ліміт хоста між
екземплярами, TOCTOU проміжних каталогів `ContentReader`, семантика async-повтору storage. Не перевірено на реальних
сервісах: LLM-провайдер, AWS S3, OIDC з реальним IdP, профілі `dev-laptop`/`single-node`.
