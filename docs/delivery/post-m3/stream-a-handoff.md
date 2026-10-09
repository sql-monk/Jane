# Потік A (Codex): завершити WP-19 і вести облік після M3

Передача від Claude 2026-10-09: попередній координатор потоку A зупинився на вимогу людини; виконавця WP-19
зупинено на написанні звіту. Спершу прочитай [README потоків](README.md) (спільні правила), `CLAUDE.md`, скіли
`jane-wp` і `jane-contracts`.

Потоки B і C ([stream-b-handoff.md](stream-b-handoff.md), [stream-c-handoff.md](stream-c-handoff.md)) ведуть інші
агенти й **чекають на твій маркер `merge: accept WP-19`** в `origin/codex/jane-integration` (B-5, C-2, C-4).

## Стан WP-19

- Гілка **`wp/19-post-m3-shared-stores-contentref`** (є на origin), вершина **`261b4dd`**, база `2c70543`.
  Worktree `C:\repos\Jane\.claude\worktrees\wp19` (`.jane-wp` = `19`), чистий. 91 файл, +5007/−2948;
  у `services/*/src` +896/−2777.
- Коміти: `c3b373b` jane-kit (спільні `JobStore`/`IdempotencyStore` SQLite і PostgreSQL з орендою й fencing,
  `SecretPolicy`, `ContractSchemas`, `RulesLoader`, `ContentWriter`/`FileTransitStore`) → по одному коміту на сервіс:
  handler-runtime, assistant, registry, llm, orchestrator (ключі), web-collector, telegram-collector, storage →
  `ae3439c` дефект storage (`PUT /v1/connections` обривав записи) → `6b4819c`/`a2cbac8` великий RAW без
  blob-URI повертається транзитним blob → контракти (`storage.v1` медіатипи `getObjectContent`, опис
  `max_parallel_fetches`) → `261b4dd` чернетка звіту.
- **Звіт [WP-19.md](../WP-19.md) на гілці — чернетка**: усі розділи є (результат по пунктах, інвентар копій,
  уніфікація, міграції, R18-обсяг, зміни поведінки, обмеження, запити), **окрім виводу перевірок**: плейсхолдери
  `@REV@` (рядок 3) і `@OUTPUTS@` (останній розділ). Виконавець за власними словами комітив кожен сервіс після
  зелених тестів сервісу, але фінальних прогонів і їхнього виводу немає — **не довіряй, перевір сам**.
- Push гілки запустив CI для `wp/**` (lint/types/unit/contract/web) — подивись результат:
  `gh run list --branch wp/19-post-m3-shared-stores-contentref`.

## Що зробити

1. **Добити перевірки й звіт** (субагент-виконавець у тому ж worktree, гілка та сама):
   `just test jane-kit`, `just test <сервіс>` для handler-runtime, assistant, registry, llm, orchestrator,
   web-collector, telegram-collector, storage; `-m integration` для PostgreSQL-реалізацій (jane-kit, assistant,
   registry, llm, handler-runtime, storage, orchestrator) на власному стеку (`just up --project jane-wp19 postgres
   minio` → `just down -v --project jane-wp19`); `just types`; `just lint`;
   `uv run contracts/tools/check_contracts.py --require-redocly`;
   `uv run contracts/tools/compat.py --base origin/codex/jane-integration --oasdiff`;
   `node web/admin/scripts/gen-api.mjs --check`; `python .claude/hooks/jane_wp.py check-diff origin/codex/jane-integration`.
   Падіння — виправити (тести не послаблювати). Замінити `@REV@` і `@OUTPUTS@` реальними SHA й виводом.
2. **Незалежне рев'ю** (субагент-рецензент, ≤2 раунди) з наголосом на ризиках великого рефакторингу:
   - незмінність зовнішньої поведінки API (R-04 ідемпотентність: той самий ключ → та сама відповідь, інше тіло →
     422, `idempotency_in_progress` → 409; R-07: job переживає рестарт, перехоплення оренди загиблого екземпляра);
   - міграції наявних даних (SQLite-файли стану колекторів, таблиці PG сервісів): старі дані читаються, оновлення
     ідемпотентне й безпечне для кількох екземплярів;
   - розділ звіту «Що змінилось у поведінці (видимо зовні)» — чи кожна зміна свідома й сумісна;
   - мутанти щонайменше для fencing оренди й виправлення `PUT /v1/connections` storage.
   Плюс **contract-guardian** на зміни `contracts/` (`storage.v1`, `limits.schema.json`,
   `contracts/docs/storage-adapter.md`).
3. **Повний CI на гілці з e2e:** `gh workflow run ci --ref wp/19-post-m3-shared-stores-contentref` (обов'язково —
   рефакторинг зачіпає всі сервіси й ланцюжки R-02…R-08). Якщо база відстала й є конфлікти — злити свіжу
   інтеграцію в гілку WP-19 (не rebase із force) або зробити перевірочну гілку `wp/19-merge-check` = інтеграція +
   WP-19 і ганяти CI на ній.
4. **Злиття** в `codex/jane-integration` з checkout без `.jane-wp` (наприклад `C:\repos\Jane\.claude\worktrees\integ-a`,
   гілка `codex/jane-integration`, чистий): `git pull --ff-only`, `git merge --no-ff
   wp/19-post-m3-shared-stores-contentref -m "merge: accept WP-19 …"` — **саме з цим маркером**, push.
   Згенеровані файли адмінки при конфлікті — перегенерувати (`corepack pnpm --dir web/admin gen:api`), не мержити
   руками.
5. **Запит WP-19 до e2e** (одна строка, координаторським комітом в інтеграції після злиття):
   `tests/e2e/compose.e2e.yaml` перевизначає `JANE_HANDLER_RUNTIME_BLOB_ROOTS` лише на `objects/` — додати
   `/var/lib/jane/storage/transit/storage` (як у базовому `infra/compose.yaml`), щоб runtime в e2e читав транзитні
   blob storage. Узгодь з потоком B, якщо він саме змінює `tests/e2e`.
6. **Облік** (координатор, без рецензента): у [M3/open-requests.md](../M3/open-requests.md) закрити R17 і R18
   (R18 — «закрито в межах files-транзиту»; поза обсягом S3/MinIO-транзит і `download_url`, див. звіт); у
   [status.md](../status.md), розділ «Після M3», — запис про WP-19 і посилання на CI.
7. **Підсумок:** коли потоки B і C завершать свої злиття — один `gh workflow run ci --ref codex/jane-integration`;
   при success — повідом людину одним реченням із SHA для злиття в `main` (людина робить
   `git merge --ff-only origin/codex/jane-integration` і `git push origin main` сама).

## Корисне

- Процес попередніх WP після M3 і їхні звіти: [WP-15](../WP-15.md) … [WP-21](../WP-21.md); вердикти рецензентів і
  перевірочні гілки — у тексті злиттів (`git log --merges origin/codex/jane-integration`).
- Хук `.claude/hooks/check_report.py` у checkout з `.jane-wp` = 19 блокує завершення ходу, поки немає
  `docs/delivery/WP-19.md` — у гілці він уже є (чернетка).
- Docker-хост зайнятий контейнерами `puluj-g-*` — не чіпати.
