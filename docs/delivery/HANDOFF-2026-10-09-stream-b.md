# Передача: потік B до M3 (2026-10-09)

Цей документ — доручення **координатору потоку B**. Роботу до M3 людина розділила між двома координаторами,
що працюють паралельно. Ти береш потік B: чотири майже готові інкременти. Потік A лишається в попереднього
координатора (сесія Claude 7). Читай документ повністю, перш ніж щось змінювати.

## 0. Що прочитати спершу

1. `CLAUDE.md` (заборони, мови, команди), `plan.md` §3–§5, `DEVELOPMENT.md`.
2. `docs/delivery/status.md` — кінець файла (сесія 7, паузи) і `docs/delivery/M3/final-review.md` — фінальне рев'ю
   M3 і звідки взялись ці інкременти.
3. Скіл `jane-wp` (`.claude/skills/jane-wp/SKILL.md` або `.agents/skills/jane-wp/`), скіл `jane-contracts`.
4. Рецензент: `.claude/agents/wp-reviewer.md` (Claude) або `.codex/agents/wp-reviewer.toml` (Codex).

## 1. Розподіл

| Потік | Хто | Обсяг | Не чіпати |
|---|---|---|---|
| **A** | попередній координатор | B2 автентифікація (`wp/01g-service-auth`, worktree `wp01g`), B1 політика ContentRef + доступ runtime до RAW storage у compose (`wp/01h-content-ref-policy`, `wp01h`); **фінальний gate M3**: CI на фінальній ревізії, зведення `docs/acceptance/matrix.md` під фінальну ревізію, real-прогін адмінки на зведеній ревізії, рев'ю дельти, `status.md` | — |
| **B** | **ти** | WP-12d, WP-13s, WP-14d, M3 should-fix (розділ 3) — довести кожен до `accepted` і злити в `codex/jane-integration` | worktree `wp01g`, `wp01h` і їхні гілки; `libs/jane-kit/**` (там працює потік A); `docs/delivery/status.md`; фінальне зведення матриці |

Обидва потоки зливають прийняте в **одну** інтеграційну гілку `codex/jane-integration`. У `main` зливає лише
людина (fast-forward), після фінального gate потоку A.

## 2. Правила роботи (коротко)

- Заборони `CLAUDE.md` діють повністю: не послаблювати тести, не вигадувати поля контрактів, ліміти — з конфігурації,
  не писати «зелене» без виводу, не комітити секрети.
- **Ніколи:** push у `main`, merge у `main`, force push (хук блокує), `docker system prune`, зупинка чи видалення
  контейнерів `puluj-g-*` (сторонній проєкт людини). Docker — лише власні compose-проєкти з унікальною назвою.
- Рев'ю обов'язкове перед злиттям: незалежний `wp-reviewer` (не автор), ≤2 раунди. Якщо раунд 2 знаходить реальний
  дефект — автор виправляє, координатор перевіряє сам репро рецензента, без 3-го раунду.
- Швидкість без втрати якості (рішення людини): повний `just check`/`just e2e` локально не ганяти — push гілки
  `wp/**` запускає lint/types/unit/contract/web/isolation/stack/adapters, повний e2e — `gh workflow run ci --ref
  <гілка>`; нові сценарії локально ×2 на одному стеку (третій — CI); рев'ю запускати паралельно з CI. У CI вже
  діє `JANE_E2E_REQUIRED=1`: skip або 0 зібраних тестів — падіння. **Real-набір Playwright адмінки в CI немає** —
  його ганяють локально.
- Записи свого потоку веди в `docs/delivery/M3/stream-b.md` (журнал: що прийнято, CI, SHA злиття), **не** в
  `status.md` — так потоки не конфліктують. Потік A посилається на твій файл.

### Як зливати в інтеграційну гілку (два координатори)

Гілка `codex/jane-integration` вибрана в checkout потоку A (`C:\Users\aleks\.codex\worktrees\fix-agent-hooks-ci\Jane`)
— **не працюй у ньому**. Для злиттів створено окремий worktree `C:\repos\Jane\.claude\worktrees\integ-b`
(detached HEAD, без `.jane-wp`). Кожне злиття:

```bash
git -C C:/repos/Jane/.claude/worktrees/integ-b fetch origin
git -C C:/repos/Jane/.claude/worktrees/integ-b checkout --detach origin/codex/jane-integration
git -C C:/repos/Jane/.claude/worktrees/integ-b merge --no-ff <гілка> -m "merge: accept <WP> ... (reviewer verdict, CI run)"
git -C C:/repos/Jane/.claude/worktrees/integ-b push origin HEAD:codex/jane-integration
```

