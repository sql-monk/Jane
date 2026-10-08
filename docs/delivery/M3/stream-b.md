# Потік B до M3 (2026-10-09)

Доручення: [HANDOFF-2026-10-09-stream-b.md](../HANDOFF-2026-10-09-stream-b.md).
Координатор потоку B працює через detached checkout `.claude/worktrees/integ-b` і публікує прийняті інкременти
в `codex/jane-integration`. Злиття в `main` та фінальний gate M3 залишаються людині й потоку A.

## Стан

| Інкремент | Гілка | Стан | Доказ / наступна дія |
|---|---|---|---|
| WP-13s | `wp/13s-r04-completions`, `fcf798c` | review очікує повний CI | два локальні адресні прогони: 4 passed кожен; [CI 37847417132](https://github.com/sql-monk/Jane/actions/runs/37847417132) ще виконує e2e; незалежне рев'ю після CI |
| WP-14d | `wp/14d-docs-entrypoints`, `467bf84` | **accepted, злито `0507ef9`** | незалежне review 1 accepted; повний [CI 37819395884](https://github.com/sql-monk/Jane/actions/runs/37819395884) на `f21947f`: 12/12, e2e 62 passed; push [CI 37848025370](https://github.com/sql-monk/Jane/actions/runs/37848025370) на `359eb0d`: success, нові offline-тести 83 passed; `467bf84` лише доповнює звіт |
| M3 should-fix | `wp/m3-should-fix` | active | пункти 1–5 закомічені; пункти 6–7 доробляються; регресії на старому engine: 2 failed, точні причини RAW/source та відсутній stored_object_id |
| WP-12d | `wp/12d2-real-reprocessing` | active, виправлення review 1 | нове ім'я замість force push; mock Playwright job, виправлення тестів і звіту; незалежне review 2 після CI й real-перевірки |

Прийнято й опубліковано 1 із 4 інкрементів потоку B. Фінальний gate M3 ще не виконаний.

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

## Межі й відкриті запити

`wp01g`, `wp01h`, їхні гілки, `libs/jane-kit/**`, `docs/delivery/status.md` і фінальне зведення матриці
залишаються потоку A. Checkout потоку A не використовується для злиття. `puluj-g-*` не зачіпається.

Запити до власників контрактів фіксуються у звітах інкрементів; сам потік B `contracts/` не змінює.
Після приймання кожного інкременту тут буде його вердикт, CI/SHA і SHA успішно опублікованого злиття.
