# Потік B до M3 (2026-10-09)

Доручення: [HANDOFF-2026-10-09-stream-b.md](../HANDOFF-2026-10-09-stream-b.md).
Координатор потоку B працює через detached checkout `.claude/worktrees/integ-b` і публікує прийняті інкременти
в `codex/jane-integration`. Злиття в `main` та фінальний gate M3 залишаються людині й потоку A.

## Стан

| Інкремент | Гілка | Стан | Доказ / наступна дія |
|---|---|---|---|
| WP-13s | `wp/13s-r04-completions`, `892a2e1` | **accepted, злито `86cdece`** | незалежне review 1 accepted; [CI 37847417132](https://github.com/sql-monk/Jane/actions/runs/37847417132) на `fcf798c`: 12/12 success, e2e 75 passed, 4 нові PASSED, 0 skipped/xfail/failed; `892a2e1` лише доповнює звіт |
| WP-14d | `wp/14d-docs-entrypoints`, `467bf84` | **accepted, злито `0507ef9`** | незалежне review 1 accepted; повний [CI 37819395884](https://github.com/sql-monk/Jane/actions/runs/37819395884) на `f21947f`: 12/12, e2e 62 passed; push [CI 37848025370](https://github.com/sql-monk/Jane/actions/runs/37848025370) на `359eb0d`: success, нові offline-тести 83 passed; `467bf84` лише доповнює звіт |
| M3 should-fix | `wp/m3-should-fix` | active, виправлення review 1 | review на `3b45a7b`: changes requested — TOCTOU resolved target/parent і неоднозначний RAW id; TOCTOU виправлено локально `c07d91a`, другий пункт у роботі; потрібні новий full CI і review 2 |
| WP-12d | `wp/12d2-real-reprocessing`, `d5d8efc` | виправлення review 1 готові; очікує should-fix | [CI 37850908072](https://github.com/sql-monk/Jane/actions/runs/37850908072) success, включно з новим `web-mock-e2e`; mock 29 passed/14 skipped; 9 real completed (8 успішних + очікуваний WP-09 failure); остаточне review 2 після зняття `test.fail` і real-перевірки WP-09 |

Прийнято й опубліковано 2 із 4 інкрементів потоку B. Фінальний gate M3 ще не виконаний.

## Журнал

- Прочитано handoff із `origin/codex/jane-integration` (`37c9192`), `CLAUDE.md`, план, довідник розробки,
  кінець `status.md`, фінальне рев'ю M3, скіли `jane-wp` / `jane-contracts` та інструкції незалежного рецензента.
- Перевірено фактичні `git status` / `git log` чотирьох checkout. Незакомічені зміни попередніх авторів
  збережені й продовжуються; WP-13s має два завершені адресні прогони після rebase, хоча handoff їх ще не згадував.
- Запущено окремих виконавців WP-12d і should-fix та незалежного `wp-reviewer` WP-14d. Повні локальні
  `just check` / `just e2e` повторно не запускаються: повні gates — CI, real Playwright — локально.
- Попереднє `git merge-tree --write-tree` для WP-13s і WP-14d проти `37c9192` — без конфліктів.
- **WP-14d — accepted (review 1), `467bf84`; злиття `0507ef9` опубліковано в origin.** Рецензент сам отримав
  `83 passed`; ruff / format / mypy успішні; `unit -k progress_log` запускає додаткову сесію (`1 passed,
  82 deselected`); 122 локальні посилання без помилок. На власних проєктах відтворив dump/restore через
  dev/profile stack: health `ok`, ліміт `777`, профіль і ETag `v3` збережені, перемикачі `false/false → true/true`;
  після прибирання `leftovers: {}`. Власність: 18 файлів, 8 поза WP-14, усі явно делеговані handoff; хуки,
  `libs/jane-kit`, `status.md`, контракти незмінні. Злиття без конфліктів; повний CI сукупної ревізії — gate потоку A.
- **WP-13s — accepted (review 1), `892a2e1`; злиття `86cdece` опубліковано в origin.** Незалежно:
  LLM 68 passed; assistant 15 passed; PostgreSQL 3 passed; нові e2e 4 passed, 9 deselected (282.24 с), без
  skip/xfail. Регресія `unknown.py` відтворена до виправлення і проходить на HEAD. Active window спостерігається
  журналом і станом роботи; повтори не додають викликів/витрат/версій. Root і рецензент перевірили повний CI
  37847417132: 12/12 success, `75 passed in 1476.24s`, усі 4 нові явно PASSED. Злиття без конфліктів.
- **Should-fix review 1 — changes requested.** Рецензент відтворив чотири TOCTOU (resolved target/parent
  для LLM/Telegram) і довільний останній RAW id за двох копій одного observation. Автор виправляє обидва;
  CI 37850604947 на `3b45a7b` не є фінальним доказом після цих виправлень. Решта адресних перевірок
  рецензента: 67 passed/4 deselected та 3 integration passed/0 skipped; власність 26/0.

## Межі й відкриті запити

`wp01g`, `wp01h`, їхні гілки, `libs/jane-kit/**`, `docs/delivery/status.md` і фінальне зведення матриці
залишаються потоку A. Checkout потоку A не використовується для злиття. `puluj-g-*` не зачіпається.

Запити до власників контрактів фіксуються у звітах інкрементів; сам потік B `contracts/` не змінює.
Після приймання кожного інкременту тут буде його вердикт, CI/SHA і SHA успішно опублікованого злиття.