Якщо push відхилено (потік A встиг злити своє) — повтори з `fetch`. Конфлікти розв'язуй, зберігаючи обидві сторони;
після нетривіального розв'язання конфлікту в коді — CI на результаті злиття (`gh workflow run ci --ref` для тимчасової
гілки `wp/integ-b-check-<n>`, запушеної з того самого HEAD). Злиття без вердикту `accepted` від рецензента — заборонено.

## 3. Інкременти потоку B

Усі worktree — у `C:\repos\Jane\.claude\worktrees\`. Агенти, що їх виконували, зупинені на вимогу людини посеред
роботи: перевір `git status`/`git log`, звітам не вір на слово.

### 3.1 WP-12d — S-M2-10 адмінка на реальному API (`web/admin/**`)

- Worktree `wp12d`, гілка `wp/12d-real-reprocessing`, локальний HEAD `1664a32` — **уже перебазовано** на
  `codex/jane-integration` `03a31fa`. На origin ця гілка лишилась на старому `4a080e1` (до rebase), force push
  заборонено → **пушити під новим ім'ям**: `git -C <wt> switch -c wp/12d2-real-reprocessing` і далі лише її.
- Зроблено (рев'ю 1 це підтвердило): таблиця `@mock` 24 повністю / 1 частково / 1 навмисний мок (було 9/12/5);
  3 дефекти адмінки виправлено; real 17 passed у автора, у рецензента 9 passed на чистому стеку; mock у рецензента
  `29 passed, 14 skipped`.
- **Рев'ю 1 — changes requested**, виправлення почато, **3 файли не закомічено**
  (`web/admin/e2e/hybrid-m2-cycle.spec.ts`, `hybrid-m2-problems.spec.ts`, `llm-scripts.ts`). Що треба:
  1. (блокер) `hybrid-m2-cycle.spec.ts:~320` — `test.fail(true, "WP-09: …")` перенести безпосередньо перед фінальним
     `expect(fed.map((i) => i.observation_id)).toEqual([...])`, щоб помилки підготовки падали як звичайні.
  2. (блокер) `docs/delivery/WP-12.md:~936-937` — прибрати хибне «CI запускає mock-набір адмінки» (job `web` робить
     лише install/lint/typecheck/vitest/build); вставити справжній вивід mock-регресії
     `corepack pnpm --dir web/admin e2e`; вписати CI 37816522056 (lint, unit, web, contract, isolation — success).
  3. рядок 12 таблиці `@mock` — уточнити (trace з успішного елемента; невдалий елемент у real не виникає) або «частково».
  4. `hybrid-m2-problems.spec.ts:~406-407` — дочекатися заголовка сторінки джерела перед таблицею «Стратегії обходу»
     (на навантаженій машині рендер >10 с), без навмання збільшених тайм-аутів.
  5. новий job CI для **mock-набору Playwright адмінки** (`.github/workflows/ci.yml` — лише новий job; `scripts/dev.py`
     — лише нова команда, якщо потрібна): chromium, `pnpm e2e` у mock-режимі, без Docker, з кешем.
- Перевірка: змінені real-специфікації — 1 прогін на чистому стеку (спершу прибери зупинений стек:
  `just down --project jane-wp12d-r1 -v`); mock — повний прогін; web lint/typecheck; push → CI зелений (з новим job).
  Розділ «Виправлення після рев'ю 1» у `WP-12.md` зі справжнім виводом → рев'ю 2 (лише виправлення) → злиття.
- **Зв'язок із 3.4:** real-тест `reprocessing one stored material takes only RAW of the task's source (WP-09 defect)`
  має `test.fail`. Коли злито виправлення WP-09 із 3.4, він стане unexpected pass → прибери `test.fail` (у тій гілці,
  що зливається другою) і прожени цей тест real.

### 3.2 WP-13s — R-04 для LLM `/v1/completions` і задач асистента (`tests/e2e`, фейк LLM, `assistant/unknown.py`)

- Worktree `wp13s2`, гілка `wp/13s-r04-completions` `fcf798c` (запушено), база — `wp/13t-real-registry-fixtures`
  `39cafb5` (уже злита в інтеграційну).
- Зроблено: `a83fc35` `delay_ms` фейкового провайдера (межа `limits.fake.max_delay_ms`); `e45bfc2` дефект WP-11 —
  недоступний оркестратор більше не валить оплачений аналіз невідомого матеріалу; `aef3c4c` e2e R-04 під час
  активної роботи для LLM completions (sync/async) і job onboarding/improvement асистента; `fcf798c` — матриця,
  сценарії, розділ «WP-13s» у `docs/delivery/WP-13.md`.
- Не зроблено: адресний локальний прогін на перебазованій гілці (перерваний); CI 37847417132 (`workflow_dispatch`,
  повний e2e) на `fcf798c` був у черзі.
- Далі: дочекайся CI 37847417132 → нові сценарії PASSED, 0 skipped → незалежне рев'ю (перевірити детермінованість
  вікна, змістовність «без подвійних ефектів», відповідність `contracts/`, межу затримки з конфігурації, тест дефекту
  асистента, що падав до виправлення) → злиття. Якщо CI червоний — виправити в гілці.

### 3.3 WP-14d — документація, точки входу, backup/restore (`README.md`, `DEVELOPMENT.md`, `infra/README.md`, `docs/operations/**`, `deploy/profiles/**`, `examples/**`)

- Worktree `wp14d`, гілка `wp/14d-docs-entrypoints` `359eb0d` (запушено), база `3c98542`.
- Зроблено всі 9 знахідок частини B фінального рев'ю + рішення людини 2026-10-08 щодо профілів; повний CI
  37819395884 на `f21947f` — 12/12, e2e 62 passed, `limits` pass; репетиція backup/restore на трьох проєктах.
  Додатково: `cc74ccd` — `max_sub_half_gaps` у самоперевірці harness (тест падав після WP-14c); `359eb0d` — тести
  `examples` і `deploy/profiles` (без Docker) у `just unit`/`just check`.
- Не зроблено: звіт `docs/delivery/M3/14d-docs.md` не описує два додаткові коміти; CI 37848025370 (push) на `359eb0d`
  був у процесі.
- Далі: дочекайся CI 37848025370 (зелений, час `just check` суттєво не зріс) → допиши звіт → рев'ю → злиття.
  Можливі текстові конфлікти в `infra/compose.yaml`/`deploy/profiles/compose.stack.yaml` з потоком A (там B1 додає
  томи/корені handler-runtime) і в `.github/workflows/ci.yml` (WP-13t додав env e2e) — розв'язати, зберігши обидві
  сторони.

### 3.4 M3 should-fix (кілька власників; наскрізне доручення координатора)

- Worktree `wpm3fix`, гілка `wp/m3-should-fix` `2f77ae6` (**не запушено**), база `3c98542`.
- Зроблено й закомічено: `4db7c27` SDK `build_archive` → канонічний stored-архів registry (WP-06); `236321c`
  `keepalive_expiry` клієнта оркестратора до виконавців з конфігурації (WP-09); `6b67f1a` політика вихідних адрес
  Web Collector проти SSRF (WP-02); `e0cc576` TOCTOU `file:`-секретів у llm і telegram (WP-10, WP-04); `2f77ae6`
  невалідний `api_base` у llm → 422 (WP-10).
- **В роботі, не закомічено** (`services/orchestrator/src/jane_orchestrator/engine.py`,
  `services/orchestrator/tests/orch_support.py`, новий `services/orchestrator/tests/test_stored_raw.py`):
  6. дефект WP-09: `POST /v1/reprocessing` зі `stored_materials.material_ids` бере RAW **інших джерел** — у
     `_feed_stored` передати `source_id` завдання у фільтр `storage GET /v1/objects` (є в контракті storage.v1);
     тест, що падає до виправлення. Лише у звіті: чи потрібен `stored_materials.object_ids`/фільтр за
     `observation_id` у `ReprocessRequest` (зміна контракту — запит до WP-00, не робити самим).
  7. WP-09: заповнювати `ProblemGroup.samples[].stored_object_id` (поле є в `contracts/openapi/orchestrator.v1.yaml`
     ~1656, 1700), коли оркестратор знає id збереженого RAW прикладу; якщо без зміни контракту не знає — описати.
- Далі: доробити 6–7 з тестами → звіт `docs/delivery/M3/m3-should-fix.md` (ще не створено: по пунктах, файли за
  власниками з `.claude/wp-paths.json`, справжній вивід тестів) → push → `gh workflow run ci --ref wp/m3-should-fix`
  (оркестратор змінено — потрібен повний e2e) → рев'ю → злиття. Можливі конфлікти з потоком A: B2 змінює app-wiring
  і settings тих самих сервісів (orchestrator, web-collector, llm, telegram) — розв'язати, зберігши обидві сторони.

## 4. Порядок і завершення

Інкременти незалежні — веди паралельно (рецензенти й CI паралельно). Рекомендований порядок злиттів:
13s → 14d → should-fix → 12d (останнім, щоб зняти `test.fail` WP-09 після злиття should-fix).

Коли всі чотири злито: допиши в `docs/delivery/M3/stream-b.md` підсумок (SHA злиттів, CI, відкриті запити до інших
власників) і повідом людині, що потік B завершено. Фінальний CI на зведеній ревізії, real-прогін адмінки, зведення
матриці й фінальне рев'ю робить потік A.

## 5. Стан інфраструктури на момент передачі

- Docker: зупинені (не видалені) контейнери проєкту `jane-wp12d-r1` (стек real-прогону WP-12d); інших стеків потоку B
  немає. `puluj-g-*` працює — не чіпати.
- CI на момент передачі: 37847417132 (13s, dispatch) і 37848025370 (14d, push) — у процесі.
